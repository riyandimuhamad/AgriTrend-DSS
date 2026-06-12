from fastapi import APIRouter, Depends

from app.middleware.auth_dependency import get_current_user
from app.schemas.prediction import (
    AdviceResponse,
    PredictionRequest,
    PredictionResponse,
    PredictionHistoryResponse,
)
from app.services.prediction_service import PredictionService

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict(
    payload: PredictionRequest,
    access_token: str = Depends(get_current_user),
    service: PredictionService = Depends(PredictionService),
) -> PredictionResponse:
    return service.predict(
        payload,
        user_id=access_token["id"],
        access_token=access_token["access_token"],
    )


@router.get("/history", response_model=PredictionHistoryResponse)
def get_history(
    current_user: dict = Depends(get_current_user),
    service: PredictionService = Depends(PredictionService),
) -> PredictionHistoryResponse:
    return service.get_history(
        user_id=current_user["id"], access_token=current_user["access_token"]
    )


@router.get("/predict/{prediction_id}/advice", response_model=AdviceResponse)
def get_advice(
    prediction_id: str,
    current_user: dict = Depends(get_current_user),
    service: PredictionService = Depends(PredictionService),
) -> AdviceResponse:
    return service.get_advice(
        prediction_id=prediction_id,
        access_token=current_user["access_token"],
        user_id=current_user["id"],
    )
