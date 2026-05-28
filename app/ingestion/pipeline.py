"""Ingestion pipeline - orchestrates PDF parsing, chunking, embedding, and storage."""

import logging
from pathlib import Path

from app.config import Settings
from app.generation import BaseEmbeddingClient
from app.ingestion.chunker import RecursiveChunker
from app.ingestion.pdf_parser import PDFParser
from app.models.schemas import Chunk, IngestResponse
from app.retrieval.vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)

# Batch size for embedding requests (avoid overwhelming the API)
EMBEDDING_BATCH_SIZE = 32


class IngestionPipeline:
    """Orchestrates the full ingestion flow: parse → chunk → embed → store."""

    def __init__(
        self,
        settings: Settings,
        embedding_client: BaseEmbeddingClient,
        vector_store: QdrantVectorStore,
    ):
        self.settings = settings
        self.embedding_client = embedding_client
        self.vector_store = vector_store
        self.pdf_parser = PDFParser()
        self.chunker = RecursiveChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

    async def ingest(self, file_path: str | Path, force_reindex: bool = False) -> IngestResponse:
        """Run the full ingestion pipeline for a PDF file.

        Args:
            file_path: Path to the PDF file.
            force_reindex: If True, drop existing collection before indexing.

        Returns:
            IngestResponse with ingestion stats.
        """
        file_path = Path(file_path)
        logger.info(f"Starting ingestion for: {file_path.name}")

        # Step 1: Optionally drop existing collection
        if force_reindex:
            logger.info("Force re-index: dropping existing collection")
            await self.vector_store.delete_collection()

        # Step 2: Ensure collection exists
        await self.vector_store.ensure_collection(
            dimension=self.settings.embedding_dimension
        )

        # Step 3: Parse PDF
        logger.info("Step 1/4: Parsing PDF...")
        pages = self.pdf_parser.parse(file_path)
        total_pages = len(pages)

        # Step 4: Chunk pages
        logger.info("Step 2/4: Chunking text...")
        chunks = self.chunker.chunk_pages(pages, source_file=file_path.name)

        # Step 5: Generate embeddings in batches
        logger.info(f"Step 3/4: Generating embeddings for {len(chunks)} chunks...")
        embeddings = await self._embed_chunks(chunks)

        # Step 6: Store in vector database
        logger.info("Step 4/4: Storing in vector database...")
        await self.vector_store.upsert_chunks(chunks, embeddings)

        logger.info(
            f"Ingestion complete: {len(chunks)} chunks from {total_pages} pages"
        )

        return IngestResponse(
            status="success",
            chunks_created=len(chunks),
            pages_processed=total_pages,
            source_file=file_path.name,
        )

    async def _embed_chunks(self, chunks: list[Chunk]) -> list[list[float]]:
        """Generate embeddings for chunks in batches.

        Args:
            chunks: List of text chunks to embed.

        Returns:
            List of embedding vectors.
        """
        all_embeddings: list[list[float]] = []
        texts = [chunk.text for chunk in chunks]

        for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
            batch = texts[i : i + EMBEDDING_BATCH_SIZE]
            batch_embeddings = await self.embedding_client.embed(batch)
            all_embeddings.extend(batch_embeddings)

            if (i + EMBEDDING_BATCH_SIZE) % 100 == 0:
                logger.info(
                    f"  Embedded {min(i + EMBEDDING_BATCH_SIZE, len(texts))}/{len(texts)} chunks"
                )

        return all_embeddings
