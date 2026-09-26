"""
Fractions Skill Score (FSS) Module (Deliverable D5).
Computes spatial verification metric FSS across operational rainfall thresholds
and neighbourhood window scales (1x1, 3x3, 5x5, 9x9 grid cells) per Roberts & Lean (2008).
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import uniform_filter  # type: ignore[import-untyped]


def compute_fss_field(
    obs: np.ndarray,
    fcst: np.ndarray,
    threshold: float,
    window_size: int = 3,
) -> float:
    """Compute Fractions Skill Score for 2D spatial fields at a given threshold & window scale.

    Parameters
    ----------
    obs : 2D array (lat, lon) of observed precipitation
    fcst : 2D array (lat, lon) of forecast precipitation
    threshold : float threshold in mm/day
    window_size : int odd neighbourhood window size (e.g., 1, 3, 5, 9)
    """
    valid = ~(np.isnan(obs) | np.isnan(fcst))
    if np.sum(valid) < 10:
        return 0.0

    # Binary exceedance fields
    i_obs = (obs >= threshold).astype(float)
    i_fcst = (fcst >= threshold).astype(float)

    # If window_size is 1, neighbourhood fraction is the binary field itself
    if window_size == 1:
        f_obs = i_obs
        f_fcst = i_fcst
    else:
        # Compute neighbourhood fractions using uniform spatial filter
        f_obs = uniform_filter(i_obs, size=window_size, mode="constant", cval=0.0)
        f_fcst = uniform_filter(i_fcst, size=window_size, mode="constant", cval=0.0)

    # Fractions Brier Score (FBS)
    fbs = np.mean((f_fcst[valid] - f_obs[valid]) ** 2)
    # Worst possible FBS (FBS_ref)
    fbs_ref = np.mean(f_fcst[valid] ** 2) + np.mean(f_obs[valid] ** 2)

    if fbs_ref < 1e-8:
        # Both fields have zero events
        return 1.0

    fss = 1.0 - (fbs / fbs_ref)
    return float(np.clip(fss, 0.0, 1.0))


def compute_multiscale_fss(
    obs_3d: np.ndarray,
    fcst_3d: np.ndarray,
    thresholds: list[float] | None = None,
    scales: list[int] | None = None,
) -> dict:
    """Compute multiscale FSS across multiple days (time, lat, lon)."""
    if thresholds is None:
        thresholds = [15.6, 35.5, 64.5, 115.6]
    if scales is None:
        scales = [1, 3, 5, 9]

    n_time = obs_3d.shape[0]
    results: dict[str, dict[int, float]] = {}

    for thresh in thresholds:
        thresh_key = f"{thresh:.1f}mm"
        results[thresh_key] = {}
        for scale in scales:
            scores = []
            for t in range(n_time):
                score = compute_fss_field(obs_3d[t], fcst_3d[t], thresh, scale)
                scores.append(score)
            results[thresh_key][scale] = round(float(np.mean(scores)), 4)

    return results
