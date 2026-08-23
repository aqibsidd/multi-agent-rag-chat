# PLAN

Task: TASK-013

## Risk tier

LOW.

## Specialist concerns

none.

## Objective

`rag_agent_node`: retrieve top-4 chunks from Qdrant for the latest message,
generate a grounded answer with `[n]`-style citations, store what was
retrieved in state (`retrieved_docs`) so the grader (TASK-014) can check
groundedness against it without re-retrieving.

## Steps

1. `app/graph/rag_agent.py`: `rag_agent_node(state, llm=None,
   vectorstore=None)` — both injectable for testing, default to
   `get_chat_model()` / `get_vectorstore()`.
2. Retrieve via real `similarity_search` (fast, already proven in
   TASK-007/008) — only the LLM is faked in the test, since that's the
   slow/nondeterministic part.
3. Build a numbered context block, prompt the LLM to answer using only
   that context and cite `[n]`.
4. Return `{"messages": [AIMessage(...)], "retrieved_docs": docs}`.
5. Test: ingest a real marker doc, run the node with a fake LLM, assert
   the fake was called with a prompt containing the retrieved chunk, and
   that `retrieved_docs` in the result actually contains it.

## Acceptance criteria

- [ ] Retrieves real chunks from Qdrant (not stubbed)
- [ ] Prompt sent to the LLM includes the retrieved content
- [ ] Returns both the AI message and `retrieved_docs`
- [ ] `pytest -q` and `ruff check .` clean

## Files expected to change

- `backend/app/graph/rag_agent.py` (new)
- `backend/tests/test_rag_agent.py` (new)
