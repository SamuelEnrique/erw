# Energy Research Warehouse (ERW), session 185: register the data machine's daily run with the Windows Task Scheduler.
#
#   powershell -ExecutionPolicy Bypass -File scripts\register_data_machine_daily.ps1             registers (or registers again)
#   powershell -ExecutionPolicy Bypass -File scripts\register_data_machine_daily.ps1 -DryRun     prints what it would register
#   powershell -ExecutionPolicy Bypass -File scripts\register_data_machine_daily.ps1 -Disabled   registers it switched off
#
# What it registers: one task, "ERW data machine daily", that runs, every day at 10:00 local time,
#   warehouse/run_data_machine.sh under warehouse/lock.py run (the data lock, waiting up to 60 minutes for it)
# from the checkout that holds the tables and the saved workbooks, its output appended to runs\data_machine_daily.out.
# It is the command of docs/machines.md, "The data machine's daily run" (session 149): 10:00 Pacific is 17:00 UTC in
# summer and 18:00 UTC in winter, both after the GitHub runner's daily run (14:00 UTC, the lock held until about 16:00).
# The run reads its keys from .env by itself: nothing secret is in the task's arguments, and this script reads no key.
#
# -Root is the checkout the task runs in. Its default is the checkout this script is in. Run from a second working
# copy (a git worktree), name the data checkout: -Root "C:\Users\Shared\Documents\erw".
#
# IT REFUSES TO REGISTER A RUN THAT WOULD COUNT FROM ZERO. warehouse\raw\ercot_zone_prices\ holds the count against
# ERCOT's ceiling of 3,000,000 rows. Without its manifest the refresh would ask ERCOT again for every workbook and
# count from zero (session 184). So without warehouse\raw\ercot_zone_prices\manifest.csv the script registers nothing,
# unless -Disabled: then the task is registered switched off, and Enable-ScheduledTask turns it on once the folder is
# there. It also refuses when the machine's role is not "data", or a price history is not in warehouse\output.
#
# A push that needs a sign-in fails at once and never waits. The task sets GCM_INTERACTIVE=never and
# GIT_TERMINAL_PROMPT=0 for the run, so on a machine nobody has signed in to GitHub on, Git Credential Manager does
# not open a window that nobody sees while the run holds the data lock: the push fails, the run records it
# (dm_commit failed, in erw_health) and ends, and the commit waits on main here.
#
# When it runs: only while the current user is logged on (a task that runs with nobody logged on needs a principal of
# type S4U, which only an administrator may register, and under S4U git finds no saved sign-in to push with). No
# elevation is needed. It does not start a missed run late (a run started hours late could hold the lock when the
# runner's daily run wants it), never runs twice at once, is stopped after six hours, and runs on battery.
#
# Idempotent: registering twice leaves one task. To remove it: scripts\unregister_data_machine_daily.ps1, or
# schtasks /Delete /TN "ERW data machine daily". To see it: Get-ScheduledTask -TaskName "ERW data machine daily".
param(
  [switch]$DryRun,
  [switch]$Disabled,
  [string]$Root = (Split-Path -Parent $PSScriptRoot),
  [string]$At = "10:00",
  [string]$Bash = "C:\Program Files\Git\bin\bash.exe"
)
$ErrorActionPreference = "Stop"
$TaskName = "ERW data machine daily"
$py = Join-Path $Root ".venv\Scripts\python.exe"
$script = Join-Path $Root "warehouse\run_data_machine.sh"
$manifest = Join-Path $Root "warehouse\raw\ercot_zone_prices\manifest.csv"

if (-not (Test-Path $Bash)) { Write-Output "NOT REGISTERED: $Bash is not there (Git for Windows)."; exit 1 }
if (-not (Test-Path $py)) { Write-Output "NOT REGISTERED: $py is not there (the checkout's venv)."; exit 1 }
if (-not (Test-Path $script)) { Write-Output "NOT REGISTERED: warehouse\run_data_machine.sh is not in $Root."; exit 1 }
$role = (& $py (Join-Path $Root "warehouse\lock.py") role) -join " "
if ($role -notmatch '"role":\s*"data"') { Write-Output "NOT REGISTERED: this machine's role is not data ($role)."; exit 1 }
foreach ($t in @("ercot_all_hub_prices_history", "ercot_zone_prices_history", "iso_zone_prices_history")) {
  if (-not (Test-Path (Join-Path $Root "warehouse\output\$t.csv"))) { Write-Output "NOT REGISTERED: warehouse\output\$t.csv is not here; the run would refuse."; exit 1 }
}
$counted = Test-Path $manifest
if (-not $counted -and -not $Disabled) {
  Write-Output "NOT REGISTERED: $manifest is not there. The refresh would ask ERCOT for every workbook again and count from zero. Restore warehouse\raw first, or register it switched off with -Disabled."
  exit 1
}

# Git Bash paths: C:\Users\x\erw -> /c/Users/x/erw
$unixRoot = "/" + $Root.Substring(0, 1).ToLower() + ($Root.Substring(2) -replace "\\", "/")
$inner = "cd '$unixRoot' && GCM_INTERACTIVE=never GIT_TERMINAL_PROMPT=0 .venv/Scripts/python.exe warehouse/lock.py run --task 'data machine daily' --wait 60 -- bash warehouse/run_data_machine.sh >> runs/data_machine_daily.out 2>&1"
$argument = '-lc "' + $inner + '"'

$user = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$action = New-ScheduledTaskAction -Execute $Bash -Argument $argument -WorkingDirectory $Root
$trigger = New-ScheduledTaskTrigger -Daily -At $At
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 6) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
if ($Disabled) { $settings.Enabled = $false }

$zone = (Get-TimeZone).Id
Write-Output "Task:      $TaskName"
Write-Output "Runs:      $Bash $argument"
Write-Output "From:      $Root"
Write-Output "Starts:    every day at $At local time ($zone), while $user is logged on"
Write-Output "Settings:  one instance (IgnoreNew), stopped after six hours, a missed run is not started late, runs on battery"
Write-Output "Counted:   warehouse\raw\ercot_zone_prices\manifest.csv is $(if ($counted) { 'here' } else { 'NOT here' })"
if ($Disabled) { Write-Output "Switched:  OFF (-Disabled). Turn it on with: Enable-ScheduledTask -TaskName `"$TaskName`"" }
if ($DryRun) {
  Write-Output "DRY RUN: nothing was registered."
  exit 0
}

New-Item -ItemType Directory -Force -Path (Join-Path $Root "runs") | Out-Null
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "ERW: the data machine's daily run, warehouse/run_data_machine.sh under the data lock (sessions 149 and 185). Remove with scripts\unregister_data_machine_daily.ps1." -Force | Out-Null
$task = Get-ScheduledTask -TaskName $TaskName
$info = $task | Get-ScheduledTaskInfo
$count = @(Get-ScheduledTask | Where-Object { $_.TaskName -eq $TaskName }).Count
$next = if ($info.NextRunTime) { $info.NextRunTime.ToUniversalTime().ToString("yyyy-MM-dd HH:mm") + " UTC" } else { "none (switched off)" }
Write-Output "REGISTERED: $count task named '$TaskName', state $($task.State). Next run: $next. Log: $(Join-Path $Root 'runs\data_machine_daily.out')"
exit 0
