from langchain_core.messages import AIMessage, HumanMessage

from app.graph.state import GraphState
from app.llm import get_chat_model
from app.vectorstore import get_vectorstore

RAG_SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the user's question using ONLY the "
    "context below, and cite sources with [n] markers matching the numbered "
    "context blocks. If the context doesn't contain the answer, say plainly "
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

    system_prompt = f"{RAG_SYSTEM_PROMPT}\n\nContext:\n{_build_context(docs)}"
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
