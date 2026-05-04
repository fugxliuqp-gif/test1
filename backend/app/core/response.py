from typing import Any

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
