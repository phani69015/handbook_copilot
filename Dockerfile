# ─── Backend Dockerfile (Multi-stage) ───────────────────────
FROM docker.io/python:3.12-slim AS base

# Install system dependencies for PyMuPDF + curl for uv install
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

WORKDIR /app

# Copy project definition first (layer caching)
COPY pyproject.toml ./

# Install dependencies using uv (project install without the package itself)
RUN uv pip install --system --no-cache \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.32.0" \
    "pydantic>=2.10.0" \
    "pydantic-settings>=2.6.0" \
    "httpx>=0.28.0" \
    "openai>=1.57.0" \
    "qdrant-client>=1.12.0" \
    "pymupdf>=1.25.0" \
    "pymupdf4llm>=0.0.17" \
    "python-multipart>=0.0.18" \
    "tiktoken>=0.8.0"

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Create data directory
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
