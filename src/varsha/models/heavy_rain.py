"""
Heavy Rainfall Exceedance Probability Models (Deliverable D3).
Per-threshold LightGBM binary classifiers predicting probability of daily rainfall
exceeding operational IMD thresholds (64.5 mm, 115.6 mm, and 204.5 mm if sample size allows).
"""

from __future__ import annotations

import numpy as np
import xarray as xr

from varsha.models.calibration import ProbabilityCalibrator, enforce_monotone_consistency

try:
    import lightgbm as lgb  # type: ignore[import-untyped]

    _HAS_LGB = True
except ImportError:
    _HAS_LGB = False

IMD_THRESHOLDS = [64.5, 115.6, 204.5]


class HeavyRainProbabilityModel:
    """Predicts calibrated exceedance probabilities for operational heavy rain thresholds."""

    _FEATURE_NAMES = [
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

    def __init__(
        self, thresholds: list[float] | None = None, n_estimators: int = 150, seed: int = 42
    ) -> None:
        self.thresholds = thresholds or [64.5, 115.6]
        self.n_estimators = n_estimators
        self.seed = seed
        # Nested dict: threshold -> lead -> booster
        self.models: dict[float, dict[int, lgb.Booster]] = {}
        # Nested dict: threshold -> lead -> ProbabilityCalibrator
        self.calibrators: dict[float, dict[int, ProbabilityCalibrator]] = {}
        self._fitted = False

    def _extract_features(
        self,
        ds: xr.Dataset,
        lead: int,
        regime_probs: np.ndarray,
        thresh: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Extract feature matrix and binary exceedance target y in vectorized NumPy."""
        land = ds["land_mask"].values
        elev = ds["elevation"].values
        dist_c = ds["dist_coast"].values
        n_time = ds.sizes["time"]

        land_idx = np.where(land.flatten() > 0.5)[0]
        n_land = len(land_idx)
        if n_land == 0:
            return np.empty((0, len(self._FEATURE_NAMES))), np.empty(0)

        tp_raw = ds["tp_raw"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]
        pwat = ds["pwat"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]
        cape = ds["cape"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]
        u850 = ds["u850"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]
        v850 = ds["v850"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]
        vort = ds["vort850"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]
        mslp = ds["mslp_anom"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]
        obs = ds["tp_obs"].values.reshape(n_time, -1)[:, land_idx]

        elev_tile = np.tile(elev.flatten()[land_idx], n_time)
        dist_tile = np.tile(dist_c.flatten()[land_idx], n_time)
        lead_col = np.full(n_time * n_land, float(lead), dtype=np.float32)
        day_of_season = np.repeat((np.arange(n_time) % 122) + 1, n_land).astype(np.float32)

        if regime_probs.shape[0] != n_time and len(regime_probs) == 4:
            rp_mat = np.tile(regime_probs, (n_time, 1))
        else:
            rp_mat = regime_probs

        p0 = np.repeat(rp_mat[:, 0], n_land).astype(np.float32)
        p1 = np.repeat(rp_mat[:, 1], n_land).astype(np.float32)
        p2 = np.repeat(rp_mat[:, 2], n_land).astype(np.float32)
        p3 = np.repeat(rp_mat[:, 3], n_land).astype(np.float32)

        X = np.column_stack(
            [
                tp_raw.flatten(),
                pwat.flatten(),
                cape.flatten(),
                u850.flatten(),
                v850.flatten(),
                vort.flatten(),
                mslp.flatten(),
                elev_tile,
                dist_tile,
                lead_col,
                day_of_season,
                p0,
                p1,
                p2,
                p3,
            ]
        )
        y = (obs.flatten() >= thresh).astype(int)
        valid = ~(np.isnan(X).any(axis=1) | np.isnan(y))
        return X[valid], y[valid]

    def fit(
        self,
        ds_train: xr.Dataset,
        regime_probs_train: np.ndarray,
        ds_val: xr.Dataset | None = None,
        regime_probs_val: np.ndarray | None = None,
    ) -> HeavyRainProbabilityModel:
        """Fit per-threshold binary classifiers and calibrate on validation split."""
        if not _HAS_LGB:
            raise ImportError("lightgbm required.")

        leads = list(ds_train["lead"].values)

        for thresh in self.thresholds:
            self.models[thresh] = {}
            self.calibrators[thresh] = {}

            for lead in leads:
                X_tr, y_tr = self._extract_features(ds_train, int(lead), regime_probs_train, thresh)
                n_pos = int(np.sum(y_tr == 1))
                if n_pos < 3:
                    continue

                pos_weight = max(1.0, float(len(y_tr) - n_pos) / max(1, n_pos))
                params = {
                    "objective": "binary",
                    "learning_rate": 0.05,
                    "num_leaves": 31,
                    "scale_pos_weight": min(pos_weight, 10.0),
                    "min_child_samples": 10,
                    "seed": self.seed,
                    "verbose": -1,
                    "deterministic": True,
                    "num_threads": 1,
                }
                lgb_train = lgb.Dataset(X_tr, label=y_tr, feature_name=self._FEATURE_NAMES)
                booster = lgb.train(params, lgb_train, num_boost_round=self.n_estimators)
                self.models[thresh][int(lead)] = booster

                # Calibration step
                calibrator = ProbabilityCalibrator()
                if ds_val is not None and regime_probs_val is not None:
                    X_v, y_v = self._extract_features(ds_val, int(lead), regime_probs_val, thresh)
                    if len(X_v) > 0 and np.sum(y_v == 1) > 0:
                        raw_val_p = np.asarray(booster.predict(X_v), dtype=np.float32)
                        calibrator.fit(raw_val_p, y_v)
                    else:
                        calibrator.fit(np.asarray(booster.predict(X_tr), dtype=np.float32), y_tr)
                else:
                    calibrator.fit(np.asarray(booster.predict(X_tr), dtype=np.float32), y_tr)

                self.calibrators[thresh][int(lead)] = calibrator

        self._fitted = True
        return self

    def predict_probabilities(
        self,
        ds_eval: xr.Dataset,
        regime_probs_eval: np.ndarray,
        lead: int,
    ) -> dict[float, np.ndarray]:
        """Predict calibrated exceedance probabilities grid for each threshold."""
        land = ds_eval["land_mask"].values
        elev = ds_eval["elevation"].values
        dist_c = ds_eval["dist_coast"].values
        n_time = ds_eval.sizes["time"]
        lat_size = ds_eval.sizes["lat"]
        lon_size = ds_eval.sizes["lon"]

        land_idx = np.where(land.flatten() > 0.5)[0]
        n_land = len(land_idx)
        if n_land == 0:
            return {th: np.zeros((n_time, lat_size, lon_size), dtype=np.float32) for th in self.thresholds}

        tp_raw = ds_eval["tp_raw"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]
        pwat = ds_eval["pwat"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]
        cape = ds_eval["cape"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]
        u850 = ds_eval["u850"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]
        v850 = ds_eval["v850"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]
        vort = ds_eval["vort850"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]
        mslp = ds_eval["mslp_anom"].sel(lead=lead).values.reshape(n_time, -1)[:, land_idx]

        elev_tile = np.tile(elev.flatten()[land_idx], n_time)
        dist_tile = np.tile(dist_c.flatten()[land_idx], n_time)
        lead_col = np.full(n_time * n_land, float(lead), dtype=np.float32)
        day_of_season = np.repeat((np.arange(n_time) % 122) + 1, n_land).astype(np.float32)

        if regime_probs_eval.shape[0] != n_time and len(regime_probs_eval) == 4:
            rp_mat = np.tile(regime_probs_eval, (n_time, 1))
        else:
            rp_mat = regime_probs_eval

        p0 = np.repeat(rp_mat[:, 0], n_land).astype(np.float32)
        p1 = np.repeat(rp_mat[:, 1], n_land).astype(np.float32)
        p2 = np.repeat(rp_mat[:, 2], n_land).astype(np.float32)
        p3 = np.repeat(rp_mat[:, 3], n_land).astype(np.float32)

        X = np.column_stack(
            [
                tp_raw.flatten(),
                pwat.flatten(),
                cape.flatten(),
                u850.flatten(),
                v850.flatten(),
                vort.flatten(),
                mslp.flatten(),
                elev_tile,
                dist_tile,
                lead_col,
                day_of_season,
                p0,
                p1,
                p2,
                p3,
            ]
        )

        raw_probs: dict[float, np.ndarray] = {}

        for thresh in self.thresholds:
            booster = self.models.get(thresh, {}).get(int(lead))
            calibrator = self.calibrators.get(thresh, {}).get(int(lead))

            if booster is None:
                tp_raw_full = ds_eval["tp_raw"].sel(lead=lead).values
                grid_thresh = (tp_raw_full >= thresh).astype(np.float32) * 0.5
            else:
                raw_p = np.asarray(booster.predict(X), dtype=np.float32)
                if calibrator is not None:
                    cal_p = calibrator.predict_proba(raw_p)
                else:
                    cal_p = raw_p

                cal_p_2d = cal_p.reshape(n_time, n_land)
                grid_thresh = np.zeros((n_time, lat_size * lon_size), dtype=np.float32)
                grid_thresh[:, land_idx] = cal_p_2d
                grid_thresh = grid_thresh.reshape(n_time, lat_size, lon_size)

            raw_probs[thresh] = grid_thresh

        # Enforce monotone consistency
        p64 = raw_probs.get(64.5, np.zeros((n_time, lat_size, lon_size), dtype=np.float32))
        p115 = raw_probs.get(115.6, np.zeros((n_time, lat_size, lon_size), dtype=np.float32))
        p204 = raw_probs.get(204.5, None)

        p64_c, p115_c, p204_c = enforce_monotone_consistency(p64, p115, p204)

        results = {64.5: p64_c, 115.6: p115_c}
        if p204_c is not None:
            results[204.5] = p204_c

        return results
