# PLAN

Task: TASK-019

## Risk tier

LOW — pure UI addition, no new backend surface (TASK-016 already emits
`agent` events; TASK-018's parser already ignores them, deferring to this
task by design).

## Specialist concerns

frontend (per BACKLOG tag).

## Objective

Show which agent(s) handled each turn as a small badge row on the
assistant's message bubble, using the `agent` SSE events TASK-018's parser
currently discards. Sources panel already works (fixed as part of
TASK-018's contract rewrite) — this task's remaining scope is just the
trace badge.

## Steps

1. `App.jsx`: track a `trace` array on the in-progress assistant message;
   on an `agent` event, append `{node, route}` (route only present on the
   supervisor's event).
2. Render a small badge row above the message content: one pill per node
   name in the trace (e.g. `supervisor → rag_agent → grader`), styled
   distinctly per node so chat vs RAG paths are visually obvious at a
   glance.
3. `index.css`: minimal badge styling, no new dependency.

## Acceptance criteria

- [ ] Chit-chat turns show `supervisor → chat_agent`
- [ ] Grounded RAG turns show `supervisor → rag_agent → grader`
- [ ] A retried turn shows the repeated `rag_agent → grader` correctly
      (trace reflects actual node sequence, not a deduped set)
- [ ] `npm run build` still succeeds

## Files expected to change

- `frontend/src/App.jsx`
- `frontend/src/index.css`
