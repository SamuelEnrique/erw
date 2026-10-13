# The queues

Energy Research Warehouse (ERW). This folder holds two queues. They do different jobs and never read each other's
files. The full account is in `docs/machines.md`.

## The chain queue (session 188): what a machine runs next

```
queue/next/NNN-<slug>.md    a whole prompt file (a chain of sessions, or one session), waiting
queue/done/NNN-<slug>.md    taken: the file as it was run
queue/CHAIN_TEMPLATE.md     the shape of a prompt file: copy it, fill it in, save it in queue/next/
```

- **To queue work:** write a prompt file from `CHAIN_TEMPLATE.md`, name it `NNN-<slug>.md` (three or more digits, then
  lower-case letters, digits and hyphens: `190-night-of-12-october.md`), put it in `queue/next/`, commit and push.
- **Order:** files are taken in the order of their numbers, lowest first.
- **Taking one:** the last step of a chain's last session is `python scripts/chain_queue.py next`.
  - A file waits: it moves to `queue/done/` in one commit of that move alone, and the command prints its new path on
    the last line (exit 0). The session reads that file and runs it.
  - Nothing waits: the command writes one row to the health table `erw_health` (step `idle`), takes the machine off
    duty and exits 3. It sends no email itself (session 243, the email rule): 15 minutes later the chain watch sends
    the machine's one email, "ready for review", unless the machine is on duty again by then.
- **Looking:** `python scripts/chain_queue.py list`, and `python scripts/chain_queue.py next --dry-run` (says what
  would happen; moves, commits, writes and sends nothing).
- **Not taken:** a file in `queue/next/` whose name is not `NNN-<slug>.md`, and a name of the task queue below
  (`NNN-code-...`, `NNN-data-...`). It is left where it is and named in what the command prints.
- **One machine draws at a time.** The move is a commit on the session's branch; it reaches other machines when it is
  pushed. A second machine that has not pulled it would take the same file.
- A prompt file's first rule is the precheck, `python scripts/precheck.py`, and its last is the queue step above.

## The planner (session 197): the chain queue's next file, drafted from the roadmap

```
docs/roadmap.md                       the planner's only source of what to do; a person writes it
queue/next/NNN-planned-<slug>.md      a chain the planner drafted; its first line says so
```

- **Off unless a person turns it on:** `planner: on` under "Status" of `docs/roadmap.md`. No model call: the planner
  copies the roadmap's own words and the rules of `CHAIN_TEMPLATE.md` into a chain of one to three sessions.
- **Looking:** `python scripts/planner.py check` (why it would or would not run), and
  `python scripts/planner.py draft --dry-run` (prints the chain; writes nothing).
- **When it runs:** `python scripts/chain_queue.py next`, with nothing waiting and the planner on, runs
  `python scripts/planner.py draft`. A chain it writes is committed alone, pushed to `wip/<name>` and taken as the next
  file. When it refuses, the machine idles as said above.
- **It refuses** when the planner is off, the roadmap is older than 7 days, "This week" has no open item for the
  machine's role that was not planned before, `queue/next/` already holds a file, the machine is at its budget of
  sessions for the day, or the hour is outside the start hours.
- **It never plans** a pull, a migration, a secret, a release-gate change, a change to `CLAUDE.md` or a deletion, nor
  more than one session that lands. `docs/machines.md`, "The planner", has the whole account.

## The task queue (session 59): single tasks for the workers

```
queue/todo/NNN-<role>-<slug>.md     waiting; role is code or data
queue/doing/NNN-<role>-<slug>.md    claimed by a machine
queue/done/NNN-<role>-<slug>.md     finished, with its report
queue/summary/<day>-<machine>.md    one line per task a machine finished that day
queue/summary/<day>-health.md       the day's health of the scheduled jobs (warehouse/health.py summary)
queue/e2e/                          the two tasks the queue's own end-to-end test runs
```

- A task file is front matter (`role`, `spend_cap_usd`, `timeout_minutes`, `permission_mode`), then the full prompt.
- `python scripts/taskqueue.py new --role code --slug x --title "..." --cap 3 --prompt-file p.md` adds one;
  `python scripts/taskqueue.py list` shows the queue.
- A worker (`python scripts/worker.py`) claims the first task for its role by a commit pushed to `main`, keeps a
  heartbeat, runs Claude Code headless, writes the report into the file and moves it to `queue/done/`.

## How the two differ

| | The chain queue | The task queue |
|---|---|---|
| Holds | whole prompt files: a chain, with its rules and its sessions | single tasks with a spend cap and a timeout |
| Taken by | the session that just finished a chain, on the same machine | whichever worker is free, by role |
| Taking is | a commit on the session's branch, not pushed by the command | a commit pushed to `main`; a lost race is undone |
| When empty | the machine says it is idle (a health row; its one email, "ready for review", follows 15 minutes later) | the worker waits 15 minutes and looks again |
| Names | `NNN-<slug>.md` | `NNN-code-<slug>.md`, `NNN-data-<slug>.md` |

Both use `queue/done/`. The names keep them apart: the task queue reads only names with a role, and the chain queue
refuses them.
