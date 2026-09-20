# Originality Statement — SIH26080 "Varsha" MVP

**Version:** 0.1 (post-Scout, pre-Build)
**Last updated:** 2026-09-20

> This document must be kept accurate as the build proceeds. Update it whenever a third-party component is added or removed.

---

## Summary

We integrate and validate proven open-source components for data access, geospatial processing, bias correction baselines, and forecast verification. The regime-aware layer — the novel contribution of this project — is built entirely by the team.

---

## What we build ourselves (novel contributions)

| Component | Description |
|---|---|
| Two-layer regime scheme | Synoptic × geographic compound keys; our original design |
| Objective regime labelling rules | Thresholds and circulation criteria adapted from literature; our Python implementation |
| Forecast-side regime classifier | Trained on forecast fields to predict regime labels at forecast time; our feature engineering and model training |
| Regime-aware bias correction (B3, B4) | Regime-specific quantile mapping and gradient-boosted model with soft regime probabilities as inputs |
| Soft regime blending | Mixing correction maps by regime probability weights |
| Heavy-rain probability product | Direct classification + threshold hierarchy enforcement + calibration |
| District alert product and dashboard | FastAPI backend + React/TypeScript/MapLibre frontend |
| Verification framework | Auto-generated report with all six named metrics, by regime, lead, and threshold |
| Controls and canaries | Positive/negative controls, leakage canaries — our design |

---

## What we adopt (standard dependencies — pip/npm)

| Package | Owner / Repo | Licence | Subsystem | Notes |
|---|---|---|---|---|
| Herbie | blaylockbk/Herbie | MIT | S1 | GFS/ECMWF download; used as-installed, not modified |
| ecmwf-opendata | ecmwf/ecmwf-opendata | Apache-2.0 | S1 | ECMWF open data downloader |
| imdlib | iamsaswata/imdlib | MIT | S2 | IMD gridded rainfall; requires live test (see ASSUMPTIONS A5) |
| earthaccess | earthaccess-dev/earthaccess | MIT | S2 | NASA Earthdata (IMERG backup) |
| MetPy | Unidata/MetPy | BSD-3-Clause | S6 | Met calculations, vorticity, derived fields |
| windspharm | ajdawson/windspharm | MIT | S6 | Spherical-harmonic wind analysis |
| nci/scores | nci/scores | Apache-2.0 | S7 | Primary verification metrics; used as independent cross-check oracle |
| xskillscore | xarray-contrib/xskillscore | Apache-2.0 | S7 | Secondary verification cross-check |
| pysteps (verification module only) | pySTEPS/pysteps | BSD-3-Clause | S7 | FSS cross-check |
| scikit-learn | scikit-learn/scikit-learn | BSD-3-Clause | S8 | Isotonic regression calibration, Platt scaling |
| MAPIE | scikit-learn-contrib/MAPIE | BSD-3-Clause | S8 | Conformal prediction intervals (stretch goal) |
| netcal (calibration-framework) | EFS-OpenSource/calibration-framework | Apache-2.0 | S8 | Calibration cross-check (ECE, reliability) |
| pangeo-data/xESMF | pangeo-data/xESMF | MIT | S9 | Conservative regridding (forecast → IMD grid) |
| xarray-regrid | xarray-contrib/xarray-regrid | Apache-2.0 | S9 | Bilinear regridding alternative |
| regionmask | regionmask/regionmask | MIT | S9 | India land mask |
| exactextract | isciences/exactextract | Apache-2.0 | S9 | Grid-to-polygon area-weighted aggregation |
| MapLibre GL JS | maplibre/maplibre-gl-js | BSD-3-Clause (see ASSUMPTIONS A1) | S11 | Interactive map |
| D3 | d3/d3 | ISC | S11 | Charts and visualisation |
| Observable Plot | observablehq/plot | ISC | S11 | Time-series and skill-score charts |
| zarrita.js | manzt/zarrita.js | MIT | S11 | Zarr grid reading in browser |

---

## What we use as a cross-check / reference (not vendored, not imported)

| Repo | Owner | Licence | Subsystem | Why reference-only |
|---|---|---|---|---|
| xclim `sdba` | Ouranosinc/xclim | Apache-2.0 | S4 | Climate-model bias adjustment; design is for long-period climate, not daily NWP. Used to cross-check our QM outputs numerically |
| ibicus | ecmwf-projects/ibicus | Apache-2.0 | S4 | Same as above; ECMWF provenance |
| python-cmethods | btschwertfeger/python-cmethods | **GPL-3.0** | S4 | GPL — cannot vendor or import. Read for algorithmic understanding only |
| SBCK-python | yrobink/SBCK-python | **GPL-3.0** | S4 | GPL — same rule |
| slerch/ppnn | slerch/ppnn | MIT | S5 | Rasp & Lerch 2018 reference code; read for evaluation protocol and pipeline patterns only |
| EUPPBench | EUPP-benchmark/climetlab-eumetnet-postprocessing-benchmark | BSD-3-Clause | S5 | European benchmark reference for evaluation protocol; not the same data or region |
| Permutation-invariant-Postprocessing | khoehlein/Permutation-invariant-Postprocessing | MIT | S5 | Research code; model type not our approach; read only |
| TempestExtremes | ClimateGlobalChange/tempestextremes | BSD-2-Clause | S6 | Low-pressure system detection (C++ CLI); reference for algorithm design; we implement our own vorticity-based detector in Python |
| properscoring | properscoring/properscoring | Apache-2.0 | S7 | **Archived** repo; use nci/scores instead |
| METplus | dtcenter/METplus | Apache-2.0 | S7 | Heavy industrial tool; reference for metric definitions only |
| WFRT/verif | WFRT/verif | BSD-3-Clause (custom text) | S7 | Visual verification tool; we auto-generate our own report |
| ARCO-ERA5 | google-research/arco-era5 | Apache-2.0 | S3 | Data route reference; requires GCP credentials for full archive |
| geoBoundaries | wmgeolab/geoBoundaries | CC-BY 4.0 (see ASSUMPTIONS A3) | S10 | Data reference; need human signoff on licence and boundary accuracy |
| cambecc/earth | cambecc/earth | MIT | S11 | Design inspiration only; not imported |
| ecmwf-lab/ai-models | ecmwf-lab/ai-models | Apache-2.0 | — | Frontier AI model runner; out of MVP scope |
| google-deepmind/weathernext | google-deepmind/weathernext | Apache-2.0 | — | AI model reference; weights may have NC restrictions |

---

## What we explicitly do NOT use (GPL / AGPL / no licence)

| Repo | Reason |
|---|---|
| open-meteo/open-meteo (server code) | AGPL-3.0 — cannot import or vendor. API usage as data route requires human signoff (HUMAN_SIGNOFF H2) |
| btschwertfeger/python-cmethods | GPL-3.0 — cannot import or vendor |
| yrobink/SBCK-python | GPL-3.0 — cannot import or vendor |
| ks905383/xagg | GPL-3.0 — replaced by exactextract (Apache-2.0) |
| Any repo with no LICENSE file | Default copyright = no permission; treat as reference-only |
