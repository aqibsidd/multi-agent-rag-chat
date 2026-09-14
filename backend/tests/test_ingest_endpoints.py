import io
import uuid

from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.ingest import extract_pdf_text
from app.main import app
from app.vectorstore import get_vectorstore

client = TestClient(app)


def test_ingest_text_endpoint_round_trips():
    marker = uuid.uuid4().hex
    response = client.post(
        "/ingest/text",
        json={"text": f"Marker fact {marker}: the office opens at 9am.", "source": f"api-{marker}"},
    )

    assert response.status_code == 200
    assert response.json()["chunks_added"] >= 1

    results = get_vectorstore().similarity_search(f"office hours {marker}", k=1)
    assert marker in results[0].page_content


def test_ingest_file_endpoint_with_txt_round_trips():
    marker = uuid.uuid4().hex
    content = f"Uploaded file fact {marker}: the warehouse is in Austin.".encode()

    response = client.post(
        "/ingest/file",
        files={"file": (f"notes-{marker}.txt", io.BytesIO(content), "text/plain")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["chunks_added"] >= 1
    assert body["filename"] == f"notes-{marker}.txt"

    results = get_vectorstore().similarity_search(f"warehouse location {marker}", k=1)
    assert marker in results[0].page_content


def test_extract_pdf_text_does_not_crash_on_a_blank_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = io.BytesIO()
    writer.write(buffer)

    text = extract_pdf_text(buffer.getvalue())
    assert isinstance(text, str)


def test_ingest_text_rejects_oversize_payload():
    big = "x" * (11 * 1024 * 1024)  # over the 10MB default
    response = client.post("/ingest/text", json={"text": big, "source": "big"})
    assert response.status_code == 413


def test_user_namespaces_keep_documents_isolated():
    marker = uuid.uuid4().hex
    client.post(
        "/ingest/text",
        json={
            "text": f"Secret {marker}: user A loves mangoes.",
            "source": f"a-{marker}",
            "user_id": "user-a",
        },
    )

    from app.vectorstore import get_vectorstore, resolve_collection

    hits_b = get_vectorstore(collection=resolve_collection("user-b")).similarity_search(
        f"secret {marker} mangoes", k=4
    )
    assert all(marker not in d.page_content for d in hits_b)

    hits_a = get_vectorstore(collection=resolve_collection("user-a")).similarity_search(
        f"secret {marker} mangoes", k=4
    )
    assert any(marker in d.page_content for d in hits_a)
