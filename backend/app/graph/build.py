from functools import partial

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from app.graph.chat_agent import chat_agent_node
from app.graph.grader import fallback_node, grader_node, route_after_grading
from app.graph.rag_agent import rag_agent_node
from app.graph.state import GraphState
from app.graph.supervisor import supervisor_node


def build_graph(llm=None, vectorstore=None):
    graph = StateGraph(GraphState)

    graph.add_node("supervisor", partial(supervisor_node, llm=llm))
    graph.add_node("chat_agent", partial(chat_agent_node, llm=llm))
    graph.add_node("rag_agent", partial(rag_agent_node, llm=llm, vectorstore=vectorstore))
    graph.add_node("grader", partial(grader_node, llm=llm))
    graph.add_node("fallback", fallback_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        lambda state: state["route"],
        {"chat": "chat_agent", "rag": "rag_agent"},
    )
    graph.add_edge("rag_agent", "grader")
    graph.add_conditional_edges(
        "grader",
        route_after_grading,
        {"end": END, "retry": "rag_agent", "give_up": "fallback"},
    )
    graph.add_edge("chat_agent", END)
    graph.add_edge("fallback", END)

    return graph.compile()


def initial_state(user_text: str) -> GraphState:
    return {
        "messages": [HumanMessage(content=user_text)],
        "route": "",
        "retrieved_docs": [],
        "grounded": False,
        "retry_count": 0,
    }
