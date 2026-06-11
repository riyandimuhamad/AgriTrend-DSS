import uuid
from datetime import datetime, timezone

from fastapi import HTTPException

from app.core.supabase_client import get_authed_client
from app.schemas.prediction import (
    AdviceResponse,
    AIAdviceStructuredOutput,
    PredictionMetrics,
    PredictionRequest,
    PredictionResponse,
)
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

    def predict(self, payload: PredictionRequest, user_id: str, access_token: str) -> PredictionResponse:
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

        prediction_id = str(uuid.uuid4())
        status = _STATUS_MAP.get(ml["status"], "WARNING")
        now = datetime.now(timezone.utc)
        db = get_authed_client(access_token)

        db.table("predictions").insert({
            "id": prediction_id,
            "user_id": user_id,
            "crop_type": payload.crop_type,
            "region": coords["region"],
            "yield_per_ha": ml["yield_per_ha"],
            "yield_total": ml["yield_total"],
            "confidence": ml["confidence"],
            "yield_min": ml["yield_min"],
            "yield_max": ml["yield_max"],
            "status": status,
            "unit": "ton",
            "created_at": now.isoformat(),
        }).execute()

        return PredictionResponse(
            data=PredictionMetrics(
                prediction_id=prediction_id,
                yield_per_ha=ml["yield_per_ha"],
                yield_total=ml["yield_total"],
                unit="ton",
                confidence=ml["confidence"],
                yield_min=ml["yield_min"],
                yield_max=ml["yield_max"],
                status=status,
                crop_type=payload.crop_type,
                region=coords["region"],
                timestamp=now,
            )
        )

    def get_advice(self, prediction_id: str, access_token: str) -> AdviceResponse:
        db = get_authed_client(access_token)
        result = (
            db.table("predictions")
            .select("crop_type, region, yield_per_ha, status")
            .eq("id", prediction_id)
            .maybe_single()
            .execute()
        )

        if result.data is None:
            raise HTTPException(
                status_code=404,
                detail="Prediction ID tidak ditemukan atau sudah kedaluwarsa.",
            )

        row = result.data
        advice: AIAdviceStructuredOutput = self._genai.generate_advice(
            crop_type=row["crop_type"],
            region=row["region"],
            yield_per_ha=row["yield_per_ha"],
            status=row["status"],
        )

        return AdviceResponse(prediction_id=prediction_id, data=advice)
