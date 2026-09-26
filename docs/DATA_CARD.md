# Data Card: Varsha Meteorological Training & Evaluation Datasets

**Document Reference:** Varsha Dataset Provenance & Data Card  
**Version:** 1.0.0

---

## 1. Dataset Overview & Intended Use
The Varsha dataset suite provides paired meteorological numerical forecast predictors and observational ground-truth precipitation fields over the Indian monsoon domain ($6^\circ\text{N}-38^\circ\text{N}, 68^\circ\text{E}-98^\circ\text{E}$).
- **Primary Purpose:** Training, calibrating, and benchmarking regime-aware AI post-processing models (B0–B4) for Southwest Monsoon (JJAS) rainfall forecasts across Day-1 to Day-5.
- **Operating Modes:**
  1. `synthetic` (Offline default for CI, deterministic validation, positive/negative controls).
  2. `real` (NOAA GFS $0.25^\circ$ NWP forecasts paired with IMD $0.25^\circ$ gridded rainfall observations).

---

## 2. Spatial & Temporal Structure
- **Temporal Coverage:** June 1 to September 30 (JJAS Monsoon Season).
- **Accumulation Windows:** Daily 24-hour accumulation aligned strictly to $[03:00\text{ UTC}, 03:00\text{ UTC}]$ ($[08:30\text{ IST}, 08:30\text{ IST}]$).
- **Spatial Domain:** Indian Subcontinent and surrounding oceanic basins.
- **Coordinate Grid:** $0.5^\circ \times 0.5^\circ$ ($65 \times 61$ cells in demo profile) or $0.25^\circ \times 0.25^\circ$ ($129 \times 121$ cells in full profile).

---

## 3. Predictor Variables & Physical Units

| Variable Key | Description | Native Units | Transformation / Normalisation |
|---|---|---|---|
| `tp_raw` | Total raw NWP 24-hour precipitation forecast | mm/day | De-accumulated from sub-daily steps |
| `pwat` | Precipitable Water / Total Column Water Vapour | $\text{kg m}^{-2}$ | Continuous |
| `cape` | Convective Available Potential Energy | $\text{J kg}^{-1}$ | Continuous |
| `u850`, `v850` | Zonal and Meridional Wind at $850\text{ hPa}$ | $\text{m s}^{-1}$ | Low-level jet magnitude and direction |
| `vort850` | Relative Vorticity at $850\text{ hPa}$ | $10^{-5}\text{ s}^{-1}$ | Synoptic vortex identifier |
| `mslp_anom`| Mean Sea Level Pressure anomaly | $\text{hPa}$ | Standardized relative to regional climatology |
| `elevation` | Surface elevation terrain | meters | Static orographic forcing |
| `dist_coast`| Distance to coastline | km | Static maritime proxy |

---

## 4. Known Biases & Data Caveats
- **Synthetic Mode:** Synthetic datasets are designed to test mathematical pipeline recovery of known non-linear structures and must not be presented as real-world forecast skill (N1).
- **Real Mode:** IMD gridded observation availability has an operational latency of 24–48 hours; sparse rain-gauge density in mountainous terrain (Himalayas, NE India) introduces observational uncertainty in ground truth.
