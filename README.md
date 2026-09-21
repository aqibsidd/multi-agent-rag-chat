# Multi-Agent RAG Chat

A multi-agent RAG chatbot — hybrid local + cloud. A supervisor routes each
message to either a plain chat agent or a document-retrieval agent;
retrieval answers go through a grounding grader that rewrites the query and
retries once if the answer isn't actually supported by what was retrieved,
and admits it doesn't know rather than hallucinating if it's still
ungrounded after that. Supports conversation memory, cross-session fact
recall, OCR fallback for scanned PDFs, and an OpenRouter one-line model
switch.

Built as a learning/portfolio project — see `.agent/PROJECT.md` and
`.agent/DECISIONS.md` for the full design rationale.

## Architecture

```
React (Vite, :5173) --> FastAPI (:8000) --> LangGraph
                                           ├── Chat: NVIDIA Nemotron (primary)
                                           │        → OpenRouter (any model via OPENROUTER_CHAT_MODEL)
                                           │        → Gemini 2.5 Flash → Groq Llama-3.3-70b
                                           ├── Embeddings: Ollama mxbai-embed-large (1024-dim, local)
                                           │              or Google gemini-embedding-001 → 768-dim (cloud, EMBED_PROVIDER=google)
                                           └── Qdrant (local Docker :6333 or Qdrant Cloud)

Graph:
  supervisor --route: chat--> chat_agent --> END
  supervisor --route: rag--> rag_agent --> grader --grounded--> END
                                 ^              |
                                 |--- retry -----+ (ungrounded, first attempt)
                                                 |
                                            give_up --> fallback --> END
                                            (ungrounded, second attempt)

Memory: SQLite checkpoints (CHECKPOINT_DB_PATH, local) or Postgres (CHECKPOINTER_URL)
         + Qdrant user-facts (user-memory:{session}) for cross-session recall.
```

Stack: Python/FastAPI/LangGraph backend, React/Vite frontend, Qdrant
vector store, LangGraph state + SQLite/Postgres checkpoints.

## Setup

1. **Qdrant** (local Docker — make sure Docker Desktop is running first):
    ```bash
    docker compose up -d              # Qdrant :6333
    docker compose --profile with-postgres up -d  # optional: Postgres checkpointer
    ```
    Dashboard: http://localhost:6333/dashboard

2. **Embeddings:**
    - Local (default): Ollama `mxbai-embed-large` (1024-dim):
      ```bash
      brew install ollama
      ollama serve                    # leave running in its own terminal
      ollama pull mxbai-embed-large
      ```
    - Cloud (Render): set `EMBED_PROVIDER=google` + `GOOGLE_API_KEY` (uses
      `gemini-embedding-001` truncated to 768-dim, no Ollama needed)
    - Scanned PDFs/images: OCR fallback needs `brew install tesseract poppler`

3. **Backend:**
    ```bash
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    # set at least one chat key: NVIDIA_API_KEY or GOOGLE_API_KEY or GROQ_API_KEY or OPENROUTER_API_KEY
    # for one-line model switching: OPENROUTER_CHAT_MODEL=anthropic/claude-3.5-sonnet
    ```

4. **Frontend:**
    ```bash
    cd frontend
    npm install
    ```

## Run

```bash
# option A: two terminals
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload
cd frontend && npm run dev              # :5173 proxies /chat,/ingest to :8000

# option B: PM2 (one command for both)
npm install -g pm2
pm2 start ecosystem.config.js
pm2 logs
```

Open http://localhost:5173.

## Deploy (Render)

Uses `render.yaml` Blueprint (free Python backend + free static frontend):

1. `OPENROUTER` / `GOOGLE` / `NVIDIA` / `GROQ` API keys, `QDRANT_URL` + `QDRANT_API_KEY`
   from Qdrant Cloud free cluster.
2. Backend: Root Dir `backend`, Start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`,
   env `EMBED_PROVIDER=google`.
3. Frontend: Root Dir `frontend`, Publish `dist`, env `VITE_API_URL=https://<backend>.onrender.com` (+ redeploy).

Requires re-upload of docs after switching `EMBED_PROVIDER` (dim changes recreate the collection).

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
pytest -q       # 46 tests (includes memory, rewrite, relevance gate, recall eval)
ruff check .
```

## Known scope decisions

These were deliberate, disclosed trade-offs, not oversights — see
`.agent/PROGRESS.md` for the reasoning behind each:

- **Streaming is per-node with LLM token streaming inside nodes.** Supervisor
  and grader still need complete text to decide routing/groundedness, but
  `chat_agent`/`rag_agent` stream via `llm.stream()` so SSE forwards sooner.
- **PDF text-extraction fidelity isn't unit-tested with real text.** Covered by
  a blank-PDF smoke test; verify with a real PDF. Scanned PDFs use a Tesseract
  fallback (`pytesseract` + `pdf2image`) when a page has <50 chars.
- **No real auth — per-user via `user_id` namespaces** (`documents_u_<user>` +
  `user:session` thread). Sufficient for a demo, not a production IAM.
- **Vectorstore caching:** first `QdrantVectorStore` construction pays a dummy
  embed to validate dims; subsequent calls are cached per (collection, provider).
  Google cloud embeddings are truncated 3072→768 via `output_dimensionality`.

## Project workflow

This project was built with the `loop-engineer-aqib` skill: an `.agent/`
directory of markdown files (`BACKLOG.md`, `STATE.md`, `PLAN.md`,
`PROGRESS.md`, `DECISIONS.md`, `ERRORS.md`) acts as persistent state for a
one-transition-per-iteration build loop. See `.agent/PROGRESS.md` for a
full history of every task, including the dependency issues hit and fixed
along the way (ERR-001, ERR-002).
