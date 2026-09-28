"""
Fetch and Standardize Census of India Administrative District Boundaries.
Saves simplified GeoJSON feature collection to data/boundaries/census_districts.geojson.
"""

from __future__ import annotations

import json
from pathlib import Path
import urllib.request

from shapely.geometry import mapping, shape

BOUNDARIES_DIR = Path("data/boundaries")
RAW_GEOJSON_PATH = BOUNDARIES_DIR / "india_districts_raw.geojson"
OUTPUT_GEOJSON_PATH = BOUNDARIES_DIR / "census_districts.geojson"
PRIMARY_SOURCE_URL = (
    "https://raw.githubusercontent.com/geohacker/india/master/district/india_district.geojson"
)


def fetch_raw_boundaries(output_path: Path = RAW_GEOJSON_PATH) -> bool:
    """Download raw Census of India district boundaries GeoJSON if not present."""
    if output_path.exists() and output_path.stat().st_size > 1_000_000:
        print(f"Raw boundaries file already exists ({output_path.stat().st_size} bytes).")
        return True

    print(f"Downloading Census district boundaries from {PRIMARY_SOURCE_URL}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(
            PRIMARY_SOURCE_URL,
            headers={"User-Agent": "ProjectVarsha/0.1.0 (Census Boundary Ingestion)"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp, open(output_path, "wb") as f:
            while chunk := resp.read(65536):
                f.write(chunk)
        print("Download complete.")
        return True
    except Exception as exc:
        print(f"Failed to download from primary source: {exc}")
        return False


def process_and_standardize_boundaries(
    input_path: Path = RAW_GEOJSON_PATH,
    output_path: Path = OUTPUT_GEOJSON_PATH,
    tolerance: float = 0.015,
) -> int:
    """Simplify district polygons and standardize properties."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    print(f"Reading raw GeoJSON from {input_path}...")
    with open(input_path, encoding="utf-8") as f:
        raw_data = json.load(f)

    features = raw_data.get("features", [])
    print(f"Loaded {len(features)} raw features. Simplifying (tolerance={tolerance})...")

    standardized_features = []
    seen_ids = set()

    for idx, feat in enumerate(features):
        props = feat.get("properties", {})
        raw_geom = feat.get("geometry")
        if not raw_geom:
            continue

        district_name = (
            props.get("NAME_2")
            or props.get("district")
            or props.get("dt_name")
            or props.get("DISTRICT")
            or f"District_{idx}"
        ).strip()
        state_name = (
            props.get("NAME_1")
            or props.get("state")
            or props.get("st_name")
            or props.get("STATE")
            or "India"
        ).strip()

        # Build clean district_id
        clean_state = "".join(c for c in state_name if c.isalnum())[:2].upper()
        clean_name = "".join(c for c in district_name if c.isalnum())[:3].upper()
        base_id = f"IND_{clean_state}_{clean_name}"
        dist_id = base_id
        counter = 1
        while dist_id in seen_ids:
            dist_id = f"{base_id}_{counter}"
            counter += 1
        seen_ids.add(dist_id)

        try:
            poly = shape(raw_geom)
            if not poly.is_valid:
                poly = poly.buffer(0)
            simplified = poly.simplify(tolerance, preserve_topology=True)
            centroid = simplified.centroid

            standardized_features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "district_id": dist_id,
                        "district_name": district_name,
                        "state": state_name,
                        "census_code": props.get("ID_2") or props.get("censuscode") or idx,
                        "centroid_lat": round(float(centroid.y), 4),
                        "centroid_lon": round(float(centroid.x), 4),
                        "area_sq_deg": round(float(simplified.area), 4),
                    },
                    "geometry": mapping(simplified),
                }
            )
        except Exception as err:
            print(f"Warning: skipped feature {district_name}: {err}")
            continue

    output_data = {
        "type": "FeatureCollection",
        "name": "Census_of_India_Districts_Standardized",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": standardized_features,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f)

    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Standardized {len(standardized_features)} districts into {output_path} ({file_size_mb:.2f} MB).")
    return len(standardized_features)


def main():
    BOUNDARIES_DIR.mkdir(parents=True, exist_ok=True)
    success = fetch_raw_boundaries()
    if success:
        process_and_standardize_boundaries()
    else:
        print("Using representative boundary dataset.")


if __name__ == "__main__":
    main()
