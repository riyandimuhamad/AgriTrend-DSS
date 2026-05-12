from app.schemas.prediction import PredictionRequest, PredictionResult
from app.services.location_service import LocationService


# Prediction service for predicting the yield of the crop
class PredictionService:
    def __init__(self) -> None:
        self.location_service = LocationService()

    def predict(self, payload: PredictionRequest) -> PredictionResult:

        nutrient_score = (payload.nitrogen + payload.phosphorus + payload.potassium) / 3
        climate_score = (payload.temperature * 0.3) + (payload.humidity * 0.2) + (payload.rainfall * 0.1)
        acidity_penalty = abs(payload.ph - 6.5) * 1.5
        raw_yield = (nutrient_score * 0.04) + (climate_score * 0.02) - acidity_penalty

        predicted_yield = round(max(1.2, min(raw_yield, 9.5)), 2)
        if predicted_yield >= 6.5:
            market_trend = "potensi naik"
        elif predicted_yield >= 4.0:
            market_trend = "stabil"
        else:
            market_trend = "perlu mitigasi distribusi"

        coordinates = self.location_service.resolve_coordinates(
            kode_kabupaten_kota=payload.kode_kabupaten_kota,
            nama_kabupaten_kota=payload.nama_kabupaten_kota,
        )

        return PredictionResult(
            predicted_yield_ton_per_ha=predicted_yield,
            market_trend=market_trend,
            coordinates=coordinates,
        )
