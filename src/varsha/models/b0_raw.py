"""
Baseline Model B0: Raw NWP Forecast.
Extracts unmodified raw NWP precipitation forecast for each lead.
"""

import numpy as np
import xarray as xr


class ModelB0Raw:
    """Identity baseline model (Raw NWP)."""

    def __init__(self) -> None:
        self.name = "B0_Raw"
        self.fitted = False

    def fit(self, ds_train: xr.Dataset) -> "ModelB0Raw":
        self.fitted = True
        return self

    def predict(self, ds_eval: xr.Dataset, lead: int) -> np.ndarray:
        """
        Return raw NWP precipitation forecast for a given lead.
        Output shape: (n_time, n_lat, n_lon)
        """
        raw = ds_eval["tp_raw"].sel(lead=lead).values
        return np.maximum(0.0, raw)
