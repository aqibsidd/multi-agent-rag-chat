from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages

from app.graph.state import GraphState


def test_graph_state_has_expected_fields():
    state: GraphState = {
        "messages": [],
        "route": "",
        "retrieved_docs": [],
        "grounded": False,
        "retry_count": 0,
    }
    assert set(state.keys()) == {
        "messages",
        "route",
        "retrieved_docs",
        "grounded",
        "retry_count",
    }


def test_add_messages_reducer_merges_not_overwrites():
    existing = [HumanMessage(content="hi", id="1")]
    incoming = [HumanMessage(content="how are you?", id="2")]
    merged = add_messages(existing, incoming)
    assert len(merged) == 2
    assert merged[0].content == "hi"
    assert merged[1].content == "how are you?"
