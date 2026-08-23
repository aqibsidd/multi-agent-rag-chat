# AGENTS.md

Root-level constitution for this project. Loaded automatically by Claude Code
and Codex every session. Rules here are non-negotiable during the loop;
architectural or scope changes go through `.agent/DECISIONS.md` instead.

## Project

A multi-agent RAG chatbot: a LangGraph supervisor routes each message to
either a plain chat agent or a RAG agent that retrieves from Qdrant and
answers with a grounding-grader retry loop. Python/FastAPI backend, React
frontend, fully local via Ollama. Learning/portfolio project — see
`.agent/PROJECT.md` and `.agent/DECISIONS.md` for the full design.

## Rules

- Python: type hints on public functions, `async def` for I/O-bound FastAPI
  routes and LangChain/Ollama calls.
- One LLM client factory (`app/llm.py`) — agents never construct an
  `OllamaLLM`/`OllamaEmbeddings` directly. Keeps provider swap (Gemini/
  OpenAI later) a one-file change.
- Never modify production environment variables or commit secrets. `.env`
  is gitignored; only `.env.example` is committed.
- Follow the LangGraph structure in DECISIONS.md; don't introduce a new
  agent-orchestration pattern without a new ADR.
- Every new piece of business logic gets a test in the same task.
- Run lint and tests before marking any task complete.

## Git

- Branch format: `feature/<task-id>-<short-name>`
- Commit format: `<type>: <description>` (feat, fix, refactor, test, docs, chore)
- Never push directly to main. Never force-push.
- Never skip hooks (`--no-verify`) or amend a commit that isn't the most recent.

## Completion

A task is complete only when ALL of:

1. Code implemented per `.agent/PLAN.md`
2. Tests pass (`.agent/TESTING.md`)
3. Lint passes
4. Type checking passes, if applicable
5. Review gate passed (loop-engineer-aqib skill's `review-checklist.md`)
6. `.agent/BACKLOG.md` and `.agent/PROGRESS.md` updated

## Learned rules (promoted from ERRORS.md)

- **Verify a new library surface is actually installed before writing code
  against it.** Before importing from a new FastAPI feature or a new
  LangChain sub-package, run a one-line import check in the venv first.
  Promoted after two DEPENDENCY incidents in a row (ERR-001:
  `langchain-text-splitters`, ERR-002: `python-multipart` for
  `UploadFile`) — both were caught by a failing test rather than checked
  up front.
