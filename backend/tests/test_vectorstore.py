from langchain_qdrant import QdrantVectorStore

from app.config import settings
from app.vectorstore import (
    ensure_collection,
    get_client,
    get_embedding_dim,
    get_vectorstore,
    resolve_collection,
)


def test_ensure_collection_is_idempotent():
    ensure_collection()
    ensure_collection()  # second call must not raise

    client = get_client()
    assert client.collection_exists(settings.qdrant_collection)

    info = client.get_collection(settings.qdrant_collection)
    assert info.config.params.vectors.size == get_embedding_dim()


def test_get_vectorstore_returns_qdrant_vectorstore():
    store = get_vectorstore()
    assert isinstance(store, QdrantVectorStore)


def test_resolve_collection_isolates_users():
    assert resolve_collection("") == settings.qdrant_collection
    assert resolve_collection("Aqib_1").startswith(settings.qdrant_collection + "_u_")
    assert resolve_collection("a@b!c") == f"{settings.qdrant_collection}_u_abc"
    # Same user, different sessions → same namespace (facts shared across
    # a user's sessions, never across users).
    assert resolve_collection("aqib") == resolve_collection("AQIB ")
