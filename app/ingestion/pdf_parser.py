"""PDF parsing module - extracts structured text from PDF files."""

import logging
from pathlib import Path

import pymupdf4llm

logger = logging.getLogger(__name__)


class PDFParser:
    """Parses PDF files into structured markdown sections with metadata."""

    def parse(self, file_path: str | Path) -> list[dict]:
        """Parse a PDF file into structured pages with section info.

        Args:
            file_path: Path to the PDF file.

        Returns:
            List of page dictionaries with keys:
                - text: Markdown text content of the page
                - page_number: 1-indexed page number
                - metadata: Additional metadata from pymupdf4llm

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            RuntimeError: If PDF parsing fails.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if not file_path.suffix.lower() == ".pdf":
            raise ValueError(f"File is not a PDF: {file_path}")

        logger.info(f"Parsing PDF: {file_path.name}")

        try:
            # pymupdf4llm returns a list of page dicts with markdown content
            pages = pymupdf4llm.to_markdown(
                str(file_path),
                page_chunks=True,  # Return per-page chunks
                show_progress=False,
            )

            parsed_pages = []
            for i, page in enumerate(pages):
                text = page.get("text", "").strip()
                if not text:
                    continue

                parsed_pages.append({
                    "text": text,
                    "page_number": page.get("metadata", {}).get("page", i) + 1,
                    "metadata": page.get("metadata", {}),
                })

            logger.info(f"Parsed {len(parsed_pages)} pages from {file_path.name}")
            return parsed_pages

        except Exception as e:
            logger.error(f"Failed to parse PDF {file_path}: {e}")
            raise RuntimeError(f"PDF parsing failed: {e}") from e

    def get_page_count(self, file_path: str | Path) -> int:
        """Get the total number of pages in a PDF without full parsing.

        Args:
            file_path: Path to the PDF file.

        Returns:
            Number of pages.
        """
        import pymupdf

        file_path = Path(file_path)
        with pymupdf.open(str(file_path)) as doc:
            return len(doc)
