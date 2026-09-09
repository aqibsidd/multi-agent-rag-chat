from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage

from app.graph.state import GraphState
from app.llm import get_chat_model

GRADER_PROMPT = (
    "You are checking whether an AI-generated answer is actually supported "
    "by the given context. If every claim in the answer is backed by the "
    "context, respond with exactly: GROUNDED\n"
    "If the answer contains information not present in the context, "
    "respond with a single rewritten search query — more specific than the "
    "original — that would help find the right information. Respond with "
    "ONLY 'GROUNDED' or the rewritten query, nothing else."
)

FALLBACK_MESSAGE = (
    "I don't have enough information in the knowledge base to answer that "
    "confidently."
)


def grader_node(state: GraphState, llm=None) -> dict:
    llm = llm or get_chat_model(temperature=0)
    answer = state["messages"][-1].content
    context = "\n\n".join(d.page_content for d in state.get("retrieved_docs", []))

    response = llm.invoke(
        [
            {"role": "system", "content": GRADER_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{context or '(none)'}\n\nAnswer:\n{answer}",
            },
        ]
    )

    verdict = response.content.strip()
    grounded = verdict.upper().startswith("GROUNDED")

    if grounded:
        return {"grounded": True}

    return {
        "grounded": False,
        "retry_count": state["retry_count"] + 1,
        # Tagged as internal so chat history / chat_agent can skip it —
        # it's a rewritten retrieval query, not a user message.
        "messages": [
            HumanMessage(
                content=verdict,
                name="grader_retry",
                additional_kwargs={"internal_retry": True},
            )
        ],
    }


def route_after_grading(state: GraphState) -> Literal["end", "retry", "give_up"]:
    if state["grounded"]:
        return "end"
    if state["retry_count"] <= 1:
        return "retry"
    return "give_up"


def fallback_node(state: GraphState) -> dict:
    return {"messages": [AIMessage(content=FALLBACK_MESSAGE)]}
