# PLAN

Task: TASK-021

## Risk tier

LOW — documentation only.

## Specialist concerns

none.

## Objective

`README.md`: setup, run, and demo-flow instructions accurate to what was
actually built and verified in TASK-020, not aspirational.

## Steps

1. Architecture summary (the ADR-004 graph diagram, in text).
2. Setup: Ollama models, Docker/Qdrant, Python venv, `.env`.
3. Run: backend (`uvicorn`), frontend (`npm run dev`).
4. Demo flow: upload a doc, ask a grounded question, ask small talk, ask
   an unanswerable question — mirrors exactly what TASK-020 verified live.
5. Note the disclosed scope decisions from PROGRESS.md (incremental vs
   token-level streaming, PDF fidelity untested) so a reader isn't
   surprised later.

## Acceptance criteria

- [ ] A reader with a clean checkout can follow it to a working app
- [ ] Every claim in it was actually verified in this run (no
      aspirational/untested claims)

## Files expected to change

- `README.md` (new)
