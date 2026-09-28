# Security & Privacy Policy: Project Varsha

**Document Reference:** Varsha Threat Model & Security Policy  
**Version:** 1.0.0

---

## 1. Threat Model & Privacy Posture

- **Zero Personal Data:** Varsha processes solely atmospheric physics, meteorological grids, and public administrative boundaries. No user credentials, cookies, telemetry, or personally identifiable information (PII) are stored or transmitted.
- **Air-Gapped & Offline Architecture:** The operational runtime contains zero external CDN dependencies, analytics trackers, or third-party web font calls.
- **Read-Only Data Serving:** The API server operates strictly on immutable, read-only precomputed product bundles (`products/<run_id>/`). No client request can execute unverified code, modify model weights, or write arbitrary disk files.

---

## 2. API Security Safeguards

- **Strict Input Validation:** All query parameters (`lead`, `layer`, `run_id`) are strongly validated against strict Pydantic schemas and whitelists (e.g. `lead` $\in [1, 5]$).
- **Path Traversal Protection:** Run IDs and file paths are sanitized against directory traversal patterns (`../`, `..\\`) using resolved canonical path assertions.
- **Content Security Policy (CSP):**
  ```text
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: blob:;
  worker-src blob:;
  connect-src 'self';
  frame-ancestors 'none';
  ```
- **CORS Configuration:** Restricted to configured local frontend origins.

---

## 3. Vulnerability Management

- **Automated Dependency Auditing:** CI pipelines execute `pip-audit` for Python dependencies and `npm audit` for Node.js modules. Any unresolved high or critical severity finding fails the build.
- **Secret Scanning:** Repository commits are scanned for hard-coded API tokens, credentials, or private keys.
