"""
Verification Slicing Module (Deliverable D5).
Evaluates metric ladders sliced along critical meteorological and operational dimensions:
1. By synoptic regime (Normal, Active, Break, Depression)
2. By forecast lead time (Day-1 to Day-5)
3. By IMD precipitation threshold (2.5, 15.6, 35.5, 64.5, 115.6 mm)
4. By geographical sub-region / climate zone
5. By calendar month (June, July, August, September)
"""

from __future__ import annotations

import numpy as np
import xarray as xr

from varsha.verify.metrics import continuous_metrics, evaluate_all_thresholds

REGIME_NAMES = {0: "normal", 1: "active", 2: "break", 3: "depression"}
MONTH_NAMES = {6: "June", 7: "July", 8: "August", 9: "September"}


def slice_metrics_by_regime(
    ds: xr.Dataset,
    fcst_3d: np.ndarray,  # (time, lat, lon)
    lead: int = 1,
) -> dict[str, dict]:
    """Slice continuous and categorical metrics by synoptic regime."""
    obs = ds["tp_obs"].values
    land = ds["land_mask"].values
    regimes = ds["synoptic_regime"].values
    len(regimes)

    results = {}
    for reg_id, reg_name in REGIME_NAMES.items():
        time_mask = regimes == reg_id
        if time_mask.sum() < 2:
            continue

        obs_sub = obs[time_mask]
        fcst_sub = fcst_3d[time_mask]

        # Apply land mask
        land_3d = np.broadcast_to(land[np.newaxis], obs_sub.shape)
        v = (land_3d > 0.5) & ~(np.isnan(obs_sub) | np.isnan(fcst_sub))

        cont = continuous_metrics(obs_sub[v], fcst_sub[v])
        cat = evaluate_all_thresholds(obs_sub[v], fcst_sub[v], thresholds=[15.6, 64.5])

        results[reg_name] = {
            "n_days": int(time_mask.sum()),
            "rmse": cont["rmse"],
            "mae": cont["mae"],
            "bias": cont["bias"],
            "ets_64_5": cat.get("64.5mm", {}).get("ets", 0.0),
            "csi_64_5": cat.get("64.5mm", {}).get("csi", 0.0),
            "pod_64_5": cat.get("64.5mm", {}).get("pod", 0.0),
            "far_64_5": cat.get("64.5mm", {}).get("far", 0.0),
        }

    return results


def slice_metrics_by_lead(
    ds: xr.Dataset,
    fcst_leads: dict[int, np.ndarray],  # lead -> (time, lat, lon)
) -> dict[int, dict]:
    """Slice metrics across Day-1 to Day-5."""
    obs = ds["tp_obs"].values
    land = ds["land_mask"].values
    land_3d = np.broadcast_to(land[np.newaxis], obs.shape)

    results = {}
    for lead, fcst in fcst_leads.items():
        v = (land_3d > 0.5) & ~(np.isnan(obs) | np.isnan(fcst))
        cont = continuous_metrics(obs[v], fcst[v])
        cat = evaluate_all_thresholds(obs[v], fcst[v], thresholds=[15.6, 64.5, 115.6])

        results[lead] = {
            "rmse": cont["rmse"],
            "mae": cont["mae"],
            "bias": cont["bias"],
            "correlation": cont["corr"],
            "ets_64_5": cat.get("64.5mm", {}).get("ets", 0.0),
            "csi_64_5": cat.get("64.5mm", {}).get("csi", 0.0),
            "fbi_64_5": cat.get("64.5mm", {}).get("fbi", 1.0),
        }

    return results
