"""Anonymous question log and feedback."""

from datetime import datetime, timezone

from app.db import connect


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_query(lang: str, question: str, answered_from_documents: bool, family_id: str | None) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO query_log (asked_at, lang, question, answered_from_documents, family_id)"
            " VALUES (?, ?, ?, ?, ?)",
            (now_iso(), lang, question, int(answered_from_documents), family_id),
        )
        return cur.lastrowid


def add_feedback(query_id: int, helpful: bool) -> bool:
    """Returns False if the query id does not exist."""
    with connect() as conn:
        if conn.execute("SELECT 1 FROM query_log WHERE id = ?", (query_id,)).fetchone() is None:
            return False
        conn.execute(
            "INSERT INTO feedback (query_id, helpful, created_at) VALUES (?, ?, ?)",
            (query_id, int(helpful), now_iso()),
        )
        return True
