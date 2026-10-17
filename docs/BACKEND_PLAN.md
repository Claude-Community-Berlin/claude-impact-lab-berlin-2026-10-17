# Backend Plan: Kita Companion

> **Superseded.** This was the first draft. The current design is `ARCHITECTURE.md` and the work split is `TEAM_PLAN.md`. Kept for history; paths are relative to `backend/`.

Based on `kita-companion-design (1).md`. Python + FastAPI REST API, documented with OpenAPI so the frontend team can build against it from minute one.

## 1. Goals

- Give the frontend team a **stable API contract** early (OpenAPI at `/docs`), so both sides work in parallel.
- Three features: **Ask**, **Draft message**, **Week board**.
- Answers come only from the Kita's own documents. No RAG, no database: all documents go into the prompt.
- Friendly errors, no secrets in Git, runs from the README on a fresh clone.

## 2. Architecture

```
Frontend (other team)
        │  JSON over HTTP (REST)
        ▼
┌─────────────────────────── FastAPI app ───────────────────────────┐
│ routers/       ask.py  draft.py  week.py  meta.py                  │
│ schemas.py     Pydantic request/response models (= the contract)   │
│ services/                                                          │
│   documents.py  load data/kita-sonnenblume/*.md once at startup    │
│   prompts.py    load prompts/*.md, fill {language} {documents}     │
│   claude.py     one wrapper around the Anthropic client            │
│   cache.py      in-memory cache for /week (key: lang + date)       │
│ errors.py      exception handlers -> friendly JSON errors          │
│ config.py      settings from .env                                  │
└───────────────┬───────────────────────────────────────────────────┘
                ▼
        Anthropic API (claude-sonnet-5-5)
```

Key decisions:

| Decision | Why |
|---|---|
| FastAPI | Auto-generated OpenAPI/Swagger, Pydantic validation, async, minimal code |
| Documents in system prompt | They are small; avoids vector DB and retrieval bugs |
| Stateless API | No accounts or sessions (out of scope). Chat history, if wanted, is sent by the frontend |
| One `claude.py` wrapper | Single place for model name, timeouts, retries, error mapping |
| In-memory cache | Enough for a demo; `/week` is the only cached call |
| CORS enabled | Frontend team will run on a different origin/port during development |

## 3. API contract (v1)

Base path: `/api/v1`. All bodies are JSON. `lang` is an ISO code: `en`, `ar`, `uk`, `tr`.

### `GET /api/v1/health`
`200 {"status": "ok"}`. For checking the server is up.

### `GET /api/v1/languages`
```json
{"languages": [{"code": "en", "label": "English", "rtl": false},
               {"code": "ar", "label": "العربية", "rtl": true}]}
```
Lets the frontend build the dropdown and flip layout direction for Arabic.

### `POST /api/v1/ask`
Request:
```json
{"question": "My son has a fever, can he go tomorrow?",
 "lang": "en",
 "history": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```
`history` is optional.

Response:
```json
{"answer": "No. In this Kita a child must be fever-free for 24h...",
 "what_to_do": "Keep him home and tell the Kita.",
 "cultural_note": "This is common in Germany to protect the other children.",
 "sources": [{"document": "house-rules.md", "section": "§4"}],
 "answered_from_documents": true,
 "suggest_draft": false}
```
When the documents do not contain the answer: `answered_from_documents: false`, `suggest_draft: true`, and `answer` says to ask the teacher. The frontend can then show the "Write to the Kita" button.

### `POST /api/v1/draft-message`
Request:
```json
{"text": "Yusuf will be late tomorrow, doctor appointment", "lang": "ar"}
```
Response:
```json
{"german_message": "Guten Morgen, Yusuf kommt morgen später...",
 "back_translation": "...in the parent's language...",
 "lang": "ar"}
```

### `GET /api/v1/week?lang=en`
Response:
```json
{"lang": "en", "generated_for": "2026-11-04",
 "items": [{"type": "event", "title": "Lantern walk", "date": "2026-11-07", "time": "17:00",
            "bring": ["a homemade lantern"],
            "cultural_note": "A German tradition...",
            "source": {"document": "letters/laternenfest.md", "section": null}},
           {"type": "closure", "title": "Kita closed (staff training)", "date": "2026-11-08"},
           {"type": "deadline", "title": "Sign the trip permission slip", "date": "2026-11-06"}]}
```
`type` is one of `event | closure | deadline | reminder`. Optional `?today=YYYY-MM-DD` overrides the date so the demo is reproducible.

### Error format (all endpoints)
```json
{"error": {"code": "ai_unavailable", "message": "Something went wrong, please try again in a moment."}}
```
| HTTP | code | When |
|---|---|---|
| 422 | `invalid_request` | Missing/empty field, unsupported `lang`, text too long |
| 502 | `ai_unavailable` | Anthropic call failed or timed out |
| 502 | `ai_bad_output` | Model returned JSON we could not parse after one retry |
| 500 | `internal_error` | Anything unexpected (details logged, never shown) |

`message` is always safe to show to the user directly.

## 4. Repo layout

```
app/
  main.py            app factory, CORS, router mounting, error handlers
  config.py          Settings (ANTHROPIC_API_KEY, MODEL, CORS_ORIGINS)
  schemas.py
  routers/           ask.py  draft.py  week.py  meta.py
  services/          documents.py  prompts.py  claude.py  cache.py
data/kita-sonnenblume/   handbook.md  house-rules.md  calendar.md  letters/*.md   (all fake)
prompts/             ask.md  draft_message.md  week.md
tests/               test_api.py  test_documents.py  eval_questions.json
requirements.txt     fastapi, uvicorn, anthropic, pydantic-settings, python-dotenv, pytest, httpx
.env.example         ANTHROPIC_API_KEY=  MODEL=claude-sonnet-5-5  CORS_ORIGINS=http://localhost:3000
.gitignore           .env, __pycache__, .venv
README.md
```
Run: `uvicorn app.main:app --reload` then open `http://localhost:8000/docs`.

## 5. AI layer

- **Structured output:** each prompt asks for JSON matching the Pydantic response model. `claude.py` parses and validates it; on failure it retries once, then returns `ai_bad_output`.
- **Language:** `{language}` is a prompt parameter. Messages in the user's language, German for the drafted message.
- **Grounding rules (from the design):** answer only from documents, cite source and section, never invent rules/dates/prices, no medical advice (quote the Kita rule and suggest a doctor), say "ask the teacher" when unknown.
- **Prompt injection:** documents and user text are wrapped in tags (`<documents>`, `<user_question>`), and the prompt states that text inside them is data, not instructions.
- **Timeouts/retries:** 30 s timeout, one retry on transient errors.
- **Caching:** `/week` is cached by `(lang, date)`. Pre-warm `en` and `ar` at startup so the demo never waits.
- **Logging:** log request id, endpoint, latency and error code. Do not log API keys.

## 6. Testing

- **Unit:** document loader, prompt filling, cache, error mapping (Anthropic client mocked).
- **API:** FastAPI `TestClient` checks every endpoint's shape and error codes with a fake `claude.py`.
- **Answer quality:** `eval_questions.json` holds the domain expert's 10 questions with the expected source. A script runs them against the real API and prints answer + source for a human to check. It includes 2-3 questions not covered by the documents that must return `answered_from_documents: false`.

## 7. Build order (matches the hackathon timeline)

| When | Task | Done when |
|---|---|---|
| By 12:30 | Skeleton, config, `claude.py`, `/health`, `/ask` with one document | One question gives one answer |
| By 13:00 | Load all documents, `ask.md` prompt, CORS, **publish OpenAPI to frontend** | Frontend can call `/ask` |
| 13:45-14:30 | `/draft-message`, `/week`, `/languages`, error handler | All endpoints return the documented shapes |
| 14:30-15:00 | Language tests (ar, uk), cache pre-warm, tests, run eval questions | Eval questions all pass the human check |
| 15:00 | Feature freeze, README run steps verified on a fresh clone | |

**Cut order if behind** (from the design): `/week` returns a static hand-written JSON file in the same shape; other languages are removed from `/languages`; `/draft-message` stays.

## 8. Working with the frontend team

1. **Agree on this contract first.** Any change to a field name goes through a message to the frontend, not a silent edit.
2. **Mock mode:** `MOCK_AI=true` in `.env` makes all endpoints return fixed example responses without calling Claude. The frontend can start building before the prompts work and without spending credits.
3. Share the running URL and `/docs` as soon as `/ask` works.
4. Keep the API key only in `.env`. One shared dev backend is enough; the frontend never needs the key.

## 9. Open questions

- **"Open language":** I read this as OpenAPI (the open standard for describing the REST API) and open-source Python libraries. If you meant something else, tell me.
- Should the chat keep history (`history` field) or is each question independent for the demo?
- Final list of languages, depends on which ones the domain expert speaks.
- Where the backend is hosted for the demo (a teammate's laptop is fine if the frontend uses the same network or a tunnel).
