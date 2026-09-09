from app.llm import get_chat_model, get_embeddings


def test_get_chat_model_uses_settings_defaults():
    model = get_chat_model()
    assert model.runnable.model_name == "nvidia/nemotron-3.5-lightning-30b-a3b"
    assert model.fallbacks[0].model == "llama3.2"
    assert model.fallbacks[0].base_url == "http://localhost:11434"


def test_get_embeddings_uses_settings_defaults():
    embeddings = get_embeddings()
    assert embeddings.model == "mxbai-embed-large"
    assert embeddings.base_url == "http://localhost:11434"
