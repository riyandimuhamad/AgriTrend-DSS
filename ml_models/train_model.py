import pandas as pd
import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import r2_score, mean_absolute_error

# 1. Load Dataset v2
DATA_PATH = "dataset_ml_v2.csv"
print("[INFO] Membaca dataset baru...")
df = pd.read_csv(DATA_PATH)

# 2. FEATURE_COLS Baru: Hapus 'tanaman_encoded' agar model fokus ke alam & tanah
FEATURE_COLS_BASE = [
    "temp_veg_mean", "temp_rep_mean", "temp_mat_mean",
    "rain_veg_total", "rain_rep_total", "rain_mat_total", "rain_total_musim",
    "humidity_mean_musim", "radiation_veg", "radiation_rep", "drought_index_mean",
    "n_bulan_data", "ph_h2o", "nitrogen_cn_kg", "clay_pct", "sand_pct", "silt_pct",
    "soc_dg_kg", "cec_mmol_kg", "bulk_density", "fertility_index", "whc_proxy",
    "musim_encoded", "kesesuaian_encoded", "ph_status_encoded", "texture_encoded"
]
TARGET_COL = "yield_ton_ha"

# Imputasi data kosong global dengan median
for col in FEATURE_COLS_BASE:
    if df[col].isnull().sum() > 0:
        df[col] = df[col].fillna(df[col].median())

print("\n" + "="*45)
print("     TRAINING MULTI-MODEL PER TANAMAN")
print("="*45)

# 3. Looping Pelatihan Terpisah per Jenis Tanaman
for tanaman in ["Padi", "Jagung"]:
    print(f"\n[PROCESS] Melatih Model Spesifik untuk: {tanaman}...")
    
    # Filter data berdasarkan komoditas
    df_crop = df[df["tanaman"] == tanaman].copy()
    
    X = df_crop[FEATURE_COLS_BASE]
    y = df_crop[TARGET_COL]
    
    # Split Data per Komoditas (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Normalisasi Fitur Mandiri per Komoditas
    scaler = MinMaxScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)
    
    # Latih Random Forest dengan Regularisasi Ketat
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_sc, y_train)
    
    # Evaluasi Performa Jujur
    y_pred = model.predict(X_test_sc)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    print(f"  -> Hasil Evaluasi Model {tanaman}:")
    print(f"     Akurasi (R² Score) : {r2 * 100:.2f}%")
    print(f"     MAE                : {mae:.4f} ton/ha")
    
    # Export Artefak Spesifik per Tanaman
    crop_name = tanaman.lower()
    joblib.dump(model, f"model_{crop_name}.joblib")
    joblib.dump(scaler, f"scaler_{crop_name}.joblib")

# Simpan daftar kolom fitur (tanpa tanaman_encoded) untuk panduan backend
with open("feature_columns.json", "w") as f:
    json.dump({"feature_columns": FEATURE_COLS_BASE}, f, indent=4)

# Buat baseline_yield_multi.json untuk threshold batas panen kabupaten
baseline_data = {}
grouped = df.groupby(['nama_kabupaten', 'tanaman'])['yield_ton_ha'].mean().reset_index()
for _, row in grouped.iterrows():
    key = f"{row['nama_kabupaten']}|{row['tanaman']}"
    baseline_data[key] = {"mean_yield_ton_ha": round(float(row['yield_ton_ha']), 2)}

with open("baseline_yield_multi.json", "w") as f:
    json.dump(baseline_data, f, indent=4)

print("\n" + "="*45)
print("[SUCCESS] Dua model jujur & independen sukses diekspor!")
print("="*45)