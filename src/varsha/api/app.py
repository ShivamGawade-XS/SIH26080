"""
FastAPI Backend Application for Project Varsha.
Serves immutable product bundles, district forecasts, GeoJSON layers, and verification reports.
"""

import json
from pathlib import Path
import re
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse

from varsha import SYSTEM_NAME, SYSTEM_TITLE, SYSTEM_VERSION
from varsha.config import get_config

app = FastAPI(
    title=SYSTEM_TITLE,
    version=SYSTEM_VERSION,
    description="Regime-Aware AI Post-Processing of Monsoon Rainfall Forecasts API",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Enforce defense-in-depth HTTP security headers on all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' data: blob:;"
    return response


PRODUCTS_DIR = Path("products")



SAFE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_\-]+$")


def get_latest_run_id() -> str:
    """Find the newest run bundle in products/ directory."""
    if not PRODUCTS_DIR.exists():
        return "SYN_DEFAULT_DEMO"
    runs = [d.name for d in PRODUCTS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]
    if not runs:
        return "SYN_DEFAULT_DEMO"
    runs.sort(reverse=True)
    return runs[0]


def load_bundle_file(run_id: str, filename: str) -> Any:
    if not run_id or run_id in ("latest", "SYN_DEFAULT_DEMO"):
        run = get_latest_run_id()
    else:
        if ".." in run_id or "/" in run_id or "\\" in run_id or not SAFE_ID_PATTERN.match(run_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid run_id: contains illegal or traversal characters",
            )
        run = run_id

    base_dir = PRODUCTS_DIR.resolve()
    run_dir = (PRODUCTS_DIR / run).resolve()
    if not str(run_dir).startswith(str(base_dir)):
        raise HTTPException(status_code=400, detail="Path traversal detected")

    path = (run_dir / filename).resolve()
    if not str(path).startswith(str(run_dir)):
        raise HTTPException(status_code=400, detail="Path traversal detected")

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Artifact {filename} for run {run} not found. Ensure pipeline has executed.",
        )
    if filename.endswith(".json") or filename.endswith(".geojson"):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    elif filename.endswith(".csv") or filename.endswith(".html"):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return None


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Healthcheck and system liveness endpoint."""
    return {
        "status": "healthy",
        "system": SYSTEM_NAME,
        "version": SYSTEM_VERSION,
    }


@app.get("/api/v1/meta")
def get_meta() -> dict[str, Any]:
    """System metadata, data mode, latest runs, and active profile."""
    cfg = get_config()
    runs = [d.name for d in PRODUCTS_DIR.iterdir() if d.is_dir()] if PRODUCTS_DIR.exists() else []
    runs.sort(reverse=True)
    latest_run = runs[0] if runs else "NONE"

    manifest = {}
    if latest_run != "NONE":
        try:
            manifest = load_bundle_file(latest_run, "manifest.json")
        except HTTPException:
            manifest = {}

    return {
        "system_name": SYSTEM_NAME,
        "version": SYSTEM_VERSION,
        "data_mode": cfg.data_mode,
        "latest_run": latest_run,
        "available_runs": runs,
        "leads": cfg.leads,
        "profile": cfg.profile.profile_name,
        "grid_resolution": cfg.profile.grid_resolution,
        "manifest": manifest,
    }


@app.get("/api/v1/runs")
def list_runs() -> list[dict[str, Any]]:
    """List all compiled forecast run bundles."""
    if not PRODUCTS_DIR.exists():
        return []
    result = []
    for d in sorted(PRODUCTS_DIR.iterdir(), reverse=True):
        if d.is_dir():
            m_path = d / "manifest.json"
            if m_path.exists():
                with open(m_path, encoding="utf-8") as f:
                    result.append(json.load(f))
            else:
                result.append({"run_id": d.name})
    return result


@app.get("/api/v1/runs/{run_id}/districts")
def get_districts(
    run_id: str,
    lead: int = Query(default=1, ge=1, le=5),
) -> list[dict[str, Any]]:
    """Get district tabular forecast for a specific lead time."""
    data = load_bundle_file(run_id, "districts.json")
    lead_key = str(lead)
    if lead_key in data:
        return data[lead_key]
    # Return all if not separated by lead
    return data if isinstance(data, list) else []


@app.get("/api/v1/runs/{run_id}/districts.geojson")
def get_districts_geojson(run_id: str) -> Any:
    """Download vector GeoJSON FeatureCollection of districts."""
    return load_bundle_file(run_id, "districts.geojson")


@app.get("/api/v1/runs/{run_id}/districts.csv")
def get_districts_csv(run_id: str) -> PlainTextResponse:
    """Download district forecasts as CSV."""
    csv_str = load_bundle_file(run_id, "districts.csv")
    return PlainTextResponse(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=districts_{run_id}.csv"},
    )


@app.get("/api/v1/runs/{run_id}/grid")
def get_grid_layer(
    run_id: str,
    lead: int = Query(default=1, ge=1, le=5),
    layer: str = Query(default="corrected", pattern="^(raw|corrected|delta|p64|p115)$"),
) -> dict[str, Any]:
    """Get spatial raster grid matrix for a given lead and layer."""
    grid_data = load_bundle_file(run_id, "grid_layers.json")
    lead_str = str(lead)
    if "layers" in grid_data and lead_str in grid_data["layers"]:
        layer_values = grid_data["layers"][lead_str].get(layer, [])
        return {
            "lats": grid_data.get("lats", []),
            "lons": grid_data.get("lons", []),
            "lead": lead,
            "layer": layer,
            "values": layer_values,
        }
    raise HTTPException(status_code=404, detail="Grid layer data not found")


@app.get("/api/v1/runs/{run_id}/regime")
def get_regimes(run_id: str) -> dict[str, Any]:
    """Get domain and regional regime probability forecasts (Day-1..5)."""
    return load_bundle_file(run_id, "regime_probs.json")


@app.get("/api/v1/districts/{district_id}")
def get_district_detail(
    district_id: str,
    run_id: str = Query(default="latest", alias="run"),
) -> dict[str, Any]:
    """Get Day-1 through Day-5 forecast timeline for a specific district."""
    if not district_id or ".." in district_id or "/" in district_id or "\\" in district_id or not SAFE_ID_PATTERN.match(district_id):
        raise HTTPException(status_code=400, detail="Invalid district_id")
    districts_data = load_bundle_file(run_id, "districts.json")
    timeline = []
    d_meta = None

    for lead in [1, 2, 3, 4, 5]:
        lead_rows = districts_data.get(str(lead), [])
        for row in lead_rows:
            if row.get("district_id") == district_id:
                timeline.append(row)
                if not d_meta:
                    d_meta = row

    if not timeline:
        raise HTTPException(
            status_code=404, detail=f"District {district_id} not found in run {run_id}"
        )

    return {
        "district_id": district_id,
        "name": d_meta.get("district_name") if d_meta else district_id,
        "state": d_meta.get("state") if d_meta else "",
        "is_subgrid": d_meta.get("is_subgrid", False) if d_meta else False,
        "timeline": timeline,
    }


@app.get("/api/v1/verification/summary")
def get_verification_summary(run_id: str = Query(default="latest", alias="run")) -> dict[str, Any]:
    """Get benchmark ladder (B0-B4) verification metrics and bootstrap CIs."""
    return load_bundle_file(run_id, "verification.json")


@app.get("/api/v1/verification/slices")
def get_verification_slices(run_id: str = Query(default="latest", alias="run")) -> dict[str, Any]:
    """Get multi-dimensional verification slices by regime, lead, and region."""
    return load_bundle_file(run_id, "verification_slices.json")


@app.get("/api/v1/verification/reliability")
def get_verification_reliability(run_id: str = Query(default="latest", alias="run")) -> dict[str, Any]:
    """Get reliability curve bins and sharpness histograms."""
    return load_bundle_file(run_id, "reliability.json")


@app.get("/api/v1/verification/controls")
def get_verification_controls(run_id: str = Query(default="latest", alias="run")) -> dict[str, Any]:
    """Get scientific controls results (positive, negative, and leakage canaries)."""
    return load_bundle_file(run_id, "controls_summary.json")


@app.get("/api/v1/verification/report", response_class=HTMLResponse)
def get_verification_report(run_id: str = Query(default="latest", alias="run")) -> HTMLResponse:
    """Render standalone HTML verification report."""
    html = load_bundle_file(run_id, "report.html")
    return HTMLResponse(content=html)


# Absolute path anchored to this file — works regardless of CWD
_WEB_DIST = Path(__file__).parent.parent.parent.parent / "web" / "dist"


@app.get("/assets/{asset_path:path}")
async def serve_asset(asset_path: str) -> Any:
    """Serve built frontend asset files (JS, CSS, map worker, etc.)."""
    file_path = _WEB_DIST / "assets" / asset_path
    if file_path.is_file():
        return FileResponse(str(file_path))
    raise HTTPException(status_code=404, detail="Asset not found")


@app.exception_handler(404)
async def spa_fallback(request: Request, exc: Exception) -> FileResponse | JSONResponse:
    """SPA fallback: return index.html for unknown UI routes so React Router works.

    API paths and /healthz always get a JSON 404 — only browser navigation
    routes get the SPA shell.
    """
    path = request.url.path
    if path.startswith("/api/") or path == "/healthz" or path.startswith("/assets/"):
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    index_path = _WEB_DIST / "index.html"
    if index_path.is_file():
        return FileResponse(str(index_path))
    return JSONResponse(
        {"detail": "Frontend not built. Run: cd web && npm run build"},
        status_code=404,
    )
