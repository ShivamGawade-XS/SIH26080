# Environment Assessment (Phase 0 Probe)

**Generated:** 2026-09-20 (Phase 0 Environment Probe)  
**System Architecture:** Windows 11 64-bit (Build 10.0.26200-SP0)  
**Hardware Profile:** Intel64 Family 6 Model 154 Stepping 3 (12 logical cores)

---

## 1. System Resources

| Resource | Specification / Measured Value |
|---|---|
| **Operating System** | Windows 11 (10.0.26200, 64-bit) |
| **CPU Logical Cores** | 12 cores |
| **System RAM** | 15.70 GB Total (5.03 GB Available at probe time) |
| **Disk Space** | 237.86 GB Total, 9.97 GB Free |

---

## 2. Runtimes and Package Managers

| Tool / Runtime | Installed | Version / Details | Path |
|---|---|---|---|
| **Python** | Yes | 3.14.3 (active default) / 3.13 auxiliary | `python.exe` |
| **uv** | Yes | `0.12.14` | `uv.exe` |
| **pip** | Yes | `26.2.1` | `pip.exe` |
| **Node.js** | Yes | `v25.1.0` | `node.exe` |
| **npm** | Yes | `11.17.0` | `npm.cmd` |
| **pnpm** | Yes | `11.24.0` | `pnpm.cmd` |
| **git** | Yes | `2.51.2.windows.1` | `git.exe` |
| **GitHub CLI (gh)**| Yes | `2.98.0` | `gh.exe` |
| **Docker** | No | Not found in system PATH | N/A |
| **Playwright** | Yes | `1.60.0` (Python/Node capable) | `playwright.exe` |


---

## 3. Network Reachability Probe

| Endpoint / Data Provider | URL | Reachability Status | Details / HTTP Code |
|---|---|---|---|
| **GitHub** | `https://github.com` | **Reachable** | HTTP 200 OK |
| **NOAA Open Data (GFS AWS S3)** | `https://noaa-gfs-bdp-pds.s3.amazonaws.com` | **Reachable** | HTTP 200 OK |
| **IMD (Pune Portal)** | `https://www.imdpune.gov.in` | **Unreachable / Timeout** | Connection timed out |
| **ECMWF Open Data** | `https://data.ecmwf.int` | **Unreachable / SSL Issue**| SSL certificate verification failed (self-signed cert in chain) |
| **NASA Earthdata (Login/Portal)** | `https://urs.earthdata.nasa.gov` | **Reachable** | HTTP 200 OK |
| **Copernicus CDS (Portal)** | `https://cds.climate.copernicus.eu` | **Reachable** | HTTP 200 OK |

---

## 4. Operating Implications & Constraints

1. **Default Data Mode:** Because IMD gridded portals frequently experience timeouts or require custom internal access, and ECMWF certificates may have corporate proxy chains, the system's strict adherence to **N1 (Honest Provenance)** requires `synthetic` mode as the primary offline-first pipeline. Real-data connectors (NOAA GFS via Herbie, IMD gridded via imdlib) are implemented with deterministic mock fixtures and caching.
2. **Offline-First Runtime (N7):** No external CDNs, fonts, or map tiles will be loaded at runtime. All map assets, tokens, and packages are bundled locally.
3. **Execution Environment:** Windows PowerShell / CMD native execution, with Python virtual environments managed via `uv` or `python -m venv`.
