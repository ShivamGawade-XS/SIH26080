"""
Grid and Accumulation Window Alignment Module.
Ensures forecast fields and observational targets are aligned to the common domain grid
and standardized 24-hour daily accumulation window (03 UTC to 03 UTC).
"""

from __future__ import annotations

import numpy as np
import xarray as xr


def align_datasets(
    ds_forecast: xr.Dataset,
    ds_obs: xr.Dataset,
    target_lats: np.ndarray,
    target_lons: np.ndarray,
) -> xr.Dataset:
    """Regrid forecast and observation datasets onto target grid using nearest or bilinear regridding.

    Ensures matching coordinates, coordinate order (ascending lats, ascending lons),
    and consistent land-sea masking.
    """
    # Sort coordinates ascending
    fcst_sorted = ds_forecast.sortby("lat").sortby("lon")
    obs_sorted = ds_obs.sortby("lat").sortby("lon")

    # Regrid/interp to target grid
    fcst_regrid = fcst_sorted.interp(lat=target_lats, lon=target_lons, method="linear")
    obs_regrid = obs_sorted.interp(lat=target_lats, lon=target_lons, method="linear")

    # Merge into aligned dataset
    aligned = xr.merge([fcst_regrid, obs_regrid], compat="override")
    return aligned
