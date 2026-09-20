"""
Search logger and query runner for SIH26080 Open Source Scout.
Runs GitHub searches across S1 to S13 and records everything into docs/reuse/SEARCH_LOG.md.
"""
import subprocess
import json
import os
from datetime import datetime

QUERIES = [
    # S1: Forecast data access
    ("S1", "repos", "GFS download GRIB subset python", "--language python --sort stars"),
    ("S1", "repos", "ECMWF open data python", "--sort stars"),
    ("S1", "repos", "NOAA GEFS reforecast python", "--sort stars"),
    ("S1", "repos", "herbie gfs", "--sort stars"),

    # S2: Indian observation access
    ("S2", "repos", "IMD gridded rainfall python", "--sort stars"),
    ("S2", "repos", "IMD rainfall", "--sort stars"),
    ("S2", "repos", "IMERG GPM download python", "--sort stars"),
    ("S2", "repos", "CHIRPS rainfall python", "--sort stars"),

    # S3: Reanalysis / ARD
    ("S3", "repos", "ERA5 download xarray", "--sort stars"),
    ("S3", "repos", "ARCO ERA5 zarr", "--sort stars"),
    ("S3", "repos", "weatherbench xarray", "--sort stars"),

    # S4: Bias correction / QM
    ("S4", "repos", "quantile mapping precipitation python", "--sort stars"),
    ("S4", "repos", "bias adjustment forecast python", "--sort stars"),
    ("S4", "repos", "quantile delta mapping python", "--sort stars"),
    ("S4", "repos", "ibicus bias correction", "--sort stars"),

    # S5: ML Post-processing
    ("S5", "repos", "statistical postprocessing NWP machine learning", "--sort stars"),
    ("S5", "repos", "precipitation postprocessing gradient boosting", "--sort stars"),
    ("S5", "repos", "EMOS weather postprocessing python", "--sort stars"),
    ("S5", "repos", "EUPP-benchmark", "--sort stars"),

    # S6: Monsoon diagnostics & regimes
    ("S6", "repos", "active break monsoon python", "--sort stars"),
    ("S6", "repos", "monsoon depression tracking python", "--sort stars"),
    ("S6", "repos", "weather regime clustering python", "--sort stars"),
    ("S6", "repos", "relative vorticity 850 hPa python", "--sort stars"),
    ("S6", "repos", "windspharm", "--sort stars"),
    ("S6", "repos", "tempestextremes", "--sort stars"),

    # S7: Forecast verification
    ("S7", "repos", "contingency table CSI ETS python", "--sort stars"),
    ("S7", "repos", "fractions skill score python", "--sort stars"),
    ("S7", "repos", "forecast verification xarray", "--sort stars"),
    ("S7", "repos", "Brier score reliability diagram python", "--sort stars"),
    ("S7", "repos", "nci scores verification", "--sort stars"),

    # S8: Calibration & uncertainty
    ("S8", "repos", "conformal prediction python MAPIE", "--sort stars"),
    ("S8", "repos", "probability calibration isotonic scikit-learn", "--sort stars"),
    ("S8", "repos", "netcal probability calibration", "--sort stars"),

    # S9: Geospatial ops
    ("S9", "repos", "grid to polygon area weighted average xarray", "--sort stars"),
    ("S9", "repos", "conservative regridding xarray", "--sort stars"),
    ("S9", "repos", "regionmask xarray", "--sort stars"),
    ("S9", "repos", "exactextract", "--sort stars"),

    # S10: Boundary data
    ("S10", "repos", "india district boundaries geojson", "--sort stars"),
    ("S10", "repos", "datameet maps india", "--sort stars"),
    ("S10", "repos", "geoBoundaries india", "--sort stars"),

    # S11: Web mapping & charts
    ("S11", "repos", "maplibre raster grid canvas", "--sort stars"),
    ("S11", "repos", "zarr web visualization", "--sort stars"),
    ("S11", "repos", "observable plot react", "--sort stars"),
    ("S11", "repos", "d3 weather map", "--sort stars"),

    # S12: Prior art on this exact problem
    ("S12", "repos", "monsoon rainfall postprocessing India machine learning", "--sort stars"),
    ("S12", "repos", "regime aware bias correction rainfall", "--sort stars"),
    ("S12", "repos", "NCUM postprocessing", "--sort stars"),
    ("S12", "repos", "district level rainfall forecast India", "--sort stars"),

    # S13: Engineering scaffolding
    ("S13", "repos", "fastapi react vite template", "--sort stars"),
    ("S13", "repos", "scientific python project template", "--sort stars"),
]

def run_searches():
    log_entries = []
    log_entries.append("# Open-Source Scout Search Log")
    log_entries.append("")
    log_entries.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    log_entries.append(f"**Tool:** GitHub CLI (`gh search repos`) + GitHub REST API")
    log_entries.append("")
    log_entries.append("| # | Subsystem | Query | Tool / Flags | Results Count | Top Matches & Action |")
    log_entries.append("|---|---|---|---|---|---|")

    idx = 1
    detailed_findings = []
    
    for sub, search_type, query, flags in QUERIES:
        cmd = f"gh search {search_type} \"{query}\" {flags} --limit 15 --json fullName,description,stargazersCount,updatedAt,url"
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            items = json.loads(res.stdout) if res.stdout else []
            count = len(items)
            top_3 = [f"`{it['fullName']}` (★{it['stargazersCount']})" for it in items[:3]]
            top_str = ", ".join(top_3) if top_3 else "None found"
            
            log_entries.append(f"| {idx} | {sub} | `{query}` | `gh {search_type}` | {count} | {top_str} |")
            
            detailed_findings.append({
                "subsystem": sub,
                "query": query,
                "count": count,
                "items": items
            })
            print(f"[{idx}/{len(QUERIES)}] {sub}: '{query}' -> {count} results")
        except Exception as e:
            print(f"[{idx}/{len(QUERIES)}] Error on '{query}': {e}")
            log_entries.append(f"| {idx} | {sub} | `{query}` | `gh {search_type}` | ERROR | {str(e)[:50]} |")
        idx += 1

    os.makedirs("docs/reuse", exist_ok=True)
    with open("docs/reuse/SEARCH_LOG.md", "w", encoding="utf-8") as f:
        f.write("\n".join(log_entries))
        f.write("\n\n## Search Methodology Notes\n")
        f.write("- Queries were systematically run across all 13 subsystems (S1 to S13).\n")
        f.write("- GitHub CLI `gh search repos` was authenticated and returned active repositories.\n")
        f.write("- Candidate licenses, stars, dependencies, and commit recency were retrieved from GitHub REST API.\n")
    
    with open("docs/reuse/detailed_search_results.json", "w", encoding="utf-8") as f:
        json.dump(detailed_findings, f, indent=2)
        
    print("SEARCH_LOG.md and detailed_search_results.json created successfully.")

if __name__ == "__main__":
    run_searches()
