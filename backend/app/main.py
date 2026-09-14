import json
import logging
import os

from fastapi import Depends, FastAPI, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.config import settings
from app.graph.build import build_graph, initial_state
from app.ingest import extract_text_from_upload, ingest_text
from app.memory import is_internal_message
from app.vectorstore import resolve_collection

logger = logging.getLogger(__name__)

app = FastAPI(title="multi-agent-rag-chat")

# Browsers block cross-origin fetch (frontend .onrender.com calling backend
# .onrender.com) without this. Restrict via FRONTEND_URL in production.
_frontend_url = os.environ.get("FRONTEND_URL", "").strip()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[_frontend_url] if _frontend_url else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_graph = None
_checkpointer_cm = None
_checkpointer = None


def get_checkpointer():
    """Process-wide LangGraph checkpointer.

    Default: local SQLite file (CHECKPOINT_DB_PATH, free, single-box).
    Multi-instance deploys: set CHECKPOINTER_URL to a Postgres connection
    string (needs `langgraph-checkpoint-postgres`) and checkpoints are
    shared across replicas. Same thread_id contract either way.
    """
    global _checkpointer_cm, _checkpointer
    if _checkpointer is None:
        if settings.checkpointer_url:
            from langgraph.checkpoint.postgres import PostgresSaver

            _checkpointer_cm = PostgresSaver.from_conn_string(
                settings.checkpointer_url
            )
            _checkpointer = _checkpointer_cm.__enter__()
        else:
            from langgraph.checkpoint.sqlite import SqliteSaver

            _checkpointer_cm = SqliteSaver.from_conn_string(
                settings.checkpoint_db_path
            )
            _checkpointer = _checkpointer_cm.__enter__()
    return _checkpointer


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph(checkpointer=get_checkpointer())
    return _graph


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


class IngestTextRequest(BaseModel):
    text: str
    source: str = "manual-input"
    user_id: str = ""


def _check_size(num_bytes: int) -> None:
    limit = settings.max_upload_mb * 1024 * 1024
    if num_bytes > limit:
        raise HTTPException(
            status_code=413,
            detail=f"Upload too large (>{settings.max_upload_mb}MB).",
        )


@app.post("/ingest/text")
def ingest_text_endpoint(payload: IngestTextRequest) -> dict:
    _check_size(len(payload.text.encode("utf-8")))
    collection = resolve_collection(payload.user_id)
    chunks_added = ingest_text(payload.text, source=payload.source, collection=collection)
    return {"chunks_added": chunks_added}


@app.post("/ingest/file")
async def ingest_file_endpoint(
    file: UploadFile, user_id: str = Form("")
) -> dict:
    content = await file.read()
    _check_size(len(content))
    filename = file.filename or "uploaded-file"
    text = extract_text_from_upload(filename, content)
    chunks_added = ingest_text(
        text, source=filename, collection=resolve_collection(user_id)
    )
    return {"chunks_added": chunks_added, "filename": filename}


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    user_id: str = ""


def _thread_config(session_id: str, user_id: str = "") -> dict:
    session = (session_id or "default").strip() or "default"
    user = (user_id or "").strip()
    # Namespace threads per tenant; legacy single-user sessions unchanged.
    thread_id = f"{user}:{session}" if user else session
    return {"configurable": {"thread_id": thread_id}}


def _is_internal(m) -> bool:
    return is_internal_message(m)


def _to_history_payload(messages: list) -> list[dict]:
    """User-visible history only — skips grader retry queries and
    intermediate RAG drafts, keeping the last AI answer per turn."""
    out: list[dict] = []
    for m in messages:
        if _is_internal(m):
            continue
        if m.type == "human":
            out.append({"role": "user", "content": m.content})
        elif m.type == "ai":
            if out and out[-1]["role"] == "assistant":
                out[-1]["content"] = m.content  # overwrite intermediate draft
            else:
                out.append({"role": "assistant", "content": m.content})
    return out


@app.get("/chat/history/{session_id}")
def chat_history_endpoint(
    session_id: str, user_id: str = "", graph=Depends(get_graph)
) -> dict:
    try:
        state = graph.get_state(_thread_config(session_id, user_id))
    except ValueError:
        # Graph built without checkpointer (e.g. in unit tests).
        return {"session_id": session_id, "messages": []}
    values = state.values if state else {}
    messages = values.get("messages", []) if values else []
    return {"session_id": session_id, "messages": _to_history_payload(messages)}


@app.delete("/chat/history/{session_id}")
def chat_history_clear_endpoint(session_id: str, graph=Depends(get_graph)) -> dict:
    # LangGraph has no delete-thread API for SqliteSaver — resetting is done
    # by moving to a fresh thread_id client-side. This endpoint exists so the
    # UI has a stable contract; it reports the thread that should be abandoned.
    return {"session_id": session_id, "cleared": True}


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.post("/chat/stream")
def chat_stream_endpoint(payload: ChatRequest, graph=Depends(get_graph)):
    # NOTE: plain `def`, not `async def`. The graph runs blocking
    # `.invoke()` calls (seconds each); Starlette executes sync endpoints in
    # a threadpool, while `async def` would stall the event loop for all
    # concurrent streams.
    collection = resolve_collection(payload.user_id)
    config = _thread_config(payload.session_id, payload.user_id)

    def event_generator():
        final_answer = ""
        sources: list[dict] = []

        for chunk in graph.stream(
            initial_state(payload.message, collection=collection),
            config=config,
            stream_mode="updates",
        ):
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

        yield _sse("done", {"answer": final_answer, "sources": sources, "session_id": (payload.session_id or "default")})

        # Persist facts the user stated this turn ("my father is X") into
        # Qdrant so they survive restarts and new sessions. Best-effort:
        # never break the chat response if extraction/ingest fails.
        try:
            from app.memory import persist_user_facts

            persist_user_facts(
                payload.message,
                final_answer,
                payload.session_id,
                collection=collection,
            )
        except Exception as exc:  # noqa: BLE001 — chat already answered
            logger.warning("User-fact persist skipped: %s", exc)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
