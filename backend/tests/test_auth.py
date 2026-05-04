import pytest


@pytest.mark.asyncio
async def test_admin_login_success(client):
    resp = await client.post("/api/admin/login", json={
        "username": "admin",
        "password": "admin123456",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_admin_login_wrong_password(client):
    resp = await client.post("/api/admin/login", json={
        "username": "admin",
        "password": "wrong",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_login_wrong_username(client):
    resp = await client.post("/api/admin/login", json={
        "username": "unknown",
        "password": "admin123456",
    })
    assert resp.status_code == 401
