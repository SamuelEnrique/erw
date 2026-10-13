# Energy Research Warehouse (ERW), session 233: remove the weekly hunt's scheduled task.
#
#   powershell -ExecutionPolicy Bypass -File scripts\unregister_weekly_hunt.ps1
#
# It removes the task "ERW weekly hunt" (scripts\register_weekly_hunt.ps1) and nothing else: the drafts already in the
# review list, runs\hunt\ and runs\weekly_hunt.log stay. A hunt that is running is not stopped. Exit 0 when the task
# is gone, whether or not it was there.
$ErrorActionPreference = "Stop"
$TaskName = "ERW weekly hunt"
$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($null -eq $task) {
  Write-Output "No task named '$TaskName' is registered: nothing to remove."
  exit 0
}
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
Write-Output "REMOVED: the task '$TaskName'."
exit 0
