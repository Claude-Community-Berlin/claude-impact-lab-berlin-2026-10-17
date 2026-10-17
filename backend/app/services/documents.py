"""Loads the Kita document pack once and renders it for the system prompt."""

from functools import lru_cache
from pathlib import Path

from app.config import get_settings


def load_documents(data_dir: Path) -> dict[str, str]:
    """Return {relative/path.md: content}, sorted so the prompt (and its cache) is stable."""
    docs = {}
    for path in sorted(data_dir.rglob("*.md")):
        docs[path.relative_to(data_dir).as_posix()] = path.read_text(encoding="utf-8").strip()
    return docs


def render_documents(docs: dict[str, str]) -> str:
    return "\n\n".join(
        f'<document name="{name}">\n{content}\n</document>' for name, content in docs.items()
    )


@lru_cache
def documents_block() -> str:
    docs = load_documents(get_settings().data_dir)
    if not docs:
        raise RuntimeError(f"No Kita documents found in {get_settings().data_dir}")
    return render_documents(docs)
