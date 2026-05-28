"""Tests for the chunker module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ingestion.chunker import RecursiveChunker


def test_chunker_basic():
    """Test that chunker splits text into chunks."""
    chunker = RecursiveChunker(chunk_size=50, chunk_overlap=10)

    pages = [
        {
            "text": "## Academic Policies\n\nThis section covers academic policies.\n\n"
            "Students must maintain a GPA of 3.0 to remain in good standing. "
            "Failure to meet this requirement will result in academic probation.\n\n"
            "## Grading\n\nGrades are assigned on a standard A-F scale. "
            "A grade of C or above is required to pass a course.",
            "page_number": 1,
        }
    ]

    chunks = chunker.chunk_pages(pages, source_file="test.pdf")

    assert len(chunks) > 0
    assert all(chunk.text for chunk in chunks)
    assert all(chunk.metadata.page_number == 1 for chunk in chunks)
    assert all(chunk.metadata.source_file == "test.pdf" for chunk in chunks)


def test_chunker_respects_size():
    """Test that chunks don't exceed the configured size."""
    chunker = RecursiveChunker(chunk_size=100, chunk_overlap=0)

    long_text = " ".join(["word"] * 500)
    pages = [{"text": long_text, "page_number": 1}]

    chunks = chunker.chunk_pages(pages, source_file="test.pdf")

    for chunk in chunks:
        token_count = chunker._count_tokens(chunk.text)
        # Allow some flexibility due to overlap text prefix
        assert token_count <= 120, f"Chunk too large: {token_count} tokens"


def test_chunker_extracts_section_title():
    """Test that section titles are extracted from markdown headers."""
    chunker = RecursiveChunker(chunk_size=200, chunk_overlap=0)

    pages = [
        {
            "text": "## Financial Aid\n\nStudents can apply for financial aid "
            "through the university portal.",
            "page_number": 5,
        }
    ]

    chunks = chunker.chunk_pages(pages, source_file="test.pdf")

    assert len(chunks) > 0
    assert chunks[0].metadata.section_title == "Financial Aid"


def test_chunker_empty_pages():
    """Test that empty pages produce no chunks."""
    chunker = RecursiveChunker(chunk_size=100, chunk_overlap=10)

    pages = [
        {"text": "", "page_number": 1},
        {"text": "   ", "page_number": 2},
    ]

    chunks = chunker.chunk_pages(pages, source_file="test.pdf")
    assert len(chunks) == 0
