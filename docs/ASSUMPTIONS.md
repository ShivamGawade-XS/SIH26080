# Engineering & Scientific Assumptions: Project Varsha

**Document Reference:** Project Varsha Assumptions Register  
**Governing Rule:** N1 (Honest Provenance), N3 (Boundaries), N5 (No Gaming)  
**Version:** 1.0.0

---

## 1. Meteorological & Physical Assumptions

| Assumption ID | Description & Context | Validation Method | Impact / Fallback |
|---|---|---|---|
| **ASM-MET-01** | **Accumulation Window Alignment:** IMD daily precipitation is defined as $03:00\text{ UTC} \rightarrow 03:00\text{ UTC}$ ($08:30\text{ IST} \rightarrow 08:30\text{ IST}$). NWP step forecasts are de-accumulated to match this exact window. | De-accumulation unit tests with step fixtures (`test_align.py`). | Configurable in `configs/data.yaml` if an alternative window is specified. |
| **ASM-MET-02** | **Core Monsoon Zone (CMZ) Extent:** Core monsoon region is defined as the rectangular bounding box $[18^\circ\text{N}-28^\circ\text{N}, 73^\circ\text{E}-86^\circ\text{E}]$ for standardized precipitation anomaly calculation. | Sensitivity analysis perturbing boundaries by $\pm 1^\circ$. | Documented in `docs/METHODOLOGY.md`. |
| **ASM-MET-03** | **Synoptic Persistence:** Active and break monsoon spells are required to maintain a minimum duration of $\ge 3$ consecutive days to filter transient high-frequency noise. | Sensitivity analysis varying spell length $\in \{2, 3, 4\}$ days. | Rule recovery verified on synthetic ground truth. |
| **ASM-MET-04** | **Sub-Daily Diurnal Peak Assumption:** For daily aggregated products, sub-daily convective peaks are captured through maximum CAPE and PWAT predictors at initialisation time. | Feature importance evaluation. | Predictors logged in feature registry. |

---

## 2. Machine Learning & Statistical Assumptions

| Assumption ID | Description & Context | Validation Method | Impact / Fallback |
|---|---|---|---|
| **ASM-ML-01** | **Year-Based Split Independence:** Monsoon seasons across distinct calendar years ($S01, S02, \dots$) are assumed to be approximately conditionally independent given large-scale ENSO/IOD phase. | Block-bootstrap CI resampling by 5-day synoptic blocks. | Prevents intra-season autocorrelation leakage. |
| **ASM-ML-02** | **Zero-Inflation Separation (Hurdle):** Precipitation occurrence ($P \ge 0.1\text{ mm}$) and non-zero precipitation intensity can be factored into a conditionally independent two-stage model. | Brier score on stage 1 and pinball loss on stage 2. | Mitigates zero-inflation artifacts in median predictions. |
| **ASM-ML-03** | **Monotone Threshold Ordering:** Exceedance probability for heavier thresholds cannot mathematically exceed lighter thresholds ($P_{\ge 115.6} \le P_{\ge 64.5}$). | Monotonicity property tests with Hypothesis. | Post-hoc isotonic clipping enforced in prediction pipeline. |

---

## 3. Cartographic & Administrative Boundary Assumptions

| Assumption ID | Description & Context | Validation Method | Impact / Fallback |
|---|---|---|---|
| **ASM-GEO-01** | **Cell-Centre Aggregation:** District aggregation assigns grid cells whose coordinates fall inside the district vector boundary. | Polygon centroid validation in `src/varsha/data/boundaries.py`. | Small districts ($\le 1$ cell) flagged with explicit `is_subgrid: true` badge. |
| **ASM-GEO-02** | **Boundary Authoritativeness:** DataMeet / GeoBoundaries community polygons are utilized as the local base for development and evaluation. Official Survey of India validation is marked as a required human signoff (H4). | Geometry topological validation (no invalid or self-intersecting rings). | Boundary fallback mode (grid clusters) available if vector loading fails. |

---

## 4. Operational & Software Architecture Assumptions

| Assumption ID | Description & Context | Validation Method | Impact / Fallback |
|---|---|---|---|
| **ASM-SYS-01** | **Offline Runtime Priority:** All dependencies, fonts (`@fontsource`), map vector assets, and static bundles are bundled locally without external network calls during `make demo`. | Playwright offline network interception. | Guarantees reproducible air-gapped evaluation. |
| **ASM-SYS-02** | **Deterministic Seeds:** All pseudo-random processes (synthetic generation, cross-validation folds, LightGBM boosting seeds) use fixed seed `42`. | Multi-run SHA-256 artifact hash comparison. | Guarantees bit-identical execution across CI runs. |
