from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    route: str
    retrieved_docs: list
    grounded: bool
    retry_count: int
