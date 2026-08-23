from app.llm import get_chat_model, get_embeddings


def test_get_chat_model_uses_settings_defaults():
    model = get_chat_model()
    assert model.model == "llama3.2"
    assert model.base_url == "http://localhost:11434"


def test_get_embeddings_uses_settings_defaults():
    embeddings = get_embeddings()
    assert embeddings.model == "nomic-embed-text"
    assert embeddings.base_url == "http://localhost:11434"
