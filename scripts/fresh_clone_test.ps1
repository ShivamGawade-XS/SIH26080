# Fresh Clone Verification Test Script (Windows PowerShell)
$ErrorActionPreference = "Stop"

$tempDir = Join-Path $env:TEMP ("varsha_test_" + [System.Guid]::NewGuid().ToString().Substring(0,8))
Write-Host "Creating fresh test directory at $tempDir..."
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

try {
    Write-Host "Copying repo files to test directory..."
    Copy-Item -Path "." -Destination $tempDir -Recurse -Exclude @("node_modules", "web/node_modules", ".git", ".pytest_cache", "products", "data/interim")

    Set-Location $tempDir

    Write-Host "Running demo-fast pipeline in fresh workspace..."
    python -m varsha.cli data synth --profile demo-fast
    python -m varsha.cli label --profile demo-fast
    python -m varsha.cli train --profile demo-fast
    python -m varsha.cli run --profile demo-fast
    python -m varsha.cli report --latest

    Write-Host "Running unit and API pytest suites..."
    python -m pytest tests/unit tests/api -v

    Write-Host "[SUCCESS] Fresh workspace verification passed completely!"
} finally {
    Set-Location -Path $PSScriptRoot\..
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $tempDir
}
