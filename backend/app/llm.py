from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI

from app.config import settings


def get_chat_model(temperature: float = 0.3):
    primary = ChatOpenAI(
        model=settings.nvidia_chat_model,
        base_url=settings.nvidia_base_url,
        api_key=settings.nvidia_api_key or "not-set",
        temperature=temperature,
    )
    fallback = ChatOllama(
        model=settings.ollama_fallback_chat_model,
        base_url=settings.ollama_base_url,
        temperature=temperature,
    )
    return primary.with_fallbacks([fallback])


def get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=settings.ollama_embed_model,
        base_url=settings.ollama_base_url,
    )
