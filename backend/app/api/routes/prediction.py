from fastapi import APIRouter, Depends

from app.middleware.auth_dependency import get_current_user
from app.schemas.prediction import AdviceResponse, PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict(
    payload: PredictionRequest,
    current_user: dict = Depends(get_current_user),
    service: PredictionService = Depends(PredictionService),
) -> PredictionResponse:
    return service.predict(payload, user_id=current_user["id"])


@router.get("/predict/{prediction_id}/advice", response_model=AdviceResponse)
def get_advice(
    prediction_id: str,
    current_user: dict = Depends(get_current_user),
    service: PredictionService = Depends(PredictionService),
) -> AdviceResponse:
    return service.get_advice(prediction_id, user_id=current_user["id"])
