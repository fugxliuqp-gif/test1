# Phase C: 统一响应格式实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use `- [ ]` syntax.

**Goal:** 所有 API 响应统一为 `{code, message, data}` 格式，前端错误处理保持一致

**Architecture:** `ApiResponse` 通用模型 + `success()`/`error()` 工厂函数 + 全局异常处理器，逐一手动包裹每个端点

**Response Format:**
```json
// 成功
{"code": 200, "message": "ok", "data": <payload>}
// 错误
{"code": 404, "message": "资源不存在", "data": null}
// 列表
{"code": 200, "message": "ok", "data": [<item>, ...]}
// 无数据操作（删除）
{"code": 200, "message": "删除成功", "data": null}
```

**Tech Stack:** FastAPI, Pydantic BaseModel, Starlette exception handlers

---

### Task C1: 创建 ApiResponse 工具模块

**Files:**
- Create: `backend/app/core/response.py`

- [ ] **Step 1: 创建 response.py**

```python
from typing import Any, Optional

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 200
    message: str = "ok"
    data: Any = None


def success(*, data: Any = None, message: str = "ok") -> ApiResponse:
    return ApiResponse(code=200, message=message, data=data)


def error(status_code: int, message: str = "error", data: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ApiResponse(code=status_code, message=message, data=data).model_dump(),
    )
```

Key points:
- `success()` 返回 `ApiResponse` 对象，FastAPI 会自动序列化
- `error()` 返回 `JSONResponse`，因为是错误路径需要直接指定 HTTP status
- `data: Any` 可接受 ORM 模型、list、dict、None 等

- [ ] **Step 2: 验证模块可导入**

```bash
cd backend && python -c "from app.core.response import success, error, ApiResponse; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add backend/app/core/response.py
git commit -m "feat: add ApiResponse model and success/error helpers"
```

---

### Task C2: 全局异常处理器

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: 在 main.py 中添加 HTTPException 和通用异常处理器**

```python
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from app.core.response import error

# 在 lifespan 之后, app 创建之后添加:

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return error(status_code=exc.status_code, message=exc.detail)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return error(status_code=500, message="服务器内部错误")
```

注意：
- `HTTPException` 处理器捕获所有 `raise HTTPException(...)`，自动包装为统一格式
- `Exception` 处理器是兜底，返回 500，不暴露内部错误细节
- `@app.exception_handler` 必须在 `app` 创建之后、但可以在 `include_router` 之前或之后，顺序不影响

- [ ] **Step 2: 验证模块加载**

```bash
cd backend && python -c "from app.main import app; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add backend/app/main.py
git commit -m "feat: add global exception handlers for unified error responses"
```

---

### Task C3: 迁移 endpoints.py

**Files:**
- Modify: `backend/app/api/v1/endpoints.py`

操作原则：每个端点从直接 return 改为 `return success(data=...)`。

**GET 列表类端点（4 个 public + 4 个 admin）：**
原：`return result.scalars().all()`
改：`return success(data=result.scalars().all())`

**CREATE 端点（4 个）：**
原：`return banner` / `return skill` 等
改：`return success(data=refreshed_obj, message="创建成功")`

**UPDATE 端点（4 个）：**
原：`return app` / `return banner` 等
改：`return success(data=refreshed_obj, message="更新成功")`

**DELETE 端点（4 个）：**
原：`return {"ok": True}`
改：`return success(data=None, message="删除成功")`

**特殊端点：**
- `POST /apply`：原 `return {"tracking_code": ...}` → `return success(data={"tracking_code": app.tracking_code}, message="提交成功")`

注意：所有 `raise HTTPException(...)` 不需要改动，Task C2 的异常处理器会自动包裹。

- [ ] **Step 1: 导入 success**

在 endpoints.py 顶部添加：`from app.core.response import success`

- [ ] **Step 2~N: 逐个修改所有端点**

- [ ] **验证语法正确**

```bash
cd backend && python -c "from app.api.v1.endpoints import router; print('OK')"
```

Expected: `OK`

- [ ] **最后提交**

```bash
git add backend/app/api/v1/endpoints.py
git commit -m "refactor: wrap all CMS endpoints with unified ApiResponse"
```

---

### Task C4: 迁移 auth.py 和 health.py

**Files:**
- Modify: `backend/app/api/v1/auth.py`
- Modify: `backend/app/api/v1/health.py`

- [ ] **Step 1: 迁移 auth.py**

导入 `success`，修改 `admin_login` 返回值：
```python
return success(data={"access_token": token, "token_type": "bearer"})
```

`raise HTTPException(401, ...)` 不需要改动 — 由全局异常处理器自动包裹。

- [ ] **Step 2: 迁移 health.py**

导入 `success`，修改 `health_check` 返回值：
```python
return success(data={
    "status": overall,
    "app_name": "南京流苏官网",
    "version": "1.0.0",
    "uptime_seconds": int(time.monotonic() - start_time),
    "database": db_status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
})
```

- [ ] **Step 3: 验证语法**

```bash
cd backend && python -c "
from app.api.v1.auth import router as ar;
from app.api.v1.health import router as hr;
print('auth OK, health OK')
"
```

Expected: `auth OK, health OK`

- [ ] **Step 4: 提交**

```bash
git add backend/app/api/v1/auth.py backend/app/api/v1/health.py
git commit -m "refactor: wrap auth and health endpoints with unified ApiResponse"
```

---

### Task C5: 测试验证

- [ ] **Step 1: 更新测试**

测试需要调整为验证新的响应格式：
- 成功响应：`data = resp.json(); assert data["code"] == 200; assert data["data"]` ...
- 错误响应：`data = resp.json(); assert data["code"] == 401; assert data["message"] == "用户名或密码错误"`

具体修改：

**test_auth.py:**
```python
async def test_admin_login_success(client):
    async with client as ac:
        resp = await ac.post("/api/admin/login", json={
            "username": "admin", "password": "admin123456",
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["message"] == "ok"
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"


async def test_admin_login_wrong_password(client):
    async with client as ac:
        resp = await ac.post("/api/admin/login", json={
            "username": "admin", "password": "wrong",
        })
    assert resp.status_code == 401
    data = resp.json()
    assert data["code"] == 401
    assert data["message"] == "用户名或密码错误"


async def test_admin_login_wrong_username(client):
    async with client as ac:
        resp = await ac.post("/api/admin/login", json={
            "username": "unknown", "password": "admin123456",
        })
    assert resp.status_code == 401
    data = resp.json()
    assert data["code"] == 401
    assert data["message"] == "用户名或密码错误"
```

**test_health.py:**
```python
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
    assert data["code"] == 200
    assert data["message"] == "ok"
    d = data["data"]
    assert d["status"] in ("healthy", "degraded")
    assert "database" in d
    assert "uptime_seconds" in d
    assert "timestamp" in d


@pytest.mark.asyncio
async def test_health_endpoint_database_field(client):
    async with client as ac:
        resp = await ac.get("/api/health")
    data = resp.json()
    assert data["data"]["database"] in ("connected", "disconnected")
```

- [ ] **Step 2: 运行全部测试**

```bash
cd backend && PYTHONPATH=. python3 -m pytest tests/ -v
```

Expected: 6 tests PASS

- [ ] **Step 3: 提交**

```bash
git add backend/tests/test_auth.py backend/tests/test_health.py
git commit -m "test: update tests for unified ApiResponse format"
```

---

### 验证清单

- [ ] `GET /api/health` → `{"code": 200, "message": "ok", "data": {...}}`
- [ ] `POST /api/admin/login` 成功 → `{"code": 200, "message": "ok", "data": {"access_token": "...", "token_type": "bearer"}}`
- [ ] `POST /api/admin/login` 密码错误 → `{"code": 401, "message": "用户名或密码错误", "data": null}`
- [ ] `GET /api/cms/banners` → `{"code": 200, "message": "ok", "data": [...]}`
- [ ] `DELETE /api/admin/banners/1` → `{"code": 200, "message": "删除成功", "data": null}`
- [ ] `PUT /api/admin/banners/999`（不存在）→ `{"code": 404, "message": "Banner 不存在", "data": null}`
- [ ] 6 tests PASS
