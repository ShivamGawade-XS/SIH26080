"""
Unit tests for Model Ladder (B0-B4) and Heavy Rain Probability Calibration (Deliverables D2, D3).
"""

import numpy as np

from varsha.config import get_config
from varsha.data.synthetic.generator import generate_synthetic_dataset
from varsha.models.b0_raw import ModelB0Raw
from varsha.models.b1_qm import ModelB1QM
from varsha.models.b2_gbm import ModelB2GBM
from varsha.models.b3_regime_qm import ModelB3RegimeQM
from varsha.models.b4_regime_gbm import ModelB4RegimeGBM
from varsha.models.calibration import enforce_monotone_consistency
from varsha.models.heavy_rain import HeavyRainProbabilityModel
from varsha.regimes.classifier import compute_out_of_fold_regime_probabilities
from varsha.regimes.rules import build_compound_regime_dataset


def test_full_model_ladder_b0_to_b4():
    """Verify all rungs in model ladder fit and predict valid non-negative rainfall grids."""
    cfg = get_config(profile_name="demo-fast")
    ds = generate_synthetic_dataset(cfg)
    ds = build_compound_regime_dataset(ds, cfg)

    oof_probs = compute_out_of_fold_regime_probabilities(ds, n_seasons=2)

    # B0 Raw
    b0 = ModelB0Raw()
    pred_b0 = b0.predict(ds, lead=1)
    assert pred_b0.shape == ds["tp_obs"].shape
    assert (pred_b0 >= 0.0).all()

    # B1 QM
    b1 = ModelB1QM(n_quantiles=30).fit(ds)
    pred_b1 = b1.predict(ds, lead=1)
    assert pred_b1.shape == ds["tp_obs"].shape
    assert (pred_b1 >= 0.0).all()

    # B2 GBM
    b2 = ModelB2GBM(n_estimators=30, seed=42).fit(ds)
    pred_b2 = b2.predict(ds, lead=1)
    assert pred_b2.shape == ds["tp_obs"].shape

    # B3 Regime QM
    b3 = ModelB3RegimeQM(n_quantiles=30).fit(ds)
    pred_b3 = b3.predict(ds, lead=1, regime_probs=oof_probs[1])
    assert pred_b3.shape == ds["tp_obs"].shape

    # B4 Regime GBM
    b4 = ModelB4RegimeGBM(n_estimators=30, seed=42).fit(ds, oof_probs[1])
    pred_b4 = b4.predict(ds, oof_probs[1], lead=1)
    assert pred_b4.shape == ds["tp_obs"].shape
    assert (pred_b4 >= 0.0).all()


def test_heavy_rain_probability_and_monotone_consistency():
    """Verify D3 heavy rain models output calibrated, monotonically ordered probabilities."""
    cfg = get_config(profile_name="demo-fast")
    ds = generate_synthetic_dataset(cfg)
    ds = build_compound_regime_dataset(ds, cfg)
    oof_probs = compute_out_of_fold_regime_probabilities(ds, n_seasons=2)

    hr = HeavyRainProbabilityModel(thresholds=[64.5, 115.6], n_estimators=30).fit(ds, oof_probs[1])
    probs = hr.predict_probabilities(ds, oof_probs[1], lead=1)

    assert 64.5 in probs and 115.6 in probs
    p64 = probs[64.5]
    p115 = probs[115.6]

    # Monotone consistency: P(>=115.6) <= P(>=64.5) everywhere
    assert np.all(p115 <= p64 + 1e-6)
    assert np.all(p64 >= 0.0) and np.all(p64 <= 1.0)


def test_monotone_consistency_function():
    """Test unit behavior of monotone projection."""
    p64 = np.array([0.4, 0.7, 0.2])
    p115 = np.array([0.5, 0.6, 0.3])  # 0.5 > 0.4 and 0.3 > 0.2 (inversions)

    p64_c, p115_c, _ = enforce_monotone_consistency(p64, p115)
    assert np.all(p115_c <= p64_c)
    assert p115_c[0] == 0.4
    assert p115_c[2] == 0.2
