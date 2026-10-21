# Removes the Task Scheduler task "ERW chain worker" (scripts/register_chain_worker.ps1). A session the worker
# started keeps running until its chain ends; to stop it too, close its process (runs\chain_worker\worker.pid).
Unregister-ScheduledTask -TaskName "ERW chain worker" -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "Removed: ERW chain worker"
