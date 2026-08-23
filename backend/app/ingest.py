from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.vectorstore import get_vectorstore

_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)


def ingest_text(text: str, source: str) -> int:
    chunks = _splitter.split_text(text)
    docs = [
        Document(page_content=chunk, metadata={"source": source, "chunk": i})
        for i, chunk in enumerate(chunks)
    ]

    if not docs:
        return 0

    get_vectorstore().add_documents(docs)
    return len(docs)
