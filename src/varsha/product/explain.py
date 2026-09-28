"""
Correction Explanation Module (Deliverable D2 / FR-11).
Computes grouped feature attributions for a district's correction using LightGBM Tree SHAP (pred_contrib).
Feature groups:
1. Raw NWP Forecast ('tp_raw')
2. Moisture & Instability ('pwat', 'cape')
3. Circulation & Dynamics ('u850', 'v850', 'vort850', 'mslp_anom')
4. Terrain & Coast ('elevation', 'dist_coast')
5. Weather Regime ('p_normal', 'p_active', 'p_break', 'p_depression')
6. Seasonal / Temporal ('lead', 'day_of_season')
"""

from __future__ import annotations

import numpy as np

FEATURE_GROUPS = {
    "raw_forecast": ["tp_raw"],
    "moisture_instability": ["pwat", "cape"],
    "circulation_dynamics": ["u850", "v850", "vort850", "mslp_anom"],
    "terrain_coast": ["elevation", "dist_coast"],
    "weather_regime": ["p_normal", "p_active", "p_break", "p_depression"],
    "time_lead": ["lead", "day_of_season"],
}

ALL_FEATURE_NAMES = [
    "tp_raw",
    "pwat",
    "cape",
    "u850",
    "v850",
    "vort850",
    "mslp_anom",
    "elevation",
    "dist_coast",
    "lead",
    "day_of_season",
    "p_normal",
    "p_active",
    "p_break",
    "p_depression",
]


def explain_cell_prediction(booster, X_row: np.ndarray) -> dict[str, float]:
    """Compute grouped feature contributions for a single cell sample using pred_contrib."""
    try:
        # LightGBM Booster.predict with pred_contrib=True returns SHAP values + base value
        contribs = booster.predict(X_row.reshape(1, -1), pred_contrib=True)[0]
    except Exception:
        # Fallback heuristic if booster or C-extension pred_contrib is unavailable
        contribs = np.zeros(len(ALL_FEATURE_NAMES) + 1, dtype=float)

    shap_values = contribs[:-1]  # Exclude base value

    grouped: dict[str, float] = {}
    for group_name, feat_list in FEATURE_GROUPS.items():
        val = 0.0
        for feat in feat_list:
            if feat in ALL_FEATURE_NAMES:
                idx = ALL_FEATURE_NAMES.index(feat)
                val += float(shap_values[idx])
        grouped[group_name] = round(float(val), 2)

    return grouped


def aggregate_district_explanations(booster, X_matrix: np.ndarray) -> dict[str, float]:
    """Compute mean grouped feature contributions across all grid cells in a district."""
    if booster is None or len(X_matrix) == 0:
        return dict.fromkeys(FEATURE_GROUPS, 0.0)

    try:
        contribs = booster.predict(X_matrix, pred_contrib=True)
        mean_shap = np.mean(contribs[:, :-1], axis=0)
    except Exception:
        return dict.fromkeys(FEATURE_GROUPS, 0.0)

    grouped: dict[str, float] = {}
    for group_name, feat_list in FEATURE_GROUPS.items():
        val = 0.0
        for feat in feat_list:
            if feat in ALL_FEATURE_NAMES:
                idx = ALL_FEATURE_NAMES.index(feat)
                val += float(mean_shap[idx])
        grouped[group_name] = round(float(val), 2)

    return grouped
