"""
=============================================================
SCRIPT 4 — MERGE & FINAL DATASET (Siap untuk Training ML)
=============================================================
Menggabungkan tiga dataset (cuaca bulanan, tanah, panen historis)
menjadi satu dataset final yang siap digunakan untuk training
model Random Forest.

Logika join:
    panen (per kabupaten per tahun)
    LEFT JOIN cuaca_bulanan (ambil agregasi per musim tanam)
    LEFT JOIN tanah_static (per kabupaten, statis)

Output:
    data/final/dataset_ml_jabar.csv     ← dataset utama untuk training
    data/final/dataset_info.json        ← metadata dan statistik dataset
    data/final/feature_columns.json     ← daftar kolom fitur untuk model

Cara jalankan (setelah script 01, 02, 03 selesai):
    python 04_merge_final.py
"""

import pandas as pd
import json
import os
import numpy as np

INPUT_PANEN   = "data/processed/panen_jabar_clean.csv"
INPUT_CUACA   = "data/raw/cuaca_jabar_2019_2024_monthly.csv"
INPUT_TANAH   = "data/raw/tanah_jabar_static.csv"
OUTPUT_FINAL  = "data/final/dataset_ml_jabar.csv"
OUTPUT_INFO   = "data/final/dataset_info.json"
OUTPUT_FEATS  = "data/final/feature_columns.json"


# ─── Fase pertumbuhan padi (dalam bulan dari awal tanam) ─────────────────────
# Musim Rendengan (MR)  : tanam Oktober–November, panen Februari–Maret
# Musim Gadu (MG)       : tanam April–Mei, panen Agustus–September
FASE_VEGETATIF   = [1, 2]    # bulan ke-1 dan ke-2 setelah tanam
FASE_REPRODUKTIF = [3, 4]    # bulan ke-3 dan ke-4
FASE_PEMATANGAN  = [5]       # bulan ke-5

MUSIM_TANAM = {
    # (nama_musim, bulan_tanam_mulai, bulan_panen, label_cuaca_bulan)
    "MR": (10, 2, [10, 11, 12, 1, 2]),    # Oktober – Februari
    "MG": ( 4, 8, [4, 5, 6, 7, 8]),       # April – Agustus
}


def aggregate_cuaca_per_musim(df_cuaca: pd.DataFrame) -> pd.DataFrame:
    """
    Mengagregasi data cuaca bulanan menjadi fitur per musim tanam per kabupaten.
    Ini menghasilkan satu baris per (kabupaten, tahun, musim).
    """
    rows = []

    for kab, group in df_cuaca.groupby("nama_kabupaten"):
        for tahun in group["year"].unique():
            year_data = group[group["year"] == tahun]

            for musim, (bulan_mulai, bulan_panen, bulan_list) in MUSIM_TANAM.items():
                # Ambil data bulan yang relevan
                # Untuk MR yang melewati tahun (Okt–Feb), perlu handle cross-year
                if musim == "MR":
                    # Bulan Okt–Des dari tahun ini
                    bulan_akhir_tahun = year_data[year_data["month"].isin([10, 11, 12])]
                    # Bulan Jan–Feb dari tahun berikutnya
                    next_year_data = df_cuaca[
                        (df_cuaca["nama_kabupaten"] == kab) &
                        (df_cuaca["year"] == tahun + 1) &
                        (df_cuaca["month"].isin([1, 2]))
                    ]
                    musim_data = pd.concat([bulan_akhir_tahun, next_year_data])
                    tahun_panen = tahun + 1
                else:
                    musim_data = year_data[year_data["month"].isin(bulan_list)]
                    tahun_panen = tahun

                if len(musim_data) == 0:
                    continue

                # Pisahkan fitur per fase pertumbuhan
                if musim == "MR":
                    fase_veg  = musim_data[musim_data["month"].isin([10, 11])]
                    fase_rep  = musim_data[musim_data["month"].isin([12, 1])]
                    fase_mat  = musim_data[musim_data["month"].isin([2])]
                else:
                    fase_veg  = musim_data[musim_data["month"].isin([4, 5])]
                    fase_rep  = musim_data[musim_data["month"].isin([6, 7])]
                    fase_mat  = musim_data[musim_data["month"].isin([8])]

                def safe_mean(df_fase, col):
                    if col in df_fase.columns and len(df_fase) > 0:
                        return round(df_fase[col].mean(), 3)
                    return np.nan

                def safe_sum(df_fase, col):
                    if col in df_fase.columns and len(df_fase) > 0:
                        return round(df_fase[col].sum(), 3)
                    return np.nan

                # Nama kolom mengacu ke kolom output script 01 (monthly aggregation)
                # Format: {variabel}_monthly_{sum|mean}
                row = {
                    "nama_kabupaten": kab,
                    "tahun_panen":    tahun_panen,
                    "musim":          musim,

                    # ── Suhu per fase ──
                    "temp_veg_mean":  safe_mean(fase_veg,  "temperature_2m_mean_monthly_mean"),
                    "temp_rep_mean":  safe_mean(fase_rep,  "temperature_2m_mean_monthly_mean"),
                    "temp_mat_mean":  safe_mean(fase_mat,  "temperature_2m_mean_monthly_mean"),

                    # ── Curah hujan per fase ──
                    "rain_veg_total": safe_sum(fase_veg,   "precipitation_sum_monthly_sum"),
                    "rain_rep_total": safe_sum(fase_rep,   "precipitation_sum_monthly_sum"),
                    "rain_mat_total": safe_sum(fase_mat,   "precipitation_sum_monthly_sum"),
                    "rain_total_musim": safe_sum(musim_data, "precipitation_sum_monthly_sum"),

                    # ── Kelembaban ──
                    "humidity_mean_musim": safe_mean(musim_data, "humidity_mean_monthly_mean"),

                    # ── Radiasi matahari ──
                    "radiation_veg":  safe_sum(fase_veg,   "shortwave_radiation_sum_monthly_sum"),
                    "radiation_rep":  safe_sum(fase_rep,   "shortwave_radiation_sum_monthly_sum"),

                    # ── Evapotranspirasi ──
                    "et0_total_musim": safe_sum(musim_data, "et0_fao_evapotranspiration_monthly_sum"),

                    # ── Indeks kekeringan rata-rata musim ──
                    "drought_index_mean": safe_mean(musim_data, "drought_index_monthly_mean"),

                    # ── Jumlah bulan data tersedia ──
                    "n_bulan_data": len(musim_data),
                }

                # Fitur interaksi yang berguna untuk model
                if row["rain_rep_total"] and row["et0_total_musim"]:
                    row["water_balance"] = round(
                        row["rain_total_musim"] - row["et0_total_musim"], 2
                    )
                else:
                    row["water_balance"] = np.nan

                rows.append(row)

    return pd.DataFrame(rows)


def merge_all(df_panen: pd.DataFrame,
              df_cuaca_musim: pd.DataFrame,
              df_tanah: pd.DataFrame) -> pd.DataFrame:
    """
    Menggabungkan semua dataset.
    """
    # Siapkan key join di panen: tambahkan kolom musim
    # Asumsi: data produktivitas tahunan BPS adalah rata-rata MR+MG
    # Kita buat dua baris per tahun (MR dan MG) untuk lebih granular
    panen_expanded = []
    for _, row in df_panen.iterrows():
        for musim in ["MR", "MG"]:
            r = row.to_dict()
            r["musim"] = musim
            r["tahun_panen"] = row["tahun"]
            panen_expanded.append(r)
    df_panen_exp = pd.DataFrame(panen_expanded)

    # Merge dengan cuaca per musim
    df_merged = df_panen_exp.merge(
        df_cuaca_musim,
        on=["nama_kabupaten", "tahun_panen", "musim"],
        how="left"
    )

    # Merge dengan data tanah (statis, key: nama_kabupaten saja)
    tanah_cols = [
        "nama_kabupaten", "ph_h2o", "nitrogen_cn_kg",
        "clay_pct", "sand_pct", "silt_pct", "soc_dg_kg",
        "cec_mmol_kg", "bulk_density", "fertility_index",
        "whc_proxy", "ph_status", "texture_class", "kesesuaian_padi"
    ]
    df_tanah_sub = df_tanah[[c for c in tanah_cols if c in df_tanah.columns]]
    df_final = df_merged.merge(df_tanah_sub, on="nama_kabupaten", how="left")

    # Encode fitur kategoris untuk model ML
    # Musim: MR=1 (basah), MG=0 (kering) — relevan untuk yield
    df_final["musim_encoded"] = (df_final["musim"] == "MR").astype(int)

    # Kesesuaian lahan: S1=2, S2=1, S3=0
    kesesuaian_map = {"S1": 2, "S2": 1, "S3": 0}
    if "kesesuaian_padi" in df_final.columns:
        df_final["kesesuaian_encoded"] = df_final["kesesuaian_padi"].map(kesesuaian_map).fillna(1)

    # pH status encoded
    ph_map = {"optimal": 2, "masam": 1, "sangat_masam": 0, "basa": 1}
    if "ph_status" in df_final.columns:
        df_final["ph_status_encoded"] = df_final["ph_status"].map(ph_map).fillna(1)

    # Tekstur encoded (untuk ML, clay_loam paling ideal untuk padi)
    tex_map = {"clay_loam": 3, "loam": 2, "clay": 1, "sandy_loam": 0}
    if "texture_class" in df_final.columns:
        df_final["texture_encoded"] = df_final["texture_class"].map(tex_map).fillna(1)

    # Hitung tren yield 3 tahun terakhir sebagai fitur konteks
    df_final = df_final.sort_values(["nama_kabupaten", "musim", "tahun_panen"])
    df_final["yield_lag1"] = df_final.groupby(
        ["nama_kabupaten", "musim"]
    )["yield_ton_ha"].shift(1)
    df_final["yield_lag2"] = df_final.groupby(
        ["nama_kabupaten", "musim"]
    )["yield_ton_ha"].shift(2)
    df_final["yield_trend"] = df_final["yield_ton_ha"] - df_final["yield_lag1"]

    return df_final.reset_index(drop=True)


def identify_feature_columns(df: pd.DataFrame) -> dict:
    """
    Mengidentifikasi kolom yang digunakan sebagai fitur input model
    vs kolom target dan kolom metadata.
    """
    target_col = "yield_ton_ha"

    metadata_cols = [
        "nama_kabupaten", "tahun", "tahun_panen", "musim",
        "luas_panen_ha", "produksi_ton", "produktivitas_ku_ha",
        "status_aktual", "yield_relative", "yield_yoy_pct",
        "sumber", "dataset", "ph_status", "texture_class",
        "kesesuaian_padi",
    ]

    all_cols = df.columns.tolist()
    feature_cols = [
        c for c in all_cols
        if c != target_col
        and c not in metadata_cols
        and df[c].dtype in [float, int, "float64", "int64"]
        and df[c].notna().sum() > len(df) * 0.5  # minimal 50% non-null
    ]

    return {
        "target": target_col,
        "features": feature_cols,
        "metadata": metadata_cols,
        "total_features": len(feature_cols),
    }


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    os.makedirs("data/final", exist_ok=True)

    # ── Load datasets ──
    print("Memuat dataset...")
    df_panen = pd.read_csv(INPUT_PANEN)
    print(f"  Panen   : {df_panen.shape}")

    if os.path.exists(INPUT_CUACA):
        df_cuaca = pd.read_csv(INPUT_CUACA)
        print(f"  Cuaca   : {df_cuaca.shape}")
        print("  Agregasi cuaca per musim tanam...")
        df_cuaca_musim = aggregate_cuaca_per_musim(df_cuaca)
        print(f"  Cuaca musim: {df_cuaca_musim.shape}")
    else:
        print("  [SKIP] Data cuaca belum tersedia — jalankan script 01 dulu")
        print("  Membuat dummy cuaca untuk demo struktur...")
        df_cuaca_musim = pd.DataFrame()

    df_tanah = pd.read_csv(INPUT_TANAH)
    print(f"  Tanah   : {df_tanah.shape}")

    # ── Merge ──
    print("\nMenggabungkan semua dataset...")
    if len(df_cuaca_musim) > 0:
        df_final = merge_all(df_panen, df_cuaca_musim, df_tanah)
    else:
        # Fallback: merge panen + tanah saja (tanpa cuaca)
        panen_expanded = []
        for _, row in df_panen.iterrows():
            for musim in ["MR", "MG"]:
                r = row.to_dict()
                r["musim"] = musim
                r["tahun_panen"] = row["tahun"]
                r["musim_encoded"] = 1 if musim == "MR" else 0
                panen_expanded.append(r)
        df_panen_exp = pd.DataFrame(panen_expanded)
        df_final = df_panen_exp.merge(
            df_tanah[["nama_kabupaten", "ph_h2o", "nitrogen_cn_kg",
                      "clay_pct", "sand_pct", "fertility_index",
                      "kesesuaian_padi"]],
            on="nama_kabupaten", how="left"
        )
        print("  [PERINGATAN] Merged tanpa data cuaca — performa model akan lebih rendah")

    df_final.to_csv(OUTPUT_FINAL, index=False)

    # ── Feature columns ──
    feat_info = identify_feature_columns(df_final)
    with open(OUTPUT_FEATS, "w", encoding="utf-8") as f:
        json.dump(feat_info, f, ensure_ascii=False, indent=2)

    # ── Dataset info ──
    info = {
        "total_rows":        len(df_final),
        "total_columns":     len(df_final.columns),
        "kabupaten_count":   df_final["nama_kabupaten"].nunique(),
        "tahun_range":       [int(df_final["tahun_panen"].min()),
                              int(df_final["tahun_panen"].max())],
        "target_stats": {
            "mean":  round(df_final["yield_ton_ha"].mean(), 3),
            "std":   round(df_final["yield_ton_ha"].std(), 3),
            "min":   round(df_final["yield_ton_ha"].min(), 3),
            "max":   round(df_final["yield_ton_ha"].max(), 3),
        },
        "missing_pct": {
            col: round(df_final[col].isna().mean() * 100, 1)
            for col in feat_info["features"]
        },
        "feature_count":     feat_info["total_features"],
        "feature_list":      feat_info["features"],
    }
    with open(OUTPUT_INFO, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    # ── Ringkasan ──
    print(f"\n{'='*55}")
    print(f"  DATASET FINAL SIAP")
    print(f"{'='*55}")
    print(f"  Total baris    : {len(df_final):,}")
    print(f"  Total kolom    : {len(df_final.columns)}")
    print(f"  Kabupaten      : {df_final['nama_kabupaten'].nunique()}")
    print(f"  Tahun          : {info['tahun_range'][0]}–{info['tahun_range'][1]}")
    print(f"  Fitur ML       : {feat_info['total_features']} kolom")
    print(f"  Target (yield) : {info['target_stats']['mean']} ± "
          f"{info['target_stats']['std']} ton/ha")
    print(f"\n  Output → {OUTPUT_FINAL}")
    print(f"  Fitur  → {OUTPUT_FEATS}")
    print(f"  Info   → {OUTPUT_INFO}")
    print(f"\n  Kolom fitur yang akan digunakan model:")
    for i, col in enumerate(feat_info["features"], 1):
        missing = info["missing_pct"].get(col, 0)
        flag = " ⚠ missing data" if missing > 20 else ""
        print(f"    {i:2}. {col:<40} ({missing:.0f}% null){flag}")


if __name__ == "__main__":
    main()
