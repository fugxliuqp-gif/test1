from fastapi import APIRouter

from .endpoints import router as cms_router

api_router = APIRouter()
api_router.include_router(cms_router)
