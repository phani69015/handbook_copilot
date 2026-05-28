#!/usr/bin/env python3
"""CLI script to ingest a PDF file into the vector database.

Usage:
    python scripts/ingest.py data/handbook.pdf
    python scripts/ingest.py data/handbook.pdf --force-reindex
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.api.dependencies import get_embedding_client, get_settings, get_vector_store
from app.ingestion.pipeline import IngestionPipeline


async def main():
    """Run the ingestion pipeline from the command line."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest.py <path-to-pdf> [--force-reindex]")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    force_reindex = "--force-reindex" in sys.argv

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    if not file_path.suffix.lower() == ".pdf":
        print(f"Error: Not a PDF file: {file_path}")
        sys.exit(1)

    print(f"{'=' * 60}")
    print(f"Handbook Copilot - PDF Ingestion")
    print(f"{'=' * 60}")
    print(f"  File:          {file_path}")
    print(f"  Force reindex: {force_reindex}")
    print(f"{'=' * 60}")

    settings = get_settings()
    embedding_client = get_embedding_client()
    vector_store = get_vector_store()

    pipeline = IngestionPipeline(
        settings=settings,
        embedding_client=embedding_client,
        vector_store=vector_store,
    )

    result = await pipeline.ingest(file_path, force_reindex=force_reindex)

    print(f"\n{'=' * 60}")
    print(f"Ingestion Complete!")
    print(f"  Status:          {result.status}")
    print(f"  Chunks created:  {result.chunks_created}")
    print(f"  Pages processed: {result.pages_processed}")
    print(f"  Source file:     {result.source_file}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
