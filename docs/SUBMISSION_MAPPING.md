# SIH26080 Problem Statement & Deliverables Traceability Mapping

**Document Reference:** Varsha Official Deliverables Mapping  
**Problem Statement ID:** SIH26080 (Ministry of Earth Sciences / IMD)  
**Version:** 1.0.0

---

## Deliverables Mapping Matrix (D1 – D5)

| Deliverable ID | Required SIH Deliverable | Implementation Module in Varsha | API Surface | Web UI View / Artifact | Automated Evidence & Verification Tests |
|---|---|---|---|---|---|
| **D1** | **Weather Regime Classifier**<br>*(Active, Break, Depression, Coastal/Orographic)* | `src/varsha/regimes/rules.py`<br>`src/varsha/regimes/classifier.py` | `GET /api/v1/runs/{id}/regime` | `/regimes` route & Console left rail | `tests/unit/test_regime_rules.py`<br>`tests/unit/test_classifier.py` |
| **D2** | **Bias-Corrected Rainfall Forecast**<br>*(Improved over raw NWP for Day-1..5 with P10/P50/P90)* | `src/varsha/models/b4_regime_gbm.py`<br>`src/varsha/models/hurdle.py` | `GET /api/v1/runs/{id}/grid` | Main Cartography Console (`/`) & District Inspector | `tests/unit/test_models.py`<br>`tests/controls/test_controls.py` |
| **D3** | **Heavy-Rainfall Exceedance Probability**<br>*(Calibrated probabilities for 64.5 & 115.6 mm/day)* | `src/varsha/models/heavy_rain.py`<br>`src/varsha/models/calibration.py` | `GET /api/v1/runs/{id}/districts` | Map Overlays (`p64`, `p115`) & District Detail | `tests/unit/test_heavy_rain.py`<br>`tests/property/test_properties.py` |
| **D4** | **District-Level Decision Product**<br>*(User-friendly district table, map, CSV, GeoJSON)* | `src/varsha/product/districts.py`<br>`src/varsha/product/alerts.py` | `GET /api/v1/runs/{id}/districts.geojson`<br>`GET /api/v1/runs/{id}/districts.csv` | Bottom District Drawer & Single-Page Brief (`/d/:id`) | `tests/unit/test_district_product.py`<br>`e2e/console.spec.ts` |
| **D5** | **Verification Report & Statistical Audit**<br>*(RMSE, ETS, CSI, POD, FAR, FSS, CIs, Controls)* | `src/varsha/verify/metrics.py`<br>`src/varsha/verify/fss.py`<br>`src/varsha/verify/report/` | `GET /api/v1/verification/summary`<br>`GET /api/v1/verification/report` | Verification View (`/verification`) & Standalone HTML Report | `tests/unit/test_metrics.py`<br>`tests/unit/test_fss.py` |
