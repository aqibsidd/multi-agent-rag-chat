"""Tiny recall eval: 10 fact Q/A pairs must retrieve their chunk top-4.

Regression net for embedding/chunking/threshold changes — if recall drops
here, a 'tuning' PR made retrieval worse. Uses real Ollama embeddings +
real Qdrant (test collection), so it needs `ollama serve` like the rest.
"""

import uuid

from app.config import settings
from app.ingest import ingest_text
from app.vectorstore import get_vectorstore

PAIRS = [
    ("refund window is 30 days", "how long is the refund window"),
    ("office opens at 9am sharp", "what time does the office open"),
    ("warehouse is in Austin Texas", "where is the warehouse"),
    ("deployments happen every Friday", "when do deployments happen"),
    ("CEO is Maria Santos", "who is the CEO"),
    ("support email is help@example.com", "what is the support email"),
    ("warranty covers two years", "how long is the warranty"),
    ("trains leave platform nine", "which platform do trains leave from"),
    ("library closes at midnight", "when does the library close"),
    ("intern stipend is forty thousand", "what is the intern stipend"),
]


def test_recall_eval_all_facts_retrievable_top4():
    marker = uuid.uuid4().hex[:8]
    for i, (fact, _) in enumerate(PAIRS):
        ingest_text(f"Eval {marker}-{i}: {fact}.", source=f"eval-{marker}-{i}")

    store = get_vectorstore()
    missed = []
    for i, (_, query) in enumerate(PAIRS):
        hits = store.similarity_search(f"eval {marker} {query}", k=4)
        if not any(f"{marker}-{i}" in h.page_content for h in hits):
            missed.append(i)
        # Gated chunks must also clear the production relevance threshold.
        assert all(
            s >= settings.relevance_min_score
            for _, s in store.similarity_search_with_score(
                f"eval {marker} {query}", k=4
            )[:1]
        )

    assert not missed, f"recall missed pairs: {missed}"
