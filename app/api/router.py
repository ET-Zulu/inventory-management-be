from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.items import router as items_router
from app.core.config import settings

api_router = APIRouter(prefix=settings.api_v1_prefix)
api_router.include_router(health_router)
api_router.include_router(categories_router)
api_router.include_router(items_router)

