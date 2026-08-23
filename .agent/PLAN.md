# PLAN

Task: TASK-020

## Risk tier

LOW — verification only, no new code paths.

## Specialist concerns

testing (per BACKLOG tag).

## Objective

Prove the whole stack works as a real running process, not just under
pytest's in-process `TestClient` — start the actual server, hit it over
real HTTP with real Ollama inference and real Qdrant, exercise all four
scenarios from PROJECT.md's success criteria.

## Steps

1. Start `uvicorn app.main:app` for real (background process), confirm
   `/health`.
2. `POST /ingest/text` with a real fact; confirm it lands.
3. `POST /chat/stream`, grounded question -> real trace + real citation.
4. `POST /chat/stream`, "hi, how are you?" -> real chat path, no
   retrieval.
5. `POST /chat/stream`, a genuinely unanswerable question -> this is the
   one scenario not already covered by a scripted-fake-LLM test: real
   Ollama judging its own groundedness, for real, with no scripted answer.
6. `npm run dev` starts without crashing (frontend process check).

## Honest scope note

No browser automation tool is active in this session, so the actual pixel-
level UI (badge colors, layout) isn't clicked through in a real browser.
What TASK-020 verifies instead: the exact wire contract the frontend's
already-reviewed code consumes, exercised live end-to-end with real
inference (not mocked) — which is the part that couldn't be proven by
unit tests alone. Frontend code review + build success (TASK-018/019)
plus this live backend proof together cover the acceptance criteria; a
literal click-through is left for the user's own first run.

## Acceptance criteria

- [ ] Real server responds on `/health`
- [ ] Real ingest -> real retrieval works
- [ ] Real grounded RAG turn produces a cited answer
- [ ] Real chat turn produces no retrieval call
- [ ] Real unanswerable question is handled honestly (retry then fallback,
      or a grounded-enough answer if the model surprises us — either is
      fine, a hallucinated confident wrong answer is not)
- [ ] `npm run dev` starts cleanly

## Files expected to change

None — this is a verification task.
