from langchain_core.messages import AIMessage

from app.graph.state import GraphState
from app.llm import get_chat_model
from app.memory import is_internal_message

CHAT_SYSTEM_PROMPT = "You are a friendly, helpful assistant. Reply conversationally."

# Keep the prompt bounded for small chat models. 20 messages
# ≈ 10 turns, enough for follow-ups like "how old is he?" without blowing
# up the context window.
MAX_HISTORY_MESSAGES = 20


def chat_agent_node(state: GraphState, llm=None) -> dict:
    llm = llm or get_chat_model()
    visible = [m for m in state["messages"] if not is_internal_message(m)]
    visible = visible[-MAX_HISTORY_MESSAGES:]
    history = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
    history += [
        {"role": "user" if m.type == "human" else "assistant", "content": m.content}
        for m in visible
    ]

    # Stream tokens so the SSE gateway can forward them as they arrive
    # instead of buffering the whole answer behind one .invoke().
    try:
        chunks = list(llm.stream(history))
        text = "".join(getattr(c, "content", "") for c in chunks) or chunks[-1].content if chunks else ""
    except Exception:  # noqa: BLE001 — stream not supported by fake LLMs in tests
        text = llm.invoke(history).content
    return {"messages": [AIMessage(content=text)]}
