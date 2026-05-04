# 健康检查 API 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为后端添加一个详细的健康检查端点 `GET /api/v1/health`，返回服务状态、数据库连接、运行时长等信息。

**Architecture:** 独立模块 `health.py` 承载健康检查逻辑，通过 lifespan 记录启动时间，异步检测数据库连接，按现有路由模式注册到 `router.py`。同时移除 `main.py` 中旧的简单 health 端点。

**Tech Stack:** FastAPI, SQLAlchemy (async), aiosqlite, pytest

---

### Task 0: 安装测试依赖

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: 添加 httpx 和 pytest-asyncio 到 requirements.txt**

在 `requirements.txt` 末尾追加：
```txt
httpx==0.28.1
pytest-asyncio==0.24.0
```

- [ ] **Step 2: 安装依赖**

Run:
```bash
cd backend && pip install httpx pytest-asyncio
```
Expected: 安装成功无报错

- [ ] **Step 3: 提交**

```bash
git add backend/requirements.txt
git commit -m "chore: add httpx and pytest-asyncio for test"
```

---

### Task 1: 创建 health.py 模块和测试

**Files:**
- Create: `backend/app/api/v1/health.py`
- Create: `backend/tests/test_health.py`

- [ ] **Step 1: 编写 health.py 模块**

```python
import time
from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import async_session_maker

router = APIRouter(tags=["health"])

# 应用启动时在 lifespan 中设置
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

- [ ] **Step 2: 编写测试**

```python
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
        resp = await ac.get("/api/v1/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_has_required_fields(client):
    async with client as ac:
        resp = await ac.get("/api/v1/health")
    data = resp.json()
    assert "status" in data
    assert "database" in data
    assert "uptime_seconds" in data
    assert "timestamp" in data
    assert data["status"] in ("healthy", "degraded")


@pytest.mark.asyncio
async def test_health_endpoint_database_field(client):
    async with client as ac:
        resp = await ac.get("/api/v1/health")
    data = resp.json()
    assert data["database"] in ("connected", "disconnected")
```

- [ ] **Step 3: 运行测试，确保通过**

Run:
```bash
cd backend && python -m pytest tests/test_health.py -v
```
Expected: All 3 tests PASS

- [ ] **Step 4: 提交**

```bash
git add backend/app/api/v1/health.py backend/tests/test_health.py
git commit -m "feat: add detailed health check endpoint"
```

---

### Task 2: 注册路由并清理 main.py

**Files:**
- Modify: `backend/app/api/v1/router.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 修改 router.py 注册 health_router**

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

- [ ] **Step 2: 修改 main.py 接入 lifespan 并移除旧的 health 端点**

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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

注意：删除了旧的 `@app.get("/health")`，该端点已被 `api_router` 中的新版替代。

- [ ] **Step 3: 运行完整测试确认一切正常**

Run:
```bash
cd backend && python -m pytest tests/ -v
```
Expected: All tests PASS

- [ ] **Step 4: 提交**

```bash
git add backend/app/api/v1/router.py backend/app/main.py
git commit -m "refactor: register health router and migrate to lifespan"
```

---

### 验证清单

- [ ] `GET /api/v1/health` 返回 200
- [ ] 响应包含 `status`, `database`, `uptime_seconds`, `timestamp` 字段
- [ ] 旧 `GET /health` 端点不再存在
- [ ] 数据库正常时 status 为 `"healthy"`
- [ ] 所有测试通过
