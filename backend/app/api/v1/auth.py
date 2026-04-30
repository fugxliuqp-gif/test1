from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.security import create_access_token

router = APIRouter()

# 默认管理员账户（生产环境应通过环境变量配置）
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123456"


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/admin/login")
async def admin_login(req: LoginRequest):
    if req.username != ADMIN_USERNAME or req.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"sub": req.username, "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}
