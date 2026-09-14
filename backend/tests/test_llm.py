from app import llm as llm_module
from app.config import Settings
from app.llm import get_chat_model, get_embeddings


def _settings_with_keys(**overrides):
    base = {
        "ollama_base_url": "http://localhost:11434",
        "ollama_embed_model": "mxbai-embed-large",
        "nvidia_api_key": "n-test",
        "nvidia_chat_model": "nvidia/nemotron-3.5-lightning-30b-a3b",
        "nvidia_base_url": "https://integrate.api.nvidia.com/v1",
        "google_api_key": "g-test",
        "google_chat_model": "gemini-2.5-flash",
        "groq_api_key": "q-test",
        "groq_chat_model": "llama-3.3-70b-versatile",
        "qdrant_url": "http://localhost:6333",
        "qdrant_collection": "documents_pytest",
        "checkpoint_db_path": "checkpoints.db",
        "memory_auto_ingest": False,
        "port": 8000,
    }
    base.update(overrides)
    return Settings(**base)


def test_get_chat_model_fallback_order_nemotron_gemini_groq(monkeypatch):
    monkeypatch.setattr(llm_module, "settings", _settings_with_keys())
    model = get_chat_model()
    assert model.runnable.model_name == "nvidia/nemotron-3.5-lightning-30b-a3b"
    assert [f.model if hasattr(f, "model") else f.model_name for f in model.fallbacks] == [
        "gemini-2.5-flash",
        "llama-3.3-70b-versatile",
    ]


def test_get_chat_model_skips_providers_without_keys(monkeypatch):
    monkeypatch.setattr(
        llm_module, "settings", _settings_with_keys(groq_api_key="")
    )
    model = get_chat_model()
    assert len(model.fallbacks) == 1
    assert model.fallbacks[0].model == "gemini-2.5-flash"


def test_get_chat_model_constructs_without_any_keys(monkeypatch):
    monkeypatch.setattr(
        llm_module,
        "settings",
        _settings_with_keys(nvidia_api_key="", google_api_key="", groq_api_key=""),
    )
    model = get_chat_model()  # must not raise; fails only at invoke time
    assert model.fallbacks == []


def test_get_embeddings_uses_settings_defaults():
    embeddings = get_embeddings()
    assert embeddings.model == "mxbai-embed-large"
    assert embeddings.base_url == "http://localhost:11434"
