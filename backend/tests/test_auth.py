import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_admin_login_success(client):
    async with client as ac:
        resp = await ac.post("/api/admin/login", json={
            "username": "admin",
            "password": "admin123456",
        })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_admin_login_wrong_password(client):
    async with client as ac:
        resp = await ac.post("/api/admin/login", json={
            "username": "admin",
            "password": "wrong",
        })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_login_wrong_username(client):
    async with client as ac:
        resp = await ac.post("/api/admin/login", json={
            "username": "unknown",
            "password": "admin123456",
        })
    assert resp.status_code == 401
