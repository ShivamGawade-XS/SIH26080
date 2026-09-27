"""
Unit tests for Objective Rule-Based Regime Labeller (Deliverable D1).
"""

import pytest

from varsha.config import get_config
from varsha.data.synthetic.generator import generate_synthetic_dataset
from varsha.regimes.rules import (
    assign_geographic_zones,
    build_compound_regime_dataset,
    compute_cmz_anomalies,
    label_synoptic_regimes,
)


@pytest.fixture
def sample_dataset():
    cfg = get_config(profile_name="demo-fast")
    return generate_synthetic_dataset(cfg, seasons=["S01"])


def test_cmz_anomaly_computation(sample_dataset):
    cfg = get_config(profile_name="demo-fast")
    anomaly = compute_cmz_anomalies(sample_dataset, cfg)
    assert len(anomaly) == len(sample_dataset.time)
    # Mean should be ~0 and std ~1
    assert abs(anomaly.mean()) < 0.1
    assert abs(anomaly.std() - 1.0) < 0.1


def test_synoptic_regime_labelling(sample_dataset):
    cfg = get_config(profile_name="demo-fast")
    df = label_synoptic_regimes(sample_dataset, cfg)
    assert len(df) == len(sample_dataset.time)
    assert "regime" in df.columns
    valid_regimes = {"active", "break", "normal", "depression"}
    assert set(df["regime"]).issubset(valid_regimes)


def test_geographic_zone_assignment(sample_dataset):
    cfg = get_config(profile_name="demo-fast")
    zones = assign_geographic_zones(sample_dataset, cfg)
    assert zones.shape == (len(sample_dataset.lat), len(sample_dataset.lon))
    unique_zones = set(zones.flatten())
    assert "interior" in unique_zones
    assert "orographic_ghats" in unique_zones or "coastal_west" in unique_zones


def test_compound_dataset_builder(sample_dataset):
    cfg = get_config(profile_name="demo-fast")
    ds_labeled = build_compound_regime_dataset(sample_dataset, cfg)
    assert "synoptic_regime" in ds_labeled.data_vars
    assert "geographic_zone" in ds_labeled.data_vars
    assert len(ds_labeled.synoptic_regime) == len(sample_dataset.time)
