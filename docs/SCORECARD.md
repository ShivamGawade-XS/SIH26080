# Verification Scorecard: Project Varsha

**Last Updated:** Phase 1 Baseline (Pre-Iteration 0)  
**Governing Rule:** Section 4.4 (Scorecard Pass Thresholds) & N5 (No Gaming)

---

## 1. Scorecard Summary Table

| Category | Measure / Metric | Pass Threshold | Current Status | Evidence / Notes |
|---|---|---|---|---|
| **Traceability** | Deliverables D1–D5 matrix $\rightarrow$ Code $\rightarrow$ API $\rightarrow$ UI $\rightarrow$ Tests | 100% rows green | 🟡 In Progress | Phase 1 Foundation created; D1–D5 traced in PRD and Architecture |
| **Statistical Validity**| Positive control, negative control, leakage canaries, bootstrap CIs | All pass | 🟡 In Progress | Control suites configured in `tests/controls/` |
| **Backend Tests** | Code coverage on core libraries (metrics, alignment, rules, models, aggregation) | $\ge 85\%$ core, $\ge 70\%$ overall | 🟡 In Progress | Baseline pytest suites configured in `tests/` |
| **Frontend Tests** | Unit tests for data transforms; Playwright E2E demo path on Chromium & WebKit | All pass | 🟡 In Progress | Web application test framework configured |
| **Accessibility (A11y)**| `axe-core` on all routes across both themes; keyboard demo path | 0 serious / critical | 🟡 In Progress | Design tokens and headless accessible primitives configured |
| **Performance** | Lighthouse Desktop (Perf, A11y, Best Practices); API cached latency p95 | $\ge 90$ each; $\le 300\text{ ms}$ | 🟡 In Progress | Static product bundle architecture benchmarked |
| **Security** | `pip-audit` & `npm audit`; input validation; no secrets in repo | 0 unresolved high/crit | 🟢 Pass | Scanned zero credentials; clean audit baseline |
| **Documentation** | `scripts/verify_docs.py`; zero unreplaced placeholders; numbers generated | All pass | 🟢 Pass | Phase 1 documentation suite active |
| **Design Integrity** | AI-look audit (Appendix B); AA contrast; 3 viewports $\times$ 2 themes | Zero tells; AA contrast | 🟢 Pass | Custom palette, tabular numbers, hairline rules |
| **Reproducibility** | Fresh clone `make demo`; bit-identical artifact hashes across runs | Bit-identical hashes | 🟡 In Progress | Fixed seeds and deterministic manifest generation configured |

---

## 2. Deliverables Traceability Matrix (D1 – D5)

| Deliverable ID | Core Function | Pipeline Module | API Route | UI Surface | Verification Test Suite | Status |
|---|---|---|---|---|---|---|
| **D1: Regime Classifier** | Synoptic & zone classification from forecast features | `src/varsha/regimes/` | `GET /api/v1/runs/{id}/regime` | Console Left Rail & Regimes View (`/regimes`) | `tests/unit/test_regime_rules.py` | 🟡 In Progress |
| **D2: Bias-Corrected Forecast** | Grid-level P10/P50/P90 correction via Model B4 | `src/varsha/models/b4_regime_gbm.py` | `GET /api/v1/runs/{id}/grid` | Console Main Map & Inspector | `tests/unit/test_models.py` | 🟡 In Progress |
| **D3: Heavy Rain Probabilities**| Calibrated exceedance probabilities at 64.5 & 115.6 mm | `src/varsha/models/heavy_rain.py` | `GET /api/v1/runs/{id}/districts` | Map Overlays & District Detail | `tests/unit/test_heavy_rain.py` | 🟡 In Progress |
| **D4: District Decision Product**| District spatial aggregation, table, CSV/GeoJSON, alerts | `src/varsha/product/districts.py` | `GET /api/v1/runs/{id}/districts.geojson` | District Table, Brief (`/d/:id`) | `tests/unit/test_district_product.py` | 🟡 In Progress |
| **D5: Verification Report** | Verification statistics, bootstrap CIs, controls | `src/varsha/verify/` | `GET /api/v1/verification/summary` | Verification View (`/verification`) & HTML Report | `tests/unit/test_metrics.py`, `tests/controls/` | 🟡 In Progress |
