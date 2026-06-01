from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    location: str = Field(min_length=2)
    crop_type: Literal["Padi", "Jagung"]
    land_area: float = Field(gt=0)
    planting_date: date


class PredictionData(BaseModel):
    yield_per_ha: float
    yield_total: float
    unit: str = "ton"

    confidence: int
    yield_min: float
    yield_max: float

    status: str

    crop_type: str
    region: str

    ai_advice: str
    timestamp: datetime


class PredictionResponse(BaseModel):
    success: bool = True
    data: PredictionData
