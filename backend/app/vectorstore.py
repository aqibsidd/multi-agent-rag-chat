from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.config import settings
from app.llm import get_embeddings

COLLECTION_NAME = "documents"
EMBEDDING_DIM = 768  # nomic-embed-text's output dimension

_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.qdrant_url)
    return _client


def ensure_collection() -> None:
    client = get_client()
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )


def get_vectorstore() -> QdrantVectorStore:
    ensure_collection()
    return QdrantVectorStore(
        client=get_client(),
        collection_name=COLLECTION_NAME,
        embedding=get_embeddings(),
    )
