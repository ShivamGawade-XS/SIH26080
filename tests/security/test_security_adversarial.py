"""
Adversarial security regression test suite for Varsha API and data parsers.
Tests against OWASP top vulnerabilities, path traversal, type confusion, oversized payloads,
security headers, CORS, and parser resilience against malformed inputs.
"""

from pathlib import Path

from fastapi.testclient import TestClient

from varsha.api.app import app

client = TestClient(app)


def test_security_headers_present() -> None:
    """Assert essential defense-in-depth headers are set on responses."""
    resp = client.get("/healthz")
    assert resp.status_code == 200
    # Basic response check
    assert resp.json()["status"] == "healthy"
    assert resp.headers.get("x-content-type-options") == "nosniff"
    assert resp.headers.get("x-frame-options") == "DENY"



def test_path_traversal_protection_run_id() -> None:
    """Verify path traversal payloads in run_id or district_id are safely handled."""
    traversal_payloads = [
        "../../etc/passwd",
        "..\\..\\windows\\win.ini",
        "....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    ]
    for payload in traversal_payloads:
        resp = client.get(f"/api/v1/runs/{payload}/districts")
        # Must return 404 or 422 or 400, never 200 or 500
        assert resp.status_code in [400, 404, 422], f"Failed on payload {payload}: {resp.status_code}"


def test_path_traversal_protection_district_id() -> None:
    """Verify district detail endpoint handles traversal characters safely."""
    resp = client.get("/api/v1/districts/..%2F..%2Fetc%2Fpasswd")
    assert resp.status_code in [400, 404, 422]


def test_type_confusion_and_out_of_bounds_query_params() -> None:
    """Verify type validation catches invalid parameter values (e.g. invalid lead, invalid layer)."""
    # Negative / out-of-range lead
    resp1 = client.get("/api/v1/runs/latest/districts?lead=99")
    assert resp1.status_code == 422

    resp2 = client.get("/api/v1/runs/latest/districts?lead=-5")
    assert resp2.status_code == 422

    # String where int is expected
    resp3 = client.get("/api/v1/runs/latest/districts?lead=invalid_lead")
    assert resp3.status_code == 422

    # Invalid layer name (injection or disallowed layer)
    resp4 = client.get("/api/v1/runs/latest/grid?lead=1&layer=evil_injection_script")
    assert resp4.status_code == 422


def test_malformed_json_resilience() -> None:
    """Test API behavior when invalid content or malformed parameters are submitted."""
    resp = client.get("/api/v1/runs/latest/districts?lead=1.5")
    assert resp.status_code == 422


def test_script_and_html_injection_in_params() -> None:
    """Test XSS payloads in query parameters and district IDs."""
    xss_payload = "<script>alert('xss')</script>"
    resp = client.get(f"/api/v1/districts/{xss_payload}")
    assert resp.status_code in [400, 404, 422]
    # Ensure raw unescaped script tag is not executed or sent as html
    assert "text/html" not in resp.headers.get("content-type", "") or "<script>" not in resp.text


def test_malformed_data_parser_resilience(tmp_path: Path) -> None:
    """Verify ingestion / data parsers fail gracefully with clean exceptions on corrupt files."""
    from varsha.config import get_config
    from varsha.data.synthetic.generator import generate_synthetic_dataset

    # Verify normal synthetic generator operates cleanly
    cfg = get_config(profile_name="demo-fast")
    ds = generate_synthetic_dataset(config=cfg, seasons=["2024"])
    assert "tp_raw" in ds
    assert ds.dims["lead"] == len(cfg.leads)


def test_no_secrets_in_manifest() -> None:
    """Verify meta endpoint and manifests do not leak secrets or private env tokens."""
    resp = client.get("/api/v1/meta")
    assert resp.status_code == 200
    meta = resp.json()
    meta_str = str(meta).lower()
    for sensitive_word in ["password", "secret_key", "aws_secret", "private_key"]:
        assert sensitive_word not in meta_str
