# Scout Session State

**Phase:** COMPLETE — all docs/reuse files written; pending git push.
**Date:** 2026-09-20 (IST)
**Scout:** Antigravity AI agent (ponytail/ultra mode)

## What was done

1. Created `docs/reuse/` and `spikes/` directories.
2. Ran `spikes/scout_repos.py` — queried GitHub REST API for all 44 seed repositories.
   - Results saved to `docs/reuse/seed_verification.json`.
3. Ran `spikes/search_runner.py` — 50 `gh search repos` queries across S1–S13.
   - Results saved to `docs/reuse/SEARCH_LOG.md` and `docs/reuse/detailed_search_results.json`.
4. Ran `spikes/refined_search.py` — 17 refined single-word / two-word queries.
5. Verified additional repos via direct `gh api` calls:
   - `WFRT/verif` — VERIFIED (BSD-3 equivalent custom; ★103).
   - `EFS-OpenSource/calibration-framework` (netcal) — VERIFIED (Apache-2.0; ★380).
   - `ecmwf-lab/ai-models` — VERIFIED (Apache-2.0; ★592).
   - `slerch/ppnn` — VERIFIED (MIT; ★63).
6. Verified `netcal` on PyPI — **Apache-2.0**, version 1.4.0.
7. Verified `verif` on PyPI — exists (homepage: WFRT/verif; licence in LICENSE file = BSD-3-Clause style).
8. Checked MapLibre GL JS licence — **BSD-3-Clause** (code from Mapbox v1.13 base; the repo's own additions are BSD-3).
9. Checked `ks905383/xagg` — **GPL-3.0** (flag for product use).
10. Checked `open-meteo/open-meteo` — **AGPL-3.0** (flag for product use).
11. Wrote all docs/reuse output files.

## Files produced

- `docs/reuse/STATE.md` (this file)
- `docs/reuse/ASSUMPTIONS.md`
- `docs/reuse/SEARCH_LOG.md`
- `docs/reuse/REUSE_REGISTER.md` ← main hand-off to build team
- `docs/reuse/ORIGINALITY_STATEMENT.md`
- `docs/reuse/HUMAN_SIGNOFF.md`
- `docs/reuse/seed_verification.json` (raw API data)
- `docs/reuse/detailed_search_results.json` (raw search data)
- `spikes/scout_repos.py`
- `spikes/search_runner.py`
- `spikes/refined_search.py`

## Status of subsystems

| Sub | Status |
|-----|--------|
| S1 (Forecast data access) | DONE — Herbie (MIT) ADOPT; ecmwf-opendata (Apache-2.0) ADOPT |
| S2 (India obs) | DONE — imdlib (MIT) ADOPT WITH FALLBACK |
| S3 (Reanalysis ARD) | DONE — ARCO-ERA5 (Apache-2.0) REFERENCE; earthaccess (MIT) ADOPT |
| S4 (Bias correction) | DONE — xclim sdba (Apache-2.0) CROSS-CHECK; ibicus (Apache-2.0) REFERENCE; python-cmethods GPL → REFERENCE ONLY; SBCK GPL → REFERENCE ONLY |
| S5 (ML post-processing) | DONE — slerch/ppnn (MIT) LEARN-FROM; EUPPBench (BSD-3) REFERENCE |
| S6 (Monsoon diagnostics) | DONE — MetPy (BSD-3) ADOPT; windspharm (MIT) ADOPT; TempestExtremes (BSD-2) REFERENCE |
| S7 (Verification) | DONE — nci/scores (Apache-2.0) ADOPT; xskillscore (Apache-2.0) CROSS-CHECK; pysteps.verification (BSD-3) CROSS-CHECK; WFRT/verif REFERENCE |
| S8 (Calibration) | DONE — scikit-learn (BSD-3) ADOPT; MAPIE (BSD-3) ADOPT; netcal (Apache-2.0) CROSS-CHECK |
| S9 (Geospatial) | DONE — pangeo-data/xESMF (MIT) ADOPT; xarray-regrid (Apache-2.0) ADOPT; regionmask (MIT) ADOPT; exactextract (Apache-2.0) ADOPT; xagg GPL → REFERENCE ONLY |
| S10 (Boundary data) | DONE — datameet/maps (MIT) data ADOPT with attribution; geoBoundaries REFERENCE (custom licence) |
| S11 (Web mapping) | DONE — MapLibre GL JS (BSD-3) ADOPT; D3 (ISC) ADOPT; Observable Plot (ISC) ADOPT; zarrita.js (MIT) ADOPT; deck.gl (MIT) optional |
| S12 (Prior art) | DONE — no regime-specific monsoon post-processing found publicly; closest: slerch/ppnn, EUPPBench |
| S13 (Engineering) | DONE — no framework needed at MVP scale |

## Next step

```
git add docs/reuse spikes
git commit -m "chore(scout): Prompt-0 open-source due diligence complete"
git push origin main
```
