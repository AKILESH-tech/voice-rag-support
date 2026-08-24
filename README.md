# Voice + RAG Support Agent

An AI-powered support agent that ingests PDF documents and answers questions using Retrieval-Augmented Generation (RAG) with voice input support.

## Architecture

```
Frontend (React + Vite) → FastAPI Backend → ChromaDB (vector search) + SQLite (telemetry)
                                         ↓
                              PDF → Extract pages → Chunk → Embed (Gemini) → Store
                                         ↓
                              Query → Embed → Retrieve → Generate (Gemini/Groq/OpenRouter)
```

## Features

- 📄 PDF ingestion with page-aware chunking
- 🔍 Semantic search via Gemini embeddings + ChromaDB
- 🤖 Grounded answers with citations and confidence scores
- 🎤 Voice input via Web Speech API
- 📊 Telemetry: retrieval, generation, and STT latencies
- 🔄 AI provider fallback: Gemini → Groq → OpenRouter → HuggingFace

## Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in your API keys
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

## Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (primary LLM + embeddings) |
| `GROQ_API_KEY` | Groq API key (fallback LLM) |
| `OPENROUTER_API_KEY` | OpenRouter API key (fallback LLM) |
| `HUGGINGFACE_API_KEY` | HuggingFace API key (fallback LLM) |
| `FRONTEND_ORIGIN` | Allowed CORS origin for frontend |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/documents` | Upload and ingest a PDF |
| GET | `/api/documents` | List all documents |
| GET | `/api/documents/{id}` | Get document status |
| POST | `/api/query` | Ask a question |
| GET | `/api/queries/{id}` | Get query + citations |
| POST | `/api/transcribe` | Transcribe audio (faster-whisper) |

## Deployment

- **Backend**: Render.com (see `backend/render.yaml`)
- **Frontend**: GitHub Pages (see `.github/workflows/deploy-pages.yml`)

## Free-Tier Limitations

- **Render free tier**: Chroma DB and uploaded PDFs are **ephemeral** — they are lost on service restart. Use a persistent disk add-on for production.
- **GitHub Pages**: Static hosting only; backend must be deployed separately.
- **Gemini free tier**: Rate limits apply (15 RPM for embedding).
