import os

# Must run before `app.config` is imported anywhere (including by other test
# modules), so the whole suite talks to a disposable Qdrant collection instead
# of the app's real "documents" collection.
os.environ.setdefault("QDRANT_COLLECTION", "documents_pytest")
# Chat endpoints auto-persist user-stated facts into Qdrant via a real LLM
# call — disable for hermetic tests (test_memory.py covers it with fakes).
os.environ.setdefault("MEMORY_AUTO_INGEST", "false")

import pytest


def _wipe_test_collections(client, base: str) -> None:
    """Delete the base test collection plus any per-user namespaces from
    prior runs (`<base>_u_*`). Without this, near-identical chunks from old
    runs crowd out fresh markers in top-k and make recall tests flaky."""
    for collection in client.get_collections().collections:
        if collection.name == base or collection.name.startswith(base + "_u_"):
            client.delete_collection(collection.name)


@pytest.fixture(scope="session", autouse=True)
def _isolated_qdrant_collection():
    """Give the test suite its own Qdrant collection, wiped clean before and
    after the run, so tests never read or leave data in the real collection
    the live app queries against."""
    from app.config import settings
    from app.vectorstore import get_client

    client = get_client()
    name = settings.qdrant_collection

    _wipe_test_collections(client, name)

    yield

    _wipe_test_collections(client, name)
