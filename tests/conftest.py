"""Shared fixtures. Every test runs in mock mode with its own empty SQLite file."""

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.db import init_db
from app.main import app
from app.services import cache, prompts

API = "/api/v1"


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    settings = get_settings()
    monkeypatch.setattr(settings, "mock_ai", True)
    monkeypatch.setattr(settings, "db_path", tmp_path / "test.db")
    cache.clear()
    prompts.invalidate()
    init_db()
    yield
    cache.clear()
    prompts.invalidate()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def staff(client):
    """Authorization header for /staff/* routes."""
    token = client.post(f"{API}/staff/login", json={"code": "SONNE"}).json()["token"]
    return {"Authorization": f"Bearer {token}"}
