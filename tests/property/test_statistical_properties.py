"""
Property-based tests for statistical verification metrics and mathematical bounds (Hypothesis).
"""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from varsha.models.calibration import enforce_monotone_consistency
from varsha.verify.metrics import categorical_scores, continuous_metrics


@settings(max_examples=50)
@given(
    obs=st.lists(st.floats(min_value=0.0, max_value=300.0), min_size=20, max_size=50),
    fcst=st.lists(st.floats(min_value=0.0, max_value=300.0), min_size=20, max_size=50),
    threshold=st.floats(min_value=1.0, max_value=150.0),
)
def test_categorical_metric_bounds(obs, fcst, threshold):
    """Categorical metrics must strictly stay within theoretical mathematical bounds."""
    min_len = min(len(obs), len(fcst))
    o_arr = np.array(obs[:min_len], dtype=float)
    f_arr = np.array(fcst[:min_len], dtype=float)

    scores = categorical_scores(o_arr, f_arr, threshold=threshold)

    # If events exist, metrics must strictly stay within theoretical bounds
    if not np.isnan(scores["pod"]):
        assert 0.0 <= scores["pod"] <= 1.0
    if not np.isnan(scores["far"]):
        assert 0.0 <= scores["far"] <= 1.0
    if not np.isnan(scores["csi"]):
        assert 0.0 <= scores["csi"] <= 1.0
    if not np.isnan(scores["ets"]):
        assert scores["ets"] <= 1.0
    if not np.isnan(scores["fbi"]):
        assert scores["fbi"] >= 0.0


@settings(max_examples=50)
@given(values=st.lists(st.floats(min_value=0.0, max_value=200.0), min_size=10, max_size=50))
def test_perfect_forecast_properties(values):
    """A perfect forecast (obs == fcst) must yield exact theoretical scores."""
    arr = np.array(values, dtype=float)
    cont = continuous_metrics(arr, arr)
    assert cont["rmse"] == 0.0
    assert cont["mae"] == 0.0
    assert abs(cont["bias"]) < 1e-6

    if np.any(arr >= 64.5):
        cat = categorical_scores(arr, arr, threshold=64.5)
        assert cat["pod"] == 1.0
        assert cat["far"] == 0.0
        assert cat["csi"] == 1.0
        assert cat["ets"] == 1.0
        assert cat["fbi"] == 1.0


@settings(max_examples=50)
@given(
    p1=st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=10, max_size=30),
    p2=st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=10, max_size=30),
)
def test_monotone_consistency_property(p1, p2):
    """Monotone projection must guarantee p115 <= p64 for any arbitrary input."""
    min_len = min(len(p1), len(p2))
    p64 = np.array(p1[:min_len], dtype=float)
    p115 = np.array(p2[:min_len], dtype=float)

    p64_c, p115_c, _ = enforce_monotone_consistency(p64, p115)
    assert np.all(p115_c <= p64_c + 1e-7)
    assert np.all(p64_c >= 0.0) and np.all(p64_c <= 1.0)
    assert np.all(p115_c >= 0.0) and np.all(p115_c <= 1.0)
