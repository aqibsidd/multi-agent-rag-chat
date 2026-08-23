import io

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

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


def extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_upload(filename: str, content: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        return extract_pdf_text(content)
    return content.decode("utf-8", errors="replace")
