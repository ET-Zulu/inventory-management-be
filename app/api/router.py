from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.core.config import settings
from app.api.v1.endpoints import vendors
from app.api.v1.endpoints import imports


api_router = APIRouter(prefix=settings.api_v1_prefix)
api_router.include_router(health_router)
api_router.include_router(vendors.router)
api_router.include_router(imports.router)

