$endpoints = @(
    '/healthz',
    '/api/v1/meta',
    '/api/v1/runs',
    '/api/v1/verification/summary?run=latest'
)
foreach ($ep in $endpoints) {
    $r = Invoke-WebRequest -Uri ("http://localhost:8000" + $ep) -UseBasicParsing
    Write-Host ($ep + "  =>  " + $r.StatusCode)
}
# Confirm API paths still get JSON 404 (not index.html)
$bad = Invoke-WebRequest -Uri 'http://localhost:8000/api/nonexistent' -UseBasicParsing -ErrorAction SilentlyContinue
Write-Host ("/api/nonexistent  =>  " + $bad.StatusCode + "  json=" + ($bad.Content -match 'detail'))
Write-Host "`nAll checks complete."
