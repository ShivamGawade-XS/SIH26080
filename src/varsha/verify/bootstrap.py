"""
Block Bootstrap Uncertainty Estimation and Paired Hypothesis Testing (Deliverable D5).
Performs block bootstrap over days (e.g., 7-day or week blocks) to preserve temporal correlation,
estimating 95% Confidence Intervals for headline skill metrics and paired differences (B4-B2, B4-B1, B2-B1).
"""

from __future__ import annotations

import numpy as np

from varsha.verify.metrics import categorical_scores


def block_bootstrap_ci(
    values: np.ndarray,
    block_size: int = 7,
    n_resamples: int = 1000,
    ci_level: float = 0.95,
    seed: int = 42,
) -> dict:
    """Compute moving-block bootstrap confidence interval for 1D array of daily metric values."""
    n = len(values)
    if n < block_size * 2:
        return {
            "mean": float(np.mean(values)),
            "ci_low": float(np.percentile(values, 2.5)),
            "ci_high": float(np.percentile(values, 97.5)),
        }

    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n / block_size))
    max_start = n - block_size

    resample_means = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        starts = rng.integers(0, max_start + 1, size=n_blocks)
        indices = np.concatenate([np.arange(s, s + block_size) for s in starts])[:n]
        resample_means[i] = np.mean(values[indices])

    alpha = (1.0 - ci_level) / 2.0
    low = np.percentile(resample_means, alpha * 100.0)
    high = np.percentile(resample_means, (1.0 - alpha) * 100.0)

    return {
        "mean": round(float(np.mean(values)), 4),
        "ci_low": round(float(low), 4),
        "ci_high": round(float(high), 4),
    }


def paired_difference_bootstrap(
    obs_3d: np.ndarray,  # (time, lat, lon)
    model_a_3d: np.ndarray,
    model_b_3d: np.ndarray,
    threshold: float = 64.5,
    metric: str = "ets",
    block_size: int = 7,
    n_resamples: int = 500,
    seed: int = 42,
) -> dict:
    """Compute block bootstrap paired difference (Model A - Model B) on 3D daily grids."""
    n_time = obs_3d.shape[0]
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n_time / block_size))
    max_start = max(0, n_time - block_size)

    # Compute overall baseline metrics
    obs_flat = obs_3d.flatten()
    a_flat = model_a_3d.flatten()
    b_flat = model_b_3d.flatten()
    valid = ~(np.isnan(obs_flat) | np.isnan(a_flat) | np.isnan(b_flat))

    score_a = categorical_scores(obs_flat[valid], a_flat[valid], threshold)
    score_b = categorical_scores(obs_flat[valid], b_flat[valid], threshold)
    baseline_diff = float(score_a[metric]) - float(score_b[metric])

    diffs = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        if max_start > 0:
            starts = rng.integers(0, max_start + 1, size=n_blocks)
            day_idx = np.concatenate([np.arange(s, s + block_size) for s in starts])[:n_time]
        else:
            day_idx = np.asarray(rng.choice(n_time, size=n_time, replace=True))

        sub_obs = obs_3d[day_idx].flatten()
        sub_a = model_a_3d[day_idx].flatten()
        sub_b = model_b_3d[day_idx].flatten()
        v = ~(np.isnan(sub_obs) | np.isnan(sub_a) | np.isnan(sub_b))

        sa = float(categorical_scores(sub_obs[v], sub_a[v], threshold)[metric])
        sb = float(categorical_scores(sub_obs[v], sub_b[v], threshold)[metric])
        diffs[i] = sa - sb

    ci_low = np.percentile(diffs, 2.5)
    ci_high = np.percentile(diffs, 97.5)
    p_value = float(np.mean(diffs <= 0.0))  # Probability that A does not beat B

    return {
        "metric": metric,
        "threshold": threshold,
        "model_a_score": round(float(score_a[metric]), 4),
        "model_b_score": round(float(score_b[metric]), 4),
        "mean_diff": round(float(baseline_diff), 4),
        "ci_95_low": round(float(ci_low), 4),
        "ci_95_high": round(float(ci_high), 4),
        "p_value": round(p_value, 4),
        "significantly_positive": bool(ci_low > 0.0),
    }
