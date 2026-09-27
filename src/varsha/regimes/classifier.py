"""
Forecast-Side Weather Regime Classifier (Deliverable D1).
Predicts prevailing synoptic regime (Normal=0, Active=1, Break=2, Depression=3)
from forecast-side fields only at each lead time.

Provides:
1. Multiclass LightGBM classifier with class weighting and probability output.
2. Out-of-fold (OOF) regime probability generation across seasons for leakage-free B4 training.
3. Verification metrics by lead (Precision, Recall, F1, Macro-F1, Confusion Matrix, ECE).
"""

from __future__ import annotations

import numpy as np
import xarray as xr

from varsha.features.predictors import (
    DOMAIN_PREDICTOR_NAMES,
    extract_all_domain_synoptic_predictors,
)

try:
    import lightgbm as lgb  # type: ignore[import-untyped]

    _HAS_LGB = True
except ImportError:
    _HAS_LGB = False

REGIME_CLASSES = ["normal", "active", "break", "depression"]
N_CLASSES = len(REGIME_CLASSES)


class RegimeClassifier:
    """Forecast-side synoptic regime probability predictor."""

    def __init__(self, n_estimators: int = 150, seed: int = 42) -> None:
        self.n_estimators = n_estimators
        self.seed = seed
        self.models: dict[int, lgb.Booster] = {}
        self._fitted = False

    def _extract_dataset_features(self, ds: xr.Dataset, lead: int) -> tuple[np.ndarray, np.ndarray]:
        """Extract (n_time, n_features) and ground-truth (n_time,) labels."""
        X = extract_all_domain_synoptic_predictors(ds, lead=lead)
        y = ds["synoptic_regime"].values.astype(int)
        return X, y

    def fit(self, ds_train: xr.Dataset) -> RegimeClassifier:
        """Fit one multiclass classifier per lead time on training dataset."""
        if not _HAS_LGB:
            raise ImportError("lightgbm is required for RegimeClassifier.")

        leads = list(ds_train["lead"].values)
        for lead in leads:
            X, y = self._extract_dataset_features(ds_train, int(lead))

            # Compute class weights for imbalance
            classes, counts = np.unique(y, return_counts=True)
            total = len(y)
            weights = np.ones(len(y), dtype=np.float32)
            for c, cnt in zip(classes, counts, strict=False):
                if cnt > 0:
                    weights[y == c] = total / (len(classes) * cnt)

            params = {
                "objective": "multiclass",
                "num_class": N_CLASSES,
                "learning_rate": 0.05,
                "num_leaves": 15,
                "min_child_samples": 5,
                "seed": self.seed,
                "verbose": -1,
                "deterministic": True,
                "num_threads": 1,
            }
            lgb_train = lgb.Dataset(X, label=y, weight=weights, feature_name=DOMAIN_PREDICTOR_NAMES)
            booster = lgb.train(params, lgb_train, num_boost_round=self.n_estimators)
            self.models[int(lead)] = booster

        self._fitted = True
        return self

    def predict_proba(self, ds_eval: xr.Dataset, lead: int) -> np.ndarray:
        """Predict (n_time, 4) probability distribution for a given lead."""
        if not self._fitted or int(lead) not in self.models:
            # Fallback uniform
            n_time = ds_eval.dims["time"]
            return np.full((n_time, N_CLASSES), 1.0 / N_CLASSES, dtype=np.float32)

        booster = self.models[int(lead)]
        X, _ = self._extract_dataset_features(ds_eval, int(lead))
        probs = booster.predict(X)  # (n_time, 4)
        return np.asarray(probs, dtype=np.float32)

    def evaluate(self, ds_eval: xr.Dataset, lead: int) -> dict:
        """Compute comprehensive evaluation metrics for a specific lead."""
        probs = self.predict_proba(ds_eval, lead)
        y_pred = np.argmax(probs, axis=1)
        y_true = ds_eval["synoptic_regime"].values.astype(int)

        # Confusion matrix
        conf_mat = np.zeros((N_CLASSES, N_CLASSES), dtype=int)
        for t in range(len(y_true)):
            conf_mat[y_true[t], y_pred[t]] += 1

        # Per-class metrics
        per_class = {}
        precisions, recalls, f1s = [], [], []
        for c, name in enumerate(REGIME_CLASSES):
            tp = conf_mat[c, c]
            fp = conf_mat[:, c].sum() - tp
            fn = conf_mat[c, :].sum() - tp

            p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0

            precisions.append(p)
            recalls.append(r)
            f1s.append(f1)
            per_class[name] = {
                "precision": round(float(p), 4),
                "recall": round(float(r), 4),
                "f1": round(float(f1), 4),
                "support": int(conf_mat[c, :].sum()),
            }

        macro_f1 = float(np.mean(f1s))
        accuracy = float(np.mean(y_pred == y_true))

        # Expected Calibration Error (ECE)
        confidences = np.max(probs, axis=1)
        correct = (y_pred == y_true).astype(float)
        ece = self._compute_ece(confidences, correct, n_bins=10)

        return {
            "lead": lead,
            "accuracy": round(accuracy, 4),
            "macro_f1": round(macro_f1, 4),
            "ece": round(ece, 4),
            "per_class": per_class,
            "confusion_matrix": conf_mat.tolist(),
        }

    @staticmethod
    def _compute_ece(confidences: np.ndarray, correct: np.ndarray, n_bins: int = 10) -> float:
        bins = np.linspace(0.0, 1.0, n_bins + 1)
        ece = 0.0
        n = len(confidences)
        for i in range(n_bins):
            in_bin = (confidences >= bins[i]) & (confidences < bins[i + 1])
            if np.sum(in_bin) > 0:
                bin_acc = np.mean(correct[in_bin])
                bin_conf = np.mean(confidences[in_bin])
                bin_size = np.sum(in_bin)
                ece += (bin_size / n) * abs(bin_acc - bin_conf)
        return float(ece)


def compute_out_of_fold_regime_probabilities(
    ds: xr.Dataset, n_seasons: int = 4
) -> dict[int, np.ndarray]:
    """Compute strictly out-of-fold regime probabilities across seasons.

    Returns {lead: (n_time, 4)} array of OOF predicted probabilities.
    Guarantees that when B4 is trained on season S, the regime features were predicted
    by a classifier trained only on other seasons S' != S (No In-Sample Leakage).
    """
    n_time = ds.sizes["time"]
    days_per_season = n_time // n_seasons
    leads = list(ds["lead"].values)

    oof_probs: dict[int, np.ndarray] = {
        int(lead): np.zeros((n_time, N_CLASSES), dtype=np.float32) for lead in leads
    }

    for s in range(n_seasons):
        val_start = s * days_per_season
        val_end = (s + 1) * days_per_season if s < n_seasons - 1 else n_time
        val_indices = np.arange(val_start, val_end)
        train_indices = np.setdiff1d(np.arange(n_time), val_indices)

        ds_train_fold = ds.isel(time=train_indices)
        ds_val_fold = ds.isel(time=val_indices)

        clf = RegimeClassifier()
        clf.fit(ds_train_fold)

        for lead in leads:
            fold_probs = clf.predict_proba(ds_val_fold, int(lead))
            oof_probs[int(lead)][val_indices] = fold_probs

    return oof_probs
