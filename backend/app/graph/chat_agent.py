from langchain_core.messages import AIMessage

from app.graph.state import GraphState
from app.llm import get_chat_model

CHAT_SYSTEM_PROMPT = "You are a friendly, helpful assistant. Reply conversationally."


def chat_agent_node(state: GraphState, llm=None) -> dict:
    llm = llm or get_chat_model()
    history = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
    history += [
        {"role": "user" if m.type == "human" else "assistant", "content": m.content}
        for m in state["messages"]
    ]

    response = llm.invoke(history)
    return {"messages": [AIMessage(content=response.content)]}
