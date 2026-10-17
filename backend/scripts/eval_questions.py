"""Ask the domain expert's questions and print the answers for a human to check.

Run from backend/:  .\\.venv\\Scripts\\python.exe scripts\\eval_questions.py [path/to/questions.json]

Uses the same prompt and message shape as POST /ask, but calls Claude directly, so no server
is needed. With MOCK_AI=true it prints the mock answers (useful to test the script itself).
PASS = the expected document is cited (or, for expected_source null, the answer admits it is
not in the documents). CHECK = a human should look. This is not an automatic grader.
Watch the "ask ok ... cache_read=" log lines: from the second call on, cache_read should be > 0.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from app.config import get_settings  # noqa: E402
from app.schemas import LANGUAGES, AskAI  # noqa: E402
from app.services import claude, mock  # noqa: E402


def verdict(expected: str | None, result: AskAI) -> str:
    cited = {s.document for s in result.sources}
    if expected is None:
        ok = not result.answered_from_documents and not cited
    else:
        ok = result.answered_from_documents and expected in cited
    return "PASS" if ok else "CHECK"


async def ask(question: str, lang: str) -> AskAI:
    if get_settings().mock_ai:
        return mock.ask(question)
    content = f"Reply language: {LANGUAGES[lang]['name']}\n\n<user_question>\n{question}\n</user_question>"
    return await claude.generate("ask", [{"role": "user", "content": content}], AskAI)


async def main(path: Path) -> None:
    logging.basicConfig(level=logging.INFO, format="    log: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    questions = json.loads(path.read_text(encoding="utf-8"))
    print(f"{len(questions)} questions, mock_ai={get_settings().mock_ai}\n")

    passed = 0
    for i, q in enumerate(questions, 1):
        result = await ask(q["question"], q["lang"])
        mark = verdict(q["expected_source"], result)
        passed += mark == "PASS"
        sources = ", ".join(f"{s.document} {s.section or ''}".strip() for s in result.sources) or "-"
        print(f"[{mark}] {i}. ({q['lang']}) {q['question']}")
        print(f"    expected: {q['expected_source'] or 'not in documents'}")
        print(f"    answer:   {result.answer}")
        print(f"    to do:    {result.what_to_do or '-'}")
        print(f"    culture:  {result.cultural_note or '-'}")
        print(f"    sources:  {sources}")
        print(f"    from_docs={result.answered_from_documents} suggest_draft={result.suggest_draft}\n")

    print(f"{passed}/{len(questions)} PASS. Read every answer anyway: tone, simple words, no invented facts.")


if __name__ == "__main__":
    default = ROOT / "tests" / "eval_questions.json"
    asyncio.run(main(Path(sys.argv[1]) if len(sys.argv) > 1 else default))
