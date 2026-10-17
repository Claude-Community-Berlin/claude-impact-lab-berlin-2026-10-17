"""SQLite connection helper and schema. One file, no server.

Usage:
    with connect() as conn:
        conn.execute("INSERT ...", (...))      # commits on exit, rolls back on error
"""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from app.config import get_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS announcements (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    type          TEXT NOT NULL,
    title         TEXT NOT NULL,          -- German source text
    message       TEXT NOT NULL DEFAULT '',
    starts_on     TEXT,                   -- YYYY-MM-DD, null when recurring
    time          TEXT,                   -- HH:MM
    deadline_on   TEXT,
    bring         TEXT NOT NULL DEFAULT '[]',   -- JSON list of German strings
    recurring     TEXT,                   -- 'daily' or null
    published_at  TEXT NOT NULL           -- ISO 8601 UTC
);

CREATE TABLE IF NOT EXISTS translations (
    announcement_id INTEGER NOT NULL REFERENCES announcements(id) ON DELETE CASCADE,
    lang            TEXT NOT NULL,
    title           TEXT NOT NULL,
    message         TEXT NOT NULL DEFAULT '',
    bring           TEXT NOT NULL DEFAULT '[]',
    cultural_note   TEXT,
    PRIMARY KEY (announcement_id, lang)
);

-- Anonymous: no name, no IP. family_id is a random id the browser sends in X-Family-Id.
CREATE TABLE IF NOT EXISTS query_log (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    asked_at                TEXT NOT NULL,   -- ISO 8601 UTC
    lang                    TEXT NOT NULL,
    question                TEXT NOT NULL,
    answered_from_documents INTEGER NOT NULL,
    family_id               TEXT
);

CREATE TABLE IF NOT EXISTS feedback (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id   INTEGER NOT NULL REFERENCES query_log(id) ON DELETE CASCADE,
    helpful    INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
"""


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    path = get_settings().db_path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
