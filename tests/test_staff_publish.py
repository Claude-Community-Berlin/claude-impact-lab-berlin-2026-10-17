"""Dev B acceptance tests (feat/staff-publish). Red until the stubs are implemented."""

API = "/api/v1"
LANGS = {"en", "ar", "uk", "tr", "es"}

NEW = {
    "type": "event",
    "title": "Sommerfest",
    "message": "Wir feiern am Freitag.",
    "starts_on": "2026-11-05",
    "time": "16:00",
    "bring": ["Kuchen"],
}


def publish(client, staff, body=None):
    r = client.post(f"{API}/staff/announcements", json=body or NEW, headers=staff)
    assert r.status_code == 201, r.text
    return r.json()


def test_publish_translates_to_all_languages(client, staff):
    ann = publish(client, staff)
    assert ann["title"] == "Sommerfest"
    assert set(ann["translations"]) == LANGS
    assert all(t["title"] for t in ann["translations"].values())


def test_list_returns_published(client, staff):
    ann = publish(client, staff)
    ids = [a["id"] for a in client.get(f"{API}/staff/announcements", headers=staff).json()]
    assert ann["id"] in ids


def test_published_item_appears_in_week_in_parent_language(client, staff):
    ann = publish(client, staff)
    week = client.get(f"{API}/week", params={"lang": "ar", "today": "2026-11-04"}).json()
    item = next(i for i in week["items"] if i["id"] == ann["id"])
    assert item["title"] == ann["translations"]["ar"]["title"]
    assert item["date"] == "2026-11-05"
    assert item["is_new"] is True


def test_week_only_shows_next_seven_days(client, staff):
    ann = publish(client, staff, {**NEW, "starts_on": "2026-12-24"})
    week = client.get(f"{API}/week", params={"lang": "en", "today": "2026-11-04"}).json()
    assert ann["id"] not in [i["id"] for i in week["items"]]


def test_seed_makes_week_non_empty(client):
    week = client.get(f"{API}/week", params={"lang": "en", "today": "2026-11-04"}).json()
    assert len(week["items"]) > 0
    assert any(i["recurring"] == "daily" for i in week["items"])  # the Matschhose reminder


def test_preview_does_not_save(client, staff):
    before = len(client.get(f"{API}/staff/announcements", headers=staff).json())
    r = client.post(f"{API}/staff/announcements/preview", json=NEW, headers=staff)
    assert r.status_code == 200
    assert set(r.json()["translations"]) == LANGS
    after = len(client.get(f"{API}/staff/announcements", headers=staff).json())
    assert before == after


def test_update_retranslates(client, staff):
    ann = publish(client, staff)
    r = client.put(f"{API}/staff/announcements/{ann['id']}", json={**NEW, "title": "Herbstfest"}, headers=staff)
    assert r.status_code == 200
    assert r.json()["title"] == "Herbstfest"
    assert set(r.json()["translations"]) == LANGS


def test_delete(client, staff):
    ann = publish(client, staff)
    assert client.delete(f"{API}/staff/announcements/{ann['id']}", headers=staff).json() == {"ok": True}
    ids = [a["id"] for a in client.get(f"{API}/staff/announcements", headers=staff).json()]
    assert ann["id"] not in ids


def test_delete_unknown_is_404(client, staff):
    r = client.delete(f"{API}/staff/announcements/9999", headers=staff)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_publish_failure_saves_nothing(client, staff, monkeypatch):
    """If translation fails, no half-published item may exist."""
    from app.config import get_settings
    from app.errors import AIError
    from app.services import claude

    monkeypatch.setattr(get_settings(), "mock_ai", False)

    async def boom(*args, **kwargs):
        raise AIError("ai_unavailable", "test")

    monkeypatch.setattr(claude, "generate", boom)
    before = len(client.get(f"{API}/staff/announcements", headers=staff).json())
    r = client.post(f"{API}/staff/announcements", json=NEW, headers=staff)
    assert r.status_code == 502
    after = len(client.get(f"{API}/staff/announcements", headers=staff).json())
    assert before == after
