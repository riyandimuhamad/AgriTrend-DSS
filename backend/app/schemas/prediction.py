from typing import Literal

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    nitrogen: float = Field(ge=0)
    phosphorus: float = Field(ge=0)
    potassium: float = Field(ge=0)
    temperature: float
    humidity: float = Field(ge=0, le=100)
    ph: float = Field(ge=0, le=14)
    rainfall: float = Field(ge=0)
    crop_type: str = Field(min_length=2)
    kode_kabupaten_kota: int | None = None
    nama_kabupaten_kota: str | None = None
    insight_mode: Literal["market_only", "agronomy_plus_market"] = "market_only"


class Coordinates(BaseModel):
    latitude: float
    longitude: float
    region: str


class PredictionResult(BaseModel):
    predicted_yield_ton_per_ha: float
    market_trend: str
    coordinates: Coordinates


class PredictionResponse(BaseModel):
    prediction: PredictionResult
    insight: str
    insight_structured: dict
