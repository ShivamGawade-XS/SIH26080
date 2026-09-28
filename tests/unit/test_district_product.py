"""
Unit tests for District Aggregation, Alert Classification, and GeoJSON export (Deliverable D4).
"""

import numpy as np

from varsha.config import get_config
from varsha.data.boundaries import load_or_create_boundaries
from varsha.data.synthetic.generator import generate_synthetic_dataset
from varsha.product.alerts import evaluate_district_alert
from varsha.product.districts import (
    aggregate_district_forecasts,
    build_districts_geojson,
    export_districts_csv,
)



def test_alert_evaluation_logic():
    # Green condition
    alert_green = evaluate_district_alert(
        p50_mm=5.0,
        max_cell_prob_64=0.05,
        max_cell_prob_115=0.01,
        expected_area_fraction_64=0.02,
        expected_area_fraction_15=0.10,
    )
    assert alert_green.level == "green"
    assert alert_green.glyph == "circle"

    # Red condition (Heavy P115 or high area fraction)
    alert_red = evaluate_district_alert(
        p50_mm=120.0,
        max_cell_prob_64=0.90,
        max_cell_prob_115=0.55,
        expected_area_fraction_64=0.60,
        expected_area_fraction_15=0.90,
    )
    assert alert_red.level == "red"
    assert alert_red.glyph == "diamond"
    assert alert_red.label == "Warning"


def test_district_aggregation_and_geojson():
    cfg = get_config(profile_name="demo-fast")
    ds = generate_synthetic_dataset(cfg, seasons=["S01"])
    districts = load_or_create_boundaries(lats=ds.lat.values, lons=ds.lon.values)

    assert len(districts) > 0

    dummy_corr = ds["tp_raw"].isel(time=-1).values  # (5, n_lat, n_lon)
    rows = aggregate_district_forecasts(
        ds=ds,
        corrected_grid=dummy_corr,
        districts=districts,
        lead=1,
        time_idx=-1,
    )

    assert len(rows) == len(districts)
    row0 = rows[0]
    assert "district_id" in row0
    assert "alert_level" in row0
    assert "corrected_p50_mm" in row0

    # Check GeoJSON conversion
    geojson = build_districts_geojson(rows, districts)
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == len(districts)
    assert geojson["features"][0]["geometry"]["type"] == "Polygon"

    # Check CSV export
    csv_str = export_districts_csv(rows)
    assert "district_id,district_name,state" in csv_str


def test_load_boundaries_from_geojson(tmp_path):
    import json
    from varsha.data.boundaries import make_district_polygon

    poly = make_district_polygon(19.0, 73.0)
    sample_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "district_id": "IND_TEST_01",
                    "district_name": "Test District",
                    "state": "Maharashtra",
                },
                "geometry": poly,
            }
        ],
    }
    p = tmp_path / "test_boundaries.geojson"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(sample_geojson, f)

    lats = np.array([18.5, 19.0, 19.5])
    lons = np.array([72.5, 73.0, 73.5])
    loaded = load_or_create_boundaries(boundary_path=p, lats=lats, lons=lons)
    assert len(loaded) == 1
    assert loaded[0].district_id == "IND_TEST_01"
    assert loaded[0].name == "Test District"
    assert len(loaded[0].cell_indices) > 0

