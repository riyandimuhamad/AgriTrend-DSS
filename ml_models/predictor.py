"""
predictor.py — Fungsi inference multi-model adaptif (Bebas Dominasi Label)
"""

import joblib
import json
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Load kedua model dan scaler secara global saat startup server backend
_models = {
    "Padi": joblib.load(BASE_DIR / "model_padi.joblib"),
    "Jagung": joblib.load(BASE_DIR / "model_jagung.joblib")
}

_scalers = {
    "Padi": joblib.load(BASE_DIR / "scaler_padi.joblib"),
    "Jagung": joblib.load(BASE_DIR / "scaler_jagung.joblib")
}

with open(BASE_DIR / "feature_columns.json") as f:
    _feature_cols = json.load(f)["feature_columns"]

with open(BASE_DIR / "baseline_yield_multi.json") as f:
    _baseline = json.load(f)


def get_status(yield_pred: float, kabupaten: str, tanaman: str) -> str:
    key = f"{kabupaten}|{tanaman}"
    if key not in _baseline:
        mean = 5.47 if tanaman == "Padi" else 6.02
    else:
        mean = _baseline[key]["mean_yield_ton_ha"]

    ratio = yield_pred / mean
    if ratio >= 1.20: return "PANEN_BERLIMPAH"
    elif ratio >= 0.80: return "NORMAL"
    else: return "GAGAL_PANEN"


def get_confidence(model, feature_vector: np.ndarray) -> tuple[float, float, float]:
    tree_predictions = np.array([tree.predict(feature_vector)[0] for tree in model.estimators_])
    std   = tree_predictions.std()
    mean  = tree_predictions.mean()
    cv = std / mean if mean > 0 else 1
    confidence = max(0, min(100, round((1 - cv) * 100)))
    yield_min = round(max(0, mean - 1.96 * std), 3)
    yield_max = round(mean + 1.96 * std, 3)
    return confidence, yield_min, yield_max


def predict_yield(
    temp_veg_mean: float, temp_rep_mean: float, temp_mat_mean: float,
    rain_veg_total: float, rain_rep_total: float, rain_mat_total: float,
    rain_total_musim: float, humidity_mean_musim: float, radiation_veg: float,
    radiation_rep: float, drought_index_mean: float, n_bulan_data: int,
    ph_h2o: float, nitrogen_cn_kg: float, clay_pct: float, sand_pct: float,
    silt_pct: float, soc_dg_kg: float, cec_mmol_kg: float, bulk_density: float,
    fertility_index: float, whc_proxy: float,
    musim_encoded: int, kesesuaian_encoded: int, ph_status_encoded: int, texture_encoded: int,
    kabupaten: str = "", 
    tanaman: str = "Padi", # Penentu model mana yang di-load backend
    luas_lahan: float = 1.0,
) -> dict:
    
    # Validasi input jenis komoditas
    if tanaman not in ["Padi", "Jagung"]:
        raise ValueError("Komoditas harus berupa 'Padi' atau 'Jagung'")

    # Susun 26 fitur murni alamiah tanpa variabel label komoditas
    feature_dict = {
        "temp_veg_mean":        temp_veg_mean,
        "temp_rep_mean":        temp_rep_mean,
        "temp_mat_mean":        temp_mat_mean,
        "rain_veg_total":       rain_veg_total,
        "rain_rep_total":       rain_rep_total,
        "rain_mat_total":       rain_mat_total,
        "rain_total_musim":     rain_total_musim,
        "humidity_mean_musim":  humidity_mean_musim,
        "radiation_veg":        radiation_veg,
        "radiation_rep":        radiation_rep,
        "drought_index_mean":   drought_index_mean,
        "n_bulan_data":         n_bulan_data,
        "ph_h2o":               ph_h2o,
        "nitrogen_cn_kg":       nitrogen_cn_kg,
        "clay_pct":             clay_pct,
        "sand_pct":             sand_pct,
        "silt_pct":             silt_pct,
        "soc_dg_kg":            soc_dg_kg,
        "cec_mmol_kg":          cec_mmol_kg,
        "bulk_density":         bulk_density,
        "fertility_index":      fertility_index,
        "whc_proxy":            whc_proxy,
        "musim_encoded":        musim_encoded,
        "kesesuaian_encoded":   kesesuaian_encoded,
        "ph_status_encoded":    ph_status_encoded,
        "texture_encoded":      texture_encoded,
    }

    # Ambil model & scaler yang sesuai secara dinamis
    model = _models[tanaman]
    scaler = _scalers[tanaman]

    X = pd.DataFrame([feature_dict])[_feature_cols]
    X_scaled = scaler.transform(X)

    # Jalankan Prediksi
    yield_per_ha = round(float(model.predict(X_scaled)[0]), 3)
    yield_total  = round(yield_per_ha * luas_lahan, 3)
    
    confidence, yield_min, yield_max = get_confidence(model, X_scaled)
    status = get_status(yield_per_ha, kabupaten, tanaman)

    return {
        "yield_per_ha": yield_per_ha,
        "yield_total":  yield_total,
        "unit":         "ton",
        "confidence":   confidence,
        "yield_min":    yield_min,
        "yield_max":    yield_max,
        "status":       status,
        "tanaman":      tanaman,
    }