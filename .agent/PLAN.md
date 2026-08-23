# PLAN

Task: TASK-009

## Risk tier

MEDIUM — accepts arbitrary file uploads (multipart). No auth on this
dev-only project (PROJECT.md scope), but still validate content type
handling doesn't crash on garbage input.

## Specialist concerns

backend, testing (per BACKLOG tags).

## Objective

`POST /ingest/text` and `POST /ingest/file` on the FastAPI app, both
calling `app.ingest.ingest_text`.

## Steps

1. Add `pypdf` to requirements.txt (needed for `.pdf` text extraction —
   not previously listed, same class of gap as ERR-001).
2. `POST /ingest/text`: Pydantic body `{text, source}`, calls
   `ingest_text`, returns `{"chunks_added": N}`.
3. `POST /ingest/file`: multipart upload. `.txt`/`.md` decoded as UTF-8;
   `.pdf` extracted via `pypdf.PdfReader`. Returns
   `{"chunks_added": N, "filename": ...}`.
4. Tests: `/ingest/text` end-to-end (real ingest, confirmed retrievable);
   `/ingest/file` with a real `.txt` upload end-to-end.

## Known scope limit

Genuine PDF text-extraction fidelity (a real multi-page PDF with real
text) isn't covered by an automated test — building a valid, text-bearing
PDF fixture needs a rendering library (e.g. `reportlab`), and adding a
whole dependency just to manufacture a test fixture isn't worth it for
this project's scope. The `.pdf` code path is exercised with a blank
PDF (proves it doesn't crash and returns a string) plus manual testing
with a real PDF from `~/Downloads` at TASK-022's demo step.

## Acceptance criteria

- [ ] `/ingest/text` round-trips: posted text is retrievable afterward
- [ ] `/ingest/file` with a `.txt` file round-trips the same way
- [ ] `.pdf` path doesn't crash on a valid (even blank) PDF
- [ ] `pytest -q` and `ruff check .` clean

## Files expected to change

- `backend/requirements.txt` (add pypdf)
- `backend/app/main.py` (add two routes)
- `backend/tests/test_ingest_endpoints.py` (new)
