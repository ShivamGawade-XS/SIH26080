# Verification Status Register

**Last Updated:** Phase 0 Baseline  
**Governing Rule:** N5 (No Gaming), Section 3 (Honesty about verification)

---

## Capability Verification Matrix

| Capability ID | Subsystem / Capability | Verification Status | Verified In This Session? | How to Verify (Human / Shell Command) |
|---|---|---|---|---|
| **CAP-01** | **Python Environment & Runtime** | **VERIFIED** | Yes (Python 3.14.3 / 3.13) | `python scripts/probe_env.py` |
| **CAP-02** | **Frontend Runtime (Node/pnpm)** | **VERIFIED** | Yes (Node v25.1.0, pnpm 11.24.0) | `pnpm -v && node -v` |
| **CAP-03** | **Network Reachability (NOAA/NASA/CDS)** | **VERIFIED** | Yes (NOAA S3, NASA, CDS reachable) | `python scripts/probe_env.py` |
| **CAP-04** | **Synthetic World Pipeline** | **UNVERIFIED (Pending Iter-0)** | No | `python -m varsha.cli data synth --profile demo-fast` |
| **CAP-05** | **Rule-Based Regime Labeller** | **UNVERIFIED (Pending Iter-0)** | No | `pytest tests/unit/test_regime_rules.py` |
| **CAP-06** | **Model Ladder (B0–B4)** | **UNVERIFIED (Pending Iter-1)** | No | `pytest tests/unit/test_models.py` |
| **CAP-07** | **Heavy Rain Probability & Calibration** | **UNVERIFIED (Pending Iter-1)** | No | `pytest tests/unit/test_heavy_rain.py` |
| **CAP-08** | **District Aggregation & Alerts** | **UNVERIFIED (Pending Iter-0)** | No | `pytest tests/unit/test_district_product.py` |
| **CAP-09** | **Positive & Negative Controls** | **UNVERIFIED (Pending Iter-1)** | No | `pytest tests/controls/test_controls.py` |
| **CAP-10** | **Leakage Canaries** | **UNVERIFIED (Pending Iter-1)** | No | `pytest tests/controls/test_canaries.py` |
| **CAP-11** | **FastAPI Backend Server** | **UNVERIFIED (Pending Iter-0)** | No | `pytest tests/api/test_contract.py` |
| **CAP-12** | **Web Console (Vite + React)** | **UNVERIFIED (Pending Iter-0)** | No | `pnpm --prefix web build && pnpm --prefix web test` |
| **CAP-13** | **Playwright E2E Test Suite** | **UNVERIFIED (Pending Iter-0)** | No | `npx playwright test` |
| **CAP-14** | **NOAA GFS Real Connector (Herbie)** | **UNVERIFIED (Network/Cache)** | No | `python -m varsha.cli data fetch --source gfs --lead 1 --date 2024-07-15` |
| **CAP-15** | **IMD Gridded Connector (imdlib)** | **UNVERIFIED (Network/Portal)** | No | `python -m varsha.cli data fetch --source imd --date 2024-07-15` |
| **CAP-16** | **ERA5 / Copernicus CDS Connector** | **UNVERIFIED (Credentials)** | No | Requires `~/.cdsapirc` token; `python -m varsha.cli data fetch --source era5` |
| **CAP-17** | **Boundary Fetch & Validation** | **UNVERIFIED (Pending Iter-0)** | No | `python scripts/fetch_boundaries.py` |
| **CAP-18** | **Docker Container Build** | **UNVERIFIED (No Docker in PATH)**| No | `docker build -t varsha-mvp .` (Docker daemon required on host) |
| **CAP-19** | **Lighthouse & axe-core A11y Audit**| **UNVERIFIED (Pending Iter-2)** | No | `pnpm --prefix web test:a11y` |
| **CAP-20** | **Deterministic Hash Comparison** | **UNVERIFIED (Pending Iter-0)** | No | `python scripts/verify_determinism.py` |

---

## Notes on Real-Mode Fallback & Offline Operation

- In accordance with **N1**, synthetic pipeline data is the gold standard for reproducible evaluation and CI.
- For all UNVERIFIED real connectors, mock fixtures structured according to exact schema specifications are used in test suites.
- No claim of real forecast skill will be made without explicit VERIFIED execution against real archived datasets.
