"""
Open-Source Scout and Due Diligence Script for SIH26080.
Queries GitHub API via `gh` CLI to inspect exact repository metadata,
licenses, star counts, latest commit dates, and descriptions.
"""
import json
import subprocess
import sys
from datetime import datetime

SEED_REPOS = [
    # S1: Forecast data access
    "blaylockbk/Herbie",
    "ecmwf/ecmwf-opendata",
    "open-meteo/open-meteo",
    # S2: Indian observation access
    "iamsaswata/imdlib",
    "nsidc/earthaccess",
    # S3: Reanalysis / ARD
    "google-research/weatherbench2",
    "google-research/arco-era5",
    # S4: Bias correction / QM
    "Ouranosinc/xclim",
    "ecmwf-projects/ibicus",
    "btschwertfeger/python-cmethods",
    "yrobink/SBCK-python",
    # S5: ML Post-processing
    "EUPP-benchmark/climetlab-eumetnet-postprocessing-benchmark",
    "khoehlein/Permutation-invariant-Postprocessing",
    "slerch/ensemble-postprocessing",
    # S6: Monsoon diagnostics & regimes
    "Unidata/MetPy",
    "ajdawson/windspharm",
    "ClimateGlobalChange/tempestextremes",
    # S7: Forecast verification
    "nci/scores",
    "xarray-contrib/xskillscore",
    "pySTEPS/pysteps",
    "pangeo-data/climpred",
    "TheClimateCorporation/properscoring",
    "NCAR/METplus",
    "met-no/verif",
    # S8: Calibration & uncertainty
    "scikit-learn-contrib/MAPIE",
    "scikit-learn/scikit-learn",
    "Jonathan-Wegener/netcal",
    # S9: Geospatial ops
    "JiaweiZhuang/xESMF",
    "pangeo-data/xESMF",
    "xarray-contrib/xarray-regrid",
    "regionmask/regionmask",
    "isciences/exactextract",
    "ks905383/xagg",
    # S10: Boundary data
    "datameet/maps",
    "wmgeolab/geoBoundaries",
    # S11: Web mapping and charts
    "maplibre/maplibre-gl-js",
    "visgl/deck.gl",
    "d3/d3",
    "observablehq/plot",
    "manzt/zarrita.js",
    "cambecc/earth",
    # AI Weather & Frontier Models
    "ecmwf/ai-models",
    "NVIDIA/earth2studio",
    "google-deepmind/graphcast"
]

def check_repo(repo_full_name):
    cmd = ["gh", "api", f"repos/{repo_full_name}"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        
        # Check license specifically
        license_key = data.get("license", {})
        lic_spdx = license_key.get("spdx_id") if license_key else "NO_LICENSE_IN_API"
        lic_name = license_key.get("name") if license_key else "None"
        
        # Also check license file via contents API if license is missing or custom
        return {
            "name": data.get("full_name"),
            "url": data.get("html_url"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "license_spdx": lic_spdx,
            "license_name": lic_name,
            "archived": data.get("archived", False),
            "updated_at": data.get("updated_at"),
            "pushed_at": data.get("pushed_at"),
            "description": data.get("description"),
            "language": data.get("language"),
            "default_branch": data.get("default_branch"),
            "status": "VERIFIED"
        }
    except subprocess.CalledProcessError as e:
        return {
            "name": repo_full_name,
            "status": "NOT_FOUND_OR_ERROR",
            "error": e.stderr.strip() if e.stderr else str(e)
        }

if __name__ == "__main__":
    results = {}
    print(f"Scouting {len(SEED_REPOS)} seed repositories...")
    for r in SEED_REPOS:
        print(f"Checking {r}...", end=" ", flush=True)
        res = check_repo(r)
        results[r] = res
        print(f"-> {res.get('status')}: {res.get('license_spdx', 'N/A')} (Stars: {res.get('stars', 'N/A')})")
    
    with open("docs/reuse/seed_verification.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Saved results to docs/reuse/seed_verification.json")
