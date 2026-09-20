# Open-Source Reuse Register — SIH26080 "Varsha" MVP

**Build team read this first.** This is the hand-off from Phase 0 (Scout) to Phase 1 (Build).

**Date:** 2026-09-20
**Status:** COMPLETE — all subsystems covered; human signoff items noted.

---

## How to use this register

- **Column "Mode"** tells you exactly how to use each entry:
  - `ADOPT` → add to `requirements.txt` / `package.json`; import normally
  - `CROSS-CHECK` → use it to validate our own implementation in tests; don't import it in production code
  - `REFERENCE` → read it, understand the algorithm, re-implement cleanly; do not copy code
  - `LEARN-FROM` → read paper/code for ideas; do not transcribe
  - `DATA-ADOPT` → use the data with attribution; do not import code
  - `SKIP / FLAG` → do not use; reason given

---

## S1 — Forecast Data Access

| Package | Repo | Licence | Mode | Notes |
|---|---|---|---|---|
| `herbie-data` | [blaylockbk/Herbie](https://github.com/blaylockbk/Herbie) ★790 | **MIT** | **ADOPT** | Downloads GFS, ECMWF, HRRR from NOMADS, AWS, GCS, Azure; supports GRIB byte-range subsetting. Active (pushed 2026-09-20). Pin version. |
| `ecmwf-opendata` | [ecmwf/ecmwf-opendata](https://github.com/ecmwf/ecmwf-opendata) ★338 | **Apache-2.0** | **ADOPT** | Official ECMWF open-data downloader. IFS/AIFS archive starts Feb 2024; use for test set, not training. |
| open-meteo server | [open-meteo/open-meteo](https://github.com/open-meteo/open-meteo) ★6222 | AGPL-3.0 | **SKIP / FLAG** | Server code is AGPL. Their public API *might* be usable as a data route; requires human sign-off (HUMAN_SIGNOFF H2). Do not import the server code. |

> **S1 spike needed:** Run `Herbie` for one July 2025 day, fetch APCP + U850 + PWAT over India, confirm GRIB subsetting works and data volume is manageable (target: < 200 MB / run). Record in `spikes/spike_s1_herbie.py`.

---

## S2 — Indian Observation Access

| Package | Repo | Licence | Mode | Notes |
|---|---|---|---|---|
| `imdlib` | [iamsaswata/imdlib](https://github.com/iamsaswata/imdlib) ★43 | **MIT** | **ADOPT with fallback** | Downloads IMD gridded 0.25° daily rainfall. Last pushed 2026-09-17 (actively maintained). CRITICAL: run a live download test first (ASSUMPTIONS A5). If it fails, fall back to IMERG. |
| `earthaccess` | [earthaccess-dev/earthaccess](https://github.com/earthaccess-dev/earthaccess) ★643 | **MIT** | **ADOPT** | NASA Earthdata auth + IMERG download. Use as fallback for recent-season obs. |

> **S2 spike needed:** `imdlib.open_data("rain", 2024, 2024, "yearwise")` — confirm download works, units (mm/day), grid (0.25°), and 2026 data availability. Record in `spikes/spike_s2_imdlib.py`.

---

## S3 — Reanalysis / Analysis-Ready Data

| Package | Repo | Licence | Mode | Notes |
|---|---|---|---|---|
| ARCO-ERA5 | [google-research/arco-era5](https://github.com/google-research/arco-era5) ★504 | **Apache-2.0** | **REFERENCE** | ERA5 in Zarr on GCS. Requires GCP auth; feasible for regime-labelling spike but don't depend on it for daily ops. Recipes are Apache-2.0. |
| WeatherBench2 | [google-research/weatherbench2](https://github.com/google-research/weatherbench2) ★637 | **Apache-2.0** | **REFERENCE** | Evaluation protocol reference; not directly used. Verification methodology is instructive. |
| CDS API | (ECMWF, not a GitHub repo) | T&C | **ADOPT** | `cdsapi` Python client (MIT) for ERA5 via Copernicus CDS. Standard, reliable. Needs a free CDS account. |

---

## S4 — Bias Correction / Quantile Mapping

Our QM implementation is custom (see code sketches in `SIH26080_Solution_Blueprint.md` §12). These packages are used to validate our output.

| Package | Repo | Licence | Mode | Notes |
|---|---|---|---|---|
| `xclim` (sdba module) | [Ouranosinc/xclim](https://github.com/Ouranosinc/xclim) ★404 | **Apache-2.0** | **CROSS-CHECK** | Run `xclim.sdba.EmpiricalQuantileMapping` on the same data and compare to our QM output. Agreement validates our implementation; disagreement should be explained. |
| `ibicus` | [ecmwf-projects/ibicus](https://github.com/ecmwf-projects/ibicus) ★83 | **Apache-2.0** | **REFERENCE** | ECMWF bias-adjustment toolkit. Designed for climate model, not NWP. Read for evaluation framework ideas. |
| `python-cmethods` | [btschwertfeger/python-cmethods](https://github.com/btschwertfeger/python-cmethods) ★82 | **GPL-3.0** | **SKIP — REFERENCE ONLY** | Do not import. Read for algorithmic understanding only. |
| `SBCK-python` | [yrobink/SBCK-python](https://github.com/yrobink/SBCK-python) ★16 | **GPL-3.0** | **SKIP — REFERENCE ONLY** | Same as above. |

---

## S5 — ML Post-Processing and Benchmarks

| Repo | Licence | Mode | Notes |
|---|---|---|---|
| [slerch/ppnn](https://github.com/slerch/ppnn) ★63 (Rasp & Lerch 2018) | **MIT** | **LEARN-FROM** | The canonical neural network post-processing paper. Read for train/test split protocol, CRPS evaluation, and baseline EMOS comparison. Do not transcribe code (it's R + Python, 2m temperature, European domain). |
| [EUPPBench](https://github.com/EUPP-benchmark/climetlab-eumetnet-postprocessing-benchmark) ★32 | **BSD-3-Clause** | **REFERENCE** | European post-processing benchmark protocol. Read for evaluation methodology. Different region and variable. |
| [khoehlein/Permutation-invariant-Postprocessing](https://github.com/khoehlein/Permutation-invariant-Postprocessing) ★4 | **MIT** | **REFERENCE** | Research code for permutation-invariant ensemble post-processing. Different approach (neural). |

---

## S6 — Monsoon Diagnostics and Regimes

| Package | Repo | Licence | Mode | Notes |
|---|---|---|---|---|
| `metpy` | [Unidata/MetPy](https://github.com/Unidata/MetPy) ★1442 | **BSD-3-Clause** | **ADOPT** | Vorticity calculation, pressure interpolation, derived fields. Use `metpy.calc.vorticity` for 850 hPa relative vorticity. Widely tested. |
| `windspharm` | [ajdawson/windspharm](https://github.com/ajdawson/windspharm) ★100 | **MIT** | **ADOPT** | Spherical harmonic wind analysis. Useful for divergence and streamfunction — helps characterise monsoon trough position and LLJ. |
| TempestExtremes | [ClimateGlobalChange/tempestextremes](https://github.com/ClimateGlobalChange/tempestextremes) ★147 | **BSD-2-Clause** | **REFERENCE** | C++ CLI tool for cyclone/low tracking. Reference for detection algorithm design; implement our own lighter Python version with MetPy + scipy.ndimage for MVP. |

> **S6 novel work:** Active/break detection, low-pressure-system tracker, orographic flow index, coastal zone logic — all built by the team. These are the core novelty of Module A.

---

## S7 — Forecast Verification

This subsystem is the most important for correctness. Use **two independent implementations** and require them to agree within numerical tolerance.

| Package | Repo | Licence | Mode | Notes |
|---|---|---|---|---|
| `scores` | [nci/scores](https://github.com/nci/scores) ★234 | **Apache-2.0** | **ADOPT + PRIMARY CROSS-CHECK** | xarray-native, JOSS-reviewed, Apache-2.0. Has POD, FAR, CSI, ETS, FSS, Brier, Diebold-Mariano. **Use as the independent oracle** to cross-check our metric code from `SIH26080_Solution_Blueprint.md` §12. |
| `xskillscore` | [xarray-contrib/xskillscore](https://github.com/xarray-contrib/xskillscore) ★243 | **Apache-2.0** | **CROSS-CHECK** | Second independent metric implementation; use for additional confidence. |
| `pysteps.verification` | [pySTEPS/pysteps](https://github.com/pySTEPS/pysteps) ★587 | **BSD-3-Clause** | **CROSS-CHECK** | FSS implementation from a mature nowcasting framework. Cross-check our FSS function against `pysteps.verification.spatialscores.fss`. |
| `climpred` | [pangeo-data/climpred](https://github.com/pangeo-data/climpred) ★259 | **MIT** | **REFERENCE** | Subseasonal/seasonal verification. Useful for block-bootstrap CI patterns. |
| `netcal` | [EFS-OpenSource/calibration-framework](https://github.com/EFS-OpenSource/calibration-framework) ★380 | **Apache-2.0** | **CROSS-CHECK** | Calibration metrics (ECE, reliability). Cross-check our reliability diagram and Brier score computation. |
| WFRT/verif | [WFRT/verif](https://github.com/WFRT/verif) ★103 | BSD-3-Clause (custom) | **REFERENCE** | Visual verification tool used at operational NWP centres. Reference for what a professional verification report looks like. We auto-generate our own. |
| METplus | [dtcenter/METplus](https://github.com/dtcenter/METplus) ★121 | Apache-2.0 | **REFERENCE** | Heavy NCAR verification suite. Reference for metric definitions only. Too heavy for MVP. |

---

## S8 — Calibration and Uncertainty

| Package | Repo | Licence | Mode | Notes |
|---|---|---|---|---|
| `scikit-learn` | [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn) ★67k | **BSD-3-Clause** | **ADOPT** | `sklearn.calibration.CalibratedClassifierCV` (isotonic/Platt), `sklearn.isotonic.IsotonicRegression`. Already installed. |
| `mapie` | [scikit-learn-contrib/MAPIE](https://github.com/scikit-learn-contrib/MAPIE) ★1591 | **BSD-3-Clause** | **ADOPT** | Conformal prediction intervals around our quantile-regression outputs. Useful for uncertainty bands on Day-3 to Day-5. |

---

## S9 — Geospatial Operations

| Package | Repo | Licence | Mode | Notes |
|---|---|---|---|---|
| `xesmf` | [pangeo-data/xESMF](https://github.com/pangeo-data/xESMF) ★252 | **MIT** | **ADOPT** | Conservative regridding of GFS 0.25° to IMD 0.25° grid (same resolution, but conservative ensures rainfall totals are preserved). Use the `pangeo-data` fork (active); not the `JiaweiZhuang` original (inactive since 2022). |
| `xarray-regrid` | [xarray-contrib/xarray-regrid](https://github.com/xarray-contrib/xarray-regrid) ★107 | **Apache-2.0** | **ADOPT** | Bilinear/conservative regridding without ESMF dependency. Lighter alternative to xESMF for rapid prototyping. |
| `regionmask` | [regionmask/regionmask](https://github.com/regionmask/regionmask) ★260 | **MIT** | **ADOPT** | India land mask; also useful for core monsoon zone boundary. |
| `exactextract` | [isciences/exactextract](https://github.com/isciences/exactextract) ★322 | **Apache-2.0** | **ADOPT** | Exact area-weighted grid-to-polygon aggregation. Replaces `xagg` (which is GPL). Has Python API. |
| `xagg` | [ks905383/xagg](https://github.com/ks905383/xagg) ★102 | **GPL-3.0** | **SKIP** | GPL; replaced by exactextract. |

---

## S10 — Boundary Data

| Source | Repo / URL | Data Licence | Mode | Notes |
|---|---|---|---|---|
| datameet India maps | [datameet/maps](https://github.com/datameet/maps) ★476 | MIT (code) | **DATA-ADOPT with review** | District + state shapefiles. MIT licence. **But**: community-sourced; accuracy for Jammu & Kashmir, Ladakh etc. needs review (HUMAN_SIGNOFF H4). |
| geoBoundaries | [wmgeolab/geoBoundaries](https://github.com/wmgeolab/geoBoundaries) ★409 | CC-BY 4.0 (likely; HUMAN_SIGNOFF H3) | **REFERENCE** | Authoritative global boundaries. Use for cross-check if CC-BY confirmed. |
| data.gov.in | [https://data.gov.in](https://data.gov.in) | Open Government Data | **DATA-ADOPT** | Recommended: download India district shapefile from the official Open Government Data platform. This is the safest choice in front of a government jury. |

---

## S11 — Web Mapping and Charts

| Package | Repo | Licence | Mode | Notes |
|---|---|---|---|---|
| MapLibre GL JS | [maplibre/maplibre-gl-js](https://github.com/maplibre/maplibre-gl-js) ★11k | BSD-3-Clause (see ASSUMPTIONS A1) | **ADOPT** | Interactive vector/raster map. Use for district choropleth (Feature-State) and raster grid layer. `npm install maplibre-gl`. |
| D3 | [d3/d3](https://github.com/d3/d3) ★113k | ISC | **ADOPT** | Time-series, skill-score, and performance diagrams. ISC = MIT-compatible. |
| Observable Plot | [observablehq/plot](https://github.com/observablehq/plot) ★5k | ISC | **ADOPT** | Higher-level charting on top of D3. Concise API for reliability diagrams and line charts. |
| zarrita.js | [manzt/zarrita.js](https://github.com/manzt/zarrita.js) ★145 | MIT | **ADOPT** | Read Zarr arrays in the browser for raster rendering without a tile server. |
| deck.gl | [visgl/deck.gl](https://github.com/visgl/deck.gl) ★14k | MIT | **OPTIONAL** | Large-scale geospatial data rendering. Stretch goal if raster grid rendering in MapLibre proves slow. |
| cambecc/earth | [cambecc/earth](https://github.com/cambecc/earth) ★6k | MIT | **REFERENCE** | Design inspiration for weather visualisation UI patterns only. Do not copy code. |

---

## S12 — Prior Art on This Exact Problem

**Finding:** No publicly available repository for "regime-aware monsoon rainfall post-processing over India" was found in any search conducted in this session. The closest public work is:

- **slerch/ppnn** (Rasp & Lerch 2018): ML post-processing, but for 2m temperature in Europe with ensemble NWP.
- **EUPPBench**: European benchmark, temperature, precipitation.
- No Indian-domain, monsoon-specific, regime-conditioned ML post-processing was found on GitHub, PyPI, or via web search.

**Implication:** This confirms our novelty claim is defensible. Frame it as "the first open-source, regime-aware, district-level monsoon rainfall post-processing system with a rigorous model ladder and Indian domain focus." Do not say "the first in the world" as unpublished or private work may exist at IMD/NCMRWF/IITM.

---

## S13 — Engineering Scaffolding

**Finding:** No orchestration framework (DVC, Prefect, Dagster) is recommended for MVP. They add configuration overhead without proportional benefit at hackathon scale.

**Recommendation (ponytail ultra):**
- One `Makefile` or `pipeline.sh` that runs each stage in order.
- Results stored as Zarr/NetCDF + Parquet. 
- FastAPI + uvicorn for the API.
- No scheduler needed; a single `python run_daily.py` called by a cron job is sufficient.

---

## Licence Danger Summary

| ⚠️ Package | Licence | Risk |
|---|---|---|
| `open-meteo` server | AGPL-3.0 | Do not ship as part of product. API use needs human review |
| `python-cmethods` | GPL-3.0 | Reference only; no import |
| `SBCK-python` | GPL-3.0 | Reference only; no import |
| `xagg` | GPL-3.0 | Do not use; replaced by exactextract |
| `datameet/maps` | MIT (code) but community data | Boundary accuracy risk in front of government jury |
| `geoBoundaries` | Likely CC-BY 4.0 | Attribution required; licence not SPDX-asserted |

---

## Recommended `requirements.txt` stubs (to verify in build)

```text
# Data access
herbie-data>=2026.0
ecmwf-opendata>=0.3
imdlib>=0.2
earthaccess>=0.9
cdsapi>=0.7

# Met calculations
metpy>=1.6
windspharm>=1.7

# Verification (all cross-check)
scores>=0.10
xskillscore>=0.0.25
pysteps>=1.8
netcal>=1.4
mapie>=0.8

# Geospatial
xesmf>=0.8
xarray-regrid>=0.3
regionmask>=0.12
exactextract>=0.3

# ML
lightgbm>=4.0    # already installed
scikit-learn>=1.4  # already installed

# Backend
fastapi>=0.111
uvicorn>=0.30

# Core scientific
xarray>=2024.3
numpy>=2.0
pandas>=2.2
scipy>=1.13
```

> **Note:** LightGBM and scikit-learn are already installed (confirmed in environment check). Pin exact versions in `requirements.txt` with `pip freeze` after environment setup.
