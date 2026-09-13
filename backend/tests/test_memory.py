import uuid
from dataclasses import dataclass

from langchain_core.messages import AIMessage, HumanMessage

from app.graph.rag_agent import rag_agent_node
from app.memory import extract_facts, history_text, persist_user_facts
from app.vectorstore import get_vectorstore


@dataclass
class FakeResponse:
    content: str


class FakeLLM:
    def __init__(self, reply: str):
        self.reply = reply
        self.invoked_with = None

    def invoke(self, messages):
        self.invoked_with = messages
        return FakeResponse(content=self.reply)


def test_extract_facts_returns_standalone_sentences():
    fake = FakeLLM("Aqib's father name is Rashid.\nAqib lives in Lucknow.")
    facts = extract_facts("my father name is Rashid, i live in Lucknow", "noted!", llm=fake)
    assert facts == ["Aqib's father name is Rashid.", "Aqib lives in Lucknow."]


def test_extract_facts_nothing_when_no_fact_stated():
    fake = FakeLLM("NOTHING")
    assert extract_facts("hi, how are you?", "I'm well!", llm=fake) == []


def test_persist_user_facts_ingests_once_and_is_retrievable():
    marker = uuid.uuid4().hex
    fake = FakeLLM(f"Aqib's father name is Rashid {marker}.")

    added = persist_user_facts(
        f"my father name is Rashid {marker}",
        "noted!",
        session_id=f"test-{marker}",
        llm=fake,
        enabled=True,
    )
    assert added >= 1

    results = get_vectorstore().similarity_search(f"aqib father name {marker}", k=1)
    assert marker in results[0].page_content
    assert results[0].metadata["source"] == f"user-memory:test-{marker}"


def test_persist_user_facts_disabled_is_noop():
    fake = FakeLLM("Some fact that must never be stored.")
    assert (
        persist_user_facts("my father is X", "noted!", "s1", llm=fake, enabled=False)
        == 0
    )
    assert fake.invoked_with is None


def test_persist_user_facts_dedupes_restatements():
    marker = uuid.uuid4().hex
    fake = FakeLLM(f"Aqib's father name is Rashid {marker}.")

    first = persist_user_facts(
        f"my father name is Rashid {marker}",
        "noted!",
        session_id=f"test-dupe-{marker}",
        llm=fake,
        enabled=True,
    )
    assert first >= 1

    second = persist_user_facts(
        f"my father name is Rashid {marker}",  # same fact, new turn
        "noted again!",
        session_id=f"test-dupe-{marker}",
        llm=FakeLLM(f"Aqib's father name is Rashid {marker}."),
        enabled=True,
    )
    assert second == 0  # already stored → no duplicate chunk


def test_rag_agent_prompt_includes_conversation_history():
    marker = uuid.uuid4().hex
    state = {
        "messages": [
            HumanMessage(content=f"my father name is Rashid {marker}"),
            AIMessage(content="noted!"),
            HumanMessage(content="what is my father name?"),
        ]
    }
    fake = FakeLLM(f"Rashid {marker}. [1]")

    rag_agent_node(state, llm=fake, vectorstore=None)

    system_content = fake.invoked_with[0]["content"]
    assert marker in system_content  # history fact visible to the RAG prompt


def test_history_text_skips_internal_grader_retries():
    msgs = [
        HumanMessage(content="original question"),
        HumanMessage(
            content="rewritten query",
            name="grader_retry",
            additional_kwargs={"internal_retry": True},
        ),
    ]
    text = history_text(msgs)
    assert "original question" in text
    assert "rewritten query" not in text
