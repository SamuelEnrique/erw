# Energy Research Warehouse (ERW), session 181: register the findings worker with the Windows Task Scheduler.
#
#   powershell -ExecutionPolicy Bypass -File scripts\register_findings_worker.ps1            registers (or registers again)
#   powershell -ExecutionPolicy Bypass -File scripts\register_findings_worker.ps1 -DryRun    prints what it would register
#
# What it registers: one task, "ERW findings worker", that runs the MAIN copy's worker
#   C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe warehouse\analysis\findings\worker.py --loop 60
# from C:\Users\lossa\Documents\erw, its output appended to runs\findings_worker.log. The worker takes the queued
# requests of /analysis (and the scanner's daily request), runs them on this machine's full histories and writes the
# cards. It reads its keys from .env by itself: nothing secret is in the task's arguments, and this script reads no key.
#
# When it starts: at log-on of the current user, always. At startup as well (before anybody logs on) only from an
# ELEVATED PowerShell: a task that runs with nobody logged on needs a principal of type S4U, and Windows lets only an
# administrator register one. Without elevation the script registers the log-on trigger alone, says so, and exits 0:
# the worker then starts when you log on after a restart, which on a laptop that logs on by itself is the same thing.
#
# It restarts on failure (every minute, 999 times), has no time limit, never runs twice (MultipleInstances IgnoreNew,
# and the worker's own lock file refuses a second instance), starts when available and runs on battery.
#
# Idempotent: registering twice leaves one task (Register-ScheduledTask -Force replaces the task of that name).
# To remove it: scripts\unregister_findings_worker.ps1. To see it: Get-ScheduledTask -TaskName "ERW findings worker",
# or  python warehouse\analysis\findings\worker.py --status.
param(
  [switch]$DryRun,
  [string]$Root = "C:\Users\lossa\Documents\erw",
  [int]$LoopSeconds = 60
)
$ErrorActionPreference = "Stop"
$TaskName = "ERW findings worker"
$py = Join-Path $Root ".venv\Scripts\python.exe"
$worker = "warehouse\analysis\findings\worker.py"
$log = Join-Path $Root "runs\findings_worker.log"

if (-not (Test-Path $py)) { Write-Output "NOT REGISTERED: $py is not there (the main copy's venv)."; exit 1 }
if (-not (Test-Path (Join-Path $Root $worker))) { Write-Output "NOT REGISTERED: $worker is not in $Root."; exit 1 }

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$elevated = (New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$user = $identity.Name

# cmd.exe appends the worker's output to the log; the worker's own exit code is cmd's, so a failure is seen and restarted
$argument = '/c ""' + $py + '" ' + $worker + ' --loop ' + $LoopSeconds + ' >> "' + $log + '" 2>&1"'
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $argument -WorkingDirectory $Root
$triggers = @(New-ScheduledTaskTrigger -AtLogOn -User $user)
if ($elevated) {
  $triggers += New-ScheduledTaskTrigger -AtStartup
  $principal = New-ScheduledTaskPrincipal -UserId $user -LogonType S4U -RunLevel Limited
  $when = "at log-on of $user and at startup (elevated shell: the task runs whether or not anybody is logged on)"
} else {
  $principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
  $when = "at log-on of $user ONLY. This shell is not elevated, so the startup trigger was left out: run this script again from an elevated PowerShell to add it"
}
$settings = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Write-Output "Task:      $TaskName"
Write-Output "Runs:      cmd.exe $argument"
Write-Output "From:      $Root"
Write-Output "Starts:    $when"
Write-Output "Settings:  restart on failure every minute (999 times), no time limit, one instance (IgnoreNew), start when available, runs on battery"
if ($DryRun) {
  Write-Output "DRY RUN: nothing was registered."
  exit 0
}

New-Item -ItemType Directory -Force -Path (Join-Path $Root "runs") | Out-Null
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $triggers -Principal $principal -Settings $settings -Description "ERW: takes the queued requests of /analysis and runs them on this machine (session 181). Remove with scripts\unregister_findings_worker.ps1." -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 3
$task = Get-ScheduledTask -TaskName $TaskName
$count = @(Get-ScheduledTask | Where-Object { $_.TaskName -eq $TaskName }).Count
Write-Output "REGISTERED: $count task named '$TaskName', state $($task.State). Log: $log"
exit 0
