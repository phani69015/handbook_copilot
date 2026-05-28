"""Tests for the prompt building module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.generation.prompts import SYSTEM_PROMPT, build_context_block, build_user_prompt


def test_system_prompt_contains_citation_instructions():
    """Test that system prompt includes citation format."""
    assert "[Section:" in SYSTEM_PROMPT
    assert "Page" in SYSTEM_PROMPT
    assert "ONLY" in SYSTEM_PROMPT


def test_build_context_block():
    """Test context block formatting."""
    chunks = [
        {
            "text": "Late submissions are penalized 5% per day.",
            "section_title": "Academic Policies",
            "page_number": 45,
        },
        {
            "text": "Grades are assigned on the A-F scale.",
            "section_title": "Grading",
            "page_number": 47,
        },
    ]

    context = build_context_block(chunks)

    assert "Source 1" in context
    assert "Source 2" in context
    assert "Academic Policies" in context
    assert "Page 45" in context
    assert "Late submissions" in context


def test_build_user_prompt():
    """Test full user prompt construction."""
    chunks = [
        {
            "text": "The library is open 24/7 during exam periods.",
            "section_title": "Campus Facilities",
            "page_number": 12,
        },
    ]

    prompt = build_user_prompt("When is the library open?", chunks)

    assert "When is the library open?" in prompt
    assert "Campus Facilities" in prompt
    assert "library is open 24/7" in prompt
    assert "Context from University Handbook" in prompt


def test_build_context_block_empty():
    """Test context block with no chunks."""
    context = build_context_block([])
    assert context == ""
