"""
Script untuk menggabungkan ulang semua file cuaca per kabupaten
menjadi satu file combined tanpa perlu hit API lagi.
"""
import pandas as pd
import os
import glob

INPUT_DIR        = "data/raw/cuaca_per_kabupaten"
OUTPUT_DAILY     = "data/raw/cuaca_jabar_2019_2024.csv"
OUTPUT_MONTHLY   = "data/raw/cuaca_jabar_2019_2024_monthly.csv"

def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
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

def main():
    # Ambil semua file CSV di folder cuaca_per_kabupaten
    all_files = glob.glob(os.path.join(INPUT_DIR, "cuaca_*.csv"))
    print(f"Ditemukan {len(all_files)} file kabupaten/kota\n")

    all_daily = []
    for path in sorted(all_files):
        df = pd.read_csv(path, parse_dates=["date"])
        nama = df["nama_kabupaten"].iloc[0]
        print(f"  ✓ {nama} — {len(df)} baris")
        all_daily.append(df)

    # Gabungkan semua
    df_combined = pd.concat(all_daily, ignore_index=True)
    df_combined = df_combined.sort_values(
        ["nama_kabupaten", "date"]
    ).reset_index(drop=True)

    # Simpan harian
    df_combined.to_csv(OUTPUT_DAILY, index=False)
    print(f"\n✓ Data harian gabungan   : {len(df_combined):,} baris → {OUTPUT_DAILY}")

    # Buat dan simpan bulanan
    df_monthly = aggregate_monthly(df_combined)
    df_monthly.to_csv(OUTPUT_MONTHLY, index=False)
    print(f"✓ Data bulanan gabungan  : {len(df_monthly):,} baris → {OUTPUT_MONTHLY}")

    # Ringkasan
    print(f"\nKabupaten/kota yang tercakup ({df_combined['nama_kabupaten'].nunique()}):")
    for nama in sorted(df_combined["nama_kabupaten"].unique()):
        n = len(df_combined[df_combined["nama_kabupaten"] == nama])
        print(f"  {nama} — {n} hari")

if __name__ == "__main__":
    main()