# PLAN

Task: TASK-012

## Risk tier

LOW.

## Specialist concerns

none.

## Objective

`chat_agent_node`: plain conversational reply for messages the supervisor
routed to `chat` — no retrieval, no Qdrant dependency. This is the branch
that must keep working even while TASK-005/007/013 stay blocked on Docker.

## Steps

1. `app/graph/chat_agent.py`: `chat_agent_node(state, llm=None)` — replies
   using the full message history, appends an `AIMessage` to `messages`.
2. Test with a fake LLM: asserts the returned message is appended (not
   overwritten) via the state's `add_messages` reducer semantics, and that
   no retrieval/vectorstore call happens (chat_agent never imports
   `app.vectorstore`).

## Acceptance criteria

- [ ] `chat_agent_node` returns `{"messages": [AIMessage(...)]}`
- [ ] Test verifies the reply content and that it doesn't touch retrieval
- [ ] `pytest -q` and `ruff check .` clean

## Files expected to change

- `backend/app/graph/chat_agent.py` (new)
- `backend/tests/test_chat_agent.py` (new)
