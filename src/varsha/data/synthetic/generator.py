"""
Synthetic Monsoon World Generator for Project Varsha.
Generates deterministic, physically grounded synthetic monsoon datasets
with known latent regimes, heavy-tail precipitation fields, and lead-dependent NWP biases.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import xarray as xr

from varsha.config import VarshaConfig


@dataclass
class SyntheticMonsoonWorld:
    ds_grid: xr.Dataset
    regime_labels_true: pd.DataFrame
    config: VarshaConfig


def generate_static_fields(
    lats: np.ndarray, lons: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate elevation, distance to coast, and land-sea mask."""
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Synthetic land mask: India-like triangle/subcontinent
    # Simple polygon approx: bounded roughly within subcontinent
    land_mask = (
        (lat_grid >= 8.0)
        & (lat_grid <= 37.0)
        & (lon_grid >= 68.5)
        & (lon_grid <= 97.0)
        & ~((lat_grid < 20.0) & (lon_grid < 72.5))  # Arabian Sea southwest
        & ~((lat_grid < 20.0) & (lon_grid > 85.0))  # Bay of Bengal southeast
    ).astype(float)

    # Western Ghats Ridge (lat 8-20, lon 73.5-75.5)
    ghats = (
        np.exp(-((lon_grid - 74.5) ** 2 / 1.5 + (lat_grid - 14.0) ** 2 / 40.0))
        * 1200.0
        * (lon_grid <= 76.0)
    )

    # Himalayan Arc (lat 27-36, lon 75-95)
    himalayas = np.exp(-((lat_grid - 30.0) ** 2 / 6.0)) * (lon_grid >= 75.0) * 3500.0

    # Northeast Hills (lat 24-28, lon 90-95)
    ne_hills = np.exp(-((lon_grid - 92.5) ** 2 / 4.0 + (lat_grid - 25.5) ** 2 / 4.0)) * 1500.0

    elevation = (ghats + himalayas + ne_hills) * land_mask
    elevation = np.clip(elevation, 0.0, 6000.0)

    # Distance to coast proxy (approximate km from coast edges)
    coastal_west = np.clip(np.abs(lon_grid - 73.0) * 100.0, 0.0, 1000.0)
    dist_coast = np.where(land_mask > 0, coastal_west, 0.0)

    return elevation, dist_coast, land_mask


def simulate_regime_sequence(n_days: int, seed: int = 42) -> list[str]:
    """Generate persistent Markov chain over {active, break, normal, depression}."""
    rng = np.random.RandomState(seed)
    states = ["active", "break", "normal", "depression"]
    # Transition matrix favoring spell persistence
    P = np.array(
        [
            [0.70, 0.05, 0.20, 0.05],  # from active
            [0.05, 0.70, 0.25, 0.00],  # from break
            [0.25, 0.20, 0.45, 0.10],  # from normal
            [0.20, 0.00, 0.40, 0.40],  # from depression
        ]
    )

    seq = ["normal"]
    current_idx = 2
    for _ in range(1, n_days):
        current_idx = rng.choice(4, p=P[current_idx])
        seq.append(states[current_idx])

    return seq


def generate_synthetic_dataset(
    config: VarshaConfig,
    seasons: list[str] | None = None,
    regime_dependent_bias: bool | None = None,
) -> xr.Dataset:
    """
    Generate multidimensional xarray Dataset containing truth, analysis fields,
    forecast predictors (PWAT, CAPE, u850, v850, vort850, mslp_anom), and raw NWP precipitation.
    """
    use_regime_bias = (
        regime_dependent_bias
        if regime_dependent_bias is not None
        else config.profile.regime_dependent_bias
    )
    res = config.profile.grid_resolution
    lats = np.arange(config.domain.lat_min, config.domain.lat_max + res / 2, res)
    lons = np.arange(config.domain.lon_min, config.domain.lon_max + res / 2, res)

    elevation, dist_coast, land_mask = generate_static_fields(lats, lons)

    season_list = (
        seasons
        or config.profile.train_seasons
        + config.profile.cal_seasons
        + config.profile.test_seasons
        + config.profile.pseudo_prospective_seasons
    )
    n_days_per_season = 122  # June 1 to Sept 30 (JJAS)
    leads = config.leads
    regime_records = []

    base_seed = config.profile.seed

    # Store data arrays
    time_coords = []

    # We will build 2D daily analysis arrays and 3D (time, lead, lat, lon) forecast arrays
    tp_obs_list = []
    tp_raw_list = []
    pwat_fcst_list = []
    cape_fcst_list = []
    u850_fcst_list = []
    v850_fcst_list = []
    vort850_fcst_list = []
    mslp_anom_fcst_list = []

    # Analysis fields
    pwat_anl_list = []
    u850_anl_list = []
    vort850_anl_list = []
    mslp_anl_list = []

    for s_idx, season in enumerate(season_list):
        s_seed = base_seed + s_idx * 1000
        rng = np.random.RandomState(s_seed)

        regime_seq = simulate_regime_sequence(n_days_per_season, seed=s_seed)

        # Depression tracking variables
        dep_lifetime = 0
        dep_center_lat, dep_center_lon = 20.0, 88.0

        for d in range(n_days_per_season):
            date_str = f"{season}-D{d + 1:03d}"
            time_coords.append(date_str)
            regime = regime_seq[d]

            # Update depression center if active depression
            if regime == "depression":
                if dep_lifetime == 0:
                    dep_center_lat = rng.uniform(19.0, 22.0)
                    dep_center_lon = rng.uniform(86.0, 89.0)
                    dep_lifetime = rng.randint(3, 6)
                else:
                    dep_center_lat += rng.uniform(0.1, 0.4)
                    dep_center_lon -= rng.uniform(0.8, 1.5)  # West-northwestward drift
                    dep_lifetime -= 1
            else:
                dep_lifetime = 0

            regime_records.append(
                {
                    "season": season,
                    "day_idx": d,
                    "valid_time": date_str,
                    "latent_regime": regime,
                    "dep_center_lat": dep_center_lat if regime == "depression" else np.nan,
                    "dep_center_lon": dep_center_lon if regime == "depression" else np.nan,
                }
            )

            # Base True Atmosphere fields
            # 1. Background moisture & monsoon trough
            lat_grid, lon_grid = np.meshgrid(lats, lons, indexing="ij")

            # PWAT (kg/m2)
            pwat_base = 45.0 + 15.0 * np.sin(np.pi * lat_grid / 30.0)
            if regime == "active":
                pwat_base += 10.0
            elif regime == "break":
                pwat_base -= 10.0
            pwat_true = np.clip(pwat_base + rng.normal(0, 3.0, pwat_base.shape), 20.0, 75.0)

            # Low level flow u850 (m/s)
            u850_base = np.zeros_like(lat_grid) + 8.0
            if regime == "active":
                u850_base = np.where((lat_grid >= 12.0) & (lat_grid <= 18.0), 16.0, 10.0)
            elif regime == "break":
                u850_base = np.where(lat_grid >= 26.0, 14.0, 4.0)
            u850_true = u850_base + rng.normal(0, 2.0, u850_base.shape)

            # Vorticity & MSLP
            vort_true = np.zeros_like(lat_grid) + 0.5e-5
            mslp_anom_true = np.zeros_like(lat_grid)

            if regime == "depression":
                dist_to_dep = np.sqrt(
                    (lat_grid - dep_center_lat) ** 2 + (lon_grid - dep_center_lon) ** 2
                )
                vort_true += 4.5e-5 * np.exp(-(dist_to_dep**2) / 8.0)
                mslp_anom_true -= 6.0 * np.exp(-(dist_to_dep**2) / 10.0)
            elif regime == "active":
                cmz_mask = (
                    (lat_grid >= 18.0)
                    & (lat_grid <= 28.0)
                    & (lon_grid >= 73.0)
                    & (lon_grid <= 86.0)
                )
                vort_true = np.where(cmz_mask, 2.0e-5, 0.5e-5)
                mslp_anom_true = np.where(cmz_mask, -2.5, 0.0)
            elif regime == "break":
                cmz_mask = (
                    (lat_grid >= 18.0)
                    & (lat_grid <= 28.0)
                    & (lon_grid >= 73.0)
                    & (lon_grid <= 86.0)
                )
                vort_true = np.where(cmz_mask, -1.0e-5, 1.0e-5)
                mslp_anom_true = np.where(cmz_mask, 2.5, -1.0)

            # True Rainfall Generation (Gamma distributed heavy tail + spatial coherence)
            # Orographic enhancement along Western Ghats with westerly flow
            orographic_rain = np.maximum(0.0, u850_true) * (elevation / 1000.0) * 4.0

            # Synoptic rain multiplier
            regime_mult = 1.0
            if regime == "active":
                regime_mult = 2.5
            elif regime == "break":
                regime_mult = 0.3
            elif regime == "depression":
                regime_mult = 3.5

            # Random spatially smoothed gamma noise
            gamma_noise = rng.gamma(shape=1.2, scale=8.0, size=lat_grid.shape)

            rain_true = (5.0 * regime_mult + orographic_rain + gamma_noise) * land_mask
            if regime == "depression":
                # Southwest quadrant heavy rain bias
                sw_quad = (
                    (lat_grid <= dep_center_lat)
                    & (lon_grid <= dep_center_lon)
                    & (dist_to_dep <= 5.0)
                )
                rain_true += (
                    np.where(sw_quad, 55.0 * np.exp(-(dist_to_dep**2) / 6.0), 0.0) * land_mask
                )
            elif regime == "break":
                # Concentrate rain in Himalayan foothills and northeast
                foothills = (lat_grid >= 26.0) & (lon_grid >= 82.0)
                rain_true = np.where(foothills, rain_true * 2.0, rain_true * 0.2)

            rain_true = np.clip(rain_true, 0.0, 350.0)
            tp_obs_list.append(rain_true)

            # Analysis fields (observed state representation)
            pwat_anl_list.append(pwat_true)
            u850_anl_list.append(u850_true)
            vort850_anl_list.append(vort_true)
            mslp_anl_list.append(mslp_anom_true)

            # Generate Lead-dependent NWP Forecasts (Leads 1 to 5)
            tp_raw_leads = []
            pwat_leads = []
            cape_leads = []
            u850_leads = []
            v850_leads = []
            vort850_leads = []
            mslp_leads = []

            for lead in leads:
                lead_factor = 1.0 + 0.15 * (lead - 1)

                # Predictors with lead degradation
                pwat_fcst = pwat_true + rng.normal(0, 1.5 * lead_factor, pwat_true.shape)
                cape_fcst = np.clip(
                    (pwat_fcst - 30.0) * 45.0 + rng.normal(0, 200.0, pwat_true.shape), 0.0, 4500.0
                )
                u850_fcst = u850_true + rng.normal(0, 1.0 * lead_factor, u850_true.shape)
                v850_fcst = rng.normal(2.0, 2.0 * lead_factor, u850_true.shape)
                vort_fcst = vort_true + rng.normal(0, 0.5e-5 * lead_factor, vort_true.shape)
                mslp_fcst = mslp_anom_true + rng.normal(0, 0.8 * lead_factor, mslp_anom_true.shape)

                # Raw NWP Rainfall with regime-dependent biases (if enabled)
                if use_regime_bias:
                    if regime == "active":
                        # Under-forecast heavy tail — stronger bias to be learnable by B4
                        tp_raw = np.where(
                            rain_true > 40.0, rain_true * (0.50 / lead_factor), rain_true * 0.85
                        )
                    elif regime == "break":
                        # Spurious light rain over central India — stronger wet bias
                        tp_raw = rain_true + np.where(
                            (lat_grid >= 15.0) & (lat_grid <= 25.0),
                            rng.uniform(6.0, 18.0, rain_true.shape),
                            0.0,
                        )
                    elif regime == "depression":
                        # Displaced footprint and smoothed peak — larger displacement
                        tp_raw = np.roll(rain_true, shift=int(lead) + 1, axis=1) * (0.65 / lead_factor)
                    else:
                        # Normal state: modest random bias
                        tp_raw = rain_true * rng.uniform(0.85, 1.15)
                else:
                    # Negative control: simple homogeneous unbiased Gaussian error
                    tp_raw = np.maximum(
                        0.0, rain_true + rng.normal(0, 5.0 * lead_factor, rain_true.shape)
                    )

                tp_raw = np.clip(tp_raw * land_mask, 0.0, 350.0)

                tp_raw_leads.append(tp_raw)
                pwat_leads.append(pwat_fcst)
                cape_leads.append(cape_fcst)
                u850_leads.append(u850_fcst)
                v850_leads.append(v850_fcst)
                vort850_leads.append(vort_fcst)
                mslp_leads.append(mslp_fcst)

            tp_raw_list.append(tp_raw_leads)
            pwat_fcst_list.append(pwat_leads)
            cape_fcst_list.append(cape_leads)
            u850_fcst_list.append(u850_leads)
            v850_fcst_list.append(v850_leads)
            vort850_fcst_list.append(vort850_leads)
            mslp_anom_fcst_list.append(mslp_leads)

    # Convert to xarray Dataset
    time_arr = np.array(time_coords)
    leads_arr = np.array(leads)

    tp_obs = np.array(tp_obs_list)  # (time, lat, lon)
    tp_raw = np.array(tp_raw_list)  # (time, lead, lat, lon)
    pwat_fcst = np.array(pwat_fcst_list)
    cape_fcst = np.array(cape_fcst_list)
    u850_fcst = np.array(u850_fcst_list)
    v850_fcst = np.array(v850_fcst_list)
    vort850_fcst = np.array(vort850_fcst_list)
    mslp_fcst = np.array(mslp_anom_fcst_list)

    pwat_anl = np.array(pwat_anl_list)
    u850_anl = np.array(u850_anl_list)
    vort850_anl = np.array(vort850_anl_list)
    mslp_anl = np.array(mslp_anl_list)

    ds = xr.Dataset(
        data_vars={
            "tp_obs": (["time", "lat", "lon"], tp_obs.astype(np.float32)),
            "tp_raw": (["time", "lead", "lat", "lon"], tp_raw.astype(np.float32)),
            "pwat": (["time", "lead", "lat", "lon"], pwat_fcst.astype(np.float32)),
            "cape": (["time", "lead", "lat", "lon"], cape_fcst.astype(np.float32)),
            "u850": (["time", "lead", "lat", "lon"], u850_fcst.astype(np.float32)),
            "v850": (["time", "lead", "lat", "lon"], v850_fcst.astype(np.float32)),
            "vort850": (["time", "lead", "lat", "lon"], vort850_fcst.astype(np.float32)),
            "mslp_anom": (["time", "lead", "lat", "lon"], mslp_fcst.astype(np.float32)),
            "pwat_anl": (["time", "lat", "lon"], pwat_anl.astype(np.float32)),
            "u850_anl": (["time", "lat", "lon"], u850_anl.astype(np.float32)),
            "vort850_anl": (["time", "lat", "lon"], vort850_anl.astype(np.float32)),
            "mslp_anl": (["time", "lat", "lon"], mslp_anl.astype(np.float32)),
            "elevation": (["lat", "lon"], elevation.astype(np.float32)),
            "dist_coast": (["lat", "lon"], dist_coast.astype(np.float32)),
            "land_mask": (["lat", "lon"], land_mask.astype(np.float32)),
        },
        coords={
            "time": time_arr,
            "lead": leads_arr,
            "lat": lats.astype(np.float32),
            "lon": lons.astype(np.float32),
        },
        attrs={
            "data_mode": "synthetic",
            "grid_resolution": res,
            "profile": config.profile.profile_name,
        },
    )

    return ds
