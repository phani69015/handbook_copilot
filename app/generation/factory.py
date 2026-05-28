"""Factory functions to create LLM and Embedding clients based on configuration."""

from app.config import Settings
from app.generation import BaseEmbeddingClient, BaseLLMClient
from app.generation.ollama_client import OllamaEmbeddingClient, OllamaLLMClient
from app.generation.openai_client import OpenAIEmbeddingClient, OpenAILLMClient


def create_llm_client(settings: Settings) -> BaseLLMClient:
    """Create an LLM client based on the configured provider.

    Args:
        settings: Application settings with provider configuration.

    Returns:
        An instance of BaseLLMClient (Ollama or OpenAI).

    Raises:
        ValueError: If the provider is not recognized.
    """
    if settings.llm_provider == "ollama":
        return OllamaLLMClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_llm_model,
        )
    elif settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when llm_provider='openai'")
        return OpenAILLMClient(
            api_key=settings.openai_api_key,
            model=settings.openai_llm_model,
        )
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


def create_embedding_client(settings: Settings) -> BaseEmbeddingClient:
    """Create an Embedding client based on the configured provider.

    Args:
        settings: Application settings with provider configuration.

    Returns:
        An instance of BaseEmbeddingClient (Ollama or OpenAI).

    Raises:
        ValueError: If the provider is not recognized.
    """
    if settings.embedding_provider == "ollama":
        return OllamaEmbeddingClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embed_model,
        )
    elif settings.embedding_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when embedding_provider='openai'")
        return OpenAIEmbeddingClient(
            api_key=settings.openai_api_key,
            model=settings.openai_embed_model,
        )
    else:
        raise ValueError(f"Unknown embedding provider: {settings.embedding_provider}")
