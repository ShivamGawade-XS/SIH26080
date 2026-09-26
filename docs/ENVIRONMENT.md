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
| **Python** | Yes | 3.14.3 (active default) / 3.13 auxiliary | `C:\Users\ASHWITH\AppData\Local\Python\pythoncore-3.14-64\python.exe` |
| **uv** | Yes | `0.12.14` | `C:\Users\ASHWITH\AppData\Local\Programs\Python\Python313\Scripts\uv.EXE` |
| **pip** | Yes | `26.2.1` | `C:\Users\ASHWITH\AppData\Local\Programs\Python\Python313\Scripts\pip.EXE` |
| **Node.js** | Yes | `v25.1.0` | `C:\Program Files\nodejs\node.EXE` |
| **npm** | Yes | `11.17.0` | `C:\Users\ASHWITH\AppData\Roaming\npm\npm.CMD` |
| **pnpm** | Yes | `11.24.0` | `C:\Users\ASHWITH\AppData\Roaming\npm\pnpm.CMD` |
| **git** | Yes | `2.51.2.windows.1` | `C:\Program Files\Git\cmd\git.EXE` |
| **GitHub CLI (gh)**| Yes | `2.98.0` | `C:\Program Files\GitHub CLI\gh.EXE` |
| **Docker** | No | Not found in system PATH | N/A |
| **Playwright** | Yes | `1.60.0` (Python/Node capable) | `C:\Users\ASHWITH\AppData\Local\Programs\Python\Python313\Scripts\playwright.EXE` |

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
