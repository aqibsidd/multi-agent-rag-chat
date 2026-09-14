from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI

from app.config import settings


def get_chat_model(temperature: float = 0.3):
    """Nemotron -> Gemini Flash -> Groq Llama. All API, no local LLM, so the
    backend deploys anywhere with just keys. Providers without a configured
    key are skipped, so local/test envs still construct fine."""
    primary = ChatOpenAI(
        model=settings.nvidia_chat_model,
        base_url=settings.nvidia_base_url,
        api_key=settings.nvidia_api_key or "not-set",
        temperature=temperature,
    )
    fallbacks = []
    if settings.google_api_key:
        fallbacks.append(
            ChatGoogleGenerativeAI(
                model=settings.google_chat_model,
                google_api_key=settings.google_api_key,
                temperature=temperature,
            )
        )
    if settings.groq_api_key:
        fallbacks.append(
            ChatGroq(
                model=settings.groq_chat_model,
                api_key=settings.groq_api_key,
                temperature=temperature,
            )
        )
    return primary.with_fallbacks(fallbacks)


def get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=settings.ollama_embed_model,
        base_url=settings.ollama_base_url,
    )
