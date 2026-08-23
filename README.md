# Multi-Agent RAG Chat

A fully local, multi-agent RAG chatbot. A supervisor routes each message to
either a plain chat agent or a document-retrieval agent; retrieval answers
go through a grounding grader that rewrites the query and retries once if
the answer isn't actually supported by what was retrieved, and admits it
doesn't know rather than hallucinating if it's still ungrounded after that.

Built as a learning/portfolio project — see `.agent/PROJECT.md` and
`.agent/DECISIONS.md` for the full design rationale.

## Architecture

```
React (Vite, :5173) --> FastAPI (:8000) --> LangGraph --> Ollama (:11434)
                                                 |
                                          Qdrant (:6333, Docker)

Graph:
  supervisor --route: chat--> chat_agent --> END
  supervisor --route: rag--> rag_agent --> grader --grounded--> END
                                 ^              |
                                 |--- retry -----+ (ungrounded, first attempt)
                                                 |
                                            give_up --> fallback --> END
                                            (ungrounded, second attempt)
```

Stack: Python/FastAPI/LangGraph backend, React/Vite frontend, Qdrant
vector store, Ollama for both chat (`llama3.2`) and embeddings
(`nomic-embed-text`) — fully offline, zero API cost.

## Setup

1. **Ollama** (chat + embedding models):
   ```bash
   brew install ollama
   ollama serve                    # leave running in its own terminal
   ollama pull llama3.2
   ollama pull nomic-embed-text
   ```

2. **Qdrant** (via Docker — make sure Docker Desktop is running first):
   ```bash
   docker compose up -d
   ```
   Dashboard: http://localhost:6333/dashboard

3. **Backend**:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

4. **Frontend**:
   ```bash
   cd frontend
   npm install
   ```

## Run

```bash
# terminal 1
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

# terminal 2
cd frontend && npm run dev
```

Open http://localhost:5173.

## Demo flow

1. Upload a `.txt`, `.md`, or `.pdf` file — it's chunked, embedded, and
   stored in Qdrant.
2. Ask a question the document answers — trace shows
   `supervisor → rag_agent → grader`, answer cites source chunks.
3. Say "hi, how are you?" — trace shows `supervisor → chat_agent`, no
   retrieval call.
4. Ask something the document can't answer — the agent says so honestly
   instead of making something up.

All four of the above were verified against the real running stack (real
Ollama inference, real Qdrant retrieval), not just mocked tests — see
`.agent/PROGRESS.md`'s TASK-020 entry.

## Tests

```bash
cd backend && source .venv/bin/activate
pytest -q       # 28 tests
ruff check .
```

## Known scope decisions

These were deliberate, disclosed trade-offs, not oversights — see
`.agent/PROGRESS.md` for the reasoning behind each:

- **Streaming is per-agent, not per-token.** Every graph node calls the
  LLM with `.invoke()` (blocking), since the supervisor and grader need
  complete text before deciding routing/groundedness. The SSE stream
  delivers each node's full output as it finishes, plus a live trace of
  which agent is running — not token-by-token generation.
- **PDF text-extraction fidelity isn't unit-tested.** Building a valid,
  text-bearing PDF fixture would need a rendering dependency (e.g.
  `reportlab`) just for a test. Covered by a blank-PDF smoke test instead;
  verify with a real PDF of your own.
- **No auth, single-user, local-only.** This is a demo/portfolio scope,
  not a production deployment (see `.agent/PROJECT.md`'s "Out of scope").

## Project workflow

This project was built with the `loop-engineer-aqib` skill: an `.agent/`
directory of markdown files (`BACKLOG.md`, `STATE.md`, `PLAN.md`,
`PROGRESS.md`, `DECISIONS.md`, `ERRORS.md`) acts as persistent state for a
one-transition-per-iteration build loop. See `.agent/PROGRESS.md` for a
full history of every task, including the dependency issues hit and fixed
along the way (ERR-001, ERR-002).
