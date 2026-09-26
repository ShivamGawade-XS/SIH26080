# Product Requirements Document (PRD): Project Varsha

**System Name:** Varsha (Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts)  
**Problem Statement:** SIH 2026 — SIH26080 (Ministry of Earth Sciences / IMD)  
**Version:** 1.0.0 (MVP Foundation)  
**Author:** Varsha Engineering & Science Team

---

## 1. Executive Summary & Problem Context

Numerical Weather Prediction (NWP) models such as the Global Forecast System (GFS) and Unified Model (NCUM) exhibit systematic, regime-dependent precipitation forecast errors over the Indian subcontinent during the Southwest Monsoon (JJAS). Biases differ dramatically across dynamical weather regimes:
- **Active Monsoon:** Intense convective clusters, under-forecast of the extreme heavy tail.
- **Break Monsoon:** Trough shifts to Himalayan foothills; models frequently produce spurious light rain over central peninsular India.
- **Monsoon Lows & Depressions:** Vortex displacement errors; intense precipitation concentrated in the southwest quadrant is misplaced or smoothed.
- **Orographic & Coastal regimes:** Western Ghats and West Coast coastal convergence exhibit unresolved ridge-line smoothing and timing offsets.

Single global bias-correction algorithms (e.g., standard quantile mapping) fail to accommodate these regime-dependent error characteristics. **Varsha** implements a two-stage regime-aware post-processing pipeline:
1. **Regime Identification (D1):** Objective, forecast-side detection of synoptic regimes and compound geographic zones for Day-1 through Day-5.
2. **Regime-Conditioned Correction (D2):** Bias correction and calibrated quantile outputs (P10/P50/P90) conditioned on regime probabilities.
3. **Operational Exceedance Probabilities (D3):** Calibrated probabilities for IMD heavy rainfall thresholds (≥64.5 mm/day, ≥115.6 mm/day).
4. **District Aggregation & Decision Product (D4):** District-level metrics, indicative alert levels, and explainable feature attributions.
5. **Rigorous Verification (D5):** Spatial and categorical verification (RMSE, ETS, CSI, POD, FAR, FSS, Reliability) with block-bootstrap confidence intervals and positive/negative controls.

---

## 2. Target Users & User Jobs

| Persona | Core Responsibilities | Jobs to be Done (JTBD) |
|---|---|---|
| **Operational Forecaster / Met Analyst** | Reviews 00/12 UTC model cycles, prepares regional weather bulletins | Evaluate where and why AI correction modified raw NWP; inspect regime classification confidence; review spatial exceedance maps. |
| **District Disaster Management Officer (DDMO)** | Early warning, NDRF/SDRF deployment, flood preparedness | Instantly identify (in <30 seconds) whether their district faces heavy/very heavy rain in the next 5 days with clear uncertainty bounds. |
| **Scientific Evaluator / Hackathon Juror** | Assesses methodological novelty, leakage prevention, statistical significance | Verify that forecast improvements are statistically significant, leak-free, reproducible, and tested against negative controls. |

---

## 3. Required Deliverables Traceability (D1 – D5)

| ID | Deliverable Name | Functional Requirements | Verification Target |
|---|---|---|---|
| **D1** | **Weather Regime Classifier** | FR-02, FR-03 | Multiclass Macro F1, Calibration, Rule Recovery ≥ 90% |
| **D2** | **Bias-Corrected Rainfall Forecast** | FR-01, FR-04, FR-05, FR-10, FR-11 | Statistically significant RMSE reduction & ETS improvement over B0/B1/B2 |
| **D3** | **Heavy-Rainfall Exceedance Probability** | FR-06 | Calibrated probabilities (≥64.5, ≥115.6 mm), Brier Skill Score, Monotone consistency |
| **D4** | **District-Level Decision Product** | FR-07, FR-08 | District table, GeoJSON/CSV export, interactive console, printable brief |
| **D5** | **Verification Report & Honesty Panel** | FR-09, FR-12 | Standalone HTML report, Slice tables, Block Bootstrap CIs, Positive/Negative controls |

---

## 4. Functional Requirements (FR)

- **FR-01 (Data Ingestion & Common Grid):** Ingest raw NWP fields and observational data onto a unified common grid (0.5° demo, 0.25° full) with uniform land-sea mask. Support `synthetic` (offline ground truth) and `real` (GFS/IMD) modes behind a polymorphic interface.
- **FR-02 (Objective Regime Labelling):** Compute ground-truth synoptic regime labels (Active, Break, Depression, Normal) and geographic zones (Orographic, Coastal, Interior) using configurable, documented meteorological rules.
- **FR-03 (Forecast-Side Regime Classifier):** Predict calibrated regime probabilities for Day-1 through Day-5 using **forecast-side predictors only** available at initialisation time.
- **FR-04 (Grid-Level Corrected Forecast):** Produce daily precipitation predictions for Day-1 to Day-5 with calibrated quantiles (P10, P50, P90).
- **FR-05 (Model Benchmark Ladder B0–B4):** Maintain an explicit five-rung model ladder:
  - `B0`: Raw NWP forecast.
  - `B1`: Global Empirical Quantile Mapping.
  - `B2`: Global Gradient Boosted Decision Tree (LightGBM, no regime features).
  - `B3`: Regime-Specific Quantile Mapping.
  - `B4`: Regime-Aware Hurdle Gradient Boosting (regime probabilities + two-stage occurrence/amount).
- **FR-06 (Calibrated Heavy-Rain Probabilities):** Output calibrated probabilities for IMD operational thresholds:
  - Heavy Rain: $\ge 64.5\text{ mm/day}$
  - Very Heavy Rain: $\ge 115.6\text{ mm/day}$
  - Extremely Heavy Rain: $\ge 204.5\text{ mm/day}$ (enabled only when positive sample size allows; otherwise flagged).
  - Enforce monotone probability hierarchy: $P(\ge 204.5) \le P(\ge 115.6) \le P(\ge 64.5)$.
- **FR-07 (District Aggregation):** Aggregate grid forecasts to district administrative boundaries via cell-centre mapping, publishing interactive tables, CSV, and GeoJSON endpoints.
- **FR-08 (Indicative Alert Rules):** Assign risk levels (Green, Yellow, Orange, Red) based on explicit rules combining P50, expected area fraction $\ge 64.5$, and max cell probability.
- **FR-09 (Comprehensive Verification Suite):** Compute continuous (RMSE, MAE, Bias, Correlation), categorical (POD, FAR, CSI, ETS, FBI), spatial (FSS at scales 1, 3, 5, 9 cells), and probabilistic (Brier, ROC, PR, Reliability) metrics with day-block bootstrap confidence intervals.
- **FR-10 (Deterministic Execution CLI):** Provide unified CLI commands (`varsha data`, `varsha train`, `varsha verify`, `varsha serve`, `varsha report`) with fixed seeds and configuration manifests.
- **FR-11 (Explainable Feature Contributions):** Compute grouped TreeSHAP / LightGBM `pred_contrib` feature attributions for any district and lead time.
- **FR-12 (Honesty & Provenance Panel):** Display non-dismissable provenance banners (Data Mode: `synthetic` vs `real`), control check results, library versions, and known limitations on all UI screens and reports.

---

## 5. Non-Functional Requirements (NFR)

- **NFR-01 (Reproducibility):** Two independent runs from identical seeds produce bit-identical artifact hashes.
- **NFR-02 (Performance Budgets):**
  - `make demo-fast` runs in $\le 2\text{ minutes}$ (CI profile).
  - `make demo` runs in $\le 10\text{ minutes}$ on standard multi-core hardware.
  - Cached API endpoints respond with $p95 \le 300\text{ ms}$.
- **NFR-03 (Accessibility):** WCAG 2.2 Level AA compliance, zero serious/critical axe-core violations, full keyboard navigation.
- **NFR-04 (Responsive Cartography):** Seamless usability across mobile (390 px), tablet (768 px), and desktop (1440+ px).
- **NFR-05 (Offline Runtime):** Zero runtime external CDN calls, self-hosted fonts (`@fontsource`), bundled vector polygons.
- **NFR-06 (Observability & Manifests):** Every run bundle contains a cryptographically hashed `manifest.json` detailing git SHA, config hash, timings, and data provenance.
- **NFR-07 (Code Quality & Typing):** Strict typing (`mypy --strict` on core modules, TypeScript strict on UI), automated linting (`ruff`, `eslint`).

---

## 6. Scope Boundaries & Out of Scope (MVP)

- **Out of Scope for MVP:** Western Disturbance winter module (documented on roadmap), ensemble perturbation generators, live operational automated polling daemons, Hindi localisation runtime (i18n string catalog ready).
