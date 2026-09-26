"""
Administrative Boundary Management and District Spatial Mapping.
Handles GeoJSON district polygon loading, cell-centre assignment, and sub-grid detection.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from shapely.geometry import Point, mapping, shape



@dataclass
class DistrictMeta:
    district_id: str
    name: str
    state: str
    centroid_lat: float
    centroid_lon: float
    cell_indices: list[tuple[int, int]]  # (lat_idx, lon_idx)
    is_subgrid: bool
    geometry: dict[str, Any]


# Representative sample districts across key Indian monsoon zones
DEFAULT_DISTRICTS_DATA: list[dict[str, Any]] = [
    {
        "id": "IND_MH_MUM",
        "name": "Mumbai City",
        "state": "Maharashtra",
        "lat": 18.96,
        "lon": 72.82,
        "zone": "coastal_west",
    },
    {
        "id": "IND_MH_PUN",
        "name": "Pune",
        "state": "Maharashtra",
        "lat": 18.52,
        "lon": 73.85,
        "zone": "orographic_ghats",
    },
    {
        "id": "IND_MH_RAT",
        "name": "Ratnagiri",
        "state": "Maharashtra",
        "lat": 16.99,
        "lon": 73.30,
        "zone": "coastal_west",
    },
    {
        "id": "IND_MH_NAG",
        "name": "Nagpur",
        "state": "Maharashtra",
        "lat": 21.14,
        "lon": 79.08,
        "zone": "interior",
    },
    {
        "id": "IND_KA_BLR",
        "name": "Bengaluru Urban",
        "state": "Karnataka",
        "lat": 12.97,
        "lon": 77.59,
        "zone": "interior",
    },
    {
        "id": "IND_KA_DKA",
        "name": "Dakshina Kannada",
        "state": "Karnataka",
        "lat": 12.87,
        "lon": 75.00,
        "zone": "coastal_west",
    },
    {
        "id": "IND_KA_SHI",
        "name": "Shivamogga",
        "state": "Karnataka",
        "lat": 14.04,
        "lon": 75.40,
        "zone": "orographic_ghats",
    },
    {
        "id": "IND_KL_EKM",
        "name": "Ernakulam",
        "state": "Kerala",
        "lat": 9.98,
        "lon": 76.30,
        "zone": "coastal_west",
    },
    {
        "id": "IND_KL_IDK",
        "name": "Idukki",
        "state": "Kerala",
        "lat": 9.85,
        "lon": 76.95,
        "zone": "orographic_ghats",
    },
    {
        "id": "IND_KL_WYD",
        "name": "Wayanad",
        "state": "Kerala",
        "lat": 11.68,
        "lon": 76.13,
        "zone": "orographic_ghats",
    },
    {
        "id": "IND_GJ_AHM",
        "name": "Ahmedabad",
        "state": "Gujarat",
        "lat": 23.02,
        "lon": 72.57,
        "zone": "interior",
    },
    {
        "id": "IND_GJ_SUR",
        "name": "Surat",
        "state": "Gujarat",
        "lat": 21.17,
        "lon": 72.83,
        "zone": "coastal_west",
    },
    {
        "id": "IND_MP_BHO",
        "name": "Bhopal",
        "state": "Madhya Pradesh",
        "lat": 23.25,
        "lon": 77.41,
        "zone": "interior",
    },
    {
        "id": "IND_MP_IND",
        "name": "Indore",
        "state": "Madhya Pradesh",
        "lat": 22.71,
        "lon": 75.85,
        "zone": "interior",
    },
    {
        "id": "IND_MP_JAB",
        "name": "Jabalpur",
        "state": "Madhya Pradesh",
        "lat": 23.18,
        "lon": 79.98,
        "zone": "interior",
    },
    {
        "id": "IND_OD_PUR",
        "name": "Puri",
        "state": "Odisha",
        "lat": 19.81,
        "lon": 85.83,
        "zone": "coastal_west",
    },
    {
        "id": "IND_OD_BBS",
        "name": "Khordha",
        "state": "Odisha",
        "lat": 20.18,
        "lon": 85.62,
        "zone": "interior",
    },
    {
        "id": "IND_WB_KOL",
        "name": "Kolkata",
        "state": "West Bengal",
        "lat": 22.57,
        "lon": 88.36,
        "zone": "interior",
    },
    {
        "id": "IND_WB_DAR",
        "name": "Darjeeling",
        "state": "West Bengal",
        "lat": 27.04,
        "lon": 88.26,
        "zone": "orographic_ne",
    },
    {
        "id": "IND_AS_KAM",
        "name": "Kamrup",
        "state": "Assam",
        "lat": 26.18,
        "lon": 91.74,
        "zone": "orographic_ne",
    },
    {
        "id": "IND_ML_EKH",
        "name": "East Khasi Hills",
        "state": "Meghalaya",
        "lat": 25.57,
        "lon": 91.89,
        "zone": "orographic_ne",
    },
    {
        "id": "IND_DL_NDL",
        "name": "New Delhi",
        "state": "Delhi",
        "lat": 28.61,
        "lon": 77.20,
        "zone": "interior",
    },
    {
        "id": "IND_TG_HYD",
        "name": "Hyderabad",
        "state": "Telangana",
        "lat": 17.38,
        "lon": 78.48,
        "zone": "interior",
    },
    {
        "id": "IND_AP_VSK",
        "name": "Visakhapatnam",
        "state": "Andhra Pradesh",
        "lat": 17.68,
        "lon": 83.21,
        "zone": "coastal_west",
    },
    {
        "id": "IND_TN_CHE",
        "name": "Chennai",
        "state": "Tamil Nadu",
        "lat": 13.08,
        "lon": 80.27,
        "zone": "coastal_west",
    },
    {
        "id": "IND_RJ_JAI",
        "name": "Jaipur",
        "state": "Rajasthan",
        "lat": 26.91,
        "lon": 75.78,
        "zone": "interior",
    },
    {
        "id": "IND_UP_LKO",
        "name": "Lucknow",
        "state": "Uttar Pradesh",
        "lat": 26.84,
        "lon": 80.94,
        "zone": "interior",
    },
    {
        "id": "IND_BR_PAT",
        "name": "Patna",
        "state": "Bihar",
        "lat": 25.59,
        "lon": 85.13,
        "zone": "interior",
    },
    {
        "id": "IND_UK_DEH",
        "name": "Dehradun",
        "state": "Uttarakhand",
        "lat": 30.31,
        "lon": 78.03,
        "zone": "orographic_ne",
    },
    {
        "id": "IND_HP_SHI",
        "name": "Shimla",
        "state": "Himachal Pradesh",
        "lat": 31.10,
        "lon": 77.17,
        "zone": "orographic_ne",
    },
]


def make_district_polygon(lat: float, lon: float, radius: float = 0.45) -> dict[str, Any]:
    """Create a regular hexagonal boundary polygon approximation around centroid."""
    angles = np.linspace(0, 2 * np.pi, 7)
    coords = [[lon + radius * np.cos(a), lat + radius * np.sin(a)] for a in angles]
    return {"type": "Polygon", "coordinates": [coords]}


def _load_boundaries_from_geojson(
    path: Path,
    lats: np.ndarray | None = None,
    lons: np.ndarray | None = None,
) -> list[DistrictMeta]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    districts = []
    features = data.get("features", [])
    for feat in features:
        props = feat.get("properties", {})
        geom = feat.get("geometry")
        if not geom:
            continue
        poly = shape(geom)
        if not poly.is_valid:
            poly = poly.buffer(0)

        dist_id = str(
            props.get("district_id")
            or props.get("ID_2")
            or f"IND_{props.get('NAME_2', 'DIST')}"
        )
        name_val = str(
            props.get("district_name")
            or props.get("NAME_2")
            or props.get("district")
            or dist_id
        )
        state_val = str(props.get("state") or props.get("NAME_1") or "")
        centroid_lat = float(props.get("centroid_lat") or poly.centroid.y)
        centroid_lon = float(props.get("centroid_lon") or poly.centroid.x)

        cell_indices: list[tuple[int, int]] = []
        if lats is not None and lons is not None:
            minx, miny, maxx, maxy = poly.bounds
            lat_cand = np.where((lats >= miny) & (lats <= maxy))[0]
            lon_cand = np.where((lons >= minx) & (lons <= maxx))[0]
            for i in lat_cand:
                for j in lon_cand:
                    pt = Point(float(lons[j]), float(lats[i]))
                    if poly.contains(pt):
                        cell_indices.append((int(i), int(j)))

            is_subgrid = len(cell_indices) <= 1
            if len(cell_indices) == 0:
                dist_matrix = (lats[:, None] - centroid_lat) ** 2 + (lons[None, :] - centroid_lon) ** 2
                min_i, min_j = np.unravel_index(np.argmin(dist_matrix), dist_matrix.shape)
                cell_indices.append((int(min_i), int(min_j)))
        else:
            is_subgrid = False

        districts.append(
            DistrictMeta(
                district_id=dist_id,
                name=name_val,
                state=state_val,
                centroid_lat=centroid_lat,
                centroid_lon=centroid_lon,
                cell_indices=cell_indices,
                is_subgrid=is_subgrid,
                geometry=geom if isinstance(geom, dict) else mapping(poly),
            )
        )
    return districts


def _create_default_boundaries(
    lats: np.ndarray | None = None,
    lons: np.ndarray | None = None,
) -> list[DistrictMeta]:
    districts = []

    for d in DEFAULT_DISTRICTS_DATA:
        lat_val = float(d["lat"])
        lon_val = float(d["lon"])
        dist_id = str(d["id"])
        name_val = str(d["name"])
        state_val = str(d["state"])

        poly_geom = make_district_polygon(lat_val, lon_val)
        poly = shape(poly_geom)

        cell_indices: list[tuple[int, int]] = []
        if lats is not None and lons is not None:
            for i, c_lat in enumerate(lats):
                for j, c_lon in enumerate(lons):
                    pt = Point(float(c_lon), float(c_lat))
                    if poly.contains(pt):
                        cell_indices.append((i, j))

            # If sub-grid (zero cells inside polygon), find nearest grid point
            is_subgrid = len(cell_indices) <= 1
            if len(cell_indices) == 0:
                dist_matrix = (lats[:, None] - lat_val) ** 2 + (lons[None, :] - lon_val) ** 2
                min_i, min_j = np.unravel_index(np.argmin(dist_matrix), dist_matrix.shape)
                cell_indices.append((int(min_i), int(min_j)))
        else:
            is_subgrid = False

        districts.append(
            DistrictMeta(
                district_id=dist_id,
                name=name_val,
                state=state_val,
                centroid_lat=lat_val,
                centroid_lon=lon_val,
                cell_indices=cell_indices,
                is_subgrid=is_subgrid,
                geometry=poly_geom,
            )
        )

    return districts


def load_or_create_boundaries(
    boundary_path: Path | str | None = None,
    lats: np.ndarray | None = None,
    lons: np.ndarray | None = None,
) -> list[DistrictMeta]:
    """
    Load district polygons from GeoJSON (e.g. Census of India) or create standardized districts.
    Maps grid cells (lats, lons) to district boundaries via point-in-polygon assignment.
    """
    if boundary_path is not None:
        p = Path(boundary_path)
        if p.exists() and p.is_file():
            return _load_boundaries_from_geojson(p, lats, lons)

    return _create_default_boundaries(lats, lons)

