"""Abstract base classes for LLM and Embedding clients."""

from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Abstract interface for LLM generation."""

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response given system and user prompts.

        Args:
            system_prompt: System-level instructions for the LLM.
            user_prompt: User query with injected context.

        Returns:
            Generated text response.
        """
        ...


class BaseEmbeddingClient(ABC):
    """Abstract interface for embedding generation."""

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a list of texts.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors (list of floats).
        """
        ...

    @abstractmethod
    async def embed_single(self, text: str) -> list[float]:
        """Generate embedding vector for a single text.

        Args:
            text: Text string to embed.

        Returns:
            Embedding vector.
        """
        ...
