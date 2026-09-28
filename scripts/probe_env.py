from typing import Any
import sys
import os
import platform
import shutil
import urllib.request
import json
import subprocess

def probe() -> None:
    results: dict[str, Any] = {}
    results["os"] = {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
    }
    results["cpu_count"] = os.cpu_count()
    
    # RAM
    ram_gb = None
    try:
        import psutil
        vm = psutil.virtual_memory()
        results["ram_total_gb"] = round(vm.total / (1024**3), 2)
        results["ram_available_gb"] = round(vm.available / (1024**3), 2)
    except ImportError:
        # On Windows, try systeminfo or ctypes
        try:
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            results["ram_total_gb"] = round(stat.ullTotalPhys / (1024**3), 2)
            results["ram_available_gb"] = round(stat.ullAvailPhys / (1024**3), 2)
        except Exception as e:
            results["ram_error"] = str(e)

    # Disk
    total, used, free = shutil.disk_usage(".")
    results["disk_total_gb"] = round(total / (1024**3), 2)
    results["disk_free_gb"] = round(free / (1024**3), 2)

    # Python
    results["python_version"] = sys.version.split()[0]
    results["python_path"] = sys.executable

    # Tools
    tools = ["uv", "pip", "node", "npm", "pnpm", "git", "docker", "playwright", "gh"]
    results["tools"] = {}
    for t in tools:
        path = shutil.which(t)
        ver = None
        if path:
            try:
                out = subprocess.run([t, "--version"], capture_output=True, text=True, timeout=5)
                ver = (out.stdout or out.stderr).strip().split("\n")[0]
            except Exception as e:
                ver = f"found at {path} (version check failed)"
        results["tools"][t] = {"installed": bool(path), "path": path, "version": ver}

    # Playwright browser capability
    # Can install browsers if node / npx / pip available
    results["playwright_capable"] = bool(shutil.which("node") or shutil.which("pip"))

    # Network tests
    urls = {
        "GitHub": "https://github.com",
        "NOAA Open Data": "https://noaa-gfs-bdp-pds.s3.amazonaws.com",
        "IMD (Pune)": "https://www.imdpune.gov.in",
        "ECMWF Open Data": "https://data.ecmwf.int",
        "NASA Earthdata": "https://urs.earthdata.nasa.gov",
        "Copernicus CDS": "https://cds.climate.copernicus.eu"
    }

    results["network"] = {}
    for name, url in urls.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
            with urllib.request.urlopen(req, timeout=5) as resp:
                results["network"][name] = {"reachable": True, "status": resp.status}
        except Exception as e:
            # Try GET if HEAD is not allowed (e.g. S3 or Cloudflare 403 on HEAD)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="GET")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    results["network"][name] = {"reachable": True, "status": resp.status}
            except Exception as e2:
                results["network"][name] = {"reachable": False, "error": str(e2)}

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    probe()
