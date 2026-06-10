from fastapi import APIRouter, Depends

from app.schemas.prediction import AdviceResponse, PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict(
    payload: PredictionRequest,
    service: PredictionService = Depends(PredictionService),
) -> PredictionResponse:
    return service.predict(payload)


@router.get("/predict/{prediction_id}/advice", response_model=AdviceResponse)
def get_advice(
    prediction_id: str,
    service: PredictionService = Depends(PredictionService),
) -> AdviceResponse:
    return service.get_advice(prediction_id)
