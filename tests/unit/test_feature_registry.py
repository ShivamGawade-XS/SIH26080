"""
Unit tests for Feature Registry and Temporal Leakage Guard (Section 6.7).
"""

import pytest

from varsha.features.registry import FEATURE_REGISTRY, FeatureRegistry, FeatureSpec


def test_default_features_registered():
    """Verify essential forecast predictors are registered and approved."""
    for feat in [
        "tp_raw",
        "pwat",
        "cape",
        "u850",
        "v850",
        "vort850",
        "mslp_anom",
        "elevation",
        "dist_coast",
    ]:
        spec = FEATURE_REGISTRY.get(feat)
        assert spec.available_at in ["init_time", "static"]
        assert spec.source in ["forecast", "static", "climatology", "regime_oof"]


def test_leakage_guard_rejects_forbidden_observation_fields():
    """Verify that feature registry raises ValueError on observed targets."""
    # Attempting to validate a feature list containing observed rainfall must fail
    with pytest.raises(ValueError, match="LEAKAGE GUARD VIOLATION"):
        FEATURE_REGISTRY.validate_features(["tp_raw", "pwat", "tp_obs"])

    with pytest.raises(ValueError, match="LEAKAGE GUARD VIOLATION"):
        FEATURE_REGISTRY.validate_features(["synoptic_regime"])


def test_custom_leakage_detection():
    """Verify dynamic detection of newly registered leaky features."""
    reg = FeatureRegistry()
    reg.register(
        FeatureSpec(
            name="future_radar",
            source="observation",
            time_reference="observed_valid",
            available_at="valid_time",
            description="Leaky valid_time observation",
        )
    )

    with pytest.raises(ValueError, match="LEAKAGE GUARD VIOLATION"):
        reg.validate_features(["future_radar"])
