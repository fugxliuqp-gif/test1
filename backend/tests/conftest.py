import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_token(client):
    resp = await client.post("/api/admin/login", json={
        "username": "admin",
        "password": "admin123456",
    })
    resp.raise_for_status()
    return resp.json()["access_token"]
