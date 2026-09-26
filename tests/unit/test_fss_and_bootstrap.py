"""
Unit tests for Fractions Skill Score (FSS) and Block Bootstrap Hypothesis Testing (Deliverable D5).
"""

import numpy as np

from varsha.verify.bootstrap import block_bootstrap_ci, paired_difference_bootstrap
from varsha.verify.fss import compute_fss_field, compute_multiscale_fss


def test_fss_perfect_forecast():
    """Verify FSS is 1.0 for a perfect match."""
    field = np.zeros((20, 20), dtype=float)
    field[5:10, 5:10] = 70.0  # Exceeds 64.5mm

    score = compute_fss_field(field, field, threshold=64.5, window_size=3)
    assert abs(score - 1.0) < 1e-4


def test_fss_zero_forecast():
    """Verify FSS drops when forecast misses completely."""
    obs = np.zeros((20, 20), dtype=float)
    obs[5:10, 5:10] = 70.0

    fcst = np.zeros((20, 20), dtype=float)  # All zero
    score = compute_fss_field(obs, fcst, threshold=64.5, window_size=3)
    assert score == 0.0


def test_multiscale_fss():
    """Verify multiscale FSS across scales and thresholds."""
    obs = np.random.uniform(0, 80, size=(5, 15, 15))
    fcst = obs + np.random.normal(0, 5, size=(5, 15, 15))

    res = compute_multiscale_fss(obs, fcst, thresholds=[15.6, 64.5], scales=[1, 3])
    assert "15.6mm" in res
    assert 1 in res["15.6mm"] and 3 in res["15.6mm"]


def test_block_bootstrap_ci():
    """Verify moving-block bootstrap confidence interval bounds."""
    data = np.array(
        [10.0, 12.0, 11.0, 9.0, 10.5, 11.2, 13.0, 10.1, 9.8, 12.5, 11.1, 10.4, 10.8, 11.5]
    )
    ci = block_bootstrap_ci(data, block_size=3, n_resamples=100)
    assert "mean" in ci
    assert ci["ci_low"] <= ci["mean"] <= ci["ci_high"]


def test_paired_difference_bootstrap():
    """Verify paired bootstrap hypothesis test."""
    obs = np.random.uniform(0, 100, size=(10, 10, 10))
    # Model A is closer to truth than Model B
    model_a = obs + np.random.normal(0, 2, size=(10, 10, 10))
    model_b = obs + np.random.normal(0, 15, size=(10, 10, 10))

    pair_res = paired_difference_bootstrap(
        obs_3d=obs,
        model_a_3d=model_a,
        model_b_3d=model_b,
        threshold=35.5,
        metric="ets",
        n_resamples=100,
    )
    assert "mean_diff" in pair_res
    assert "ci_95_low" in pair_res
    assert "p_value" in pair_res
