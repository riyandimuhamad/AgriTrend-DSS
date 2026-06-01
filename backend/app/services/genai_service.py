from app.core.config import settings

try:
    from google import genai
except Exception:
    genai = None

_SYSTEM_PROMPT = """Anda adalah analis pasar pertanian senior untuk wilayah Jawa Barat yang memberikan saran bisnis singkat dan faktual kepada petani.

ATURAN KETAT:
1. Anda HANYA boleh membahas kondisi pasar, harga, dan strategi penjualan berdasarkan data hasil panen yang diberikan.
2. DILARANG KERAS membuat asumsi tentang harga pasar spesifik jika tidak diberikan data harga.
3. DILARANG memberikan saran medis, pupuk, atau teknik pertanian — itu BUKAN domain Anda.
4. Jika data tidak cukup untuk analisis mendalam, katakan "Data tidak cukup untuk analisis ini."
5. Gunakan Bahasa Indonesia yang jelas dan mudah dipahami oleh petani.
6. Respons maksimal 3 paragraf pendek dan to-the-point.
7. Akhiri dengan 1 rekomendasi aksi konkret yang dapat dilakukan petani dalam 30 hari ke depan."""


class GenAIService:
    def __init__(self) -> None:
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model

    def generate_advice(
        self,
        crop_type: str,
        region: str,
        yield_per_ha: float,
        status: str,
    ) -> str:
        prompt = (
            f"Tanaman: {crop_type}\n"
            f"Wilayah: {region}\n"
            f"Prediksi hasil panen: {yield_per_ha:.2f} ton/ha\n"
            f"Status panen: {status}\n"
            "Berikan analisis pasar dan rekomendasi aksi konkret untuk petani."
        )

        if self._api_key and genai is not None:
            try:
                client = genai.Client(api_key=self._api_key)
                response = client.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config={"system_instruction": _SYSTEM_PROMPT},
                )
                if getattr(response, "text", None):
                    return response.text.strip()
            except Exception:
                pass

        return self._fallback(crop_type, region, yield_per_ha, status)

    @staticmethod
    def _fallback(crop_type: str, region: str, yield_per_ha: float, status: str) -> str:
        if status == "NORMAL":
            return (
                f"Hasil panen {crop_type} di {region} diprediksi normal ({yield_per_ha:.2f} ton/ha). "
                "Kondisi pasar saat ini relatif stabil sehingga peluang penjualan cukup baik. "
                "Dalam 30 hari ke depan, segera jalin komunikasi dengan pengepul atau koperasi setempat "
                "untuk mengamankan harga jual sebelum masa panen tiba."
            )
        if status == "CRITICAL":
            return (
                f"Hasil panen {crop_type} di {region} diprediksi rendah ({yield_per_ha:.2f} ton/ha). "
                "Data tidak cukup untuk analisis pasar mendalam pada kondisi ini. "
                "Dalam 30 hari ke depan, prioritaskan koordinasi dengan dinas pertanian setempat "
                "untuk mendapatkan bantuan atau skema subsidi yang tersedia."
            )
        return (
            f"Hasil panen {crop_type} di {region} diprediksi di bawah rata-rata ({yield_per_ha:.2f} ton/ha). "
            "Pertimbangkan untuk mendiversifikasi kanal penjualan agar tidak bergantung pada satu pembeli. "
            "Dalam 30 hari ke depan, susun dua kanal penjualan (offtaker dan pasar lokal) "
            "untuk memperkuat posisi tawar."
        )
