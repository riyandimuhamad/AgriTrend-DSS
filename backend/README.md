# Auth MVP (FastAPI + Supabase)

Struktur modular sederhana untuk belajar:

- `app/core`: konfigurasi `.env`, client Supabase, global exception handler
- `app/schemas`: validasi request/response auth (Pydantic v2)
- `app/services`: logika bisnis auth (register/login/get current user)
- `app/middleware`: dependency verifikasi JWT Bearer token
- `app/api`: endpoint auth

## Endpoint

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me` (butuh `Authorization: Bearer <access_token>`)
- `POST /api/v1/ml/predict` (dummy prediksi + insight AI + koordinat wilayah)
- `GET /health`

Contoh body `POST /api/v1/ml/predict`:

```json
{
  "nitrogen": 90,
  "phosphorus": 42,
  "potassium": 43,
  "temperature": 25.5,
  "humidity": 80.2,
  "ph": 6.5,
  "rainfall": 202.9,
  "crop_type": "rice",
  "kode_kabupaten_kota": 3201,
  "nama_kabupaten_kota": "KABUPATEN BOGOR",
  "insight_mode": "market_only"
}
```

## Run

```bash
uv sync
uv run main.py
```
