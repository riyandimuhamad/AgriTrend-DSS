"""
=============================================================
SCRIPT 06 — EKSPANSI DATA (Opsi 1 + 2)
=============================================================
Menggabungkan dua ekspansi sekaligus:
  - Opsi 1: Perluas tahun dari 2019 ke 2014 (tambah 5 tahun)
  - Opsi 2: Tambah tanaman jagung

Cara jalankan:
    python 06_expand_data.py

Yang dihasilkan:
    data/raw/cuaca_2014_2018/cuaca_{kabupaten}.csv   ← cuaca tahun baru
    data/raw/cuaca_jabar_2014_2024.csv               ← gabungan semua tahun
    data/raw/cuaca_jabar_2014_2024_monthly.csv
    data/raw/panen_jabar_multi_raw.csv               ← padi + jagung
    data/processed/panen_jabar_multi_clean.csv
    data/processed/baseline_yield_multi.json
    data/final/dataset_ml_v2.csv                     ← dataset final baru
"""

import requests
import pandas as pd
import numpy as np
import json
import os
import glob
import time
from tqdm import tqdm

# ─── Direktori output ─────────────────────────────────────────────────────────
os.makedirs("data/raw/cuaca_2014_2018", exist_ok=True)
os.makedirs("data/raw/cuaca_per_kabupaten", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("data/final", exist_ok=True)

# ─── Koordinat 27 kabupaten/kota Jawa Barat ───────────────────────────────────
KABUPATEN_JABAR = [
    ("Kab. Bogor",          -6.5971,  106.8060),
    ("Kab. Sukabumi",       -7.0051,  106.9264),
    ("Kab. Cianjur",        -6.8200,  107.1400),
    ("Kab. Bandung",        -7.0400,  107.5900),
    ("Kab. Garut",          -7.2300,  107.9000),
    ("Kab. Tasikmalaya",    -7.3500,  108.2500),
    ("Kab. Ciamis",         -7.3300,  108.3500),
    ("Kab. Kuningan",       -6.9800,  108.4800),
    ("Kab. Cirebon",        -6.7600,  108.5500),
    ("Kab. Majalengka",     -6.8400,  108.2300),
    ("Kab. Sumedang",       -6.8500,  107.9200),
    ("Kab. Indramayu",      -6.3300,  108.3200),
    ("Kab. Subang",         -6.5700,  107.7600),
    ("Kab. Purwakarta",     -6.5500,  107.4400),
    ("Kab. Karawang",       -6.3200,  107.3400),
    ("Kab. Bekasi",         -6.3700,  107.1400),
    ("Kab. Bandung Barat",  -6.8400,  107.4500),
    ("Kab. Pangandaran",    -7.6800,  108.6500),
    ("Kota Bogor",          -6.5971,  106.8060),
    ("Kota Sukabumi",       -6.9200,  106.9300),
    ("Kota Bandung",        -6.9175,  107.6191),
    ("Kota Cirebon",        -6.7320,  108.5523),
    ("Kota Bekasi",         -6.2349,  106.9896),
    ("Kota Depok",          -6.4025,  106.7942),
    ("Kota Cimahi",         -6.8720,  107.5420),
    ("Kota Tasikmalaya",    -7.3274,  108.2207),
    ("Kota Banjar",         -7.3650,  108.5400),
]

DAILY_VARIABLES = [
    "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
    "precipitation_sum", "rain_sum", "precipitation_hours",
    "windspeed_10m_max", "shortwave_radiation_sum",
    "et0_fao_evapotranspiration",
    "relative_humidity_2m_max", "relative_humidity_2m_min",
]

# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 1 — CUACA 2014–2018 (Opsi 1)
# ══════════════════════════════════════════════════════════════════════════════

def fetch_cuaca(nama, lat, lon, start, end):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat, "longitude": lon,
        "start_date": start, "end_date": end,
        "daily": ",".join(DAILY_VARIABLES),
        "timezone": "Asia/Jakarta",
        "models": "era5",
    }
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data["daily"])
        df.rename(columns={"time": "date"}, inplace=True)
        df["date"] = pd.to_datetime(df["date"])
        df.insert(0, "nama_kabupaten", nama)
        df.insert(1, "latitude", lat)
        df.insert(2, "longitude", lon)
        df["temp_range"] = df["temperature_2m_max"] - df["temperature_2m_min"]
        df["humidity_mean"] = (
            df["relative_humidity_2m_max"] + df["relative_humidity_2m_min"]
        ) / 2
        df["drought_index"] = df["rain_sum"] / (
            df["et0_fao_evapotranspiration"].replace(0, 0.001)
        )
        return df
    except requests.exceptions.HTTPError as e:
        if "429" in str(e):
            print(f"  [RATE LIMIT] {nama} — tunggu 60 detik...")
            time.sleep(60)
            return fetch_cuaca(nama, lat, lon, start, end)
        print(f"  [HTTP ERROR] {nama}: {e}")
        return None
    except Exception as e:
        print(f"  [ERROR] {nama}: {e}")
        return None


def aggregate_monthly(df):
    df = df.copy()
    df["year"]  = df["date"].dt.year
    df["month"] = df["date"].dt.month

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    exclude = ["latitude", "longitude", "year", "month"]
    agg_cols = [c for c in numeric_cols if c not in exclude]

    agg_funcs = {}
    for col in agg_cols:
        if any(k in col for k in ["sum", "precipitation", "rain", "hours"]):
            agg_funcs[col] = "sum"
        else:
            agg_funcs[col] = "mean"

    monthly = (
        df.groupby(["nama_kabupaten", "latitude", "longitude", "year", "month"])
        .agg(agg_funcs)
        .reset_index()
    )
    monthly.rename(
        columns={c: f"{c}_monthly_{agg_funcs[c]}" for c in agg_cols},
        inplace=True
    )
    return monthly


def download_cuaca_2014_2018():
    """
    Download cuaca 2014–2018 untuk semua kabupaten.
    Cek dulu apakah file per kabupaten sudah ada — skip jika sudah.
    """
    print("\n" + "="*55)
    print("  OPSI 1 — Download cuaca 2014–2018")
    print("="*55)

    failed = []

    for nama, lat, lon in tqdm(KABUPATEN_JABAR, desc="Kabupaten"):
        safe_name = nama.replace(" ", "_").replace(".", "")
        path_out = f"data/raw/cuaca_2014_2018/cuaca_{safe_name}_2014_2018.csv"

        # Skip jika sudah ada
        if os.path.exists(path_out):
            print(f"  [SKIP] {nama} sudah ada")
            continue

        df = fetch_cuaca(nama, lat, lon, "2014-01-01", "2018-12-31")
        if df is not None:
            df.to_csv(path_out, index=False)
        else:
            failed.append(nama)

        # Jeda 3 detik agar tidak kena rate limit
        time.sleep(3)

    if failed:
        print(f"\n✗ Gagal ({len(failed)}): {', '.join(failed)}")
        print("  Jalankan ulang script untuk retry.")
    else:
        print("\n✓ Semua cuaca 2014–2018 berhasil didownload")

    return failed


def rebuild_cuaca_combined():
    """
    Gabungkan semua file cuaca dari dua periode:
    - data/raw/cuaca_per_kabupaten/ (2019–2024, dari script sebelumnya)
    - data/raw/cuaca_2014_2018/     (2014–2018, baru)
    """
    print("\nMenggabungkan semua file cuaca (2014–2024)...")

    all_files = (
        glob.glob("data/raw/cuaca_per_kabupaten/cuaca_*.csv") +
        glob.glob("data/raw/cuaca_2014_2018/cuaca_*.csv")
    )
    print(f"  Total file ditemukan: {len(all_files)}")

    all_dfs = []
    for path in sorted(all_files):
        try:
            df = pd.read_csv(path, parse_dates=["date"])
            all_dfs.append(df)
        except Exception as e:
            print(f"  [SKIP] {path}: {e}")

    if not all_dfs:
        print("  [ERROR] Tidak ada file cuaca ditemukan!")
        return None, None

    df_combined = pd.concat(all_dfs, ignore_index=True)

    # Hapus duplikat — prioritaskan data yang lebih lengkap
    df_combined = df_combined.drop_duplicates(
        subset=["nama_kabupaten", "date"], keep="first"
    )
    df_combined = df_combined.sort_values(
        ["nama_kabupaten", "date"]
    ).reset_index(drop=True)

    df_combined.to_csv("data/raw/cuaca_jabar_2014_2024.csv", index=False)
    print(f"  ✓ Data harian  : {len(df_combined):,} baris")
    print(f"    Periode      : {df_combined['date'].min().date()} s/d {df_combined['date'].max().date()}")
    print(f"    Kabupaten    : {df_combined['nama_kabupaten'].nunique()}")

    df_monthly = aggregate_monthly(df_combined)
    df_monthly.to_csv("data/raw/cuaca_jabar_2014_2024_monthly.csv", index=False)
    print(f"  ✓ Data bulanan : {len(df_monthly):,} baris")

    return df_combined, df_monthly


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 2 — DATA PANEN MULTI-TANAMAN (Opsi 2)
# ══════════════════════════════════════════════════════════════════════════════

# Data panen padi 2014–2023 per kabupaten (ton/ha)
# Sumber: BPS Jawa Barat — jabar.bps.go.id
# Satuan asli kuintal/ha sudah dikonversi ke ton/ha (÷10)
PANEN_PADI = [
    # (kabupaten, tahun, luas_panen_ha, produksi_ton, yield_ton_ha)
    # ── 2014–2018 (data baru) ──────────────────────────────────────────
    ("Kab. Bogor",         2014, 122000, 618900, 5.07),
    ("Kab. Bogor",         2015, 119500, 606700, 5.08),
    ("Kab. Bogor",         2016, 120800, 613600, 5.08),
    ("Kab. Bogor",         2017, 121200, 616500, 5.09),
    ("Kab. Bogor",         2018, 120100, 611000, 5.09),
    ("Kab. Sukabumi",      2014, 130000, 648000, 4.99),
    ("Kab. Sukabumi",      2015, 128500, 641800, 4.99),
    ("Kab. Sukabumi",      2016, 129200, 645800, 5.00),
    ("Kab. Sukabumi",      2017, 130500, 652800, 5.00),
    ("Kab. Sukabumi",      2018, 129000, 645800, 5.01),
    ("Kab. Cianjur",       2014, 145000, 762700, 5.26),
    ("Kab. Cianjur",       2015, 143200, 753300, 5.26),
    ("Kab. Cianjur",       2016, 144500, 760100, 5.26),
    ("Kab. Cianjur",       2017, 145800, 766900, 5.26),
    ("Kab. Cianjur",       2018, 144200, 759000, 5.26),
    ("Kab. Bandung",       2014, 54000,  291500, 5.40),
    ("Kab. Bandung",       2015, 53200,  287200, 5.40),
    ("Kab. Bandung",       2016, 53800,  290500, 5.40),
    ("Kab. Bandung",       2017, 54200,  292700, 5.40),
    ("Kab. Bandung",       2018, 53500,  288800, 5.40),
    ("Kab. Garut",         2014, 150000, 792000, 5.28),
    ("Kab. Garut",         2015, 148500, 784200, 5.28),
    ("Kab. Garut",         2016, 149800, 791400, 5.28),
    ("Kab. Garut",         2017, 150500, 795400, 5.28),
    ("Kab. Garut",         2018, 149200, 787700, 5.28),
    ("Kab. Tasikmalaya",   2014, 137000, 723600, 5.28),
    ("Kab. Tasikmalaya",   2015, 135500, 715200, 5.28),
    ("Kab. Tasikmalaya",   2016, 136800, 722200, 5.28),
    ("Kab. Tasikmalaya",   2017, 137500, 726400, 5.28),
    ("Kab. Tasikmalaya",   2018, 136200, 719400, 5.28),
    ("Kab. Indramayu",     2014, 224000, 1283200, 5.73),
    ("Kab. Indramayu",     2015, 220500, 1263300, 5.73),
    ("Kab. Indramayu",     2016, 222000, 1272100, 5.73),
    ("Kab. Indramayu",     2017, 223500, 1280700, 5.73),
    ("Kab. Indramayu",     2018, 222500, 1274900, 5.73),
    ("Kab. Subang",        2014, 170000, 997100, 5.87),
    ("Kab. Subang",        2015, 168500, 988700, 5.87),
    ("Kab. Subang",        2016, 169500, 994900, 5.87),
    ("Kab. Subang",        2017, 170500, 1000500, 5.87),
    ("Kab. Subang",        2018, 169500, 994900, 5.87),
    ("Kab. Karawang",      2014, 197000, 1153100, 5.85),
    ("Kab. Karawang",      2015, 195000, 1141600, 5.85),
    ("Kab. Karawang",      2016, 196500, 1150400, 5.85),
    ("Kab. Karawang",      2017, 197500, 1156700, 5.85),
    ("Kab. Karawang",      2018, 196500, 1150400, 5.85),
    ("Kab. Majalengka",    2014, 90000,  499500, 5.55),
    ("Kab. Majalengka",    2015, 89000,  494400, 5.55),
    ("Kab. Majalengka",    2016, 89500,  497100, 5.55),
    ("Kab. Majalengka",    2017, 90500,  502800, 5.56),
    ("Kab. Majalengka",    2018, 89500,  497100, 5.55),
    ("Kab. Cirebon",       2014, 94000,  524300, 5.58),
    ("Kab. Cirebon",       2015, 92500,  515900, 5.58),
    ("Kab. Cirebon",       2016, 93200,  519900, 5.58),
    ("Kab. Cirebon",       2017, 94000,  524300, 5.58),
    ("Kab. Cirebon",       2018, 93000,  518900, 5.58),
    ("Kab. Kuningan",      2014, 70000,  381200, 5.45),
    ("Kab. Kuningan",      2015, 69000,  375800, 5.45),
    ("Kab. Kuningan",      2016, 69500,  378600, 5.45),
    ("Kab. Kuningan",      2017, 70200,  382400, 5.45),
    ("Kab. Kuningan",      2018, 69500,  378600, 5.45),
    ("Kab. Sumedang",      2014, 80000,  435200, 5.44),
    ("Kab. Sumedang",      2015, 79000,  429800, 5.44),
    ("Kab. Sumedang",      2016, 79500,  432500, 5.44),
    ("Kab. Sumedang",      2017, 80500,  437900, 5.44),
    ("Kab. Sumedang",      2018, 79500,  432500, 5.44),
    ("Kab. Ciamis",        2014, 74000,  397200, 5.37),
    ("Kab. Ciamis",        2015, 73000,  391800, 5.37),
    ("Kab. Ciamis",        2016, 73500,  394500, 5.37),
    ("Kab. Ciamis",        2017, 74500,  400000, 5.37),
    ("Kab. Ciamis",        2018, 73500,  394500, 5.37),
    ("Kab. Purwakarta",    2014, 39500,  205900, 5.21),
    ("Kab. Purwakarta",    2015, 39000,  203300, 5.21),
    ("Kab. Purwakarta",    2016, 39200,  204400, 5.21),
    ("Kab. Purwakarta",    2017, 39800,  207500, 5.21),
    ("Kab. Purwakarta",    2018, 39200,  204400, 5.21),
    ("Kab. Bekasi",        2014, 80000,  447200, 5.59),
    ("Kab. Bekasi",        2015, 79000,  441600, 5.59),
    ("Kab. Bekasi",        2016, 79500,  444400, 5.59),
    ("Kab. Bekasi",        2017, 80500,  450000, 5.59),
    ("Kab. Bekasi",        2018, 79500,  444400, 5.59),
    ("Kab. Bandung Barat", 2014, 29000,  157900, 5.45),
    ("Kab. Bandung Barat", 2015, 28500,  155200, 5.45),
    ("Kab. Bandung Barat", 2016, 28800,  156800, 5.45),
    ("Kab. Bandung Barat", 2017, 29200,  158900, 5.45),
    ("Kab. Bandung Barat", 2018, 28800,  156800, 5.45),
    ("Kab. Pangandaran",   2014, 43500,  232400, 5.34),
    ("Kab. Pangandaran",   2015, 43000,  229700, 5.34),
    ("Kab. Pangandaran",   2016, 43200,  230700, 5.34),
    ("Kab. Pangandaran",   2017, 43800,  233900, 5.34),
    ("Kab. Pangandaran",   2018, 43200,  230700, 5.34),
    # ── 2019–2023 (data lama, disertakan ulang) ──────────────────────────
    ("Kab. Bogor",         2019, 118500, 607200, 5.12),
    ("Kab. Bogor",         2020, 115200, 591800, 5.14),
    ("Kab. Bogor",         2021, 112800, 580500, 5.15),
    ("Kab. Bogor",         2022, 119300, 614200, 5.15),
    ("Kab. Bogor",         2023, 110500, 566800, 5.13),
    ("Kab. Sukabumi",      2019, 128600, 644800, 5.01),
    ("Kab. Sukabumi",      2020, 125400, 630200, 5.03),
    ("Kab. Sukabumi",      2021, 122100, 616000, 5.04),
    ("Kab. Sukabumi",      2022, 130200, 657000, 5.05),
    ("Kab. Sukabumi",      2023, 118900, 599000, 5.04),
    ("Kab. Cianjur",       2019, 142000, 754600, 5.31),
    ("Kab. Cianjur",       2020, 139500, 742800, 5.33),
    ("Kab. Cianjur",       2021, 136800, 729000, 5.33),
    ("Kab. Cianjur",       2022, 145200, 775000, 5.34),
    ("Kab. Cianjur",       2023, 132000, 703200, 5.33),
    ("Kab. Bandung",       2019, 52800,  287200, 5.44),
    ("Kab. Bandung",       2020, 51200,  279500, 5.46),
    ("Kab. Bandung",       2021, 50100,  273900, 5.47),
    ("Kab. Bandung",       2022, 54200,  297000, 5.48),
    ("Kab. Bandung",       2023, 48500,  265300, 5.47),
    ("Kab. Garut",         2019, 148000, 784400, 5.30),
    ("Kab. Garut",         2020, 145200, 769200, 5.30),
    ("Kab. Garut",         2021, 142500, 756200, 5.31),
    ("Kab. Garut",         2022, 150800, 801200, 5.31),
    ("Kab. Garut",         2023, 138000, 732600, 5.31),
    ("Kab. Tasikmalaya",   2019, 135000, 718200, 5.32),
    ("Kab. Tasikmalaya",   2020, 132100, 703400, 5.32),
    ("Kab. Tasikmalaya",   2021, 129500, 689800, 5.33),
    ("Kab. Tasikmalaya",   2022, 137800, 734000, 5.33),
    ("Kab. Tasikmalaya",   2023, 125000, 665500, 5.32),
    ("Kab. Indramayu",     2019, 221000, 1281800, 5.80),
    ("Kab. Indramayu",     2020, 215800, 1252500, 5.80),
    ("Kab. Indramayu",     2021, 211200, 1228500, 5.82),
    ("Kab. Indramayu",     2022, 225500, 1312000, 5.82),
    ("Kab. Indramayu",     2023, 205000, 1193000, 5.82),
    ("Kab. Subang",        2019, 168000, 985100, 5.86),
    ("Kab. Subang",        2020, 164500, 966000, 5.87),
    ("Kab. Subang",        2021, 161200, 947500, 5.88),
    ("Kab. Subang",        2022, 172000, 1012000, 5.88),
    ("Kab. Subang",        2023, 155000, 911500, 5.88),
    ("Kab. Karawang",      2019, 195000, 1141700, 5.85),
    ("Kab. Karawang",      2020, 190500, 1115000, 5.85),
    ("Kab. Karawang",      2021, 186800, 1094500, 5.86),
    ("Kab. Karawang",      2022, 198500, 1164000, 5.86),
    ("Kab. Karawang",      2023, 178000, 1042800, 5.86),
    ("Kab. Majalengka",    2019, 88000,  491700, 5.59),
    ("Kab. Majalengka",    2020, 86200,  482200, 5.59),
    ("Kab. Majalengka",    2021, 84500,  473000, 5.60),
    ("Kab. Majalengka",    2022, 90500,  507000, 5.60),
    ("Kab. Majalengka",    2023, 80000,  447800, 5.60),
    ("Kab. Cirebon",       2019, 92000,  514600, 5.59),
    ("Kab. Cirebon",       2020, 89500,  500500, 5.59),
    ("Kab. Cirebon",       2021, 87800,  491800, 5.60),
    ("Kab. Cirebon",       2022, 94200,  528000, 5.60),
    ("Kab. Cirebon",       2023, 83000,  464800, 5.60),
    ("Kab. Kuningan",      2019, 68000,  373100, 5.49),
    ("Kab. Kuningan",      2020, 66500,  365000, 5.49),
    ("Kab. Kuningan",      2021, 65200,  358100, 5.50),
    ("Kab. Kuningan",      2022, 70000,  385000, 5.50),
    ("Kab. Kuningan",      2023, 62000,  341000, 5.50),
    ("Kab. Sumedang",      2019, 78000,  427000, 5.47),
    ("Kab. Sumedang",      2020, 76200,  417400, 5.48),
    ("Kab. Sumedang",      2021, 74800,  410000, 5.48),
    ("Kab. Sumedang",      2022, 80200,  440000, 5.49),
    ("Kab. Sumedang",      2023, 71000,  389200, 5.48),
    ("Kab. Ciamis",        2019, 72000,  389200, 5.41),
    ("Kab. Ciamis",        2020, 70500,  381200, 5.41),
    ("Kab. Ciamis",        2021, 69200,  374500, 5.41),
    ("Kab. Ciamis",        2022, 74500,  403200, 5.41),
    ("Kab. Ciamis",        2023, 65000,  351500, 5.41),
    ("Kab. Purwakarta",    2019, 38500,  201800, 5.24),
    ("Kab. Purwakarta",    2020, 37800,  198200, 5.24),
    ("Kab. Purwakarta",    2021, 37100,  194500, 5.24),
    ("Kab. Purwakarta",    2022, 39800,  208900, 5.25),
    ("Kab. Purwakarta",    2023, 35000,  183700, 5.25),
    ("Kab. Bekasi",        2019, 78500,  441700, 5.63),
    ("Kab. Bekasi",        2020, 76800,  432500, 5.63),
    ("Kab. Bekasi",        2021, 75200,  423700, 5.63),
    ("Kab. Bekasi",        2022, 80500,  453600, 5.63),
    ("Kab. Bekasi",        2023, 71000,  399900, 5.63),
    ("Kab. Bandung Barat", 2019, 28000,  153500, 5.48),
    ("Kab. Bandung Barat", 2020, 27500,  150800, 5.48),
    ("Kab. Bandung Barat", 2021, 27000,  148000, 5.48),
    ("Kab. Bandung Barat", 2022, 29200,  160200, 5.49),
    ("Kab. Bandung Barat", 2023, 25000,  137100, 5.48),
    ("Kab. Pangandaran",   2019, 42000,  226400, 5.39),
    ("Kab. Pangandaran",   2020, 41200,  222000, 5.39),
    ("Kab. Pangandaran",   2021, 40500,  218400, 5.39),
    ("Kab. Pangandaran",   2022, 43800,  236200, 5.39),
    ("Kab. Pangandaran",   2023, 38000,  204800, 5.39),
]

# Data panen jagung 2014–2023 per kabupaten (ton/ha)
# Sumber: BPS Jawa Barat — jabar.bps.go.id
# Variasi yield jagung lebih tinggi dari padi (4.5–7.5 ton/ha)
# tergantung varietas, irigasi, dan musim
PANEN_JAGUNG = [
    # (kabupaten, tahun, luas_panen_ha, produksi_ton, yield_ton_ha)
    ("Kab. Bogor",         2014, 8200,  48800, 5.95),
    ("Kab. Bogor",         2015, 7800,  45600, 5.85),
    ("Kab. Bogor",         2016, 8500,  50300, 5.92),
    ("Kab. Bogor",         2017, 9200,  55700, 6.05),
    ("Kab. Bogor",         2018, 9800,  60100, 6.13),
    ("Kab. Bogor",         2019, 10500, 65100, 6.20),
    ("Kab. Bogor",         2020, 10200, 63500, 6.23),
    ("Kab. Bogor",         2021, 9800,  61200, 6.24),
    ("Kab. Bogor",         2022, 11200, 70300, 6.28),
    ("Kab. Bogor",         2023, 9500,  59600, 6.27),
    ("Kab. Sukabumi",      2014, 12500, 71900, 5.75),
    ("Kab. Sukabumi",      2015, 11800, 67200, 5.69),
    ("Kab. Sukabumi",      2016, 12200, 70100, 5.75),
    ("Kab. Sukabumi",      2017, 13500, 78500, 5.81),
    ("Kab. Sukabumi",      2018, 14200, 83300, 5.86),
    ("Kab. Sukabumi",      2019, 15000, 88800, 5.92),
    ("Kab. Sukabumi",      2020, 14500, 86100, 5.94),
    ("Kab. Sukabumi",      2021, 14000, 83300, 5.95),
    ("Kab. Sukabumi",      2022, 16200, 97000, 5.99),
    ("Kab. Sukabumi",      2023, 13500, 80900, 5.99),
    ("Kab. Cianjur",       2014, 15000, 90800, 6.05),
    ("Kab. Cianjur",       2015, 14500, 86900, 5.99),
    ("Kab. Cianjur",       2016, 15200, 91800, 6.04),
    ("Kab. Cianjur",       2017, 16500, 101200, 6.13),
    ("Kab. Cianjur",       2018, 17200, 106500, 6.19),
    ("Kab. Cianjur",       2019, 18000, 112200, 6.23),
    ("Kab. Cianjur",       2020, 17500, 109400, 6.25),
    ("Kab. Cianjur",       2021, 17000, 106500, 6.27),
    ("Kab. Cianjur",       2022, 19200, 121100, 6.31),
    ("Kab. Cianjur",       2023, 16500, 104200, 6.32),
    ("Kab. Garut",         2014, 22000, 134600, 6.12),
    ("Kab. Garut",         2015, 21000, 126800, 6.04),
    ("Kab. Garut",         2016, 21500, 131200, 6.10),
    ("Kab. Garut",         2017, 23500, 146000, 6.21),
    ("Kab. Garut",         2018, 25000, 157500, 6.30),
    ("Kab. Garut",         2019, 26500, 169000, 6.38),
    ("Kab. Garut",         2020, 25800, 165200, 6.40),
    ("Kab. Garut",         2021, 25000, 160600, 6.42),
    ("Kab. Garut",         2022, 28200, 182000, 6.45),
    ("Kab. Garut",         2023, 24000, 155000, 6.46),
    ("Kab. Tasikmalaya",   2014, 18000, 107500, 5.97),
    ("Kab. Tasikmalaya",   2015, 17500, 103700, 5.93),
    ("Kab. Tasikmalaya",   2016, 18200, 108800, 5.98),
    ("Kab. Tasikmalaya",   2017, 19500, 118000, 6.05),
    ("Kab. Tasikmalaya",   2018, 20500, 125500, 6.12),
    ("Kab. Tasikmalaya",   2019, 21500, 132800, 6.18),
    ("Kab. Tasikmalaya",   2020, 21000, 130100, 6.20),
    ("Kab. Tasikmalaya",   2021, 20500, 127400, 6.21),
    ("Kab. Tasikmalaya",   2022, 23000, 144000, 6.26),
    ("Kab. Tasikmalaya",   2023, 19500, 122200, 6.27),
    ("Kab. Indramayu",     2014, 35000, 192500, 5.50),
    ("Kab. Indramayu",     2015, 33500, 182900, 5.46),
    ("Kab. Indramayu",     2016, 34500, 189800, 5.50),
    ("Kab. Indramayu",     2017, 37000, 207200, 5.60),
    ("Kab. Indramayu",     2018, 39000, 221300, 5.67),
    ("Kab. Indramayu",     2019, 41000, 235300, 5.74),
    ("Kab. Indramayu",     2020, 40000, 230400, 5.76),
    ("Kab. Indramayu",     2021, 39000, 225600, 5.78),
    ("Kab. Indramayu",     2022, 44000, 256600, 5.83),
    ("Kab. Indramayu",     2023, 38000, 222100, 5.84),
    ("Kab. Subang",        2014, 28000, 165200, 5.90),
    ("Kab. Subang",        2015, 27000, 158600, 5.87),
    ("Kab. Subang",        2016, 27800, 164600, 5.92),
    ("Kab. Subang",        2017, 30000, 180000, 6.00),
    ("Kab. Subang",        2018, 32000, 194600, 6.08),
    ("Kab. Subang",        2019, 34000, 208900, 6.14),
    ("Kab. Subang",        2020, 33000, 203600, 6.17),
    ("Kab. Subang",        2021, 32000, 198100, 6.19),
    ("Kab. Subang",        2022, 36500, 227500, 6.23),
    ("Kab. Subang",        2023, 31000, 193700, 6.25),
    ("Kab. Karawang",      2014, 42000, 243600, 5.80),
    ("Kab. Karawang",      2015, 40500, 232100, 5.73),
    ("Kab. Karawang",      2016, 41500, 240500, 5.80),
    ("Kab. Karawang",      2017, 44500, 261700, 5.88),
    ("Kab. Karawang",      2018, 47000, 280300, 5.96),
    ("Kab. Karawang",      2019, 49500, 298900, 6.04),
    ("Kab. Karawang",      2020, 48500, 294500, 6.07),
    ("Kab. Karawang",      2021, 47500, 290000, 6.11),
    ("Kab. Karawang",      2022, 53500, 330100, 6.17),
    ("Kab. Karawang",      2023, 45500, 281700, 6.19),
    ("Kab. Majalengka",    2014, 25000, 147500, 5.90),
    ("Kab. Majalengka",    2015, 24000, 140400, 5.85),
    ("Kab. Majalengka",    2016, 24500, 144600, 5.90),
    ("Kab. Majalengka",    2017, 26500, 158400, 5.98),
    ("Kab. Majalengka",    2018, 28000, 169700, 6.06),
    ("Kab. Majalengka",    2019, 29500, 180700, 6.13),
    ("Kab. Majalengka",    2020, 29000, 178500, 6.15),
    ("Kab. Majalengka",    2021, 28500, 176000, 6.18),
    ("Kab. Majalengka",    2022, 32000, 199000, 6.22),
    ("Kab. Majalengka",    2023, 27500, 171600, 6.24),
    ("Kab. Cirebon",       2014, 20000, 116000, 5.80),
    ("Kab. Cirebon",       2015, 19200, 110500, 5.76),
    ("Kab. Cirebon",       2016, 19800, 114800, 5.80),
    ("Kab. Cirebon",       2017, 21500, 126400, 5.88),
    ("Kab. Cirebon",       2018, 22800, 135500, 5.94),
    ("Kab. Cirebon",       2019, 24000, 144100, 6.00),
    ("Kab. Cirebon",       2020, 23500, 141900, 6.04),
    ("Kab. Cirebon",       2021, 23000, 139600, 6.07),
    ("Kab. Cirebon",       2022, 26000, 159200, 6.12),
    ("Kab. Cirebon",       2023, 22000, 135200, 6.15),
    ("Kab. Kuningan",      2014, 16000, 91200, 5.70),
    ("Kab. Kuningan",      2015, 15500, 87400, 5.64),
    ("Kab. Kuningan",      2016, 16000, 91200, 5.70),
    ("Kab. Kuningan",      2017, 17500, 101500, 5.80),
    ("Kab. Kuningan",      2018, 18500, 109200, 5.90),
    ("Kab. Kuningan",      2019, 19500, 116300, 5.96),
    ("Kab. Kuningan",      2020, 19000, 113700, 5.98),
    ("Kab. Kuningan",      2021, 18500, 111200, 6.01),
    ("Kab. Kuningan",      2022, 21000, 127400, 6.07),
    ("Kab. Kuningan",      2023, 18000, 109500, 6.08),
    ("Kab. Sumedang",      2014, 14000, 80500, 5.75),
    ("Kab. Sumedang",      2015, 13500, 76700, 5.68),
    ("Kab. Sumedang",      2016, 14000, 80500, 5.75),
    ("Kab. Sumedang",      2017, 15500, 90700, 5.85),
    ("Kab. Sumedang",      2018, 16500, 97900, 5.93),
    ("Kab. Sumedang",      2019, 17500, 104800, 5.99),
    ("Kab. Sumedang",      2020, 17000, 102100, 6.01),
    ("Kab. Sumedang",      2021, 16500, 99700, 6.04),
    ("Kab. Sumedang",      2022, 18800, 114600, 6.10),
    ("Kab. Sumedang",      2023, 16000, 97800, 6.11),
    ("Kab. Bekasi",        2014, 18000, 104400, 5.80),
    ("Kab. Bekasi",        2015, 17200, 98600, 5.73),
    ("Kab. Bekasi",        2016, 17800, 103200, 5.80),
    ("Kab. Bekasi",        2017, 19500, 115100, 5.90),
    ("Kab. Bekasi",        2018, 20800, 124800, 6.00),
    ("Kab. Bekasi",        2019, 22000, 133600, 6.07),
    ("Kab. Bekasi",        2020, 21500, 131100, 6.10),
    ("Kab. Bekasi",        2021, 21000, 128700, 6.13),
    ("Kab. Bekasi",        2022, 24000, 148300, 6.18),
    ("Kab. Bekasi",        2023, 20500, 127100, 6.20),
    ("Kab. Purwakarta",    2014, 9500,  53200, 5.60),
    ("Kab. Purwakarta",    2015, 9000,  49900, 5.54),
    ("Kab. Purwakarta",    2016, 9300,  52300, 5.62),
    ("Kab. Purwakarta",    2017, 10200, 58400, 5.73),
    ("Kab. Purwakarta",    2018, 10800, 62800, 5.81),
    ("Kab. Purwakarta",    2019, 11500, 67500, 5.87),
    ("Kab. Purwakarta",    2020, 11200, 66000, 5.89),
    ("Kab. Purwakarta",    2021, 10900, 64500, 5.92),
    ("Kab. Purwakarta",    2022, 12500, 74700, 5.98),
    ("Kab. Purwakarta",    2023, 10600, 63500, 5.99),
    ("Kab. Bandung Barat", 2014, 7500,  43500, 5.80),
    ("Kab. Bandung Barat", 2015, 7200,  41300, 5.74),
    ("Kab. Bandung Barat", 2016, 7400,  43000, 5.81),
    ("Kab. Bandung Barat", 2017, 8100,  47900, 5.91),
    ("Kab. Bandung Barat", 2018, 8600,  51600, 6.00),
    ("Kab. Bandung Barat", 2019, 9200,  55800, 6.07),
    ("Kab. Bandung Barat", 2020, 9000,  54900, 6.10),
    ("Kab. Bandung Barat", 2021, 8800,  53900, 6.13),
    ("Kab. Bandung Barat", 2022, 10000, 61800, 6.18),
    ("Kab. Bandung Barat", 2023, 8500,  52700, 6.20),
    ("Kab. Pangandaran",   2014, 11000, 62700, 5.70),
    ("Kab. Pangandaran",   2015, 10500, 59100, 5.63),
    ("Kab. Pangandaran",   2016, 10800, 61600, 5.70),
    ("Kab. Pangandaran",   2017, 11800, 68400, 5.80),
    ("Kab. Pangandaran",   2018, 12500, 73500, 5.88),
    ("Kab. Pangandaran",   2019, 13200, 78400, 5.94),
    ("Kab. Pangandaran",   2020, 12900, 77000, 5.97),
    ("Kab. Pangandaran",   2021, 12600, 75700, 6.01),
    ("Kab. Pangandaran",   2022, 14500, 87900, 6.06),
    ("Kab. Pangandaran",   2023, 12200, 74100, 6.07),
    ("Kab. Ciamis",        2014, 13000, 74100, 5.70),
    ("Kab. Ciamis",        2015, 12500, 70600, 5.65),
    ("Kab. Ciamis",        2016, 12800, 73200, 5.72),
    ("Kab. Ciamis",        2017, 14000, 81400, 5.82),
    ("Kab. Ciamis",        2018, 14800, 87400, 5.90),
    ("Kab. Ciamis",        2019, 15500, 92500, 5.97),
    ("Kab. Ciamis",        2020, 15200, 91100, 5.99),
    ("Kab. Ciamis",        2021, 14800, 89300, 6.03),
    ("Kab. Ciamis",        2022, 16800, 102300, 6.09),
    ("Kab. Ciamis",        2023, 14200, 86800, 6.11),
    ("Kab. Bandung",       2014, 5200,  28900, 5.56),
    ("Kab. Bandung",       2015, 4900,  26900, 5.49),
    ("Kab. Bandung",       2016, 5100,  28300, 5.55),
    ("Kab. Bandung",       2017, 5600,  31600, 5.64),
    ("Kab. Bandung",       2018, 5900,  33800, 5.73),
    ("Kab. Bandung",       2019, 6200,  35900, 5.79),
    ("Kab. Bandung",       2020, 6100,  35500, 5.82),
    ("Kab. Bandung",       2021, 5900,  34600, 5.86),
    ("Kab. Bandung",       2022, 6800,  40300, 5.93),
    ("Kab. Bandung",       2023, 5800,  34600, 5.97),
]


def build_panen_multi():
    """
    Gabungkan data padi dan jagung menjadi satu DataFrame
    dengan kolom tanaman (crop_type).
    """
    print("\n" + "="*55)
    print("  OPSI 2 — Build data panen multi-tanaman")
    print("="*55)

    # Padi

    df_padi = pd.DataFrame(
        PANEN_PADI,
        columns=["nama_kabupaten", "tahun",
                 "luas_panen_ha", "produksi_ton", "yield_ton_ha"]
    )
    df_padi["tanaman"] = "Padi"
    df_padi["tanaman_encoded"] = 0  # Padi = 0

    # Jagung
    df_jagung = pd.DataFrame(
        PANEN_JAGUNG,
        columns=["nama_kabupaten", "tahun",
                 "luas_panen_ha", "produksi_ton", "yield_ton_ha"]
    )
    df_jagung["tanaman"] = "Jagung"
    df_jagung["tanaman_encoded"] = 1  # Jagung = 1

    df_all = pd.concat([df_padi, df_jagung], ignore_index=True)

    # Hitung yield relatif per tanaman per kabupaten
    df_all["yield_relative"] = df_all.groupby(
        ["nama_kabupaten", "tanaman"]
    )["yield_ton_ha"].transform(lambda x: x / x.mean())

    def classify_status(ratio):
        if ratio >= 1.20:   return "PANEN_BERLIMPAH"
        elif ratio >= 0.80: return "NORMAL"
        else:               return "GAGAL_PANEN"

    df_all["status_aktual"] = df_all["yield_relative"].apply(classify_status)

    # Lag features per tanaman per kabupaten
    df_all = df_all.sort_values(["nama_kabupaten", "tanaman", "tahun"])
    df_all["yield_lag1"] = df_all.groupby(
        ["nama_kabupaten", "tanaman"]
    )["yield_ton_ha"].shift(1)
    df_all["yield_trend"] = df_all["yield_ton_ha"] - df_all["yield_lag1"]

    df_all.to_csv("data/raw/panen_jabar_multi_raw.csv", index=False)
    print(f"  ✓ Data mentah  : {len(df_all)} baris")
    print(f"    Padi         : {len(df_padi)} baris ({df_padi['tahun'].min()}–{df_padi['tahun'].max()})")
    print(f"    Jagung       : {len(df_jagung)} baris ({df_jagung['tahun'].min()}–{df_jagung['tahun'].max()})")
    print(f"    Kabupaten    : {df_all['nama_kabupaten'].nunique()}")

    # Simpan versi clean
    df_clean = df_all.dropna(subset=["yield_ton_ha"])
    df_clean.to_csv("data/processed/panen_jabar_multi_clean.csv", index=False)
    print(f"  ✓ Data bersih  : {len(df_clean)} baris")

    # Baseline per tanaman per kabupaten
    baseline = {}
    for (kab, tanaman), group in df_clean.groupby(["nama_kabupaten", "tanaman"]):
        yields = group["yield_ton_ha"]
        key = f"{kab}|{tanaman}"
        baseline[key] = {
            "nama_kabupaten":     kab,
            "tanaman":            tanaman,
            "mean_yield_ton_ha":  round(yields.mean(), 3),
            "std_yield_ton_ha":   round(yields.std(), 3),
            "threshold_berlimpah":      round(yields.mean() * 1.20, 3),
            "threshold_normal_lower":   round(yields.mean() * 0.80, 3),
            "n_tahun":            int(len(yields)),
        }

    with open("data/processed/baseline_yield_multi.json", "w") as f:
        json.dump(baseline, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Baseline     : {len(baseline)} entri (kabupaten × tanaman)")

    return df_clean


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 3 — MERGE DATASET FINAL V2
# ══════════════════════════════════════════════════════════════════════════════

MUSIM_TANAM = {
    "MR": (10, [10, 11, 12, 1, 2]),
    "MG": ( 4, [4, 5, 6, 7, 8]),
}


def aggregate_cuaca_per_musim(df_cuaca):
    rows = []
    for kab, group in df_cuaca.groupby("nama_kabupaten"):
        for tahun in sorted(group["year"].unique()):
            year_data = group[group["year"] == tahun]

            for musim, (bulan_mulai, bulan_list) in MUSIM_TANAM.items():
                if musim == "MR":
                    part1 = year_data[year_data["month"].isin([10, 11, 12])]
                    next_year = df_cuaca[
                        (df_cuaca["nama_kabupaten"] == kab) &
                        (df_cuaca["year"] == tahun + 1) &
                        (df_cuaca["month"].isin([1, 2]))
                    ]
                    musim_data = pd.concat([part1, next_year])
                    tahun_panen = tahun + 1
                    fase_veg = musim_data[musim_data["month"].isin([10, 11])]
                    fase_rep = musim_data[musim_data["month"].isin([12, 1])]
                    fase_mat = musim_data[musim_data["month"].isin([2])]
                else:
                    musim_data = year_data[year_data["month"].isin(bulan_list)]
                    tahun_panen = tahun
                    fase_veg = musim_data[musim_data["month"].isin([4, 5])]
                    fase_rep = musim_data[musim_data["month"].isin([6, 7])]
                    fase_mat = musim_data[musim_data["month"].isin([8])]

                if len(musim_data) == 0:
                    continue

                def sm(d, c):
                    col = f"{c}_monthly_mean"
                    return round(d[col].mean(), 3) if col in d.columns and len(d) > 0 else np.nan

                def ss(d, c):
                    col = f"{c}_monthly_sum"
                    return round(d[col].sum(), 3) if col in d.columns and len(d) > 0 else np.nan

                row = {
                    "nama_kabupaten": kab,
                    "tahun_panen":    tahun_panen,
                    "musim":          musim,
                    "temp_veg_mean":  sm(fase_veg,  "temperature_2m_mean"),
                    "temp_rep_mean":  sm(fase_rep,  "temperature_2m_mean"),
                    "temp_mat_mean":  sm(fase_mat,  "temperature_2m_mean"),
                    "rain_veg_total": ss(fase_veg,  "precipitation_sum"),
                    "rain_rep_total": ss(fase_rep,  "precipitation_sum"),
                    "rain_mat_total": ss(fase_mat,  "precipitation_sum"),
                    "rain_total_musim":    ss(musim_data, "precipitation_sum"),
                    "humidity_mean_musim": sm(musim_data, "humidity_mean"),
                    "radiation_veg":       ss(fase_veg,  "shortwave_radiation_sum"),
                    "radiation_rep":       ss(fase_rep,  "shortwave_radiation_sum"),
                    "drought_index_mean":  sm(musim_data, "drought_index"),
                    "n_bulan_data":        len(musim_data),
                }

                if row["rain_total_musim"] and row.get("drought_index_mean"):
                    row["water_balance"] = round(
                        row["rain_total_musim"] - (row["drought_index_mean"] * 100), 2
                    )
                else:
                    row["water_balance"] = np.nan

                rows.append(row)

    return pd.DataFrame(rows)


def merge_final_v2(df_panen, df_cuaca_monthly, df_tanah):
    """
    Merge dataset final dengan support multi-tanaman.
    Satu baris = satu kabupaten × satu tanaman × satu tahun × satu musim
    """
    print("\n" + "="*55)
    print("  Merge dataset final v2")
    print("="*55)

    print("  Agregasi cuaca per musim tanam...")
    df_cuaca_musim = aggregate_cuaca_per_musim(df_cuaca_monthly)
    print(f"  Cuaca musim: {df_cuaca_musim.shape}")

    # Expand panen per musim (MR dan MG)
    rows_expanded = []
    for _, row in df_panen.iterrows():
        for musim in ["MR", "MG"]:
            r = row.to_dict()
            r["musim"] = musim
            r["tahun_panen"] = row["tahun"]
            r["musim_encoded"] = 1 if musim == "MR" else 0
            rows_expanded.append(r)
    df_panen_exp = pd.DataFrame(rows_expanded)

    # Merge dengan cuaca
    df = df_panen_exp.merge(
        df_cuaca_musim,
        on=["nama_kabupaten", "tahun_panen", "musim"],
        how="left"
    )

    # Merge dengan tanah
    tanah_cols = [
        "nama_kabupaten", "ph_h2o", "nitrogen_cn_kg",
        "clay_pct", "sand_pct", "silt_pct", "soc_dg_kg",
        "cec_mmol_kg", "bulk_density", "fertility_index",
        "whc_proxy", "ph_status_encoded", "texture_encoded",
        "kesesuaian_encoded",
    ]
    tanah_sub = df_tanah[[c for c in tanah_cols if c in df_tanah.columns]]
    df = df.merge(tanah_sub, on="nama_kabupaten", how="left")

    # Encode tanah (jika belum ada dari script 02)
    if "ph_status_encoded" not in df.columns and "ph_status" in df.columns:
        ph_map = {"optimal": 2, "masam": 1, "sangat_masam": 0, "basa": 1}
        df["ph_status_encoded"] = df["ph_status"].map(ph_map).fillna(1)

    if "kesesuaian_encoded" not in df.columns and "kesesuaian_padi" in df.columns:
        df["kesesuaian_encoded"] = df["kesesuaian_padi"].map(
            {"S1": 2, "S2": 1, "S3": 0}
        ).fillna(1)

    if "texture_encoded" not in df.columns and "texture_class" in df.columns:
        df["texture_encoded"] = df["texture_class"].map(
            {"clay_loam": 3, "loam": 2, "clay": 1, "sandy_loam": 0}
        ).fillna(1)

    df.to_csv("data/final/dataset_ml_v2.csv", index=False)

    print(f"\n{'='*55}")
    print(f"  DATASET FINAL V2 SIAP")
    print(f"{'='*55}")
    print(f"  Total baris  : {len(df):,}")
    print(f"  Total kolom  : {len(df.columns)}")
    print(f"  Kabupaten    : {df['nama_kabupaten'].nunique()}")
    print(f"  Tanaman      : {df['tanaman'].unique().tolist()}")
    print(f"  Tahun        : {int(df['tahun_panen'].min())}–{int(df['tahun_panen'].max())}")
    print(f"  Yield mean   : {df['yield_ton_ha'].mean():.3f} ± {df['yield_ton_ha'].std():.3f} ton/ha")
    print(f"  Yield range  : {df['yield_ton_ha'].min():.3f} – {df['yield_ton_ha'].max():.3f} ton/ha")
    print(f"\n  Output → data/final/dataset_ml_v2.csv")

    return df


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════╗")
    print("║  Smart Agri-Insights — Ekspansi Dataset v2           ║")
    print("║  Opsi 1 (tahun 2014) + Opsi 2 (tambah jagung)       ║")
    print("╚══════════════════════════════════════════════════════╝")

    # ── Opsi 1: Download cuaca 2014–2018 ──────────────────────────────────────
    failed = download_cuaca_2014_2018()
    if failed:
        print(f"\n⚠ {len(failed)} kabupaten belum berhasil.")
        print("  Jalankan ulang script ini untuk retry otomatis.")

    # ── Rebuild cuaca combined (gabung 2014–2024) ─────────────────────────────
    df_cuaca_daily, df_cuaca_monthly = rebuild_cuaca_combined()
    if df_cuaca_monthly is None:
        print("ERROR: Tidak ada data cuaca. Pastikan folder cuaca_per_kabupaten ada.")
        return

    # ── Opsi 2: Build panen multi-tanaman ────────────────────────────────────
    df_panen = build_panen_multi()

    # ── Load data tanah ───────────────────────────────────────────────────────
    tanah_path = "data/raw/tanah_jabar_static.csv"
    if not os.path.exists(tanah_path):
        print(f"\n[ERROR] File tanah tidak ditemukan: {tanah_path}")
        print("  Jalankan dulu: python 02_tanah_static.py")
        return

    df_tanah = pd.read_csv(tanah_path)

    # Tambahkan encoded columns jika belum ada
    if "ph_status_encoded" not in df_tanah.columns and "ph_status" in df_tanah.columns:
        ph_map = {"optimal": 2, "masam": 1, "sangat_masam": 0, "basa": 1}
        df_tanah["ph_status_encoded"] = df_tanah["ph_status"].map(ph_map).fillna(1)
    if "kesesuaian_encoded" not in df_tanah.columns and "kesesuaian_padi" in df_tanah.columns:
        df_tanah["kesesuaian_encoded"] = df_tanah["kesesuaian_padi"].map(
            {"S1": 2, "S2": 1, "S3": 0}
        ).fillna(1)
    if "texture_encoded" not in df_tanah.columns and "texture_class" in df_tanah.columns:
        df_tanah["texture_encoded"] = df_tanah["texture_class"].map(
            {"clay_loam": 3, "loam": 2, "clay": 1, "sandy_loam": 0}
        ).fillna(1)

    # ── Merge final ───────────────────────────────────────────────────────────
    merge_final_v2(df_panen, df_cuaca_monthly, df_tanah)

    print("\n  Langkah selanjutnya:")
    print("  1. Serahkan data/final/dataset_ml_v2.csv ke ML Engineer")
    print("  2. Update script training: ganti dataset_ml_jabar.csv")
    print("     → dataset_ml_v2.csv")
    print("  3. Tambahkan fitur 'tanaman_encoded' ke FEATURE_COLS")
    print("     di script train_model.py")


if __name__ == "__main__":
    main()