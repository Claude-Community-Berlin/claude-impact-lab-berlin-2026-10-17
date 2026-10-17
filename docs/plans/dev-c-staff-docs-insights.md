# Dev C: Knowledge base, insights, README and frontend handoff

**Branch:** `feat/staff-docs-insights` · **Time box:** about 110 minutes · **Done when:** `pytest tests/test_staff_docs_insights.py` is green, the README works on a fresh clone, and the frontend team has what they need.

Context: `docs/TEAM_PLAN.md` (system, schedule, git rules) and `docs/ARCHITECTURE.md`. All paths are relative to `backend/` unless they start with `docs/`, `frontend/` or are the root `README.md`.

## Your job in one sentence
Let Kita staff keep the documents up to date (so `/ask` always uses the newest text), show them anonymous insights, and make the whole project runnable and understandable for judges and for the frontend team.

## Files you own (edit freely)
`app/routers/staff_documents.py` · `app/routers/staff_insights.py` · `app/services/documents.py` · `app/services/insights.py` (new) · `scripts/export_openapi.py` (new) · root `README.md` · `tests/test_staff_docs_insights.py`

**Do not edit:** `app/schemas.py`, `app/main.py`, `app/db.py`, `app/errors.py`, `app/services/claude.py`, `tests/conftest.py`.

## Helpers already available
- `prompts.invalidate()` clears the cached documents and prompts. **Call it after every write.**
- `documents.load_documents(dir)` and `documents.documents_block()` (cached) already exist.
- `errors.NotFound(...)` and `errors.InvalidRequest(...)` → `{"error": {"code": ..., "message": ...}}`.
- `from app.db import connect`; table `query_log` (`asked_at` ISO UTC, `lang`, `question`, `answered_from_documents` 0/1, `family_id` nullable).
- Schemas: `DocumentInfo`, `DocumentContent`, `DocumentWrite`, `InsightsResponse`, `LanguageCount`, `QuestionCount`.

## Tasks

### C1. Documents API (30 min)
- `GET /staff/documents` → `list[DocumentInfo]`: `name` (relative posix path, e.g. `letters/laternenfest.md`), `title` (first `# ` heading, else the file name), `updated_at` (file mtime, ISO), `size` (bytes). Sorted by name.
- `GET /staff/documents/{name:path}` → `DocumentContent`; missing file → `NotFound("Document not found.")`.
- `PUT /staff/documents/{name:path}` → writes the file (creates it if new, including the folder), calls `prompts.invalidate()`, returns `DocumentContent`.
- **Path safety (required):** the name must end in `.md`; build `target = (data_dir / name).resolve()` and reject with `InvalidRequest("Invalid document name.")` unless `target` is inside `data_dir.resolve()`. No `..`, no absolute paths, no backslashes. Write UTF-8, `\n` line endings.
- Put the file logic in `services/documents.py` (`list_docs()`, `read_doc(name)`, `write_doc(name, content)`), keep the router thin.

### C2. Insights (30 min), `services/insights.py` + router
Plain SQL, no Claude. Suggested queries over `query_log`:
```sql
SELECT COUNT(DISTINCT family_id) FROM query_log WHERE family_id IS NOT NULL;      -- families
SELECT COUNT(*) FROM query_log WHERE asked_at >= :week_ago;                       -- questions_this_week
SELECT lang, COUNT(DISTINCT family_id) c FROM query_log
  WHERE family_id IS NOT NULL GROUP BY lang ORDER BY c DESC;                      -- languages
SELECT question AS text, COUNT(*) c FROM query_log
  GROUP BY question ORDER BY c DESC LIMIT 5;                                      -- top_questions
SELECT question AS text, COUNT(*) c FROM query_log
  WHERE answered_from_documents = 0 GROUP BY question ORDER BY c DESC LIMIT 5;    -- unanswered
```
`week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(timespec="seconds")` (same format `logs.now_iso()` writes, so string comparison works). Empty database returns zeros and empty lists, not errors. Questions are grouped by exact text (no Claude clustering). Never return `family_id` or anything that identifies a family.

### C3. README (20 min), root `README.md`
Replace the event text with the team's README (hackathon rule: who it is for, the problem, how to run). Use the three one-liners from `docs/design/kita-companion-design.md` ("Who it's for / Their problem today / What the demo lets them do"). Add: how to run backend (`cd backend`, venv, `.env`, `uvicorn`) and frontend, the demo login (`SONNE`), `MOCK_AI`, a short architecture picture or link to `docs/ARCHITECTURE.md`, and a **Credits** list (FastAPI, Uvicorn, Pydantic, Anthropic SDK, React, Vite). State plainly that all data is fake.

### C4. OpenAPI export and frontend handoff (15 min)
- `scripts/export_openapi.py` imports `app.main.app`, writes `docs/openapi.json` (`json.dumps(app.openapi(), indent=2)`). Run it after the other branches merge so the file shows the final contract.
- Write `docs/FRONTEND_HANDOFF.md` for the frontend team (1 page): base URL, `/docs`, the screen-to-endpoint table from `docs/ARCHITECTURE.md` §3, headers (`X-Family-Id`, `Authorization: Bearer`), the error format with `message` safe to show, and this Vite snippet to avoid CORS:
  ```ts
  // frontend/vite.config.ts → inside defineConfig: server
  proxy: { '/api': 'http://localhost:8000' }
  ```
  Also note the mocked UI numbers ("14 Familien", weather, "gesehen von 11") that have no backend yet.

### C5. Fresh-clone test (15 min, last)
After everything is merged to `develop`: clone into a new empty folder, follow your README word for word (with `MOCK_AI=true`, then once with a real key), run `pytest`, open `/docs`. Fix the README for anything that failed.

## Rules for your code
- A document write must never touch files outside `data_dir`. The tests use a temporary copy of the pack; never point a test at the real `data/kita-sonnenblume`.
- Do not log document contents.

## Hand-offs
- **From Dev A:** the real document pack lands in `data/kita-sonnenblume/`; your list endpoint will show it automatically.
- **To the frontend team:** `docs/FRONTEND_HANDOFF.md` and `docs/openapi.json`.

## Before you open the PR
`git fetch && git rebase origin/develop` · `pytest -q` (your file green) · `git status` shows no `.env` · PR title "Document editor, insights, README and frontend handoff" into `develop`.
