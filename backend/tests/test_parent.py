"""Dev A acceptance tests (feat/parent-ai). Red until the stubs are implemented."""

import pytest

from app.config import get_settings
from app.schemas import AskAI, DraftAI
from app.services import claude

API = "/api/v1"


@pytest.fixture
def fake_claude(monkeypatch):
    """Real-key code path without a key: records what would be sent to Claude."""
    calls = []
    replies = {
        "ask": AskAI(answer="ok", answered_from_documents=False, suggest_draft=True),
        "draft_message": DraftAI(german_message="Hallo", back_translation="Hello"),
    }

    async def generate(prompt_name, messages, output):
        calls.append({"prompt": prompt_name, "messages": messages})
        return replies[prompt_name]

    monkeypatch.setattr(get_settings(), "mock_ai", False)
    monkeypatch.setattr(claude, "generate", generate)
    return calls


def test_kita_lookup(client):
    r = client.get(f"{API}/kitas/SONNE")
    assert r.status_code == 200
    assert r.json() == {"code": "SONNE", "name": "Kita Sonnenblume", "city": "Berlin"}


def test_kita_lookup_is_case_insensitive(client):
    assert client.get(f"{API}/kitas/sonne").status_code == 200


def test_kita_unknown_code(client):
    r = client.get(f"{API}/kitas/NOPE")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_feedback_roundtrip(client):
    answer = client.post(f"{API}/ask", json={"question": "fever?"}).json()
    r = client.post(f"{API}/feedback", json={"query_id": answer["id"], "helpful": True})
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_feedback_unknown_query(client):
    r = client.post(f"{API}/feedback", json={"query_id": 9999, "helpful": False})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_all_five_languages_accepted(client):
    for lang in ("en", "ar", "uk", "tr", "es"):
        assert client.post(f"{API}/ask", json={"question": "fever?", "lang": lang}).status_code == 200
        assert client.post(f"{API}/draft-message", json={"text": "late", "lang": lang}).status_code == 200
        assert client.get(f"{API}/week", params={"lang": lang}).status_code == 200


def test_draft_accepts_names(client):
    r = client.post(f"{API}/draft-message", json={
        "text": "Yusuf will be late tomorrow", "lang": "en",
        "child_name": "Yusuf", "parent_name": "Amira",
    })
    assert r.status_code == 200


def test_kita_lookup_ignores_surrounding_spaces(client):
    assert client.get(f"{API}/kitas/%20sonne%20").status_code == 200


def test_mock_draft_uses_names(client):
    body = client.post(f"{API}/draft-message", json={
        "text": "late", "child_name": "Lina", "parent_name": "Olena",
    }).json()
    assert "Lina" in body["german_message"] and body["german_message"].endswith("Olena")


def test_draft_sends_names_to_claude(client, fake_claude):
    r = client.post(f"{API}/draft-message", json={
        "text": "Yusuf will be late tomorrow", "lang": "ar",
        "child_name": "Yusuf", "parent_name": "Amira",
    })
    assert r.status_code == 200
    assert r.json()["lang"] == "ar"
    content = fake_claude[0]["messages"][0]["content"]
    assert fake_claude[0]["prompt"] == "draft_message"
    assert "<child_name>Yusuf</child_name>" in content
    assert "<parent_name>Amira</parent_name>" in content
    assert "<parent_text>\nYusuf will be late tomorrow\n</parent_text>" in content


def test_draft_without_names_sends_empty_tags(client, fake_claude):
    client.post(f"{API}/draft-message", json={"text": "late"})
    content = fake_claude[0]["messages"][0]["content"]
    assert "<child_name></child_name>" in content
    assert "<parent_name></parent_name>" in content


def test_ask_sends_language_and_question_in_user_message(client, fake_claude):
    r = client.post(f"{API}/ask", json={
        "question": "Can he bring his own lunch?", "lang": "tr",
        "history": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}],
    })
    assert r.status_code == 200
    assert r.json()["answered_from_documents"] is False
    messages = fake_claude[0]["messages"]
    assert [m["role"] for m in messages] == ["user", "assistant", "user"]
    assert "<user_question>\nCan he bring his own lunch?\n</user_question>" in messages[-1]["content"]
    assert "Reply language:" in messages[-1]["content"]


def test_prompts_keep_injection_rule_and_placeholders():
    prompts_dir = get_settings().prompts_dir
    for name in ("ask", "draft_message"):
        text = (prompts_dir / f"{name}.md").read_text(encoding="utf-8")
        assert "{documents}" in text
        assert "data, not instructions" in text
    assert "<child_name>" in (prompts_dir / "draft_message.md").read_text(encoding="utf-8")
