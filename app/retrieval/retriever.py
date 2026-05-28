"""Retriever module - handles query embedding and context retrieval."""

import logging

from app.config import Settings
from app.generation import BaseEmbeddingClient
from app.models.schemas import Citation
from app.retrieval.vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieves relevant context chunks for a given query."""

    def __init__(
        self,
        settings: Settings,
        embedding_client: BaseEmbeddingClient,
        vector_store: QdrantVectorStore,
    ):
        self.settings = settings
        self.embedding_client = embedding_client
        self.vector_store = vector_store

    async def retrieve(self, query: str) -> tuple[list[dict], list[Citation], float]:
        """Retrieve relevant chunks for a query.

        Args:
            query: The user's question.

        Returns:
            Tuple of:
                - List of chunk dicts (text + metadata) for context injection
                - List of Citation objects for the response
                - Average confidence score
        """
        # Step 1: Embed the query
        logger.info(f"Embedding query: {query[:50]}...")
        query_vector = await self.embedding_client.embed_single(query)

        # Step 2: Search vector store
        results = await self.vector_store.search(
            query_vector=query_vector,
            top_k=self.settings.retrieval_top_k,
            score_threshold=self.settings.retrieval_score_threshold,
        )

        if not results:
            logger.info("No relevant chunks found above score threshold")
            return [], [], 0.0

        logger.info(f"Retrieved {len(results)} relevant chunks")

        # Step 3: Build citations
        citations = [
            Citation(
                section=result["section_title"],
                page=result["page_number"],
                relevance_score=round(result["score"], 3),
            )
            for result in results
        ]

        # Step 4: Calculate average confidence
        avg_confidence = sum(r["score"] for r in results) / len(results)

        return results, citations, round(avg_confidence, 3)
