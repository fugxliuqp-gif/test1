# Phase A: 安全加固实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 P0 安全漏洞：密钥/密码硬编码、密码明文比较、CORS 全开

**Architecture:** 将硬编码配置迁移到环境变量，密码验证改用 bcrypt 哈希比较，CORS origins 改为可配置

**Tech Stack:** FastAPI, Pydantic Settings, python-jose, passlib[bcrypt], bcrypt

---

### Task 0: 创建 .env 和 .env.example 文件

**Files:**
- Create: `backend/.env`（不提交 Git）
- Create: `backend/.env.example`（提交 Git，占位值）

- [ ] **Step 1: 生成安全密钥并写入 .env**

```bash
cd backend
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" > .env
```

再追加到 `.env`：
```bash
cat >> .env << 'EOL'
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=
CORS_ORIGINS=["http://localhost:5174","http://localhost:8000"]
EOL
```

- [ ] **Step 2: 生成默认管理员密码的 bcrypt 哈希并填入 .env**

```bash
cd backend
python -c "
import bcrypt
pw = bcrypt.hashpw(b'admin123456', bcrypt.gensalt())
print('ADMIN_PASSWORD_HASH=' + pw.decode())
" >> .env
```

Expected: `.env` 文件包含 SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD_HASH, CORS_ORIGINS

- [ ] **Step 3: 创建 .env.example（占位值，可提交 Git）**

```bash
cat > backend/.env.example << 'EOL'
SECRET_KEY=change-me-in-production
ADMIN_USERNAME=admin
# 生成方法: python -c "import bcrypt; print(bcrypt.hashpw(b'your-password', bcrypt.gensalt()).decode())"
ADMIN_PASSWORD_HASH=
CORS_ORIGINS=["http://localhost:5174","http://localhost:8000"]
EOL
```

- [ ] **Step 4: 提交 .env.example（.env 已在 .gitignore 中，不会被提交）**

```bash
git add backend/.env.example
git commit -m "chore: add .env.example with placeholder values for local development"
```

⚠️ **重要：** `.env` 文件包含真实密钥，永远不要提交到 Git。`.gitignore` 已包含 `.env`。

---

### Task 1: 更新 Config 从环境变量读取安全配置

**Files:**
- Modify: `backend/app/core/config.py`

- [ ] **Step 1: 更新 config.py，新增安全配置字段**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "南京流苏官网"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/cms.db"
    SECRET_KEY: str = ""  # 必须从环境变量设置，无默认值
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = ""  # bcrypt 哈希，必须从环境变量设置
    CORS_ORIGINS: list[str] = ["http://localhost:5174", "http://localhost:8000"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
```

注意：
- `SECRET_KEY` 和 `ADMIN_PASSWORD_HASH` 默认空字符串，启动时校验
- `CORS_ORIGINS` 从环境变量读取 JSON 数组

- [ ] **Step 2: 添加启动时校验**

在 `config.py` 末尾追加验证：

```python
# 启动时校验安全配置
if not settings.SECRET_KEY:
    raise RuntimeError("SECRET_KEY 未配置！请在 .env 或环境变量中设置。")
if not settings.ADMIN_PASSWORD_HASH:
    raise RuntimeError("ADMIN_PASSWORD_HASH 未配置！请在 .env 或环境变量中设置。")
```

- [ ] **Step 3: 运行验证**

```bash
cd backend && python -c "from app.core.config import settings; print('SECRET_KEY:', settings.SECRET_KEY[:10]+'...'); print('ADMIN_PASSWORD_HASH:', settings.ADMIN_PASSWORD_HASH[:20]+'...'); print('CORS_ORIGINS:', settings.CORS_ORIGINS)"
```

Expected: 打印配置信息，无 RuntimeError

- [ ] **Step 4: 提交**

```bash
git add backend/app/core/config.py
git commit -m "fix: move secret key and admin credentials to env vars"
```

---

### Task 2: 密码验证改用 bcrypt

**Files:**
- Modify: `backend/app/api/v1/auth.py`

- [ ] **Step 1: 更新 auth.py，使用 bcrypt 哈希比对**

```python
import bcrypt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/admin/login")
async def admin_login(req: LoginRequest):
    if req.username != settings.ADMIN_USERNAME:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not bcrypt.checkpw(
        req.password.encode("utf-8"),
        settings.ADMIN_PASSWORD_HASH.encode("utf-8"),
    ):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    from app.core.security import create_access_token
    token = create_access_token({"sub": req.username, "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}
```

关键改动：
- 移除硬编码的 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD`
- 改为从 `settings.ADMIN_USERNAME` 和 `settings.ADMIN_PASSWORD_HASH` 读取
- 使用 `bcrypt.checkpw()` 进行安全哈希比对

- [ ] **Step 2: 验证后端能正常启动**

```bash
cd backend && python -c "from app.api.v1.auth import router; print('auth router loaded OK')"
```

Expected: `auth router loaded OK`

- [ ] **Step 3: 提交**

```bash
git add backend/app/api/v1/auth.py
git commit -m "fix: use bcrypt for admin password verification"
```

---

### Task 3: CORS 可配置

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: 更新 main.py 从 settings 读取 CORS origins**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(title=settings.APP_NAME)

# CORS — 从环境变量配置
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

- [ ] **Step 2: 验证启动**

```bash
cd backend && python -c "from app.main import app; print('main.py loaded OK')"
```

Expected: `main.py loaded OK`

- [ ] **Step 3: 提交**

```bash
git add backend/app/main.py
git commit -m "fix: make CORS origins configurable via env"
```

---

### Task 4: 测试验证

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: 创建测试目录和 auth 测试**

```python
# tests/__init__.py — 空文件
```

```python
# tests/test_auth.py
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
```

- [ ] **Step 2: 确认 httpx/pytest-asyncio 已安装**

```bash
cd backend && pip install httpx pytest-asyncio
```

- [ ] **Step 3: 运行测试**

```bash
cd backend && python -m pytest tests/ -v
```

Expected: 3 tests PASS

- [ ] **Step 4: 提交**

```bash
git add backend/tests/
git commit -m "test: add auth tests for admin login"
```

---

### 验证清单

- [ ] 无 `.env` 文件时 `SECRET_KEY` 为空，启动报错提示配置
- [ ] 无 `.env` 文件时 `ADMIN_PASSWORD_HASH` 为空，启动报错提示配置
- [ ] 使用正确密码登录返回 200 + access_token
- [ ] 使用错误密码登录返回 401
- [ ] 使用错误用户名登录返回 401
- [ ] CORS origins 可通过环境变量配置
- [ ] `.env` 中 SECRET_KEY 是随机生成的 token_urlsafe(32)
