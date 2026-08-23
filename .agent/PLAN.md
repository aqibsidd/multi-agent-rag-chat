# PLAN

Task: TASK-015

## Risk tier

MEDIUM — this is where all prior nodes get wired into the actual
supervisor topology ADR-004 committed to. A wiring mistake (wrong edge,
missing path_map entry) would be silent until a real conversation hits it.

## Specialist concerns

testing — every edge in the ADR-004 diagram must be exercised, not just
"the graph compiles."

## Objective

`app/graph/build.py`: `build_graph(llm=None, vectorstore=None) ->
CompiledGraph` wiring supervisor -> {chat_agent | rag_agent -> grader ->
{end | retry rag_agent | fallback}}, matching the diagram from ADR-004 and
the state-machine reference used for this whole project's own dev-loop
(different graph, same idea: explicit nodes and conditional edges).

## Steps

1. `app/graph/build.py`: `StateGraph(GraphState)`, register all 5 nodes
   (supervisor, chat_agent, rag_agent, grader, fallback).
2. `add_conditional_edges("supervisor", lambda s: s["route"], {"chat":
   "chat_agent", "rag": "rag_agent"})`.
3. `add_edge("rag_agent", "grader")`.
4. `add_conditional_edges("grader", route_after_grading, {"end": END,
   "retry": "rag_agent", "give_up": "fallback"})`.
5. `add_edge("chat_agent", END)`, `add_edge("fallback", END)`.
6. `llm`/`vectorstore` injected into node closures for testability —
   `build_graph` accepts them and partially applies each node function, so
   tests can pass a fake LLM through the WHOLE graph, not just individual
   nodes.
7. Tests with a fake LLM covering: (a) chit-chat -> supervisor -> chat_agent
   -> END, no retrieval; (b) grounded doc question -> supervisor ->
   rag_agent -> grader -> END; (c) ungrounded then grounded on retry ->
   rag_agent -> grader -> rag_agent -> grader -> END; (d) ungrounded twice
   -> rag_agent -> grader -> rag_agent -> grader -> fallback -> END.

## Acceptance criteria

- [ ] Graph compiles
- [ ] All 4 end-to-end scenarios above pass with a fake LLM (fast,
      deterministic — no real Ollama generation needed for graph-shape
      tests, though retrieval can stay real since it's already proven fast)
- [ ] `pytest -q` and `ruff check .` clean

## Files expected to change

- `backend/app/graph/build.py` (new)
- `backend/tests/test_graph_build.py` (new)
