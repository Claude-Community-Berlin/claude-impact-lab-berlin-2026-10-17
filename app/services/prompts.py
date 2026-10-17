"""Loads prompts/*.md. System prompts hold only stable text (instructions + documents)
so they are cached; per-request values (language, question, date) go in the user message."""

from functools import lru_cache

from app.config import get_settings
from app.services.documents import documents_block


@lru_cache
def system_prompt(name: str) -> str:
    template = (get_settings().prompts_dir / f"{name}.md").read_text(encoding="utf-8")
    return template.replace("{documents}", documents_block())


def invalidate() -> None:
    """Call after any change to the documents or prompt files."""
    system_prompt.cache_clear()
    documents_block.cache_clear()
