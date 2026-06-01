from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import httpx

# load predictor from ml_models
_ML_DIR = Path(__file__).resolve().parents[3] / "ml_models"
_DATA_DIR = Path(__file__).resolve().parents[1] / "data"

if str(_ML_DIR) not in sys.path:
    sys.path.insert(0, str(_ML_DIR))

from predictor import predict_yield

# supported crops
SUPPORTED_CROPS = {"padi": "Padi", "jagung": "Jagung"}

# soil data per kabupaten
with (_DATA_DIR / "soil_data.json").open(encoding="utf-8") as _f:
    _SOIL: dict = json.load(_f)


def _get_soil(region: str) -> dict:
    return _SOIL.get(region, _SOIL["_default"])


# encoding helpers
def _musim_encoded(d: date) -> int:
    return 1 if d.month in (10, 11, 12, 1, 2, 3) else 0


def _ph_status_encoded(ph: float) -> int:
    return 1 if ph <= 5.4 else 2


def _texture_encoded(clay: float) -> int:
    return 1 if clay >= 40.0 else 3


def _kesesuaian_encoded(fertility: float) -> int:
    return 1 if fertility < 7.0 else 2


# weather fetch (Open-Meteo archive)
def _fetch_weather_phases(lat: float, lon: float, planting_date: date) -> dict:
    phases = {
        "veg": (planting_date, planting_date + timedelta(days=29)),
        "rep": (planting_date + timedelta(days=30), planting_date + timedelta(days=59)),
        "mat": (planting_date + timedelta(days=60), planting_date + timedelta(days=89)),
    }
    result: dict = {}
    totals = {"rain": 0.0, "hum": 0.0, "rad": 0.0}

    for phase, (start, end) in phases.items():
        try:
            resp = httpx.get(
                "https://archive-api.open-meteo.com/v1/archive",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "start_date": str(start),
                    "end_date": str(end),
                    "daily": "temperature_2m_mean,precipitation_sum,relative_humidity_2m_mean,shortwave_radiation_sum",
                    "timezone": "Asia/Jakarta",
                },
                timeout=15,
            )
            resp.raise_for_status()
            daily = resp.json().get("daily", {})

            def _mean(vals: list) -> float:
                v = [x for x in (vals or []) if x is not None]
                return sum(v) / len(v) if v else 0.0

            temp = _mean(daily.get("temperature_2m_mean", []))
            rain = sum(
                x for x in (daily.get("precipitation_sum") or []) if x is not None
            )
            hum = _mean(daily.get("relative_humidity_2m_mean", []))
            rad = _mean(daily.get("shortwave_radiation_sum", []))
        except Exception:
            temp, rain, hum, rad = 27.0, 200.0, 80.0, 18.0

        result[f"temp_{phase}_mean"] = round(temp, 2)
        result[f"rain_{phase}_total"] = round(rain, 2)
        totals["rain"] += rain
        totals["hum"] += hum
        totals["rad"] += rad

    result["rain_total_musim"] = round(totals["rain"], 2)
    result["humidity_mean_musim"] = round(totals["hum"] / 3, 2)
    result["radiation_veg"] = round(totals["rad"] / 3, 2)
    result["radiation_rep"] = round(totals["rad"] / 3, 2)
    result["drought_index_mean"] = round(min(1.0, totals["rain"] / 600.0), 3)
    result["n_bulan_data"] = 3
    return result


# public API
def run_prediction(
    location: str,
    crop_type: str,
    region: str,
    lat: float,
    lon: float,
    planting_date: date,
    land_area: float,
) -> dict:
    canonical = SUPPORTED_CROPS.get(crop_type.lower().strip())
    if canonical is None:
        supported = ", ".join(SUPPORTED_CROPS.values())
        raise ValueError(
            f"Komoditas '{crop_type}' tidak didukung. Pilihan: {supported}."
        )

    soil = _get_soil(region)
    weather = _fetch_weather_phases(lat, lon, planting_date)
    ph, clay, fertility = soil["ph_h2o"], soil["clay_pct"], soil["fertility_index"]

    return predict_yield(
        **weather,
        ph_h2o=ph,
        nitrogen_cn_kg=soil["nitrogen_cn_kg"],
        clay_pct=clay,
        sand_pct=soil["sand_pct"],
        silt_pct=soil["silt_pct"],
        soc_dg_kg=soil["soc_dg_kg"],
        cec_mmol_kg=soil["cec_mmol_kg"],
        bulk_density=soil["bulk_density"],
        fertility_index=fertility,
        whc_proxy=soil["whc_proxy"],
        musim_encoded=_musim_encoded(planting_date),
        kesesuaian_encoded=_kesesuaian_encoded(fertility),
        ph_status_encoded=_ph_status_encoded(ph),
        texture_encoded=_texture_encoded(clay),
        kabupaten=region,
        tanaman=canonical,
        luas_lahan=land_area,
    )
