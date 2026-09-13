from app.config import Settings


def test_settings_defaults():
    s = Settings()
    assert s.ollama_base_url == "http://localhost:11434"
    assert s.ollama_fallback_chat_model == "llama3.2"
    assert s.nvidia_chat_model == "nvidia/nemotron-3.5-lightning-30b-a3b"
    assert s.nvidia_base_url == "https://integrate.api.nvidia.com/v1"
    assert s.ollama_embed_model == "mxbai-embed-large"
    assert s.qdrant_url == "http://localhost:6333"
    assert s.memory_auto_ingest is False  # conftest forces false for hermetic tests
    assert s.relevance_min_score == 0.5
    assert s.max_upload_mb == 10
    assert s.checkpointer_url == ""
    assert s.port == 8000
