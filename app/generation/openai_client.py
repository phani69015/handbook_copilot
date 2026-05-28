"""OpenAI LLM and Embedding client implementations."""

import logging

from openai import AsyncOpenAI

from app.generation import BaseEmbeddingClient, BaseLLMClient

logger = logging.getLogger(__name__)


class OpenAILLMClient(BaseLLMClient):
    """LLM client that communicates with OpenAI's API."""

    def __init__(self, api_key: str, model: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using OpenAI's chat completions API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI LLM error: {e}")
            raise RuntimeError(f"OpenAI LLM request failed: {e}") from e


class OpenAIEmbeddingClient(BaseEmbeddingClient):
    """Embedding client that communicates with OpenAI's API."""

    def __init__(self, api_key: str, model: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts using OpenAI."""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise RuntimeError(f"OpenAI embedding request failed: {e}") from e

    async def embed_single(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        embeddings = await self.embed([text])
        return embeddings[0]
