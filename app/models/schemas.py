"""Pydantic models for request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


# ─── Shared Models ───────────────────────────────────────────


class Citation(BaseModel):
    """A citation pointing to a specific section and page in the handbook."""

    section: str = Field(..., description="Section title from the handbook")
    page: int = Field(..., description="Page number in the PDF")
    relevance_score: float = Field(..., description="Similarity score (0-1)")


class ChunkMetadata(BaseModel):
    """Metadata attached to each chunk stored in the vector database."""

    section_title: str = ""
    page_number: int = 0
    chunk_index: int = 0
    source_file: str = ""


class Chunk(BaseModel):
    """A text chunk with its metadata."""

    text: str
    metadata: ChunkMetadata


# ─── Invite Code Models ──────────────────────────────────────


class InviteCodeGenerateRequest(BaseModel):
    """Request to generate invite codes."""

    count: int = Field(default=1, ge=1, le=20, description="Number of codes to generate")


class InviteCodeInfo(BaseModel):
    """Info about a single invite code."""

    code: str
    status: str  # "available" or "used"
    used_by: str | None = None
    created_at: str = ""


class InviteCodeResponse(BaseModel):
    """Response after generating invite codes."""

    codes: list[str]
    message: str


class InviteCodeListResponse(BaseModel):
    """Response listing all invite codes."""

    codes: list[InviteCodeInfo]
    total_available: int
    total_used: int


# ─── College Models ──────────────────────────────────────────


class CollegeRegisterRequest(BaseModel):
    """Request body for college registration."""

    college_name: str = Field(..., min_length=3, max_length=200, description="Full college name")
    invite_code: str = Field(..., min_length=5, description="Invite code from platform admin")
    openai_api_key: str = Field(
        default="",
        description="Optional OpenAI API key for faster AI responses",
    )


class CollegeInfo(BaseModel):
    """College information (public — no API keys exposed)."""

    college_name: str
    college_code: str
    total_chunks: int = 0
    is_indexed: bool = False
    has_openai_key: bool = False
    created_at: datetime = Field(default_factory=datetime.now)


class CollegeRegisterResponse(BaseModel):
    """Response after registering a college."""

    college_name: str
    college_code: str
    has_openai_key: bool = False
    message: str


class CollegeListResponse(BaseModel):
    """Response listing all registered colleges."""

    colleges: list[CollegeInfo]
    total: int


# ─── API Request Models ──────────────────────────────────────


class QueryRequest(BaseModel):
    """Request body for the /query endpoint."""

    question: str = Field(..., min_length=3, max_length=2000, description="Student question")


class IngestRequest(BaseModel):
    """Request body for the /ingest endpoint (when using file path)."""

    file_path: str = Field(..., description="Path to PDF file in data/ directory")
    force_reindex: bool = Field(default=False, description="Drop existing collection and re-index")


# ─── API Response Models ─────────────────────────────────────


class QueryResponse(BaseModel):
    """Response body for the /query endpoint."""

    answer: str = Field(..., description="Generated answer with inline citations")
    citations: list[Citation] = Field(default_factory=list, description="Structured citations")
    chunks_used: int = Field(..., description="Number of chunks used for generation")
    confidence: float = Field(..., description="Average relevance score of retrieved chunks")
    college_name: str = Field(default="", description="College name for context")


class IngestResponse(BaseModel):
    """Response body for the /ingest endpoint."""

    status: str = Field(..., description="Ingestion status")
    chunks_created: int = Field(..., description="Number of chunks stored")
    pages_processed: int = Field(..., description="Number of PDF pages processed")
    source_file: str = Field(..., description="Name of the ingested file")
    college_code: str = Field(default="", description="College code")
    timestamp: datetime = Field(default_factory=datetime.now)


class CollectionStats(BaseModel):
    """Response body for the /stats endpoint."""

    total_chunks: int = 0
    total_pages: int = 0
    source_files: list[str] = Field(default_factory=list)
    embedding_provider: str = ""
    embedding_model: str = ""
    llm_provider: str = ""
    llm_model: str = ""
    last_ingested: datetime | None = None
    collection_exists: bool = False


class HealthResponse(BaseModel):
    """Response body for the /health endpoint."""

    status: str = "healthy"
    qdrant_connected: bool = False
    ollama_available: bool = False
    llm_provider: str = ""
    embedding_provider: str = ""


class ChunkPreview(BaseModel):
    """A chunk preview for the admin panel."""

    id: str
    text_preview: str = Field(..., description="First 200 chars of chunk text")
    section: str
    page: int
    chunk_index: int


class ChunkListResponse(BaseModel):
    """Response body for the /chunks endpoint."""

    chunks: list[ChunkPreview]
    total: int
    offset: int
    limit: int
