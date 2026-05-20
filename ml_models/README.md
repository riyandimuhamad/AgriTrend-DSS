# AgriTrend-DSS: Machine Learning Model Artifacts & Technical Documentation

Repositori ini menyimpan artefak model prediktif (Machine Learning) dan modul kecerdasan buatan buatan (Generative AI) yang berfungsi sebagai inti pengolah data pada sistem Pendukung Keputusan (Decision Support System) AgriTrend-DSS untuk wilayah Jawa Barat, khususnya Kabupaten Garut.

---

## Performa Model

Model prediktif dikembangkan menggunakan algoritma Random Forest Regressor yang dilatih menggunakan dataset spesifik regional Jawa Barat dengan total 20.000 baris data pasca-proses pembersihan data.

* **R-squared (R2) Score**: 96.80%
* **Mean Absolute Error (MAE)**: 0.2451 ton/hektar

---

## Struktur Berkas Utama

1. **`ml_models/agri_trend_rf_model.joblib`**: Objek biner model Random Forest Regressor seberat 43 MB yang sudah siap digunakan untuk melakukan prediksi produktivitas hasil panen.
2. **`gemini_integration.py`**: Modul integrasi serverless cloud menggunakan SDK Google GenAI (model gemini-2.5-flash) untuk mengonversi hasil prediksi model menjadi narasi analisis wawasan pasar formal.

---

## Spesifikasi Urutan Fitur Input

Aplikasi backend (Streamlit) wajib mengirimkan matriks data dengan urutan fitur yang presisi sebagai berikut sebelum melakukan eksekusi fungsi prediksi:

1. Temperature_C
2. Humidity_pct
3. pH
4. Rainfall_mm
5. N
6. P
7. K
8. Region_enc
9. Crop_enc

---

## Contoh Integrasi Backend (Streamlit)

Berikut adalah implementasi kode standar untuk memuat model, melakukan prediksi, dan menghasilkan narasi wawasan pasar menggunakan fungsi integrasi yang telah disinkronisasikan:

```python
import joblib
import pandas as pd
from gemini_integration import generate_market_analysis

# 1. Memuat model Random Forest regional Jawa Barat
model = joblib.load('ml_models/agri_trend_rf_model.joblib')

# 2. Representasi data input dari user interface Streamlit (Urutan wajib sesuai)
data_input = pd.DataFrame([[27.5, 80.0, 6.5, 200.0, 90, 42, 43, 2, 1]], 
                           columns=['Temperature_C', 'Humidity_pct', 'pH', 'Rainfall_mm', 'N', 'P', 'K', 'Region_enc', 'Crop_enc'])

# 3. Melakukan eksekusi prediksi produktivitas
prediksi_yield = model.predict(data_input)[0]

# 4. Menghasilkan narasi analisis strategi pasar via Gemini API
# Komoditas dan lokasi disesuaikan berdasarkan nilai encoding pada input
analisis_pasar = generate_market_analysis(
    prediksi_yield_rf=prediksi_yield, 
    tanaman_aktif="Padi", 
    lokasi_panen="Kabupaten Garut"
)

print(f"Hasil Prediksi: {prediksi_yield:.2f} ton/ha")
print("Analisis Pasar:\n", analisis_pasar)