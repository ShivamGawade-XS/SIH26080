"""
Predictor Feature Extraction and Engineering for Project Varsha.
Extracts forecast-side domain-scale and grid-cell level features for regime classification
and rainfall post-processing models.
"""

from __future__ import annotations

import numpy as np
import xarray as xr


def extract_all_domain_synoptic_predictors(ds: xr.Dataset, lead: int) -> np.ndarray:
    """Extract domain-aggregated forecast-side synoptic features for all time steps at once.

    Returns (n_time, 9) feature matrix in vectorized NumPy operations.
    """
    lat = ds["lat"].values
    lon = ds["lon"].values
    n_time = ds.sizes["time"]

    tp_raw = ds["tp_raw"].sel(lead=lead).values
    u850 = ds["u850"].sel(lead=lead).values
    v850 = ds["v850"].sel(lead=lead).values
    vort = ds["vort850"].sel(lead=lead).values
    mslp = ds["mslp_anom"].sel(lead=lead).values
    pwat = ds["pwat"].sel(lead=lead).values
    cape = ds["cape"].sel(lead=lead).values

    # Core Monsoon Zone (CMZ: 18-28N, 73-88E)
    cmz_lat_idx = np.where((lat >= 18.0) & (lat <= 28.0))[0]
    cmz_lon_idx = np.where((lon >= 73.0) & (lon <= 88.0))[0]

    if len(cmz_lat_idx) > 0 and len(cmz_lon_idx) > 0:
        cmz_rain = tp_raw[:, cmz_lat_idx[:, None], cmz_lon_idx].mean(axis=(1, 2))
    else:
        cmz_rain = tp_raw.mean(axis=(1, 2))

    # Low-Level Jet (LLJ: 10-18N, 70-80E)
    llj_lat_idx = np.where((lat >= 10.0) & (lat <= 18.0))[0]
    llj_lon_idx = np.where((lon >= 70.0) & (lon <= 80.0))[0]
    if len(llj_lat_idx) > 0 and len(llj_lon_idx) > 0:
        u_llj = u850[:, llj_lat_idx[:, None], llj_lon_idx]
        v_llj = v850[:, llj_lat_idx[:, None], llj_lon_idx]
        llj_speed = np.mean(np.sqrt(u_llj**2 + v_llj**2), axis=(1, 2))
    else:
        llj_speed = np.mean(np.sqrt(u850**2 + v850**2), axis=(1, 2))

    # Trough latitude proxy
    if len(cmz_lon_idx) > 0:
        mslp_strip = mslp[:, :, cmz_lon_idx].mean(axis=2)  # (n_time, lat)
    else:
        mslp_strip = mslp.mean(axis=2)
    min_lat_idx = np.argmin(mslp_strip, axis=1)
    trough_lat = lat[min_lat_idx]

    # Max vorticity & Min MSLP
    max_vort = vort.max(axis=(1, 2))
    min_mslp = mslp.min(axis=(1, 2))

    # Domain averages
    mean_pwat = pwat.mean(axis=(1, 2))
    mean_cape = cape.mean(axis=(1, 2))

    lead_col = np.full(n_time, float(lead), dtype=np.float32)
    day_of_season = ((np.arange(n_time) % 122) + 1).astype(np.float32)

    return np.column_stack(
        [
            cmz_rain,
            llj_speed,
            trough_lat,
            max_vort,
            min_mslp,
            mean_pwat,
            mean_cape,
            lead_col,
            day_of_season,
        ]
    ).astype(np.float32)


DOMAIN_PREDICTOR_NAMES = [
    "cmz_fcst_rain",
    "llj_speed",
    "trough_lat",
    "max_vort850",
    "min_mslp_anom",
    "mean_pwat",
    "mean_cape",
    "lead",
    "day_of_season",
]
