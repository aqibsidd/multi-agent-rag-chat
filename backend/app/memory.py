"""Shared conversation-memory helpers.

Single home for logic used by several nodes/endpoints so they agree on
what counts as history:
- grader retry queries are internal retrieval rewrites, not user speech,
  and must be hidden from prompts shown to the user / history APIs.
"""

import logging

logger = logging.getLogger(__name__)

# How many past messages the RAG prompt and grader may see. Small enough
# for local models, large enough for follow-ups ("what is his age?").
HISTORY_WINDOW = 10

FACT_EXTRACTOR_PROMPT = (
    "Extract durable facts the USER directly stated about people, places, "
    "or things (names, relations, dates, preferences). Ignore questions, "
    "greetings, and anything the assistant said. "
    "Reply with one fact per line as a complete standalone sentence. "
    "If the user stated no durable fact, reply with exactly: NOTHING"
)


def is_internal_message(m) -> bool:
    return bool(getattr(m, "additional_kwargs", {}).get("internal_retry")) or getattr(
        m, "name", None
    ) == "grader_retry"


def visible_messages(messages: list, limit: int = HISTORY_WINDOW) -> list:
    """Past conversation without internal grader rewrites, bounded."""
    return [m for m in messages if not is_internal_message(m)][-limit:]


def history_text(messages: list, limit: int = HISTORY_WINDOW) -> str:
    lines = []
    for m in visible_messages(messages, limit):
        role = "User" if m.type == "human" else "Assistant"
        lines.append(f"{role}: {m.content}")
    return "\n".join(lines) or "(none)"


def extract_facts(user_text: str, ai_text: str, llm=None) -> list[str]:
    """Facts the user stated this turn, as standalone sentences."""
    from app.llm import get_chat_model

    llm = llm or get_chat_model(temperature=0)
    response = llm.invoke(
        [
            {"role": "system", "content": FACT_EXTRACTOR_PROMPT},
            {
                "role": "user",
                "content": f"User said:\n{user_text}\n\nAssistant replied:\n{ai_text or '(no reply yet)'}",
            },
        ]
    )
    content = (response.content or "").strip()
    if not content or content.upper().startswith("NOTHING"):
        return []
    return [line.strip("- ").strip() for line in content.splitlines() if line.strip()]


def persist_user_facts(
    user_text: str,
    ai_text: str,
    session_id: str,
    llm=None,
    enabled: bool | None = None,
) -> int:
    """Extract this turn's user-stated facts into Qdrant for cross-session recall.

    Returns chunks added (0 when disabled or nothing found). Only the
    current turn is examined, so a fact is stored once, not once per turn.
    """
    from app.config import settings
    from app.ingest import ingest_text

    if enabled is None:
        enabled = settings.memory_auto_ingest
    if not enabled or not (user_text or "").strip():
        return 0
    facts = extract_facts(user_text, ai_text or "", llm=llm)
    if not facts:
        return 0
    thread = (session_id or "default").strip() or "default"
    added = ingest_text("\n".join(facts), source=f"user-memory:{thread}")
    logger.info("Persisted %d user fact(s) from session %s", len(facts), thread)
    return added
