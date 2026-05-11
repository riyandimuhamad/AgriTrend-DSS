import json

from fastapi import APIRouter, Depends

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.genai_service import GenAIService
from app.services.prediction_service import PredictionService

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict_and_generate_insight(
    payload: PredictionRequest,
    prediction_service: PredictionService = Depends(PredictionService),
    genai_service: GenAIService = Depends(GenAIService),
) -> PredictionResponse:
    prediction = prediction_service.predict(payload)
    insight_structured = genai_service.generate_insight(
        {
            "crop_type": payload.crop_type,
            "kode_kabupaten_kota": payload.kode_kabupaten_kota,
            "nama_kabupaten_kota": payload.nama_kabupaten_kota,
            "temperature": payload.temperature,
            "ph": payload.ph,
            "rainfall": payload.rainfall,
            "predicted_yield_ton_per_ha": prediction.predicted_yield_ton_per_ha,
            "market_trend": prediction.market_trend,
            "coordinates": prediction.coordinates.model_dump(),
        },
        mode=payload.insight_mode,
    )
    insight = json.dumps(insight_structured, ensure_ascii=False)
    return PredictionResponse(
        prediction=prediction,
        insight=insight,
        insight_structured=insight_structured,
    )
