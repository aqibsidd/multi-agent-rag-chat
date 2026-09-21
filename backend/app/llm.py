from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI

from app.config import settings


def get_chat_model(temperature: float = 0.3):
    """Nemotron -> OpenRouter (one-line model switch) -> Gemini -> Groq.
    All API, no local LLM. Providers without a key are skipped, so
    local/test envs still construct fine. Set OPENROUTER_CHAT_MODEL to
    any OpenRouter slug to swap fallbacks without code."""
    primary = ChatOpenAI(
        model=settings.nvidia_chat_model,
        base_url=settings.nvidia_base_url,
        api_key=settings.nvidia_api_key or "not-set",
        temperature=temperature,
    )
    fallbacks = []
    if settings.openrouter_api_key:
        fallbacks.append(
            ChatOpenAI(
                model=settings.openrouter_chat_model,
                base_url=settings.openrouter_base_url,
                api_key=settings.openrouter_api_key,
                temperature=temperature,
            )
        )
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


def get_embeddings():
    """Ollama locally, Google on Render/cloud. Same key as the chat
    fallback — gemini-embedding-001 is 3072-dim, free tier."""
    if settings.embed_provider == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(
            model=settings.google_embed_model,
            google_api_key=settings.google_api_key or "not-set",
        )
    return OllamaEmbeddings(
        model=settings.ollama_embed_model,
        base_url=settings.ollama_base_url,
    )
