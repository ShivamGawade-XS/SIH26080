# Ground-Truth Audit & Gap Register: Project Varsha (Phase 0)

**Date:** 2026-09-25  
**Audit Mode:** Strict empirical audit (all claims tested via live commands)

---

## 1. System Inventory & Baseline State

- **Git Commit:** `8577460` ("chore(scout): Prompt-0 open-source due diligence complete")
- **Git Status:** 1 commit ahead, untracked directories `src/`, `tests/`, `web/`, `configs/`, `docs/`, `products/`.
- **Git Tags:** None present.
- **Python:** 3.14.5 | **Node:** v25.1.0 | **uv:** 0.12.14 | **LightGBM:** 4.6.0 | **FastAPI:** 0.115.11

---

## 2. Flaw & Gap Register

| ID | Area | Severity | Finding | Evidence (command + output excerpt) |
|---|---|---|---|---|
| AUD-01 | Verification (D5) / CLI | **S1 — Fake Result** | `cmd_report` in `src/varsha/cli.py` hardcodes `model_ladder` (14.2, 12.1, 10.4, 11.2, 8.9) and `paired_comparisons` rather than computing them from actual model verification runs. | `src/varsha/cli.py:267-348`: Static dict containing hardcoded RMSE/MAE/ETS numbers passed directly to `generate_html_report()`. |
| AUD-02 | API / Fallbacks | **S1 — Fake Result** | `src/varsha/api/app.py` verification endpoints (`/verification/summary`, `/slices`, `/reliability`, `/controls`) return hardcoded synthetic dictionaries on fallback instead of typed HTTP errors or serving real computed files. | `src/varsha/api/app.py:216-290`: Exception handlers catch `HTTPException` and return static mock dictionaries. |
| AUD-03 | Performance / ML Engine | **S2 — Wrong or broken** | Training and test suites hit timeouts (>120s) because feature extraction (`b2_gbm.py`, `b4_regime_gbm.py`, `heavy_rain.py`, `classifier.py`) performs tens of thousands of individual Python loops over `.isel(time=t).sel(lead=lead)`. | `task-31` and `task-110` timed out at 120s in `test_model_ladder.py` and `varsha train`. |
| AUD-04 | Verification Artifacts | **S2 — Wrong or broken** | `compile_product_bundle` and `cmd_verify` do not save `verification.json`, `verification_slices.json`, and `reliability.json` into the product bundle, breaking API traceability. | `src/varsha/product/bundle.py`: Missing serialization for verification metrics and reliability data. |
| AUD-05 | Web / Unit Tests | **S3 — Bug / Rough Edge** | `npm run test` in `web/` fails because Vitest finds no test files in `web/src`. | `npm run test`: `No test files found, exiting with code 1`. |
| AUD-06 | Web / Bundle Size | **S4 — Polish** | Frontend initial JS bundle is 1,022 kB (284 kB gzipped), triggering Vite chunk-size warning. Needs route lazy loading for `/verification`, `/method`, etc. | `npm run build`: `dist/assets/index-DwlxqRsl.js 1,022.45 kB ... Some chunks are larger than 500 kB`. |
| AUD-07 | Product Bundle / Hardcoded Fallbacks | **S3 — Bug / Rough Edge** | `bundle.py` contains static fallback regime probabilities and alert classifications if parameters are missing. | `src/varsha/product/bundle.py:67-73, 114-120`: Default hardcoded regime tuples. |
| AUD-08 | Documentation | **S4 — Polish** | `docs/STATE.md`, `docs/SCORECARD.md`, and `docs/KNOWN_LIMITATIONS.md` are out of sync with actual implemented architecture and test results. | `docs/STATE.md` references pre-iteration baseline from 2026-09-20. |

---

## 3. Plan of Execution (Phase 1 → Phase 2 → Phase 3)

1. **Phase 1 (Fix & Finish):**
   - **Vectorize feature extractions** across `classifier.py`, `b2_gbm.py`, `b4_regime_gbm.py`, `heavy_rain.py`, reducing extraction time from 100+ seconds to <0.5 seconds.
   - **Compute real verification metrics** in `src/varsha/verify/metrics.py` and write `verification.json`, `verification_slices.json`, `reliability.json`, `controls_summary.json` directly into the product bundle.
   - **Wire `cmd_report` and `cmd_run`** to use genuinely computed evaluation metrics across B0, B1, B2, B3, B4.
   - **Remove fake fallbacks** in `src/varsha/api/app.py` and `src/varsha/product/bundle.py`.
   - **Add frontend unit/component tests** in `web/src` for Vitest.
2. **Phase 2 (UX, Responsiveness, Perf & Visual Polish):**
   - Lazy load routes in `web/src/App.tsx` to optimize bundle size below 500 kB chunk threshold.
   - Verify mobile/tablet/desktop responsive layouts (390px, 768px, 1440px).
   - Ensure explicit loading, error, and empty states.
   - Validate accessibility (focus rings, ARIA, keyboard navigation).
3. **Phase 3 (Verification & Honest Report):**
   - Run complete backend test suite (`pytest`) and frontend test suite (`vitest`, `npm run build`).
   - Run end-to-end demo generation (`demo-fast`).
   - Update `docs/STATE.md`, `docs/SCORECARD.md`, `docs/KNOWN_LIMITATIONS.md`, `README.md`.
