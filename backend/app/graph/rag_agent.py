from langchain_core.messages import AIMessage, HumanMessage

from app.config import settings
from app.graph.state import GraphState
from app.llm import get_chat_model
from app.memory import history_text, visible_messages
from app.vectorstore import get_vectorstore

RAG_SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the user's question using ONLY the "
    "context below, and cite sources with [n] markers matching the numbered "
    "context blocks. Facts the user directly stated in the conversation "
    "history below may also be used for follow-up questions about them. "
    "If neither the context nor the conversation history contains the "
    "answer, say plainly "
    "that you don't have that information in the knowledge base."
)


def _build_context(docs: list) -> str:
    if not docs:
        return "(no relevant documents found)"
    return "\n\n".join(
        f"[{i + 1}] (source: {d.metadata.get('source', 'unknown')})\n{d.page_content}"
        for i, d in enumerate(docs)
    )


REWRITE_PROMPT = (
    "Rewrite the question as a standalone question that can be understood "
    "without the conversation history. Resolve pronouns (he/she/it/they) to "
    "the names they refer to. Reply with only the rewritten question, "
    "nothing else."
)


def _rewrite_query(llm, prior_messages: list, query: str) -> str:
    """Standalone retrieval query using history (fixes 'what is his age?'
    searching the raw pronoun). Skipped when there is no prior history.
    Never raises — falls back to the raw query."""
    try:
        response = llm.invoke(
            [
                {"role": "system", "content": REWRITE_PROMPT},
                {
                    "role": "user",
                    "content": f"{history_text(prior_messages)}\n\nQuestion: {query}",
                },
            ]
        )
        return (response.content or "").strip() or query
    except Exception:  # noqa: BLE001 — rewrite is best-effort only
        return query


def rag_agent_node(state: GraphState, llm=None, vectorstore=None) -> dict:
    llm = llm or get_chat_model()
    vectorstore = vectorstore or get_vectorstore(
        collection=state.get("collection") or None
    )

    raw_query = state["messages"][-1].content
    prior = visible_messages(state["messages"][:-1])
    query = _rewrite_query(llm, prior, raw_query) if prior else raw_query
    scored = vectorstore.similarity_search_with_score(query, k=4)
    docs = [d for d, s in scored if s >= settings.relevance_min_score]

    system_prompt = (
        f"{RAG_SYSTEM_PROMPT}\n\n"
        f"Conversation history:\n{history_text(state['messages'][:-1])}\n\n"
        f"Context:\n{_build_context(docs)}"
    )
    response = llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            HumanMessage(content=query),
        ]
    )

    return {
        "messages": [AIMessage(content=response.content)],
        "retrieved_docs": docs,
    }
