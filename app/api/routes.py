"""FastAPI route definitions - Multi-college with invite codes and per-college OpenAI keys."""

import logging
import shutil
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile

from app.api.dependencies import (
    get_embedding_client,
    get_llm_client,
    get_settings,
    get_vector_store,
)
from app.config import Settings
from app.generation import BaseEmbeddingClient, BaseLLMClient
from app.generation.openai_client import OpenAILLMClient
from app.generation.prompts import SYSTEM_PROMPT, build_user_prompt
from app.ingestion.pipeline import IngestionPipeline
from app.models.registry import CollegeRegistry, InviteCodeStore
from app.models.schemas import (
    ChunkListResponse,
    CollegeInfo,
    CollegeListResponse,
    CollegeRegisterRequest,
    CollegeRegisterResponse,
    HealthResponse,
    IngestResponse,
    InviteCodeGenerateRequest,
    InviteCodeListResponse,
    InviteCodeResponse,
    QueryRequest,
    QueryResponse,
)
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)

router = APIRouter()

DATA_DIR = Path("/app/data")

# Singletons
_registry = CollegeRegistry()
_invite_store = InviteCodeStore()


def get_registry() -> CollegeRegistry:
    return _registry


def get_invite_store() -> InviteCodeStore:
    return _invite_store


def _verify_admin_secret(
    x_admin_secret: str = Header(..., alias="X-Admin-Secret"),
    settings: Settings = Depends(get_settings),
) -> None:
    """Dependency to verify the admin secret header."""
    if x_admin_secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid admin secret")


# ─── Health Check ────────────────────────────────────────────


@router.get("/health", response_model=HealthResponse)
async def health_check(
    settings: Settings = Depends(get_settings),
    vector_store: QdrantVectorStore = Depends(get_vector_store),
):
    """Check system health: Qdrant connectivity and Ollama availability."""
    qdrant_healthy = await vector_store.is_healthy()

    ollama_available = False
    if settings.llm_provider == "ollama" or settings.embedding_provider == "ollama":
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{settings.ollama_base_url}/api/tags", timeout=5.0
                )
                ollama_available = resp.status_code == 200
        except Exception:
            ollama_available = False

    return HealthResponse(
        status="healthy" if qdrant_healthy else "degraded",
        qdrant_connected=qdrant_healthy,
        ollama_available=ollama_available,
        llm_provider=settings.llm_provider,
        embedding_provider=settings.embedding_provider,
    )


# ═══════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS (Protected by X-Admin-Secret header)
# ═══════════════════════════════════════════════════════════════


@router.post(
    "/admin/invite-codes/generate",
    response_model=InviteCodeResponse,
    dependencies=[Depends(_verify_admin_secret)],
)
async def generate_invite_codes(request: InviteCodeGenerateRequest):
    """Generate new invite codes (admin only)."""
    store = get_invite_store()
    codes = store.generate(request.count)
    return InviteCodeResponse(
        codes=codes,
        message=f"Generated {len(codes)} invite code(s)",
    )


@router.get(
    "/admin/invite-codes",
    response_model=InviteCodeListResponse,
    dependencies=[Depends(_verify_admin_secret)],
)
async def list_invite_codes():
    """List all invite codes and their status (admin only)."""
    store = get_invite_store()
    codes = store.list_all()
    return InviteCodeListResponse(
        codes=codes,
        total_available=store.count_available(),
        total_used=store.count_used(),
    )


@router.delete(
    "/admin/invite-codes/{code}",
    dependencies=[Depends(_verify_admin_secret)],
)
async def revoke_invite_code(code: str):
    """Revoke/delete an invite code (admin only)."""
    store = get_invite_store()
    if not store.revoke(code):
        raise HTTPException(status_code=404, detail=f"Invite code not found: {code}")
    return {"status": "revoked", "code": code}


# ═══════════════════════════════════════════════════════════════
# COLLEGE REGISTRATION (Requires valid invite code)
# ═══════════════════════════════════════════════════════════════


@router.post("/colleges/register", response_model=CollegeRegisterResponse)
async def register_college(request: CollegeRegisterRequest):
    """Register a new college (requires valid invite code)."""
    invite_store = get_invite_store()
    registry = get_registry()

    # Validate invite code
    if not invite_store.validate(request.invite_code):
        raise HTTPException(
            status_code=403,
            detail="Invalid or already used invite code. Contact the platform administrator.",
        )

    # Register the college
    college = registry.register(
        college_name=request.college_name,
        openai_api_key=request.openai_api_key,
    )

    # Consume the invite code
    invite_store.consume(request.invite_code, college.college_code)

    return CollegeRegisterResponse(
        college_name=college.college_name,
        college_code=college.college_code,
        has_openai_key=college.has_openai_key,
        message=(
            f"College registered successfully! "
            f"Share code '{college.college_code}' with students."
        ),
    )


@router.get("/colleges", response_model=CollegeListResponse)
async def list_colleges():
    """List all registered colleges."""
    registry = get_registry()
    colleges = registry.list_all()
    return CollegeListResponse(colleges=colleges, total=len(colleges))


@router.get("/colleges/{college_code}", response_model=CollegeInfo)
async def get_college(college_code: str):
    """Get college info by code."""
    registry = get_registry()
    college = registry.get(college_code)
    if not college:
        raise HTTPException(status_code=404, detail=f"College not found: {college_code}")
    return college


# ═══════════════════════════════════════════════════════════════
# COLLEGE INGESTION
# ═══════════════════════════════════════════════════════════════


@router.post("/colleges/{college_code}/ingest", response_model=IngestResponse)
async def ingest_college_handbook(
    college_code: str,
    file: UploadFile = File(...),
    force_reindex: bool = Form(default=False),
    settings: Settings = Depends(get_settings),
    embedding_client: BaseEmbeddingClient = Depends(get_embedding_client),
):
    """Upload and ingest a PDF handbook for a specific college."""
    registry = get_registry()

    if not registry.exists(college_code):
        raise HTTPException(status_code=404, detail=f"College not found: {college_code}")

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Save uploaded file
    college_dir = DATA_DIR / college_code
    college_dir.mkdir(parents=True, exist_ok=True)
    file_path = college_dir / file.filename

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        logger.info(f"Saved uploaded file to {file_path}")

        # Create a vector store for this college's collection
        collection_name = registry.get_collection_name(college_code)
        college_vector_store = QdrantVectorStore(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            collection_name=collection_name,
        )

        # Create ingestion pipeline for this college
        pipeline = IngestionPipeline(
            settings=settings,
            embedding_client=embedding_client,
            vector_store=college_vector_store,
        )

        # Run ingestion
        result = await pipeline.ingest(file_path, force_reindex=force_reindex)
        result.college_code = college_code

        # Update registry
        registry.update(
            college_code,
            total_chunks=result.chunks_created,
            is_indexed=True,
        )

        return result

    except Exception as e:
        logger.error(f"Ingestion failed for {college_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}") from e


# ═══════════════════════════════════════════════════════════════
# COLLEGE QUERY (Uses per-college OpenAI key if available)
# ═══════════════════════════════════════════════════════════════


@router.post("/colleges/{college_code}/query", response_model=QueryResponse)
async def query_college_handbook(
    college_code: str,
    request: QueryRequest,
    settings: Settings = Depends(get_settings),
    embedding_client: BaseEmbeddingClient = Depends(get_embedding_client),
    default_llm: BaseLLMClient = Depends(get_llm_client),
):
    """Answer a student question using the college's handbook.

    If the college has an OpenAI API key, uses OpenAI for faster generation.
    Otherwise falls back to the default LLM (Ollama).
    """
    registry = get_registry()
    college = registry.get(college_code)

    if not college:
        raise HTTPException(status_code=404, detail=f"College not found: {college_code}")

    if not college.is_indexed:
        raise HTTPException(
            status_code=400,
            detail="This college's handbook has not been uploaded yet.",
        )

    # Determine which LLM to use
    college_openai_key = registry.get_openai_key(college_code)
    if college_openai_key:
        # Use college's OpenAI key for faster generation
        llm = OpenAILLMClient(
            api_key=college_openai_key,
            model=settings.openai_llm_model,
        )
        logger.info(f"Using OpenAI LLM for college {college_code}")
    else:
        # Fall back to default (Ollama)
        llm = default_llm
        logger.info(f"Using default Ollama LLM for college {college_code}")

    # Create vector store for this college
    collection_name = registry.get_collection_name(college_code)
    college_vector_store = QdrantVectorStore(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        collection_name=collection_name,
    )

    # Create retriever for this college
    retriever = Retriever(
        settings=settings,
        embedding_client=embedding_client,
        vector_store=college_vector_store,
    )

    logger.info(f"Query for {college.college_name}: {request.question[:80]}...")

    # Retrieve relevant chunks
    chunks, citations, confidence = await retriever.retrieve(request.question)

    # Handle no results
    if not chunks:
        return QueryResponse(
            answer=(
                f"I couldn't find specific information about this in the {college.college_name} handbook. "
                "Please contact your college administration for further assistance."
            ),
            citations=[],
            chunks_used=0,
            confidence=0.0,
            college_name=college.college_name,
        )

    # Build prompt and generate
    user_prompt = build_user_prompt(request.question, chunks)
    answer = await llm.generate(SYSTEM_PROMPT, user_prompt)

    return QueryResponse(
        answer=answer,
        citations=citations,
        chunks_used=len(chunks),
        confidence=confidence,
        college_name=college.college_name,
    )


# ═══════════════════════════════════════════════════════════════
# COLLEGE DATA MANAGEMENT
# ═══════════════════════════════════════════════════════════════


@router.get("/colleges/{college_code}/chunks", response_model=ChunkListResponse)
async def get_college_chunks(
    college_code: str,
    limit: int = 20,
    settings: Settings = Depends(get_settings),
):
    """Get chunk previews for a specific college."""
    registry = get_registry()

    if not registry.exists(college_code):
        raise HTTPException(status_code=404, detail=f"College not found: {college_code}")

    collection_name = registry.get_collection_name(college_code)
    college_vector_store = QdrantVectorStore(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        collection_name=collection_name,
    )

    if limit > 100:
        limit = 100

    previews, total = await college_vector_store.get_chunks_preview(limit=limit, offset=None)

    return ChunkListResponse(
        chunks=previews,
        total=total,
        offset=0,
        limit=limit,
    )


@router.delete("/colleges/{college_code}/collection")
async def delete_college_collection(
    college_code: str,
    settings: Settings = Depends(get_settings),
):
    """Delete a college's vector collection (for re-indexing)."""
    registry = get_registry()

    if not registry.exists(college_code):
        raise HTTPException(status_code=404, detail=f"College not found: {college_code}")

    collection_name = registry.get_collection_name(college_code)
    college_vector_store = QdrantVectorStore(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        collection_name=collection_name,
    )

    await college_vector_store.delete_collection()
    registry.update(college_code, total_chunks=0, is_indexed=False)

    return {"status": "deleted", "message": f"Collection for {college_code} deleted successfully"}


# ═══════════════════════════════════════════════════════════════
# SYSTEM CONFIG
# ═══════════════════════════════════════════════════════════════


@router.get("/config")
async def get_config(settings: Settings = Depends(get_settings)):
    """Get current system configuration (read-only, no secrets)."""
    return {
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider,
        "llm_model": (
            settings.ollama_llm_model
            if settings.llm_provider == "ollama"
            else settings.openai_llm_model
        ),
        "embedding_model": (
            settings.ollama_embed_model
            if settings.embedding_provider == "ollama"
            else settings.openai_embed_model
        ),
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "retrieval_top_k": settings.retrieval_top_k,
        "retrieval_score_threshold": settings.retrieval_score_threshold,
    }
