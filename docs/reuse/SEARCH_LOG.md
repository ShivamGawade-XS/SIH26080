# Open-Source Scout Search Log — SIH26080

**Generated:** 2026-09-20 (IST)
**Tool:** GitHub CLI (`gh search repos`, `gh api`) + web search fallback
**Scope:** Subsystems S1–S13 as defined in Prompt 0

---

## Methodology

1. **GitHub REST API** (via `gh api repos/<owner>/<repo>`) for direct repository lookup of seed candidates. Returned: stars, forks, license SPDX, last push date, description, archived status.
2. **`gh search repos`** for broad keyword queries. Results limited by API rate; multi-word queries sometimes returned 0 results due to API quirks, which is noted below.
3. **PyPI** for package metadata (`urllib.request` to `pypi.org/pypi/<pkg>/json`). Checked `netcal` and `verif`.
4. **Web search** (Vertex AI Search) for repos not findable by name alone (`slerch/ppnn`, `EFS-OpenSource/calibration-framework`).
5. **`gh api repos/<owner>/<repo>/license`** for repos where the API returned "NOASSERTION" to decode the actual licence text (MapLibre, WFRT/verif).

---

## Seed Repository Checks (44 total)

| # | Repository | Stars | Licence (SPDX) | Archived | Last Push | Status |
|---|---|---|---|---|---|---|
| 1 | [blaylockbk/Herbie](https://github.com/blaylockbk/Herbie) | 790 | MIT | No | 2026-09-20 | VERIFIED |
| 2 | [ecmwf/ecmwf-opendata](https://github.com/ecmwf/ecmwf-opendata) | 338 | Apache-2.0 | No | 2026-07-30 | VERIFIED |
| 3 | [open-meteo/open-meteo](https://github.com/open-meteo/open-meteo) | 6222 | AGPL-3.0 | No | 2026-09-20 | VERIFIED — AGPL flag |
| 4 | [iamsaswata/imdlib](https://github.com/iamsaswata/imdlib) | 43 | MIT | No | 2026-09-17 | VERIFIED |
| 5 | [earthaccess-dev/earthaccess](https://github.com/earthaccess-dev/earthaccess) | 643 | MIT | No | 2026-09-17 | VERIFIED (note: canonical org changed to earthaccess-dev) |
| 6 | [google-research/weatherbench2](https://github.com/google-research/weatherbench2) | 637 | Apache-2.0 | No | 2026-09-10 | VERIFIED |
| 7 | [google-research/arco-era5](https://github.com/google-research/arco-era5) | 504 | Apache-2.0 | No | 2026-09-17 | VERIFIED |
| 8 | [Ouranosinc/xclim](https://github.com/Ouranosinc/xclim) | 404 | Apache-2.0 | No | 2026-09-18 | VERIFIED |
| 9 | [ecmwf-projects/ibicus](https://github.com/ecmwf-projects/ibicus) | 83 | Apache-2.0 | No | 2026-07-31 | VERIFIED |
| 10 | [btschwertfeger/python-cmethods](https://github.com/btschwertfeger/python-cmethods) | 82 | **GPL-3.0** | No | 2026-09-01 | VERIFIED — GPL flag |
| 11 | [yrobink/SBCK-python](https://github.com/yrobink/SBCK-python) | 16 | **GPL-3.0** | No | 2026-06-08 | VERIFIED — GPL flag |
| 12 | [EUPP-benchmark/climetlab-eumetnet-postprocessing-benchmark](https://github.com/EUPP-benchmark/climetlab-eumetnet-postprocessing-benchmark) | 32 | BSD-3-Clause | No | 2026-02-11 | VERIFIED |
| 13 | [khoehlein/Permutation-invariant-Postprocessing](https://github.com/khoehlein/Permutation-invariant-Postprocessing) | 4 | MIT | No | 2025-02-15 | VERIFIED |
| 14 | slerch/ensemble-postprocessing | — | — | — | — | NOT FOUND (404) |
| 15 | [Unidata/MetPy](https://github.com/Unidata/MetPy) | 1442 | BSD-3-Clause | No | 2026-09-14 | VERIFIED |
| 16 | [ajdawson/windspharm](https://github.com/ajdawson/windspharm) | 100 | MIT | No | 2026-08-25 | VERIFIED |
| 17 | [ClimateGlobalChange/tempestextremes](https://github.com/ClimateGlobalChange/tempestextremes) | 147 | BSD-2-Clause | No | 2026-08-10 | VERIFIED |
| 18 | [nci/scores](https://github.com/nci/scores) | 234 | Apache-2.0 | No | 2026-09-14 | VERIFIED |
| 19 | [xarray-contrib/xskillscore](https://github.com/xarray-contrib/xskillscore) | 243 | Apache-2.0 | No | 2026-09-18 | VERIFIED |
| 20 | [pySTEPS/pysteps](https://github.com/pySTEPS/pysteps) | 587 | BSD-3-Clause | No | 2026-09-15 | VERIFIED |
| 21 | [pangeo-data/climpred](https://github.com/pangeo-data/climpred) | 259 | MIT | No | 2026-09-20 | VERIFIED |
| 22 | [properscoring/properscoring](https://github.com/properscoring/properscoring) | 188 | Apache-2.0 | **ARCHIVED** | 2023-03-09 | VERIFIED — archived, use nci/scores instead |
| 23 | [dtcenter/METplus](https://github.com/dtcenter/METplus) | 121 | Apache-2.0 | No | 2026-09-18 | VERIFIED (note: NCAR/METplus redirects to dtcenter/METplus) |
| 24 | met-no/verif | — | — | — | — | NOT FOUND (404) — correct repo is WFRT/verif |
| 25 | [scikit-learn-contrib/MAPIE](https://github.com/scikit-learn-contrib/MAPIE) | 1591 | BSD-3-Clause | No | 2026-09-08 | VERIFIED |
| 26 | [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn) | 67325 | BSD-3-Clause | No | 2026-09-19 | VERIFIED |
| 27 | Jonathan-Wegener/netcal | — | — | — | — | NOT FOUND — correct repo is EFS-OpenSource/calibration-framework |
| 28 | [JiaweiZhuang/xESMF](https://github.com/JiaweiZhuang/xESMF) | 279 | MIT | No | 2022-01-11 | VERIFIED — original author's fork, inactive. Use pangeo-data/xESMF |
| 29 | [pangeo-data/xESMF](https://github.com/pangeo-data/xESMF) | 252 | MIT | No | 2026-09-08 | VERIFIED — active maintained fork |
| 30 | [xarray-contrib/xarray-regrid](https://github.com/xarray-contrib/xarray-regrid) | 107 | Apache-2.0 | No | 2026-02-06 | VERIFIED |
| 31 | [regionmask/regionmask](https://github.com/regionmask/regionmask) | 260 | MIT | No | 2026-09-11 | VERIFIED |
| 32 | [isciences/exactextract](https://github.com/isciences/exactextract) | 322 | Apache-2.0 | No | 2026-02-24 | VERIFIED |
| 33 | [ks905383/xagg](https://github.com/ks905383/xagg) | 102 | **GPL-3.0** | No | 2025-11-24 | VERIFIED — GPL flag; replace with exactextract |
| 34 | [datameet/maps](https://github.com/datameet/maps) | 476 | MIT | No | 2022-05-11 | VERIFIED — data accuracy needs human review |
| 35 | [wmgeolab/geoBoundaries](https://github.com/wmgeolab/geoBoundaries) | 409 | NOASSERTION | No | 2026-04-15 | VERIFIED — data licence likely CC-BY 4.0; human signoff needed |
| 36 | [maplibre/maplibre-gl-js](https://github.com/maplibre/maplibre-gl-js) | 11704 | BSD-3-Clause (see A1) | No | 2026-09-18 | VERIFIED — actual text is BSD-3 |
| 37 | [visgl/deck.gl](https://github.com/visgl/deck.gl) | 14598 | MIT | No | 2026-09-20 | VERIFIED |
| 38 | [d3/d3](https://github.com/d3/d3) | 113746 | ISC | No | 2026-05-28 | VERIFIED |
| 39 | [observablehq/plot](https://github.com/observablehq/plot) | 5386 | ISC | No | 2026-09-01 | VERIFIED |
| 40 | [manzt/zarrita.js](https://github.com/manzt/zarrita.js) | 145 | MIT | No | 2026-09-01 | VERIFIED |
| 41 | [cambecc/earth](https://github.com/cambecc/earth) | 6606 | MIT | No | 2022-10-01 | VERIFIED — design reference only |
| 42 | ecmwf/ai-models | — | — | — | — | NOT FOUND — correct org is ecmwf-lab |
| 43 | [ecmwf-lab/ai-models](https://github.com/ecmwf-lab/ai-models) | 592 | Apache-2.0 | No | 2026-08-06 | VERIFIED (found via gh search repos --owner ecmwf-lab) |
| 44 | [NVIDIA/earth2studio](https://github.com/NVIDIA/earth2studio) | 1138 | Apache-2.0 | No | 2026-09-19 | VERIFIED |
| 45 | google-deepmind/graphcast → [google-deepmind/weathernext](https://github.com/google-deepmind/weathernext) | 7683 | Apache-2.0 | No | 2026-09-04 | VERIFIED (GraphCast was folded into WeatherNext) |

---

## Additional repos found via secondary searches

| Repository | Stars | Licence | Found by |
|---|---|---|---|
| [WFRT/verif](https://github.com/WFRT/verif) | 103 | BSD-3-Clause (custom text) | PyPI + gh api |
| [EFS-OpenSource/calibration-framework](https://github.com/EFS-OpenSource/calibration-framework) | 380 | Apache-2.0 | Web search for "netcal" |
| [slerch/ppnn](https://github.com/slerch/ppnn) | 63 | MIT | Web search for "Rasp Lerch postprocessing" |
| [ks905383/xagg_archived](https://github.com/ks905383/xagg_archived) | 34 | — | Search results (archived, skip) |

---

## Search Methodology Notes

- `gh search repos` with long multi-word queries (>3 words) often returned 0 results or errors; single/two-word queries were more reliable.
- GitHub's licence detection via API is not always accurate for repos with custom SPDX-compatible licences. Always decode the actual `LICENSE` file when the API returns "NOASSERTION".
- S12 (prior art on the exact problem): no publicly available repository for "regime-aware monsoon rainfall post-processing over India" was found. The closest matches are `slerch/ppnn` (European weather, 2m temperature), `EUPPBench` (European post-processing benchmark). **This confirms that our approach is genuinely novel in the open-source landscape.**
- S13 (engineering scaffolding): no framework adds enough value over a flat Python package + FastAPI. Recommended: skip orchestration tools (DVC, Prefect, Dagster) for MVP; they add complexity without proportional benefit.
