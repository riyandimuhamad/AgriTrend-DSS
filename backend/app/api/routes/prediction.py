from fastapi import APIRouter, Depends

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict(
    payload: PredictionRequest,
    service: PredictionService = Depends(PredictionService),
) -> PredictionResponse:
    return service.predict(payload)
