# AgriTrend-DSS — Backend

Backend API untuk sistem pendukung keputusan pertanian Jawa Barat. Memprediksi hasil panen berdasarkan lokasi, komoditas, dan tanggal tanam menggunakan model Random Forest + analisis pasar via Gemini AI.

## Tech Stack

- **FastAPI** — REST API framework
- **Supabase** — Auth & database
- **scikit-learn / joblib** — ML model inference
- **Google Gemini** — AI market advice
- **Open-Meteo** — Weather data (free, no API key)
- **uv** — Package manager

---

## Prasyarat

### 1. Install uv

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

> Dokumentasi lengkap: https://docs.astral.sh/uv/getting-started/installation/

### 2. Python 3.12+

---

uv akan otomatis mengelola versi Python yang dibutuhkan.

## Instalasi

```bash
# 1. Clone repo
git clone https://github.com/riyandimuhamad/AgriTrend-DSS.git
cd AgriTrend-DSS/backend

# 2. Install semua dependencies
uv sync

# 3. Salin dan isi file environment
cp .env.example .env
```

### Isi `.env`

| Key               | Keterangan                                                                         |
| ----------------- | ---------------------------------------------------------------------------------- |
| `SUPABASE_URL`    | URL project Supabase                                                               |
| `SUPABASE_KEY`    | Anon/service key Supabase                                                          |
| `GEMINI_API_KEY`  | API key Google Gemini ([dapatkan di sini](https://aistudio.google.com/app/apikey)) |
| `GEMINI_MODEL`    | Default: `gemini-2.5-flash`                                                        |
| `ALLOWED_ORIGINS` | Origin frontend, pisahkan dengan koma                                              |

---

### Generate ML Model

Model tidak disertakan di repo. Generate dari dataset yang tersedia:

```bash
cd ../ml_models
python train_model.py
```

Akan menghasilkan: `model_padi.joblib`, `model_jagung.joblib`, `scaler_padi.joblib`, `scaler_jagung.joblib`

## Menjalankan Server

```bash
uv run main.py
```

Server berjalan di `http://localhost:8000`

## Endpoints

### Auth

| Method | Endpoint                | Deskripsi                    | Auth         |
| ------ | ----------------------- | ---------------------------- | ------------ |
| `POST` | `/api/v1/auth/register` | Daftar akun baru             | —            |
| `POST` | `/api/v1/auth/login`    | Login, mendapat access token | —            |
| `GET`  | `/api/v1/auth/me`       | Info user yang sedang login  | Bearer token |

### Prediksi

| Method | Endpoint             | Deskripsi            | Auth |
| ------ | -------------------- | -------------------- | ---- |
| `POST` | `/api/v1/ml/predict` | Prediksi hasil panen | —    |

### Lainnya

| Method | Endpoint  | Deskripsi    |
| ------ | --------- | ------------ |
| `GET`  | `/health` | Health check |
| `GET`  | `/docs`   | Swagger UI   |

---

## Contoh Request & Response

### `POST /api/v1/ml/predict`

**Request:**

```json
{
  "location": "Subang",
  "crop_type": "Padi",
  "land_area": 2.0,
  "planting_date": "2025-10-01"
}
```

> `crop_type` hanya menerima: `"Padi"` atau `"Jagung"`

**Response:**

```json
{
  "success": true,
  "data": {
    "yield_per_ha": 5.87,
    "yield_total": 11.74,
    "unit": "ton",
    "confidence": 95,
    "yield_min": 5.62,
    "yield_max": 6.12,
    "status": "NORMAL",
    "crop_type": "Padi",
    "region": "Kab. Subang",
    "ai_advice": "Hasil panen diprediksi normal musim ini. Pertimbangkan menjual sebagian saat harga stabil...",
    "timestamp": "2025-10-01T08:30:00Z"
  }
}
```

**Status panen:**
| Status | Keterangan |
|--------|-----------|
| `NORMAL` | Hasil ≥ 80% dari rata-rata historis kabupaten |
| `WARNING` | Hasil 60–80% dari rata-rata |
| `CRITICAL` | Hasil < 60% dari rata-rata |

---

## Struktur Proyek

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py          # Endpoint auth
│   │       └── prediction.py    # Endpoint prediksi
│   ├── core/
│   │   ├── config.py            # Konfigurasi dari .env
│   │   ├── exceptions.py        # Global exception handler
│   │   └── supabase_client.py   # Supabase client
│   ├── data/
│   │   ├── region_coordinates.json  # Koordinat 27 kab/kota Jabar
│   │   └── soil_data.json           # Data tanah per kabupaten
│   ├── middleware/
│   │   └── auth_dependency.py   # JWT Bearer verification
│   ├── schemas/
│   │   ├── auth.py              # Schema request/response auth
│   │   └── prediction.py        # Schema request/response prediksi
│   └── services/
│       ├── auth_service.py      # Logika register/login
│       ├── genai_service.py     # Gemini AI market advice
│       ├── location_service.py  # Resolve lokasi → koordinat
│       ├── ml_service.py        # Weather fetch + model inference
│       └── prediction_service.py # Orkestrasi prediksi
├── .env.example
├── main.py
├── pyproject.toml
└── requirements.txt
```

---

## Dependencies Utama

Lihat [`requirements.txt`](./requirements.txt) untuk daftar lengkap.

| Package             | Versi   | Fungsi                   |
| ------------------- | ------- | ------------------------ |
| `fastapi`           | 0.136.1 | Web framework            |
| `uvicorn`           | 0.46.0  | ASGI server              |
| `supabase`          | 2.30.0  | Auth & database client   |
| `scikit-learn`      | 1.8.0   | ML model inference       |
| `joblib`            | 1.5.3   | Load model `.joblib`     |
| `pandas`            | 3.0.3   | Data processing          |
| `numpy`             | 2.4.6   | Numerical computation    |
| `httpx`             | 0.28.1  | HTTP client (Open-Meteo) |
| `google-genai`      | 2.7.0   | Gemini AI SDK            |
| `pydantic-settings` | 2.14.0  | Konfigurasi dari `.env`  |
