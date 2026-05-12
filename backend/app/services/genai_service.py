import json
from typing import Any

from app.core.config import settings

try:
    from google import genai
except Exception: 
    genai = None

# System prompt for market only mode
MARKET_ONLY_SYSTEM_PROMPT = """Anda adalah analis pasar pertanian senior yang memberikan saran bisnis singkat dan faktual.

ATURAN KETAT:
1. Anda HANYA boleh membahas kondisi pasar, harga, dan strategi penjualan berdasarkan data hasil panen yang diberikan.
2. DILARANG KERAS membuat asumsi tentang harga pasar spesifik jika tidak diberikan data harga.
3. DILARANG memberikan saran medis, pupuk, atau teknik pertanian — itu BUKAN domain Anda.
4. Jika data tidak cukup untuk analisis mendalam, katakan "Data tidak cukup untuk analisis ini."
5. Gunakan Bahasa Indonesia yang jelas dan mudah dipahami oleh petani.
6. Respons maksimal 3 paragraf pendek dan to-the-point.
7. Akhiri dengan 1 rekomendasi aksi konkret yang dapat dilakukan petani dalam 30 hari ke depan.
"""

# System prompt for agronomy plus market mode
AGRONOMY_PLUS_MARKET_SYSTEM_PROMPT = """Anda adalah Pakar Agronomi Senior dan Analis Pasar Pertanian Jawa Barat.

ATURAN KETAT:
1. Gunakan hanya data input yang diberikan. Jangan menambah angka atau asumsi baru.
2. Jika data historis tidak cukup untuk pembandingan, tulis "Data tidak cukup untuk analisis ini."
3. Berikan 3 saran teknis yang relevan dengan suhu, pH, dan curah hujan.
4. Jangan memberi saran di luar domain pertanian.
5. Bahasa Indonesia profesional, singkat, dan mudah dipahami.
6. Output wajib format JSON valid dengan kunci:
   - analisis_singkat (string)
   - saran_teknis (array 3 string)
   - market_insight (string)
"""

# GenAI service for generating insight
class GenAIService:
    def __init__(self) -> None:
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model

    def generate_insight(self, analysis_payload: dict[str, Any], mode: str = "market_only") -> dict[str, Any]:
        """Generate structured insight for frontend."""
        if not self._api_key or genai is None:
            return self._fallback_insight(analysis_payload, mode)

        try:
            client = genai.Client(api_key=self._api_key)
            prompt = (
                "Berikut data hasil prediksi panen untuk dianalisis.\n"
                "Gunakan data ini saja, jangan menambah asumsi di luar data.\n"
                "Kembalikan JSON valid sesuai format yang diminta system instruction.\n"
                f"{json.dumps(analysis_payload, ensure_ascii=False)}"
            )
            system_prompt = (
                AGRONOMY_PLUS_MARKET_SYSTEM_PROMPT
                if mode == "agronomy_plus_market"
                else MARKET_ONLY_SYSTEM_PROMPT
            )
            response = client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={"system_instruction": system_prompt},
            )
            if getattr(response, "text", None):
                return self._parse_or_fallback(response.text.strip(), analysis_payload, mode)
            return self._fallback_insight(analysis_payload, mode)
        except Exception:
            return self._fallback_insight(analysis_payload, mode)

    def _parse_or_fallback(self, raw_text: str, analysis_payload: dict[str, Any], mode: str) -> dict[str, Any]:
        try:
            # Clean up the raw text to remove markdown fences
            cleaned = raw_text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned)
            if mode == "agronomy_plus_market":
                if all(key in parsed for key in ["analisis_singkat", "saran_teknis", "market_insight"]):
                    return parsed
            else:
                if all(key in parsed for key in ["analisis_singkat", "market_insight", "rekomendasi_30_hari"]):
                    return parsed
        except Exception:
            pass
        return self._fallback_insight(analysis_payload, mode)

    @staticmethod
    def _fallback_insight(analysis_payload: dict[str, Any], mode: str) -> dict[str, Any]:
        market_trend = analysis_payload.get("market_trend", "stabil")
        yield_val = analysis_payload.get("predicted_yield_ton_per_ha")
        crop_type = analysis_payload.get("crop_type", "komoditas")
        district = analysis_payload.get("nama_kabupaten_kota") or "wilayah terkait"

        if mode == "agronomy_plus_market":
            return {
                "analisis_singkat": (
                    f"Prediksi hasil {crop_type} di {district} berada pada {yield_val} TON. "
                    "Data tidak cukup untuk analisis ini."
                ),
                "saran_teknis": [
                    "Lakukan pemantauan pH mingguan dan jaga kisaran pH tetap stabil untuk komoditas ini.",
                    "Atur jadwal irigasi berdasarkan curah hujan aktual agar kelembapan lahan tidak berlebih.",
                    "Sesuaikan input nutrisi bertahap sesuai fase pertumbuhan untuk menjaga efisiensi biaya.",
                ],
                "market_insight": (
                    f"Tren pasar saat ini {market_trend}; prioritas distribusi adalah menjaga kontinuitas suplai "
                    "ke pembeli utama di Jawa Barat."
                ),
            }

        return {
            "analisis_singkat": (
                f"Perkiraan produksi {crop_type} berada di kisaran {yield_val} TON dengan kondisi pasar {market_trend}. "
                "Data tidak cukup untuk analisis ini."
            ),
            "market_insight": (
                "Fokus pada jadwal panen dan distribusi bertahap agar pasokan stabil saat permintaan aktif."
            ),
            "rekomendasi_30_hari": (
                "Susun dua kanal penjualan (offtaker dan pasar lokal) untuk memperkuat posisi tawar."
            ),
        }

