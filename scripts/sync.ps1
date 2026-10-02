# ERW: sync this machine from the cloud (session 59). Windows PowerShell wrapper of scripts/sync.py; arguments pass through.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
& $py (Join-Path $root "scripts\sync.py") @args
exit $LASTEXITCODE
