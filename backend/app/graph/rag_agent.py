from langchain_core.messages import AIMessage, HumanMessage

from app.graph.state import GraphState
from app.llm import get_chat_model
from app.memory import history_text
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


def rag_agent_node(state: GraphState, llm=None, vectorstore=None) -> dict:
    llm = llm or get_chat_model()
    vectorstore = vectorstore or get_vectorstore()

    query = state["messages"][-1].content
    docs = vectorstore.similarity_search(query, k=4)

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
