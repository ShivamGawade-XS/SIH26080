"""
Integration tests for Scientific Controls Protocol (Section 6.10 / Section 6.7).
"""

from varsha.config import get_config
from varsha.data.synthetic.generator import generate_synthetic_dataset
from varsha.models.b2_gbm import ModelB2GBM
from varsha.models.b4_regime_gbm import ModelB4RegimeGBM
from varsha.regimes.classifier import RegimeClassifier
from varsha.regimes.rules import build_compound_regime_dataset
from varsha.verify.controls import run_all_controls, run_leakage_canary


def test_leakage_canary_control():
    """Verify leakage canary catches forbidden observation fields."""
    cfg = get_config(profile_name="demo-fast")
    ds = generate_synthetic_dataset(cfg)
    ds = build_compound_regime_dataset(ds, cfg)

    res = run_leakage_canary(ds)
    assert res["pass"] is True
    assert "All leakage canary checks passed" in res["evidence"]


def test_positive_and_negative_controls():
    """Verify execution of positive and negative controls on synthetic datasets."""
    cfg = get_config(profile_name="demo-fast")

    ds_biased = generate_synthetic_dataset(cfg, regime_dependent_bias=True)
    ds_biased = build_compound_regime_dataset(ds_biased, cfg)

    ds_unbiased = generate_synthetic_dataset(cfg, regime_dependent_bias=False)
    ds_unbiased = build_compound_regime_dataset(ds_unbiased, cfg)

    clf = RegimeClassifier(n_estimators=30).fit(ds_biased)
    probs_b = clf.predict_proba(ds_biased, lead=1)
    probs_u = clf.predict_proba(ds_unbiased, lead=1)

    b2_b = ModelB2GBM(n_estimators=30).fit(ds_biased).predict(ds_biased, lead=1)
    b4_b = (
        ModelB4RegimeGBM(n_estimators=30)
        .fit(ds_biased, probs_b)
        .predict(ds_biased, probs_b, lead=1)
    )

    b2_u = ModelB2GBM(n_estimators=30).fit(ds_unbiased).predict(ds_unbiased, lead=1)
    b4_u = (
        ModelB4RegimeGBM(n_estimators=30)
        .fit(ds_unbiased, probs_u)
        .predict(ds_unbiased, probs_u, lead=1)
    )

    controls = run_all_controls(
        ds_biased=ds_biased,
        ds_unbiased=ds_unbiased,
        b2_biased=b2_b,
        b4_biased=b4_b,
        b2_unbiased=b2_u,
        b4_unbiased=b4_u,
        lead=1,
        n_resamples=50,
    )

    assert "positive_control" in controls
    assert "negative_control" in controls
    assert "leakage_canary" in controls
    assert controls["leakage_canary"]["pass"] is True
