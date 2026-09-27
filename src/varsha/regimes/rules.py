"""
Objective Rule-Based Regime Labelling Engine (Deliverable D1).
Calculates ground-truth synoptic regime labels and geographic compound keys
from analysis / observation fields.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import xarray as xr

from varsha.config import VarshaConfig

SYNOPTIC_REGIMES = ["normal", "active", "break", "depression"]
GEOGRAPHIC_ZONES = ["interior", "orographic_ghats", "coastal_west", "orographic_ne"]


@dataclass
class RegimeLabelResult:
    daily_synoptic_df: (
        pd.DataFrame
    )  # index: time, cols: [regime, cmz_anomaly, max_vorticity, min_mslp_anom]
    grid_compound_keys: np.ndarray  # (time, lat, lon) strings or integer codes
    zone_grid: np.ndarray  # (lat, lon) static zone assignment


def compute_cmz_anomalies(ds: xr.Dataset, config: VarshaConfig) -> pd.Series:
    """Compute daily standardized precipitation anomaly over Core Monsoon Zone."""
    cfg = config.raw_configs.get("data", {}).get(
        "core_monsoon_zone", {"lat_min": 18.0, "lat_max": 28.0, "lon_min": 73.0, "lon_max": 86.0}
    )

    cmz = ds["tp_obs"].sel(
        lat=slice(cfg["lat_min"], cfg["lat_max"]), lon=slice(cfg["lon_min"], cfg["lon_max"])
    )

    # Area-mean daily series over CMZ
    cmz_mean = cmz.mean(dim=["lat", "lon"]).to_series()

    # Standardize
    mu = cmz_mean.mean()
    sigma = cmz_mean.std()
    if sigma < 1e-6:
        sigma = 1.0

    anomaly = (cmz_mean - mu) / sigma
    return anomaly


def label_synoptic_regimes(ds: xr.Dataset, config: VarshaConfig) -> pd.DataFrame:
    """
    Apply objective rule thresholds from regimes.yaml:
    - active: CMZ anomaly >= 0.7 for >= 3 consecutive days
    - break: CMZ anomaly <= -0.7 for >= 3 consecutive days
    - depression: 850 hPa vorticity >= 3.0e-5 and MSLP depression >= 2.0 hPa for >= 2 days
    - normal: default
    """
    regimes_cfg = config.raw_configs.get("regimes", {}).get("synoptic_regimes", {})
    act_thresh = regimes_cfg.get("active", {}).get("cmz_anomaly_threshold", 0.7)
    brk_thresh = regimes_cfg.get("break", {}).get("cmz_anomaly_threshold", -0.7)
    vort_thresh = regimes_cfg.get("depression", {}).get("vorticity_850_min", 3.0e-5)
    mslp_thresh = regimes_cfg.get("depression", {}).get("mslp_depression_min", 2.0)

    cmz_anom = compute_cmz_anomalies(ds, config)
    times = ds["time"].values

    # Max vorticity and min MSLP anomaly per day over domain
    max_vort = ds["vort850_anl"].max(dim=["lat", "lon"]).values
    min_mslp = ds["mslp_anl"].min(dim=["lat", "lon"]).values

    n_days = len(times)
    labels = ["normal"] * n_days

    # 1. Flag depression days (vortex criteria)
    dep_mask = (max_vort >= vort_thresh) & (min_mslp <= -mslp_thresh)

    # 2. Flag active / break days
    act_mask = cmz_anom.values >= act_thresh
    brk_mask = cmz_anom.values <= brk_thresh

    # Apply persistence filtering (minimum spell length)
    for i in range(n_days):
        if dep_mask[i]:
            # check spell >= 2
            start = max(0, i - 1)
            end = min(n_days, i + 2)
            if np.sum(dep_mask[start:end]) >= 2:
                labels[i] = "depression"
                continue

        if act_mask[i]:
            # check spell >= 3
            start = max(0, i - 2)
            end = min(n_days, i + 3)
            if np.sum(act_mask[start:end]) >= 3:
                labels[i] = "active"
                continue

        if brk_mask[i]:
            # check spell >= 3
            start = max(0, i - 2)
            end = min(n_days, i + 3)
            if np.sum(brk_mask[start:end]) >= 3:
                labels[i] = "break"
                continue

    df = pd.DataFrame(
        {
            "time": times,
            "regime": labels,
            "cmz_anomaly": cmz_anom.values,
            "max_vorticity": max_vort,
            "min_mslp_anom": min_mslp,
        }
    ).set_index("time")

    return df


def assign_geographic_zones(ds: xr.Dataset, config: VarshaConfig) -> np.ndarray:
    """Assign static geographic zone matrix (n_lat, n_lon)."""
    lats = ds["lat"].values
    lons = ds["lon"].values
    elev = ds["elevation"].values
    dist_c = ds["dist_coast"].values

    lat_grid, lon_grid = np.meshgrid(lats, lons, indexing="ij")

    # Default: interior
    zones = np.full(lat_grid.shape, "interior", dtype=object)

    # Western Ghats
    ghats_mask = (elev >= 400.0) & (lon_grid <= 76.5) & (lat_grid >= 8.0) & (lat_grid <= 21.0)
    zones[ghats_mask] = "orographic_ghats"

    # Coastal West
    coastal_mask = (
        (dist_c <= 50.0) & (lon_grid <= 75.0) & (lat_grid >= 8.0) & (lat_grid <= 23.0) & ~ghats_mask
    )
    zones[coastal_mask] = "coastal_west"

    # Northeast Hills
    ne_mask = (elev >= 300.0) & (lon_grid >= 88.0) & (lat_grid >= 22.0)
    zones[ne_mask] = "orographic_ne"

    return zones


def build_compound_regime_dataset(ds: xr.Dataset, config: VarshaConfig) -> xr.Dataset:
    """Compute and attach synoptic regime series and compound regime grids to dataset."""
    df_synoptic = label_synoptic_regimes(ds, config)
    zone_grid = assign_geographic_zones(ds, config)

    # Map regimes to integer codes: 0=normal, 1=active, 2=break, 3=depression
    regime_map = {r: i for i, r in enumerate(SYNOPTIC_REGIMES)}
    zone_map = {z: i for i, z in enumerate(GEOGRAPHIC_ZONES)}

    synoptic_codes = [regime_map[r] for r in df_synoptic["regime"]]
    zone_codes = np.vectorize(zone_map.get)(zone_grid)

    ds_out = ds.copy()
    ds_out["synoptic_regime"] = ("time", np.array(synoptic_codes, dtype=np.int32))
    ds_out["synoptic_regime_name"] = ("time", df_synoptic["regime"].values)
    ds_out["cmz_anomaly"] = ("time", df_synoptic["cmz_anomaly"].values.astype(np.float32))
    ds_out["geographic_zone"] = (["lat", "lon"], zone_codes.astype(np.int32))

    return ds_out
