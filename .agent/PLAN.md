# PLAN

Task: TASK-001

## Risk tier

LOW — no schema, auth, secrets, or destructive operation. Local dev
environment setup only.

## Specialist concerns

none — doesn't touch backend logic, DB, security, frontend, or deployment;
it's environment setup.

## Objective

Create a Python virtual environment and `backend/requirements.txt` with all
dependencies the project needs, verified installable.

## Steps

1. Create `backend/` directory.
2. Attempt `python3.14 -m venv backend/.venv` (matches PROJECT.md's already-
   installed Python 3.14.6). If venv creation or the subsequent pip install
   fails on a wheel build, classify as DEPENDENCY (not CODE_BUG) and fall
   back to `python3.12` per BACKLOG.md's note, installing 3.12 via
   `brew install python@3.12` if not already present.
3. Write `backend/requirements.txt`:
   fastapi, uvicorn[standard], langgraph, langchain, langchain-ollama,
   langchain-qdrant, qdrant-client, python-dotenv, pytest, ruff.
4. `pip install -r backend/requirements.txt` inside the venv.
5. `ruff --version` and `pytest --version` both run inside the venv, to
   confirm the dev-tool half of the install is real, not just the app libs.

## Acceptance criteria

- [ ] `backend/.venv` exists and activates without error
- [ ] `backend/requirements.txt` lists all 10 packages above
- [ ] `pip install -r backend/requirements.txt` completes with exit 0
- [ ] `ruff --version` and `pytest --version` both succeed inside the venv

## Files expected to change

- `backend/requirements.txt` (new)
- `backend/.venv/` (new, gitignored)
