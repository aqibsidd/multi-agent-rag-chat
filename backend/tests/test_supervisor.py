from dataclasses import dataclass

from langchain_core.messages import HumanMessage

from app.graph.supervisor import supervisor_node


@dataclass
class FakeResponse:
    content: str


class FakeLLM:
    def __init__(self, reply: str):
        self.reply = reply

    def invoke(self, messages):
        return FakeResponse(content=self.reply)


def test_routes_to_chat_for_small_talk():
    state = {"messages": [HumanMessage(content="hi, how are you?")]}
    result = supervisor_node(state, llm=FakeLLM("chat"))
    assert result == {"route": "chat"}


def test_routes_to_rag_for_document_question():
    state = {"messages": [HumanMessage(content="what does the report say about Q3 revenue?")]}
    result = supervisor_node(state, llm=FakeLLM("rag"))
    assert result == {"route": "rag"}
