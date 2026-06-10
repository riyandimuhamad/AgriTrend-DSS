from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    location: str = Field(min_length=2)
    crop_type: Literal["Padi", "Jagung"]
    land_area: float = Field(gt=0)
    planting_date: date


# --- Structured output schema for Gemini ---
class AIAdviceStructuredOutput(BaseModel):
    analysis: str = Field(description="Analisis supply-demand dan risiko pasar, 2-3 paragraf.")
    recommendation: str = Field(description="Satu tindakan konkret yang bisa dieksekusi petani dalam 30 hari ke depan.")


# --- Response schemas ---
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


class AdviceResponse(BaseModel):
    success: bool = True
    prediction_id: str
    data: AIAdviceStructuredOutput
