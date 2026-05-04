# Phase B: 测试基础设施实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建完整的测试基础设施：共享 fixture、pytest 配置、健康检查 API + 测试、CI 流程

**Architecture:** conftest.py 集中管理 fixture，pyproject.toml 配置 pytest，独立 test 数据库隔离测试数据，GitHub Actions 自动运行

**Tech Stack:** pytest, pytest-asyncio, httpx, FastAPI TestClient, SQLite

---

### Task B1: conftest.py — 共享 Fixture 和测试数据库

**Files:**
- Modify: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: 创建 conftest.py**

```python
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
```

- [ ] **Step 2: 移除 __init__.py 中冗余内容（保持空文件）**

确认 `backend/tests/__init__.py` 为空文件即可。

- [ ] **Step 3: 提交**

```bash
git add backend/tests/
git commit -m "test: add conftest.py with shared client and auth_token fixtures"
```

---

### Task B2: pytest 配置

**Files:**
- Create: `backend/pyproject.toml`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

注意：不添加 `asyncio_default_fixture_loop_scope`，保持默认 behavior。

- [ ] **Step 2: 验证配置生效**

```bash
cd backend && python3 -m pytest tests/ -v
```

Expected: 3 tests PASS，无 warning

- [ ] **Step 3: 提交**

```bash
git add backend/pyproject.toml
git commit -m "test: add pytest configuration with asyncio_mode=auto"
```

---

### Task B3: 健康检查 API + 测试

**Files:**
- Create: `backend/app/api/health.py`
- Create: `backend/tests/test_health.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/api/v1/router.py`

- [ ] **Step 1: 创建 health.py**

```python
import time
from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import async_session_maker

router = APIRouter(tags=["health"])

start_time: float = 0.0


def set_start_time(ts: float) -> None:
    global start_time
    start_time = ts


async def check_database() -> str:
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return "connected"
    except Exception:
        return "disconnected"


@router.get("/health")
async def health_check():
    db_status = await check_database()
    overall = "healthy" if db_status == "connected" else "degraded"
    return {
        "status": overall,
        "app_name": "南京流苏官网",
        "version": "1.0.0",
        "uptime_seconds": int(time.monotonic() - start_time),
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
```

- [ ] **Step 2: 注册路由**

修改 `backend/app/api/v1/router.py`，注册 health_router：

```python
from fastapi import APIRouter

from .endpoints import router as cms_router
from .auth import router as auth_router
from .health import router as health_router

api_router = APIRouter()
api_router.include_router(cms_router)
api_router.include_router(auth_router)
api_router.include_router(health_router)
```

- [ ] **Step 3: 在 main.py 中添加 lifespan 设置 start_time**

```python
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import health
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    health.set_start_time(time.monotonic())
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

- [ ] **Step 4: 创建测试**

```python
# tests/test_health.py
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
```

- [ ] **Step 5: 运行全部测试**

```bash
cd backend && python3 -m pytest tests/ -v
```

Expected: 6 tests PASS (3 auth + 3 health)

- [ ] **Step 6: 提交**

```bash
git add backend/app/api/health.py backend/app/api/v1/router.py backend/app/main.py backend/tests/test_health.py
git commit -m "feat: add health check endpoint with tests"
```

---

### Task B4: CI 配置

**Files:**
- Create: `.github/workflows/test.yml`

- [ ] **Step 1: 创建 CI 工作流**

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install httpx pytest pytest-asyncio

    - name: Create .env
      run: |
        cd backend
        cp .env.example .env
        python3 -c "
import secrets, bcrypt
key = secrets.token_urlsafe(32)
hash = bcrypt.hashpw(b'admin123456', bcrypt.gensalt()).decode()
with open('.env', 'w') as f:
    f.write(f'SECRET_KEY={key}\n')
    f.write(f'ADMIN_USERNAME=admin\n')
    f.write(f'ADMIN_PASSWORD_HASH={hash}\n')
    f.write('CORS_ORIGINS=[\"http://localhost:5174\",\"http://localhost:8000\"]\n')
"

    - name: Run tests
      run: |
        cd backend
        PYTHONPATH=. python3 -m pytest tests/ -v
```

- [ ] **Step 2: 验证 CI 配置语法**

```bash
cd ~/projects/skills/nanjingliusu && python3 -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml')); print('YAML OK')"
```

或手动检查格式正确。

- [ ] **Step 3: 提交**

```bash
git add .github/workflows/test.yml
git commit -m "ci: add GitHub Actions test workflow"
```

---

### 验证清单

- [ ] `conftest.py` 中的 `client` fixture 被 test_auth.py 和 test_health.py 复用
- [ ] `auth_token` fixture 可被后续测试复用
- [ ] `pytest tests/ -v` 跑全部 6 个测试全部 PASS
- [ ] `GET /api/health` 返回 200 + 完整字段
- [ ] `pyproject.toml` 中 `asyncio_mode = "auto"`
- [ ] CI 配置语法正确
