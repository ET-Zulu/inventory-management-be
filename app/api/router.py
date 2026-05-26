from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router

from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.items import router as items_router

from app.core.config import settings
from app.api.v1.endpoints.transactions import router as transaction_router
from app.api.v1.endpoints.dashboard import router as dashboard_router

from app.api.v1.endpoints import vendors
from app.api.v1.endpoints import imports



api_router = APIRouter(prefix=settings.api_v1_prefix)
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(health_router)
api_router.include_router(categories_router)
api_router.include_router(items_router)
api_router.include_router(vendors.router)
api_router.include_router(imports.router)

api_router.include_router(transaction_router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])