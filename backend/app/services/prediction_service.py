from datetime import datetime, timezone

from fastapi import HTTPException

from app.schemas.prediction import PredictionData, PredictionRequest, PredictionResponse
from app.services.genai_service import GenAIService
from app.services.location_service import LocationService
from app.services.ml_service import run_prediction

_STATUS_MAP = {
    "PANEN_BERLIMPAH": "NORMAL",
    "NORMAL": "NORMAL",
    "GAGAL_PANEN": "CRITICAL",
}


class PredictionService:
    def __init__(self) -> None:
        self._location = LocationService()
        self._genai = GenAIService()

    def predict(self, payload: PredictionRequest) -> PredictionResponse:
        coords = self._location.resolve_by_name(payload.location)

        try:
            ml = run_prediction(
                location=payload.location,
                crop_type=payload.crop_type,
                region=coords["region"],
                lat=coords["latitude"],
                lon=coords["longitude"],
                planting_date=payload.planting_date,
                land_area=payload.land_area,
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception:
            raise HTTPException(
                status_code=503,
                detail="Layanan prediksi sedang tidak tersedia. Coba beberapa saat lagi.",
            )

        status = _STATUS_MAP.get(ml["status"], "WARNING")
        ai_advice = self._genai.generate_advice(
            crop_type=payload.crop_type,
            region=coords["region"],
            yield_per_ha=ml["yield_per_ha"],
            status=status,
        )

        return PredictionResponse(
            data=PredictionData(
                yield_per_ha=ml["yield_per_ha"],
                yield_total=ml["yield_total"],
                unit="ton",
                confidence=ml["confidence"],
                yield_min=ml["yield_min"],
                yield_max=ml["yield_max"],
                status=status,
                crop_type=payload.crop_type,
                region=coords["region"],
                ai_advice=ai_advice,
                timestamp=datetime.now(timezone.utc),
            )
        )
