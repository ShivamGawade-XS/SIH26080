"""
District Aggregation Engine & Export Builder (Deliverable D4).
Aggregates grid-cell post-processed rainfall and exceedance probabilities
to administrative district boundaries.
"""

from typing import Any

import numpy as np
import pandas as pd
import xarray as xr

from varsha.data.boundaries import DistrictMeta
from varsha.product.alerts import evaluate_district_alert


def aggregate_district_forecasts(
    ds: xr.Dataset,
    corrected_grid: np.ndarray,  # (n_time, n_lead, n_lat, n_lon) or (n_lead, n_lat, n_lon)
    districts: list[DistrictMeta],
    lead: int,
    time_idx: int = -1,
    p10_grid: np.ndarray | None = None,
    p90_grid: np.ndarray | None = None,
    prob64_grid: np.ndarray | None = None,
    prob115_grid: np.ndarray | None = None,
    regime_name: str = "normal",
    regime_confidence: float = 0.85,
    attributions: dict[str, np.ndarray] | None = None,
) -> list[dict[str, Any]]:
    """
    Aggregate grid cells to districts for a given lead time.
    Returns structured list of district forecast records.
    """
    valid_time = str(ds["time"].values[time_idx])
    raw_lead_grid = ds["tp_raw"].isel(time=time_idx).sel(lead=lead).values

    corr_lead_grid = (
        corrected_grid[time_idx, lead - 1] if corrected_grid.ndim == 4 else corrected_grid[lead - 1]
    )

    p10_lead = (
        (p10_grid[time_idx, lead - 1] if p10_grid.ndim == 4 else p10_grid[lead - 1])
        if p10_grid is not None
        else np.maximum(0.0, corr_lead_grid * 0.70)
    )
    p90_lead = (
        (p90_grid[time_idx, lead - 1] if p90_grid.ndim == 4 else p90_grid[lead - 1])
        if p90_grid is not None
        else np.maximum(0.0, corr_lead_grid * 1.35)
    )

    # Exceedance grids approximation if not provided directly
    p64_lead = (
        (prob64_grid[time_idx, lead - 1] if prob64_grid.ndim == 4 else prob64_grid[lead - 1])
        if prob64_grid is not None
        else np.clip((corr_lead_grid - 30.0) / 45.0, 0.0, 1.0)
    )
    p115_lead = (
        (prob115_grid[time_idx, lead - 1] if prob115_grid.ndim == 4 else prob115_grid[lead - 1])
        if prob115_grid is not None
        else np.clip((corr_lead_grid - 80.0) / 50.0, 0.0, 1.0)
    )
    p15_lead = np.clip(corr_lead_grid / 20.0, 0.0, 1.0)

    district_rows = []

    for dist in districts:
        cell_raw = [raw_lead_grid[i, j] for i, j in dist.cell_indices]
        cell_corr = [corr_lead_grid[i, j] for i, j in dist.cell_indices]
        cell_p10 = [p10_lead[i, j] for i, j in dist.cell_indices]
        cell_p90 = [p90_lead[i, j] for i, j in dist.cell_indices]
        cell_p64 = [p64_lead[i, j] for i, j in dist.cell_indices]
        cell_p115 = [p115_lead[i, j] for i, j in dist.cell_indices]
        cell_p15 = [p15_lead[i, j] for i, j in dist.cell_indices]

        raw_mean = float(np.mean(cell_raw))
        corr_p50 = float(np.mean(cell_corr))
        p10_val = float(np.mean(cell_p10))
        p90_val = float(np.mean(cell_p90))

        # Expected area fractions and max probabilities (strictly mean of cell exceedance probabilities)
        eaf_64 = float(np.mean(cell_p64))
        eaf_115 = float(np.mean(cell_p115))
        eaf_15 = float(np.mean(cell_p15))
        max_p64 = float(np.max(cell_p64))
        max_p115 = float(np.max(cell_p115))

        # Evaluate alert
        alert = evaluate_district_alert(
            p50_mm=corr_p50,
            max_cell_prob_64=max_p64,
            max_cell_prob_115=max_p115,
            expected_area_fraction_64=eaf_64,
            expected_area_fraction_15=eaf_15,
        )

        # Attributions (TreeSHAP grouped features in mm)
        attr_dict: dict[str, float] = {}
        if attributions:
            for grp_name, grp_grid in attributions.items():
                cell_vals = [grp_grid[i, j] for i, j in dist.cell_indices]
                attr_dict[grp_name] = round(float(np.mean(cell_vals)), 2)
        else:
            attr_dict = {
                "moisture_instability": 0.0,
                "circulation_vorticity": 0.0,
                "terrain_orography": 0.0,
                "regime_conditioning": 0.0,
                "nwp_baseline": round(corr_p50, 2),
            }

        row = {
            "district_id": dist.district_id,
            "district_name": dist.name,
            "state": dist.state,
            "lead_day": lead,
            "valid_date": valid_time,
            "raw_mean_mm": round(raw_mean, 1),
            "corrected_p50_mm": round(corr_p50, 1),
            "p10_mm": round(p10_val, 1),
            "p90_mm": round(p90_val, 1),
            "delta_mm": round(corr_p50 - raw_mean, 1),
            "expected_area_fraction_ge_64": round(eaf_64, 3),
            "expected_area_fraction_ge_115": round(eaf_115, 3),
            "max_cell_prob_ge_64": round(max_p64, 3),
            "max_cell_prob_ge_115": round(max_p115, 3),
            "dominant_regime": regime_name,
            "regime_confidence": round(regime_confidence, 2),
            "alert_level": alert.level,
            "alert_label": alert.label,
            "alert_action": alert.action,
            "alert_glyph": alert.glyph,
            "is_subgrid": dist.is_subgrid,
            "centroid_lat": dist.centroid_lat,
            "centroid_lon": dist.centroid_lon,
            "attributions": attr_dict,
        }
        district_rows.append(row)

    return district_rows


def build_districts_geojson(
    district_rows: list[dict[str, Any]],
    districts: list[DistrictMeta],
) -> dict[str, Any]:
    """Convert district forecast list into GeoJSON FeatureCollection."""
    features = []
    dist_map = {d.district_id: d for d in districts}

    for row in district_rows:
        d_meta = dist_map.get(row["district_id"])
        if d_meta:
            features.append(
                {
                    "type": "Feature",
                    "id": row["district_id"],
                    "geometry": d_meta.geometry,
                    "properties": {
                        **row,
                        "disclaimer": "Indicative; not an official IMD warning",
                    },
                }
            )

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def export_districts_csv(district_rows: list[dict[str, Any]]) -> str:
    """Export district forecasts to CSV string."""
    df = pd.DataFrame(district_rows)
    return df.to_csv(index=False)
