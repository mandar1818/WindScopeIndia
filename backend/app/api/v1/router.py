from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.india import router as india_router

api_v1_router = APIRouter()

# Core service health
api_v1_router.include_router(health_router)

# India Renewable Energy Intelligence Platform APIs
api_v1_router.include_router(india_router, prefix="/india", tags=["India Platform"])
# Also expose endpoints without /india prefix for canonical root access
api_v1_router.include_router(india_router, tags=["India Platform Root"])


