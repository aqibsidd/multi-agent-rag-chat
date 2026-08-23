import json
import uuid

from fastapi.testclient import TestClient

from app.graph.build import build_graph
from app.ingest import ingest_text
from app.main import app, get_graph
from tests.test_graph_build import (
    CHAT_KEY,
    GRADER_KEY,
    RAG_KEY,
    SUPERVISOR_KEY,
    ScriptedFakeLLM,
)

client = TestClient(app)


def parse_sse(body: str) -> list[tuple[str, dict]]:
    events = []
    for block in body.strip().split("\n\n"):
        lines = block.splitlines()
        event = next(line.removeprefix("event: ") for line in lines if line.startswith("event: "))
        data = next(line.removeprefix("data: ") for line in lines if line.startswith("data: "))
        events.append((event, json.loads(data)))
    return events


def test_chitchat_stream_emits_only_supervisor_and_chat_agent():
    fake = ScriptedFakeLLM({SUPERVISOR_KEY: ["chat"], CHAT_KEY: ["I'm doing great, thanks!"]})
    app.dependency_overrides[get_graph] = lambda: build_graph(llm=fake)

    response = client.post("/chat/stream", json={"message": "hi, how are you?"})
    events = parse_sse(response.text)

    app.dependency_overrides.clear()

    agent_nodes = [data["node"] for event, data in events if event == "agent"]
    assert agent_nodes == ["supervisor", "chat_agent"]

    done = next(data for event, data in events if event == "done")
    assert done["answer"] == "I'm doing great, thanks!"
    assert done["sources"] == []


def test_grounded_rag_stream_emits_full_trace_and_sources():
    marker = uuid.uuid4().hex
    ingest_text(f"Deployment {marker}: releases happen every Friday.", source=f"test-stream-{marker}")

    fake = ScriptedFakeLLM(
        {
            SUPERVISOR_KEY: ["rag"],
            RAG_KEY: [f"Releases happen every Friday. [1] ({marker})"],
            GRADER_KEY: ["GROUNDED"],
        }
    )
    app.dependency_overrides[get_graph] = lambda: build_graph(llm=fake)

    response = client.post("/chat/stream", json={"message": f"when do releases happen for {marker}?"})
    events = parse_sse(response.text)

    app.dependency_overrides.clear()

    agent_nodes = [data["node"] for event, data in events if event == "agent"]
    assert agent_nodes == ["supervisor", "rag_agent", "grader"]

    supervisor_event = next(data for event, data in events if event == "agent" and data["node"] == "supervisor")
    assert supervisor_event["route"] == "rag"

    done = next(data for event, data in events if event == "done")
    assert marker in done["answer"]
    assert done["sources"][0]["source"] == f"test-stream-{marker}"
