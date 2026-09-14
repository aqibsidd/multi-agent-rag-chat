import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_embed_model: str = os.environ.get("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
    # Embeddings provider: "ollama" (local dev) or "google" (Render/cloud —
    # same GOOGLE_API_KEY as the chat fallback, no extra key).
    embed_provider: str = os.environ.get("EMBED_PROVIDER", "ollama").strip().lower()
    google_embed_model: str = os.environ.get(
        "GOOGLE_EMBED_MODEL", "models/text-embedding-004"
    )
    nvidia_api_key: str = os.environ.get("NVIDIA_API_KEY", "")
    nvidia_chat_model: str = os.environ.get(
        "NVIDIA_CHAT_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b"
    )
    nvidia_base_url: str = os.environ.get(
        "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
    )
    google_api_key: str = os.environ.get("GOOGLE_API_KEY", "")
    google_chat_model: str = os.environ.get("GOOGLE_CHAT_MODEL", "gemini-2.5-flash")
    groq_api_key: str = os.environ.get("GROQ_API_KEY", "")
    groq_chat_model: str = os.environ.get(
        "GROQ_CHAT_MODEL", "llama-3.3-70b-versatile"
    )
    qdrant_url: str = os.environ.get("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: str = os.environ.get("QDRANT_API_KEY", "")
    qdrant_collection: str = os.environ.get("QDRANT_COLLECTION", "documents")
    checkpoint_db_path: str = os.environ.get("CHECKPOINT_DB_PATH", "checkpoints.db")
    memory_auto_ingest: bool = (
        os.environ.get("MEMORY_AUTO_INGEST", "true").strip().lower() == "true"
    )
    relevance_min_score: float = float(os.environ.get("RELEVANCE_MIN_SCORE", "0.5"))
    max_upload_mb: int = int(os.environ.get("MAX_UPLOAD_MB", "10"))
    checkpointer_url: str = os.environ.get("CHECKPOINTER_URL", "")
    port: int = int(os.environ.get("PORT", "8000"))


settings = Settings()
