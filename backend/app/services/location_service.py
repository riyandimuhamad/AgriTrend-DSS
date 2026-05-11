import json
from pathlib import Path
from typing import Any

from app.schemas.prediction import Coordinates


class LocationService:
    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        dataset_path = base_dir / "data" / "region_coordinates.json"
        self._dataset = self._load_dataset(dataset_path)

    def resolve_coordinates(
        self,
        kode_kabupaten_kota: int | None = None,
        nama_kabupaten_kota: str | None = None,
    ) -> Coordinates:
        by_code = self._dataset.get("by_code", {})
        by_name = self._dataset.get("by_name", {})

        if kode_kabupaten_kota is not None:
            row = by_code.get(str(kode_kabupaten_kota))
            if row:
                return Coordinates(**row)

        if nama_kabupaten_kota:
            key = nama_kabupaten_kota.strip().upper()
            code = by_name.get(key)
            if code and code in by_code:
                return Coordinates(**by_code[code])

        return Coordinates(**self._dataset["default"])

    @staticmethod
    def _load_dataset(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {
                "by_code": {},
                "by_name": {},
                "default": {
                    "latitude": -6.1754,
                    "longitude": 106.8451,
                    "region": "DKI Jakarta(Example)",
                },
            }

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
