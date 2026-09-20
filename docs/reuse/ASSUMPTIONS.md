# Assumptions Log — SIH26080 Open-Source Scout

**Date started:** 2026-09-20
**Agent:** Antigravity AI (ponytail/ultra mode)

---

## Assumptions made during this session

| # | Assumption | Rationale | Risk if wrong | Flag to verify |
|---|---|---|---|---|
| A1 | MapLibre GL JS is usable as BSD-3 | The `LICENSE.txt` in the repo contains the BSD-3-Clause text from the Mapbox GL JS v1.13 fork and the project's own additions, even though GitHub's API labels it "Other/NOASSERTION". The actual text is permissive. | Low — the BSD-3 text is present and clear. | Read LICENSE.txt before shipping |
| A2 | `WFRT/verif` is BSD-3 equivalent | PyPI lists no SPDX, GitHub API says "Other". The decoded LICENSE file is a standard BSD-3-Clause text authored by "Weather Forecast Research Team". | Low — text is permissive. | Retain a copy of the licence file |
| A3 | `geoBoundaries` data for India is usable | The repo licence is NOASSERTION. The project website (www.geoboundaries.org) states "CC-BY 4.0" for the data. | Medium — must confirm CC-BY before using the data | Human should verify on the website and note the required attribution |
| A4 | `datameet/maps` district data is current and authoritative | The repo has MIT code, and the Shapefiles are community-sourced. They may lag official Survey of India boundaries. | Medium — wrong boundaries in front of MoES jury is a risk | Cross-check with official India government data |
| A5 | `imdlib` still works against IMD's current portal | A 2023 GitHub issue noted that the old portal stopped working and the library was adapted. Last push: 2026-09-17, which suggests ongoing maintenance. | High — IMD portal access is a known fragile dependency | Run a live download test in Phase 0 spike |
| A6 | `open-meteo` historical API is usable even though server code is AGPL | Using the public open-meteo.com API (HTTP requests) is distinct from distributing the AGPL server code. Using their API as a data source is allowed under their terms for non-commercial/research | Medium — verify open-meteo's API terms of use before using in the product | Human signoff required (see HUMAN_SIGNOFF.md) |
| A7 | Model weights for GraphCast/GenCast/Pangu are not needed | The MVP uses GFS post-processing, not AI forecasts as inputs. AI-model weights are often CC-BY-NC restricted. | Low for MVP | Flag if team later wants AI model output as a second NWP |
| A8 | `slerch/ppnn` (Rasp & Lerch code) is MIT licensed | API confirms MIT licence. Code is reference-only for pipeline patterns. | Low | Confirm before adapting any snippets |
| A9 | `xagg` (GPL-3.0) can be replaced by `exactextract` (Apache-2.0) for area-weighted aggregation | Both do grid→polygon area-weighted aggregation. exactextract has a Python API as of v0.3+. | Low for MVP | Verify exactextract Python API covers our use case in a spike |
| A10 | No SIH-specific rules prohibit use of open-source libraries | SIH rules on this could be stricter than assumed. | Medium | See HUMAN_SIGNOFF.md item H1 |
