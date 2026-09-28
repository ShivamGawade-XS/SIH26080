"""
Baseline Model B3: Regime-Wise Empirical Quantile Mapping (Deliverable D2).
Fits empirical quantile mapping transfer functions separately for each
synoptic regime class (normal, active, break, depression) and lead time.
"""

from __future__ import annotations

import numpy as np
import xarray as xr

from varsha.models.b1_qm import ModelB1QM


class ModelB3RegimeQM:
    """Regime-conditioned empirical quantile mapping corrector."""

    MODEL_NAME = "B3_RegimeQM"

    def __init__(self, n_quantiles: int = 50) -> None:
        self.n_quantiles = n_quantiles
        # Nested dict: regime_id -> lead -> ModelB1QM
        self.regime_models: dict[int, dict[int, ModelB1QM]] = {}
        self._fitted = False

    def fit(self, ds_train: xr.Dataset) -> ModelB3RegimeQM:
        """Fit empirical quantile mapping separately per regime and lead."""
        regimes = np.unique(ds_train["synoptic_regime"].values)
        leads = list(ds_train["lead"].values)

        for reg in regimes:
            reg_int = int(reg)
            self.regime_models[reg_int] = {}
            # Slice dataset for this regime
            reg_time_mask = ds_train["synoptic_regime"].values == reg_int
            if reg_time_mask.sum() < 5:
                # Fallback to global model if too few samples in regime
                ds_sub = ds_train
            else:
                ds_sub = ds_train.isel(time=reg_time_mask)

            for lead in leads:
                qm = ModelB1QM(n_quantiles=self.n_quantiles)
                qm.fit(ds_sub)
                self.regime_models[reg_int][int(lead)] = qm

        self._fitted = True
        return self

    def predict(
        self, ds_eval: xr.Dataset, lead: int, regime_probs: np.ndarray | None = None
    ) -> np.ndarray:
        """Predict corrected precipitation by blending or selecting regime QM transfer.

        Returns (time, lat, lon) array.
        """
        if not self._fitted:
            return ds_eval["tp_raw"].sel(lead=lead).values

        n_time = ds_eval.sizes["time"]
        lat_size = ds_eval.sizes["lat"]
        lon_size = ds_eval.sizes["lon"]
        output = np.zeros((n_time, lat_size, lon_size), dtype=np.float32)

        for t in range(n_time):
            ds_t = ds_eval.isel(time=[t])
            if regime_probs is not None:
                # Weighted mixture of quantile mapping predictions
                p = regime_probs[t]
                weighted_pred = np.zeros((lat_size, lon_size), dtype=np.float32)
                for reg_idx, weight in enumerate(p):
                    if reg_idx in self.regime_models and int(lead) in self.regime_models[reg_idx]:
                        pred_reg = self.regime_models[reg_idx][int(lead)].predict(ds_t, lead)[0]
                        weighted_pred += weight * pred_reg
                output[t] = weighted_pred
            else:
                # Use synoptic regime if available
                reg_val = (
                    int(ds_eval["synoptic_regime"].values[t]) if "synoptic_regime" in ds_eval else 0
                )
                if reg_val in self.regime_models and int(lead) in self.regime_models[reg_val]:
                    output[t] = self.regime_models[reg_val][int(lead)].predict(ds_t, lead)[0]
                else:
                    output[t] = ds_t["tp_raw"].sel(lead=lead).values[0]

        return output
