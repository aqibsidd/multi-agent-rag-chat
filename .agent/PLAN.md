# PLAN

Task: TASK-018

## Risk tier

MEDIUM — the old frontend targets a different backend contract entirely
(different SSE format, different field names); "point at the new backend"
means fixing that contract, not just a URL.

## Specialist concerns

frontend (per BACKLOG tag).

## Objective

Extract `frontend/` from `~/Downloads/rag-chat-app.zip`, rewire it to
actually work against this project's backend (not just its port), confirm
`npm run build` succeeds.

## Steps

1. Extract `frontend/` from the zip (scratchpad, not `/tmp`).
2. Read the existing `App.jsx`/`vite.config.js` fully before changing
   anything, to find every real contract mismatch, not just the obvious
   port difference.
3. Fix: proxy target/paths (`:8000`, `/ingest` `/chat` `/health`, no `/api`
   prefix); SSE parser (named `event:`/`data:` blocks, not a `type` field
   inside `data:`); `chunksAdded` -> `chunks_added`; drop the nonexistent
   `chunk` field from source rendering; header/title text to match the
   real stack.
4. `npm install`, `npm run build`.

## Acceptance criteria

- [ ] `npm run build` succeeds
- [ ] SSE parser matches the backend's actual named-event format
- [ ] No leftover references to the old backend's field names or `/api`
      prefix

## Files expected to change

- `frontend/` (new, extracted + modified)

## Retrospective note

Written after IMPLEMENT, not before — went straight to extraction under
"in 1 go" momentum and skipped this file. Caught during the next COMMIT
step's file review. No functional harm (the actual work matched what this
plan would have said), but it broke the one-transition discipline the
loop-engineer-aqib skill exists to enforce. Rule for the rest of this run:
even moving fast, write PLAN.md before IMPLEMENT, always.
