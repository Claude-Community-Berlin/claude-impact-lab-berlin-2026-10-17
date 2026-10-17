"""Loads the Kita document pack once and renders it for the system prompt, and lets staff
list, read and write the documents."""

from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from app.config import get_settings
from app.errors import InvalidRequest, NotFound


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


# ---------- staff document editor ----------

def _safe_path(name: str) -> Path:
    """Resolve a document name inside data_dir, or raise InvalidRequest."""
    data_dir = get_settings().data_dir.resolve()
    if (not name.endswith(".md") or "\\" in name or name.startswith("/")
            or any(part.startswith(".") for part in Path(name).parts)):
        raise InvalidRequest("Invalid document name.")
    target = (data_dir / name).resolve()
    if not target.is_relative_to(data_dir) or target == data_dir:
        raise InvalidRequest("Invalid document name.")
    return target


def _title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or fallback
    return fallback


def list_docs() -> list[dict]:
    data_dir = get_settings().data_dir
    docs = []
    for path in sorted(data_dir.rglob("*.md")):
        stat = path.stat()
        docs.append({
            "name": path.relative_to(data_dir).as_posix(),
            "title": _title(path.read_text(encoding="utf-8"), path.name),
            "updated_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds"),
            "size": stat.st_size,
        })
    return sorted(docs, key=lambda d: d["name"])


def read_doc(name: str) -> dict:
    target = _safe_path(name)
    if not target.is_file():
        raise NotFound("Document not found.")
    return {"name": name, "content": target.read_text(encoding="utf-8")}


def write_doc(name: str, content: str) -> dict:
    from app.services import prompts  # imported here: prompts imports this module

    target = _safe_path(name)
    text = content.replace("\r\n", "\n").replace("\r", "\n")
    if not text.endswith("\n"):
        text += "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    prompts.invalidate()
    return {"name": name, "content": text}
