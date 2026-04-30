from fastapi import APIRouter

from .endpoints import router as cms_router
from .auth import router as auth_router

api_router = APIRouter()
api_router.include_router(cms_router)
api_router.include_router(auth_router)
