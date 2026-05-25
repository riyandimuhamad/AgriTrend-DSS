"""
=============================================================
SCRIPT 1 — PENGAMBILAN DATA CUACA (Open-Meteo Historical API)
=============================================================
Mengambil data cuaca historis per kabupaten/kota di Jawa Barat
dari tahun 2019 hingga 2024 menggunakan ERA5 reanalysis data.

Cara jalankan:
    pip install requests pandas tqdm
    python 01_cuaca_openmeteo.py

Output:
    data/raw/cuaca_jabar_2019_2024.csv
    data/raw/cuaca_per_kabupaten/cuaca_{kabupaten}.csv
"""

import requests
import pandas as pd
import time
import os
from tqdm import tqdm

# ─── Konfigurasi ──────────────────────────────────────────────────────────────
OUTPUT_DIR = "data/raw/cuaca_per_kabupaten"
OUTPUT_COMBINED = "data/raw/cuaca_jabar_2019_2024.csv"
START_DATE = "2019-01-01"
END_DATE   = "2024-12-31"

# ─── Daftar koordinat pusat tiap kabupaten/kota di Jawa Barat ─────────────────
# Sumber koordinat: BPS Jawa Barat + Google Maps centroid
# KABUPATEN_JABAR = [
#     # (nama,                    latitude,   longitude)
#     ("Kab. Bogor",              -6.5971,    106.8060),
#     ("Kab. Sukabumi",           -7.0051,    106.9264),
#     ("Kab. Cianjur",            -6.8200,    107.1400),
#     ("Kab. Bandung",            -7.0400,    107.5900),
#     ("Kab. Garut",              -7.2300,    107.9000),
#     ("Kab. Tasikmalaya",        -7.3500,    108.2500),
#     ("Kab. Ciamis",             -7.3300,    108.3500),
#     ("Kab. Kuningan",           -6.9800,    108.4800),
#     ("Kab. Cirebon",            -6.7600,    108.5500),
#     ("Kab. Majalengka",         -6.8400,    108.2300),
#     ("Kab. Sumedang",           -6.8500,    107.9200),
#     ("Kab. Indramayu",          -6.3300,    108.3200),
#     ("Kab. Subang",             -6.5700,    107.7600),
#     ("Kab. Purwakarta",         -6.5500,    107.4400),
#     ("Kab. Karawang",           -6.3200,    107.3400),
#     ("Kab. Bekasi",             -6.3700,    107.1400),
#     ("Kab. Bandung Barat",      -6.8400,    107.4500),
#     ("Kab. Pangandaran",        -7.6800,    108.6500),
#     ("Kota Bogor",              -6.5971,    106.8060),
#     ("Kota Sukabumi",           -6.9200,    106.9300),
#     ("Kota Bandung",            -6.9175,    107.6191),
#     ("Kota Cirebon",            -6.7320,    108.5523),
#     ("Kota Bekasi",             -6.2349,    106.9896),
#     ("Kota Depok",              -6.4025,    106.7942),
#     ("Kota Cimahi",             -6.8720,    107.5420),
#     ("Kota Tasikmalaya",        -7.3274,    108.2207),
#     ("Kota Banjar",             -7.3650,    108.5400),
# ]

# Karena di scraping pertama gagal, maka mengambil data yang gagal saja
KABUPATEN_JABAR = [
    # ("Kab. Kuningan",       -6.9800,  108.4800),
    # ("Kab. Cirebon",        -6.7600,  108.5500),
    # ("Kab. Sumedang",       -6.8500,  107.9200),
    # ("Kab. Indramayu",      -6.3300,  108.3200),
    # ("Kab. Subang",         -6.5700,  107.7600),
    # ("Kab. Purwakarta",     -6.5500,  107.4400),
    # ("Kab. Karawang",       -6.3200,  107.3400),
    # ("Kab. Bekasi",         -6.3700,  107.1400),
    # ("Kab. Bandung Barat",  -6.8400,  107.4500),
    ("Kab. Pangandaran",    -7.6800,  108.6500),
    # ("Kota Bogor",          -6.5971,  106.8060),
    ("Kota Sukabumi",       -6.9200,  106.9300),
    # ("Kota Bandung",        -6.9175,  107.6191),
]

# ─── Variabel cuaca yang diambil ──────────────────────────────────────────────
# Dokumentasi lengkap: https://open-meteo.com/en/docs/historical-weather-api
DAILY_VARIABLES = [
    "temperature_2m_max",        # Suhu maksimum harian (°C)
    "temperature_2m_min",        # Suhu minimum harian (°C)
    "temperature_2m_mean",       # Suhu rata-rata harian (°C)
    "precipitation_sum",         # Total curah hujan harian (mm)
    "rain_sum",                  # Total hujan (bukan salju) harian (mm)
    "precipitation_hours",       # Jam hujan per hari
    "windspeed_10m_max",         # Kecepatan angin maksimum (km/h)
    "shortwave_radiation_sum",   # Total radiasi matahari (MJ/m²)
    "et0_fao_evapotranspiration",# Evapotranspirasi referensi FAO (mm)
    "relative_humidity_2m_max",  # Kelembaban udara maksimum (%)
    "relative_humidity_2m_min",  # Kelembaban udara minimum (%)
]

# ─── Fungsi utama pengambilan data ────────────────────────────────────────────
def fetch_cuaca(nama: str, lat: float, lon: float,
                start: str, end: str) -> pd.DataFrame | None:
    """
    Mengambil data cuaca historis dari Open-Meteo untuk satu lokasi.
    
    Returns DataFrame dengan kolom: date, semua variabel cuaca, + metadata lokasi
    Returns None jika request gagal
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude":  lat,
        "longitude": lon,
        "start_date": start,
        "end_date":   end,
        "daily":      ",".join(DAILY_VARIABLES),
        "timezone":   "Asia/Jakarta",
        # Model ERA5 — konsisten dan tersedia sejak 1940
        # Untuk akurasi lebih tinggi 2021+, ganti ke "best_match"
        "models":     "era5",
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Bangun DataFrame dari response
        daily = data["daily"]
        df = pd.DataFrame(daily)
        df.rename(columns={"time": "date"}, inplace=True)
        df["date"] = pd.to_datetime(df["date"])

        # Tambahkan metadata lokasi
        df.insert(0, "nama_kabupaten", nama)
        df.insert(1, "latitude",  lat)
        df.insert(2, "longitude", lon)

        # Hitung fitur turunan yang berguna untuk ML
        df["temp_range"] = df["temperature_2m_max"] - df["temperature_2m_min"]
        df["humidity_mean"] = (
            df["relative_humidity_2m_max"] + df["relative_humidity_2m_min"]
        ) / 2
        # Indeks kekeringan sederhana: rasio curah hujan vs evapotranspirasi
        # Nilai < 1 = defisit air, nilai > 1 = surplus air
        df["drought_index"] = df["rain_sum"] / (
            df["et0_fao_evapotranspiration"].replace(0, 0.001)
        )

        return df

    except requests.exceptions.Timeout:
        print(f"  [TIMEOUT] {nama} — coba lagi nanti")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"  [HTTP ERROR] {nama}: {e}")
        return None
    except Exception as e:
        print(f"  [ERROR] {nama}: {e}")
        return None


def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agregasi data harian ke bulanan — lebih berguna untuk model ML
    karena prediksi panen berbasis musim, bukan harian.
    """
    df["year"]  = df["date"].dt.year
    df["month"] = df["date"].dt.month

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    exclude = ["latitude", "longitude", "year", "month"]
    agg_cols = [c for c in numeric_cols if c not in exclude]

    # Pilih fungsi agregasi per kolom
    agg_funcs = {}
    for col in agg_cols:
        if "sum" in col or "precipitation" in col or "rain" in col:
            agg_funcs[col] = "sum"    # akumulasi untuk variabel presipitasi
        elif "hours" in col:
            agg_funcs[col] = "sum"
        else:
            agg_funcs[col] = "mean"   # rata-rata untuk suhu, kelembaban, dll

    monthly = (
        df.groupby(["nama_kabupaten", "latitude", "longitude", "year", "month"])
        .agg(agg_funcs)
        .reset_index()
    )
    monthly.rename(
        columns={c: f"{c}_monthly_{agg_funcs[c]}" for c in agg_cols},
        inplace=True
    )

    # Tambahkan kolom tanggal untuk kemudahan plotting
    monthly["date"] = pd.to_datetime(
        monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2) + "-01"
    )

    return monthly


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)

    all_daily   = []
    all_monthly = []
    failed      = []

    print(f"Mengambil data cuaca {START_DATE} s/d {END_DATE}")
    print(f"Total lokasi: {len(KABUPATEN_JABAR)} kabupaten/kota Jawa Barat\n")

    for nama, lat, lon in tqdm(KABUPATEN_JABAR, desc="Kabupaten"):
        df_daily = fetch_cuaca(nama, lat, lon, START_DATE, END_DATE)

        if df_daily is None:
            failed.append(nama)
            continue

        # Simpan per kabupaten
        safe_name = nama.replace(" ", "_").replace(".", "")
        path_kabupaten = os.path.join(OUTPUT_DIR, f"cuaca_{safe_name}.csv")
        df_daily.to_csv(path_kabupaten, index=False)

        # Agregasi ke bulanan
        df_monthly = aggregate_monthly(df_daily)

        all_daily.append(df_daily)
        all_monthly.append(df_monthly)

        # Jeda 0.5 detik agar tidak flood API (rate limit Open-Meteo: ~10k req/day free)
        time.sleep(3)

    # Gabungkan semua kabupaten
    if all_daily:
        df_combined_daily = pd.concat(all_daily, ignore_index=True)
        df_combined_daily.to_csv(OUTPUT_COMBINED, index=False)

        df_combined_monthly = pd.concat(all_monthly, ignore_index=True)
        df_combined_monthly.to_csv(
            OUTPUT_COMBINED.replace(".csv", "_monthly.csv"), index=False
        )

        print(f"\n✓ Data harian    : {len(df_combined_daily):,} baris "
              f"→ {OUTPUT_COMBINED}")
        print(f"✓ Data bulanan   : {len(df_combined_monthly):,} baris "
              f"→ {OUTPUT_COMBINED.replace('.csv', '_monthly.csv')}")

    if failed:
        print(f"\n✗ Gagal diambil ({len(failed)} lokasi): {', '.join(failed)}")
        print("  Jalankan ulang script untuk retry lokasi yang gagal.")

    # ── Preview struktur output ──
    print("\n── Contoh struktur data harian (5 baris pertama Bandung) ──")
    sample = pd.read_csv(OUTPUT_COMBINED)
    bandung = sample[sample["nama_kabupaten"] == "Kota Bandung"].head()
    print(bandung[["date", "nama_kabupaten",
                   "temperature_2m_mean", "precipitation_sum",
                   "drought_index", "shortwave_radiation_sum"]].to_string(index=False))


if __name__ == "__main__":
    main()
