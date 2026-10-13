from fastapi import APIRouter
from backend.api import health, evals, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(evals.router, prefix="/api", tags=["evals"])
api_router.include_router(ui.router, tags=["ui"])
