"""FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events."""
    settings = Settings()
    logger.info("=" * 60)
    logger.info("Handbook Copilot - Starting up")
    logger.info(f"  LLM Provider:       {settings.llm_provider}")
    logger.info(f"  Embedding Provider: {settings.embedding_provider}")
    logger.info(f"  Qdrant:             {settings.qdrant_host}:{settings.qdrant_port}")
    logger.info(f"  Collection:         {settings.qdrant_collection}")
    logger.info("=" * 60)
    yield
    logger.info("Handbook Copilot - Shutting down")


app = FastAPI(
    title="Handbook Copilot API",
    description=(
        "RAG-based university handbook assistant. "
        "Provides cited answers to student queries using vector search."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware - allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
