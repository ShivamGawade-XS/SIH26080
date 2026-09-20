# Human Signoff Required — SIH26080 Open-Source Scout

These items require a human decision before the build proceeds. Do not commit to any disputed item until cleared.

---

## H1 — SIH/MoES originality and third-party code rules

**What:** The SIH 2026 competition rules on using open-source code, AI-generated code, and third-party components were **not in the materials reviewed by this agent**. The portal says "Copyright © 2025 SIH. All rights reserved." but does not reproduce the full rules here.

**Action required:**
- Log in to the SIH portal and locate the "Rules and Regulations" or "Submission Guidelines" PDF/page.
- Check specifically: "Can participants use open-source libraries?" "Must third-party code be disclosed?" "Is AI-assisted code generation allowed?"
- Record the answer in `ORIGINALITY_STATEMENT.md`.

**Risk if ignored:** Disqualification.

---

## H2 — open-meteo API terms of use

**What:** The `open-meteo/open-meteo` server code is AGPL-3.0 and is for non-commercial use only per its README ("Free Weather Forecast API for non-commercial use"). A hackathon team using the public API as a **data source** (not distributing the server) is likely acceptable, but this must be confirmed against their API terms.

**Action required:**
- Visit [https://open-meteo.com/terms](https://open-meteo.com/terms) and confirm that the historical-forecast API may be used in a competition/research context.
- If confirmed: it can be used as a data route (not a code dependency). Add attribution.
- If not confirmed: fall back to NOAA GEFS reforecast or direct GFS archive downloads.

**Risk if ignored:** ToS violation; invalid data source.

---

## H3 — geoBoundaries India district data licence

**What:** The `wmgeolab/geoBoundaries` repo's licence is "NOASSERTION" in the GitHub API, but the project website states CC-BY 4.0 for the data. CC-BY requires attribution.

**Action required:**
- Visit [https://www.geoboundaries.org](https://www.geoboundaries.org) and confirm the exact data licence.
- If CC-BY 4.0: add attribution in the product and in `ORIGINALITY_STATEMENT.md`.
- Also compare the geoBoundaries India district boundaries against officially published Survey of India / MoES depictions (particularly for disputed territories). A government jury will notice incorrect boundary depictions.

**Risk if ignored:** Attribution missing (CC-BY violation) or map controversy in front of a MoES jury.

---

## H4 — datameet/maps boundaries for districts

**What:** `datameet/maps` has MIT licence (code) and community-sourced shapefiles. The district boundaries may not match the official Survey of India's current depiction.

**Action required:**
- Compare datameet district boundaries with an authoritative government source (e.g., the Open Government Data Platform India, [https://data.gov.in](https://data.gov.in)).
- If there are discrepancies in Jammu & Kashmir, Ladakh, or other sensitive areas, use only the authoritative source.

**Risk if ignored:** Boundary controversy, especially for a MoES government jury.

---

## H5 — Mentor / domain expert review of regime definitions

**What:** The regime labelling rules (active/break thresholds, depression detection parameters) are based on literature (Rajeevan et al. 2010, Hurley & Boos 2015). These need domain expert validation.

**Action required:**
- Consult a meteorologist (university faculty, IMD alumni, or the optional SIH mentor slot).
- Validate that the thresholds used are consistent with published IMD practice.

**Risk if ignored:** Regime definitions challenged by the jury; weak scientific foundation.
