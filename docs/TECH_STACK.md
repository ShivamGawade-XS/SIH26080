# Technology Stack & Architecture Decisions

**Document Reference:** Varsha Technology Stack Specification  
**Version:** 1.0.0

---

## 1. Technology Selection Matrix

| Subsystem Layer | Selected Technology | Version / Spec | Justification & Alternatives Considered |
|---|---|---|---|
| **Language & Core Runtime** | **Python** | `3.11+` (`3.14.3` probed) | Industry standard for meteorological computation, scientific data science, and ML post-processing. |
| **Package & Env Management** | **uv** (fallback: `venv`+`pip`) | `uv >= 0.12` | Ultra-fast, deterministic dependency resolution with pinned lockfiles. |
| **Multidimensional Data** | **xarray + numpy + zarr** | `xarray >= 2024.0`, `zarr >= 2.18` | Native NetCDF/GRIB CDM semantics, named coordinates (`time`, `lead`, `lat`, `lon`), chunked I/O. |
| **Tabular & Columnar Data** | **pandas + pyarrow** | `pandas >= 2.2`, `pyarrow >= 15.0` | Parquet file storage for fast slice extraction and high-throughput serialization. |
| **Geospatial Processing** | **geopandas + shapely** | `geopandas >= 0.14`, `shapely >= 2.0` | Vector administrative boundaries, spatial indexing, point-in-polygon assignment. |
| **Machine Learning Engine** | **LightGBM + scikit-learn** | `lightgbm >= 4.3`, `scikit-learn >= 1.4` | High-speed gradient boosting with native quantile regression (`pinball`), multiclass support, fast TreeSHAP feature contributions (`pred_contrib`). Avoids heavy PyTorch dependencies for tabular MVP (ADR 002). |
| **Data Connectors (Real Mode)** | **herbie-data + imdlib** | `herbie-data >= 2024.0`, `imdlib >= 0.1` | Automated subsetting and downloading of NOAA GFS and IMD gridded binaries. |
| **Backend API Framework** | **FastAPI + Pydantic v2** | `fastapi >= 0.110`, `pydantic >= 2.6` | High performance, automatic OpenAPI documentation, strict schema validation. |
| **CLI & Harness** | **typer + rich** | `typer >= 0.9` | Ergonomic command-line tooling with clear execution feedback. |
| **Report Generation** | **Jinja2 + Matplotlib** | `jinja2 >= 3.1`, `matplotlib >= 3.8` | Standalone, print-ready, zero-network self-contained HTML verification reports with SVG charts. |
| **Frontend Framework** | **React 18 + TypeScript + Vite**| `react ^18.3`, `vite ^5.2`, `ts ^5.4` | Fast development, strict typing, small bundle footprint, modular architecture. |
| **Map Visualization** | **MapLibre GL JS (offline)** | `maplibre-gl ^4.0` | High-performance WebGL vector rendering of district polygons and graticule with zero external tile server dependency (ADR 004). |
| **Scientific Charting (Web)**| **D3 Scales & Hand-Crafted SVG**| `d3-scale`, `d3-shape`, `d3-axis` | Maximum typographic and aesthetic control, accessible SVG DOM, zero generic chart templates. |
| **Design System & Styling** | **CSS Modules + Custom Properties** | Vanilla CSS Tokens | Strictly follows anti-template rules: no default Tailwind blues/purples, warm paper theme, tabular numbers. |
| **Testing & Verification** | **pytest + hypothesis + Playwright**| `pytest >= 8.0`, `hypothesis >= 6.100` | Unit, property-based metric verification, Golden contingency fixtures, and headless browser E2E. |

---

## 2. Architecture Decision Records (ADRs)

Detailed ADR documents are recorded under `docs/adr/`:
- **ADR 001:** [Cell-Centre District Spatial Aggregation](adr/ADR-001-immutable-product-bundles.md)
- **ADR 002:** [LightGBM Hurdle Model Formulation for B4](adr/ADR-002-two-stage-regime-aware-correction.md)
- **ADR 003:** [Static-First Product Bundle Architecture](adr/ADR-003-scientific-controls-and-leakage-canaries.md)
- **ADR 004:** [Offline MapLibre Vector Cartography Without CDN Tiles](adr/ADR-004-offline-first-cartography-and-zero-tileserver.md)
- **ADR 005:** [Synthetic World Generator for Deterministic Ground-Truth CI](PRD.md)

