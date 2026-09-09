from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.config import settings
from app.llm import get_embeddings

EMBEDDING_DIMS = {
    "nomic-embed-text": 768,
    "mxbai-embed-large": 1024,
    "bge-m3": 1024,
    "bge-small-en-v1.5": 384,
    "all-minilm": 384,
}


def get_embedding_dim() -> int:
    return EMBEDDING_DIMS.get(settings.ollama_embed_model, 1024)


# Backwards compat for imports/tests.
EMBEDDING_DIM = 768

_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.qdrant_url)
    return _client


def ensure_collection() -> None:
    client = get_client()
    dim = get_embedding_dim()
    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        return
    # Embedding model changed (e.g. 768 -> 1024)? Old vectors are
    # incompatible, so recreate rather than fail on insert.
    info = client.get_collection(settings.qdrant_collection)
    params = getattr(getattr(info, "config", None), "params", None)
    vectors = getattr(params, "vectors", None)
    existing_dim = getattr(vectors, "size", None)
    if existing_dim is not None and existing_dim != dim:
        client.delete_collection(settings.qdrant_collection)
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )


def get_vectorstore() -> QdrantVectorStore:
    ensure_collection()
    return QdrantVectorStore(
        client=get_client(),
        collection_name=settings.qdrant_collection,
        embedding=get_embeddings(),
    )
