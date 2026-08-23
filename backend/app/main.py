from fastapi import FastAPI, UploadFile
from pydantic import BaseModel

from app.ingest import extract_text_from_upload, ingest_text

app = FastAPI(title="multi-agent-rag-chat")


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
