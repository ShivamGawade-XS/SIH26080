# ADR 003: Static-First Product Bundle Architecture

**Status:** Accepted  
**Deciders:** Varsha Core Team  
**Date:** 2026-09-20

---

## Context
Meteorological decision systems must operate reliably in environments with intermittent connectivity, during disaster response situations, and under rigorous verification audits. If an API calculates heavy spatial aggregations and ML inferences dynamically per request, it introduces high latency, potential runtime non-determinism, and CPU bottlenecks.

## Decision
Adopt an immutable **Static-First Product Bundle Architecture**:
1. The ML and verification pipeline executes offline or on schedule, compiling all outputs for a given forecast cycle into an immutable directory: `products/<run_id>/`.
2. The bundle contains precomputed JSON, GeoJSON, Parquet slice tables, quantized compact grid binaries, manifest metadata, and a standalone HTML report.
3. The FastAPI server acts as a high-speed, lightweight static/slice server reading from these precomputed bundles. The web frontend can also consume a snapshot bundle offline without any active backend server.

## Consequences
- **Positive:** Sub-10ms API responses; zero runtime model inference failure risk; complete auditability and reproducibility; simple caching; offline demo capability.
- **Negative:** Storage overhead per forecast cycle (mitigated by quantized grid binaries $\le 150\text{ KB}$).
