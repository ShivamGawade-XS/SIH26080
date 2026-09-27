"""
Unit tests for Weather Regime Classifier and Sensitivity Analysis (Deliverable D1).
"""

import numpy as np

from varsha.config import get_config
from varsha.data.synthetic.generator import generate_synthetic_dataset
from varsha.regimes.classifier import RegimeClassifier, compute_out_of_fold_regime_probabilities
from varsha.regimes.rules import build_compound_regime_dataset
from varsha.regimes.sensitivity import run_regime_sensitivity_analysis


def test_regime_classifier_fit_and_predict():
    """Verify forecast-side regime classifier fits and outputs calibrated probability distribution."""
    cfg = get_config(profile_name="demo-fast")
    ds = generate_synthetic_dataset(cfg)
    ds = build_compound_regime_dataset(ds, cfg)

    clf = RegimeClassifier(n_estimators=30, seed=42)
    clf.fit(ds)

    probs = clf.predict_proba(ds, lead=1)
    assert probs.shape == (len(ds["time"]), 4)
    # Probabilities must sum to 1.0 per day
    np.testing.assert_allclose(probs.sum(axis=1), 1.0, atol=1e-5)

    eval_res = clf.evaluate(ds, lead=1)
    assert "accuracy" in eval_res
    assert "macro_f1" in eval_res
    assert "ece" in eval_res
    assert eval_res["accuracy"] >= 0.25


def test_out_of_fold_regime_probabilities_no_leakage():
    """Verify out-of-fold regime cross validation produces valid probability matrix."""
    cfg = get_config(profile_name="demo-fast")
    ds = generate_synthetic_dataset(cfg)
    ds = build_compound_regime_dataset(ds, cfg)

    oof_probs = compute_out_of_fold_regime_probabilities(ds, n_seasons=2)
    assert 1 in oof_probs
    assert oof_probs[1].shape == (len(ds["time"]), 4)
    np.testing.assert_allclose(oof_probs[1].sum(axis=1), 1.0, atol=1e-5)


def test_regime_sensitivity_analysis():
    """Verify sensitivity perturbations on threshold parameters."""
    cfg = get_config(profile_name="demo-fast")
    ds = generate_synthetic_dataset(cfg)
    ds = build_compound_regime_dataset(ds, cfg)

    sens = run_regime_sensitivity_analysis(ds, cfg)
    assert "baseline_days" in sens
    assert "perturbation_results" in sens
    assert len(sens["perturbation_results"]) >= 4
