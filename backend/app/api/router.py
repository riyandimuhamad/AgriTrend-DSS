from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.prediction import router as prediction_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(prediction_router, prefix="/ml", tags=["Prediction"])
