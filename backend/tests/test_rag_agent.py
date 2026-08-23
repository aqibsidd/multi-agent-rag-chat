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

    def invoke(self, messages):
        self.invoked_with = messages
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
