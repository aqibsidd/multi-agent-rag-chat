# DECISIONS

Architecture Decision Records. Append-only, never edit a past ADR — supersede
it with a new one that references the old number.

## ADR-001

Date: 2026-08-23

Decision: Python + FastAPI backend, LangGraph for agent orchestration.

Reason: Strongest multi-agent resume/portfolio signal in 2026; explicit
graph of agents with built-in state, streaming, and conditional edges.
User already runs Python projects (document_ocr, hindi_story_studio).

Rejected: Node + LangGraph.js (would reuse more of the existing
`rag-chat-app.zip` backend, but weaker ecosystem for agent graphs); hand-
rolled Python with no framework (more code, no free streaming/state).

Because: the portfolio value and LangGraph's maturity outweighed reuse
savings from the Node prototype.

## ADR-002

Date: 2026-08-23

Decision: Ollama only (`llama3.2` chat, `nomic-embed-text` embeddings) for
this project. No Gemini/OpenAI calls, though the LLM client is factored
behind `app/llm.py` so swapping providers later is a one-file change.

Reason: Zero cost, fully offline, both models already pulled locally.
User explicitly chose this over free-tier Gemini despite the latency
tradeoff of local inference on 8GB RAM.

Rejected: Gemini free tier (would be faster per turn); OpenAI (costs money).

Because: zero-cost and offline mattered more than latency for this
learning project; the tradeoff was made explicitly and the design (3 calls
max/turn, single model, single long generation) compensates for it.

## ADR-003

Date: 2026-08-23

Decision: Qdrant via Docker for the vector store, replacing the HNSWLib
in-process file store from the earlier `rag-chat-app.zip` prototype.

Reason: A real standalone vector DB with a dashboard (`:6333/dashboard`)
that's screenshottable for a portfolio, supports metadata filtering, and
is what employers recognize as "a vector database" rather than a library.

Rejected: ChromaDB embedded (easier, no Docker, but less of a "real DB"
story); pgvector (more setup, no benefit here since there's no relational
data to co-locate); FAISS (closest to the old HNSWLib setup, but still a
library, not a database).

Because: the dashboard and "real DB" framing were explicitly what the user
wanted out of this rebuild.

## ADR-004

Date: 2026-08-23

Decision: Runtime agent graph is Supervisor -> {chat_agent | rag_agent ->
grader (self-correcting, one retry)}. 3 LLM calls per turn, max.

Reason: Reads as genuinely multi-agent (routing AND a quality loop) while
staying within the 3-call/turn budget the 8GB-RAM constraint requires.

Rejected: Supervisor + N specialists (simpler, but no quality loop);
research crew / plan-work-write (parallel local generations would thrash
8GB RAM); debate/judge panel (doubles generation time, hard to justify).

Because: the self-correcting RAG topology was the best fit for "genuinely
multi-agent" within the hardware budget.

## ADR-005

Date: 2026-08-23

Decision: Adapt the React frontend from `~/Downloads/rag-chat-app.zip`
rather than building a new one.

Reason: It already has working SSE streaming and a file-upload UI; only
the agent-trace/source display needs to be added.

Rejected: Building fresh — no reason to, the existing plumbing works.

Because: reuse of already-correct code beats rewriting it.
