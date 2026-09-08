import os

# Must run before `app.config` is imported anywhere (including by other test
# modules), so the whole suite talks to a disposable Qdrant collection instead
# of the app's real "documents" collection.
os.environ.setdefault("QDRANT_COLLECTION", "documents_pytest")

import pytest


@pytest.fixture(scope="session", autouse=True)
def _isolated_qdrant_collection():
    """Give the test suite its own Qdrant collection, wiped clean before and
    after the run, so tests never read or leave data in the real collection
    the live app queries against."""
    from app.config import settings
    from app.vectorstore import get_client

    client = get_client()
    name = settings.qdrant_collection

    if client.collection_exists(name):
        client.delete_collection(name)

    yield

    if client.collection_exists(name):
        client.delete_collection(name)
