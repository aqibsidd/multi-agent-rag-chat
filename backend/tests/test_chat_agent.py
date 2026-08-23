import inspect
from dataclasses import dataclass

from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages

from app.graph import chat_agent
from app.graph.chat_agent import chat_agent_node


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


def test_chat_agent_appends_reply_via_reducer():
    state = {"messages": [HumanMessage(content="hi, how are you?")]}
    fake = FakeLLM("I'm doing well, thanks for asking!")

    result = chat_agent_node(state, llm=fake)
    merged = add_messages(state["messages"], result["messages"])

    assert len(merged) == 2
    assert merged[1].content == "I'm doing well, thanks for asking!"
    assert merged[1].type == "ai"


def test_chat_agent_source_never_references_vectorstore():
    # Inspects the module's own source rather than sys.modules, which would
    # give a false pass once another test file imports app.vectorstore
    # (TASK-007) in the same pytest session.
    source = inspect.getsource(chat_agent)
    assert "vectorstore" not in source
