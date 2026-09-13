import uuid
from dataclasses import dataclass

from langchain_core.messages import HumanMessage

from app.graph.rag_agent import rag_agent_node
from app.ingest import ingest_text


@dataclass
class FakeResponse:
    content: str


class FakeLLM:
    def __init__(self, reply: str):
        self.reply = reply
        self.invoked_with = None
        self.calls = []

    def invoke(self, messages):
        self.invoked_with = messages
        self.calls.append(messages)
        return FakeResponse(content=self.reply)


def test_rag_agent_retrieves_real_chunks_and_prompts_with_them():
    marker = uuid.uuid4().hex
    ingest_text(
        f"The onboarding checklist item {marker} requires a laptop setup.",
        source=f"test-rag-{marker}",
    )

    state = {"messages": [HumanMessage(content=f"what does checklist item {marker} require?")]}
    fake = FakeLLM("It requires a laptop setup. [1]")

    result = rag_agent_node(state, llm=fake, vectorstore=None)

    # The prompt sent to the LLM must actually contain the retrieved chunk.
    system_content = fake.invoked_with[0]["content"]
    assert marker in system_content

    assert result["messages"][0].content == "It requires a laptop setup. [1]"
    assert any(marker in d.page_content for d in result["retrieved_docs"])


class ScriptedLLM:
    """Queue of replies; records every prompt for rewrite assertions."""

    def __init__(self, replies: list[str]):
        self.replies = list(replies)
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        return FakeResponse(content=self.replies.pop(0))


def test_rag_agent_rewrites_follow_up_with_history_before_retrieval():
    marker = uuid.uuid4().hex
    ingest_text(
        f"Aqib Rashid {marker} is 25 years old.",
        source=f"test-rewrite-{marker}",
    )

    state = {
        "messages": [
            HumanMessage(content=f"who is Aqib Rashid {marker}?"),
            HumanMessage(content="how old is he?"),
        ]
    }
    # First call = rewrite, second call = answer.
    fake = ScriptedLLM([f"how old is Aqib Rashid {marker}?", f"He is 25. [1] ({marker})"])

    result = rag_agent_node(state, llm=fake, vectorstore=None)

    assert len(fake.calls) == 2  # rewrite ran because prior history exists
    assert marker in result["messages"][0].content
    assert any(marker in d.page_content for d in result["retrieved_docs"])


def test_rag_agent_skips_rewrite_on_first_turn():
    marker = uuid.uuid4().hex
    ingest_text(f"Visa rule {marker}: entry within 30 days.", source=f"test-1st-{marker}")

    state = {"messages": [HumanMessage(content=f"what is visa rule {marker}?")]}
    fake = ScriptedLLM([f"Entry within 30 days. [1] ({marker})"])

    result = rag_agent_node(state, llm=fake, vectorstore=None)

    assert len(fake.calls) == 1  # no history → single answer call, no extra cost
    assert marker in result["messages"][0].content


def test_rag_agent_drops_junk_chunks_below_relevance_gate():
    state = {"messages": [HumanMessage(content="quantum banana philosophy")]}

    result = rag_agent_node(state, llm=FakeLLM("I don't know."))
    # Unrelated query: nothing should pass the 0.5 gate in the test data.
    assert result["retrieved_docs"] == []
