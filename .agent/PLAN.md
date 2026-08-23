# PLAN

Task: TASK-008

## Risk tier

LOW — writes to the dev Qdrant collection, easily wiped in a dev
environment; no destructive or irreversible operation.

## Specialist concerns

none.

## Objective

`app/ingest.py`: chunk raw text, embed, upsert to Qdrant with source
metadata — the shared pipeline both `/ingest/text` and `/ingest/file`
(TASK-009) will call.

## Steps

1. Add missing dependency `langchain-text-splitters` (ERR-001 — was
   omitted from TASK-001's requirements.txt).
2. `ingest_text(text: str, source: str) -> int`: `RecursiveCharacterTextSplitter`
   (chunk_size=1000, chunk_overlap=150) -> `Document` list with
   `{"source": source, "chunk": i}` metadata -> `get_vectorstore().add_documents(...)`
   -> returns chunk count.
3. Test against the real, live Qdrant (consistent with TASK-007): ingest a
   short text, confirm the chunk count returned and that a similarity
   search against the vectorstore actually retrieves it back.

## Acceptance criteria

- [ ] `ingest_text()` chunks, embeds, and upserts with correct metadata
- [ ] Returns the number of chunks added
- [ ] A similarity search after ingest finds the ingested content
- [ ] `pytest -q` and `ruff check .` clean

## Files expected to change

- `backend/requirements.txt` (add langchain-text-splitters)
- `backend/app/ingest.py` (new)
- `backend/tests/test_ingest.py` (new)
