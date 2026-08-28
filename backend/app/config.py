from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"
    gemini_fallback_models: str = "gemini-1.5-flash-8b,gemini-1.5-pro"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    openrouter_api_key: str | None = None
    openrouter_model: str = "meta-llama/llama-3.1-8b-instruct:free"
    huggingface_api_key: str | None = None
    huggingface_model: str = "HuggingFaceH4/zephyr-7b-beta"
    ai_provider_order: str = "gemini,groq,openrouter,huggingface"
    ai_timeout_seconds: float = 25.0
    database_url: str = "sqlite:///./voice_rag.db"
    frontend_origin: str = "http://localhost:5174"
    chroma_path: str = "./chroma_db"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5
    retrieval_threshold: float = 0.4
    firebase_project_id: str = ""
    google_application_credentials: str | None = None
    firebase_allow_dev_auth: bool = True

    model_config = {"env_file": ".env"}

settings = Settings()
