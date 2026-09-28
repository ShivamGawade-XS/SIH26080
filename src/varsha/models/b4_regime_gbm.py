"""
Baseline Model B4: Regime-Aware Gradient-Boosted Model (Deliverable D2).
Trained on forecast predictors, terrain features, and out-of-fold regime probabilities.
Outputs corrected expectation (P50) and quantile bounds (P10/P90).
"""

from __future__ import annotations

import numpy as np
import xarray as xr

from varsha.features.registry import FEATURE_REGISTRY

try:
    import lightgbm as lgb  # type: ignore[import-untyped]
    _HAS_LGB = True
except ImportError:
    _HAS_LGB = False

REGIME_CLASSES = ["normal", "active", "break", "depression"]
N_REGIMES = len(REGIME_CLASSES)


class ModelB4RegimeGBM:
    """Regime-aware gradient boosted model with out-of-fold probability features."""

    MODEL_NAME = "B4_RegimeGBM"
    _FEATURE_NAMES = [
        "tp_raw", "pwat", "cape", "u850", "v850", "vort850",
        "mslp_anom", "elevation", "dist_coast", "lead", "day_of_season",
        "p_normal", "p_active", "p_break", "p_depression",
    ]

    def __init__(
        self,
        n_estimators: int = 120,
        seed: int = 42,
        quantiles: list[float] | None = None,
    ) -> None:
        self.n_estimators = n_estimators
        self.seed = seed
        self.quantiles = quantiles or [0.1, 0.5, 0.9]
        self.models: dict[int, lgb.Booster] = {}
        self.quantile_models: dict[float, dict[int, lgb.Booster]] = {
            q: {} for q in self.quantiles
        }
        self._fitted = False

    def _extract_features(
        self,
        ds: xr.Dataset,
        lead: int,
        regime_probs: np.ndarray,
        mask_time: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Build feature matrix including regime probability columns in vectorized NumPy."""
        FEATURE_REGISTRY.validate_features(self._FEATURE_NAMES)

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

        # Handle regime_probs shape (n_time, 4) or broadcast if needed
        if regime_probs.ndim == 1 and len(regime_probs) == 4:
            rp_mat = np.tile(regime_probs, (n_time, 1))
        elif regime_probs.shape[0] == 1 and n_time > 1:
            rp_mat = np.tile(regime_probs, (n_time, 1))
        elif regime_probs.shape[0] != n_time:
            rp_mat = np.tile(regime_probs[0], (n_time, 1))
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
        regime_probs_train: np.ndarray | dict[int, np.ndarray],
        train_season_mask: np.ndarray | None = None,
    ) -> ModelB4RegimeGBM:
        """Fit one GBM per lead using out-of-fold regime probabilities."""
        if not _HAS_LGB:
            raise ImportError("lightgbm is required. Install with: pip install lightgbm")

        leads = list(ds_train["lead"].values)
        for lead in leads:
            rp = (
                regime_probs_train.get(int(lead), regime_probs_train.get(1, list(regime_probs_train.values())[0]))
                if isinstance(regime_probs_train, dict)
                else regime_probs_train
            )
            X_tr, y_tr = self._extract_features(
                ds_train, int(lead), rp, mask_time=train_season_mask
            )
            if len(X_tr) == 0:
                continue

            lgb_train = lgb.Dataset(X_tr, label=y_tr, feature_name=self._FEATURE_NAMES)
            for alpha in self.quantiles:
                params = {
                    "objective": "quantile",
                    "alpha": float(alpha),
                    "num_leaves": 15,
                    "learning_rate": 0.05,
                    "n_estimators": self.n_estimators,
                    "min_child_samples": 20,
                    "subsample": 0.8,
                    "colsample_bytree": 1.0,
                    "seed": self.seed,
                    "verbose": -1,
                    "deterministic": True,
                    "num_threads": 1,
                }
                booster = lgb.train(params, lgb_train, num_boost_round=self.n_estimators)
                self.quantile_models[float(alpha)][int(lead)] = booster
                if abs(alpha - 0.5) < 1e-4:
                    self.models[int(lead)] = booster

        self._fitted = True
        return self

    def predict(
        self,
        ds_eval: xr.Dataset,
        regime_probs_eval: np.ndarray | dict[int, np.ndarray],
        lead: int,
        quantile: float = 0.5,
    ) -> np.ndarray:
        """Predict corrected rainfall grid (time, lat, lon) for specified quantile (default P50)."""
        if not self._fitted:
            return ds_eval["tp_raw"].sel(lead=lead).values

        # Select matching quantile model or median fallback
        booster = None
        if quantile in self.quantile_models and lead in self.quantile_models[quantile]:
            booster = self.quantile_models[quantile][lead]
        elif lead in self.models:
            booster = self.models[lead]
        else:
            return ds_eval["tp_raw"].sel(lead=lead).values

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

        rp = (
            regime_probs_eval.get(lead, regime_probs_eval.get(1, list(regime_probs_eval.values())[0]))
            if isinstance(regime_probs_eval, dict)
            else regime_probs_eval
        )
        if rp.shape[0] != n_time and len(rp) == 4:
            rp_mat = np.tile(rp, (n_time, 1))
        else:
            rp_mat = rp

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

        preds = np.maximum(0.0, booster.predict(X)).reshape(n_time, n_land)
        result = np.zeros((n_time, lat_size * lon_size), dtype=np.float32)
        result[:, land_idx] = preds
        return result.reshape(n_time, lat_size, lon_size)

    def predict_quantiles(
        self,
        ds_eval: xr.Dataset,
        regime_probs_eval: np.ndarray | dict[int, np.ndarray],
        lead: int,
    ) -> dict[float, np.ndarray]:
        """Predict calibrated quantile bounds (0.1, 0.5, 0.9) with monotonic crossing prevention.

        Returns:
            Dictionary mapping quantile alpha to 3D rainfall grids (time, lat, lon).
        """
        if not self._fitted:
            raw = ds_eval["tp_raw"].sel(lead=lead).values
            return {q: raw for q in self.quantiles}

        raw_preds: dict[float, np.ndarray] = {}
        for alpha in sorted(self.quantiles):
            raw_preds[alpha] = self.predict(
                ds_eval, regime_probs_eval, lead=lead, quantile=alpha
            )

        # Enforce non-crossing monotonicity (q0.1 <= q0.5 <= q0.9)
        alphas = sorted(self.quantiles)
        stacked = np.stack([raw_preds[a] for a in alphas], axis=-1)
        sorted_stacked = np.sort(stacked, axis=-1)

        return {alphas[idx]: sorted_stacked[..., idx] for idx, _ in enumerate(alphas)}


    def compute_feature_attributions(
        self,
        ds_eval: xr.Dataset,
        regime_probs_eval: np.ndarray | dict[int, np.ndarray],
        lead: int,
        time_idx: int = -1,
    ) -> dict[str, np.ndarray]:
        """Compute grouped TreeSHAP attributions per land cell in mm for a given time step.

        Returns dict with grouped contributions:
          'moisture_instability', 'circulation_vorticity', 'terrain_orography',
          'regime_conditioning', 'nwp_baseline'
        Each mapped to a full 2D grid (lat_size, lon_size).
        """
        lat_size = ds_eval.sizes["lat"]
        lon_size = ds_eval.sizes["lon"]
        land = ds_eval["land_mask"].values
        land_idx = np.where(land.flatten() > 0.5)[0]
        n_land = len(land_idx)

        default_zero = {
            "moisture_instability": np.zeros((lat_size, lon_size), dtype=np.float32),
            "circulation_vorticity": np.zeros((lat_size, lon_size), dtype=np.float32),
            "terrain_orography": np.zeros((lat_size, lon_size), dtype=np.float32),
            "regime_conditioning": np.zeros((lat_size, lon_size), dtype=np.float32),
            "nwp_baseline": np.zeros((lat_size, lon_size), dtype=np.float32),
        }

        if not self._fitted or lead not in self.models or n_land == 0:
            return default_zero

        booster = self.models[lead]
        ds_single = ds_eval.isel(time=[time_idx])
        rp = (
            regime_probs_eval.get(lead, regime_probs_eval.get(1, list(regime_probs_eval.values())[0]))
            if isinstance(regime_probs_eval, dict)
            else regime_probs_eval
        )
        rp_single = rp[[time_idx]] if rp.ndim == 2 else rp

        X, _ = self._extract_features(ds_single, lead=lead, regime_probs=rp_single)
        if len(X) == 0:
            return default_zero

        # LightGBM TreeSHAP: shape (n_land, n_features + 1)
        shap_values = np.asarray(booster.predict(X, pred_contrib=True))

        # Map feature indices
        f_idx = {name: i for i, name in enumerate(self._FEATURE_NAMES)}
        base_val = shap_values[:, -1]

        # Group 1: Moisture & Instability (pwat, cape)
        grp_moisture = shap_values[:, f_idx["pwat"]] + shap_values[:, f_idx["cape"]]
        # Group 2: Circulation & Dynamics (u850, v850, vort850, mslp_anom)
        grp_circulation = (
            shap_values[:, f_idx["u850"]]
            + shap_values[:, f_idx["v850"]]
            + shap_values[:, f_idx["vort850"]]
            + shap_values[:, f_idx["mslp_anom"]]
        )
        # Group 3: Terrain & Orography (elevation, dist_coast)
        grp_terrain = shap_values[:, f_idx["elevation"]] + shap_values[:, f_idx["dist_coast"]]
        # Group 4: Regime Conditioning (p_normal, p_active, p_break, p_depression)
        grp_regime = (
            shap_values[:, f_idx["p_normal"]]
            + shap_values[:, f_idx["p_active"]]
            + shap_values[:, f_idx["p_break"]]
            + shap_values[:, f_idx["p_depression"]]
        )
        # Group 5: NWP Baseline & Lead (tp_raw, lead, day_of_season, base_val)
        grp_nwp = (
            shap_values[:, f_idx["tp_raw"]]
            + shap_values[:, f_idx["lead"]]
            + shap_values[:, f_idx["day_of_season"]]
            + base_val
        )

        out = {}
        for k, vals in [
            ("moisture_instability", grp_moisture),
            ("circulation_vorticity", grp_circulation),
            ("terrain_orography", grp_terrain),
            ("regime_conditioning", grp_regime),
            ("nwp_baseline", grp_nwp),
        ]:
            arr = np.zeros((lat_size * lon_size), dtype=np.float32)
            arr[land_idx] = vals
            out[k] = arr.reshape(lat_size, lon_size)

        return out
