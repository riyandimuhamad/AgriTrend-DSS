# AgriTrend DSS

Decision Support System berbasis Machine Learning dan Generative AI untuk prediksi hasil panen dan analisis tren pasar komoditas pertanian.

## Daftar Isi

- [Gambaran Umum](#gambaran-umum)
- [Tech Stack](#tech-stack)
- [Prasyarat](#prasyarat)
- [Instalasi](#instalasi)
- [Konfigurasi](#konfigurasi)
- [Supabase Setup](#supabase-setup)
- [Menjalankan Aplikasi](#menjalankan-aplikasi)
- [Perintah Tersedia](#perintah-tersedia)
- [Dokumentasi API](#dokumentasi-api)
- [Struktur Project](#struktur-project)
- [Lisensi](#lisensi)

---

## Gambaran Umum

AgriTrend DSS membantu petani lokal dalam mengambil keputusan berbasis data melalui:

- **Prediksi hasil panen** berdasarkan data agronomi (N, P, K, suhu, kelembapan, pH, curah hujan)
- **Klasifikasi tren pasar** — _potensi naik_, _stabil_, atau _perlu mitigasi distribusi_
- **AI insight** menggunakan Google Gemini dengan dua mode analisis: `market_only` dan `agronomy_plus_market`
- **Resolusi koordinat wilayah** dari kode atau nama kabupaten/kota
- **Autentikasi** berbasis JWT melalui Supabase Auth

---

## Tech Stack

| Layer           | Teknologi                                                 |
| --------------- | --------------------------------------------------------- |
| Frontend        | React 19, TanStack Router, Vite, TypeScript, Tailwind CSS |
| Backend         | FastAPI, Python 3.12, Uvicorn                             |
| Database & Auth | Supabase (PostgreSQL + Auth)                              |
| AI              | Google Gemini API (`gemini-2.5-flash`)                    |
| ML              | scikit-learn (Random Forest), joblib                      |
| Deployment      | Vercel (backend), Cloudflare (frontend)                   |

---

## Prasyarat

### Node.js v24+

Download dan install dari situs resmi:

**https://nodejs.org/en/download**

Pilih versi **LTS** atau **Current v24**, kemudian ikuti installer sesuai sistem operasi.

```bash
node --version   # v24.x.x atau lebih
npm --version
```

### Python 3.12+

Download dari **https://www.python.org/downloads/**

```bash
python --version   # 3.12 atau lebih
```

### uv (direkomendasikan)

`uv` adalah Python package manager yang lebih cepat dari `pip`. Jika tidak tersedia, setup script akan otomatis fallback ke `pip`.

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Instalasi

Clone repository:

```bash
git clone https://github.com/riyandimuhamad/AgriTrend-DSS.git
cd AgriTrend-DSS
```

Jalankan setup otomatis:

```bash
node setup.js
```

Script akan menangani seluruh proses: menyalin file `.env`, menginstall dependencies frontend dan backend, melatih serta memvalidasi model Machine Learning secara otomatis (`train_model.py` & `predictor.py`), lalu menjalankan kedua server secara bersamaan.

---

## Konfigurasi

Salin file contoh environment:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### `backend/.env`

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your-supabase-anon-key
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
ALLOWED_ORIGINS=http://localhost:5173
```

### `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Referensi environment variables backend

| Variable          | Wajib | Default            | Keterangan                         |
| ----------------- | ----- | ------------------ | ---------------------------------- |
| `SUPABASE_URL`    | Ya    | —                  | URL project Supabase               |
| `SUPABASE_KEY`    | Ya    | —                  | Anon/service key Supabase          |
| `GEMINI_API_KEY`  | Ya    | —                  | API key Google Gemini              |
| `GEMINI_MODEL`    | Tidak | `gemini-2.5-flash` | Model Gemini yang digunakan        |
| `ALLOWED_ORIGINS` | Tidak | `*`                | CORS origins, pisahkan dengan koma |
| `HOST`            | Tidak | `0.0.0.0`          | Host server                        |
| `PORT`            | Tidak | `8000`             | Port server                        |

---

## Supabase Setup

Tabel dan kebijakan keamanan berikut harus dibuat secara manual melalui **SQL Editor** di dashboard Supabase project Anda.

### 1. Buat tabel `predictions`

```sql
CREATE TABLE predictions (
    id           uuid PRIMARY KEY,
    user_id      uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    crop_type    text NOT NULL,
    region       text NOT NULL,
    yield_per_ha float8 NOT NULL,
    yield_total  float8 NOT NULL,
    yield_min    float8 NOT NULL,
    yield_max    float8 NOT NULL,
    confidence   int NOT NULL,
    status       text NOT NULL,
    unit         text NOT NULL DEFAULT 'ton',
    created_at   timestamptz NOT NULL DEFAULT now(),
    advice_analysis text,
    advice_recommendation text;
);
```

### 2. Aktifkan Row Level Security (RLS)

```sql
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user can manage own predictions"
ON predictions FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);
```

### 3. Buat index (opsional, untuk performa)

```sql
CREATE INDEX idx_predictions_user_id ON predictions(user_id);
```

> Tabel `auth.users` tidak perlu dibuat — sudah dikelola otomatis oleh Supabase Auth.

---

## Menjalankan Aplikasi

Setelah instalasi selesai, jalankan development server:

```bash
node setup.js dev
```

| Service      | URL                          |
| ------------ | ---------------------------- |
| Backend API  | http://localhost:8000        |
| Frontend     | http://localhost:5173        |
| Swagger UI   | http://localhost:8000/docs   |
| Health check | http://localhost:8000/health |

---

## Perintah Tersedia

| Perintah                | Keterangan                                                                     |
| ----------------------- | ------------------------------------------------------------------------------ |
| `node setup.js`         | Install dependensi, train & verifikasi model ML, dan jalankan dev server       |
| `node setup.js install` | Hanya install dependensi dan setup (train/verifikasi) model ML                |
| `node setup.js dev`     | Hanya jalankan dev server                                                      |
| `npm run setup`         | Alias untuk `node setup.js`                                                    |
| `npm run install:all`   | Alias untuk `node setup.js install`                                            |
| `npm run dev`           | Alias untuk `node setup.js dev`                                                |

---

## Dokumentasi API

Base URL: `http://localhost:8000/api/v1`

Dokumentasi interaktif tersedia di `/docs` (Swagger UI) saat server berjalan.

### Autentikasi

| Method | Endpoint         | Auth   | Deskripsi                   |
| ------ | ---------------- | ------ | --------------------------- |
| `POST` | `/auth/register` | —      | Daftar akun baru            |
| `POST` | `/auth/login`    | —      | Login dan mendapatkan token |
| `POST` | `/auth/logout`   | Bearer | Logout                      |
| `GET`  | `/auth/me`       | Bearer | Profil user aktif           |

**Request body (register):**

```json
{
  "email": "user@example.com",
  "username": "namauser",
  "password": "min8karakter"
}
```

**Request body (login):**

```json
{
  "email": "user@example.com",
  "password": "min8karakter"
}
```

**Response:**

```json
{
  "access_token": "eyJ...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {},
  "message": "Login berhasil."
}
```

---

### Prediksi

| Method | Endpoint      | Auth | Deskripsi                           |
| ------ | ------------- | ---- | ----------------------------------- |
| `POST` | `/ml/predict` | —    | Prediksi hasil panen dan AI insight |

**Request body:**

```json
{
  "nitrogen": 50,
  "phosphorus": 30,
  "potassium": 20,
  "temperature": 28.5,
  "humidity": 70,
  "ph": 6.5,
  "rainfall": 200,
  "crop_type": "padi",
  "kode_kabupaten_kota": 3204,
  "nama_kabupaten_kota": "KABUPATEN BANDUNG",
  "insight_mode": "market_only"
}
```

| Field                 | Tipe           | Keterangan                                  |
| --------------------- | -------------- | ------------------------------------------- |
| `nitrogen`            | float          | Kandungan nitrogen (≥ 0)                    |
| `phosphorus`          | float          | Kandungan fosfor (≥ 0)                      |
| `potassium`           | float          | Kandungan kalium (≥ 0)                      |
| `temperature`         | float          | Suhu rata-rata (°C)                         |
| `humidity`            | float          | Kelembapan udara (0–100)                    |
| `ph`                  | float          | pH tanah (0–14)                             |
| `rainfall`            | float          | Curah hujan (mm, ≥ 0)                       |
| `crop_type`           | string         | Jenis komoditas (min. 2 karakter)           |
| `kode_kabupaten_kota` | int \| null    | Kode BPS wilayah                            |
| `nama_kabupaten_kota` | string \| null | Nama wilayah (fallback jika kode tidak ada) |
| `insight_mode`        | string         | `market_only` atau `agronomy_plus_market`   |

**Response:**

```json
{
  "prediction": {
    "predicted_yield_ton_per_ha": 5.8,
    "market_trend": "stabil",
    "coordinates": {
      "latitude": -7.0367,
      "longitude": 107.5222,
      "region": "KABUPATEN BANDUNG"
    }
  },
  "insight": "...",
  "insight_structured": {
    "analisis_singkat": "...",
    "market_insight": "...",
    "rekomendasi_30_hari": "..."
  }
}
```

**Nilai `market_trend`:**

| Nilai                       | Kondisi                       |
| --------------------------- | ----------------------------- |
| `potensi naik`              | Prediksi yield >= 6.5 ton/ha  |
| `stabil`                    | Prediksi yield 4.0–6.4 ton/ha |
| `perlu mitigasi distribusi` | Prediksi yield < 4.0 ton/ha   |

**Struktur `insight_structured` berdasarkan `insight_mode`:**

| Mode                   | Keys                                                         |
| ---------------------- | ------------------------------------------------------------ |
| `market_only`          | `analisis_singkat`, `market_insight`, `rekomendasi_30_hari`  |
| `agronomy_plus_market` | `analisis_singkat`, `saran_teknis` (array), `market_insight` |

---

### Health Check

```
GET /health
```

```json
{ "status": "ok" }
```

---

### Format Error

Semua error menggunakan format yang seragam:

```json
{
  "success": false,
  "message": "Request failed",
  "detail": "Pesan error detail"
}
```

| HTTP Status | Kondisi                          |
| ----------- | -------------------------------- |
| `400`       | Request tidak valid              |
| `401`       | Token tidak ada atau tidak valid |
| `403`       | Email belum diverifikasi         |
| `409`       | Email sudah terdaftar            |
| `422`       | Validasi input gagal             |
| `429`       | Rate limit Supabase              |
| `500`       | Internal server error            |

---

## Wilayah yang Didukung

Resolusi koordinat tersedia untuk wilayah berikut. Wilayah di luar daftar akan menggunakan koordinat default Indonesia.

| Kode | Nama Wilayah       |
| ---- | ------------------ |
| 3171 | Kota Jakarta Pusat |
| 3201 | Kabupaten Bogor    |
| 3202 | Kabupaten Sukabumi |
| 3203 | Kabupaten Cianjur  |
| 3204 | Kabupaten Bandung  |
| 3205 | Kabupaten Garut    |

---

## Struktur Project

```
AgriTrend-DSS/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── auth.py
│   │   │       └── prediction.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── exceptions.py
│   │   │   └── supabase_client.py
│   │   ├── data/
│   │   │   └── region_coordinates.json
│   │   ├── middleware/
│   │   │   └── auth_dependency.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   └── prediction.py
│   │   └── services/
│   │       ├── auth_service.py
│   │       ├── genai_service.py
│   │       ├── location_service.py
│   │       └── prediction_service.py
│   ├── .env.example
│   ├── main.py
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   └── src/
├── ml_models/
│   ├── train_model.py
│   └── predictor.py
├── dataset/
├── setup.js
└── package.json
```

## License

ISC &copy; [AgriTrend-DSS Team](https://github.com/riyandimuhamad/AgriTrend-DSS)
