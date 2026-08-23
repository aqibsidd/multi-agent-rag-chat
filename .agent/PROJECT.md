# PROJECT

## Purpose

A multi-agent RAG chatbot, built as a learning/portfolio piece. Upload a
document, ask questions about it in a chat UI, and watch which agent
handled each turn: a supervisor routes chit-chat straight to a chat agent,
and document questions to a RAG agent that retrieves from a real vector DB
and self-corrects when its answer isn't grounded in what it retrieved.

## Success criteria

- Ingest a PDF/text file, see it land in Qdrant with a populated collection.
- Ask a question the docs answer -> traced path is
  `supervisor -> rag_agent -> grader`, answer cites source chunks.
- Ask small talk ("hi, how are you") -> traced path is
  `supervisor -> chat_agent`, no retrieval call made.
- Ask something the docs can't answer -> grader marks it ungrounded, one
  query-rewrite retry fires, then the agent admits it doesn't know rather
  than hallucinating.
- Frontend shows streaming tokens, sources, and which agent answered.

## Constraints

- M1 Mac, 8GB RAM, fully local inference (Ollama: `llama3.2`,
  `nomic-embed-text` — both already pulled). No paid API calls.
- At most 3 LLM calls per user turn (supervisor, answer, grader) to keep
  latency tolerable on this hardware; only one long generation per turn.
- One model throughout so Ollama never reloads weights mid-turn.

## Out of scope

- Multi-user auth, persistence of chat history across sessions.
- Cloud deployment.
- More than 2 specialist agents (chat, RAG) — no research-crew/debate
  topology; see DECISIONS.md ADR-004 for why.
