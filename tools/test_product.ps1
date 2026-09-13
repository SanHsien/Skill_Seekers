[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $venvPython) {
    $pythonExe = $venvPython
} else {
    $pythonExe = (Get-Command python -ErrorAction Stop).Source
}

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = (Join-Path $repoRoot "src")

Write-Host "==> Product Smoke Test: skill_seekers import and version"
& $pythonExe -c "import sys; sys.path.insert(0, 'src'); import skill_seekers; print('skill_seekers version:', getattr(skill_seekers, '__version__', 'unknown'))"
if ($LASTEXITCODE -ne 0) { throw "Import test failed" }

Write-Host "==> Product Smoke Test: CLI --version"
& $pythonExe -m skill_seekers.cli.main --version
if ($LASTEXITCODE -ne 0) { throw "CLI --version failed" }

Write-Host "==> Product Smoke Test: CLI --help"
& $pythonExe -m skill_seekers.cli.main --help | Out-Null
if ($LASTEXITCODE -ne 0) { throw "CLI --help failed" }

Write-Host "==> Product Smoke Test: CLI doctor --help"
& $pythonExe -m skill_seekers.cli.doctor --help | Out-Null
if ($LASTEXITCODE -ne 0) { throw "CLI doctor --help failed" }

Write-Host "==> Product Smoke Test: CLI config --help"
& $pythonExe -m skill_seekers.cli.config_command --help | Out-Null
if ($LASTEXITCODE -ne 0) { throw "CLI config --help failed" }

Write-Host "PRODUCT SMOKE TEST GREEN"
