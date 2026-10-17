"""Fixed responses for MOCK_AI=true, so the frontend can build without Claude."""

from app.schemas import AskAI, DraftAI, Source, WeekAI, WeekItem


def ask(question: str) -> AskAI:
    if "fever" in question.lower() or "fieber" in question.lower():
        return AskAI(
            answer="No. In this Kita a child must be fever-free for 24 hours before coming back.",
            what_to_do="Keep your child at home and tell the Kita in the morning.",
            cultural_note="This is common in Germany to protect the other children.",
            sources=[Source(document="house-rules.md", section="§4 Illness")],
            answered_from_documents=True,
            suggest_draft=True,
        )
    return AskAI(
        answer="I don't know this from your Kita's documents. Please ask the teacher.",
        what_to_do="You can send the teacher a short message. I can write it for you in German.",
        cultural_note=None,
        sources=[],
        answered_from_documents=False,
        suggest_draft=True,
    )


def draft(text: str) -> DraftAI:
    return DraftAI(
        german_message=(
            "Guten Morgen Frau Becker,\n\nYusuf kommt morgen etwas später, "
            "weil er einen Arzttermin hat. Wir sind gegen 10 Uhr da.\n\nViele Grüße\nAmira"
        ),
        back_translation=(
            "Good morning Ms Becker, Yusuf will come a bit later tomorrow because he has "
            "a doctor's appointment. We will be there around 10. Best regards, Amira"
        ),
    )


def week() -> WeekAI:
    return WeekAI(items=[
        WeekItem(type="deadline", title="Sign the trip permission slip", date="2026-11-04",
                 source=Source(document="letters/ausflug.md")),
        WeekItem(type="event", title="Lantern walk (Laternenfest)", date="2026-11-05", time="17:00",
                 bring=["a homemade lantern", "warm clothes"],
                 cultural_note="A German tradition for St. Martin: children walk with lanterns and sing.",
                 source=Source(document="letters/laternenfest.md")),
        WeekItem(type="closure", title="Kita closed (staff training)", date="2026-11-06",
                 source=Source(document="calendar.md")),
    ])
