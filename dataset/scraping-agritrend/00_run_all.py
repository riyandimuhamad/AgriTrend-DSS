"""
=============================================================
SCRIPT 0 — MASTER RUNNER + VALIDASI
=============================================================
Jalankan script ini untuk mengeksekusi seluruh pipeline
pengumpulan data secara berurutan.

Cara jalankan:
    pip install requests pandas numpy tqdm
    python 00_run_all.py

Urutan eksekusi:
    1. Script 02 — Data tanah statis (tercepat, tidak butuh internet)
    2. Script 03 — Data historis panen dari BPS embed + Open Data Jabar
    3. Script 01 — Data cuaca dari Open-Meteo (butuh internet, ±5–10 menit)
    4. Script 04 — Merge semua dataset menjadi dataset ML final
"""

import subprocess
import sys
import os
import json
import time

SCRIPTS = [
    ("02_tanah_static.py",    "Data tanah statis Jawa Barat"),
    ("03_panen_historis.py",  "Data historis panen BPS + Open Data Jabar"),
    ("01_cuaca_openmeteo.py", "Data cuaca Open-Meteo (butuh internet)"),
    ("04_merge_final.py",     "Merge dataset final"),
]


def run_script(filename: str, deskripsi: str) -> bool:
    print(f"\n{'─'*55}")
    print(f"  Menjalankan: {deskripsi}")
    print(f"  File       : {filename}")
    print(f"{'─'*55}")

    start = time.time()
    result = subprocess.run(
        [sys.executable, filename],
        capture_output=False,
        text=True
    )
    elapsed = time.time() - start

    if result.returncode == 0:
        print(f"\n  ✓ Selesai dalam {elapsed:.1f} detik")
        return True
    else:
        print(f"\n  ✗ GAGAL (kode {result.returncode})")
        return False


def validate_outputs():
    """Validasi semua output file tersedia dan tidak kosong."""
    expected_files = [
        "data/raw/tanah_jabar_static.csv",
        "data/raw/tanah_jabar_static.json",
        "data/raw/panen_jabar_raw.csv",
        "data/processed/panen_jabar_clean.csv",
        "data/processed/baseline_yield.json",
        "data/final/dataset_ml_jabar.csv",
        "data/final/feature_columns.json",
        "data/final/dataset_info.json",
    ]

    print(f"\n{'='*55}")
    print("  VALIDASI OUTPUT")
    print(f"{'='*55}")

    all_ok = True
    for path in expected_files:
        exists = os.path.exists(path)
        if exists:
            size = os.path.getsize(path)
            print(f"  ✓  {path} ({size:,} bytes)")
        else:
            print(f"  ✗  {path} — TIDAK DITEMUKAN")
            all_ok = False

    # Tampilkan ringkasan dataset final
    final_path = "data/final/dataset_ml_jabar.csv"
    info_path  = "data/final/dataset_info.json"
    if os.path.exists(final_path) and os.path.exists(info_path):
        with open(info_path) as f:
            info = json.load(f)
        print(f"\n  Dataset ML Final:")
        print(f"    Baris    : {info['total_rows']:,}")
        print(f"    Fitur    : {info['feature_count']}")
        print(f"    Kabupaten: {info['kabupaten_count']}")
        print(f"    Yield    : {info['target_stats']['mean']} ± "
              f"{info['target_stats']['std']} ton/ha")

    return all_ok


def main():
    print("╔══════════════════════════════════════════════════════╗")
    print("║  Smart Agri-Insights — Pipeline Pengumpulan Data     ║")
    print("║  Fokus: Jawa Barat, Tanaman Padi, 2019–2024          ║")
    print("╚══════════════════════════════════════════════════════╝")

    # Pindah ke direktori script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    results = {}
    for filename, deskripsi in SCRIPTS:
        if not os.path.exists(filename):
            print(f"\n  [SKIP] {filename} tidak ditemukan")
            continue
        success = run_script(filename, deskripsi)
        results[filename] = success

        # Jika tanah/panen gagal, berhenti (prerequisite untuk merge)
        if not success and filename in ["02_tanah_static.py", "03_panen_historis.py"]:
            print("\n  Script prerequisite gagal. Pipeline dihentikan.")
            break

    # Validasi
    validate_outputs()

    # Ringkasan
    print(f"\n{'='*55}")
    print("  RINGKASAN PIPELINE")
    print(f"{'='*55}")
    for filename, success in results.items():
        status = "✓ SUKSES" if success else "✗ GAGAL "
        print(f"  {status}  {filename}")

    total_ok = sum(results.values())
    print(f"\n  {total_ok}/{len(results)} script berhasil dijalankan")

    if total_ok == len(results):
        print("\n  Dataset siap untuk training model ML!")
        print("  Langkah selanjutnya:")
        print("    1. Buka notebook EDA: notebooks/01_eda.ipynb")
        print("    2. Training model   : python ml/train_model.py")
        print("    3. Evaluasi model   : python ml/evaluate.py")
    else:
        print("\n  Beberapa script gagal. Periksa error di atas.")


if __name__ == "__main__":
    main()
