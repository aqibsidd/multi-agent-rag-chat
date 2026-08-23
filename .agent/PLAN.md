# PLAN

Task: TASK-007

## Risk tier

MEDIUM — creates a persistent collection in an external service (Qdrant).
Not HIGH: no schema migration on existing data, easily dropped/recreated
in a dev environment, no destructive operation.

## Specialist concerns

database — collection creation must be idempotent (safe to call every
startup) and match the real embedding dimension.

## Objective

`app/vectorstore.py`: single place that owns the Qdrant collection and
hands back a LangChain-compatible vector store, for `app/ingest.py`
(TASK-008) and `rag_agent` (TASK-013) to share.

## Steps

1. `get_client()` — singleton `QdrantClient(url=settings.qdrant_url)`.
2. `ensure_collection()` — idempotent: `client.collection_exists(...)`
   before `create_collection(...)`, vector size 768 (nomic-embed-text's
   real dimension, confirmed against langchain_qdrant's actual
   `QdrantVectorStore.__init__` signature before writing this — matches
   `distance=Distance.COSINE`, its own default).
3. `get_vectorstore()` — calls `ensure_collection()`, returns a
   `QdrantVectorStore` wrapping the client + `get_embeddings()`.
4. Test against the **real, live** Qdrant (it's actually running — TASK-005
   just confirmed this) rather than mocking: create the collection twice
   (idempotency), confirm it exists via the client directly.

## Acceptance criteria

- [ ] `ensure_collection()` is idempotent — calling it twice doesn't error
- [ ] Collection exists in Qdrant with vector size 768 after calling it
- [ ] `get_vectorstore()` returns a `QdrantVectorStore` instance
- [ ] `pytest -q` and `ruff check .` clean

## Files expected to change

- `backend/app/vectorstore.py` (new)
- `backend/tests/test_vectorstore.py` (new)
