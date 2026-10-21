# Session 384 report: reliability, the green streak's remaining causes

20 to 21 October 2026, from 21:16 UTC on 20 October, unattended, on lab-desktop (the data machine), the first session of the chain of 20 to 21 October, night (`queue/done/013-night-20-october-data.md`). Model spend USD 0. Pulls: none. Part (a) landed; part (c) is below; **part (b) was not run**: the session waited for the scheduled runs of 21 October, and at 05:15 UTC on 21 October Samuel asked for the wait to stop and for session 386 to run at once. Part (b) is carried into the next chain (`queue/next/016-day-21-october-data.md`, session 387).

## Read these first

- **Why the daily run of 20 October stopped at 18:06 UTC** (`queue/summary/2026-10-20-health.md`, "## Root causes"): its console window closed. Task Scheduler's event 201 at 11:06:08 Pacific gives the return code 3221225786 (0xC000013A, STATUS_CONTROL_C_EXIT); there is no event of the scheduler stopping the task, its six-hour limit was far off, and the System log holds no sign-out or shutdown. The task runs "Interactive only", so it has a console window, and the run was in `dm_battery_scenario_steps`'s retry (the first try had failed at 11:02:39 Pacific on the stale `battery_stack_monthly`, which session 373's restore fixed). A Ctrl+C would have released the lock through `lock.py run`'s `finally`; a closed window ends the process before it, which is why the lock was held until it lapsed at 20:00 UTC.
- **The fix, landed**: `warehouse/lock.py`'s `on_console_close()` registers a console handler (`SetConsoleCtrlHandler`) for the close, sign-out and shutdown events, and `run()` releases the lock there, once, whichever way the run ends. `tests/test_session384.py`, 5 tests. Not proven end to end: a probe that closes a real console window could not get a window handle from this session (two tries, under conhost and the default console; the probe processes were ended).
- **For Samuel's ruling, not made**: running the task with no console window ("Run whether user is logged on or not"), which takes the close out of reach. It changes the task's account settings, so it is yours.

## (c) The loader's guard, comparing values when the stamps differ (a draft, for Samuel's ruling; `load.py` not changed)

Session 374's load refused 31 tables as "older than the live copy": each is a copy restored from the archive, whose `retrieved_at` stamps are older than those of GitHub's load, and the three read were equal value for value. The guard (`older_than_live()`, session 60) looks at the newest stamp only. The draft keeps the refusal for a copy that differs, and lets an equal one through without writing:

```python
VALUE_CHECK_ROWS = 2_000_000  # above this, the stamps alone decide, as today (a whole-table read)
STAMPS = {"retrieved_at", "loaded_at"}


def same_values(conn, name, df, shape, license):
    """Session 384's draft: True when Supabase holds exactly this table's rows, the stamps left out of both sides."""
    if conn is None or len(df) > VALUE_CHECK_ROWS:
        return False
    cols = [c for c in df.columns if c not in STAMPS]
    live = pd.DataFrame(conn.execute(f"select {', '.join(cols)} from {shape} where table_name = %s", (name,)).fetchall())
    if len(live) != len(df):
        return False
    return rows_sha256(df[cols], license) == rows_sha256(live[cols], license)
```

and, in `older_than_live()`, where the stamps are compared:

```python
            if pd.notna(mine_t) and pd.notna(theirs_t) and mine_t < theirs_t:
                if same_values(conn, name, df, shape, license):
                    return "equal"  # the caller writes nothing: the live rows and their newer stamps stay
                return f"its newest retrieved_at here is {mine}, Supabase holds rows retrieved {theirs}"
```

with the caller treating `"equal"` as `unchanged` (no write, the row hash stored). What it changes: the 31 tables load as unchanged instead of failing the load; a table that differs, `ferc_eqr_contracts` with 452 rows fewer here, is still refused. What it costs: one whole-table read for each table whose stamps are older here, under the reader's own timeout. Open points for the ruling: the row ceiling; whether `rows_sha256` must sort both sides first (it hashes in the frame's order); and whether a table equal in value should take the restored stamps or keep the live ones (the draft keeps the live ones).

## Checks

| What | Exit | Notes |
|---|---|---|
| `tests.test_session384` | 0 | 5 tests |
| the whole suite, `GITHUB_ACTIONS=true`, before `task/384-lock` | 0 | 4,705 tests, 278 skipped, 249 s, foreground (`runs/s384_suite.out`) |
| `scripts/freeze.py status` | 0 | no freeze |

## Landing

`task/384-lock`, merged as `dfbe8e08` (checks passed, run 39502028928), deployed 21:52 UTC. Rule 8: `s384-land-before` and `-after`, 0 differences on 25 pages, expected (every page in review). This report lands with session 386's note.

## Decisions made without you

1. The release on close is done once, from the handler or from `finally`, whichever comes first; a failed release in the handler is printed, not raised, since the console is closing.
2. The handler returns False, so Windows still ends the process as it would have.
3. Part (b) carried to session 387 rather than run on a day whose scheduled runs had not finished.

## For Samuel's ruling

- The task with no console window (above).
- The guard of part (c).

## Files

- Changed: `warehouse/lock.py`, `queue/summary/2026-10-20-health.md` (commit `0291de7f`).
- New: `tests/test_session384.py`, this report.
