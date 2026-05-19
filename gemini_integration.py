import os
from google import genai

def generate_market_analysis(prediksi_yield_rf, tanaman_aktif, lokasi_panen):
    """
    Fungsi untuk menghasilkan analisis pasar menggunakan API Gemini Flash
    berdasarkan input parameter dari model Machine Learning Random Forest.
    Dibuat oleh: Riyandi (ML Architect)
    """
    try:
        # Menggunakan SDK google-genai terbaru. 
        # Client otomatis membaca token dari environment variable GEMINI_API_KEY di server Vercel.
        client = genai.Client()
        
        prompt_system = f"""
        Anda adalah AgriTrend AI Market Consultant, pakar ekonomi pertanian senior di Jawa Barat.
        Tugas: Berikan analisis wawasan pasar, potensi risiko saturasi, dan rekomendasi aksi nyata berdasarkan input data prediksi berikut.

        Data Input:
        - Komoditas Tanaman: {tanaman_aktif}
        - Prediksi Hasil Panen: {prediksi_yield_rf:.2f} ton/hektar
        - Wilayah Lokasi: {lokasi_panen}

        Format Output Wajib Menggunakan Markdown:
        ### Analisis Satuan Pasar
        [Narasi maksimal 2 kalimat kondisi pasar tanaman ini]

        ### Potensi Risiko dan Saturasi
        [Sebutkan risiko jika pasokan melonjak di wilayah tersebut]

        ### Rekomendasi Aksi Taktis
        - [Rekomendasi taktis 1]
        - [Rekomendasi taktis 2]

        Catatan: Jawaban harus lugas, langsung pada intinya, menggunakan Bahasa Indonesia formal. Dilarang keras menggunakan emoji atau karakter ikon ikonik dalam jawaban Anda.
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_system,
        )
        return response.text
        
    except Exception as e:
        return f"[ERROR] Gagal memproses narasi pasar via Gemini: {str(e)}"

if __name__ == "__main__":
    print("[INFO] Testing struktur fungsi Gemini Integration...")
    print("[INFO] Fungsi siap di-import oleh Ni'am ke backend Streamlit.")
