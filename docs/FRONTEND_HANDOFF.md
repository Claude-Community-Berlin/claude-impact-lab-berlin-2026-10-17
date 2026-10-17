# Frontend handoff: Kita Companion API

Everything the frontend needs to talk to the backend. The full contract (every field, every type) is in [`openapi.json`](openapi.json); regenerate it with `python scripts/export_openapi.py` from `backend/`.

## Base URL and live docs

- Run the backend: `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload` (port **8000**).
- All endpoints live under **`/api/v1`**, e.g. `http://localhost:8000/api/v1/health`.
- Interactive docs, where you can try every call: **http://localhost:8000/docs**.
- No Anthropic key? Set `MOCK_AI=true` in `backend/.env`. `/ask`, `/draft-message` and `/week` then return fixed example answers, which is enough to build the UI.

## Avoid CORS: proxy `/api` through Vite

```ts
// frontend/vite.config.ts → inside defineConfig: server
proxy: { '/api': 'http://localhost:8000' }
```

Then call relative URLs (`fetch('/api/v1/ask', ...)`) and the browser never makes a cross-origin request.

## Headers

| Header | Where | What |
|---|---|---|
| `Content-Type: application/json` | every `POST` / `PUT` | |
| `X-Family-Id: <random id>` | parent calls (`/ask`) | Generate once with `crypto.randomUUID()`, keep it in `localStorage`. Anonymous, max 64 chars, only used to count families. Optional. |
| `Authorization: Bearer <token>` | every `/staff/*` call except login | Get the token from `POST /staff/login` with `{"code": "SONNE"}`. Demo only, not real security. |

## Screen → endpoint

| Screen | Call | Notes |
|---|---|---|
| Onboarding: Kita code | `GET /kitas/{code}` → `{code, name, city}` | 404 → show "Kita code not found" |
| Onboarding / settings: languages | `GET /languages` | en, ar, uk, tr, es; each has `rtl` (true for Arabic → set `dir="rtl"`) |
| Home: This week | `GET /week?lang=ar` → `{items: [...]}` | Each item: `type`, `title`, `date`, `time`, `bring[]`, `cultural_note`, `is_new`, `recurring` |
| Home / Ask: chat | `POST /ask` `{question, lang, history}` | `answered_from_documents: false` → show the not-found card; keep `id` for feedback |
| Answer 👍 / 👎 | `POST /feedback` `{query_id, helpful}` | `query_id` = the `id` from `/ask` |
| Composer / Result | `POST /draft-message` `{text, lang, child_name?, parent_name?}` | Returns `german_message` + `back_translation` |
| Settings: delete my data | none | Clear `localStorage`; the server stores nothing per parent |
| Staff login | `POST /staff/login` `{code}` → `{token}` | Wrong code → 401 |
| Dashboard: list / publish | `GET` / `POST /staff/announcements` | Publish translates into all languages; takes a few seconds, show a spinner |
| Dashboard: edit / delete | `PUT` / `DELETE /staff/announcements/{id}` | |
| Preview (language tabs) | `POST /staff/announcements/preview` | Same body as publish, nothing is saved |
| Documents list | `GET /staff/documents` → `[{name, title, updated_at, size}]` | `name` can contain a folder: `letters/laternenfest.md` |
| Document editor | `GET` / `PUT /staff/documents/{name}` `{content}` | Name must end in `.md`. PUT creates the file if new; `/ask` uses the new text immediately |
| Parents overview | `GET /staff/insights` | `families`, `questions_this_week`, `languages[]`, `top_questions[]`, `unanswered[]` |

**Status today:** the documents, insights, ask, draft and week endpoints work. `/kitas`, `/feedback` and the announcement endpoints still return **501 `not_implemented`** until the other branches merge. Build against the shapes in `/docs`; they will not change.

## Errors

Every error has the same shape:

```json
{ "error": { "code": "not_found", "message": "Document not found." } }
```

`message` is always safe to show to the user. Branch on `code`:

| Status | `code` | Meaning |
|---|---|---|
| 401 | `unauthorized` | Staff token missing or wrong → back to login |
| 404 | `not_found` | Unknown Kita code, document or announcement |
| 422 | `invalid_request` | Bad input (empty question, wrong document name, ...) |
| 501 | `not_implemented` | Endpoint not built yet |
| 502 | `ai_unavailable` / `ai_bad_output` | Claude failed; show the message and a retry button |

## Numbers that are still mocked in the UI

These have no backend; keep them hardcoded for the demo and don't claim otherwise:

- **"gesehen von 11 von 14"** (seen-by counts): no seen-tracking endpoint.
- **"Light rain · 9°"** (weather): would need an external weather API.
- **"14 Familien verbunden"** and **"38 Fragen"**: `GET /staff/insights` now gives real `families` and `questions_this_week`, but they only count families who asked a question, so the numbers start at 0. Use them on the parents overview if you want live data.

All data in the demo is fake. Never enter real children's or parents' data.
