"""Qdrant vector store interface."""

import logging
import uuid

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from app.models.schemas import Chunk, ChunkPreview

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Interface for Qdrant vector database operations."""

    def __init__(self, host: str, port: int, collection_name: str):
        """Initialize the Qdrant client.

        Args:
            host: Qdrant server hostname.
            port: Qdrant server port.
            collection_name: Name of the Qdrant collection.
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.client = AsyncQdrantClient(host=host, port=port)

    async def ensure_collection(self, dimension: int) -> None:
        """Ensure the collection exists, create if not.

        Args:
            dimension: Embedding vector dimension.
        """
        exists = await self.client.collection_exists(self.collection_name)

        if not exists:
            logger.info(
                f"Creating collection '{self.collection_name}' with dimension={dimension}"
            )
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE,
                ),
            )
        else:
            logger.info(f"Collection '{self.collection_name}' already exists")

    async def delete_collection(self) -> None:
        """Delete the collection if it exists."""
        try:
            await self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
        except Exception:
            logger.info(f"Collection '{self.collection_name}' does not exist, nothing to delete")

    async def upsert_chunks(
        self, chunks: list[Chunk], embeddings: list[list[float]]
    ) -> None:
        """Store chunks with their embeddings in Qdrant.

        Args:
            chunks: List of text chunks with metadata.
            embeddings: Corresponding embedding vectors.
        """
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": chunk.text,
                        "section_title": chunk.metadata.section_title,
                        "page_number": chunk.metadata.page_number,
                        "chunk_index": chunk.metadata.chunk_index,
                        "source_file": chunk.metadata.source_file,
                    },
                )
            )

        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            await self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
            )

        logger.info(f"Upserted {len(points)} points to '{self.collection_name}'")

    async def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        score_threshold: float = 0.7,
    ) -> list[dict]:
        """Search for similar chunks by vector using query_points.

        Args:
            query_vector: Query embedding vector.
            top_k: Number of results to return.
            score_threshold: Minimum similarity score.

        Returns:
            List of result dicts with text, metadata, and score.
        """
        response = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            with_payload=True,
        )

        return [
            {
                "text": hit.payload.get("text", ""),
                "section_title": hit.payload.get("section_title", ""),
                "page_number": hit.payload.get("page_number", 0),
                "chunk_index": hit.payload.get("chunk_index", 0),
                "source_file": hit.payload.get("source_file", ""),
                "score": hit.score,
            }
            for hit in response.points
        ]

    async def get_collection_info(self) -> dict:
        """Get collection statistics.

        Returns:
            Dictionary with collection info (point count, etc.)
        """
        try:
            exists = await self.client.collection_exists(self.collection_name)
            if not exists:
                return {
                    "total_chunks": 0,
                    "collection_exists": False,
                }

            info = await self.client.get_collection(self.collection_name)
            return {
                "total_chunks": info.points_count or 0,
                "collection_exists": True,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {
                "total_chunks": 0,
                "collection_exists": False,
            }

    async def get_chunks_preview(
        self, limit: int = 20, offset: int | str | None = None
    ) -> tuple[list[ChunkPreview], int]:
        """Get a paginated preview of stored chunks.

        Args:
            limit: Maximum number of chunks to return.
            offset: Offset for pagination (point ID or None for start).

        Returns:
            Tuple of (list of ChunkPreview, total count).
        """
        info = await self.get_collection_info()
        total = info["total_chunks"]

        if total == 0:
            return [], 0

        # Scroll through points
        results, _next_offset = await self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        previews = [
            ChunkPreview(
                id=str(point.id),
                text_preview=point.payload.get("text", "")[:200],
                section=point.payload.get("section_title", ""),
                page=point.payload.get("page_number", 0),
                chunk_index=point.payload.get("chunk_index", 0),
            )
            for point in results
        ]

        return previews, total

    async def is_healthy(self) -> bool:
        """Check if Qdrant is reachable and healthy."""
        try:
            await self.client.get_collections()
            return True
        except Exception:
            return False
