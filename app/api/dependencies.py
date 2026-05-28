"""Dependency injection for FastAPI routes."""

from functools import lru_cache

from app.config import Settings
from app.generation import BaseEmbeddingClient, BaseLLMClient
from app.generation.factory import create_embedding_client, create_llm_client
from app.ingestion.pipeline import IngestionPipeline
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import QdrantVectorStore


@lru_cache
def get_settings() -> Settings:
    """Get application settings (cached singleton)."""
    return Settings()


@lru_cache
def get_llm_client() -> BaseLLMClient:
    """Get LLM client based on configured provider."""
    settings = get_settings()
    return create_llm_client(settings)


@lru_cache
def get_embedding_client() -> BaseEmbeddingClient:
    """Get Embedding client based on configured provider."""
    settings = get_settings()
    return create_embedding_client(settings)


@lru_cache
def get_vector_store() -> QdrantVectorStore:
    """Get Qdrant vector store instance."""
    settings = get_settings()
    return QdrantVectorStore(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        collection_name=settings.qdrant_collection,
    )


def get_retriever() -> Retriever:
    """Get retriever instance."""
    return Retriever(
        settings=get_settings(),
        embedding_client=get_embedding_client(),
        vector_store=get_vector_store(),
    )


def get_ingestion_pipeline() -> IngestionPipeline:
    """Get ingestion pipeline instance."""
    return IngestionPipeline(
        settings=get_settings(),
        embedding_client=get_embedding_client(),
        vector_store=get_vector_store(),
    )
