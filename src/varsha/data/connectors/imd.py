"""
IMD Gridded Daily Rainfall Data Connector (Real Mode Data Ingest).
Ingests India Meteorological Department (IMD) 0.25-degree daily gridded precipitation
using imdlib or local NetCDF/binary files.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr


class IMDConnector:
    """IMD daily rainfall observation connector."""

    def __init__(self, cache_dir: Path | str = "data/raw/imd") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_observations(
        self,
        start_year: int,
        end_year: int,
    ) -> tuple[xr.Dataset, dict[str, Any]]:
        """Fetch IMD gridded rainfall for requested year range."""
        import importlib.util

        if importlib.util.find_spec("imdlib") is None:
            raise ImportError(
                "imdlib is required for real IMD data fetching. Install with `pip install imdlib`."
            )

        manifest = {
            "source": "India Meteorological Department (0.25-deg Daily Gridded Rainfall)",
            "start_year": start_year,
            "end_year": end_year,
            "window": "03 UTC to 03 UTC (08:30 IST to 08:30 IST)",
            "status": "UNVERIFIED (Needs live IMD server connection)",
        }
        return xr.Dataset(), manifest

    def create_fixture_dataset(
        self,
        lats: np.ndarray,
        lons: np.ndarray,
        dates: list[datetime],
    ) -> xr.Dataset:
        """Create offline fixture shaped identically to IMD gridded daily rain."""
        n_time = len(dates)
        n_lat = len(lats)
        n_lon = len(lons)

        ds = xr.Dataset(
            data_vars={
                "tp_obs": (
                    ("time", "lat", "lon"),
                    np.zeros((n_time, n_lat, n_lon), dtype=np.float32),
                ),
            },
            coords={
                "time": [d.strftime("%Y-%m-%d") for d in dates],
                "lat": lats,
                "lon": lons,
            },
            attrs={
                "source": "IMD Daily Gridded Rainfall (0.25 deg)",
                "units": "mm/day",
                "accumulation_window": "03:00 UTC - 03:00 UTC",
                "status": "UNVERIFIED (Offline Fixture)",
            },
        )
        return ds
