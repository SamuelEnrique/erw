# Energy Research Warehouse (ERW), session 185: remove the data machine's daily run from the Windows Task Scheduler.
#
#   powershell -ExecutionPolicy Bypass -File scripts\unregister_data_machine_daily.ps1
#
# Unregisters the task "ERW data machine daily". A run in progress is not stopped: it finishes under the data lock
# and releases it (stopping it here would leave the lock to expire by itself). Nothing else is removed: the log
# (runs\data_machine_daily.out), the tables, the saved workbooks and every commit stay. Safe when the task is absent:
# it says so and exits 0.
$ErrorActionPreference = "Stop"
$TaskName = "ERW data machine daily"

$task = Get-ScheduledTask | Where-Object { $_.TaskName -eq $TaskName }
if (-not $task) {
  Write-Output "No task named '$TaskName' is registered: nothing to remove."
  exit 0
}
if ($task.State -eq "Running") {
  Write-Output "'$TaskName' is running now. It is left to finish (it holds the data lock); run this again when it has ended."
  exit 1
}
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
Write-Output "UNREGISTERED: '$TaskName'. The log, the tables and the saved workbooks are as they were."
exit 0
