"""
API Gateway — v1 Router
Aggregates all v1 route modules.
"""

from fastapi import APIRouter

from app.api.v1.transactions import router as transactions_router
from app.api.v1.users import router as users_router
from app.api.v1.frauds import router as frauds_router
from app.api.v1.health import router as health_router
from app.api.v1.websocket import router as websocket_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router, tags=["Health"])
api_v1_router.include_router(transactions_router, prefix="/transactions", tags=["Transactions"])
api_v1_router.include_router(users_router, prefix="/users", tags=["Users"])
api_v1_router.include_router(frauds_router, prefix="/frauds", tags=["Fraud Alerts"])
api_v1_router.include_router(websocket_router, tags=["WebSocket"])
