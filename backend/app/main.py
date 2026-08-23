import json

from fastapi import Depends, FastAPI, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.graph.build import build_graph, initial_state
from app.ingest import extract_text_from_upload, ingest_text

app = FastAPI(title="multi-agent-rag-chat")

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


class IngestTextRequest(BaseModel):
    text: str
    source: str = "manual-input"


@app.post("/ingest/text")
def ingest_text_endpoint(payload: IngestTextRequest) -> dict:
    chunks_added = ingest_text(payload.text, source=payload.source)
    return {"chunks_added": chunks_added}


@app.post("/ingest/file")
async def ingest_file_endpoint(file: UploadFile) -> dict:
    content = await file.read()
    filename = file.filename or "uploaded-file"
    text = extract_text_from_upload(filename, content)
    chunks_added = ingest_text(text, source=filename)
    return {"chunks_added": chunks_added, "filename": filename}


class ChatRequest(BaseModel):
    message: str


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.post("/chat/stream")
async def chat_stream_endpoint(payload: ChatRequest, graph=Depends(get_graph)):
    def event_generator():
        final_answer = ""
        sources: list[dict] = []

        for chunk in graph.stream(initial_state(payload.message), stream_mode="updates"):
            for node_name, update in chunk.items():
                agent_payload = {"node": node_name}
                if node_name == "supervisor":
                    agent_payload["route"] = update.get("route")
                yield _sse("agent", agent_payload)

                if "retrieved_docs" in update:
                    sources = [
                        {"source": d.metadata.get("source", "unknown"), "preview": d.page_content[:150]}
                        for d in update["retrieved_docs"]
                    ]

                if "messages" in update:
                    message = update["messages"][-1]
                    if message.type == "ai":
                        final_answer = message.content
                        yield _sse("token", {"text": message.content})

        yield _sse("done", {"answer": final_answer, "sources": sources})

    return StreamingResponse(event_generator(), media_type="text/event-stream")
