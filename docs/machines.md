# Machines

How the Energy Research Warehouse (ERW) runs on several machines at once without two of them writing the warehouse at the same
time, and without anyone having to remember a schedule (session 59). The pieces are a role per machine, a data lock, the
schedule in the database, code work on branches merged by a check, and a queue of tasks that workers take.

## The machines and their roles

Every machine has one setting, its **role**, in `.erw/machine.json` (not in git):

| Role | What it does | What it may not do |
|---|---|---|
| `data` | pulls sources, writes `warehouse/output`, loads Supabase, uploads Redivis drafts, writes the archive | write without the data lock (every data writer refuses) |
| `code` | the site, docs, tests, methods, derived pages from data already loaded | take the data lock, so it writes no warehouse data |

| Machine | Role | Notes |
|---|---|---|
| Home laptop | `data` (from session 59) | holds the raw files (`warehouse/raw/`, several GB) |
| Portable laptop | `code` | may close at any time: whatever task it holds survives (see "Interruption") |
| Lab machine | `data` (from the week after session 59) | `scripts/setup.ps1 -Role data` |
| GitHub Actions | `data` | the daily job and the weekly vacuum take the lock like any machine, named `github:<workflow>#<run id>` |

Switching a machine is one command: `python warehouse/lock.py role data` (or `code`). `python warehouse/lock.py role` shows
the current setting. `ERW_ROLE=data` in the environment overrides the file for one command.

## Setting up a machine

```powershell
# Windows
git clone https://github.com/SamuelEnrique/erw.git; cd erw
copy-item <the .env from a password manager> .env
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -Role data -Name home-laptop
```

```bash
# macOS or Linux
git clone https://github.com/SamuelEnrique/erw.git && cd erw
cp <the .env from a password manager> .env
bash scripts/setup.sh --role code --name portable-laptop
```

Setup checks git, Python, Node and Claude Code; makes `.venv` and installs `requirements.txt` (on Python 3.14,
`requirements-py314.txt` with `--no-deps`); installs the site's packages; checks that `.env` names every key the role needs
(never printing a value); sets the role; runs the sync; and, on Windows, keeps the machine awake while plugged in (a data
machine by default; a code machine with `-KeepAwake`), so a run started in the evening is not cut off by sleep. On battery
the power plan is unchanged. `-Worker` also registers the worker to start at logon (Task Scheduler).

## Sync: the cloud is the source of truth

`scripts/sync.py` (`sync.ps1`, `sync.sh`) starts every session on every machine:

1. **git**: on `main` with no uncommitted tracked changes, a fast-forward to `origin/main` (a merge if local commits exist;
   never a force or a rebase). On another branch it fetches and reports.
2. **the tables**: every table in `warehouse/metadata/coverage.csv` against the local CSV's rows. A table missing here is
   restored from its Redivis dataset (the public one or the internal one, as coverage's license says), with its provenance
   header from Redivis's `erw_headers` table, and checked against Redivis's row count. A table present with another row
   count is reported (a data machine may hold rows newer than the last upload); `--refresh` replaces it. `--check` only
   reports.

The archive (`warehouse/archive/`, and the private Supabase Storage bucket `erw-archive`) holds every row ever written, by
month; `python warehouse/archive/restore.py <table>` rebuilds a table Redivis lacks. Raw source files stay on the data
machine that downloaded them: they are too large for any copy the ERW pays nothing for, and every table records the URL
it came from.

### Cloud copies

Measured 2026-10-02 (session 59):

| Copy | What | Where | Size | Limit | Monthly cost |
|---|---|---|---|---|---|
| Code, metadata, news tables | git | GitHub, `SamuelEnrique/erw`, public | 172 MB | GitHub recommends under 1 GB, 5 GB strongly; files under 100 MB | USD 0 (public repository; Actions minutes free) |
| Every public table, as last uploaded | Redivis draft | `samuelca.energy_research_warehouse` (81 tables) | 2.79 GB | not reported by Redivis's API; check the account page | USD 0 so far |
| Every internal table (PJM, licensed) | Redivis draft | `samuelca.energy_research_warehouse_internal` (14 tables) | 119 MB | as above | USD 0 so far |
| The live set the site reads | Postgres | Supabase project (Pro plan, spend cap on) | 381 MB | 8 GB included (the loader stops at 7,500 MB, warns at 6,000 MB) | USD 25 (Samuel's plan; the ERW adds nothing to it) |
| The append-only archive | object storage | Supabase Storage, private bucket `erw-archive` (547 files) | 507 MB | 100 GB included in Pro | included |
| The network map's hourly file | object storage | Supabase Storage, public bucket `erw-public` | 191 kB | as above | included |
| Raw source files | files | the data machine's disk only | several GB | the disk | USD 0 |

No other service is used. The site (Vercel) reads Supabase; it holds no copy.

## The data lock

One row, `data`, of the Supabase table `erw_locks` (migration 016, functions `erw_lock_acquire`, `renew`, `check`,
`release`, `status`, callable with the service key only). It names its holder and task and expires (default 120 minutes)
unless renewed, so a machine that closes or crashes cannot hold it forever.

```bash
python warehouse/lock.py acquire --task "backfill x" --minutes 120 --wait 30   # prints nothing secret; token in .erw/, per session
python warehouse/lock.py run --task "daily" -- bash warehouse/run_daily.sh      # take, renew every 10 minutes, run, release
python warehouse/lock.py release
python warehouse/lock.py status
```

**The holder is the session, not the machine (session 65).** A session's identity is `ERW_SESSION`, else Claude Code's
`CLAUDE_CODE_SESSION_ID`, else the GitHub run id; a plain terminal has none and counts as the machine's one terminal. The
holder recorded in `erw_locks` is `<machine>/<first 8 characters of the session>`, and the token is kept in
`.erw/lock.<session>.json`, which only that session reads (`ERW_LOCK_TOKEN` in the environment still wins, so a worker
passes its token to the task it starts). Two sessions on one machine therefore cannot both hold the lock: the second
finds it held by the first, by name, and its writers refuse. Before session 65 the token sat in one file per machine,
`.erw/lock.json`, which every process on the machine read: while one session held the lock, any other session on that
machine passed `require()` with the same token, and `release` in either gave it up for both.

Every data writer calls `lock.require()` and refuses without the lock: the connectors' writer (`iso_prices.write_csv`,
`write_snapshot`, so every connector), the Supabase loader (`load.py`, except `--dry-run`), the Redivis uploader
(`upload.py`, except its read-only `--reconcile`, `--restore` and `--check-license` without `--fix`), the archive
(`archive.py write`, `reindex`, `seed-consolidated`, `sync`) and the vacuum. Not data writes: a write outside
`warehouse/output` (tests, scratch folders), and test runs (`python -m unittest`, pytest, or `ERW_LOCK_EXEMPT=1`).

The daily job takes the lock before its first step (waiting up to 60 minutes for a machine that holds it) and releases it
after its commit, whatever happened; the weekly vacuum runs under `lock.py run`. Two scheduled writers are outside the
lock by design: `latest-prices` (every 15 minutes, replaces the rows of the small table `latest_prices` in Supabase) and
`hourly-network` (writes one object to `erw-public`). Each writes only its own live object, never `warehouse/output`, so
neither can collide with a data run.

## The schedule

The schedule lives in the database, not on any machine (migration 015, `warehouse/supabase/scheduler.py`): pg_cron calls
`public.erw_dispatch(workflow, body)`, which uses pg_net to call GitHub's `workflow_dispatch` with a token kept in
Supabase Vault (`github_dispatch`; set by `python warehouse/supabase/scheduler.py --set-token` from `GH_TOKEN` in `.env`,
never in the repository).

| Job | When (UTC) | Workflow |
|---|---|---|
| `erw-daily` | 14:00 daily | `daily-prices.yml`, `once=1` (a second run the same day is skipped) |
| `erw-latest-prices` | every 15 minutes | `latest-prices.yml` |
| `erw-hourly-network` | :05 every hour except 14:05 | `hourly-network.yml` |
| `erw-roundup` | Sundays 23:00 | `roundup.yml`, `once=1` |
| `erw-weekly-vacuum` | Sundays 10:00 | `weekly-vacuum.yml` |

`python warehouse/supabase/scheduler.py --status` lists the jobs and their last runs. When the GitHub token is renewed,
run `--set-token` once.

### Health: skips, retries, the daily summary (session 61)

No scheduled job fails on GitHub, so GitHub sends no failure email; the digest and the Roundup are the only emails.
Every step runs under `warehouse/health.py run`, which writes one row per step to the Supabase table `erw_health`
(migration 017, service key only):

- **skipped**, a success with a one-line reason, when the job should not run: the data lock is held after the wait, the
  day's work is done (the daily job: a run succeeded today or today's "Daily prices" commit is on main; the Roundup:
  not Sunday), EIA has not finished publishing the newest hour (the network), or the start duplicates another
  (`health.py dedupe`: the database's dispatch is the schedule; a run GitHub's own schedule starts yields to it);
- **retried**, when a step failed once and passed on its second try a minute later;
- **failed**, when it failed twice. A step that spends on the model or sends email (the daily run, the Roundup and its
  send) is not retried: its connectors retry their own requests, and a second try could send twice.

The daily job writes the previous UTC day's rows into `queue/summary/<day>-health.md`: runs against the expected count
(fewer than half means the schedule may have stopped), every failure and retry, and the skips by reason.
`python warehouse/health.py summary --day <day>` writes it by hand. A market failing three daily runs in a row is a
failure row there, no longer a GitHub issue.

## Code work: branches, checks, merge

A code task works on its own branch, `task/<NNN>-<slug>`. A push to `task/**` runs `.github/workflows/code-branch.yml`:
`tests/` (lock-exempt), the site build, and `check-routes` against the live site; when they pass, the workflow opens a pull
request with its own token and merges it (or, if the repository does not let Actions open pull requests, merges the
branch into `main` directly, after the same checks). A failing branch stays unmerged, and the run's log says why. Data
tasks do not use branches: they commit to `main` under the data lock.

## The queue and the worker

```
queue/todo/NNN-<role>-<slug>.md     waiting
queue/doing/NNN-<role>-<slug>.md    claimed by a machine
queue/done/NNN-<role>-<slug>.md     finished, with its report
queue/summary/<day>-<machine>.md    one line per task a machine finished that day
```

A task file is front matter (`role`, `spend_cap_usd`, `timeout_minutes`, `permission_mode`), then the full prompt.
`python scripts/taskqueue.py new --role code --slug x --title "..." --cap 3 --prompt-file p.md` adds one;
`python scripts/taskqueue.py list` shows the queue.

- **Claiming** is a commit moving the file from `todo/` to `doing/`, pushed to `main`. If another machine pushed first,
  the claim is undone and the worker moves on to the next task.
- **Heartbeat**: a worker renews a row `task:NNN` in `erw_locks` every 10 minutes (it expires after 30). A task in `doing/`
  whose heartbeat expired more than 15 minutes after its claim goes back to `todo/` (any worker does this each turn).
- **The worker** (`scripts/worker.ps1`, `worker.sh`, or `python scripts/worker.py`) loops: sync; requeue stale tasks;
  resume its own task in `doing/` or claim the first one for its role (a data machine takes the data lock first); run
  Claude Code headless (`claude -p`) with the repo's permission settings, the task's permission mode, its spend cap
  (`--max-budget-usd`) and its timeout; write the report into the task file; move it to `done/`; add the day's summary
  line; push. With nothing to do it waits 15 minutes. `--once` takes at most one task.
- **A usage limit** never fails a task: the worker waits until the reset time Claude names (else 30 minutes) and resumes
  the same Claude session, as often as it takes. The pause does not count against the timeout.
- **Run the worker in its own clone** (for example `C:\Users\<you>\erw-worker`), so it never switches branches under
  someone working in the main checkout. It needs the same `.env`.

### Interruption

A code task's branch is pushed to `wip/<NNN>-<slug>` every 10 minutes while it runs. If the laptop closes: its heartbeat
expires; another worker (or the same one, when it wakes) requeues the task; whoever takes it next starts from the
`wip/` branch, not from nothing. A worker that wakes and finds its task still in `doing/` under its own name resumes it on
its own branch. A data task's commits are on `main`; the data lock expires on its own if the machine never comes back.

## Starting the worker at logon

Windows: `scripts\setup.ps1 -Worker` registers a Task Scheduler task "ERW worker" that runs `scripts\worker.ps1` at logon,
restarting it if it stops. macOS: a LaunchAgent running `scripts/worker.sh` with `KeepAlive`. Linux: a systemd user
service with `Restart=always`. Stop it from the same place.

## Alerts: when an unattended session needs a person (session 91)

A night's chain of sessions can stand still with nobody told in two ways: a session waits for input or for a permission,
or the chain stops saving (the laptop closed, a crash, a usage limit, a command that hangs). Each now sends one line by
email, through the sender the digest and `scripts/notify.py` use (Resend), to the fixed recipients only
(`DIGEST_RECIPIENTS`), never to a subscriber. One script does both: `scripts/alert.py`. It needs only Python's standard
library and the keys in `.env`.

### A session waits: the Notification hook

Claude Code runs the hooks named in `.claude/settings.json`. Its `Notification` event fires when Claude Code sends a
notification; the matcher filters by notification type (Claude Code's hooks reference,
`https://code.claude.com/docs/en/hooks`). Four types are a wait, and each has a matcher group that pipes the event to
`python scripts/alert.py hook`:

| Type | When | The line says |
|---|---|---|
| `permission_prompt` | Claude needs a permission to use a tool | waits for a permission |
| `idle_prompt` | Claude finished and nobody has typed, about a minute | waits for input |
| `elicitation_dialog` | a connected tool asks the person a question | waits for an answer |
| `agent_needs_input` | a background session needs input | waits for input |

The line names the machine, the first eight characters of the session, the folder, the chain if one is marked on this
machine, and what Claude Code said: "A Claude Code session waits for a permission on samueloldlaptop (session f4e41419,
in erw), in the chain "night of 4 October": Claude needs your permission to use Bash".

- **At most one email per session and kind every 10 minutes** (`.erw/alerts/`), so a session left open does not fill an
  inbox. A send that failed is not counted.
- **It cannot stop or slow a session.** The reference says a Notification hook cannot block (its exit code is
  ignored); the hook is `async`, has a 45-second timeout, prints nothing and always exits 0.
- **To silence it on a machine:** `ERW_ALERTS=off` in the environment, or an empty file `.erw/alerts_off`. Working at
  the keyboard, the "waits for input" line arrives a minute after every answer you leave unread for a minute: silence
  it there, or keep it.
- **A running session does not pick the hook up.** Hooks are read when a session starts; start a new session (or
  review them in `/hooks`). A session started with `claude -p` fires the hook too.
- The hook runs in bash (`"shell": "bash"`, Git Bash on Windows), like the session-start hook beside it.

### A chain stops saving: the mark and the watch

```bash
python scripts/alert.py chain start --name "night of 4 October, sessions 90 to 101" --hours 14   # first thing in a chain
python scripts/alert.py chain beat      # a save that is not a push (a long pull pushes nothing for half an hour)
python scripts/alert.py chain done      # last thing: with "CHAIN DONE"
python scripts/alert.py chain status    # the mark, the newest push, and what the check would say now
python scripts/alert.py chain check --dry-run
```

- **The mark** is one row, `chain`, of `erw_locks`, the data lock's own table (migration 016): who started the chain,
  its name, when, and when the mark lapses by itself (`--hours`, default 16). It is not the data lock and blocks nothing.
  The token is in `.erw/chain.json` on the machine that started it; `done` and `beat` work only there.
- **A save** is a commit pushed to a `wip/` or `task/` branch (read from GitHub), or a beat. Every chain already pushes
  a `wip/` copy after each working step, so a chain needs to do nothing more than start and end the mark.
- **The watch** is `.github/workflows/chain-watch.yml`: every 15 minutes it runs `alert.py chain check` on GitHub, not on
  the machine that runs the chain, because the usual reason a chain stops saving is that its machine stopped. No chain
  marked: it says so and ends. A marked chain with no save for 30 minutes: one line, "The chain "..." (machine/session)
  has saved nothing for 37 minutes: its last save was a push to wip/090-fixes at 06:48 UTC. Marked as running since
  05:52 UTC." It says so **once at 30 minutes and again every hour after** (90, 150, ...), not every quarter of an hour.
  A mark that lapsed without `done` is said once.
- Like every scheduled job it runs under `warehouse/health.py` and never fails on GitHub; its 96 runs a day are in the
  daily health summary. The database's schedule starts it (migration 022, `erw-chain-watch`), and GitHub's own schedule
  too; the second start is skipped.
- **A long step is a silence.** A pull or a build of more than half an hour pushes nothing: run `chain beat` before it,
  or expect the line.

### The permission allowlist

`.claude/settings.json` also holds the project's permission rules (Claude Code's permissions reference,
`https://code.claude.com/docs/en/permissions`). Rules are read deny first, then ask, then allow; a rule must match each
part of a compound command; `*` stands for any text, and belongs after the subcommand.

| Allowed without asking | Not in the list, so asked for in a session that asks |
|---|---|
| git: status, diff, log, show, branch, fetch, add, commit, merge, checkout, switch; a push to a `wip/` branch | a push to `main` by any other spelling than `git push origin main`, or to a `task/` branch named as such |
| the tests, the validator, the coverage builder, the lock, the health wrapper, the derived builders, the archive, the Redivis draft uploader, the loader, sync, the two email helpers | the connectors (a pull is approved per session), `apply.py` (a migration), `ask.py` and anything that calls the model |
| the site: `npm ci`, the build, `tsc`, `next start`, the scripts in `site/scripts/` | inline code (`python -c`, `python - <<EOF`, `node -e`): it can do anything, so it is not a routine action |
| writes under `runs/` (where a gate's output is redirected), and fetches of the live site and GitHub | edits to the repository's files: that is the session's permission mode, not this list |

**Denied in every mode:** a force push, in the five spellings a session writes (`--force`, `-f`, before or after the
branch, and `--force-with-lease`). Every chain's rules already say "never force push"; this makes Claude Code refuse it.

Three limits, from the reference, to keep in mind:

- **The `wip/` rule also matches `git push origin wip/x:task/x`**, the push that deploys: a `*` matches any text, and no
  allow rule can say "but not this". Rules 8 and 9 of `CLAUDE.md` govern that push, not this list.
- **A rule matches the command as written.** `git -C . push --force` is not stopped by the deny rules. They are a guard
  against the usual spelling, not a wall.
- **Project allow rules apply once the folder is trusted** (the dialog an interactive session shows the first time);
  deny rules always apply. `.claude/settings.local.json` is the place for one machine's own rules; it is not in git.

The rules reduce how often a session asks. They do not choose the mode a chain runs in (`defaultMode` is not set here).
