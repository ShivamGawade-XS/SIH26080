# Varsha: Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts

[![CI Status](https://github.com/ShivamGawade-XS/SIH26080/actions/workflows/ci.yml/badge.svg)](https://github.com/ShivamGawade-XS/SIH26080/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)

> **PROVENANCE & INTEGRITY NOTICE (N1 / N2):**  
> Varsha operates in two data modes: `synthetic` (default, offline, reproducible) and `real` (NOAA GFS NWP forecasts paired with IMD gridded daily rainfall observations). Synthetic results demonstrate that the pipeline correctly recovers known physical regime structures and satisfies scientific controls under ground-truth conditions. **Synthetic metrics are never presented as real-world forecast skill.** All alert categories are indicative and do not constitute official statutory IMD warnings.

---

## 1. Problem Overview (SIH26080)

Rainfall forecast errors over the Indian subcontinent during the Southwest Monsoon (JJAS) vary systematically across dynamical weather regimes (Active Monsoon, Break Monsoon, Monsoon Lows/Depressions, Orographic, and Coastal regimes). Standard global bias-correction methods fail to adapt to these shifting physical states.

**Varsha** addresses problem statement **SIH26080** (Ministry of Earth Sciences / IMD) via a two-stage post-processing architecture:
1. **Regime Identification (D1):** Objective detection of synoptic regimes and geographic zones from forecast-side circulation predictors.
2. **Regime-Conditioned Hurdle Post-Processing (D2):** Quantile regression (P10/P50/P90) conditioned on out-of-fold regime probabilities.
3. **Heavy Rainfall Exceedance Probabilities (D3):** Calibrated exceedance models for IMD operational thresholds ($\ge 64.5\text{ mm}$, $\ge 115.6\text{ mm}$).
4. **District Decision Support (D4):** High-speed spatial aggregation to 700+ administrative districts with indicative alert levels and TreeSHAP explanations.
5. **Statistical Verification Suite (D5):** Categorical (POD, FAR, CSI, ETS), spatial (FSS), and continuous metrics with block-bootstrap confidence intervals and scientific controls.

---

## 2. 60-Second Quickstart

### Prerequisites
- Python 3.11+ (probed and tested on Python 3.13 / 3.14)
- Node.js 20+ and npm / pnpm

### Local Setup & Demo
```bash <!-- verify -->
# 1. Install dependencies
pip install -e ".[dev]"
cd web && npm install && cd ..

# 2. Run fast CI pipeline & tests (approx. 45s)
make demo-fast

# 3. Launch interactive web console
make demo
```

Once launched, navigate to `http://localhost:8000` to interact with the local cartography console.

---

## 3. Makefile Targets

| Target | Description |
|---|---|
| `make setup` | Install Python development dependencies and web packages |
| `make demo-fast` | Execute fast coarse-grid pipeline and full pytest suite ($\le 2\text{ min}$) |
| `make demo` | Execute default $0.5^\circ$ pipeline, build frontend, and launch server |
| `make test` | Run unit, property-based, golden, controls, and API test suites |
| `make lint` | Run Ruff linter on Python codebase |
| `make typecheck` | Run Mypy static type verification |
| `make verify` | Run comprehensive quality gate (lint, types, tests, docs check) |
| `make e2e` | Run Playwright end-to-end browser tests |
| `make clean` | Remove temporary product bundles and build caches |

---

## 4. Architecture & Model Ladder

```text
data sources ─► connectors ─► aligned dataset ─► feature registry ─► models B0-B4 ─► product bundle ─► FastAPI ─► React Web Console
 (synthetic)       (grid, mask)    (Zarr/NetCDF)  (leakage guard)    (hurdle gbm)   (JSON/GeoJSON)
```

- **B0 (Raw NWP):** Raw numerical model forecast baseline.
- **B1 (Global QM):** Global empirical quantile mapping.
- **B2 (Global LightGBM):** Gradient boosted trees using dynamical/thermodynamic predictors without regime inputs.
- **B3 (Regime QM):** Quantile mapping fitted per discrete regime category.
- **B4 (Regime Hurdle LightGBM):** Two-stage occurrence and quantile regression conditioned on out-of-fold regime probability distributions.

---

## 5. Documentation Map

- **Product Requirements:** [`docs/PRD.md`](docs/PRD.md)
- **System Architecture:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **Scientific Methodology:** [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)
- **Technology Stack & ADRs:** [`docs/TECH_STACK.md`](docs/TECH_STACK.md)
- **Design System:** [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md)
- **Verification Plan:** [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md)
- **Data & Model Cards:** [`docs/DATA_CARD.md`](docs/DATA_CARD.md) | [`docs/MODEL_CARD.md`](docs/MODEL_CARD.md)
- **Jury Demo Script:** [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md)
- **Known Limitations:** [`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md)
- **Open-Source Due Diligence:** [`docs/reuse/REUSE_REGISTER.md`](docs/reuse/REUSE_REGISTER.md)
