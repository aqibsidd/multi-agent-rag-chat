import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_fallback_chat_model: str = os.environ.get("OLLAMA_FALLBACK_CHAT_MODEL", "llama3.2")
    ollama_embed_model: str = os.environ.get("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
    nvidia_api_key: str = os.environ.get("NVIDIA_API_KEY", "")
    nvidia_chat_model: str = os.environ.get(
        "NVIDIA_CHAT_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b"
    )
    nvidia_base_url: str = os.environ.get(
        "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
    )
    qdrant_url: str = os.environ.get("QDRANT_URL", "http://localhost:6333")
    qdrant_collection: str = os.environ.get("QDRANT_COLLECTION", "documents")
    checkpoint_db_path: str = os.environ.get("CHECKPOINT_DB_PATH", "checkpoints.db")
    port: int = int(os.environ.get("PORT", "8000"))


settings = Settings()
