"""Anonymous insights for staff over query_log. Plain SQL, no Claude. Never returns family ids."""

from datetime import datetime, timedelta, timezone

from app.db import connect
from app.schemas import InsightsResponse, LanguageCount, QuestionCount


def compute() -> InsightsResponse:
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(timespec="seconds")
    with connect() as conn:
        families = conn.execute(
            "SELECT COUNT(DISTINCT family_id) FROM query_log WHERE family_id IS NOT NULL"
        ).fetchone()[0]
        this_week = conn.execute(
            "SELECT COUNT(*) FROM query_log WHERE asked_at >= ?", (week_ago,)
        ).fetchone()[0]
        languages = conn.execute(
            "SELECT lang, COUNT(DISTINCT family_id) AS c FROM query_log"
            " WHERE family_id IS NOT NULL GROUP BY lang ORDER BY c DESC, lang"
        ).fetchall()
        top = conn.execute(
            "SELECT question, COUNT(*) AS c FROM query_log"
            " GROUP BY question ORDER BY c DESC, question LIMIT 5"
        ).fetchall()
        unanswered = conn.execute(
            "SELECT question, COUNT(*) AS c FROM query_log WHERE answered_from_documents = 0"
            " GROUP BY question ORDER BY c DESC, question LIMIT 5"
        ).fetchall()

    return InsightsResponse(
        families=families,
        questions_this_week=this_week,
        languages=[LanguageCount(lang=r["lang"], count=r["c"]) for r in languages],
        top_questions=[QuestionCount(text=r["question"], count=r["c"]) for r in top],
        unanswered=[QuestionCount(text=r["question"], count=r["c"]) for r in unanswered],
    )
