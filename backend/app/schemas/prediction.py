from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    location: str = Field(min_length=2)
    crop_type: Literal["Padi", "Jagung"]
    land_area: float = Field(gt=0)
    planting_date: date


class AIAdviceStructuredOutput(BaseModel):
    analysis: str = Field(
        description="Analisis mendalam mengenai supply-demand, dinamika pasar, dan risiko penjualan berdasarkan hasil prediksi volume panen. Ditulis dalam 2-3 paragraf pendek menggunakan Bahasa Indonesia."
    )
    recommendation: str = Field(
        description="Satu tindakan bisnis konkret, spesifik, dan sangat realistis yang harus dilakukan petani dalam 30 hari ke depan untuk mengamankan keuntungan atau memitigasi kerugian."
    )


class PredictionMetrics(BaseModel):
    prediction_id: str
    yield_per_ha: float
    yield_total: float
    unit: str = "ton"
    confidence: int
    yield_min: float
    yield_max: float
    status: str
    crop_type: str
    region: str
    timestamp: datetime


class PredictionResponse(BaseModel):
    success: bool = True
    data: PredictionMetrics


class PredictionHistoryItem(BaseModel):
    prediction_id: str
    crop_type: str
    region: str
    yield_per_ha: float
    yield_total: float
    unit: str
    confidence: int
    yield_min: float
    yield_max: float
    status: str
    timestamp: datetime
    advice: AIAdviceStructuredOutput | None = None


class PredictionHistoryResponse(BaseModel):
    success: bool = True
    data: list[PredictionHistoryItem]


class AdviceResponse(BaseModel):
    success: bool = True
    prediction_id: str
    data: AIAdviceStructuredOutput
