# Energy Research Warehouse (ERW), session 181: remove the findings worker from the Windows Task Scheduler.
#
#   powershell -ExecutionPolicy Bypass -File scripts\unregister_findings_worker.ps1
#
# Stops the task "ERW findings worker" if it is running and unregisters it. Nothing else is removed: the log
# (runs\findings_worker.log), the state file and every queued request stay; a request that waits is taken by the next
# worker that runs (scripts\register_findings_worker.ps1, or  python warehouse\analysis\findings\worker.py --once).
# Safe when the task is absent: it says so and exits 0. An elevated shell is needed only if the task was registered
# from one (with the startup trigger).
param(
  [string]$Root = "C:\Users\lossa\Documents\erw"
)
$ErrorActionPreference = "Stop"
$TaskName = "ERW findings worker"

$task = Get-ScheduledTask | Where-Object { $_.TaskName -eq $TaskName }
if (-not $task) {
  Write-Output "No task named '$TaskName' is registered: nothing to remove."
  exit 0
}
# ask the worker to finish the request in hand first: it reads this file at its next turn (within a second) and stops
$stop = Join-Path $Root "runs\findings_worker.stop"
if (Test-Path (Join-Path $Root "runs\findings_worker.lock")) {
  New-Item -ItemType File -Force -Path $stop | Out-Null
  Start-Sleep -Seconds 5
}
if ((Get-ScheduledTask -TaskName $TaskName).State -eq "Running") {
  Stop-ScheduledTask -TaskName $TaskName
}
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
if (Test-Path $stop) { Remove-Item -Force $stop }
Write-Output "UNREGISTERED: '$TaskName'. The log, the state file and the queue are as they were."
exit 0
