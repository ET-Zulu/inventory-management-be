from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.core.config import settings
from app.api.v1.endpoints.transactions import router as transaction_router

api_router = APIRouter(prefix=settings.api_v1_prefix)
api_router.include_router(health_router)

api_router.include_router(transaction_router, prefix="/transactions", tags=["Transactions"])