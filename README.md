# Handbook Copilot

A RAG-based university handbook assistant that provides cited answers to student queries using vector search.

## Architecture

```
Student/Admin → Streamlit UI → FastAPI Backend → Qdrant (Vector DB)
                                     ↕
                              Ollama / OpenAI (LLM + Embeddings)
```

## Quick Start (Podman)

```bash
# 1. Clone and enter directory
cd handbook-copilot

# 2. Copy environment config
cp .env.example .env

# 3. Start all services
podman-compose up -d --build

# 4. Pull Ollama models (first time only, takes ~5 min)
./scripts/pull_models.sh
```

## UI & Access URLs

| Interface | URL | Description |
|-----------|-----|-------------|
| Student Chat | http://localhost:8501/💬_Student_Chat | Ask questions, get cited answers |
| Admin Panel | http://localhost:8501/⚙️_Admin_Panel | Upload PDFs, monitor ingestion, test queries |
| API Docs (Swagger) | http://localhost:8000/docs | Interactive API documentation |
| API Docs (ReDoc) | http://localhost:8000/redoc | Alternative API docs |
| Qdrant Dashboard | http://localhost:6333/dashboard | Browse vectors, collections, inspect data |
| Ollama API | http://localhost:11434 | Local LLM server |

## Usage

1. **Admin**: Open Admin Panel → Upload a PDF handbook → Wait for ingestion
2. **Student**: Open Student Chat → Ask questions → Get cited answers

## Switching LLM Provider

Edit `.env`:

```env
# Use local Ollama (default, free)
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama

# Or use OpenAI (requires API key)
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

Then restart: `podman-compose restart backend`

> Note: Switching embedding provider requires re-ingesting the PDF (different vector dimensions).

## Services

| Service              | Port  | Purpose                    |
| -------------------- | ----- | -------------------------- |
| Backend (FastAPI)    | 8000  | API + RAG pipeline         |
| Frontend (Streamlit) | 8501  | Student chat + Admin panel |
| Qdrant               | 6333  | Vector database            |
| Ollama               | 11434 | Local LLM inference        |

## API Endpoints

| Method | Endpoint    | Description              |
| ------ | ----------- | ------------------------ |
| POST   | /query      | Ask a question (RAG)     |
| POST   | /ingest     | Upload + ingest PDF      |
| GET    | /health     | System health check      |
| GET    | /stats      | Collection statistics    |
| GET    | /chunks     | Preview stored chunks    |
| GET    | /config     | Current configuration    |
| DELETE | /collection | Delete vector collection |

## Tech Stack

- **Backend**: Python 3.12, FastAPI, Pydantic
- **Vector DB**: Qdrant
- **LLM**: Ollama (Llama 3.1) / OpenAI (GPT-4o)
- **Embeddings**: nomic-embed-text / text-embedding-3-small
- **PDF Parsing**: PyMuPDF4LLM
- **Frontend**: Streamlit
- **Infra**: Podman Compose, named volumes, isolated networks
