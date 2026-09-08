from app.graph.state import GraphState
from app.llm import get_chat_model
from app.vectorstore import get_vectorstore

SUPERVISOR_PROMPT_BASE = (
    "Classify the user's LAST message as exactly one word: 'chat' if it's "
    "small talk, a greeting, or general conversation with no need for "
    "document lookup, or 'rag' if it asks a question that likely needs "
    "information from uploaded documents. Respond with only 'chat' or "
    "'rag', nothing else."
)

# Appended only when the knowledge base already has documents in it, so a
# short/ambiguous question (a name, "tell me about X") leans toward actually
# checking the documents instead of guessing it's small talk.
SUPERVISOR_PROMPT_DOCS_HINT = (
    "\n\nThe knowledge base already has uploaded documents in it. If the "
    "message is ambiguous or ties to a specific person, topic, or thing "
    "rather than being clearly generic small talk, prefer 'rag' so the "
    "documents get checked."
)


def _knowledge_base_has_documents(vectorstore) -> bool:
    return vectorstore.client.count(
        collection_name=vectorstore.collection_name, exact=True
    ).count > 0


def supervisor_node(state: GraphState, llm=None, vectorstore=None) -> dict:
    llm = llm or get_chat_model(temperature=0)
    vectorstore = vectorstore or get_vectorstore()
    last_message = state["messages"][-1].content

    prompt = SUPERVISOR_PROMPT_BASE
    if _knowledge_base_has_documents(vectorstore):
        prompt += SUPERVISOR_PROMPT_DOCS_HINT

    response = llm.invoke(
        [
            {"role": "system", "content": prompt},
            {"role": "user", "content": last_message},
        ]
    )

    route = "rag" if "rag" in response.content.strip().lower() else "chat"
    return {"route": route}
