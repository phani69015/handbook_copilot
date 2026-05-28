"""Chunking module - splits parsed text into semantically meaningful chunks."""

import logging
import re

import tiktoken

from app.models.schemas import Chunk, ChunkMetadata

logger = logging.getLogger(__name__)


class RecursiveChunker:
    """Section-aware recursive text chunker with token-based sizing.

    Splits text respecting section boundaries and uses tiktoken for
    accurate token counting. Supports overlap for context continuity.
    """

    # Separators ordered by priority (try to split at section boundaries first)
    SEPARATORS = [
        "\n## ",       # H2 headers (major sections)
        "\n### ",      # H3 headers (subsections)
        "\n#### ",     # H4 headers
        "\n\n",        # Paragraph breaks
        "\n",          # Line breaks
        ". ",          # Sentences
        " ",           # Words (last resort)
    ]

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """Initialize the chunker.

        Args:
            chunk_size: Maximum tokens per chunk.
            chunk_overlap: Token overlap between consecutive chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._tokenizer = tiktoken.get_encoding("cl100k_base")

    def _count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self._tokenizer.encode(text))

    def _extract_section_title(self, text: str) -> str:
        """Extract the most recent section title from text.

        Looks for markdown headers (##, ###, etc.) in the text.
        """
        # Find all headers in the text
        headers = re.findall(r"^#{1,4}\s+(.+)$", text, re.MULTILINE)
        if headers:
            return headers[-1].strip()
        return ""

    def _split_text(self, text: str, separators: list[str]) -> list[str]:
        """Recursively split text using the separator hierarchy.

        Args:
            text: Text to split.
            separators: Ordered list of separators to try.

        Returns:
            List of text segments within chunk_size.
        """
        if self._count_tokens(text) <= self.chunk_size:
            return [text] if text.strip() else []

        if not separators:
            # Last resort: hard split by tokens
            tokens = self._tokenizer.encode(text)
            chunks = []
            for i in range(0, len(tokens), self.chunk_size):
                chunk_tokens = tokens[i : i + self.chunk_size]
                chunks.append(self._tokenizer.decode(chunk_tokens))
            return chunks

        # Try the first separator
        separator = separators[0]
        remaining_separators = separators[1:]

        parts = text.split(separator)

        if len(parts) == 1:
            # This separator doesn't exist in text, try next one
            return self._split_text(text, remaining_separators)

        # Merge parts back together respecting chunk_size
        chunks = []
        current_chunk = ""

        for i, part in enumerate(parts):
            # Re-add the separator (except for the first part)
            candidate = part if i == 0 else separator + part

            if not current_chunk:
                current_chunk = candidate
            elif self._count_tokens(current_chunk + candidate) <= self.chunk_size:
                current_chunk += candidate
            else:
                # Current chunk is full, finalize it
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = candidate

        # Don't forget the last chunk
        if current_chunk.strip():
            if self._count_tokens(current_chunk) <= self.chunk_size:
                chunks.append(current_chunk.strip())
            else:
                # Still too large, recurse with next separator
                chunks.extend(self._split_text(current_chunk, remaining_separators))

        return chunks

    def _add_overlap(self, chunks: list[str]) -> list[str]:
        """Add overlap between consecutive chunks for context continuity.

        Args:
            chunks: List of text chunks.

        Returns:
            List of chunks with overlap prepended from the previous chunk.
        """
        if len(chunks) <= 1 or self.chunk_overlap == 0:
            return chunks

        overlapped = [chunks[0]]

        for i in range(1, len(chunks)):
            prev_tokens = self._tokenizer.encode(chunks[i - 1])
            overlap_tokens = prev_tokens[-self.chunk_overlap :]
            overlap_text = self._tokenizer.decode(overlap_tokens)

            overlapped_chunk = f"...{overlap_text.strip()} {chunks[i]}"
            overlapped.append(overlapped_chunk)

        return overlapped

    def chunk_pages(self, pages: list[dict], source_file: str = "") -> list[Chunk]:
        """Chunk a list of parsed pages into semantically meaningful chunks.

        Args:
            pages: List of page dicts from PDFParser (with 'text' and 'page_number').
            source_file: Name of the source PDF file.

        Returns:
            List of Chunk objects with metadata.
        """
        all_chunks: list[Chunk] = []
        chunk_index = 0

        for page in pages:
            page_text = page["text"]
            page_number = page["page_number"]

            # Split the page text
            text_segments = self._split_text(page_text, self.SEPARATORS)

            # Add overlap
            text_segments = self._add_overlap(text_segments)

            for segment in text_segments:
                if not segment.strip():
                    continue

                # Extract section title from the chunk content
                section_title = self._extract_section_title(segment)
                if not section_title:
                    # Try to inherit from page context
                    section_title = self._extract_section_title(page_text)

                chunk = Chunk(
                    text=segment.strip(),
                    metadata=ChunkMetadata(
                        section_title=section_title or f"Page {page_number}",
                        page_number=page_number,
                        chunk_index=chunk_index,
                        source_file=source_file,
                    ),
                )
                all_chunks.append(chunk)
                chunk_index += 1

        logger.info(
            f"Created {len(all_chunks)} chunks from {len(pages)} pages "
            f"(chunk_size={self.chunk_size}, overlap={self.chunk_overlap})"
        )
        return all_chunks
