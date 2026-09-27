"""
Probability Calibration and Monotone Consistency Module (Deliverable D3).
Provides Isotonic and Platt scaling calibration, and enforces strict
monotone probability ordering across operational rainfall thresholds:
P(>=204.5 mm) <= P(>=115.6 mm) <= P(>=64.5 mm).
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.isotonic import IsotonicRegression  # type: ignore[import-untyped]
from sklearn.linear_model import LogisticRegression  # type: ignore[import-untyped]


class ProbabilityCalibrator:
    """Calibrates raw model probabilities using Isotonic or Platt scaling."""

    def __init__(self, method: str = "isotonic") -> None:
        self.method = method
        self._calibrator: Any = None

    def fit(self, raw_probs: np.ndarray, y_true: np.ndarray) -> ProbabilityCalibrator:
        """Fit calibration curve on validation set."""
        valid = ~(np.isnan(raw_probs) | np.isnan(y_true))
        raw_probs = np.clip(raw_probs[valid], 1e-6, 1.0 - 1e-6)
        y = y_true[valid].astype(int)

        n_pos = np.sum(y == 1)
        if n_pos < 10 or self.method == "platt":
            # Fall back to Platt scaling (logistic) when positive samples are scarce
            self._calibrator = LogisticRegression(solver="lbfgs")
            self._calibrator.fit(raw_probs.reshape(-1, 1), y)
            self.method = "platt"
        else:
            self._calibrator = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
            self._calibrator.fit(raw_probs, y)
        return self

    def predict_proba(self, raw_probs: np.ndarray) -> np.ndarray:
        """Transform raw probabilities to calibrated probabilities."""
        if self._calibrator is None:
            return np.clip(raw_probs, 0.0, 1.0)

        shape = raw_probs.shape
        flat_p = raw_probs.flatten()
        if self.method == "platt":
            cal = self._calibrator.predict_proba(flat_p.reshape(-1, 1))[:, 1]
        else:
            cal = self._calibrator.predict(flat_p)

        return np.clip(cal.reshape(shape), 0.0, 1.0)


def enforce_monotone_consistency(
    p64: np.ndarray, p115: np.ndarray, p204: np.ndarray | None = None
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """Enforce monotone ordering P(>=204.5) <= P(>=115.6) <= P(>=64.5).

    Any physical inversion where a higher threshold has a higher predicted probability
    is adjusted by projecting onto the isotonic cone.
    """
    p64_adj = np.clip(p64, 0.0, 1.0)
    p115_adj = np.minimum(p64_adj, np.clip(p115, 0.0, 1.0))
    p204_adj = None
    if p204 is not None:
        p204_adj = np.minimum(p115_adj, np.clip(p204, 0.0, 1.0))

    return p64_adj, p115_adj, p204_adj


def compute_reliability_curve(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> dict:
    """Compute empirical reliability curve and sharpness histogram for D3/D5."""
    valid = ~(np.isnan(y_true) | np.isnan(y_prob))
    yt = y_true[valid].astype(int)
    yp = np.clip(y_prob[valid], 0.0, 1.0)

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    observed_freq = np.zeros(n_bins, dtype=float)
    mean_predicted = np.zeros(n_bins, dtype=float)
    bin_counts = np.zeros(n_bins, dtype=int)

    total_samples = len(yp)
    for i in range(n_bins):
        in_bin = (yp >= bins[i]) & (yp <= bins[i + 1] if i == n_bins - 1 else yp < bins[i + 1])
        count = int(np.sum(in_bin))
        bin_counts[i] = count
        if count > 0:
            observed_freq[i] = float(np.mean(yt[in_bin]))
            mean_predicted[i] = float(np.mean(yp[in_bin]))
        else:
            observed_freq[i] = float(bin_centers[i])
            mean_predicted[i] = float(bin_centers[i])

    # Brier Score & BSS vs climatology
    brier_score = float(np.mean((yp - yt) ** 2))
    clim = float(np.mean(yt))
    brier_clim = float(np.mean((clim - yt) ** 2)) if len(yt) > 0 else 1.0
    bss = 1.0 - (brier_score / brier_clim) if brier_clim > 1e-8 else 0.0

    return {
        "bin_centers": [round(float(x), 4) for x in bin_centers],
        "mean_predicted": [round(float(x), 4) for x in mean_predicted],
        "observed_freq": [round(float(x), 4) for x in observed_freq],
        "bin_counts": [int(x) for x in bin_counts],
        "bin_weights": [round(float(x / total_samples), 4) for x in bin_counts]
        if total_samples > 0
        else [],
        "brier_score": round(brier_score, 5),
        "brier_skill_score": round(bss, 4),
        "climatology": round(clim, 4),
    }
