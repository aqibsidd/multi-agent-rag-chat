# PLAN

Task: TASK-014

## Risk tier

LOW — no external side effects, but this is the trickiest logic in the
project (a stateful retry loop), so extra care in testing both branches.

## Specialist concerns

testing (per BACKLOG tag) — must prove both the grounded path and the
retry-then-give-up path actually work, not just that the function runs.

## Objective

`grader_node` + `route_after_grading` (conditional edge) + `fallback_node`:
after `rag_agent` answers, judge whether the answer is grounded in
`retrieved_docs`. If not, and no retry has been used yet, rewrite the query
and route back to `rag_agent` once. If still ungrounded after that retry,
route to a fallback that admits it doesn't know rather than hallucinating
further.

## Design note

One LLM call does double duty: the grader prompt asks for either
`GROUNDED` or a rewritten, more specific query — avoiding a separate
rewrite call. `retry_count` increments only on an ungrounded verdict;
`route_after_grading` allows exactly one retry (`retry_count <= 1` routes
back to `rag_agent`; beyond that, `give_up`). This keeps the retry path
bounded to exactly one extra round, matching PROJECT.md's success
criterion ("one query-rewrite retry fires, then admits it doesn't know").

## Steps

1. `app/graph/grader.py`: `grader_node(state, llm=None)`,
   `route_after_grading(state) -> Literal["end","retry","give_up"]`,
   `fallback_node(state)`.
2. Tests with a fake LLM: (a) grounded verdict routes to `end` without
   touching `retry_count`; (b) ungrounded verdict increments `retry_count`
   and replaces the last message with the rewritten query; (c)
   `route_after_grading` returns `retry` at `retry_count == 1` and
   `give_up` at `retry_count == 2`; (d) `fallback_node` produces an
   honest "don't know" message.

## Acceptance criteria

- [ ] Grounded case: `route_after_grading` returns `end`
- [ ] Ungrounded, first attempt: returns `retry`, `retry_count` becomes 1
- [ ] Ungrounded, second attempt: returns `give_up`, `retry_count` becomes 2
- [ ] `fallback_node` never claims an answer it doesn't have
- [ ] `pytest -q` and `ruff check .` clean

## Files expected to change

- `backend/app/graph/grader.py` (new)
- `backend/tests/test_grader.py` (new)
