# Project Backlog & Iteration Planning: Project Varsha

**Document Reference:** Varsha Development Backlog  
**Version:** 1.0.0

---

## 1. Iteration 0: Walking Skeleton (`v0.1`) — Iter-0

- [x] **BK-001 (Phase 0 & Foundation Docs):** Environment probe, PRD, Architecture, Methodology, Tech Stack, Scorecard, Assumptions, Design System.
- [ ] **BK-002 (Data & Synthetic Engine):** Implement `src/varsha/data/synthetic/` generator with terrain, Markov regimes, and lead-dependent NWP biases.
- [ ] **BK-003 (Regime Rules & Labeller):** Implement `src/varsha/regimes/rules.py` with CMZ anomaly and depression detection.
- [ ] **BK-004 (Model Baselines B0 & B1):** Implement raw NWP extractor and empirical quantile mapping in `src/varsha/models/`.
- [ ] **BK-005 (District Aggregator & Alert Rules):** Implement cell-centre district aggregator with sub-grid fallback in `src/varsha/product/districts.py`.
- [ ] **BK-006 (Bundle Builder & FastAPI Server):** Implement static bundle writer (`src/varsha/product/bundle.py`) and FastAPI endpoints in `src/varsha/api/app.py`.
- [ ] **BK-007 (Web Console Frontend):** Implement React + Vite web console with local MapLibre vector map, lead selector, district drawer, and theme toggle.
- [ ] **BK-008 (Walking Skeleton E2E & CI):** Implement end-to-end integration test and Playwright smoke test. Tag `iter-0`.

---

## 2. Iteration 1: Model Ladder (B2–B4), Heavy Rain & Controls — Iter-1

- [ ] **BK-101 (Forecast-Side Regime Classifier):** Implement LightGBM multiclass classifier predicting synoptic regimes from forecast predictors only.
- [ ] **BK-102 (Feature Registry & Leakage Guard):** Implement `src/varsha/features/registry.py` with strict temporal availability enforcement.
- [ ] **BK-103 (Model B4 Hurdle Implementation):** Implement two-stage LightGBM hurdle model with nested out-of-fold regime conditioning.
- [ ] **BK-104 (Heavy Rain Classifiers):** Dedicated calibrated binary models for $\ge 64.5\text{ mm}$ and $\ge 115.6\text{ mm}$ with monotone hierarchy enforcement.
- [ ] **BK-105 (Positive & Negative Controls):** Implement automated test suites asserting positive control on biased synthetic data and negative control on unbiased data.
- [ ] **BK-106 (Verification Metrics Suite):** Implement RMSE, MAE, POD, FAR, CSI, ETS, and Fractions Skill Score (FSS) with block-bootstrap CIs.

---

## 3. Iteration 2: Verification Report, SHAP Explanations & District Brief — Iter-2

- [ ] **BK-201 (Standalone HTML Report):** Jinja2 standalone verification report with embedded SVG charts and honesty panel.
- [ ] **BK-202 (TreeSHAP District Explanations):** Grouped feature contribution engine using LightGBM `pred_contrib`.
- [ ] **BK-203 (District Brief Page):** Dedicated printable single-page district brief (`/d/:id`) with 5-day small multiples and confidence statements.
- [ ] **BK-204 (Regime Sensitivity Analysis):** Perturbation analysis of regime thresholds and downstream skill impact.

---

## 4. Iteration 3: Cartography Polish, A11y & Performance Hardening — Iter-3

- [ ] **BK-301 (Cartography Refinement):** Swiss-style hairline graticules, custom classed IMD rain colormaps, and SVG hatch patterns.
- [ ] **BK-302 (Accessibility Compliance):** WCAG 2.2 AA audit with `axe-core`, keyboard shortcuts (`/`, `[`, `]`, `Esc`), and screen reader ARIA labels.
- [ ] **BK-303 (Performance & Quantized Grid):** Quantized binary grid packing ($\le 150\text{ KB}$) and cached API response optimization ($p95 \le 300\text{ ms}$).

---

## 5. Iteration 4+: Robustness, Multi-Persona Attack & Final Packaging — Iter-4+

- [ ] **BK-401 (Persona Attack Cycles):** Run 7 persona audits (Meteorologist, Statistician, District Officer, Art Director, SRE, Skeptical Juror, New Developer).
- [ ] **BK-402 (Fresh Clone Automation):** Verify `scripts/fresh_clone_test.sh` and deterministic artifact hashing.
- [ ] **BK-403 (Real-Mode Connectors & Smoke Test):** GFS via Herbie and IMD gridded via imdlib with offline fallback fixtures.
