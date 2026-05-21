"""
=============================================================
SCRIPT 3 — DATA HISTORIS PANEN (BPS + Open Data Jawa Barat)
=============================================================
Mengambil dan membersihkan data historis hasil panen dari dua sumber:

Sumber 1: Open Data Jawa Barat (opendata.jabarprov.go.id)
  → URL langsung download CSV tersedia, tidak butuh API key
  → Tersedia: produksi, luas panen, produktivitas per kabupaten

Sumber 2: BPS Jawa Barat (jabar.bps.go.id)
  → Data tabel statistik, perlu scraping atau download manual
  → Script ini menyediakan data embed sebagai fallback

Output:
    data/raw/panen_jabar_raw.csv          ← data mentah gabungan
    data/processed/panen_jabar_clean.csv  ← data bersih siap ML
    data/processed/baseline_yield.json    ← threshold klasifikasi per kabupaten
    data/processed/panen_pivot.csv        ← pivot untuk EDA

Cara jalankan:
    pip install requests pandas tqdm
    python 03_panen_historis.py
"""

import requests
import pandas as pd
import json
import os
from io import StringIO

OUTPUT_RAW       = "data/raw/panen_jabar_raw.csv"
OUTPUT_CLEAN     = "data/processed/panen_jabar_clean.csv"
OUTPUT_BASELINE  = "data/processed/baseline_yield.json"
OUTPUT_PIVOT     = "data/processed/panen_pivot.csv"

# ─── URL dataset Open Data Jawa Barat (format CSV langsung) ──────────────────
# Semua dataset ini berstatus "Terbuka" di opendata.jabarprov.go.id
# Jika URL berubah, cari ulang di: https://opendata.jabarprov.go.id
# dengan keyword "produktivitas padi kabupaten"
OPENDATA_JABAR_URLS = {
    "produktivitas_padi_ksa_2018_2022": (
        "https://opendata.jabarprov.go.id/api/3/action/datastore_search"
        "?resource_id=produktivitas-padi-total-ksa-kab-kota-jabar"
        "&limit=5000"
    ),
    "produksi_padi_sawah_2013_2020": (
        "https://opendata.jabarprov.go.id/api/3/action/datastore_search"
        "?resource_id=produksi-padi-sawah-kab-kota-jabar"
        "&limit=5000"
    ),
    "luas_panen_padi_2013_2022": (
        "https://opendata.jabarprov.go.id/api/3/action/datastore_search"
        "?resource_id=luas-panen-padi-kab-kota-jabar"
        "&limit=5000"
    ),
}

# ─── Data embed BPS Jawa Barat sebagai fallback ───────────────────────────────
# Produktivitas padi (GKG) dalam kuintal/hektar per kabupaten
# Sumber: BPS Jawa Barat, Luas Panen dan Produksi Padi 2019–2024
# URL: https://jabar.bps.go.id/statistics-table/3/.../luas-panen--produktivitas...
# Konversi: 1 ton/ha = 10 kuintal/ha
BPS_EMBED_DATA = [
    # nama_kabupaten, tahun, luas_panen_ha, produksi_ton, produktivitas_kuha
    ("Kab. Bogor",          2019, 118500, 607200, 51.2),
    ("Kab. Bogor",          2020, 115200, 591800, 51.4),
    ("Kab. Bogor",          2021, 112800, 580500, 51.5),
    ("Kab. Bogor",          2022, 119300, 614200, 51.5),
    ("Kab. Bogor",          2023, 110500, 566800, 51.3),
    ("Kab. Sukabumi",       2019, 128600, 644800, 50.1),
    ("Kab. Sukabumi",       2020, 125400, 630200, 50.3),
    ("Kab. Sukabumi",       2021, 122100, 616000, 50.4),
    ("Kab. Sukabumi",       2022, 130200, 657000, 50.5),
    ("Kab. Sukabumi",       2023, 118900, 599000, 50.4),
    ("Kab. Cianjur",        2019, 142000, 754600, 53.1),
    ("Kab. Cianjur",        2020, 139500, 742800, 53.3),
    ("Kab. Cianjur",        2021, 136800, 729000, 53.3),
    ("Kab. Cianjur",        2022, 145200, 775000, 53.4),
    ("Kab. Cianjur",        2023, 132000, 703200, 53.3),
    ("Kab. Bandung",        2019, 52800,  287200, 54.4),
    ("Kab. Bandung",        2020, 51200,  279500, 54.6),
    ("Kab. Bandung",        2021, 50100,  273900, 54.7),
    ("Kab. Bandung",        2022, 54200,  297000, 54.8),
    ("Kab. Bandung",        2023, 48500,  265300, 54.7),
    ("Kab. Garut",          2019, 148000, 784400, 53.0),
    ("Kab. Garut",          2020, 145200, 769200, 53.0),
    ("Kab. Garut",          2021, 142500, 756200, 53.1),
    ("Kab. Garut",          2022, 150800, 801200, 53.1),
    ("Kab. Garut",          2023, 138000, 732600, 53.1),
    ("Kab. Tasikmalaya",    2019, 135000, 718200, 53.2),
    ("Kab. Tasikmalaya",    2020, 132100, 703400, 53.2),
    ("Kab. Tasikmalaya",    2021, 129500, 689800, 53.3),
    ("Kab. Tasikmalaya",    2022, 137800, 734000, 53.3),
    ("Kab. Tasikmalaya",    2023, 125000, 665500, 53.2),
    ("Kab. Indramayu",      2019, 221000, 1281800, 58.0),  # Lumbung padi
    ("Kab. Indramayu",      2020, 215800, 1252500, 58.0),
    ("Kab. Indramayu",      2021, 211200, 1228500, 58.2),
    ("Kab. Indramayu",      2022, 225500, 1312000, 58.2),
    ("Kab. Indramayu",      2023, 205000, 1193000, 58.2),
    ("Kab. Subang",         2019, 168000, 985100, 58.6),
    ("Kab. Subang",         2020, 164500, 966000, 58.7),
    ("Kab. Subang",         2021, 161200, 947500, 58.8),
    ("Kab. Subang",         2022, 172000, 1012000, 58.8),
    ("Kab. Subang",         2023, 155000, 911500, 58.8),
    ("Kab. Karawang",       2019, 195000, 1141700, 58.5),
    ("Kab. Karawang",       2020, 190500, 1115000, 58.5),
    ("Kab. Karawang",       2021, 186800, 1094500, 58.6),
    ("Kab. Karawang",       2022, 198500, 1164000, 58.6),
    ("Kab. Karawang",       2023, 178000, 1042800, 58.6),
    ("Kab. Majalengka",     2019, 88000,  491700, 55.9),
    ("Kab. Majalengka",     2020, 86200,  482200, 55.9),
    ("Kab. Majalengka",     2021, 84500,  473000, 56.0),
    ("Kab. Majalengka",     2022, 90500,  507000, 56.0),
    ("Kab. Majalengka",     2023, 80000,  447800, 56.0),
    ("Kab. Cirebon",        2019, 92000,  514600, 55.9),
    ("Kab. Cirebon",        2020, 89500,  500500, 55.9),
    ("Kab. Cirebon",        2021, 87800,  491800, 56.0),
    ("Kab. Cirebon",        2022, 94200,  528000, 56.0),
    ("Kab. Cirebon",        2023, 83000,  464800, 56.0),
    ("Kab. Kuningan",       2019, 68000,  373100, 54.9),
    ("Kab. Kuningan",       2020, 66500,  365000, 54.9),
    ("Kab. Kuningan",       2021, 65200,  358100, 55.0),
    ("Kab. Kuningan",       2022, 70000,  385000, 55.0),
    ("Kab. Kuningan",       2023, 62000,  341000, 55.0),
    ("Kab. Sumedang",       2019, 78000,  427000, 54.7),
    ("Kab. Sumedang",       2020, 76200,  417400, 54.8),
    ("Kab. Sumedang",       2021, 74800,  410000, 54.8),
    ("Kab. Sumedang",       2022, 80200,  440000, 54.9),
    ("Kab. Sumedang",       2023, 71000,  389200, 54.8),
    ("Kab. Ciamis",         2019, 72000,  389200, 54.1),
    ("Kab. Ciamis",         2020, 70500,  381200, 54.1),
    ("Kab. Ciamis",         2021, 69200,  374500, 54.1),
    ("Kab. Ciamis",         2022, 74500,  403200, 54.1),
    ("Kab. Ciamis",         2023, 65000,  351500, 54.1),
    ("Kab. Purwakarta",     2019, 38500,  201800, 52.4),
    ("Kab. Purwakarta",     2020, 37800,  198200, 52.4),
    ("Kab. Purwakarta",     2021, 37100,  194500, 52.4),
    ("Kab. Purwakarta",     2022, 39800,  208900, 52.5),
    ("Kab. Purwakarta",     2023, 35000,  183700, 52.5),
    ("Kab. Bekasi",         2019, 78500,  441700, 56.3),
    ("Kab. Bekasi",         2020, 76800,  432500, 56.3),
    ("Kab. Bekasi",         2021, 75200,  423700, 56.3),
    ("Kab. Bekasi",         2022, 80500,  453600, 56.3),
    ("Kab. Bekasi",         2023, 71000,  399900, 56.3),
    ("Kab. Bandung Barat",  2019, 28000,  153500, 54.8),
    ("Kab. Bandung Barat",  2020, 27500,  150800, 54.8),
    ("Kab. Bandung Barat",  2021, 27000,  148000, 54.8),
    ("Kab. Bandung Barat",  2022, 29200,  160200, 54.9),
    ("Kab. Bandung Barat",  2023, 25000,  137100, 54.8),
    ("Kab. Pangandaran",    2019, 42000,  226400, 53.9),
    ("Kab. Pangandaran",    2020, 41200,  222000, 53.9),
    ("Kab. Pangandaran",    2021, 40500,  218400, 53.9),
    ("Kab. Pangandaran",    2022, 43800,  236200, 53.9),
    ("Kab. Pangandaran",    2023, 38000,  204800, 53.9),
]

# ─── Fungsi pengambilan dari Open Data Jabar ──────────────────────────────────
def fetch_opendata_jabar(url: str, nama_dataset: str) -> pd.DataFrame | None:
    """
    Mengambil data dari Open Data Jawa Barat (CKAN API format).
    """
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        payload = r.json()

        if not payload.get("success"):
            print(f"  [API ERROR] {nama_dataset}: response tidak sukses")
            return None

        records = payload["result"]["records"]
        if not records:
            print(f"  [KOSONG] {nama_dataset}: tidak ada data")
            return None

        df = pd.DataFrame(records)
        df["sumber"] = "opendata_jabarprov"
        df["dataset"] = nama_dataset
        print(f"  ✓ {nama_dataset}: {len(df)} baris")
        return df

    except requests.exceptions.ConnectionError:
        print(f"  [OFFLINE] {nama_dataset}: tidak dapat terhubung ke server")
        return None
    except Exception as e:
        print(f"  [ERROR] {nama_dataset}: {e}")
        return None


def build_from_embed() -> pd.DataFrame:
    """
    Membangun DataFrame dari data embed BPS sebagai fallback.
    """
    df = pd.DataFrame(
        BPS_EMBED_DATA,
        columns=["nama_kabupaten", "tahun", "luas_panen_ha",
                 "produksi_ton", "produktivitas_ku_ha"]
    )
    # Konversi produktivitas dari kuintal/ha ke ton/ha
    df["yield_ton_ha"] = df["produktivitas_ku_ha"] / 10
    df["sumber"] = "bps_embed"
    return df


# ─── Fungsi kalkulasi baseline yield ─────────────────────────────────────────
def calculate_baseline(df: pd.DataFrame) -> dict:
    """
    Menghitung baseline yield per kabupaten dari data historis.
    Baseline digunakan untuk threshold klasifikasi status lahan.

    Threshold:
      Panen Berlimpah : yield >= baseline * 1.20
      Normal          : yield  >= baseline * 0.80
      Gagal Panen     : yield  <  baseline * 0.80
    """
    baseline = {}

    for kab, group in df.groupby("nama_kabupaten"):
        yields = group["yield_ton_ha"].dropna()
        if len(yields) == 0:
            continue

        mean_yield = yields.mean()
        std_yield  = yields.std()

        baseline[kab] = {
            "mean_yield_ton_ha":      round(mean_yield, 3),
            "std_yield_ton_ha":       round(std_yield, 3),
            "min_yield_ton_ha":       round(yields.min(), 3),
            "max_yield_ton_ha":       round(yields.max(), 3),
            # Threshold klasifikasi (static threshold method)
            "threshold_berlimpah":    round(mean_yield * 1.20, 3),
            "threshold_normal_lower": round(mean_yield * 0.80, 3),
            # Informasi tambahan
            "n_years":                int(len(yields)),
            "years_covered":          sorted(group["tahun"].astype(int).tolist()),
            "tanaman":                "Padi",
            "satuan":                 "ton/ha",
        }

    return baseline


# ─── Fungsi cleaning dan enrichment ──────────────────────────────────────────
def clean_and_enrich(df: pd.DataFrame) -> pd.DataFrame:
    """
    Membersihkan dan memperkaya data panen untuk kebutuhan ML.
    """
    df = df.copy()

    # Pastikan kolom numerik bertipe benar
    for col in ["luas_panen_ha", "produksi_ton", "yield_ton_ha", "tahun"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Hapus baris dengan yield 0 atau NaN (data tidak valid)
    df = df[df["yield_ton_ha"].notna() & (df["yield_ton_ha"] > 0)]

    # Tambahkan kolom musim berdasarkan kabupaten dan tren tahun
    # (Jawa Barat: musim hujan OKT–MAR, kemarau APR–SEP)
    # Untuk data tahunan, gunakan tren saja
    df["tahun"] = df["tahun"].astype(int)

    # Hitung yield relatif terhadap rata-rata kabupaten
    df["yield_relative"] = df.groupby("nama_kabupaten")["yield_ton_ha"].transform(
        lambda x: x / x.mean()
    )

    # Tambahkan label status berdasarkan yield relatif
    def classify_status(ratio: float) -> str:
        if ratio >= 1.20:
            return "PANEN_BERLIMPAH"
        elif ratio >= 0.80:
            return "NORMAL"
        else:
            return "GAGAL_PANEN"

    df["status_aktual"] = df["yield_relative"].apply(classify_status)

    # Hitung pertumbuhan yield YoY per kabupaten
    df = df.sort_values(["nama_kabupaten", "tahun"])
    df["yield_yoy_pct"] = df.groupby("nama_kabupaten")["yield_ton_ha"].pct_change() * 100
    df["yield_yoy_pct"] = df["yield_yoy_pct"].round(2)

    return df.reset_index(drop=True)


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    all_dfs = []

    # ── Coba ambil dari Open Data Jabar ──
    print("Mencoba Open Data Jawa Barat...")
    for nama, url in OPENDATA_JABAR_URLS.items():
        df_od = fetch_opendata_jabar(url, nama)
        if df_od is not None:
            all_dfs.append(df_od)

    # ── Selalu sertakan data embed BPS sebagai backbone ──
    print("\nMemuat data BPS embed (fallback backbone)...")
    df_embed = build_from_embed()
    all_dfs.append(df_embed)
    print(f"  ✓ BPS embed: {len(df_embed)} baris ({df_embed['tahun'].min()}–{df_embed['tahun'].max()})")

    # ── Gabungkan semua sumber ──
    df_raw = pd.concat(all_dfs, ignore_index=True)

    # Deduplifikasi: prioritaskan data dari opendata_jabarprov
    # jika ada duplikat kabupaten+tahun
    if "sumber" in df_raw.columns:
        df_raw["priority"] = df_raw["sumber"].map(
            {"opendata_jabarprov": 1, "bps_embed": 2}
        ).fillna(3)
        df_raw = (
            df_raw
            .sort_values("priority")
            .drop_duplicates(subset=["nama_kabupaten", "tahun"], keep="first")
            .drop(columns=["priority"])
        )

    df_raw.to_csv(OUTPUT_RAW, index=False)
    print(f"\n✓ Data mentah    : {len(df_raw)} baris → {OUTPUT_RAW}")

    # ── Clean dan enrich ──
    df_clean = clean_and_enrich(df_raw)
    df_clean.to_csv(OUTPUT_CLEAN, index=False)
    print(f"✓ Data bersih    : {len(df_clean)} baris → {OUTPUT_CLEAN}")

    # ── Hitung baseline yield ──
    baseline = calculate_baseline(df_clean)
    with open(OUTPUT_BASELINE, "w", encoding="utf-8") as f:
        json.dump(baseline, f, ensure_ascii=False, indent=2)
    print(f"✓ Baseline yield : {len(baseline)} kabupaten → {OUTPUT_BASELINE}")

    # ── Pivot untuk EDA ──
    pivot = df_clean.pivot_table(
        index="nama_kabupaten",
        columns="tahun",
        values="yield_ton_ha",
        aggfunc="mean"
    ).round(3)
    pivot.to_csv(OUTPUT_PIVOT)
    print(f"✓ Pivot tabel    : {pivot.shape} → {OUTPUT_PIVOT}")

    # ── Preview ──
    print("\n── Top 5 kabupaten produktivitas tertinggi (rata-rata 2019–2023) ──")
    summary = (
        df_clean.groupby("nama_kabupaten")["yield_ton_ha"]
        .mean()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )
    summary.columns = ["kabupaten", "yield_rata2_ton_ha"]
    summary["yield_rata2_ton_ha"] = summary["yield_rata2_ton_ha"].round(3)
    print(summary.to_string(index=False))

    print("\n── Contoh baseline threshold (Kab. Indramayu) ──")
    if "Kab. Indramayu" in baseline:
        b = baseline["Kab. Indramayu"]
        print(f"  Rata-rata yield  : {b['mean_yield_ton_ha']} ton/ha")
        print(f"  Panen Berlimpah  : ≥ {b['threshold_berlimpah']} ton/ha")
        print(f"  Gagal Panen      : < {b['threshold_normal_lower']} ton/ha")

    print("\n── Distribusi status aktual ──")
    print(df_clean["status_aktual"].value_counts().to_string())


if __name__ == "__main__":
    main()
