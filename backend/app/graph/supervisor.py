from app.graph.state import GraphState
from app.llm import get_chat_model

SUPERVISOR_PROMPT = (
    "Classify the user's LAST message as exactly one word: 'chat' if it's "
    "small talk, a greeting, or general conversation with no need for "
    "document lookup, or 'rag' if it asks a question that likely needs "
    "information from uploaded documents. Respond with only 'chat' or "
    "'rag', nothing else."
)


def supervisor_node(state: GraphState, llm=None) -> dict:
    llm = llm or get_chat_model(temperature=0)
    last_message = state["messages"][-1].content

    response = llm.invoke(
        [
            {"role": "system", "content": SUPERVISOR_PROMPT},
            {"role": "user", "content": last_message},
        ]
    )

    route = "rag" if "rag" in response.content.strip().lower() else "chat"
    return {"route": route}
