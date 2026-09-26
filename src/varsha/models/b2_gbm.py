"""
Baseline Model B2: Global Gradient-Boosted Model (no regime information).
Trained on cell-level NWP forecast predictors to improve daily rainfall.
No regime features are used — this isolates the value of regime awareness in B4.
"""

from __future__ import annotations

import numpy as np
import xarray as xr

try:
    import lightgbm as lgb  # type: ignore[import-untyped]

    _HAS_LGB = True
except ImportError:
    _HAS_LGB = False


class ModelB2GBM:
    """Global GBM corrector (no regime features).

    Feature set per cell-day-lead:
        tp_raw, pwat, cape, u850, v850, vort850, mslp_anom,
        elevation, dist_coast, lead (integer), day_of_season (1..122)
    """

    MODEL_NAME = "B2_GlobalGBM"
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
    ]

    def __init__(self, n_estimators: int = 200, seed: int = 42) -> None:
        self.n_estimators = n_estimators
        self.seed = seed
        self.models: dict[int, lgb.Booster] = {}
        self._fitted = False

    def _extract_features(
        self, ds: xr.Dataset, lead: int, mask_time: np.ndarray | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """Flatten dataset into (n_samples, n_features) feature matrix in vectorized NumPy."""
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
            ]
        )
        y = obs.flatten()

        if mask_time is not None:
            row_mask = np.repeat(mask_time, n_land)
            X = X[row_mask]
            y = y[row_mask]

        valid = ~(np.isnan(X).any(axis=1) | np.isnan(y))
        return X[valid], y[valid]

    def fit(
        self,
        ds_train: xr.Dataset,
        train_season_mask: np.ndarray | None = None,
    ) -> ModelB2GBM:
        """Fit one GBM per lead time."""
        if not _HAS_LGB:
            raise ImportError(
                "lightgbm is required for ModelB2GBM. Install with: pip install lightgbm"
            )

        leads = list(ds_train["lead"].values)
        for lead in leads:
            X_tr, y_tr = self._extract_features(ds_train, int(lead), mask_time=train_season_mask)
            if len(X_tr) == 0:
                continue

            params = {
                "objective": "regression_l1",
                "num_leaves": 15,
                "learning_rate": 0.05,
                "n_estimators": self.n_estimators,
                "min_child_samples": 20,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "seed": self.seed,
                "verbose": -1,
                "deterministic": True,
                "num_threads": 1,
            }
            lgb_train = lgb.Dataset(X_tr, label=y_tr, feature_name=self._FEATURE_NAMES)
            booster = lgb.train(
                params,
                lgb_train,
                num_boost_round=self.n_estimators,
            )
            self.models[int(lead)] = booster

        self._fitted = True
        return self

    def predict(self, ds_eval: xr.Dataset, lead: int) -> np.ndarray:
        """Predict corrected rainfall grid (time, lat, lon) for a given lead."""
        if not self._fitted or int(lead) not in self.models:
            return ds_eval["tp_raw"].sel(lead=lead).values

        booster = self.models[int(lead)]
        land = ds_eval["land_mask"].values
        elev = ds_eval["elevation"].values
        dist_c = ds_eval["dist_coast"].values
        n_time = ds_eval.sizes["time"]
        lat_size = ds_eval.sizes["lat"]
        lon_size = ds_eval.sizes["lon"]

        land_idx = np.where(land.flatten() > 0.5)[0]
        n_land = len(land_idx)
        if n_land == 0:
            return np.zeros((n_time, lat_size, lon_size), dtype=np.float32)

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
            ]
        )

        preds = booster.predict(X)
        preds = np.maximum(0.0, preds).reshape(n_time, n_land)

        result = np.zeros((n_time, lat_size * lon_size), dtype=np.float32)
        result[:, land_idx] = preds
        return result.reshape(n_time, lat_size, lon_size)
