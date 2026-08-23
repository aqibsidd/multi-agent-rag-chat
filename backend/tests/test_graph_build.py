import uuid
from dataclasses import dataclass

from app.graph.build import build_graph, initial_state
from app.ingest import ingest_text


@dataclass
class FakeResponse:
    content: str


class ScriptedFakeLLM:
    """Routes replies by matching a substring of each node's distinctive
    system prompt, so one fake can stand in for every node in the graph.
    Each matched key holds a list of replies consumed in order (last one
    repeats if a node is called more times than it has scripted replies)."""

    def __init__(self, script: dict[str, list[str]]):
        self.script = {k: list(v) for k, v in script.items()}
        self.calls: list[str] = []

    def invoke(self, messages):
        content = messages[0]["content"]
        self.calls.append(content)
        for key, replies in self.script.items():
            if key in content:
                reply = replies.pop(0) if len(replies) > 1 else replies[0]
                return FakeResponse(content=reply)
        raise AssertionError(f"No script entry matched prompt: {content[:80]!r}")


SUPERVISOR_KEY = "Classify the user's LAST message"
CHAT_KEY = "friendly, helpful assistant"
RAG_KEY = "Answer the user's question using ONLY the context"
GRADER_KEY = "checking whether an AI-generated answer"


def test_chitchat_routes_to_chat_agent_without_retrieval():
    fake = ScriptedFakeLLM({SUPERVISOR_KEY: ["chat"], CHAT_KEY: ["I'm doing great, thanks!"]})
    graph = build_graph(llm=fake)

    result = graph.invoke(initial_state("hi, how are you?"))

    assert result["messages"][-1].content == "I'm doing great, thanks!"
    assert not any(RAG_KEY in c or GRADER_KEY in c for c in fake.calls)


def test_grounded_doc_question_ends_after_one_grader_pass():
    marker = uuid.uuid4().hex
    ingest_text(f"Fact {marker}: the launch date is March 3rd.", source=f"test-graph-{marker}")

    fake = ScriptedFakeLLM(
        {
            SUPERVISOR_KEY: ["rag"],
            RAG_KEY: [f"The launch date is March 3rd. [1] ({marker})"],
            GRADER_KEY: ["GROUNDED"],
        }
    )
    graph = build_graph(llm=fake)

    result = graph.invoke(initial_state(f"when is the launch date for {marker}?"))

    assert marker in result["messages"][-1].content
    assert result["grounded"] is True
    assert result["retry_count"] == 0


def test_ungrounded_then_grounded_on_retry():
    marker = uuid.uuid4().hex
    ingest_text(f"Policy {marker}: refunds are processed in 5 days.", source=f"test-graph-{marker}")

    fake = ScriptedFakeLLM(
        {
            SUPERVISOR_KEY: ["rag"],
            RAG_KEY: [f"Refunds take 5 days. [1] ({marker})"],
            GRADER_KEY: [f"refund policy {marker} specifics", "GROUNDED"],
        }
    )
    graph = build_graph(llm=fake)

    result = graph.invoke(initial_state(f"what is the refund policy for {marker}?"))

    assert result["grounded"] is True
    assert result["retry_count"] == 1
    assert marker in result["messages"][-1].content


def test_ungrounded_twice_falls_back_honestly():
    marker = uuid.uuid4().hex
    ingest_text(f"Note {marker}: unrelated content.", source=f"test-graph-{marker}")

    fake = ScriptedFakeLLM(
        {
            SUPERVISOR_KEY: ["rag"],
            RAG_KEY: ["Here's a made-up answer."],
            GRADER_KEY: ["rewritten query one", "still not grounded"],
        }
    )
    graph = build_graph(llm=fake)

    result = graph.invoke(initial_state(f"tell me about {marker}"))

    assert result["retry_count"] == 2
    assert "don't have enough information" in result["messages"][-1].content
