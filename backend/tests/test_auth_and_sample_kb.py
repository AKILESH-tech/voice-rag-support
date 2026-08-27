import hashlib
import time
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.auth.access import get_passcode
from app.db.database import init_db


def _token() -> str:
    today = time.strftime("%Y-%m-%d")
    return hashlib.sha256(f"{get_passcode()}{today}".encode()).hexdigest()


@pytest.mark.anyio
async def test_verify_auth_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/auth/verify", json={"passcode": get_passcode()})
    assert res.status_code == 200
    assert "token" in res.json()


@pytest.mark.anyio
async def test_sample_kb_requires_access_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/sample-kb")
    assert res.status_code == 401


@pytest.mark.anyio
async def test_sample_kb_available_with_token():
    headers = {"x-access-token": _token()}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/sample-kb", headers=headers)
    assert res.status_code == 200
    templates = res.json()
    assert len(templates) >= 3
    assert "filename" in templates[0]


@pytest.mark.anyio
async def test_sample_kb_bootstrap_endpoint():
    init_db()
    headers = {"x-access-token": _token()}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/sample-kb/bootstrap", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "created" in data
    assert "existing" in data
