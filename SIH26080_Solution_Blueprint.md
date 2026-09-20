# SIH 2026 · SIH26080 — Solution Blueprint

**Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts**
Ministry of Earth Sciences (MoES) · Smart Automation · Software

> **How to use this file.** This is a planning scaffold: the full problem statement (verbatim), a detailed solution design, risks, a roadmap, and a draft of the idea-submission content. Treat it as your team's working document. Anything marked **(verify)** is something I could not confirm from a primary source. Check it before you put it in a submission or say it to a jury. Write the final submission in your own words and check the portal for any rules on AI-generated content.

---

## Table of contents

1. Problem statement (verbatim from the portal)
2. Requirements breakdown (what is literally asked)
3. Domain primer (what you need to understand first)
4. What the jury will likely care about (inference)
5. Solution overview and architecture
6. Data plan
7. Module A: Weather regime identification
8. Module B: Regime-aware rainfall correction
9. Module C: Heavy-rainfall probability
10. Module D: District-level product and dashboard
11. Module E: Verification framework
12. Code sketches (tested on synthetic data)
13. Novelty and differentiation
14. Feasibility, risks and honest limitations
15. Roadmap, team roles, finale plan
16. Tech stack and repository layout
17. Idea-submission content (draft sections and slide outline)
18. Jury Q&A prep
19. References to read
20. Verify-list, checklists, glossary

---

## 1. Problem statement (verbatim from the portal)

**Listing row (as seen on the portal):**

| PS ID | Organization | Problem Statement Title | Technology Bucket | Category | Idea Count (Max: 500) |
|---|---|---|---|---|---|
| SIH26080 | Ministry of Earth Sciences (MoES) | Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts | Smart Automation | Software | 1/500 (at the time it was viewed; this will change) |

**Detail page (copied exactly):**

```text
Problem Statement ID	SIH26080
Title	Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts
Problem Creater's Name	Sarim Moin
Problem Creater's Organization	Ministry of Earth Sciences (MoES)
Problem Creater's Department	Ministry of Education's Innovation Cell (MIC)
Description	
• Problem Statement Rainfall forecast errors over India vary with weather regimes such as active monsoon, break monsoon, monsoon lows/depressions, orographic rainfall, coastal rainfall and western disturbances. A single bias-correction method may not work equally well in all situations.The challenge is to build an AI/ML-based rainfall post-processing system that first identifies the prevailing weather regime and then applies suitable correction to the raw NWP rainfall forecast.The aim is to improve district/grid-level rainfall forecasts, especially for heavy and very heavy rainfall events.
• Expected Outcome Expected Outcome - Description:

Weather regime classifier - Classification of active, break, depression,coastal/orographic rainfall regimes Bias-corrected rainfall forecast - Improved rainfall forecast compared to raw NWP output Heavy rainfall probability - Probability of rainfall exceeding operational thresholds District-level rainfall product - User-friendly rainfall forecast table/map Verification report - Skill comparison using RMSE, ETS, CSI, POD, FAR and FSS
Youtube Link	
Technology Bucket	Smart Automation
Category	Software
Problem Statement Type	
Copyright © 2025 SIH. All rights reserved.
```

*The "Expected Outcome" text above is one run-on block on the portal. Section 2 splits it into its five parts. The split is mine, and the wording is unchanged.*

---

## 2. Requirements breakdown (what is literally asked)

### 2.1 The core task, in one sentence

Build an AI/ML system that (1) **first identifies the prevailing weather regime**, then (2) **applies a regime-appropriate correction** to raw NWP rainfall forecasts, so that (3) **district/grid-level rainfall forecasts improve, especially for heavy and very heavy events**.

### 2.2 The five required deliverables

| # | Deliverable (portal wording) | What it means concretely | Our module | Acceptance test (how we know it's done) |
|---|---|---|---|---|
| D1 | **Weather regime classifier**: classification of active, break, depression, coastal/orographic rainfall regimes | A model that, given forecast fields for a date and lead time, outputs which regime is in play (ideally with probabilities) | Module A | Confusion matrix and per-class F1 on held-out years; accuracy reported per lead time |
| D2 | **Bias-corrected rainfall forecast**: improved forecast compared to raw NWP output | Corrected daily rainfall at each grid cell, Day-1 to Day-N | Module B | Beats raw NWP *and* a regime-blind correction on held-out years, with confidence intervals |
| D3 | **Heavy rainfall probability**: probability of rainfall exceeding operational thresholds | Calibrated P(rain ≥ 64.5 / 115.6 / 204.5 mm) per cell and per district | Module C | Reliability diagram close to the diagonal; Brier skill score above the reference |
| D4 | **District-level rainfall product**: user-friendly table/map | A daily table and map by district (corrected rain, probabilities, regime, alert colour) | Module D | A non-technical viewer can read it in 30 seconds; CSV/GeoJSON downloadable |
| D5 | **Verification report**: skill comparison using RMSE, ETS, CSI, POD, FAR and FSS | A reproducible report comparing raw vs corrected, by regime, lead and threshold | Module E | Auto-generated from a script; all six named metrics present |

### 2.3 Subtle points in the wording (read these twice)

1. **"First identifies … then applies."** The regime step must be *upstream* of the correction. A single big model with no regime step does not satisfy the brief. Use the regime explicitly, as an input or a router.
2. **The problem text lists six regimes; the classifier deliverable lists four.** The text names active, break, monsoon lows/depressions, orographic, coastal, and western disturbances. D1 names only active, break, depression, and coastal/orographic. **Cover the four in D1 fully, add a "normal/other" class, and treat western disturbances as a clearly labelled extension** (see Module A).
3. **"District/grid-level."** They accept either, but a *district* product is a named deliverable (D4). Do both: model at grid level, aggregate to districts.
4. **"Especially for heavy and very heavy rainfall."** This is the score that matters most. Heavy-rain skill is where you win or lose. RMSE alone will not show it.
5. **"Operational thresholds."** Use IMD's official categories, not arbitrary numbers (Section 3.4).
6. **"AI/ML-based."** The correction must involve learning. Pure quantile mapping is a *baseline*, not the answer. You still need it as a baseline.
7. **The title says "Monsoon."** The core season is **June–September (JJAS)**. Western disturbances mostly matter outside that window (Section 7.6).

### 2.4 What is *not* asked (do not waste time on it)

- Building a new NWP model or running WRF/NCUM yourself.
- Nowcasting (0–6 h). That is a different PS (SIH26084).
- Temperature, wind, or other variables (that is closer to SIH26081).
- A mobile app. The brief says "table/map," so a web dashboard is enough.

---

## 3. Domain primer (what you need to understand first)

### 3.1 What "post-processing" is

Numerical Weather Prediction (NWP) models solve physical equations on a grid. Their rainfall output has systematic errors: too much drizzle, too little heavy rain, misplaced peaks, timing errors. **Post-processing** learns the relationship between the model's forecast and what was actually observed, then corrects future forecasts. The classic methods are:

- **Bias correction / mean adjustment:** subtract the average error.
- **Quantile mapping (QM):** map the forecast's distribution onto the observed distribution.
- **Regression / ML (e.g. gradient boosting, neural nets):** learn a richer correction from many predictors.

### 3.2 Why "regime-aware" is the idea

The model's error is **not the same in every weather situation**. During an *active* spell the model may under-forecast heavy rain over central India. During a *break* it may produce spurious rain. Over the *Western Ghats* the model's terrain is smoothed, so orographic peaks are misplaced. A single correction averages these opposite errors and fixes none of them well. The PS wants you to first identify the situation, then correct accordingly.

### 3.3 The regimes in plain language

| Regime | What it is | Typical forecast error (hypothesis to test, not a fact to assert) |
|---|---|---|
| **Active monsoon** | Spell of above-normal rainfall over the core monsoon zone (central India), strong westerlies, monsoon trough near its normal position | Heavy-rain amounts under-forecast |
| **Break monsoon** | Spell of below-normal rainfall over the core zone; the trough shifts toward the Himalayan foothills, so rain falls over the foothills and NE India | Spurious light rain in the core zone; misplaced rain near the foothills |
| **Monsoon low / depression** | A cyclonic vortex in the monsoon flow; produces large, organised rain areas, often heaviest in the south-west quadrant | Location and intensity errors |
| **Orographic** | Rain enhanced by moist air lifted over hills (Western Ghats, Meghalaya, Himalayan foothills) | Smoothed terrain leads to misplaced or under-forecast peaks |
| **Coastal** | Rain along coasts (offshore troughs, vortices, sea-breeze interaction) | Sharp coast-inland gradients poorly resolved |
| **Western disturbance (WD)** | Mid-latitude troughs moving west to east, affecting NW India (mostly Oct–May; can interact with the monsoon) | Snow/rain amount and timing errors |

*Column 3 is a hypothesis to test in your own verification, not a result to quote.*

### 3.4 IMD rainfall categories (use these as "operational thresholds")

24-hour rainfall categories, as used by the India Meteorological Department:

| Category | Rainfall in 24 h (mm) |
|---|---|
| Very light | 0.1 – 2.4 |
| Light | 2.5 – 15.5 |
| Moderate | 15.6 – 64.4 |
| **Heavy** | **64.5 – 115.5** |
| **Very heavy** | **115.6 – 204.4** |
| **Extremely heavy** | **≥ 204.5** |

IMD's colour-coded warnings are **Green** (no warning), **Yellow** (be aware), **Orange** (be prepared) and **Red** (take action). Mapping your probabilities onto these colours makes the product feel operational. **(verify the exact wording and criteria on the IMD site before quoting them.)**

### 3.5 Verification metrics in plain language

Convert forecast and observation to "event / no event" at a threshold (say ≥ 64.5 mm). Count: **H** = hits, **M** = misses, **FA** = false alarms, **CN** = correct negatives.

| Metric | Formula | Reads as | Good value |
|---|---|---|---|
| **POD** (hit rate) | H / (H + M) | Of the real events, how many did we catch? | Higher (max 1) |
| **FAR** (false-alarm ratio) | FA / (H + FA) | Of the events we forecast, how many did not happen? | Lower (min 0) |
| **CSI** (threat score) | H / (H + M + FA) | Overall hit quality, ignoring correct negatives | Higher (max 1) |
| **ETS** (equitable threat score) | (H − H_rand) / (H + M + FA − H_rand), with H_rand = (H+M)(H+FA)/N | CSI corrected for hits expected by chance | Higher (max 1); 0 = no skill |
| **FBI** (frequency bias) | (H + FA) / (H + M) | Do we over-forecast (>1) or under-forecast (<1) events? | Near 1 |
| **RMSE** | √mean((forecast − obs)²) | Typical error magnitude in mm | Lower |
| **FSS** (fractions skill score) | 1 − MSE / MSE_ref, computed on neighbourhood event *fractions* | Skill when exact location is slightly off but the area is right | Higher (max 1) |
| **Brier score / BSS** | mean((p − o)²), skill vs a reference | Quality of probability forecasts | Lower BS / higher BSS |

**Why so many metrics?** RMSE is dominated by light-rain days and hides heavy-rain failure. ETS/CSI/POD/FAR judge the *event*. FSS forgives small position errors, which is fair for rainfall. Probabilities need Brier/reliability. The PS names six of these, so your report must contain all six.

### 3.6 Practical gotchas that cause silent errors

1. **Day-boundary mismatch.** IMD's daily rainfall covers **03 UTC to 03 UTC** (08:30 IST to 08:30 IST). A "24-hour forecast from the 00 UTC run" covers 00–24 UTC. **Align the accumulation windows** (3-hourly or hourly forecast output allows this). Misalignment is a classic, invisible source of bias. **(verify the IMD convention for the specific dataset you use.)**
2. **Accumulation buckets.** GFS rainfall (APCP) is stored as accumulations over varying windows (e.g. 0–3 h, 0–6 h, 6–9 h, 6–12 h …). Difference and sum them carefully. **(verify against the GRIB index of the files you download.)**
3. **Model upgrades break stationarity.** NWP models are updated (e.g. GFS v16 went operational in 2021, **verify**). Errors learned on old versions may not hold for new ones. This limits how far back you can safely train.
4. **Autocorrelation and leakage.** Weather is correlated in space and time. Randomly splitting rows into train/test leaks information and inflates skill. **Split by year (or at least by long blocks).**
5. **Rare events.** "Extremely heavy" days are so rare that you may have only a handful of samples. Plan for that (pooling, tail models, honest uncertainty).
6. **Observation quality.** Gridded rain is an interpolation of sparse gauges (or satellite estimates), so it has its own error. Say so in the report.

---

## 4. What the jury will likely care about (inference, not official)

I don't have MoES's marking criteria, and the portal excerpt did not include a criteria table. Based on the deliverables and how such panels typically judge, expect:

1. **Did you understand the meteorology?** Do you know what a break spell is? Can you defend your regime definitions?
2. **Is the improvement real?** Held-out years, proper baselines, confidence intervals, no leakage.
3. **Does it help where it matters?** Heavy/very heavy rainfall, not just average error.
4. **Is it usable operationally?** Automated daily run, district product, clear outputs, sensible failure handling.
5. **Is it honest about limits?** Regimes it handles badly, lead times where it stops helping.
6. **Is it feasible and scalable?** Runs on modest compute; data sources are accessible; can plug in India's own models (NCMRWF/IMD) later.
7. **Presentation and demo.** A working pipeline run live beats slides.

**Check the portal for a "marking criteria" attachment or the 2026 idea-submission template and follow it exactly.** Past SIH templates typically ask for: problem understanding, proposed solution, technical approach, feasibility and viability, impact and benefits, and research/references. **(verify for 2026.)**

---

## 5. Solution overview and architecture

### 5.1 The idea in one paragraph

We ingest raw NWP forecasts (GFS as the workhorse, optionally ECMWF open data as a second source), observed rainfall (IMD gridded) and reanalysis (ERA5). A **regime module** labels historical days with objective rules, then trains a classifier that predicts the regime **from forecast-side fields only**. A **correction module** learns rainfall corrections that depend on the regime (regime-specific quantile mapping plus a gradient-boosted model with regime probabilities as inputs). A **heavy-rain module** turns forecasts into calibrated exceedance probabilities at IMD thresholds. A **product layer** aggregates to districts and serves a map, table, and API. A **verification module** produces the report, always comparing against raw NWP and a regime-blind correction, so the value of "regime-aware" is *measured* rather than assumed.

### 5.2 Architecture

```text
                 ┌──────────────────────────── OFFLINE (training) ─────────────────────────────┐
                 │                                                                              │
  ERA5 (analysis)│──► Regime labelling (rules) ──► Regime labels (historical, "truth")          │
  IMD rain (obs) │──► Obs rain fields ─────────────────────────────────┐                        │
  NWP archive    │──► Forecast fields + predictors ──► Feature store ──┼─► Train A: regime      │
  (GFS / others) │                                                     │   classifier           │
                 │                                                     └─► Train B: correction  │
                 │                                                          + Train C: heavy-   │
                 │                                                          rain probability    │
                 └──────────────────────────────────────────────────────────────────────────────┘
                                                     │ trained models + calibration
                                                     ▼
                 ┌──────────────────────────── ONLINE (daily run) ─────────────────────────────┐
  Latest NWP run │──► Fetch + crop + align windows ──► Predict regime (soft probabilities)     │
                 │                                       │                                      │
                 │                                       ▼                                      │
                 │                         Regime-aware correction (per grid cell, per lead)    │
                 │                                       │                                      │
                 │                                       ▼                                      │
                 │                         Heavy-rain probabilities (64.5 / 115.6 / 204.5 mm)   │
                 │                                       │                                      │
                 │                                       ▼                                      │
                 │                    District aggregation ──► Table · Map · CSV/GeoJSON · API  │
                 └──────────────────────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
                 Verification module (retrospective + rolling): raw vs blind-corrected vs regime-aware
```

### 5.3 Design principles

1. **Baselines first.** Raw NWP, global quantile mapping, and a global (regime-blind) ML model are built before the regime-aware model. The regime-aware model must beat these to be worth anything.
2. **Regime from forecast fields.** At prediction time the observed regime is unknown, so the classifier uses only forecast-side predictors.
3. **Soft, not hard.** Regime probabilities go into the correction step. Wrong hard labels would inject errors, so let uncertain days blend.
4. **Probabilistic outputs.** Heavy-rain products are probabilities, calibrated and verified.
5. **Reproducible pipeline.** One command re-runs everything (data to models to report).
6. **Honest reporting.** Report where it does *not* help.

### 5.4 Scope decisions (make these explicitly)

| Decision | Recommended | Why |
|---|---|---|
| Season | **JJAS (Jun–Sep)** core | The PS is about monsoon rainfall |
| Spatial resolution | **0.25° grid, India land mask (~4,000–4,500 cells)** | Matches IMD gridded rain; feasible compute |
| Lead times | **Day-1 to Day-5** core; Day-6/7 stretch | Correction value fades with lead; keeps the data manageable |
| Variable | **Daily rainfall (24 h totals)** | The named target |
| Regime scope | **Active, break, depression, orographic, coastal + "normal/other"**; WD as extension | Matches D1 |
| Model families | Quantile mapping (baseline), gradient boosting (main), optional small neural net (stretch) | Fits data volume |
| Deployment | **Batch daily run + Streamlit/FastAPI dashboard** | Fits a hackathon; extendable |

---

## 6. Data plan

> Every source below is free. **Some access details change, so run a feasibility spike** (Section 15) **before committing to any of them.**

### 6.1 Source table

| Role | Source | What you get | Access | Caveats |
|---|---|---|---|---|
| **Raw NWP (main)** | **NOAA GFS** 0.25° forecasts | Rain accumulations, PWAT, CAPE, winds, pressure, geopotential, etc. | NOAA open-data mirrors on cloud storage; NCAR RDA archive; Python helper `Herbie` **(verify current archive locations and depth)** | Model version changes over time (e.g. GFS v16 in 2021, **verify**). Rain is stored as accumulations |
| **Raw NWP (second model)** | **ECMWF Open Data (IFS, AIFS)** 0.25° | Deterministic forecasts, and AI-model forecasts | Free GRIB2; cloud mirrors; `ecmwf-opendata` and `Herbie` packages | The 0.25° IFS archive starts **Feb 2024**, so only ~2–3 monsoons; useful as a cross-check, thin for training |
| **Raw NWP (optional, long history)** | **NOAA GEFS v12 reforecast** (2000–2019) | A homogeneous multi-decade forecast set, ideal for calibration | Cloud-hosted **(verify bucket, variables, members, resolution)** | One consistent model version is a *big* advantage; confirm the fields you need exist |
| **India's own models (bonus)** | **NCMRWF NCUM / NEPS**, MoES's high-resolution system **(verify names/status)** | Indian operational forecasts | Likely restricted; may come via MoES | Don't depend on it. Design the pipeline so any gridded forecast can be plugged in, and say so |
| **Observed rain (truth)** | **IMD gridded rainfall 0.25° daily** | Long-period gauge-based daily rainfall grid over India | Free; the `imdlib` Python package downloads it **(verify latency for recent years and the terms of use)** | Interpolated from sparse gauges; check whether the current season is available |
| **Observed rain (backup / recent)** | **NASA GPM IMERG** (Late/Final) | Satellite rainfall at ~0.1° | Free NASA Earthdata login | Satellite estimates are biased in heavy orographic rain; "Final" has a multi-month delay |
| **Reanalysis (regime labels, predictors)** | **ERA5** | Hourly winds, pressure, humidity, vorticity, etc. | Free Copernicus CDS account | Reanalysis is not observation. Use it for regime labelling only |
| **Terrain and coast** | SRTM/ETOPO-type elevation; coastline | Elevation, slope, distance to coast | Free | Preprocess once |
| **Administrative boundaries** | District shapefile (Survey of India-consistent) | District polygons | Use an authoritative, government-consistent source | **Map-boundary sensitivity:** use official boundaries so the map is not wrong or contentious in front of a government jury |
| **Low-pressure-system tracks** | IMD/IITM records; reanalysis-based catalogues | Depression/low tracks | **(verify availability)** | Or detect them yourself from ERA5 (Module A) |

### 6.2 Recommended data strategy (tiers)

- **Tier 1 (must have):** GFS forecasts + IMD observed rain + ERA5. Train on the most recent model-consistent period, test on held-out years, and run a **pseudo-prospective test on the 2026 monsoon** that just ended. That is a genuine out-of-sample season. If IMD's gridded data for 2026 is not yet released, use IMERG as the observation and *say so*.
- **Tier 2 (should have):** ECMWF open-data IFS/AIFS as a second NWP source for a cross-model test ("does the method generalise beyond one model?"). It is short-history, so use it for testing more than training.
- **Tier 3 (nice to have):** GEFS v12 reforecast for a long, homogeneous training period, *if* the fields and access work out.
- **Tier 4 (pitch only):** "Plug-in ready" for NCMRWF/NCUM/IMD models.

### 6.3 Volume and compute (order-of-magnitude estimates)

- Grid: 0.25° over India gives about 4,000–4,500 land cells.
- One monsoon season: ~122 days. Five seasons is ~610 days.
- Rows per lead time for 5 seasons: about 610 × 4,300 ≈ **2.6 million**. For 5 lead times, about **13 million rows**. Gradient boosting on this fits a laptop/Colab if you use float32 and sensible features.
- Downloading: fetch only the GRIB fields you need (byte-range subsetting) and crop to India immediately. This turns hundreds of GB into single-digit GB.
- Store as **Zarr/NetCDF** (grids) and **Parquet** (training tables).

### 6.4 Alignment checklist (do this before modelling)

- [ ] Same grid for forecast and observation (regrid the forecast to the IMD 0.25° grid; use conservative regridding for rainfall).
- [ ] Same accumulation window (IMD day ≈ 03 UTC to 03 UTC; **verify**).
- [ ] Same India land mask everywhere.
- [ ] Unit check (mm/day, no kg/m² surprises: 1 kg/m² = 1 mm).
- [ ] Missing-data handling documented (missing forecast runs, missing obs days).
- [ ] Forecast valid-time vs init-time bookkeeping (a leak-prone spot).

---

## 7. Module A: Weather regime identification

This is the part MoES will scrutinise most. Get the definitions right and defensible.

### 7.1 The key design insight: two kinds of regime

The PS lumps together things that are different in nature:

| Type | Regimes | Varies in | How to represent |
|---|---|---|---|
| **Synoptic (weather-state) regimes** | Active, break, depression/low, (WD) | **Time** (which days) | A per-day label, possibly per sub-region, from large-scale fields |
| **Geographic regimes** | Orographic, coastal | **Space** (which places) | Static zone masks, modulated by flow (e.g. upslope wind) |

A grid cell on a given day therefore has a **compound key**: (synoptic regime, geographic zone). A cell on the Western Ghats during an active spell is not the same as an inland central-India cell during an active spell. This two-layer scheme matches the physics *and* neatly reconciles the "four vs six regimes" wording issue.

### 7.2 Objective labelling rules (the "ground truth" for training the classifier)

Use **ERA5 and observed rain** to label *historical* days. Rule-based labels are transparent and defensible. Start from the literature and adapt.

**Active / break spells**
- Compute a **standardised daily rainfall anomaly over the core monsoon zone (CMZ)** in central India from observed rain.
- The classic approach (Rajeevan et al., 2010) labels **active** when the normalised anomaly is at least about **+1** and **break** when it is at most about **−1**, for **3 or more consecutive days**, plus supporting circulation criteria (monsoon-trough position and 850 hPa flow). **(verify the exact thresholds, the CMZ boundary, and the circulation conditions in the paper before citing them.)**
- Days that satisfy neither are **"normal/transition."**

**Monsoon lows / depressions**
- Detect from ERA5 by tracking **850 hPa relative vorticity maxima plus sea-level-pressure minima** over the monsoon domain, in the spirit of low-pressure-system catalogues (Hurley and Boos, 2015 **(verify)**). Cross-check with IMD-declared depressions/deep depressions where available. IMD's classes are tied to wind speed: depression roughly 17–27 knots, deep depression 28–33 knots **(verify)**.
- Label days (and a spatial neighbourhood) as "depression/low active."

**Orographic**
- Static zones: Western Ghats windward slopes, Meghalaya/NE hills, Himalayan foothills (from elevation and slope).
- Dynamic modulation: an **upslope-flow index** = 850 hPa wind component pointing up the terrain gradient × moisture (e.g. PWAT). High index means orographic regime is "on."

**Coastal**
- Static zone: land cells within a set distance of the coast (start with ~50–100 km; tune it).
- Dynamic: offshore trough/vortex or strong onshore flow indicators.

**Normal / other**
- Everything that doesn't match. This class is essential. Without it, the classifier is forced to invent a regime for ordinary days.

### 7.3 The forecast-side classifier (this is the part many teams get wrong)

**At forecast time you do not have ERA5-observed regimes. You only have the forecast.** So:

- **Train** the classifier to predict the *historical rule-based label* from **forecast-side fields at the same valid time and lead**.
- **Predictors** (engineer physically meaningful domain-scale features):
  - Core-zone mean forecast rainfall and its anomaly vs climatology
  - 850 hPa wind: monsoon low-level jet strength, zonal wind over the peninsula
  - Monsoon-trough latitude proxy (e.g. pressure/height gradient, vorticity axis)
  - Max 850 hPa vorticity and min sea-level pressure in the monsoon domain (low/depression signature)
  - PWAT, CAPE (moisture and instability)
  - 500 hPa geopotential height (large-scale pattern)
  - Upslope-flow index over the Ghats/NE hills
  - Lead time and day-of-year
- **Model:** start with **gradient-boosted trees** (multiclass). A small CNN on domain-scale fields is a stretch goal, not a starting point.
- **Output:** **class probabilities** (soft regime membership), not just the argmax.
- **Evaluate:** confusion matrix, per-class precision/recall/F1, and **accuracy vs lead time**. Expect degradation at longer leads. That is normal and worth showing.

### 7.4 Optional cross-check: unsupervised weather typing

Cluster large-scale circulation fields (k-means or a self-organising map) to find recurring patterns, then compare the clusters with the rule-based regimes. Agreement strengthens your defence. Disagreement is informative. It is optional and only worth doing if time allows.

### 7.5 Class imbalance

Depressions and strong orographic events are rare relative to "normal." Use class weights or resampling, report per-class metrics, and **do not quote overall accuracy alone**. A model that always says "normal" can still have high accuracy.

### 7.6 Western disturbances (extension)

- WDs matter mostly **October–May** and over NW India. In JJAS, they matter mainly through interaction with the monsoon.
- If you add them, extend the data window beyond JJAS, define WD days from upper-level trough tracking (500/300 hPa) or potential-vorticity features, and label the module clearly as an **extension**.
- **Recommendation:** put WD in the "roadmap" slide and cover it only if the core is done. It is named in the problem text, so acknowledge it explicitly.

### 7.7 Honest limits of this module

- Regime labels come from *rules*, and rules are debatable. Document every threshold and test sensitivity (e.g. ±0.25 on the anomaly threshold).
- Regime forecast skill drops with lead time. The design (soft probabilities) is meant to absorb that.
- Regimes overlap in reality (a depression over the Ghats is also orographic). The compound-key scheme handles some of it. Say where it doesn't.

---

## 8. Module B: Regime-aware rainfall correction

### 8.1 The model ladder (this is your experiment design)

Build these in order. The gaps between rungs *are* your results.

| Rung | Name | Description | Purpose |
|---|---|---|---|
| **B0** | Raw NWP | Uncorrected forecast | The thing to beat |
| **B1** | Global quantile mapping | One empirical CDF-matching per grid cell (or per subregion) and lead, no regime | The standard baseline |
| **B2** | Global ML | Gradient boosting on the same predictors, **no regime information** | Isolates "ML helps" from "regime helps" |
| **B3** | Regime-wise quantile mapping | B1 fitted separately per regime | Simple, transparent regime-aware method |
| **B4** | **Regime-aware ML (main)** | Gradient boosting with regime probabilities (and zone keys) as features, or a mixture of regime-specific experts weighted by regime probabilities | The proposed system |

**The headline claim you can make is B4 vs B2 (and vs B1).** B4 vs B0 alone proves nothing about regimes, because B2 might already deliver most of the gain. A jury that knows the field will ask for this comparison, so run it first.

### 8.2 Predictors (features) for B2/B4

- **Raw forecast rain:** at the cell, plus 3×3 and 5×5 neighbourhood mean/max (to absorb small position errors).
- **Forecast rain percentile vs local climatology** (an "anomaly" feature).
- **Physical predictors:** PWAT, CAPE, 850 hPa wind components, moisture-flux convergence, vertical velocity (e.g. 500 hPa omega), sea-level pressure anomaly.
- **Tendency/persistence:** rain forecast at neighbouring lead steps; previous-day forecast error is *not* available at forecast time unless you have the previous day's observation. If you use it, make sure it's truly available operationally.
- **Static:** latitude, longitude, elevation, slope, distance to coast, orographic roughness, zone ID.
- **Time:** lead time, day-of-year.
- **Regime:** the classifier's **probabilities** (from Module A), not the hard label.

### 8.3 Model structure for rain: a two-stage (hurdle) approach

Rainfall is zero-inflated and heavy-tailed. Model it in stages:

1. **Occurrence:** P(rain ≥ small threshold, e.g. 2.5 mm) via a classifier.
2. **Amount given rain:** a regressor. Use a log or power transform, and/or **quantile regression** (median plus upper quantiles such as 75th/90th/95th) to keep the tail.
3. **Combine:** expected value or median for the "corrected forecast," and upper quantiles for uncertainty bands.

Variant: correct with QM first, then fit a **residual ML model** on top. It is stable when data is limited.

### 8.4 Fixing the heavy tail (where most methods fail)

- Plain quantile mapping clips at the top of the training range and cannot produce values beyond it. Fit a **generalised Pareto distribution (GPD) tail** above a high threshold (say the 95th percentile) for extrapolation **(verify the approach on your data)**.
- Use **sample weights** or dedicated heavy-rain models so the loss is not dominated by the many light-rain days.
- Verify **frequency bias** at heavy thresholds. Raw models often under-forecast heavy events, and naive correction can over-correct into many false alarms. Report the POD/FAR trade-off honestly.

### 8.5 Training and validation protocol (non-negotiable)

- **Split by monsoon season (year).** Use **leave-one-year-out cross-validation** across the training seasons. Keep the **final test seasons untouched** until the end, including the 2026 pseudo-prospective season.
- **Never tune on the test years.** Tune hyperparameters inside cross-validation.
- **One model per lead time**, or lead time as a feature. Compare both.
- **Handle model-version breaks** (Section 3.6). If you train across versions, add a version flag or restrict to the consistent period.
- Report **uncertainty**: block-bootstrap confidence intervals (resample by week or season, not by row).

### 8.6 Explainability (cheap, jury-friendly)

- Feature importance and SHAP for the main model. It is nice to show, for a single district, *why* the correction changed the forecast.
- Show the **learned correction pattern per regime** (for example the average correction map during active spells vs breaks). If it looks physically sensible, that supports the whole concept. If the maps are identical across regimes, that's a warning that regime-awareness isn't adding much. Say so.

### 8.7 Optional stretch goals (only after everything above works)

- A small neural net or U-Net on gridded fields (only if the data volume supports it).
- Multi-model blending of GFS and ECMWF corrections (edges into SIH26081's territory).
- Ensemble-based post-processing if ensemble members are available.
- Extend to lead Day-6/7.

---

## 9. Module C: Heavy-rainfall probability

### 9.1 Targets

Exceedance probabilities at IMD's categories:

- P(rain ≥ **64.5 mm**) (heavy)
- P(rain ≥ **115.6 mm**) (very heavy)
- P(rain ≥ **204.5 mm**) (extremely heavy). This will be very rare, so treat it as a stretch or pool over regions.

### 9.2 Method options

1. **Direct classification** per threshold, with a gradient-boosted classifier using the same predictors (including regime probabilities).
2. **Derived from quantile predictions.** Estimate the predictive distribution from the quantile models (Section 8.3) and read off exceedances.
3. **Hybrid:** classification for 64.5 mm, and an extreme-value tail approach for 115.6/204.5 mm where samples are scarce.

### 9.3 Making probabilities trustworthy

- **Calibrate** with isotonic regression or Platt scaling, fitted on held-out data.
- **Enforce consistency:** P(≥204.5) ≤ P(≥115.6) ≤ P(≥64.5). Apply a simple monotone fix (see the code sketch).
- **Verify with:** reliability diagrams, Brier score and Brier skill score (reference: climatology), ROC/AUC, and precision-recall curves (better for rare events).
- **Operating points:** show a probability-to-alert mapping, for example "issue Orange if P(≥64.5 mm) ≥ x." Choose x with a stated POD/FAR trade-off. Do not present the number as an official IMD rule.

### 9.4 Spatial meaning (be explicit)

Two district-level definitions are worth offering because warning practice concerns "somewhere in the district":

- **P(district-mean rain ≥ T)**, and
- **P(at least one cell in the district ≥ T)** or the **fraction of district area** expected to exceed T.

Say clearly which you use in each table column.

---

## 10. Module D: District-level product and dashboard

### 10.1 Aggregation

Grid to district using area-weighted statistics from the district polygons: mean, max, and area-fraction above thresholds. Document the method. Mention that district boundary files must be authoritative.

### 10.2 The daily product (table)

| Column | Meaning |
|---|---|
| District, State | Identifier |
| Lead (Day-1…Day-5) | Forecast horizon |
| Raw NWP rain (mm) | Uncorrected district mean |
| **Corrected rain (mm)** | Regime-aware forecast |
| Uncertainty band (P10–P90) | From quantile models |
| P(≥64.5 mm), P(≥115.6 mm) | Calibrated probabilities |
| Dominant regime (and confidence) | From Module A |
| Alert colour (Green/Yellow/Orange/Red) | From probability rules (state your rule) |
| Skill note | For example "regime forecast confidence: low" |

### 10.3 Dashboard screens

1. **Map view:** layer toggle (raw / corrected / difference / probability), lead-time slider, district hover.
2. **Regime panel:** today's regime probabilities and a short plain-language explanation.
3. **District drill-down:** Day-1 to Day-5 bars (raw vs corrected), probability gauges, "why did it change?" (SHAP).
4. **Verification tab:** interactive skill charts (by regime, lead, threshold), with the raw vs blind vs regime-aware comparison.
5. **Data and model info:** what data was used, when it was last run, and known limits.
6. **Downloads:** CSV/GeoJSON and an API endpoint.

### 10.4 Operational features (this is what "Smart Automation" hints at)

- **One scheduled job** that fetches the latest NWP run, runs the pipeline, updates outputs, and logs.
- **Graceful failure:** if the latest run is missing, use the previous run and flag it on the dashboard.
- **Versioning:** stamp every product with model version, data version, and run time.
- **Basic monitoring:** rolling verification once observations arrive (e.g. weekly skill vs raw).

### 10.5 UX principles

Show **plain language** first ("Very heavy rain likely in these districts on Day-2"), then numbers. Use colour consistently with IMD's scheme. Always show raw vs corrected so users see what the system changed.

---

## 11. Module E: Verification framework

### 11.1 What to compute (all six named metrics, plus proper extras)

- **Continuous:** RMSE, MAE, mean bias, correlation.
- **Categorical (per threshold):** POD, FAR, CSI, ETS, frequency bias.
- **Neighbourhood:** **FSS** at several thresholds and neighbourhood sizes.
- **Probabilistic:** Brier score, BSS, reliability diagram, ROC, PR curve.

### 11.2 Thresholds and neighbourhoods

- Thresholds (mm/day): **2.5, 15.6, 35.5 (optional), 64.5, 115.6** (204.5 if the sample size allows).
- FSS neighbourhoods: e.g. 1, 3, 5, 9 grid cells (≈ 0.25° to 2.25°). Report where the skill becomes "useful" as the scale increases.

### 11.3 The slices (this is where the regime story is proven)

1. **Overall** (all days, all cells)
2. **By regime** (active, break, depression, orographic, coastal, normal)
3. **By lead time** (Day-1 to Day-5)
4. **By threshold** (light to very heavy)
5. **By region** (IMD's four homogeneous regions or the 36 meteorological subdivisions **(verify)**)
6. **By month** (June/July/Aug/Sep)

### 11.4 Rigor requirements

- **Held-out years only** (plus the 2026 pseudo-prospective season).
- **Same observation, mask and windows for all rungs** of the model ladder.
- **Confidence intervals** by block bootstrap (resample days/weeks). Weather is autocorrelated, so row-wise bootstrap understates uncertainty.
- **Significance:** state whether differences between rungs are statistically distinguishable, not only whether the mean is higher.
- **Report negatives:** where regime-aware is not better, say so.

### 11.5 The report itself

Auto-generate from a script (Jupyter/Quarto to HTML/PDF), containing:

1. Data and method summary (with the alignment choices)
2. Regime classifier results (confusion matrix, per-class F1, vs lead)
3. Skill tables: B0 to B4 across metrics, thresholds, leads
4. Regime-wise breakdown and the "where it helps / doesn't" summary
5. Probability verification (reliability, BSS)
6. Case studies: 2–3 real heavy-rain events (raw vs corrected vs observed maps)
7. Limitations and next steps

### 11.6 What to claim, and what not to

- Do **not** promise a percentage improvement in advance. Improvements from post-processing are often modest, and heavy-rain gains are hard-won.
- **A defensible pitch:** "consistent, statistically supported gains at heavy thresholds in specific regimes, with honest limits elsewhere," backed by a reproducible report.
- Never present numbers you did not compute yourselves.

---

## 12. Code sketches (tested on synthetic data)

*These are starting points, not production code. The metric and quantile-mapping functions were run on synthetic data to check they behave: a perfect forecast scores POD/CSI/ETS/FSS = 1, and quantile mapping raised frequency bias from about 0.69 to 1.0 on the synthetic case. Test everything on your real data.*

### 12.1 Categorical metrics (POD, FAR, CSI, ETS, FBI)

```python
import numpy as np

def contingency(obs, fc, thr):
    o, f = obs >= thr, fc >= thr
    hits   = np.sum(o & f)
    misses = np.sum(o & ~f)
    fa     = np.sum(~o & f)
    cn     = np.sum(~o & ~f)
    return hits, misses, fa, cn

def cat_scores(h, m, fa, cn):
    n = h + m + fa + cn
    pod = h / (h + m) if (h + m) else np.nan
    far = fa / (h + fa) if (h + fa) else np.nan
    csi = h / (h + m + fa) if (h + m + fa) else np.nan
    fbi = (h + fa) / (h + m) if (h + m) else np.nan
    h_rand = (h + m) * (h + fa) / n
    den = h + m + fa - h_rand
    ets = (h - h_rand) / den if den > 0 else np.nan
    return dict(POD=pod, FAR=far, CSI=csi, ETS=ets, FBI=fbi)
```

### 12.2 Fractions Skill Score (FSS)

```python
from scipy.ndimage import uniform_filter

def fss(obs2d, fc2d, thr, window):
    """obs2d, fc2d: 2-D rain fields (one day). window: neighbourhood size in grid cells."""
    o = (obs2d >= thr).astype(float)
    f = (fc2d >= thr).astype(float)
    of = uniform_filter(o, size=window, mode="constant")
    ff = uniform_filter(f, size=window, mode="constant")
    mse = np.mean((ff - of) ** 2)
    ref = np.mean(ff ** 2) + np.mean(of ** 2)
    return 1 - mse / ref if ref > 0 else np.nan
```

### 12.3 Empirical quantile mapping (baseline B1, and B3 when fitted per regime)

```python
def fit_qm(fc_train, obs_train, n_q=100):
    q = np.linspace(0, 1, n_q + 1)
    return np.quantile(fc_train, q), np.quantile(obs_train, q)

def apply_qm(fc, fq, oq):
    # np.interp clamps beyond the training range: add a GPD tail for extremes (Section 8.4)
    return np.interp(fc, fq, oq)

# B3: fit one (fq, oq) pair per regime (and per lead / zone), then route each sample
# to the mapping of its most probable regime, or blend the mappings by regime probability.
```

### 12.4 Keeping heavy-rain probabilities consistent

```python
# columns: P(>=64.5), P(>=115.6), P(>=204.5). A higher threshold can never be more likely.
p_fixed = np.minimum.accumulate(p, axis=1)
```

### 12.5 Leave-one-year-out training skeleton (LightGBM)

```python
import lightgbm as lgb

years = sorted(df["year"].unique())
for test_year in years:
    tr, te = df[df.year != test_year], df[df.year == test_year]
    X_tr, X_te = tr[FEATURES], te[FEATURES]
    # stage 1: occurrence (P(rain >= 2.5 mm))
    occ = lgb.LGBMClassifier(n_estimators=400, learning_rate=0.05)
    occ.fit(X_tr, tr.obs >= 2.5)
    # stage 2: amount given rain, log-transformed target, several quantiles
    wet = tr.obs >= 2.5
    models = {}
    for a in (0.5, 0.75, 0.9, 0.95):
        m = lgb.LGBMRegressor(objective="quantile", alpha=a, n_estimators=400, learning_rate=0.05)
        m.fit(X_tr[wet], np.log1p(tr.obs[wet]))
        models[a] = m
    # ... predict on te, invert the transform, score with Section 11 metrics, store per fold
```

### 12.6 Data-access snippets (verify current APIs before use)

```python
# GFS via Herbie (subset by GRIB index to avoid huge downloads)
from herbie import Herbie
H = Herbie("2025-07-15 00:00", model="gfs", product="pgrb2.0p25", fxx=24)
# ds = H.xarray("APCP")   # then crop to India and difference accumulation buckets

# ECMWF open data
from ecmwf.opendata import Client
Client().retrieve(step=24, type="fc", param="tp", target="ifs_tp_24h.grib2")

# IMD gridded rainfall
import imdlib as imd
data = imd.open_data("rain", 2021, 2025, "yearwise")
ds = data.get_xarray()
```

---

## 13. Novelty and differentiation

**Assume other teams will also build "a regime classifier plus XGBoost."** With 500 idea slots per PS, expect overlap. Where you can genuinely stand out:

1. **Two-layer regime scheme** (synoptic state × geographic zone) that matches the physics, instead of one flat list of labels.
2. **Objective, documented regime labels** with a sensitivity analysis, rather than hand-waved categories.
3. **Forecast-side regime classifier**, which is operationally honest. Many prototypes quietly use observed regimes that don't exist at forecast time.
4. **A proper model ladder (B0 to B4)** that isolates the value of regimes, rather than only comparing to raw NWP.
5. **Soft regime blending**, which is robust when the regime forecast is uncertain.
6. **Calibrated heavy-rain probabilities** with reliability diagrams and a consistent threshold hierarchy.
7. **Tail handling** (extreme-value tail), which targets the PS's "heavy and very heavy" emphasis directly.
8. **Model-agnostic pipeline**, demonstrated on GFS and a second model (ECMWF open data), and ready for NCMRWF/IMD models.
9. **Operational product**: an automated daily run, versioned outputs, graceful failures, plain-language district alerts.
10. **Pseudo-prospective test on the 2026 monsoon**, a real out-of-sample season.

*Do not claim "first" or "novel" in absolute terms.* Post-processing is a mature research field. Frame the novelty as "a regime-aware, verified, operations-ready implementation tailored to Indian monsoon regimes."

---

## 14. Feasibility, risks and honest limitations

### 14.1 Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Regime-aware model gains over regime-blind ML are small | **High** | High | Design the pitch around honest, measured gains and per-regime results; still valuable if some regimes clearly benefit |
| 2 | Heavy-rain samples too few, so results are noisy | High | High | Pool across space and lead, use tail models, report confidence intervals, don't over-interpret 204.5 mm |
| 3 | Data access/latency issues (IMD current-season data, archive depth) | Medium | High | Feasibility spike first; IMERG backup; cache everything locally |
| 4 | Window/accumulation misalignment causes fake bias | Medium | High | Alignment checklist (Section 6.4); test with a known case |
| 5 | Leakage inflates results | Medium | Very high | Year-based splits, review init/valid-time bookkeeping, second person audits |
| 6 | Model-version breaks (NWP upgrades) | Medium | Medium | Train on a consistent period or add a version flag; state it |
| 7 | Regime labels challenged as arbitrary | Medium | Medium | Cite literature, document thresholds, sensitivity analysis, meteorologist mentor |
| 8 | Compute/time overrun (GRIB handling is slow) | High | Medium | Subset GRIB fields, crop early, cache Zarr/Parquet, 0.25° only |
| 9 | Team lacks meteorology knowledge | High | High | Use the optional mentor slot; reach out to IMD/NIO/IITM contacts or a meteorology faculty |
| 10 | Demo fails live | Medium | High | Pre-cached data, offline fallback, recorded backup video |
| 11 | Overclaiming ("operational-ready") | Medium | High | Say "prototype validated retrospectively and on the 2026 season" |
| 12 | Map/boundary controversy | Low | Medium | Use authoritative government-consistent boundaries |
| 13 | Another team does the same thing, better presented | Medium | Medium | Differentiators in Section 13 plus a live pipeline demo |

### 14.2 Brutally honest limitations to state upfront

- Post-processing corrects *systematic* error. It cannot fix a forecast whose weather system is simply wrong.
- Skill gains usually shrink with lead time. Day-1 to Day-3 will benefit most.
- Extremely heavy events (≥ 204.5 mm) are too rare to verify reliably in a few seasons.
- Gridded observations are themselves uncertain, especially for heavy orographic rain.
- Regime definitions are conventions, not laws of nature.
- A hackathon prototype is not an operational system. Say what it would take (data-sharing, testing over more seasons, integration with MoES/IMD systems).

### 14.3 Why this is still a good pick

The PS is scoped: one variable, one clear pipeline, a standard verification toolkit, and free data. A focused team can produce a **working end-to-end system with real, honest numbers**, and that is what wins.

---

## 15. Roadmap, team roles, finale plan

> **SIH's exact dates and rounds for 2026 are not in the materials I saw. Check the portal and adjust.** The plan below is relative. In a typical SIH software flow, the idea submission comes first and shortlisted teams go on to a longer build/finale round. **(verify)**

### 15.1 Phase 0: Feasibility spike (do this *before* submitting; 2–4 days of effort)

Goal: replace assumptions with facts, and get one real baseline number for the submission.

- [ ] Confirm you can download **GFS** for one monsoon month (subsetted fields, cropped to India).
- [ ] Confirm you can load **IMD gridded rain** for the same period (and check the 2026 availability).
- [ ] Regrid, align the accumulation window, and mask to India.
- [ ] Compute **raw NWP skill** (RMSE, POD/FAR/CSI/ETS at 64.5 mm, FSS) for that month.
- [ ] Fit a **simple quantile mapping** on part of the data and test on the rest. Record the change.
- [ ] Try a crude regime label (active/break from rainfall anomaly) and look at the raw error by label.
- [ ] Record: data sizes, time per step, surprises.

**Output:** one slide/figure: "Raw NWP vs simple correction on [period]," plus a data-feasibility note. This makes the submission credible.

### 15.2 Phase 1: Idea submission

- Fill the portal template using the draft content in Section 17, in your own words.
- Include the architecture diagram, the model ladder, the verification plan, and your Phase-0 evidence.
- Name a mentor if you can (the field is optional but useful here).

### 15.3 Phase 2: Build (if shortlisted)

| Stage | Deliverable | Notes |
|---|---|---|
| 2.1 Data pipeline | Reproducible download, alignment, feature store | Automate and cache; write tests for the window alignment |
| 2.2 Regime labelling | Rule-based labels for all seasons, with a sensitivity check | Meteorologist review |
| 2.3 Baselines | B0, B1, B2 with cross-validated scores | Complete the baselines *before* regimes |
| 2.4 Regime classifier | Forecast-side classifier with metrics by lead | Report per-class F1 |
| 2.5 Regime-aware correction | B3 and B4 | Compare against B2 and B1 |
| 2.6 Heavy-rain probability | Calibrated probabilities and reliability plots | Enforce threshold consistency |
| 2.7 District product | Aggregation, table, map, CSV/GeoJSON | Use official boundaries |
| 2.8 Dashboard and daily job | Streamlit/FastAPI app and scheduler | Add versioning and fallbacks |
| 2.9 Verification report | Auto-generated HTML/PDF | Includes the 2026 season test |
| 2.10 Demo hardening | Cached data, backup video, rehearsal | Practise 3 times |

### 15.4 Suggested team roles (adapt to your team size)

| Role | Owns | Skills to look for |
|---|---|---|
| **Team lead / integration** | Architecture, timeline, pipeline glue, final demo | Python, systems thinking |
| **Data engineer** | GRIB/NetCDF handling, regridding, feature store, daily job | `xarray`, `cfgrib`, Zarr/Parquet |
| **ML engineer** | Classifier, correction models, calibration | LightGBM/XGBoost, scikit-learn |
| **Meteorology/verification lead** | Regime definitions, metrics, report, mentor contact | Reads papers, stats-minded |
| **Frontend/dashboard** | Map, tables, UX, API | Streamlit or React + MapLibre/Leaflet |
| **Documentation/presentation** | Slides, storyline, Q&A prep, demo script | Clear writing, speaking |

If someone has no meteorology background, pair them with the verification lead early. A **meteorology mentor is your biggest single risk reducer.**

### 15.5 Grand-finale plan (if it's a timed, live round)

- **Pre-cache** the data and pre-train the models. Do not plan to download or train during the finale window.
- **Live demo path:** run the pipeline on the *latest* available forecast, then open the dashboard. Have a saved fallback ready.
- **Story arc (5–7 minutes):** Problem → Why regimes → Data and method → Model ladder results → Heavy-rain skill → Live district product → Limits and roadmap.
- **Backup:** a recorded run-through video and a static export of the results.

---

## 16. Tech stack and repository layout

### 16.1 Stack

| Layer | Suggested tools |
|---|---|
| Language | Python 3.11+ |
| Grids and files | `xarray`, `cfgrib`/`eccodes`, `netCDF4`, `zarr`, `dask` |
| Data access | `Herbie`, `ecmwf-opendata`, `imdlib`, `cdsapi`, `earthaccess` (NASA) **(verify current versions)** |
| Regridding | `xESMF` or `xarray` interpolation (conservative for rain) |
| Geospatial | `geopandas`, `rasterio`, `regionmask`, `shapely` |
| ML | `scikit-learn`, `LightGBM` or `XGBoost`, `SHAP`, optional `PyTorch` |
| Verification | `numpy`, `scipy`, `properscoring` or your own functions, `matplotlib`/`plotly` |
| Backend/API | `FastAPI` |
| Dashboard | `Streamlit` (fastest) or React + MapLibre/Leaflet |
| Orchestration | `cron`, GitHub Actions, or a simple scheduler; `Makefile` or `dvc` for reproducibility |
| Reporting | Jupyter/Quarto to HTML/PDF |
| Environment | `conda`/`uv`, Docker for the demo machine |

### 16.2 Repository layout

```text
sih26080-regime-rain/
├── README.md
├── environment.yml / pyproject.toml
├── Makefile                      # make data | make train | make report | make run
├── configs/
│   ├── data.yaml                 # sources, domain, dates, windows
│   ├── regimes.yaml              # every threshold, documented
│   └── models.yaml
├── src/
│   ├── data/                     # download, crop, regrid, align, mask
│   ├── regimes/                  # labelling rules + forecast-side classifier
│   ├── features/                 # predictors, static fields
│   ├── models/                   # qm.py, gbm.py, heavy_rain.py, calibration.py
│   ├── verify/                   # metrics.py, slices.py, bootstrap.py
│   ├── product/                  # district aggregation, alert rules
│   └── app/                      # FastAPI + dashboard
├── notebooks/                    # exploration and the report
├── tests/                        # alignment, leakage, metrics tests
├── data/                         # (gitignored) raw/ interim/ processed/
└── reports/                      # generated verification reports
```

**Tests worth writing:** metric correctness (perfect forecast scores 1), window alignment on a known day, no train/test year overlap, monotone probabilities.

---

## 17. Idea-submission content (draft sections and slide outline)

> These are **scaffolds in bullet form** so you can write your own version. Fill the blanks with your Phase-0 numbers, and rewrite the text in your own words.

### 17.1 Title

*Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts: a verified, district-level heavy-rain guidance system.* (Adapt as you like.)

### 17.2 Problem understanding

- NWP rainfall over India has systematic errors that differ by situation: active vs break spells, depressions, orography, coast.
- A single correction averages opposing errors, so heavy-rain events are the most affected.
- Heavy and very heavy rain drives floods, landslides and urban flooding, so improving it has direct public-safety value.
- Gap: post-processing that is explicitly regime-aware and verified at the district level.

### 17.3 Proposed solution

- A pipeline that (1) identifies the prevailing regime from forecast fields, (2) applies regime-appropriate correction, (3) issues calibrated heavy-rain probabilities, (4) publishes a district product, and (5) auto-generates a verification report.
- Two-layer regime scheme: synoptic state × geographic zone.
- Model ladder to prove the value of regimes.

### 17.4 Technical approach

- Data: GFS (and ECMWF open data as a second model), IMD gridded rainfall, ERA5.
- Regimes: objective rules → forecast-side classifier with soft probabilities.
- Correction: regime-wise quantile mapping + gradient boosting (two-stage rainfall model, quantile outputs, extreme-value tail).
- Probabilities: calibrated exceedance at IMD thresholds, threshold-consistent.
- Verification: RMSE, ETS, CSI, POD, FAR, FSS (+ Brier/reliability), sliced by regime, lead and threshold, block-bootstrap confidence intervals, held-out years and the 2026 season.
- Product: district aggregation → table, map, CSV/GeoJSON, API; automated daily run.

### 17.5 Feasibility and viability

- All data sources are free and accessible; compute needs are modest (a few million rows per lead time).
- Standard, well-understood methods; risk is contained by a baselines-first ladder.
- Phase-0 evidence: [your raw vs simple-correction result here].
- Modular: any gridded forecast (including NCMRWF/IMD models) can be plugged in.

### 17.6 Impact and benefits

- Better heavy-rain guidance for disaster-management agencies, water resource managers, agriculture and urban authorities.
- District-level, plain-language output supports early warning.
- Reproducible verification builds trust and supports operational adoption.
- Scalable to more regions, variables, lead times.

### 17.7 Research and references

See Section 19. Cite only what you have actually read.

### 17.8 Suggested slide outline (8–10 slides)

1. Title and team
2. The problem: regime-dependent errors (one striking example map)
3. Why a single correction fails (schematic)
4. Solution overview (architecture diagram)
5. Regime module (two-layer scheme, labels, forecast-side classifier)
6. Correction and heavy-rain probability (model ladder)
7. Verification plan and Phase-0 evidence
8. District product and dashboard mock-up
9. Feasibility, risks and mitigation
10. Impact, roadmap (incl. WD and NCMRWF integration)

---

## 18. Jury Q&A prep

| Likely question | Strong answer (in substance) |
|---|---|
| **How exactly do you define active/break/depression?** | Objective rules from the literature on observed rain and ERA5, with every threshold in a config file, plus a sensitivity check. Cite the source. |
| **The regime isn't known at forecast time. How do you use it?** | We predict it from forecast-side fields only, trained against the rule-based labels, and pass soft probabilities into the correction. |
| **What if the regime classifier is wrong?** | Soft probabilities blend corrections, so a wrong hard call doesn't dominate. We report accuracy by lead time and show the effect on final skill. |
| **How do you know regimes actually help?** | The model ladder: regime-aware ML (B4) vs regime-blind ML (B2) and global quantile mapping (B1), on held-out years, with confidence intervals. |
| **Isn't a good ML model already enough?** | That's exactly what B2 vs B4 tests. Here is what we found: [report honestly, including if the gain is small]. |
| **How do you avoid data leakage?** | Year-based splits, leave-one-year-out CV, untouched test seasons, init/valid-time audit, plus a pseudo-prospective test on 2026. |
| **Why not deep learning?** | Limited seasons of consistent NWP data make deep nets prone to overfitting. Gradient boosting is robust and explainable. Deep learning is a stretch goal if more data is available. |
| **How do you handle extremely heavy rain with so few samples?** | Pooling, an extreme-value tail fit, honest uncertainty, and we don't claim skill we can't verify. |
| **Are the probabilities reliable?** | Calibrated with held-out data and checked with reliability diagrams and Brier skill score. |
| **How does it compare with what IMD does operationally?** | We don't claim to replace IMD's system. We provide a transparent post-processing layer that could complement it, and we're ready to test on NCMRWF/IMD model output. |
| **Does the improvement hold for other models?** | We tested a second model (ECMWF open data) and the pipeline is model-agnostic. [State the result.] |
| **Is it operational?** | It's a working prototype with an automated daily run, versioning and fallbacks. Operational adoption would need longer validation and integration. |
| **What are the limitations?** | Post-processing can't fix a wrong weather system; gains shrink with lead time; extreme events are hard to verify; observation uncertainty. |
| **What would you do with more time/data?** | Western-disturbance module, more seasons via reforecasts, ensemble post-processing, multi-model blending, integration with MoES models. |
| **Why does observation quality matter?** | Gridded rain is interpolated from gauges. Errors in heavy orographic rain limit verification, and we say so. |

---

## 19. References to read

*From my recollection. **Verify each citation (authors, year, journal) before using it.** Cite only what you have read.*

| Topic | Reference |
|---|---|
| Active/break monsoon spells | Rajeevan, M., Gadgil, S., Bhate, J. (2010). Active and break spells of the Indian summer monsoon. *J. Earth Syst. Sci.* |
| IMD gridded rainfall | Pai, D.S., et al. (2014). Development of a new high spatial resolution (0.25° × 0.25°) long period (1901–2010) daily gridded rainfall data set over India. *Mausam* |
| Monsoon low-pressure systems | Hurley, J.V., Boos, W.R. (2015). A global climatology of monsoon low-pressure systems. *Q. J. R. Meteorol. Soc.* |
| Fractions Skill Score | Roberts, N.M., Lean, H.W. (2008). Scale-selective verification of rainfall accumulations from high-resolution forecasts of convective events. *Mon. Wea. Rev.* |
| Post-processing review | Vannitsem, S., et al. (2021). Statistical postprocessing for weather forecasts: review, challenges, and avenues in a big data world. *Bull. Amer. Meteor. Soc.* |
| ML post-processing | Rasp, S., Lerch, S. (2018). Neural networks for postprocessing ensemble weather forecasts. *Mon. Wea. Rev.* |
| Proper scoring rules | Gneiting, T., Raftery, A.E. (2007). Strictly proper scoring rules, prediction, and estimation. *J. Amer. Statist. Assoc.* |
| GEFS v12 reforecast | Hamill, T.M., et al. (2022). The reanalysis for the GEFS v12 reforecast *(verify the exact title and authors)* |
| ERA5 | Hersbach, H., et al. (2020). The ERA5 global reanalysis. *Q. J. R. Meteorol. Soc.* |
| IMD rainfall categories and warning colours | IMD website and press material *(verify the current definitions)* |

---

## 20. Verify-list, checklists, glossary

### 20.1 Things I could not confirm (check before you rely on them)

1. IMD/MoES marking criteria and the 2026 idea-submission template for this PS.
2. The SIH 2026 timeline, round structure, team-size rules, and any rules on AI-generated content in submissions.
3. GFS archive depth and current hosting locations; model-version dates (GFS v16 in 2021).
4. GEFS v12 reforecast: bucket, variables, members, resolution.
5. IMD gridded rainfall: current-year availability, latency, and terms of use; whether a near-real-time 0.25° product exists for the 2026 season.
6. IMD's day convention for daily rainfall (03 UTC to 03 UTC) for the exact dataset you use.
7. Exact active/break criteria and the core-monsoon-zone boundary from the source paper.
8. IMD depression/deep-depression wind thresholds and current warning-colour definitions.
9. Availability and access terms for NCMRWF/NCUM/NEPS and any new MoES high-resolution model data.
10. Current versions/APIs of `Herbie`, `imdlib`, `cdsapi`, `earthaccess`.
11. Reference details in Section 19.
12. What ECMWF open data currently provides (the 0.25° archive begins Feb 2024; ECMWF moved to a broader open-data policy in Oct 2025, so check what fields and history are available now).

### 20.2 Before-you-submit checklist

- [ ] Phase-0 spike done, with one real baseline number
- [ ] Marking criteria/template read and followed
- [ ] Mentor named (meteorology, if possible)
- [ ] All six metrics (RMSE, ETS, CSI, POD, FAR, FSS) in the verification plan
- [ ] Model ladder (B0 to B4) shown
- [ ] Regime definitions cited and documented
- [ ] Forecast-side classifier explicitly stated
- [ ] Heavy-rain thresholds match IMD categories
- [ ] Limitations slide included
- [ ] Nothing claimed that you haven't computed
- [ ] Submission written in your own words

### 20.3 Glossary

| Term | Meaning |
|---|---|
| **NWP** | Numerical Weather Prediction: physics-based forecast models |
| **Post-processing** | Statistical/ML correction of raw model output |
| **Bias correction** | Adjusting forecasts to remove systematic error |
| **Quantile mapping (QM)** | Matching the forecast distribution to the observed distribution |
| **Regime** | A recurring weather situation with a characteristic pattern and error behaviour |
| **Active / break spell** | Periods of enhanced / suppressed monsoon rainfall over the core zone |
| **Monsoon low / depression** | A cyclonic vortex in the monsoon flow that brings organised heavy rain |
| **Orographic rain** | Rain enhanced by air lifted over terrain |
| **Western disturbance (WD)** | A mid-latitude trough that brings rain/snow to NW India |
| **CMZ** | Core monsoon zone: the central-India region used to define active/break spells |
| **Lead time** | How far ahead the forecast is issued (Day-1, Day-2 …) |
| **POD / FAR / CSI / ETS / FBI** | Categorical verification scores (Section 3.5) |
| **FSS** | Fractions Skill Score: neighbourhood-based rainfall skill |
| **BSS** | Brier Skill Score: skill of probability forecasts vs a reference |
| **Reliability diagram** | Plot showing whether forecast probabilities match observed frequencies |
| **LOYO-CV** | Leave-one-year-out cross-validation |
| **GPD** | Generalised Pareto Distribution, used to model extreme tails |
| **Hurdle model** | Two-stage model: does it rain, and how much |
| **APCP** | GFS accumulated precipitation field |
| **Pseudo-prospective test** | Testing on a recent, untouched period, as if forecasting in real time |
| **IMERG** | NASA's satellite-based global precipitation product |
| **ERA5** | ECMWF's global atmospheric reanalysis |

---

*End of blueprint. Next steps: run the Phase-0 spike, then adapt Section 17 into your own submission text.*
