import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import health
from app.api.v1.router import api_router
from app.core.response import error


@asynccontextmanager
async def lifespan(application: FastAPI):
    health.set_start_time(time.monotonic())
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="南京流苏智慧信息技术有限公司官网后端 API。提供 CMS 内容管理、入驻申请审核、管理员认证等功能。",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return error(status_code=exc.status_code, message=exc.detail)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return error(status_code=500, message="服务器内部错误")


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
