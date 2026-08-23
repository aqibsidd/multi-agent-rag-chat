import uuid

from app.ingest import ingest_text
from app.vectorstore import get_vectorstore


def test_ingest_text_chunks_embeds_and_is_retrievable():
    # Unique marker per run so this test doesn't collide with prior runs'
    # leftover data in the shared dev Qdrant collection.
    marker = uuid.uuid4().hex
    text = (
        f"The secret code for this test is {marker}. " * 5
        + "It appears nowhere else in the knowledge base."
    )

    chunks_added = ingest_text(text, source=f"test-{marker}")
    assert chunks_added >= 1

    results = get_vectorstore().similarity_search(f"secret code {marker}", k=1)
    assert len(results) == 1
    assert marker in results[0].page_content
    assert results[0].metadata["source"] == f"test-{marker}"


def test_ingest_empty_text_adds_nothing():
    assert ingest_text("", source="empty") == 0
