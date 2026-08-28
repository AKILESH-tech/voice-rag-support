import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import init_db


def _headers() -> dict:
    return {"Authorization": "Bearer dev_voice_user"}


@pytest.mark.anyio
async def test_auth_me_with_dev_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/auth/me", headers=_headers())
    assert res.status_code == 200
    assert res.json()["uid"] == "voice_user"


@pytest.mark.anyio
async def test_sample_kb_requires_auth_header():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/sample-kb")
    assert res.status_code == 401


@pytest.mark.anyio
async def test_sample_kb_available_with_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/sample-kb", headers=_headers())
    assert res.status_code == 200
    templates = res.json()
    assert len(templates) >= 3
    assert "filename" in templates[0]


@pytest.mark.anyio
async def test_sample_kb_bootstrap_endpoint():
    init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/sample-kb/bootstrap", headers=_headers())
    assert res.status_code == 200
    data = res.json()
    assert "created" in data
    assert "existing" in data
