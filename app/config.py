"""Application configuration using Pydantic Settings."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ─── Provider Selection ──────────────────────────────────
    llm_provider: Literal["ollama", "openai"] = "ollama"
    embedding_provider: Literal["ollama", "openai"] = "ollama"

    # ─── Ollama Configuration ────────────────────────────────
    ollama_base_url: str = "http://ollama:11434"
    ollama_llm_model: str = "llama3.1:8b"
    ollama_embed_model: str = "nomic-embed-text"

    # ─── OpenAI Configuration ────────────────────────────────
    openai_api_key: str = ""
    openai_llm_model: str = "gpt-4o"
    openai_embed_model: str = "text-embedding-3-small"

    # ─── Qdrant Configuration ────────────────────────────────
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "handbook"

    # ─── Retrieval Configuration ─────────────────────────────
    retrieval_top_k: int = 5
    retrieval_score_threshold: float = 0.7

    # ─── Chunking Configuration ──────────────────────────────
    chunk_size: int = 500
    chunk_overlap: int = 50

    # ─── Admin Configuration ─────────────────────────────────
    admin_password: str = "admin123"
    admin_secret: str = "change-me"

    # ─── Application Configuration ───────────────────────────
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    @property
    def embedding_dimension(self) -> int:
        """Return embedding dimension based on provider/model."""
        if self.embedding_provider == "openai":
            return 1536  # text-embedding-3-small
        return 768  # nomic-embed-text
