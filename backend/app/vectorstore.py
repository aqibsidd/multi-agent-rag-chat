import re

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
    if settings.embed_provider == "google":
        return 3072  # gemini-embedding-001
    return EMBEDDING_DIMS.get(settings.ollama_embed_model, 1024)


# Backwards compat for imports/tests.
EMBEDDING_DIM = 768

_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,  # Qdrant Cloud needs it
        )
    return _client


def resolve_collection(user_id: str = "") -> str:
    """Per-user Qdrant collection. Empty user_id keeps the legacy shared
    collection, so single-user local setups behave exactly as before.
    Pass `X-User-Id` (or body `user_id`) to isolate tenants."""
    base = settings.qdrant_collection
    clean = re.sub(r"[^a-z0-9_-]", "", (user_id or "").strip().lower())[:32]
    return f"{base}_u_{clean}" if clean else base


def ensure_collection(collection: str | None = None) -> None:
    name = collection or settings.qdrant_collection
    client = get_client()
    dim = get_embedding_dim()
    if not client.collection_exists(name):
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        return
    # Embedding model changed (e.g. 768 -> 1024)? Old vectors are
    # incompatible, so recreate rather than fail on insert.
    info = client.get_collection(name)
    params = getattr(getattr(info, "config", None), "params", None)
    vectors = getattr(params, "vectors", None)
    existing_dim = getattr(vectors, "size", None)
    if existing_dim is not None and existing_dim != dim:
        client.delete_collection(name)
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )


def get_vectorstore(collection: str | None = None) -> QdrantVectorStore:
    name = collection or settings.qdrant_collection
    ensure_collection(name)
    return QdrantVectorStore(
        client=get_client(),
        collection_name=name,
        embedding=get_embeddings(),
    )
