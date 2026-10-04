# ERW: set up a Windows machine (session 59). docs/machines.md.
#
#   powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -Role data -Name home-laptop
#   powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -Role code -Name portable-laptop -KeepAwake -Worker
#
# Checks git, Python, Node and Claude Code; makes .venv and installs the Python requirements; installs the site's packages;
# checks that .env names every key the role needs (never prints a value); sets the machine's role; syncs from the cloud.
# Keep-awake (a data machine by default, a code machine with -KeepAwake): the machine never sleeps or hibernates while
# plugged in, so a run is not cut off; on battery the power plan is unchanged. -Worker registers "ERW worker" in Task
# Scheduler to start scripts\worker.ps1 at logon and restart it if it stops. -SkipSite, -SkipSync skip those steps.
param(
  [Parameter(Mandatory = $true)][ValidateSet("data", "code")][string]$Role,
  [string]$Name = $env:COMPUTERNAME.ToLower(),
  [switch]$KeepAwake,
  [switch]$Worker,
  [switch]$SkipSite,
  [switch]$SkipSync
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$problems = @()
function Step($m) { Write-Host "== $m" }

Step "tools"
foreach ($t in @("git", "python", "node", "npm")) {
  if (-not (Get-Command $t -ErrorAction SilentlyContinue)) { $problems += "$t is not installed or not on PATH" }
}
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
  $problems += "Claude Code is not installed (npm install -g @anthropic-ai/claude-code, then run claude once to sign in); the worker needs it"
}
if ($problems.Count -gt 0 -and -not (Get-Command python -ErrorAction SilentlyContinue)) { $problems | ForEach-Object { Write-Host "  MISSING: $_" }; exit 1 }

Step "Python environment (.venv)"
$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { python -m venv .venv }
$ver = & $py -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"
& $py -m pip install -q --upgrade pip
if ($ver -eq "3.14") { & $py -m pip install -q --no-deps -r requirements-py314.txt } else { & $py -m pip install -q -r requirements.txt }
& $py -m pip install -q --no-deps -e package   # the erw client, which the package tests import (session 77)
Write-Host "  Python $ver, requirements installed"

if (-not $SkipSite) {
  Step "site packages"
  Push-Location site; npm ci --silent; Pop-Location
}

Step ".env"
$need = @("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_ANON_KEY")
if ($Role -eq "data") { $need += @("SUPABASE_DB_URL", "EIA_API_KEY", "REDIVIS_API_TOKEN", "REDIVIS_OWNER", "ANTHROPIC_API_KEY") }
if (-not (Test-Path ".env")) { $problems += ".env is missing: copy it from the password manager into $root" }
else {
  $have = (Get-Content .env | Where-Object { $_ -match '^[A-Z_][A-Z0-9_]*=.+' } | ForEach-Object { ($_ -split '=', 2)[0] })
  foreach ($k in $need) { if ($have -notcontains $k) { $problems += ".env has no value for $k (needed by a $Role machine)" } }
  Write-Host "  $($need.Count) keys checked (values not shown)"
}

Step "role"
& $py warehouse\lock.py role $Role --name $Name

if (-not $SkipSync) {
  Step "sync"
  if ($Role -eq "data") { & $py scripts\sync.py } else { & $py scripts\sync.py --check }
}

if ($Role -eq "data" -or $KeepAwake) {
  Step "keep awake while plugged in"
  powercfg /change standby-timeout-ac 0
  powercfg /change hibernate-timeout-ac 0
  Write-Host "  sleep and hibernate on AC power: never (on battery: unchanged)"
}

if ($Worker) {
  Step "worker at logon"
  $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$root\scripts\worker.ps1`"" -WorkingDirectory $root
  $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
  $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 5) -ExecutionTimeLimit (New-TimeSpan -Days 0)
  Register-ScheduledTask -TaskName "ERW worker" -Action $action -Trigger $trigger -Settings $settings -Description "ERW queue worker (docs/machines.md)" -Force | Out-Null
  Write-Host "  registered: Task Scheduler, ERW worker (stop: Stop-ScheduledTask 'ERW worker'; remove: Unregister-ScheduledTask 'ERW worker')"
}

if ($problems.Count -gt 0) {
  Write-Host "== not ready:"
  $problems | ForEach-Object { Write-Host "  - $_" }
  exit 1
}
Write-Host "== ready: $Name is a $Role machine"
