# PLAN

Task: TASK-010

## Risk tier

LOW — a type definition, no runtime behavior.

## Specialist concerns

none.

## Objective

`app/graph/state.py`: the shared state every graph node reads/writes —
messages, routing decision, retrieved docs, groundedness, retry count.

## Steps

1. `app/graph/__init__.py` (package init).
2. `GraphState` TypedDict: `messages` (using LangGraph's `add_messages`
   reducer so nodes can append rather than overwrite), `route` (str),
   `retrieved_docs` (list), `grounded` (bool), `retry_count` (int).
3. Test: confirms the reducer actually merges message lists (not a
   tautological "TypedDict has these keys" test).

## Acceptance criteria

- [ ] `GraphState` has all 5 fields
- [ ] `add_messages` reducer verified to merge, not overwrite
- [ ] `pytest -q` and `ruff check .` clean

## Files expected to change

- `backend/app/graph/__init__.py` (new)
- `backend/app/graph/state.py` (new)
- `backend/tests/test_graph_state.py` (new)
