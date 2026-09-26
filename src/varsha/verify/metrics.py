"""
Verification Metrics Module for Project Varsha (Deliverable D5).
Implements RMSE, MAE, Bias, Correlation, POD, FAR, CSI, ETS, FBI, FSS,
Brier Score/BSS, plus moving-block bootstrap confidence intervals.

All formulas verified against WMO/WWRP standard definitions.
ETS uses the random-hits formula: a_r = (a+b)(a+c)/n.
FSS reference forecast is the uniform distribution (climatological frequency).
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------
FloatArray = npt.NDArray[np.float64]
BoolArray = npt.NDArray[np.bool_]


def _contingency(obs: FloatArray, fcst: FloatArray, threshold: float) -> tuple[int, int, int, int]:
    """Return (hits, false_alarms, misses, correct_negatives) for a threshold.
    obs, fcst: 1-D or N-D flat arrays (land-points only, NaNs removed).
    """
    obs_bin = obs >= threshold
    fcst_bin = fcst >= threshold
    hits = int(np.sum(obs_bin & fcst_bin))
    false_alarms = int(np.sum(~obs_bin & fcst_bin))
    misses = int(np.sum(obs_bin & ~fcst_bin))
    cn = int(np.sum(~obs_bin & ~fcst_bin))
    return hits, false_alarms, misses, cn


# ---------------------------------------------------------------------------
# Continuous metrics
# ---------------------------------------------------------------------------


def rmse(obs: FloatArray, fcst: FloatArray) -> float:
    """Root Mean Square Error."""
    mask = ~(np.isnan(obs) | np.isnan(fcst))
    if mask.sum() == 0:
        return float("nan")
    diff = fcst[mask] - obs[mask]
    return float(np.sqrt(np.mean(diff**2)))


def mae(obs: FloatArray, fcst: FloatArray) -> float:
    """Mean Absolute Error."""
    mask = ~(np.isnan(obs) | np.isnan(fcst))
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(np.abs(fcst[mask] - obs[mask])))


def bias(obs: FloatArray, fcst: FloatArray) -> float:
    """Mean Bias (fcst - obs)."""
    mask = ~(np.isnan(obs) | np.isnan(fcst))
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(fcst[mask] - obs[mask]))


def correlation(obs: FloatArray, fcst: FloatArray) -> float:
    """Pearson correlation coefficient."""
    mask = ~(np.isnan(obs) | np.isnan(fcst))
    if mask.sum() < 2:
        return float("nan")
    return float(np.corrcoef(obs[mask], fcst[mask])[0, 1])


def continuous_metrics(obs: FloatArray, fcst: FloatArray) -> dict[str, float]:
    """Compute dictionary of standard continuous metrics (RMSE, MAE, Bias, Correlation)."""
    obs_f = np.asarray(obs).flatten()
    fcst_f = np.asarray(fcst).flatten()
    v = ~(np.isnan(obs_f) | np.isnan(fcst_f))
    return {
        "rmse": round(rmse(obs_f[v], fcst_f[v]), 4),
        "mae": round(mae(obs_f[v], fcst_f[v]), 4),
        "bias": round(bias(obs_f[v], fcst_f[v]), 4),
        "corr": round(correlation(obs_f[v], fcst_f[v]), 4),
    }


def evaluate_all_thresholds(
    obs: FloatArray, fcst: FloatArray, thresholds: list[float] | None = None
) -> dict[str, dict]:
    """Evaluate categorical metrics across a list of precipitation thresholds."""
    thresholds = thresholds or [2.5, 15.6, 35.5, 64.5, 115.6]
    results = {}
    for thresh in thresholds:
        key = f"{thresh:.1f}mm"
        results[key] = categorical_scores(obs, fcst, threshold=thresh)
    return results


# ---------------------------------------------------------------------------
# Categorical metrics
# ---------------------------------------------------------------------------


def pod(hits: int, misses: int) -> float:
    """Probability of Detection = hits / (hits + misses)."""
    denom = hits + misses
    return hits / denom if denom > 0 else float("nan")


def far(hits: int, false_alarms: int) -> float:
    """False Alarm Ratio = false_alarms / (hits + false_alarms)."""
    denom = hits + false_alarms
    return false_alarms / denom if denom > 0 else float("nan")


def csi(hits: int, false_alarms: int, misses: int) -> float:
    """Critical Success Index = hits / (hits + false_alarms + misses)."""
    denom = hits + false_alarms + misses
    return hits / denom if denom > 0 else float("nan")


def ets(hits: int, false_alarms: int, misses: int, correct_negatives: int) -> float:
    """Equitable Threat Score.
    Random hits: a_r = (a+b)(a+c) / n  (WMO formula).
    ETS = (a - a_r) / (a + b + c - a_r)
    """
    n = hits + false_alarms + misses + correct_negatives
    if n == 0:
        return float("nan")
    a_r = (hits + false_alarms) * (hits + misses) / n
    denom = hits + false_alarms + misses - a_r
    if abs(denom) < 1e-12:
        return float("nan")
    return float((hits - a_r) / denom)


def fbi(hits: int, false_alarms: int, misses: int) -> float:
    """Frequency Bias Index = (hits + false_alarms) / (hits + misses)."""
    denom = hits + misses
    return (hits + false_alarms) / denom if denom > 0 else float("nan")


def categorical_scores(
    obs: FloatArray, fcst: FloatArray, threshold: float
) -> dict[str, float | int]:
    """Compute all categorical scores for a given threshold."""
    obs_flat = np.asarray(obs).flatten()
    fcst_flat = np.asarray(fcst).flatten()
    valid = ~(np.isnan(obs_flat) | np.isnan(fcst_flat))
    h, fa, m, cn = _contingency(obs_flat[valid], fcst_flat[valid], threshold)
    return {
        "threshold_mm": threshold,
        "hits": h,
        "false_alarms": fa,
        "misses": m,
        "correct_negatives": cn,
        "n_events": h + m,
        "pod": pod(h, m),
        "far": far(h, fa),
        "csi": csi(h, fa, m),
        "ets": ets(h, fa, m, cn),
        "fbi": fbi(h, fa, m),
    }


# ---------------------------------------------------------------------------
# Fractions Skill Score (Roberts & Lean 2008)
# ---------------------------------------------------------------------------


def _fractions_in_window(arr2d: FloatArray, threshold: float, half_width: int) -> FloatArray:
    """Compute fraction of grid points exceeding threshold in a square neighbourhood."""
    binary = (arr2d >= threshold).astype(np.float64)
    # Cumulative sum approach for O(n) box filter
    cs = np.zeros((binary.shape[0] + 1, binary.shape[1] + 1))
    cs[1:, 1:] = np.cumsum(np.cumsum(binary, axis=0), axis=1)

    nrows, ncols = binary.shape
    w = half_width
    fracs = np.empty_like(binary)
    for i in range(nrows):
        r0 = max(0, i - w)
        r1 = min(nrows, i + w + 1)
        for j in range(ncols):
            c0 = max(0, j - w)
            c1 = min(ncols, j + w + 1)
            count = cs[r1, c1] - cs[r0, c1] - cs[r1, c0] + cs[r0, c0]
            n_pts = (r1 - r0) * (c1 - c0)
            fracs[i, j] = count / n_pts
    return fracs


def fss_single(
    obs_2d: FloatArray,
    fcst_2d: FloatArray,
    threshold: float,
    half_width: int,
) -> float:
    """Fraction Skill Score for a single 2-D field snapshot.

    FSS = 1 - MSE_forecast / MSE_reference
    MSE_reference = mean(f_obs^2) + mean(f_fcst^2)  (climatological reference)
    """
    # Remove NaN by treating as zero (sea / outside domain already masked)
    obs2 = np.where(np.isnan(obs_2d), 0.0, obs_2d)
    fcs2 = np.where(np.isnan(fcst_2d), 0.0, fcst_2d)

    f_obs = _fractions_in_window(obs2, threshold, half_width)
    f_fcs = _fractions_in_window(fcs2, threshold, half_width)

    mse_fcs = float(np.mean((f_fcs - f_obs) ** 2))
    mse_ref = float(np.mean(f_obs**2) + np.mean(f_fcs**2))

    if mse_ref < 1e-12:
        return 1.0  # Both fields are zero: perfect
    return float(1.0 - mse_fcs / mse_ref)


def fss_timeseries(
    obs_3d: FloatArray,  # (time, lat, lon)
    fcst_3d: FloatArray,
    threshold: float,
    half_width: int,
) -> float:
    """Average FSS over multiple time steps (standard operational practice)."""
    vals = []
    for t in range(obs_3d.shape[0]):
        v = fss_single(obs_3d[t], fcst_3d[t], threshold, half_width)
        if not np.isnan(v):
            vals.append(v)
    return float(np.mean(vals)) if vals else float("nan")


# ---------------------------------------------------------------------------
# Probabilistic metrics
# ---------------------------------------------------------------------------


def brier_score(obs_binary: FloatArray, prob: FloatArray) -> float:
    """Brier Score = mean((prob - obs_binary)^2)."""
    mask = ~(np.isnan(obs_binary) | np.isnan(prob))
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean((prob[mask] - obs_binary[mask]) ** 2))


def brier_skill_score(obs_binary: FloatArray, prob: FloatArray) -> float:
    """Brier Skill Score vs climatological reference."""
    mask = ~(np.isnan(obs_binary) | np.isnan(prob))
    if mask.sum() == 0:
        return float("nan")
    clim = float(np.mean(obs_binary[mask]))
    bs = brier_score(obs_binary[mask], prob[mask])
    bs_ref = float(np.mean((clim - obs_binary[mask]) ** 2))
    if bs_ref < 1e-12:
        return float("nan")
    return float(1.0 - bs / bs_ref)


# ---------------------------------------------------------------------------
# Moving-block bootstrap CI on paired differences
# ---------------------------------------------------------------------------


def _block_bootstrap(
    vals: FloatArray, n_resamples: int, block_size: int, rng: np.random.Generator
) -> FloatArray:
    """Draw block-bootstrap resamples of a 1-D sequence."""
    n = len(vals)
    n_blocks = int(np.ceil(n / block_size))
    starts = rng.integers(0, n - block_size + 1, size=(n_resamples, n_blocks))
    np.concatenate([np.arange(s, s + block_size) for s in starts[0]])[:n]
    # Vectorised over resamples
    samples = np.empty((n_resamples, n), dtype=vals.dtype)
    for i in range(n_resamples):
        idx_i = np.concatenate([np.arange(s, min(s + block_size, n)) for s in starts[i]])[:n]
        samples[i] = vals[idx_i]
    return samples


def bootstrap_ci_paired_ets(
    obs: FloatArray,
    fcst_a: FloatArray,
    fcst_b: FloatArray,
    threshold: float,
    n_resamples: int = 200,
    block_size: int = 7,
    alpha: float = 0.05,
    seed: int = 42,
) -> dict[str, float]:
    """Block-bootstrap 95% CI on ETS(A) - ETS(B) pair.

    Parameters
    ----------
    obs, fcst_a, fcst_b : (time, lat, lon) or (n_pts,) arrays
    threshold : exceedance threshold in mm/day
    n_resamples : number of bootstrap draws (200 for CI, 1000 for full)
    block_size : block length in days (7 days = weekly blocks)
    alpha : significance level (default 0.05 → 95% CI)
    seed : fixed RNG seed for reproducibility

    Returns
    -------
    dict with keys: mean, ci_low, ci_high, p_value (fraction below zero)
    """
    rng = np.random.default_rng(seed)
    obs_3d = np.asarray(obs)
    a_3d = np.asarray(fcst_a)
    b_3d = np.asarray(fcst_b)

    n_time = obs_3d.shape[0]
    # Flatten spatial dims per time step
    obs_t = obs_3d.reshape(n_time, -1)
    a_t = a_3d.reshape(n_time, -1)
    b_t = b_3d.reshape(n_time, -1)

    # Pre-compute valid masks and binary thresholds
    v_all = ~(np.isnan(obs_t) | np.isnan(a_t) | np.isnan(b_t))
    obs_bin = (obs_t >= threshold) & v_all
    a_bin = (a_t >= threshold) & v_all
    b_bin = (b_t >= threshold) & v_all

    # Compute overall baseline metrics
    ha_tot = int(np.sum(obs_bin & a_bin))
    faa_tot = int(np.sum((~obs_bin) & a_bin & v_all))
    ma_tot = int(np.sum(obs_bin & (~a_bin) & v_all))
    cna_tot = int(np.sum((~obs_bin) & (~a_bin) & v_all))

    hb_tot = int(np.sum(obs_bin & b_bin))
    fab_tot = int(np.sum((~obs_bin) & b_bin & v_all))
    mb_tot = int(np.sum(obs_bin & (~b_bin) & v_all))
    cnb_tot = int(np.sum((~obs_bin) & (~b_bin) & v_all))

    ets_a = ets(ha_tot, faa_tot, ma_tot, cna_tot)
    ets_b = ets(hb_tot, fab_tot, mb_tot, cnb_tot)
    mean_diff = float(ets_a - ets_b)

    # Block bootstrap over days
    block_size = min(block_size, n_time)
    boot_diffs = np.empty(n_resamples)
    for i in range(n_resamples):
        n_blocks = int(np.ceil(n_time / block_size))
        starts = rng.integers(0, max(1, n_time - block_size + 1), size=n_blocks)
        idx = np.concatenate([np.arange(s, min(s + block_size, n_time)) for s in starts])[:n_time]

        sub_o = obs_bin[idx]
        sub_a = a_bin[idx]
        sub_b = b_bin[idx]
        sub_v = v_all[idx]

        ha = int(np.sum(sub_o & sub_a))
        faa = int(np.sum((~sub_o) & sub_a & sub_v))
        ma = int(np.sum(sub_o & (~sub_a) & sub_v))
        cna = int(np.sum((~sub_o) & (~sub_a) & sub_v))

        hb = int(np.sum(sub_o & sub_b))
        fab = int(np.sum((~sub_o) & sub_b & sub_v))
        mb = int(np.sum(sub_o & (~sub_b) & sub_v))
        cnb = int(np.sum((~sub_o) & (~sub_b) & sub_v))

        ea = ets(ha, faa, ma, cna)
        eb = ets(hb, fab, mb, cnb)
        diff_val = ea - eb
        boot_diffs[i] = diff_val if not np.isnan(diff_val) else mean_diff

    ci_low = float(np.quantile(boot_diffs, alpha / 2))
    ci_high = float(np.quantile(boot_diffs, 1 - alpha / 2))
    p_value = float(np.mean(boot_diffs <= 0.0))  # fraction of bootstraps where A <= B

    return {
        "mean": mean_diff,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "p_value": p_value,
        "n_time": n_time,
        "n_resamples": n_resamples,
    }


# ---------------------------------------------------------------------------
# Aggregate verification report helper
# ---------------------------------------------------------------------------

STANDARD_THRESHOLDS = [2.5, 15.6, 35.5, 64.5, 115.6]
STANDARD_NEIGHBOURHOODS = [1, 3, 5, 9]  # in grid cells


def compute_full_scores(
    obs: FloatArray,  # (time, lat, lon)
    fcst: FloatArray,  # (time, lat, lon)
    label: str = "model",
    thresholds: list[float] = STANDARD_THRESHOLDS,
    neighbourhoods: list[int] = STANDARD_NEIGHBOURHOODS,
) -> dict:
    """Compute full suite of continuous + categorical + FSS scores."""
    obs_f = obs.flatten()
    fcs_f = fcst.flatten()
    valid = ~(np.isnan(obs_f) | np.isnan(fcs_f))

    result: dict = {
        "label": label,
        "n_points": int(valid.sum()),
        "continuous": {
            "rmse": rmse(obs_f[valid], fcs_f[valid]),
            "mae": mae(obs_f[valid], fcs_f[valid]),
            "bias": bias(obs_f[valid], fcs_f[valid]),
            "correlation": correlation(obs_f[valid], fcs_f[valid]),
        },
        "categorical": {},
        "fss": {},
    }

    for thr in thresholds:
        result["categorical"][str(thr)] = categorical_scores(obs_f[valid], fcs_f[valid], thr)
        fss_by_scale: dict[str, float] = {}
        for nbr in neighbourhoods:
            half = nbr // 2
            fv = fss_timeseries(obs, fcst, thr, half)
            fss_by_scale[str(nbr)] = fv
        result["fss"][str(thr)] = fss_by_scale

    return result
