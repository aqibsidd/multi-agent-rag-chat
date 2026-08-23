import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_chat_model: str = os.environ.get("OLLAMA_CHAT_MODEL", "llama3.2")
    ollama_embed_model: str = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    qdrant_url: str = os.environ.get("QDRANT_URL", "http://localhost:6333")
    port: int = int(os.environ.get("PORT", "8000"))


settings = Settings()
