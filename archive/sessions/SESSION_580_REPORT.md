# Session 580 report: the database's heavier reads, measured

Chain 034 (`queue/done/034-night-22-october-code.md`), samueloldlaptop, code machine, unattended, 22 October 2026
(UTC). Branch `wip/580-s`, cut from `origin/wip/506-combined` and merged with `origin/main`. Not landed: session 589
lands the chain.

## Summary

The site's reader (`site/lib/supabase.ts`) can now print one line a request with its table, query, status, rows and
time, switched on by `ERW_READ_TIMING=1` and off by default. One build and one route check against it were timed:
tonight the database answers every read the site makes in 80 to 200 ms when asked alone, and no read met the
statement timeout. The only slow requests (nine, 0.9 to 6.9 s) were in the build's opening burst. Of the five slowest,
two kinds lack an index that fits them (the queue read of `energy_projects`, the event pages' reads of
`event_window_daily`); migration 036 holds a small partial index for each, written and **not applied**. The review is
`docs/reviews/slow-reads-2026-10-22.md`.

## What I did

1. `site/lib/supabase.ts`: `readTiming(v)` (on only for `"1"`), `READ_TIMING` from `ERW_READ_TIMING`, `readClock()`
   (0 and no clock when off) and `readLine()` (returns at once when off; on, prints `[erw-read] {kind, table, query,
   status, range, ms}`). Both readers, `onePage` (rows) and `countOf` (counts), take the time inside session 90's turn,
   in a `try`/`finally` around their request, so a request that throws is a line with status `failed`. Session 537's
   `askAgainOnFailure`, session 499's public-rows read and count, session 148's paged reader and session 90's turns
   are unchanged, and the request (address, headers, cache settings, retries) is the one it was. A first form wrapped
   the request in a function; it broke session 148's test that one line sends a page's request
   (`test-ask-speed.mjs`), so the request line was kept as it was and the clock put around it.
2. `site/scripts/test-read-timing.mjs`: seven cases run with the switch off and on, with a stand-in for fetch (no
   request leaves the machine): off prints nothing and sends the same requests and returns the same rows and
   failures; on prints one line a request (one page, three pages, three tries of a statement timeout, a refused
   request, a count). The license hold's by-row case is vacuous today (no table is held by row; the test says so).
3. `site/scripts/slow-reads.mjs`: reads a log's `[erw-read]` lines, groups them by kind, table and query, prints the
   N slowest as a Markdown table; exit 2 when a log holds no line.
4. The measurement: `ERW_READ_TIMING=1 npm run build` (210 requests), then `next start -p 3580` with the switch on and
   `check-routes.mjs` against it with the local server as its own baseline (10,367 requests, no request to
   production). The 25 slowest were asked again alone, three times each, straight to PostgREST with the anon key, and
   nine row counts read (read-only GETs; scripts in `runs/s580/`, not committed).
5. `EXPLAIN` through the anon key: PostgREST refuses it (`PGRST107` for `application/vnd.pgrst.plan+text`), one
   request. The plans were read from the indexes in `warehouse/supabase/migrations/` and the row counts instead.
6. `warehouse/supabase/migrations/036_slow_read_indexes.sql` (two partial indexes, `entities_projects_kind` and
   `series_event_window_by_event`, plus `analyze`) and its rollback `warehouse/supabase/rollbacks/036_slow_read_indexes.sql`.
   Not applied: no SQL was run against the database.
7. `docs/reviews/slow-reads-2026-10-22.md`: the twenty slowest, the five read against the indexes, what is not settled.
8. `tests/test_session580.py`: the node test both ways, the summary script on a fixture log, the code's switch and
   request lines, sessions 537 and 499 standing, migration 036 indexes-only with a matching rollback, no em dash.

## Checks

| Check | Command | Exit |
|---|---|---|
| precheck | `$PY scripts/precheck.py --what "session 580"` | 0 |
| database probe | `$PY scripts/db_probe.py` (0.65 s for 1,000 rows) | 0 |
| build lock, duty beat | `buildlock.py acquire s580`, `duty.py beat` | 0, 0 |
| build, timing on | `ERW_READ_TIMING=1 timeout 1800 npm run build > runs/s580_build.out` (no "statement timeout" in the log) | 0 |
| route check against it | `node scripts/check-routes.mjs http://localhost:3580 http://localhost:3580` (226 pages, 0 failed) | 0 |
| summary | `node scripts/slow-reads.mjs runs/s580/all.log 30 --json ...` | 0 |
| node test, off and on | `node --import ./scripts/alias-register.mjs scripts/test-read-timing.mjs off` / `on` | 0, 0 |
| session 537's node test | `node --import ./scripts/alias-register.mjs scripts/test-failed-read.mjs` | 0 |
| type check (final code, under the build lock) | `node node_modules/typescript/bin/tsc --noEmit -p .` | 0 |
| tests | `ERW_LOCK_EXEMPT=1 $PY -m unittest tests.test_session580 tests.test_session537 tests.test_session143` (35 tests) | 0 |
| migration tests | `tests.test_session143 158 177 181 188_idle 70 72` (199 tests): one failure against the first form, session 148's line check in `test-ask-speed.mjs`; after the fix, the same seven and 580 (209 tests, 1 skipped) | 1, then 0 |

The build measured the first form of the switch (a wrapper with the same clock points); the final form was type-checked
and tested but not built again (one build). No page's figure can move: with the switch off no read changes, which the
node test proves; check-values was not run, no page being touched.

## Decisions made without you

- The switch is `ERW_READ_TIMING=1` exactly; any other value is off.
- The lines go to the server's own log (console), not to a file: no file is written by the site.
- The route check's baseline was the local server itself, so the measurement sent no request to production.
- The five slowest are taken by request (one page), the unit the 3 s statement timeout cancels.
- Both proposed indexes are partial, one table each, after migration 032's pattern, to stay small under the 300 MB cap.
- The scripts that asked PostgREST again (`runs/s580/retime.py`, `counts.py`, `explain.py`) stay in `runs/`, not committed.

## For Samuel's ruling

- Apply migration 036 (`python warehouse/supabase/apply.py --only 036`), then confirm with `explain (analyze, buffers)` in the SQL editor that the two reads use the new indexes; rollback `apply.py --rollback 036`.

## To finish

Nothing. (Session 589 lands the chain; migration 036 waits for the ruling above.)

## Files changed

- `site/lib/supabase.ts`
- `site/scripts/test-read-timing.mjs` (new)
- `site/scripts/slow-reads.mjs` (new)
- `tests/test_session580.py` (new)
- `warehouse/supabase/migrations/036_slow_read_indexes.sql` (new, not applied)
- `warehouse/supabase/rollbacks/036_slow_read_indexes.sql` (new)
- `docs/reviews/slow-reads-2026-10-22.md` (new)
- `archive/sessions/SESSION_580_REPORT.md` (new)
