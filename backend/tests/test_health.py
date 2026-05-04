import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(client):
    async with client as ac:
        resp = await ac.get("/api/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_has_required_fields(client):
    async with client as ac:
        resp = await ac.get("/api/health")
    data = resp.json()
    assert "status" in data
    assert "database" in data
    assert "uptime_seconds" in data
    assert "timestamp" in data
    assert data["status"] in ("healthy", "degraded")


@pytest.mark.asyncio
async def test_health_endpoint_database_field(client):
    async with client as ac:
        resp = await ac.get("/api/health")
    data = resp.json()
    assert data["database"] in ("connected", "disconnected")
