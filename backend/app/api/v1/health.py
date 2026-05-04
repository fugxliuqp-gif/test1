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
