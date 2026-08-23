# TESTING

## Before any task is marked complete

```
cd backend && source .venv/bin/activate
pytest -q
ruff check .
```

Frontend, when a task touches it:

```
cd frontend && npm run build
```

## Scoped test runs

```
pytest -q -k <keyword>
```

## Manual/integration checks (not automated, run when relevant)

```
curl -s localhost:8000/health
docker compose ps                       # Qdrant up?
curl -s localhost:6333/collections      # Qdrant reachable + collection exists?
```

## Completion requirement

All `pytest` tests pass. No `ruff` errors. No frontend build errors. A task
cannot reach Status: DONE otherwise.
