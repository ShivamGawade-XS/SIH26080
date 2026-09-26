"""
Feature Registry and Leakage Guard for Project Varsha.
Governing Rule: Section 6.7 (Enforce no-leakage in code, not intention).

Every feature used in training or inference must be registered with:
- name: Identifier
- source: 'forecast', 'static', 'climatology', or 'regime_oof'
- time_reference: 'forecast_valid', 'static', 'climatology', 'oof_probability'
- available_at: 'init_time' (must be <= init_time of the forecast)

Any feature not available at init_time (e.g. valid_time observations, analysis fields)
is strictly rejected when constructing the model feature matrix.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    source: Literal["forecast", "static", "climatology", "regime_oof", "observation"]
    time_reference: Literal[
        "forecast_valid", "static", "climatology", "oof_probability", "observed_valid"
    ]
    available_at: Literal["init_time", "valid_time", "static"]
    description: str


class FeatureRegistry:
    """Registry maintaining approved features and guarding against temporal leakage."""

    def __init__(self) -> None:
        self._registry: dict[str, FeatureSpec] = {}
        self._register_default_features()

    def register(self, spec: FeatureSpec) -> None:
        """Register a feature specification."""
        self._registry[spec.name] = spec

    def get(self, name: str) -> FeatureSpec:
        """Retrieve a feature specification by name."""
        if name not in self._registry:
            raise KeyError(f"Feature '{name}' is not registered in FeatureRegistry.")
        return self._registry[name]

    def validate_features(self, feature_names: list[str]) -> None:
        """Assert all requested features are safe from temporal leakage.

        Raises ValueError if any feature is an observation or not available at init_time.
        """
        for name in feature_names:
            spec = self.get(name)
            if (
                spec.source == "observation"
                or spec.available_at != "init_time"
                and spec.available_at != "static"
            ):
                raise ValueError(
                    f"LEAKAGE GUARD VIOLATION: Feature '{name}' is marked as source='{spec.source}' "
                    f"and available_at='{spec.available_at}'. Features available after init_time "
                    f"are strictly prohibited in forecast post-processing."
                )

    def _register_default_features(self) -> None:
        # Static geographical fields
        self.register(
            FeatureSpec(
                name="elevation",
                source="static",
                time_reference="static",
                available_at="static",
                description="Terrain elevation in meters",
            )
        )
        self.register(
            FeatureSpec(
                name="dist_coast",
                source="static",
                time_reference="static",
                available_at="static",
                description="Distance to Indian coastline in kilometers",
            )
        )

        # NWP forecast predictors (available at init_time)
        self.register(
            FeatureSpec(
                name="tp_raw",
                source="forecast",
                time_reference="forecast_valid",
                available_at="init_time",
                description="Raw NWP total precipitation forecast (mm/day)",
            )
        )
        self.register(
            FeatureSpec(
                name="pwat",
                source="forecast",
                time_reference="forecast_valid",
                available_at="init_time",
                description="Precipitable water anomaly / column moisture (mm)",
            )
        )
        self.register(
            FeatureSpec(
                name="cape",
                source="forecast",
                time_reference="forecast_valid",
                available_at="init_time",
                description="Convective Available Potential Energy (J/kg)",
            )
        )
        self.register(
            FeatureSpec(
                name="u850",
                source="forecast",
                time_reference="forecast_valid",
                available_at="init_time",
                description="850 hPa zonal wind component (m/s)",
            )
        )
        self.register(
            FeatureSpec(
                name="v850",
                source="forecast",
                time_reference="forecast_valid",
                available_at="init_time",
                description="850 hPa meridional wind component (m/s)",
            )
        )
        self.register(
            FeatureSpec(
                name="vort850",
                source="forecast",
                time_reference="forecast_valid",
                available_at="init_time",
                description="850 hPa relative vorticity (10^-5 s^-1)",
            )
        )
        self.register(
            FeatureSpec(
                name="mslp_anom",
                source="forecast",
                time_reference="forecast_valid",
                available_at="init_time",
                description="Mean sea level pressure anomaly (hPa)",
            )
        )
        self.register(
            FeatureSpec(
                name="lead",
                source="forecast",
                time_reference="forecast_valid",
                available_at="init_time",
                description="Forecast lead day index (1..5)",
            )
        )
        self.register(
            FeatureSpec(
                name="day_of_season",
                source="climatology",
                time_reference="climatology",
                available_at="init_time",
                description="Day of JJAS season (1..122)",
            )
        )

        # Out-of-fold regime probabilities (strictly computed without in-sample leakage)
        for regime in ["p_normal", "p_active", "p_break", "p_depression"]:
            self.register(
                FeatureSpec(
                    name=regime,
                    source="regime_oof",
                    time_reference="oof_probability",
                    available_at="init_time",
                    description=f"Out-of-fold calibrated probability for regime {regime}",
                )
            )

        # Explicitly registered forbidden observation fields to catch accidental usage
        self.register(
            FeatureSpec(
                name="tp_obs",
                source="observation",
                time_reference="observed_valid",
                available_at="valid_time",
                description="Observed precipitation (Ground Truth Target)",
            )
        )
        self.register(
            FeatureSpec(
                name="synoptic_regime",
                source="observation",
                time_reference="observed_valid",
                available_at="valid_time",
                description="Observed ground truth regime label from analysis",
            )
        )


FEATURE_REGISTRY = FeatureRegistry()
