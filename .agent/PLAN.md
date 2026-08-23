# PLAN

Task: TASK-016

## Risk tier

MEDIUM — the first endpoint that actually drives the full multi-agent
graph over the network; a mistake here is the difference between "the
frontend shows nothing" and "it works."

## Specialist concerns

backend (per BACKLOG tag).

## Objective

`POST /chat/stream`: runs the compiled graph (TASK-015) and streams
progress over SSE — a per-node "agent" trace event as each node completes
(so the UI can show which agent handled the turn) plus the final answer
and its sources.

## Scope decision: what "streaming" means here

Confirmed empirically before writing any code: `graph.stream(state,
stream_mode="updates")` yields `{node_name: partial_state}` as each node
finishes (verified live against real Ollama — supervisor then chat_agent,
correct shape). All graph nodes call `llm.invoke()` (blocking, full
response), not `llm.stream()` — that was the right call for supervisor/
grader, which need the complete text to decide routing/groundedness
before acting on it, and changing chat_agent/rag_agent to stream would
mean revisiting two already-shipped, tested tasks for uncertain gain.

So this delivers **incremental, per-agent streaming** (progressive
delivery over a live SSE connection, with an explicit trace of which
agent produced what) rather than true token-by-token LLM streaming. This
is disclosed here rather than silently passed off as full token
streaming — genuine token-level streaming would need every node's
LLM call re-plumbed through `.stream()` with config propagation, which is
a larger change than this task's scope.

## Steps

1. `get_graph()`: lazy singleton, exposed as a FastAPI dependency so tests
   can override it with a graph built from a fake LLM (same pattern as
   TASK-015's tests).
2. `POST /chat/stream`: for each `{node_name: update}` from
   `stream_mode="updates"`, emit an `agent` SSE event (`route` included
   when the node is `supervisor`); for any AI message produced, emit a
   `token` event with its content. After the stream ends, emit a final
   `done` event with the answer and (if `rag_agent` ran) sources.
3. Tests: reuse `ScriptedFakeLLM` — assert the chit-chat path emits only
   `supervisor`+`chat_agent` agent events, and the grounded RAG path emits
   `supervisor`+`rag_agent`+`grader` plus a `done` event carrying sources.

## Acceptance criteria

- [ ] `agent` events show the real node sequence for both the chat and
      RAG paths
- [ ] `done` event carries the final answer text and (for RAG) sources
- [ ] `pytest -q` and `ruff check .` clean

## Files expected to change

- `backend/app/main.py` (add `/chat/stream`)
- `backend/tests/test_chat_stream.py` (new)
