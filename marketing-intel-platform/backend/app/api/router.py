from fastapi import APIRouter

from app.api.routes import anomalies, metrics, upload

api_router = APIRouter()

api_router.include_router(upload.router)
api_router.include_router(metrics.router)
api_router.include_router(anomalies.router)

