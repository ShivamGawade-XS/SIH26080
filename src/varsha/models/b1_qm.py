"""
Baseline Model B1: Global Empirical Quantile Mapping.
Applies empirical quantile mapping per lead time to correct distribution biases.
"""

import numpy as np
import xarray as xr


class ModelB1QM:
    """Empirical Quantile Mapping Baseline."""

    def __init__(self, n_quantiles: int = 100) -> None:
        self.name = "B1_GlobalQM"
        self.n_quantiles = n_quantiles
        self.quantiles = np.linspace(0.001, 0.999, n_quantiles)
        # Store empirical quantiles per lead: lead -> (nwp_q, obs_q)
        self.lead_maps: dict[int, tuple[np.ndarray, np.ndarray]] = {}

    def fit(self, ds_train: xr.Dataset) -> "ModelB1QM":
        """Fit empirical quantiles between raw forecast and observation per lead."""
        obs = ds_train["tp_obs"].values.flatten()
        obs_clean = obs[~np.isnan(obs)]
        obs_q = np.quantile(obs_clean, self.quantiles)

        leads = ds_train["lead"].values
        for lead in leads:
            raw = ds_train["tp_raw"].sel(lead=lead).values.flatten()
            raw_clean = raw[~np.isnan(raw)]
            raw_q = np.quantile(raw_clean, self.quantiles)
            # Ensure strictly monotonic for np.interp
            raw_q = np.maximum.accumulate(raw_q)
            obs_q_mono = np.maximum.accumulate(obs_q)
            self.lead_maps[int(lead)] = (raw_q, obs_q_mono)

        return self

    def predict(self, ds_eval: xr.Dataset, lead: int) -> np.ndarray:
        """Correct raw forecast using fitted empirical quantile map for lead."""
        raw = ds_eval["tp_raw"].sel(lead=lead).values
        if int(lead) not in self.lead_maps:
            return np.maximum(0.0, raw)

        raw_q, obs_q = self.lead_maps[int(lead)]

        # Interpolate
        orig_shape = raw.shape
        raw_flat = raw.flatten()
        corrected_flat = np.interp(raw_flat, raw_q, obs_q)
        corrected = corrected_flat.reshape(orig_shape)

        return np.maximum(0.0, corrected)
