from app.config import Settings


def test_settings_defaults():
    s = Settings()
    assert s.ollama_base_url == "http://localhost:11434"
    assert s.nvidia_chat_model == "nvidia/nemotron-3.5-lightning-30b-a3b"
    assert s.nvidia_base_url == "https://integrate.api.nvidia.com/v1"
    assert s.google_chat_model == "gemini-2.5-flash"
    assert s.groq_chat_model == "llama-3.3-70b-versatile"
    assert s.ollama_embed_model == "mxbai-embed-large"
    assert s.embed_provider == "ollama"
    assert s.google_embed_model == "models/text-embedding-004"
    assert s.qdrant_url == "http://localhost:6333"
    assert s.qdrant_api_key == ""
    assert s.memory_auto_ingest is False  # conftest forces false for hermetic tests
    assert s.port == 8000
