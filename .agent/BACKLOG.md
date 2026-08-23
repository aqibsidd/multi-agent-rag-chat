# BACKLOG

Status values: `READY` · `BLOCKED` · `IN_PROGRESS` · `DONE` · `AWAITING_HUMAN`.
Tag `needs-human` = touches secrets, destructive ops, or requires something
only a human can do/decide.

## EPIC-001 Foundation

### TASK-001
- [x] Python venv + `backend/requirements.txt` (fastapi, uvicorn, langgraph,
      langchain, langchain-ollama, langchain-qdrant, qdrant-client,
      python-dotenv, pytest, ruff). Try Python 3.14 first; if wheels fail to
      build, fall back to 3.12 (classify as DEPENDENCY, not a code bug).
- Priority: P0
- Status: DONE
- Dependencies: none
- Tags: none

### TASK-002
- [x] `backend/.env.example` + `app/config.py` (Ollama base URL, chat model,
      embed model, Qdrant URL, port). `.env` gitignored.
- Priority: P0
- Status: DONE
- Dependencies: TASK-001
- Tags: none

### TASK-003
- [x] `docker-compose.yml` at repo root: Qdrant service, port 6333, named
      volume for persistence.
- Priority: P0
- Status: DONE
- Dependencies: TASK-001
- Tags: none

### TASK-004
- [x] FastAPI app skeleton (`app/main.py`) with `GET /health` returning
      `{"status": "ok"}`, plus a test for it.
- Priority: P0
- Status: DONE
- Dependencies: TASK-002
- Tags: testing

### TASK-005
- [x] Start Qdrant (`docker compose up -d`) and verify
      `curl localhost:6333/collections` responds.
- Priority: P0
- Status: DONE
- Dependencies: TASK-003
- Tags: needs-human
- Note: Docker daemon was started by the user's request ("do yourself check
  docker") on 2026-08-23. `docker compose up -d` succeeded; GET
  /collections returns 200 with an empty collection list.

## EPIC-002 Ingest

### TASK-006
- [x] `app/llm.py` — single factory for the Ollama chat model and
      embeddings client. No agent constructs these directly (AGENTS.md rule).
- Priority: P0
- Status: DONE
- Dependencies: TASK-002
- Tags: none

### TASK-007
- [x] `app/vectorstore.py` — Qdrant client, collection create-if-missing,
      matching the embedding dimension for `nomic-embed-text`.
- Priority: P0
- Status: DONE
- Dependencies: TASK-005, TASK-006
- Tags: database

### TASK-008
- [x] `app/ingest.py` — chunk (recursive char splitter), embed, upsert to
      Qdrant with source metadata.
- Priority: P0
- Status: DONE
- Dependencies: TASK-007
- Tags: none

### TASK-009
- [ ] `POST /ingest/file` (multipart, txt/md/pdf) and `POST /ingest/text`
      endpoints + tests.
- Priority: P0
- Status: READY
- Dependencies: TASK-008
- Tags: backend, testing

## EPIC-003 Agent graph

### TASK-010
- [x] LangGraph state schema (`app/graph/state.py`): messages, route,
      retrieved docs, grounded flag, retry count.
- Priority: P0
- Status: DONE
- Dependencies: TASK-006
- Tags: none

### TASK-011
- [x] Supervisor node: classifies a message as chit-chat vs needs-docs,
      sets `route`.
- Priority: P0
- Status: DONE
- Dependencies: TASK-010
- Tags: testing

### TASK-012
- [x] `chat_agent` node: plain conversational reply, no retrieval.
- Priority: P0
- Status: DONE
- Dependencies: TASK-010
- Tags: none

### TASK-013
- [x] `rag_agent` node: retrieve top-4 from Qdrant, generate a grounded
      answer with citations.
- Priority: P0
- Status: DONE
- Dependencies: TASK-007, TASK-010
- Tags: none

### TASK-014
- [x] `grader` node + conditional edge: checks the answer is grounded in
      retrieved chunks; if not, rewrites the query and retries `rag_agent`
      exactly once, then answers "I don't know" if still ungrounded.
- Priority: P0
- Status: DONE
- Dependencies: TASK-013
- Tags: testing

### TASK-015
- [x] Wire the full graph (`app/graph/build.py`); unit tests with a fake
      LLM verifying both routing branches and the retry edge.
- Priority: P0
- Status: DONE
- Dependencies: TASK-011, TASK-012, TASK-014
- Tags: testing

## EPIC-004 API

### TASK-016
- [ ] `POST /chat/stream` — SSE endpoint streaming tokens plus per-node
      trace events (`{"event":"agent","node":"rag_agent"}` etc.) so the
      frontend can show which agent handled the turn.
- Priority: P0
- Status: READY
- Dependencies: TASK-015
- Tags: backend

### TASK-017
- [ ] Integration test hitting `/chat/stream` end-to-end against a real
      ingested doc, asserting the trace shows `supervisor -> rag_agent ->
      grader` for a document question and `supervisor -> chat_agent` for
      small talk.
- Priority: P0
- Status: BLOCKED
- Dependencies: TASK-016, TASK-009
- Tags: testing

## EPIC-005 Frontend

### TASK-018
- [ ] Extract the frontend from `~/Downloads/rag-chat-app.zip` into
      `frontend/`, point its API base at the new backend, confirm it still
      builds.
- Priority: P1
- Status: BLOCKED
- Dependencies: TASK-016
- Tags: frontend

### TASK-019
- [ ] Add an agent-trace badge and sources panel to the chat UI, wired to
      the new SSE trace event shape from TASK-016.
- Priority: P1
- Status: BLOCKED
- Dependencies: TASK-018
- Tags: frontend

### TASK-020
- [ ] `npm run build` passes; manual smoke test of the full flow (upload,
      ask grounded question, ask small talk, ask an unanswerable question).
- Priority: P1
- Status: BLOCKED
- Dependencies: TASK-019
- Tags: testing

## EPIC-006 Demo

### TASK-021
- [ ] README: setup, run, and demo-flow instructions.
- Priority: P2
- Status: BLOCKED
- Dependencies: TASK-020
- Tags: none

### TASK-022
- [ ] Seed a real doc, capture screenshots of the Qdrant dashboard and the
      chat UI's agent trace for the portfolio writeup.
- Priority: P2
- Status: BLOCKED
- Dependencies: TASK-021
- Tags: needs-human
- Note: requires a human to look at the running UI/dashboard and choose
  what to screenshot.
