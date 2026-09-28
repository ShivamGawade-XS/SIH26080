"""
Unit tests for Baseline Models B0 and B1.
"""

import numpy as np
import pytest

from varsha.config import get_config
from varsha.data.synthetic.generator import generate_synthetic_dataset
from varsha.models.b0_raw import ModelB0Raw
from varsha.models.b1_qm import ModelB1QM


@pytest.fixture
def sample_dataset():
    cfg = get_config(profile_name="demo-fast")
    return generate_synthetic_dataset(cfg, seasons=["S01", "S02"])


def test_model_b0_raw_prediction(sample_dataset):
    model = ModelB0Raw().fit(sample_dataset)
    pred_lead1 = model.predict(sample_dataset, lead=1)
    raw_lead1 = sample_dataset["tp_raw"].sel(lead=1).values

    assert pred_lead1.shape == raw_lead1.shape
    assert np.allclose(pred_lead1, raw_lead1)
    assert np.all(pred_lead1 >= 0.0)


def test_model_b1_quantile_mapping(sample_dataset):
    model = ModelB1QM(n_quantiles=20).fit(sample_dataset)
    assert len(model.lead_maps) == len(sample_dataset.lead)

    pred_lead1 = model.predict(sample_dataset, lead=1)
    assert pred_lead1.shape == sample_dataset["tp_raw"].sel(lead=1).values.shape
    assert np.all(pred_lead1 >= 0.0)
    assert not np.isnan(pred_lead1).any()


def test_model_b4_quantile_regression(sample_dataset):
    from varsha.models.b4_regime_gbm import ModelB4RegimeGBM

    n_time = sample_dataset.sizes["time"]
    regime_probs = np.full((n_time, 4), 0.25, dtype=np.float32)
    b4 = ModelB4RegimeGBM(n_estimators=15, quantiles=[0.1, 0.5, 0.9]).fit(
        sample_dataset, regime_probs
    )
    q_preds = b4.predict_quantiles(sample_dataset, regime_probs, lead=1)

    assert 0.1 in q_preds and 0.5 in q_preds and 0.9 in q_preds
    # Verify non-crossing monotonicity: q0.1 <= q0.5 <= q0.9
    assert np.all(q_preds[0.1] <= q_preds[0.5] + 1e-5)
    assert np.all(q_preds[0.5] <= q_preds[0.9] + 1e-5)
    assert np.all(q_preds[0.1] >= 0.0)

