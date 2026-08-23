from fastapi import FastAPI

app = FastAPI(title="multi-agent-rag-chat")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
