# PLAN

Task: TASK-006

## Risk tier

LOW — client construction only, no external calls made at import time.

## Specialist concerns

none.

## Objective

`app/llm.py`: the only place in the codebase that constructs an Ollama
chat model or embeddings client (AGENTS.md rule) — everything else imports
from here, so swapping providers later is a one-file change.

## Steps

1. `get_chat_model()` -> `ChatOllama` using `settings.ollama_base_url` /
   `ollama_chat_model`.
2. `get_embeddings()` -> `OllamaEmbeddings` using `settings.ollama_base_url`
   / `ollama_embed_model`.
3. Test: both factories return an instance with the expected `model`
   attribute set from `Settings` defaults, without making a network call
   (Ollama doesn't need to be running for client construction).

## Acceptance criteria

- [ ] `get_chat_model()` and `get_embeddings()` both exist, read from
      `app.config.settings`, no hardcoded model names
- [ ] Test passes without Ollama running (construction only, no `.invoke`)
- [ ] `pytest -q` and `ruff check .` clean

## Files expected to change

- `backend/app/llm.py` (new)
- `backend/tests/test_llm.py` (new)
