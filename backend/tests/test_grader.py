from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from app.graph.grader import (
    FALLBACK_MESSAGE,
    fallback_node,
    grader_node,
    route_after_grading,
)


@dataclass
class FakeResponse:
    content: str


class FakeLLM:
    def __init__(self, reply: str):
        self.reply = reply

    def invoke(self, messages):
        return FakeResponse(content=self.reply)


def base_state(retry_count: int = 0, answer: str = "the sky is blue") -> dict:
    return {
        "messages": [AIMessage(content=answer)],
        "retrieved_docs": [Document(page_content="the sky is blue", metadata={})],
        "retry_count": retry_count,
        "grounded": False,
        "route": "rag",
    }


def test_grounded_verdict_does_not_touch_retry_count():
    state = base_state(retry_count=0)

    result = grader_node(state, llm=FakeLLM("GROUNDED"))

    assert result == {"grounded": True}
    assert route_after_grading({**state, **result}) == "end"


def test_ungrounded_first_attempt_increments_retry_and_rewrites_query():
    state = base_state(retry_count=0)
    result = grader_node(state, llm=FakeLLM("what color is the sky specifically?"))

    assert result["grounded"] is False
    assert result["retry_count"] == 1
    assert result["messages"][0].content == "what color is the sky specifically?"
    assert route_after_grading({**state, **result}) == "retry"


def test_ungrounded_second_attempt_gives_up():
    state = base_state(retry_count=1)
    result = grader_node(state, llm=FakeLLM("still not grounded"))

    assert result["retry_count"] == 2
    assert route_after_grading({**state, **result}) == "give_up"


def test_fallback_node_is_honest():
    message = fallback_node(base_state())["messages"][0]
    assert message.content == FALLBACK_MESSAGE
    assert "don't have enough information" in message.content
