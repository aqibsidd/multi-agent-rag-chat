from langchain_qdrant import QdrantVectorStore

from app.vectorstore import (
    COLLECTION_NAME,
    EMBEDDING_DIM,
    ensure_collection,
    get_client,
    get_vectorstore,
)


def test_ensure_collection_is_idempotent():
    ensure_collection()
    ensure_collection()  # second call must not raise

    client = get_client()
    assert client.collection_exists(COLLECTION_NAME)

    info = client.get_collection(COLLECTION_NAME)
    assert info.config.params.vectors.size == EMBEDDING_DIM


def test_get_vectorstore_returns_qdrant_vectorstore():
    store = get_vectorstore()
    assert isinstance(store, QdrantVectorStore)
