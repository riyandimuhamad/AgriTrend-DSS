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
- `GET /health`

## Run

```bash
uv sync
uv run main.py
```
