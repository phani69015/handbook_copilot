"""Prompt templates for the RAG system."""

SYSTEM_PROMPT = """You are a knowledgeable and helpful university handbook assistant. Your role is to answer student questions accurately based ONLY on the provided handbook context.

## Rules:
1. ONLY answer using information from the provided context sections below.
2. ALWAYS cite your sources using the format: [Section: "Section Title", Page X]
3. If the context does not contain enough information to answer the question, respond with: "I couldn't find specific information about this in the handbook. Please contact the university administration for further assistance."
4. Be concise and direct in your answers.
5. If multiple sections are relevant, synthesize the information and cite all relevant sources.
6. Do NOT make up or infer information that is not explicitly stated in the context.
7. Use bullet points or numbered lists when presenting multiple items or steps.

## Example Response Format:
"According to the handbook, late submissions are penalized at 5% per day up to a maximum of 7 days [Section: "Academic Policies", Page 45]. After 7 days, the assignment receives a grade of zero [Section: "Grading Guidelines", Page 47]."
"""

USER_PROMPT_TEMPLATE = """## Context from University Handbook:

{context}

---

## Student Question:
{question}

Please provide a clear, accurate answer with citations to the relevant handbook sections."""


def build_context_block(chunks: list[dict]) -> str:
    """Build a formatted context block from retrieved chunks.

    Args:
        chunks: List of chunk dictionaries with 'text', 'section_title', and 'page_number'.

    Returns:
        Formatted context string with clear section delimiters.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        section = chunk.get("section_title", "Unknown Section")
        page = chunk.get("page_number", 0)
        text = chunk.get("text", "")
        context_parts.append(
            f"### Source {i} — Section: \"{section}\", Page {page}\n{text}"
        )
    return "\n\n---\n\n".join(context_parts)


def build_user_prompt(question: str, chunks: list[dict]) -> str:
    """Build the complete user prompt with context and question.

    Args:
        question: The student's question.
        chunks: Retrieved context chunks.

    Returns:
        Complete user prompt string.
    """
    context = build_context_block(chunks)
    return USER_PROMPT_TEMPLATE.format(context=context, question=question)
