# Energy Research Warehouse (ERW), session 233: register the weekly hunt with the Windows Task Scheduler.
#
#   powershell -ExecutionPolicy Bypass -File scripts\register_weekly_hunt.ps1            registers (or registers again)
#   powershell -ExecutionPolicy Bypass -File scripts\register_weekly_hunt.ps1 -DryRun    prints what it would register
#
# What it registers: one task, "ERW weekly hunt", that runs on the data machine every Saturday at 12:00 local time
#   <Root>\.venv\Scripts\python.exe warehouse\analysis\findings\hunt.py --weekly
# from <Root>, its output appended to runs\weekly_hunt.log. Saturday noon is after the machine's daily run and a day
# and a half before the Sunday Roundup (Sunday 23:00 UTC), so a draft approved on Saturday or Sunday can be chosen for
# it. The hunt reads tables and writes drafts to the review list (/internal/findings); it writes no warehouse table,
# calls no model and posts nothing anywhere. It reads its keys from .env by itself: nothing secret is in the task's
# arguments, and this script reads no key.
#
# A Saturday the machine was off: the task starts when the machine is next available (StartWhenAvailable). One
# instance at a time, a limit of three hours, runs on battery. From an elevated PowerShell the task runs whether or
# not anybody is logged on (principal S4U); without elevation it runs only while the current user is logged on, and
# the script says so.
#
# Idempotent: registering twice leaves one task. To remove it: scripts\unregister_weekly_hunt.ps1.
param(
  [switch]$DryRun,
  [string]$Root = (Split-Path -Parent $PSScriptRoot),
  [string]$At = "12:00"
)
$ErrorActionPreference = "Stop"
$TaskName = "ERW weekly hunt"
$py = Join-Path $Root ".venv\Scripts\python.exe"
$hunt = "warehouse\analysis\findings\hunt.py"
$log = Join-Path $Root "runs\weekly_hunt.log"

if (-not (Test-Path $py)) { Write-Output "NOT REGISTERED: $py is not there (the checkout's venv)."; exit 1 }
if (-not (Test-Path (Join-Path $Root $hunt))) { Write-Output "NOT REGISTERED: $hunt is not in $Root."; exit 1 }

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$elevated = (New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$user = $identity.Name

$argument = '/c ""' + $py + '" ' + $hunt + ' --weekly >> "' + $log + '" 2>&1"'
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $argument -WorkingDirectory $Root
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At $At
if ($elevated) {
  $principal = New-ScheduledTaskPrincipal -UserId $user -LogonType S4U -RunLevel Limited
  $when = "every Saturday at $At local time, whether or not anybody is logged on (elevated shell)"
} else {
  $principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
  $when = "every Saturday at $At local time, ONLY while $user is logged on. This shell is not elevated: run this script again from an elevated PowerShell for a task that runs with nobody logged on"
}
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 3) -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Write-Output "Task:      $TaskName"
Write-Output "Runs:      cmd.exe $argument"
Write-Output "From:      $Root"
Write-Output "Starts:    $when"
Write-Output "Settings:  a missed Saturday starts when the machine is next available, a limit of three hours, one instance, runs on battery"
if ($DryRun) {
  Write-Output "DRY RUN: nothing was registered."
  exit 0
}

New-Item -ItemType Directory -Force -Path (Join-Path $Root "runs") | Out-Null
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "ERW: the weekly hunt for deeper findings (session 233): runs the pattern library, drafts what passes its tests to /internal/findings. Remove with scripts\unregister_weekly_hunt.ps1." -Force | Out-Null
$task = Get-ScheduledTask -TaskName $TaskName
$info = Get-ScheduledTaskInfo -TaskName $TaskName
$count = @(Get-ScheduledTask | Where-Object { $_.TaskName -eq $TaskName }).Count
Write-Output "REGISTERED: $count task named '$TaskName', state $($task.State), next run $($info.NextRunTime). Log: $log"
exit 0
