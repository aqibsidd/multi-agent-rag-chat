from app.config import Settings


def test_settings_defaults():
    s = Settings()
    assert s.ollama_base_url == "http://localhost:11434"
    assert s.ollama_chat_model == "llama3.2"
    assert s.ollama_embed_model == "nomic-embed-text"
    assert s.qdrant_url == "http://localhost:6333"
    assert s.port == 8000
