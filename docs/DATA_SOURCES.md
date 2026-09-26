# Data Sources, Licences & Provenance Register

**Document Reference:** Varsha External Data Sources & Licencing Register  
**Version:** 1.0.0

---

## 1. Primary Data Sources Matrix

| Source Name | Provider / Agency | Licence | Access Method | Resolution & Variables | Verification Status |
|---|---|---|---|---|---|
| **Synthetic Monsoon World** | Project Varsha (Internal) | Apache-2.0 / MIT | `src/varsha/data/synthetic/` | $0.5^\circ / 0.25^\circ$, 24h precip, PWAT, CAPE, $u/v_{850}$, MSLP, vorticity | **VERIFIED** (Deterministic Python Generator) |
| **NOAA Global Forecast System (GFS)** | NOAA / NCEP Open Data | Public Domain / Open Data (CC0) | AWS S3 via `herbie-data` | $0.25^\circ$, APCP, PWAT, CAPE, UGRD/VGRD, PRES, HGT | **UNVERIFIED (Network/Cache required)** |
| **IMD Gridded Daily Rainfall** | India Meteorological Department (Pune) | IMD Data Policy (Academic/Research) | `imdlib` / NetCDF archive | $0.25^\circ \times 0.25^\circ$ daily rainfall (1901–present) | **UNVERIFIED (Portal credentials/archive)** |
| **Copernicus ERA5 Reanalysis** | ECMWF / Copernicus Climate Change Service | Copernicus Open Licence | CDS API (`cdsapi`) | $0.25^\circ$, hourly single levels & pressure levels | **UNVERIFIED (CDS API key required)** |
| **Survey of India / DataMeet Boundaries** | DataMeet Community Maps | Creative Commons Attribution 2.5 India / ODbL | `scripts/fetch_boundaries.py` | Indian State & District administrative vector polygons | **UNVERIFIED (Human Signoff H4)** |

---

## 2. Licensing Compliance & Attribution Statements

1. **NOAA GFS Data:** NOAA Open Data Dissemination (NODD) program via AWS Open Data. Free for commercial and research use.
2. **IMD Gridded Precipitation:** Published by the National Climate Centre, IMD Pune. Used for operational evaluation and academic benchmarking under fair use guidelines.
3. **Synthetic Datasets:** Fully synthetic mathematical constructs generated via deterministic seed algorithms. No real-world privacy or proprietary data encumbrance.
