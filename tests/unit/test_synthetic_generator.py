"""
Unit tests for Synthetic Monsoon World Generator.
"""

import numpy as np

from varsha.config import get_config
from varsha.data.synthetic.generator import (
    generate_static_fields,
    generate_synthetic_dataset,
    simulate_regime_sequence,
)


def test_static_fields_shape_and_bounds():
    lats = np.arange(8.0, 38.0, 1.0)
    lons = np.arange(68.0, 98.0, 1.0)
    elev, dist_c, mask = generate_static_fields(lats, lons)

    assert elev.shape == (len(lats), len(lons))
    assert dist_c.shape == (len(lats), len(lons))
    assert mask.shape == (len(lats), len(lons))

    assert np.all(elev >= 0.0)
    assert np.all(elev <= 6000.0)
    assert np.all((mask == 0.0) | (mask == 1.0))
    # Western Ghats peak check
    assert np.max(elev) > 1000.0


def test_regime_sequence_simulation():
    seq = simulate_regime_sequence(122, seed=42)
    assert len(seq) == 122
    unique_regimes = set(seq)
    assert "active" in unique_regimes or "normal" in unique_regimes
    assert all(r in ["active", "break", "normal", "depression"] for r in seq)


def test_synthetic_dataset_generation():
    cfg = get_config(profile_name="demo-fast")
    # Test on single season for fast execution
    ds = generate_synthetic_dataset(cfg, seasons=["S01"])

    assert "tp_obs" in ds.data_vars
    assert "tp_raw" in ds.data_vars
    assert "pwat" in ds.data_vars
    assert "vort850" in ds.data_vars

    assert ds.tp_raw.shape[1] == len(cfg.leads)  # 5 leads
    assert not np.isnan(ds.tp_raw.values).any()
    assert np.all(ds.tp_obs.values >= 0.0)
