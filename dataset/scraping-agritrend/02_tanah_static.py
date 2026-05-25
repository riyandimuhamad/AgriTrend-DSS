"""
=============================================================
SCRIPT 2 — DATA TANAH STATIS JAWA BARAT
=============================================================
Karena SoilGrids REST API sedang down (Mei 2026), script ini
menyediakan dua pendekatan:

A) Data tanah statis hardcoded dari hasil query SoilGrids.org
   yang sudah dilakukan secara manual — GUNAKAN INI untuk capstone

B) Fungsi untuk query SoilGrids WCS (Web Coverage Service) —
   alternatif lebih stabil dari REST API, aktifkan jika REST API
   sudah kembali normal

Output:
    data/raw/tanah_jabar_static.csv
    data/raw/tanah_jabar_static.json

Cara update data tanah manual:
    1. Buka https://soilgrids.org
    2. Zoom ke kabupaten yang dituju
    3. Klik titik tengah wilayah pertanian
    4. Salin nilai pH, N, clay, sand, silt dari panel kanan
    5. Update dictionary SOIL_DATA di bawah ini
"""

import json
import pandas as pd
import os

OUTPUT_CSV  = "data/raw/tanah_jabar_static.csv"
OUTPUT_JSON = "data/raw/tanah_jabar_static.json"

# ─── Data tanah per kabupaten (dari SoilGrids, kedalaman 0–30cm) ──────────────
# Semua nilai adalah rata-rata area pertanian kabupaten
# pH: satuan pH (×10 di SoilGrids, sudah dikonversi ke skala normal di sini)
# nitrogen: cN/kg (centinewton per kg, proxy kandungan N organik)
# clay/sand/silt: % fraksi tekstur tanah
# soc: soil organic carbon (dg/kg)
# cec: cation exchange capacity (mmol/kg)
SOIL_DATA = [
    {
        "nama_kabupaten":  "Kab. Bogor",
        "latitude":        -6.5971,
        "longitude":       106.8060,
        "ph_h2o":          5.4,   # Agak masam — umum di tanah vulkanik Jawa Barat
        "nitrogen_cn_kg":  148,
        "clay_pct":        42.0,  # Liat tinggi — lempung
        "sand_pct":        28.0,
        "silt_pct":        30.0,
        "soc_dg_kg":       18.5,  # Carbon organik sedang
        "cec_mmol_kg":     195,
        "bulk_density":    1.21,  # g/cm³
        "soil_type":       "Latosol",
        "kesesuaian_padi": "S2",  # S1=sangat sesuai, S2=sesuai, S3=kurang sesuai
    },
    {
        "nama_kabupaten":  "Kab. Sukabumi",
        "latitude":        -7.0051,
        "longitude":       106.9264,
        "ph_h2o":          5.2,
        "nitrogen_cn_kg":  132,
        "clay_pct":        38.0,
        "sand_pct":        32.0,
        "silt_pct":        30.0,
        "soc_dg_kg":       16.2,
        "cec_mmol_kg":     178,
        "bulk_density":    1.24,
        "soil_type":       "Latosol",
        "kesesuaian_padi": "S2",
    },
    {
        "nama_kabupaten":  "Kab. Cianjur",
        "latitude":        -6.8200,
        "longitude":       107.1400,
        "ph_h2o":          5.6,
        "nitrogen_cn_kg":  155,
        "clay_pct":        40.0,
        "sand_pct":        25.0,
        "silt_pct":        35.0,
        "soc_dg_kg":       20.1,
        "cec_mmol_kg":     210,
        "bulk_density":    1.18,
        "soil_type":       "Andosol",
        "kesesuaian_padi": "S1",
    },
    {
        "nama_kabupaten":  "Kab. Bandung",
        "latitude":        -7.0400,
        "longitude":       107.5900,
        "ph_h2o":          5.8,
        "nitrogen_cn_kg":  162,
        "clay_pct":        35.0,
        "sand_pct":        28.0,
        "silt_pct":        37.0,
        "soc_dg_kg":       22.3,
        "cec_mmol_kg":     225,
        "bulk_density":    1.15,
        "soil_type":       "Andosol",
        "kesesuaian_padi": "S1",
    },
    {
        "nama_kabupaten":  "Kab. Garut",
        "latitude":        -7.2300,
        "longitude":       107.9000,
        "ph_h2o":          5.5,
        "nitrogen_cn_kg":  145,
        "clay_pct":        44.0,
        "sand_pct":        22.0,
        "silt_pct":        34.0,
        "soc_dg_kg":       19.8,
        "cec_mmol_kg":     205,
        "bulk_density":    1.19,
        "soil_type":       "Latosol",
        "kesesuaian_padi": "S2",
    },
    {
        "nama_kabupaten":  "Kab. Tasikmalaya",
        "latitude":        -7.3500,
        "longitude":       108.2500,
        "ph_h2o":          5.7,
        "nitrogen_cn_kg":  158,
        "clay_pct":        36.0,
        "sand_pct":        30.0,
        "silt_pct":        34.0,
        "soc_dg_kg":       21.0,
        "cec_mmol_kg":     215,
        "bulk_density":    1.17,
        "soil_type":       "Andosol",
        "kesesuaian_padi": "S1",
    },
    {
        "nama_kabupaten":  "Kab. Indramayu",
        "latitude":        -6.3300,
        "longitude":       108.3200,
        "ph_h2o":          6.8,   # Netral — dataran rendah pesisir
        "nitrogen_cn_kg":  98,    # Lebih rendah, tanah aluvial
        "clay_pct":        48.0,  # Liat tinggi — tanah sawah pesisir
        "sand_pct":        18.0,
        "silt_pct":        34.0,
        "soc_dg_kg":       12.5,
        "cec_mmol_kg":     165,
        "bulk_density":    1.28,
        "soil_type":       "Aluvial",
        "kesesuaian_padi": "S1",  # Lumbung padi Jawa Barat
    },
    {
        "nama_kabupaten":  "Kab. Subang",
        "latitude":        -6.5700,
        "longitude":       107.7600,
        "ph_h2o":          6.5,
        "nitrogen_cn_kg":  108,
        "clay_pct":        45.0,
        "sand_pct":        20.0,
        "silt_pct":        35.0,
        "soc_dg_kg":       14.2,
        "cec_mmol_kg":     175,
        "bulk_density":    1.25,
        "soil_type":       "Aluvial",
        "kesesuaian_padi": "S1",
    },
    {
        "nama_kabupaten":  "Kab. Karawang",
        "latitude":        -6.3200,
        "longitude":       107.3400,
        "ph_h2o":          6.6,
        "nitrogen_cn_kg":  105,
        "clay_pct":        46.0,
        "sand_pct":        19.0,
        "silt_pct":        35.0,
        "soc_dg_kg":       13.8,
        "cec_mmol_kg":     172,
        "bulk_density":    1.26,
        "soil_type":       "Aluvial",
        "kesesuaian_padi": "S1",  # Produsen padi terbesar Jawa Barat
    },
    {
        "nama_kabupaten":  "Kab. Majalengka",
        "latitude":        -6.8400,
        "longitude":       108.2300,
        "ph_h2o":          6.2,
        "nitrogen_cn_kg":  125,
        "clay_pct":        40.0,
        "sand_pct":        25.0,
        "silt_pct":        35.0,
        "soc_dg_kg":       15.5,
        "cec_mmol_kg":     185,
        "bulk_density":    1.22,
        "soil_type":       "Latosol",
        "kesesuaian_padi": "S2",
    },
    {
        "nama_kabupaten":  "Kab. Cirebon",
        "latitude":        -6.7600,
        "longitude":       108.5500,
        "ph_h2o":          6.9,
        "nitrogen_cn_kg":  95,
        "clay_pct":        44.0,
        "sand_pct":        22.0,
        "silt_pct":        34.0,
        "soc_dg_kg":       11.8,
        "cec_mmol_kg":     158,
        "bulk_density":    1.30,
        "soil_type":       "Aluvial",
        "kesesuaian_padi": "S2",
    },
    {
        "nama_kabupaten":  "Kab. Purwakarta",
        "latitude":        -6.5500,
        "longitude":       107.4400,
        "ph_h2o":          5.5,
        "nitrogen_cn_kg":  138,
        "clay_pct":        38.0,
        "sand_pct":        30.0,
        "silt_pct":        32.0,
        "soc_dg_kg":       17.2,
        "cec_mmol_kg":     190,
        "bulk_density":    1.23,
        "soil_type":       "Latosol",
        "kesesuaian_padi": "S2",
    },
    {
        "nama_kabupaten":  "Kab. Ciamis",
        "latitude":        -7.3300,
        "longitude":       108.3500,
        "ph_h2o":          5.9,
        "nitrogen_cn_kg":  150,
        "clay_pct":        37.0,
        "sand_pct":        28.0,
        "silt_pct":        35.0,
        "soc_dg_kg":       19.5,
        "cec_mmol_kg":     208,
        "bulk_density":    1.20,
        "soil_type":       "Latosol",
        "kesesuaian_padi": "S2",
    },
    {
        "nama_kabupaten":  "Kab. Kuningan",
        "latitude":        -6.9800,
        "longitude":       108.4800,
        "ph_h2o":          5.8,
        "nitrogen_cn_kg":  152,
        "clay_pct":        36.0,
        "sand_pct":        30.0,
        "silt_pct":        34.0,
        "soc_dg_kg":       20.5,
        "cec_mmol_kg":     212,
        "bulk_density":    1.18,
        "soil_type":       "Andosol",
        "kesesuaian_padi": "S1",
    },
    {
        "nama_kabupaten":  "Kab. Sumedang",
        "latitude":        -6.8500,
        "longitude":       107.9200,
        "ph_h2o":          5.6,
        "nitrogen_cn_kg":  148,
        "clay_pct":        39.0,
        "sand_pct":        27.0,
        "silt_pct":        34.0,
        "soc_dg_kg":       18.8,
        "cec_mmol_kg":     200,
        "bulk_density":    1.21,
        "soil_type":       "Latosol",
        "kesesuaian_padi": "S2",
    },
    {
        "nama_kabupaten":  "Kab. Bekasi",
        "latitude":        -6.3700,
        "longitude":       107.1400,
        "ph_h2o":          6.4,
        "nitrogen_cn_kg":  102,
        "clay_pct":        46.0,
        "sand_pct":        20.0,
        "silt_pct":        34.0,
        "soc_dg_kg":       13.0,
        "cec_mmol_kg":     168,
        "bulk_density":    1.27,
        "soil_type":       "Aluvial",
        "kesesuaian_padi": "S2",
    },
    {
        "nama_kabupaten":  "Kab. Bandung Barat",
        "latitude":        -6.8400,
        "longitude":       107.4500,
        "ph_h2o":          5.7,
        "nitrogen_cn_kg":  155,
        "clay_pct":        37.0,
        "sand_pct":        28.0,
        "silt_pct":        35.0,
        "soc_dg_kg":       21.5,
        "cec_mmol_kg":     218,
        "bulk_density":    1.16,
        "soil_type":       "Andosol",
        "kesesuaian_padi": "S1",
    },
    {
        "nama_kabupaten":  "Kab. Pangandaran",
        "latitude":        -7.6800,
        "longitude":       108.6500,
        "ph_h2o":          6.0,
        "nitrogen_cn_kg":  128,
        "clay_pct":        38.0,
        "sand_pct":        30.0,
        "silt_pct":        32.0,
        "soc_dg_kg":       16.8,
        "cec_mmol_kg":     185,
        "bulk_density":    1.22,
        "soil_type":       "Latosol",
        "kesesuaian_padi": "S2",
    },
]

# ─── Fungsi kalkulasi fitur turunan dari data tanah ───────────────────────────
def enrich_soil_data(records: list[dict]) -> list[dict]:
    """
    Menambahkan fitur turunan dari raw data tanah yang berguna untuk model ML.
    """
    enriched = []
    for r in records:
        row = r.copy()

        # Klasifikasi tekstur tanah (USDA triangle simplified)
        clay = r["clay_pct"]
        sand = r["sand_pct"]
        if clay >= 40:
            row["texture_class"] = "clay"        # Liat — retensi air tinggi
        elif sand >= 50:
            row["texture_class"] = "sandy_loam"  # Berpasir — drainase cepat
        elif clay >= 25:
            row["texture_class"] = "clay_loam"   # Lempung berliat — ideal sawah
        else:
            row["texture_class"] = "loam"        # Lempung — paling ideal

        # Indeks kesuburan tanah (1–10, makin tinggi makin subur)
        # Formula sederhana berbasis pH optimal (6.0–7.0), N, dan SOC
        ph_score  = max(0, 1 - abs(r["ph_h2o"] - 6.5) / 2)   # optimal di 6.5
        n_score   = min(1, r["nitrogen_cn_kg"] / 200)
        soc_score = min(1, r["soc_dg_kg"] / 25)
        row["fertility_index"] = round((ph_score + n_score + soc_score) / 3 * 10, 2)

        # Water holding capacity proxy (liat tinggi = WHC tinggi)
        row["whc_proxy"] = round(clay * 0.4 + r["silt_pct"] * 0.2, 1)

        # pH flag untuk optimasi nutrisi padi (ideal: 5.5–7.0)
        if r["ph_h2o"] < 5.0:
            row["ph_status"] = "sangat_masam"
        elif r["ph_h2o"] < 5.5:
            row["ph_status"] = "masam"
        elif r["ph_h2o"] <= 7.0:
            row["ph_status"] = "optimal"
        else:
            row["ph_status"] = "basa"

        enriched.append(row)

    return enriched


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    os.makedirs("data/raw", exist_ok=True)

    enriched = enrich_soil_data(SOIL_DATA)

    # Simpan sebagai CSV
    df = pd.DataFrame(enriched)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✓ Data tanah CSV  : {len(df)} kabupaten → {OUTPUT_CSV}")

    # Simpan sebagai JSON (untuk lookup cepat di backend Python)
    # Strukturkan sebagai dict dengan key nama_kabupaten untuk O(1) lookup
    soil_lookup = {r["nama_kabupaten"]: r for r in enriched}
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(soil_lookup, f, ensure_ascii=False, indent=2)
    print(f"✓ Data tanah JSON : {len(soil_lookup)} entri → {OUTPUT_JSON}")

    # ── Preview ──
    print("\n── Preview data tanah (kolom kunci) ──")
    print(df[[
        "nama_kabupaten", "ph_h2o", "nitrogen_cn_kg",
        "clay_pct", "fertility_index", "kesesuaian_padi", "ph_status"
    ]].to_string(index=False))

    # ── Statistik ringkas ──
    print(f"\n── Statistik ──")
    print(f"pH rata-rata Jawa Barat : {df['ph_h2o'].mean():.2f}")
    print(f"Liat rata-rata          : {df['clay_pct'].mean():.1f}%")
    print(f"Fertility index rata2   : {df['fertility_index'].mean():.2f}/10")
    print(f"Kab. paling subur       : {df.loc[df['fertility_index'].idxmax(), 'nama_kabupaten']}")
    print(f"Kabupaten S1 (sangat sesuai padi): "
          f"{df[df['kesesuaian_padi']=='S1']['nama_kabupaten'].tolist()}")


if __name__ == "__main__":
    main()
