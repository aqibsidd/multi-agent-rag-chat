# PLAN

Task: TASK-004

## Risk tier

LOW — a health-check endpoint, no auth/data surface.

## Specialist concerns

testing (per BACKLOG tag) — a test must exist and actually exercise the
endpoint.

## Objective

`backend/app/main.py`: FastAPI app with `GET /health` returning
`{"status": "ok"}`.

## Steps

1. `app/main.py`: `FastAPI()` instance, `/health` route.
2. `tests/test_main.py`: `TestClient` hits `/health`, asserts 200 and body.

## Acceptance criteria

- [ ] `GET /health` returns `{"status": "ok"}` with status 200
- [ ] Test exercises the real route via `TestClient`, not a stub
- [ ] `pytest -q` and `ruff check .` both clean

## Files expected to change

- `backend/app/main.py` (new)
- `backend/tests/test_main.py` (new)
