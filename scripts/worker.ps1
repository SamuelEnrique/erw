# ERW: the queue worker (session 59). Windows PowerShell wrapper of scripts/worker.py; arguments pass through.
# Runs until stopped (Ctrl+C); docs/machines.md says how to start it at logon.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
Set-Location $root
& $py (Join-Path $root "scripts\worker.py") @args
exit $LASTEXITCODE
