# PLAN

Task: TASK-011

## Risk tier

LOW — routing logic, no data mutation, no external side effects beyond an
LLM call.

## Specialist concerns

testing (per BACKLOG tag) — must verify both routing branches.

## Objective

`supervisor_node`: classifies the latest user message as `chat` or `rag`,
sets `route` in state. Routing decision needs one fast LLM call
(ADR-004: 3-call/turn budget).

## Steps

1. `app/graph/supervisor.py`: `supervisor_node(state, llm=None)` — accepts
   an optional LLM for testability (defaults to `get_chat_model()` from
   TASK-006), classifies the last message, returns `{"route": "chat"|"rag"}`.
2. Test with a fake LLM object (`.invoke` returning a stub response) so the
   test is fast and deterministic — real Ollama inference is correct for
   runtime but too slow/nondeterministic for a unit test, consistent with
   TASK-015's existing plan to use a fake LLM for graph tests.
3. Test both branches: a message that should route to `chat` and one that
   should route to `rag`.

## Acceptance criteria

- [ ] `supervisor_node` returns `{"route": "chat"}` or `{"route": "rag"}`
      based on the fake LLM's classification
- [ ] Both branches covered by a test that would fail if the parsing logic
      were wrong (not a tautology)
- [ ] `pytest -q` and `ruff check .` clean

## Files expected to change

- `backend/app/graph/supervisor.py` (new)
- `backend/tests/test_supervisor.py` (new)
