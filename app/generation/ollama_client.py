"""Ollama LLM and Embedding client implementations."""

import logging

import httpx

from app.generation import BaseEmbeddingClient, BaseLLMClient

logger = logging.getLogger(__name__)


class OllamaLLMClient(BaseLLMClient):
    """LLM client that communicates with Ollama's local API."""

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using Ollama's chat API."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 1024,
                        },
                    },
                    timeout=120.0,
                )
                response.raise_for_status()
                return response.json()["message"]["content"]
            except httpx.HTTPStatusError as e:
                logger.error(f"Ollama LLM error: {e.response.status_code} - {e.response.text}")
                raise RuntimeError(f"Ollama LLM request failed: {e}") from e
            except httpx.ConnectError as e:
                logger.error(f"Cannot connect to Ollama at {self.base_url}")
                raise RuntimeError(f"Cannot connect to Ollama: {e}") from e


class OllamaEmbeddingClient(BaseEmbeddingClient):
    """Embedding client that communicates with Ollama's embed API."""

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts using Ollama."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/embed",
                    json={
                        "model": self.model,
                        "input": texts,
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                return response.json()["embeddings"]
            except httpx.HTTPStatusError as e:
                logger.error(f"Ollama embed error: {e.response.status_code} - {e.response.text}")
                raise RuntimeError(f"Ollama embedding request failed: {e}") from e
            except httpx.ConnectError as e:
                logger.error(f"Cannot connect to Ollama at {self.base_url}")
                raise RuntimeError(f"Cannot connect to Ollama: {e}") from e

    async def embed_single(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        embeddings = await self.embed([text])
        return embeddings[0]
