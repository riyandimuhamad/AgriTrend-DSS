import json
import re
from pathlib import Path
from typing import Any


class LocationService:
    def __init__(self) -> None:
        path = Path(__file__).resolve().parents[1] / "data" / "region_coordinates.json"
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        self._by_name: dict[str, dict] = data["by_name"]
        self._default: dict = data["default"]

    def resolve_by_name(self, location: str) -> dict[str, Any]:

        # Exact match (uppercase)
        key = location.strip().upper()
        if key in self._by_name:
            return self._by_name[key]

        # Try with 'KABUPATEN' prefix
        kab_key = f"KABUPATEN {key}"
        if kab_key in self._by_name:
            return self._by_name[kab_key]

        # Fuzzy: find any entry containing the location word
        for name, coords in self._by_name.items():
            bare = re.sub(r"^(KABUPATEN|KOTA)\s+", "", name)
            if bare == key:
                return coords

        return self._default
