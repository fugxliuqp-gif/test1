import bcrypt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.core.response import success
from app.core.security import create_access_token

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/admin/login", tags=["Auth"], summary="管理员登录")
async def admin_login(req: LoginRequest):
    if req.username != settings.ADMIN_USERNAME:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not bcrypt.checkpw(
        req.password.encode("utf-8"),
        settings.ADMIN_PASSWORD_HASH.encode("utf-8"),
    ):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token({"sub": req.username, "role": "admin"})
    return success(data={"access_token": token, "token_type": "bearer"})
