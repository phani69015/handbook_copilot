"""Tests for retriever module (unit tests with mocks)."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.schemas import Citation
from app.retrieval.retriever import Retriever


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.retrieval_top_k = 5
    settings.retrieval_score_threshold = 0.7
    return settings


@pytest.fixture
def mock_embedding_client():
    client = AsyncMock()
    client.embed_single.return_value = [0.1] * 768
    return client


@pytest.fixture
def mock_vector_store():
    store = AsyncMock()
    store.search.return_value = [
        {
            "text": "Late submissions are penalized.",
            "section_title": "Academic Policies",
            "page_number": 45,
            "chunk_index": 0,
            "source_file": "handbook.pdf",
            "score": 0.92,
        },
        {
            "text": "Maximum penalty is 7 days.",
            "section_title": "Academic Policies",
            "page_number": 46,
            "chunk_index": 1,
            "source_file": "handbook.pdf",
            "score": 0.85,
        },
    ]
    return store


@pytest.mark.asyncio
async def test_retriever_returns_chunks_and_citations(
    mock_settings, mock_embedding_client, mock_vector_store
):
    """Test that retriever returns chunks, citations, and confidence."""
    retriever = Retriever(
        settings=mock_settings,
        embedding_client=mock_embedding_client,
        vector_store=mock_vector_store,
    )

    chunks, citations, confidence = await retriever.retrieve("late submission policy")

    assert len(chunks) == 2
    assert len(citations) == 2
    assert confidence > 0

    # Verify citations structure
    assert citations[0].section == "Academic Policies"
    assert citations[0].page == 45
    assert citations[0].relevance_score == 0.92


@pytest.mark.asyncio
async def test_retriever_no_results(mock_settings, mock_embedding_client):
    """Test retriever when no chunks are found."""
    vector_store = AsyncMock()
    vector_store.search.return_value = []

    retriever = Retriever(
        settings=mock_settings,
        embedding_client=mock_embedding_client,
        vector_store=vector_store,
    )

    chunks, citations, confidence = await retriever.retrieve("unrelated question")

    assert len(chunks) == 0
    assert len(citations) == 0
    assert confidence == 0.0
