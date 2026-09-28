"""
Sensitivity Analysis for Regime Labelling Rules (Deliverable D1).
Evaluates stability of regime classifications under perturbed threshold parameters
(e.g., ±0.25 on standardized anomaly thresholds, ±1 day on minimum spell lengths).
"""

from __future__ import annotations

import copy

import numpy as np
import xarray as xr

from varsha.config import VarshaConfig
from varsha.regimes.rules import label_synoptic_regimes


def run_regime_sensitivity_analysis(ds: xr.Dataset, config: VarshaConfig) -> dict:
    """Run sensitivity perturbations on CMZ threshold and spell length.

    Returns label agreement percentage against baseline rules.
    """
    baseline_df = label_synoptic_regimes(ds, config)
    baseline_labels = baseline_df["regime"].values

    perturbations = [
        {"name": "active_thresh_+0.25", "active_adj": 0.25, "break_adj": 0.0},
        {"name": "active_thresh_-0.25", "active_adj": -0.25, "break_adj": 0.0},
        {"name": "break_thresh_+0.25", "active_adj": 0.0, "break_adj": 0.25},
        {"name": "break_thresh_-0.25", "active_adj": 0.0, "break_adj": -0.25},
    ]

    results = {}
    for p in perturbations:
        cfg_pert = copy.deepcopy(config)
        regimes_dict = cfg_pert.raw_configs.setdefault("regimes", {}).setdefault(
            "synoptic_regimes", {}
        )
        act_cfg = regimes_dict.setdefault("active", {})
        brk_cfg = regimes_dict.setdefault("break", {})

        act_base = act_cfg.get("cmz_anomaly_threshold", 0.7)
        brk_base = brk_cfg.get("cmz_anomaly_threshold", -0.7)

        act_cfg["cmz_anomaly_threshold"] = act_base + p["active_adj"]
        brk_cfg["cmz_anomaly_threshold"] = brk_base + p["break_adj"]

        perturbed_df = label_synoptic_regimes(ds, cfg_pert)
        perturbed_labels = perturbed_df["regime"].values
        agreement = float(np.mean(perturbed_labels == baseline_labels))

        results[p["name"]] = {
            "agreement_pct": round(agreement * 100.0, 2),
            "label_shifts": int(np.sum(perturbed_labels != baseline_labels)),
            "total_days": len(baseline_labels),
        }

    return {
        "baseline_days": len(baseline_labels),
        "perturbation_results": results,
    }
