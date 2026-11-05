# The chain worker: keeps a machine running the chain queue (docs/machines.md, "The chain worker").
# Written by the owner on 21 October 2026. Run by the Task Scheduler task "ERW chain worker" every 10 minutes while
# the user is logged on (register_chain_worker.ps1). Each run: if no worker-started Claude Code session is alive and
# queue/next holds a file this machine would take, start one Claude Code session, non-interactive, that takes the
# file and runs it as a chain, and wait for it to end. Nothing else: no emails, no health rows (the chain's own
# steps write those).
param(
    [string]$Root = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)),
    [string]$Model = "opus"
)
$ErrorActionPreference = "Continue"
$log = Join-Path $Root "runs\chain_worker"
New-Item -ItemType Directory -Force -Path $log | Out-Null
$lock = Join-Path $log "worker.pid"
$stamp = Get-Date -Format "yyyyMMddTHHmmss"
function Note($s) { Add-Content -Path (Join-Path $log "worker.log") -Value ("{0} {1}" -f (Get-Date -Format "s"), $s) }

# 1. One session at a time: a live PID in worker.pid means a session this worker started is still running.
if (Test-Path $lock) {
    $old = Get-Content $lock -ErrorAction SilentlyContinue
    if ($old -and (Get-Process -Id ([int]$old) -ErrorAction SilentlyContinue)) { exit 0 }
    Remove-Item $lock -Force -ErrorAction SilentlyContinue
    Note "stale lock removed (pid $old)"
}

# 1b. A Claude Code session on this machine (interactive or worker-started) is left alone while it shows work: a commit
#     in the main checkout or any worktree within the last 30 minutes. A session open with no commit for 30 minutes is
#     stalled (waiting for a time of day, a lock, a person): it is closed, and a fresh session takes the chain from its
#     reports. The owner's rule of 21 October: no machine sits idle; every session's work is on a pushed branch.
$procs = Get-Process -Name "claude" -ErrorAction SilentlyContinue
if ($procs) {
    $logs = @(Join-Path $Root ".git\logs\HEAD")
    $wt = Join-Path $Root ".git\worktrees"
    if (Test-Path $wt) { $logs += Get-ChildItem $wt -Directory | ForEach-Object { Join-Path $_.FullName "logs\HEAD" } }
    $newest = Get-Date "2000-01-01"
    foreach ($f in $logs) { if (Test-Path $f) { $t = (Get-Item $f).LastWriteTime; if ($t -gt $newest) { $newest = $t } } }
    $quiet = ((Get-Date) - $newest).TotalMinutes
    if ($quiet -lt 30) { exit 0 }
    Note ("a Claude Code session has shown no commit for {0:N0} minutes: closing it" -f $quiet)
    $procs | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 10
}

Set-Location $Root
$py = Join-Path $Root ".venv\Scripts\python.exe"

# 2. The queue, as it stands on main. No session is running (step 1b), so the checkout is put back on main first;
#    a switch or pull that fails (local changes in the way) is left alone and the dry run reads what is there.
& git switch --quiet main 2>$null | Out-Null
& git pull --ff-only --quiet origin main 2>$null | Out-Null

# 3. Would this machine take a file? (--dry-run moves, commits, writes and sends nothing; exit 0 yes, 3 nothing waits)
& $py scripts\chain_queue.py next --dry-run *> (Join-Path $log "$stamp.dryrun.txt")
if ($LASTEXITCODE -ne 0) { exit 0 }

# 4. Start one session and wait for it. The reaper is off so a long build is not killed for memory.
$env:CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP = "1"
$prompt = "Run .venv\Scripts\python.exe scripts\chain_queue.py next and run the file it prints as a chain, unattended, " +
          "starting with its first session's precheck. Do not stop to ask at any point: a reversible choice goes under " +
          "'Decisions made without you', an irreversible one under 'For Samuel's ruling', undone. When the chain's last " +
          "session's queue step prints another file, run that one the same way. Stop only when the queue step exits 3."
$args = @("/c", "claude", "-p", ('"' + $prompt + '"'), "--permission-mode", "bypassPermissions", "--model", $Model)
Note "starting a session (model $Model), log $stamp"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList $args -WorkingDirectory $Root -PassThru -NoNewWindow `
        -RedirectStandardOutput (Join-Path $log "$stamp.out") -RedirectStandardError (Join-Path $log "$stamp.err")
$p.Id | Set-Content $lock
$p.WaitForExit()
Note ("session ended, exit {0}, log {1}" -f $p.ExitCode, $stamp)
Remove-Item $lock -Force -ErrorAction SilentlyContinue
exit 0
