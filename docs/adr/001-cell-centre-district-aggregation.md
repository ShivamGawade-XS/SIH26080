# ADR 001: Cell-Centre District Spatial Aggregation

**Status:** Accepted  
**Deciders:** Varsha Core Team  
**Date:** 2026-09-20

---

## Context
NWP forecast grids ($0.5^\circ \approx 55\text{ km}$, $0.25^\circ \approx 27\text{ km}$) do not conform to irregular administrative district boundaries. Aggregating continuous raster/grid data to vector polygons can be achieved via:
1. Exact polygon intersection / area-weighted fractional polygon clipping (e.g. `exactextract` / `rasterio`).
2. Cell-centre point-in-polygon mapping.

## Decision
For the MVP foundation, we implement **cell-centre point-in-polygon assignment** with explicit sub-grid fallbacks:
1. Each district is assigned all grid cells whose coordinate centres lie within the district boundary polygon.
2. If a small district contains zero or one cell centre, it is tagged with a boolean flag `is_subgrid: true`, and falls back to the nearest grid cell centre. The UI, table, and API explicitly display a sub-grid notice for these districts.
3. Area-weighted polygon fractional intersection is documented as a planned post-MVP enhancement.

## Consequences
- **Positive:** Extremely fast precomputation during pipeline bundle generation ($< 1\text{ second}$ for all 700+ Indian districts); simple data serialization; fully transparent point-to-polygon mapping.
- **Negative:** Small coastal or enclave districts may sample only a single nearby cell rather than an interpolated area fraction; handled gracefully with explicit UI indicators.
