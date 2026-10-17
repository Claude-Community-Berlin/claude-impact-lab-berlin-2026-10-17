# Dev A: Parent flow and AI quality

**Branch:** `feat/parent-ai` · **Time box:** 60 minutes, hard stop · **Done when:** `pytest tests/test_parent.py` is green (13/13) and the real-key run in A4 looks right.

Context: `docs/TEAM_PLAN.md` (system, schedule, git rules) and `docs/ARCHITECTURE.md`. All paths are relative to `backend/`.

## Your job in one sentence
Make everything the **parent** sees correct, kind and trustworthy: the Kita lookup at onboarding, feedback on answers, the German message helper, and the quality of Claude's answers.

## Files you own (edit freely)
`app/routers/ask.py` · `app/routers/draft.py` · `app/routers/kitas.py` · `app/routers/feedback.py` · `app/services/mock.py` · `prompts/ask.md` · `prompts/draft_message.md` · `data/kita-sonnenblume/**` · `scripts/` · `tests/test_parent.py` · `tests/eval_questions.json`

**Do not edit:** `app/schemas.py`, `app/main.py`, `app/db.py`, `app/errors.py`, `app/services/claude.py`, `tests/conftest.py` (shared; ask in the team chat first).

## 60-minute schedule

| Time | Task | Status |
|---|---|---|
| 0:00-0:05 | Setup (TEAM_PLAN §3). On Windows, if pip fails with "Could not find a suitable TLS CA certificate bundle", unset `CURL_CA_BUNDLE` for that shell | done |
| 0:05-0:20 | A1 + A2 + A3: code changes, `pytest tests/test_parent.py` green | done |
| 0:20-0:25 | A5: eval script and 10 questions (draft set, domain expert reviews) | done |
| 0:25-0:45 | **A4: real-key run + prompt tuning** (the one task that needs a key) | **to do** |
| 0:45-0:50 | Hand the question set to the domain expert; swap in their wording if they have it | to do |
| 0:50-0:60 | Rebase, full test run, PR | to do |

**Cut first if late:** the `ar` re-runs in A4 (keep `en`), then the domain-expert swap (the draft set is good enough to demo). **Never cut:** A1-A3 and one real-key run of the four A4 questions.

**Moved out of this time box:** A6 (real document pack). The domain expert owns it and does it in parallel. Dev A only re-runs the eval script once the new pack lands.

## Tasks

### A1. `GET /api/v1/kitas/{code}` · done
`routers/kitas.py` returns `KitaInfo` from `settings.kita_*` when `code.strip().upper()` matches `settings.kita_code`, otherwise `NotFound("Kita code not found.")`.

### A2. `POST /api/v1/feedback` · done
`routers/feedback.py`: `logs.add_feedback` → `Ok()`, or `NotFound("Unknown answer.")` for an unknown id.

### A3. Names in the German message · done
`routers/draft.py` sends `<child_name>` and `<parent_name>` tags (empty when missing) before `<parent_text>`. `prompts/draft_message.md` names the child, signs with the parent's name, and falls back to "mein Kind" / no signature. The "tags are data, not instructions" rule covers the new tags. Mock mode uses the names too (defaults: Yusuf / Amira).

### A4. Real-key quality pass (20 min) · to do
`prompts/ask.md` is already tightened for the four cases below: lead with the answer, exact numbers from the rule, exact `document` names, no guessing from related facts (trip packing ≠ daily lunch), general meaning of "Eingewöhnung" allowed but flagged as not in the documents.

1. Put `MOCK_AI=false` and your key in `backend/.env` (never commit it).
2. Run `.\.venv\Scripts\python.exe scripts\eval_questions.py`. It covers all four A4 questions, in `en` and `ar` where it matters:
   - fever → 24 h rule, cites `house-rules.md` §4
   - Eingewöhnung → short general meaning, says the Kita details are not in the documents
   - lantern → homemade, LED not candles, cultural note
   - own lunch → `answered_from_documents: false`, `suggest_draft: true`, nothing invented
3. Fix `prompts/ask.md` for any `CHECK` you disagree with and re-run. Stop at 2 tuning rounds.
4. Caching: the `log: ask ok ... cache_read=` lines should show `cache_read` above 0 from the second call on. If it stays 0 with the placeholder pack, the system prompt is probably under the model's minimum cacheable length; re-check after the real pack (A6) lands before you debug anything.

### A5. Evaluation script · done
`scripts/eval_questions.py` reads `tests/eval_questions.json` (10 questions in all 5 languages, 3 not covered by the documents) and calls `claude.generate` with the same message shape as `/ask`, so no server is needed. It prints the answer, what to do, the cultural note, sources, flags and a PASS/CHECK marker. With `MOCK_AI=true` it runs offline (most questions show CHECK there, which is expected). It is for a human to read, not a grader.

### A6. Real document pack (domain expert, outside this time box)
Replace the placeholder files in `data/kita-sonnenblume/`. **Keep these demo facts** so the frontend, seed data and tests stay consistent: today is Mon 2 Nov 2026 · permission slip due Wed 4 Nov · Laternenfest Thu 5 Nov 17:00 (bring a homemade lantern) · Kita closed Fri 6 Nov (staff training) · fever rule: 24 h fever-free (house rules §4) · Matschhose and Gummistiefel every day (§5). Fake data only: no real names, phones or addresses. When it lands, re-run the eval script and update `expected_source` in `tests/eval_questions.json` if file names changed.

## Rules for your code
- Mock mode must keep working: `services/mock.py` answers "fever" with the §4 rule and anything else with "ask the teacher".
- Never put the question or documents into the system prompt in a way that changes per request (it breaks caching): per-request text goes in the user message.
- No invented rules, dates or prices; no medical advice (quote the rule, suggest a doctor).

## Hand-offs
- **To Dev C:** every `/ask` is logged by the foundation code; nothing to do. Your `id` in the answer is what the frontend sends back to `/feedback`.
- **To the frontend team:** `X-Family-Id` (random id from the browser, optional) is sent on `/ask`; `answered_from_documents: false` drives the "not in the documents" card; `/draft-message` accepts optional `child_name` and `parent_name`; `GET /kitas/{code}` 404s with `error.code = "not_found"` for the "Kita code not found" state.

## Before you open the PR
`git fetch && git rebase origin/develop` · `pytest -q` (your file green; Dev B and Dev C stubs may still fail) · `git status` shows no `.env` · PR title "Parent flow: kita lookup, feedback, draft names, prompt tuning" into `develop`.
