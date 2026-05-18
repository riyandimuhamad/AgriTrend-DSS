import requests
import json

prediksi_yield_rf = 42.58  
tanaman_aktif = "Padi (Rice)"
lokasi_panen = "Kabupaten Garut"

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

# Endpoint API lokal Ollama
url_ollama = "http://localhost:11434/api/generate"
payload_data = {
    "model": "qwen2.5:7b",  # Menggunakan model 7b yang sudah terinstall di laptop kamu
    "prompt": prompt_system,
    "stream": False
}

print("[INFO] Mengirim parameter prediksi ke Ollama lokal...")
try:
    respons_api = requests.post(url_ollama, json=payload_data)
    hasil_json = respons_api.json()
    
    print("\n=======================================================")
    print(" REKOMENDASI GEN-AI OLLAMA (AGRITREND DSS MARKETS) ")
    print("=======================================================")
    
    if 'response' in hasil_json:
        print(hasil_json['response'].encode('ascii', 'ignore').decode('ascii'))
    elif 'message' in hasil_json and 'content' in hasil_json['message']:
        print(hasil_json['message']['content'].encode('ascii', 'ignore').decode('ascii'))
    else:
        print("[DEBUG] Struktur JSON asli dari Ollama:")
        print(json.dumps(hasil_json, indent=2))
        
    print("=======================================================")

except requests.exceptions.ConnectionError:
    print("[ERROR] Aplikasi Ollama belum aktif di background.")
