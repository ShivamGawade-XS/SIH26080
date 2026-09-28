# ADR 004: Offline MapLibre Vector Cartography Without External Tile Servers

**Status:** Accepted  
**Deciders:** Varsha Core Team  
**Date:** 2026-09-20

---

## Context
Standard web GIS applications rely on external raster or vector tile services (Mapbox, OpenStreetMap tiles, Carto, Stamen). In accordance with **N7 (Offline-First Runtime)**, **N6 (Licences)**, and **N9 (Design Integrity)**:
1. The application must operate with 100% functionality without any internet connection.
2. External commercial tile API keys (Mapbox) or third-party tracking CDNs are strictly prohibited.
3. Cartography should follow Swiss typographic and national met service aesthetic restraint rather than generic commercial street maps.

## Decision
1. Use **MapLibre GL JS** initialized with a local inline vector style.
2. Render district boundaries directly from bundled GeoJSON polygon layers over a clean, warm background (`#F4F2ED` in light mode, `#0F1418` in dark mode).
3. Overlay an explicit geographic graticule ($5^\circ$ interval) with degree annotations, scale bar, and raster data overlay.
4. No external HTTP requests are made for basemap tiles.

## Consequences
- **Positive:** 100% offline functionality; zero external license encumbrance; fast initial render; completely custom palette aligned with design tokens.
- **Negative:** Street-level zooming beyond administrative district level is intentionally omitted.
