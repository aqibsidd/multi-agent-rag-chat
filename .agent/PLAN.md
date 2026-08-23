# PLAN

Task: TASK-002

## Risk tier

LOW — config scaffolding only. No real secrets involved (Ollama and Qdrant
are both local, no API keys needed); `.env.example` documents shape, not
values.

## Specialist concerns

none — no business logic, no DB/security/frontend/deployment surface yet.

## Objective

Create `backend/.env.example` and `backend/app/config.py` so every later
task reads configuration from one place instead of hardcoding URLs/models.

## Steps

1. Create `backend/app/__init__.py` (package init).
2. Write `backend/.env.example` with: `OLLAMA_BASE_URL`,
   `OLLAMA_CHAT_MODEL`, `OLLAMA_EMBED_MODEL`, `QDRANT_URL`, `PORT`.
3. Write `backend/app/config.py` using `pydantic-settings`-free approach
   (plain `os.environ.get` + `python-dotenv`'s `load_dotenv()`, since
   `pydantic-settings` isn't in requirements.txt and adding a new dep for
   this is unjustified) — a `Settings` dataclass with defaults matching
   `.env.example`.
4. `backend/tests/test_config.py`: confirms `Settings()` loads the correct
   defaults when no `.env` is present.

## Acceptance criteria

- [ ] `backend/.env.example` documents all 5 variables
- [ ] `backend/app/config.py` exposes a `Settings` object with sane
      defaults (`OLLAMA_BASE_URL=http://localhost:11434`,
      `OLLAMA_CHAT_MODEL=llama3.2`, `OLLAMA_EMBED_MODEL=nomic-embed-text`,
      `QDRANT_URL=http://localhost:6333`, `PORT=8000`)
- [ ] `pytest -q` passes the new config test
- [ ] `ruff check .` clean

## Files expected to change

- `backend/.env.example` (new)
- `backend/app/__init__.py` (new)
- `backend/app/config.py` (new)
- `backend/tests/test_config.py` (new)
