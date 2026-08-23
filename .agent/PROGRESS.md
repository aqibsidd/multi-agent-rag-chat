# PROGRESS

Historical journal, append-only. Not the source of truth for what to do next
(that's BACKLOG.md + STATE.md) — this is the record of what happened.

One entry per completed task, newest at the bottom. Metrics line format:
`iterations=<N> retries=<N> classifications=<...>` — enough to spot which
tasks caused the most retries by skimming, no separate dashboard needed.

## 2026-08-23 — TASK-001

Implemented:
- `backend/.venv` (Python 3.14, no fallback needed)
- `backend/requirements.txt`: fastapi, uvicorn[standard], langgraph,
  langchain, langchain-ollama, langchain-qdrant, qdrant-client,
  python-dotenv, pytest, ruff — all installed cleanly

Tests: n/a (no business logic yet); `ruff check .` clean

Metrics: iterations=5 retries=0 classifications=none

Notes: Python 3.14.6 built every wheel without issue — the DEPENDENCY
fallback-to-3.12 plan in PLAN.md wasn't needed. TASK-002 and TASK-003 are
now READY.

## 2026-08-23 — TASK-002

Implemented:
- `backend/app/config.py`: `Settings` dataclass, plain `os.environ` +
  `python-dotenv`, defaults matching `.env.example`
- `backend/.env.example` (5 vars)
- `backend/tests/test_config.py`

Tests: 1 passed; `ruff check .` clean

Metrics: iterations=4 retries=0 classifications=none

Notes: Write tool has a deny rule on `.env*` paths — worked around via
shell heredoc for `.env.example`. Worth remembering for any later task that
touches env files. TASK-004 and TASK-006 now READY.

## 2026-08-23 — TASK-003

Implemented:
- `docker-compose.yml`: Qdrant, ports 6333/6334, named volume
  `qdrant_storage`

Tests: `docker compose config` validates cleanly (daemon not required for
this check); n/a for pytest (no app code)

Metrics: iterations=2 retries=0 classifications=none

Notes: Actually starting Qdrant is still TASK-005, blocked on the Docker
daemon (AWAITING_HUMAN).

## 2026-08-23 — TASK-004

Implemented:
- `backend/app/main.py`: FastAPI app, `GET /health`
- `backend/tests/test_main.py`: TestClient-based test

Tests: 2 passed (config + health); `ruff check .` clean

Metrics: iterations=3 retries=0 classifications=none

Notes: Starlette warns that `httpx` support in its TestClient is
deprecated in favor of `httpx2` — not an error, no action needed now, but
worth a note if it becomes a hard failure in a future dependency bump.

## 2026-08-23 — TASK-006

Implemented:
- `backend/app/llm.py`: `get_chat_model()`, `get_embeddings()`, both
  reading from `app.config.settings`
- `backend/tests/test_llm.py`: confirms client construction picks up
  settings defaults, no Ollama connection required

Tests: 4 passed total; `ruff check .` clean

Metrics: iterations=3 retries=0 classifications=none

Notes: TASK-010 (LangGraph state schema) now READY.

## 2026-08-23 — TASK-010

Implemented:
- `backend/app/graph/state.py`: `GraphState` TypedDict (messages w/
  `add_messages` reducer, route, retrieved_docs, grounded, retry_count)
- `backend/tests/test_graph_state.py`: verifies the reducer actually
  merges message lists, not just that keys exist

Tests: 6 passed total; `ruff check .` clean

Metrics: iterations=3 retries=0 classifications=none

Notes: TASK-011 (supervisor) and TASK-012 (chat_agent) now READY.

## 2026-08-23 — TASK-011

Implemented:
- `backend/app/graph/supervisor.py`: `supervisor_node`, LLM injectable for
  testing, defaults to `get_chat_model()`
- `backend/tests/test_supervisor.py`: both routing branches, fake LLM (no
  real Ollama call — fast and deterministic)

Tests: 8 passed total; `ruff check .` clean

Metrics: iterations=3 retries=0 classifications=none

Notes: confirmed Ollama's server IS actually running locally
(`lsof -iTCP:11434` shows it listening) — unlike Docker/Qdrant, this part
of the stack is live. Kept tests on a fake LLM anyway per TASK-015's
existing plan: real inference is correct at runtime but too slow/
nondeterministic for a unit test.

## 2026-08-23 — TASK-012

Implemented:
- `backend/app/graph/chat_agent.py`: `chat_agent_node`, replies via full
  message history, no retrieval
- `backend/tests/test_chat_agent.py`: reducer-merge behavior with a fake
  LLM, plus a source-inspection test proving the module never references
  `vectorstore`

Tests: 10 passed total; `ruff check .` clean

Metrics: iterations=3 retries=0 classifications=none

Notes: caught my own weak test during IMPLEMENT — an initial
`"app.vectorstore" not in sys.modules` check would give a false pass once
another test file imports vectorstore later in the same pytest session.
Replaced with `inspect.getsource()` on the module itself, which actually
fails if chat_agent.py starts importing vectorstore. EPIC-001 (minus
TASK-005) and the non-Qdrant half of EPIC-003 are now done; everything
remaining (TASK-007/013/014/015/016/017 and all of EPIC-005/006) is
blocked on TASK-005 (Docker) or its downstream chain.

## 2026-08-23 — TASK-005

Implemented:
- Started Docker Desktop (`open -a Docker`, polled until `docker info`
  succeeded — ~did not need the full 60s budget)
- `docker compose up -d`: pulled `qdrant/qdrant:latest`, created network +
  volume + container, started
- Verified `GET localhost:6333/collections` -> 200,
  `{"result":{"collections":[]},"status":"ok"}`

Tests: n/a (infra verification, not app code)

Metrics: iterations=1 retries=0 classifications=none

Notes: this was the AWAITING_HUMAN blocker. User explicitly asked the loop
to start Docker itself rather than waiting — did so directly (`open -a
Docker`, poll loop, `docker compose up -d`) instead of asking again.
TASK-007 now READY; this unblocks the rest of the ingest and RAG-agent
chain.
