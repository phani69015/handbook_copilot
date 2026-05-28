# Handbook Copilot

AI-powered handbook assistant for universities and colleges. Students get instant, cited answers from their institution's handbook using vector search and RAG.

## Features

- **Multi-Tenant** — Any number of colleges, each with their own isolated handbook data
- **Invite Code System** — Only authorized admins can register colleges (platform-controlled access)
- **Per-College OpenAI Key** — Colleges can optionally provide an OpenAI key for faster responses (~1-2s vs ~5-10s)
- **Cited Answers** — Every response includes section name and page number references
- **Smart Chunking** — Section-aware recursive text splitting with overlap for context continuity
- **Switchable LLM** — Ollama (local, free) or OpenAI (fast, per-college key)
- **Admin Dashboard** — Upload PDFs, monitor ingestion, preview chunks, test queries

## Architecture

```
College Admin → Register (invite code) → Upload PDF → Indexed in Qdrant
                                                          ↓
Student → Enter college code → Ask question → Embed → Search → LLM → Cited answer
```

```
┌─────────────────────────────────────────────────────────────┐
│  Docker Compose                                             │
│                                                             │
│  Frontend (Streamlit:8501) → Backend (FastAPI:8000)         │
│                                    ↕              ↕         │
│                              Qdrant:6333    Ollama:11434    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Clone and enter directory
git clone https://github.com/phani69015/handbook_copilot.git
cd handbook_copilot

# 2. Copy environment config
cp .env.example .env

# 3. Start all services
docker compose up -d --build

# 4. Pull Ollama models (first time only)
./scripts/pull_models.sh

# 5. Generate invite codes (admin only)
curl -X POST http://localhost:8000/admin/invite-codes/generate \
  -H "X-Admin-Secret: <your-secret>" \
  -H "Content-Type: application/json" \
  -d '{"count": 5}'
```

## UI & Access URLs

| Interface | URL | Description |
|-----------|-----|-------------|
| Home (Landing) | http://localhost:8501 | Product page, college list |
| Register College | http://localhost:8501/🏫_Register_College | Admin: register + upload handbook |
| Student Chat | http://localhost:8501/💬_Student_Chat | Students: enter code, ask questions |
| API Docs (Swagger) | http://localhost:8000/docs | Interactive API documentation |
| Qdrant Dashboard | http://localhost:6333/dashboard | Browse vectors, collections |

## User Flows

### Platform Admin (You)

1. Generate invite codes via secret API endpoint
2. Give invite codes to college administrators

### College Administrator

1. Enter invite code on Register page
2. Enter college name + (optional) OpenAI API key
3. Upload student handbook PDF
4. Share the generated college code with students

### Student

1. Open Student Chat page
2. Enter college code (e.g., `SPC-a3b2`)
3. Ask questions → get instant cited answers

## API Endpoints

### Public

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |
| GET | `/colleges` | List registered colleges |
| GET | `/colleges/{code}` | Get college info |
| POST | `/colleges/register` | Register college (requires invite code) |
| POST | `/colleges/{code}/ingest` | Upload + index PDF |
| POST | `/colleges/{code}/query` | Query a college's handbook |
| GET | `/colleges/{code}/chunks` | Preview stored chunks |
| DELETE | `/colleges/{code}/collection` | Delete college data |

### Admin (Protected by `X-Admin-Secret` header)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/invite-codes/generate` | Generate new invite codes |
| GET | `/admin/invite-codes` | List all codes + status |
| DELETE | `/admin/invite-codes/{code}` | Revoke a code |

## Switching LLM Provider

Edit `.env`:

```env
# Use local Ollama (default, free)
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama

# Or use OpenAI globally (requires API key)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

Then restart: `docker compose restart backend`

> **Per-college override**: If a college provides an OpenAI key during registration, their queries automatically use OpenAI for generation (faster) while embeddings stay on Ollama (no re-ingestion needed).

## Services

| Service | Port | Purpose |
|---------|------|---------|
| Backend (FastAPI) | 8000 | API + RAG pipeline |
| Frontend (Streamlit) | 8501 | Landing + Student Chat + Register |
| Qdrant | 6333 | Vector database |
| Ollama | 11434 | Local LLM inference |

## Tech Stack

- **Backend**: Python 3.12, FastAPI, Pydantic, uvicorn
- **Vector DB**: Qdrant (cosine similarity search)
- **LLM**: Ollama (Llama 3.2 / 3.1) or OpenAI (GPT-4o)
- **Embeddings**: nomic-embed-text (768d) / text-embedding-3-small (1536d)
- **PDF Parsing**: PyMuPDF4LLM (markdown extraction with page/section metadata)
- **Chunking**: Custom recursive splitter (section-aware, 500 tokens, 50 overlap)
- **Frontend**: Streamlit (multi-page app)
- **Infra**: Docker Compose, named volumes, isolated bridge networks
- **Security**: Invite code system, per-college API key isolation, admin secret header

## Project Structure

```
handbook-copilot/
├── docker-compose.yml          # Full stack orchestration
├── Dockerfile                  # Backend container
├── Dockerfile.frontend         # Frontend container
├── .env.example                # Environment template
├── app/
│   ├── main.py                 # FastAPI entrypoint
│   ├── config.py               # Pydantic settings
│   ├── api/routes.py           # All API endpoints
│   ├── generation/             # LLM interface (Ollama/OpenAI, factory pattern)
│   ├── ingestion/              # PDF parser, chunker, pipeline
│   ├── retrieval/              # Qdrant vector store, retriever
│   └── models/                 # Schemas + college registry + invite store
├── frontend/
│   ├── streamlit_app.py        # Landing page
│   └── pages/                  # Register College + Student Chat
├── scripts/                    # Ingestion CLI + model pull
└── tests/                      # Unit tests
```

## Deployment

### Local (Docker Compose)

```bash
docker compose up -d --build
```

### Cloud

Deploy all services using Docker Compose on any cloud provider (AWS, GCP, DigitalOcean, Hetzner, etc.) or use managed services:

- **Qdrant** → Qdrant Cloud (free 1GB tier)
- **Backend + Frontend** → Any container hosting (Render, Railway, Cloud Run)
- **LLM** → OpenAI API (per-college keys) or self-hosted Ollama on GPU instance
