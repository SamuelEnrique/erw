# Registers the Task Scheduler task "ERW chain worker" on this machine: scripts/chain_worker.ps1 every 10 minutes
# while the current user is logged on (docs/machines.md, "The chain worker"). No elevation needed. Run from the
# repository root: powershell -ExecutionPolicy Bypass -File scripts\register_chain_worker.ps1
# Remove it with scripts\unregister_chain_worker.ps1.
param(
    [string]$Root = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)),
    [string]$Model = "opus"
)
$script = Join-Path $Root "scripts\chain_worker.ps1"
if (-not (Test-Path $script)) { throw "not found: $script" }
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument ("-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`" -Root `"$Root`" -Model $Model") `
    -WorkingDirectory $Root
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 10)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) -MultipleInstances IgnoreNew -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName "ERW chain worker" -Action $action -Trigger $trigger -Settings $settings `
    -Principal $principal -Force | Out-Null
Start-ScheduledTask -TaskName "ERW chain worker"
Get-ScheduledTask -TaskName "ERW chain worker" | Select-Object TaskName, State
Write-Host "Registered: every 10 minutes while $env:USERNAME is logged on; root $Root; model $Model."
Write-Host "Log: $Root\runs\chain_worker\worker.log"
