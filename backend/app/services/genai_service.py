from app.core.config import settings
from app.schemas.prediction import AIAdviceStructuredOutput

try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None

_SYSTEM_PROMPT = """Anda adalah analis pasar pertanian senior yang memberikan saran bisnis taktis, singkat, dan faktual kepada petani berdasarkan hasil prediksi panen.

KONTEKS PARAMETER:
Anda akan menerima data Tanaman, Wilayah, Prediksi Hasil, dan Status Panen (NORMAL, WARNING, atau CRITICAL). Karena data harga riil tidak diberikan, lakukan analisis pasar berbasis dinamika volume (supply) dan manajemen risiko penjualan.

PANDUAN STRATEGI BERDASARKAN STATUS:
- STATUS NORMAL: Pasokan aman. Fokus pada strategi pengamanan harga pasar (lock-in price) bersama koperasi atau offtaker sebelum panen raya agar harga tidak jatuh akibat lonjakan supply.
- STATUS WARNING / CRITICAL: Pasokan rendah/terancam. Volume penjualan berkurang. Fokus pada diversifikasi kanal penjualan (pasar lokal vs korporasi), efisiensi distribusi untuk menekan margin loss, atau koordinasi dengan dinas terkait untuk skema mitigasi.

ATURAN KETAT:
1. Pembahasan HANYA seputar manajemen risiko pasar, rantai pasok, dan strategi penjualan.
2. DILARANG MENCANTUMKAN ANGKA HARGA SPESIFIK (misal: Rp 15.000/kg) karena data harga tidak disediakan. Fokuslah pada tren supply-demand.
3. DILARANG KERAS memberikan saran teknis pertanian (pupuk, pestisida, penanganan hama, atau medis).
4. Gunakan Bahasa Indonesia yang jelas, memotivasi, dan mudah dipahami oleh petani lokal."""


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
    ) -> AIAdviceStructuredOutput:
        prompt = (
            f"Analisis data berikut:\n"
            f"- Tanaman: {crop_type}\n"
            f"- Wilayah: {region}\n"
            f"- Prediksi Hasil Panen: {yield_per_ha:.2f} ton/ha\n"
            f"- Status Panen: {status}\n\n"
            f"Berikan analisis pasar dan strategi mitigasi penjualan yang sesuai."
        )

        if self._api_key and genai is not None:
            try:
                client = genai.Client(api_key=self._api_key)
                response = client.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=_SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        response_schema=AIAdviceStructuredOutput,
                    ),
                )
                # SDK otomatis mem-parse ke dict saat response_schema Pydantic diberikan
                parsed = response.parsed
                if parsed is not None:
                    return parsed
            except Exception as e:
                print(f"[GenAI] Error: {e}")

        return self._fallback(crop_type, region, yield_per_ha, status)

    @staticmethod
    def _fallback(
        crop_type: str, region: str, yield_per_ha: float, status: str
    ) -> AIAdviceStructuredOutput:
        if status == "NORMAL":
            return AIAdviceStructuredOutput(
                analysis=f"Hasil panen {crop_type} di {region} diprediksi normal ({yield_per_ha:.2f} ton/ha). Kondisi pasar relatif stabil sehingga peluang penjualan cukup baik.",
                recommendation="Segera jalin komunikasi dengan pengepul atau koperasi setempat untuk mengamankan kontrak harga jual sebelum masa panen tiba.",
            )
        if status == "CRITICAL":
            return AIAdviceStructuredOutput(
                analysis=f"Hasil panen {crop_type} di {region} diprediksi rendah ({yield_per_ha:.2f} ton/ha). Penurunan volume berisiko mengganggu stabilitas pendapatan.",
                recommendation="Segera koordinasi dengan kelompok tani atau dinas pertanian untuk mendapatkan informasi skema subsidi yang tersedia.",
            )
        return AIAdviceStructuredOutput(
            analysis=f"Hasil panen {crop_type} di {region} diprediksi di bawah rata-rata ({yield_per_ha:.2f} ton/ha). Keterbatasan volume menuntut tata kelola distribusi yang lebih taktis.",
            recommendation="Susun dua jalur penjualan alternatif (pasar lokal dan offtaker langsung) untuk membagi risiko serapan pasar.",
        )
