"""
Precise candidate resolver for SIH26080 open-source due diligence.
Searches GitHub for exact packages, verified owners, licenses, and topics.
"""
import subprocess
import json
import time

QUERIES = [
    # Verif
    "verif weather verification",
    "forecast verification python",
    "FSS fractions skill score",
    "netcal calibration",
    "climetlab postprocessing",
    "monsoon rainfall bias correction",
    "imd rainfall python",
    "ecmwf ai-models",
    "rasp lerch postprocessing",
    "quantile mapping xclim",
    "weather regime python",
    "india geojson datameet",
    "geoboundaries india",
    "maplibre-gl js",
    "exactextract",
    "xagg",
    "scores xarray"
]

def search_topic(q):
    cmd = ["gh", "search", "repos", q, "--limit", "5", "--json", "fullName,description,stargazersCount,updatedAt,url"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(res.stdout) if res.stdout else []
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    results = {}
    for q in QUERIES:
        print(f"Searching for '{q}'...")
        r = search_topic(q)
        results[q] = r
        time.sleep(1) # respect rate limit
    with open("docs/reuse/refined_search_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Done!")
