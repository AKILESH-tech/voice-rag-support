from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.ai.provider import FallbackAIProvider
from app.config import settings
from app.db.database import init_db
from app.api.routes import router
from app.ingestion.sample_kb import bootstrap_sample_kb


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    bootstrap_sample_kb()
    yield


app = FastAPI(title="Voice RAG Support", version="1.0.0", lifespan=lifespan)
provider = FallbackAIProvider()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "voice-rag-support"}


@app.get("/health/ai-fallback")
def ai_fallback_health():
    return {
        "provider_order": provider.configured_provider_order(),
        "gemini_models": provider.gemini_model_chain(),
        "configured": {
            "gemini": bool(settings.gemini_api_key),
            "groq": bool(settings.groq_api_key),
            "openrouter": bool(settings.openrouter_api_key),
            "huggingface": bool(settings.huggingface_api_key),
        },
    }
