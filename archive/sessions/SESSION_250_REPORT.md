# Session 250 report: the morning note, and the fault it found

13 October 2026, 09:27 to 10:10 UTC (the push at 09:55), unattended, on lab-desktop (the data machine), the last session of the chain of 12 to 13 October. Branch `task/250-morning-note`, which carries session 249 too. Model spend USD 0: no model call. No pull, no request to any publisher. One change to the live database, under the data lock: migration 032, an index. No page edited.

## Read these first

- **Not meant, and mine: from about 07:20 to 09:41 UTC the emissions page's read of the hourly carbon table could be cancelled by the database.** Session 245 loaded 430 days of that table into the live set (155,911 rows; it was 12,700). The emissions page asks for "the table since seven days ago" with no balancing authority named, a thousand rows a page, in the key's order. The database answered from the primary key, walking every hour of each balancing authority to find its last week: 958 ms for the first page. At 09:39 UTC, asked four times with the site's key, it was cancelled once at the three-second limit and took 0.8 to 1.7 s the other three times. A page whose read is cancelled draws "no data".
- **What it broke:** the route check on `/emissions` in the code machine's sessions 235 and 238 (their reports name it as "not this session's page"), and session 249's landing (run 38376287516, step "Site build and check-routes", failed 09:35 UTC). No visitor saw it: the page is in review, and every snapshot of the night shows the in-review page. Session 245's report had said every page reading the table "asks for its last few days by date, so no page shows a different number". The number was right; the time was not checked.
- **The fix is one index, migration 032, applied at 09:41 UTC under the data lock.** `series_carbon_hourly_since`: the table's rows by hour with the columns the read selects, for this table alone, 13 MB. The same read is 22 ms, from the index alone (`explain analyze`, before and after, in `runs/session250/`). No row, table, policy or page query changed. **It is the reversible choice: `python warehouse/supabase/apply.py --rollback 032` drops it.** The other choices were to load fewer days (undoing what session 245 was asked for) or to change the page's query (pages are the code machine's tonight).
- **I did not time the read through the site's key after the index.** The command was refused by this session's permission check after the migration ran; I did not work around it. The plan above is the database's own measurement. The check run of this landing is the test that counts, and its result is in "The landing".
- **`docs/state/morning_2026-10-13.md` is written:** what landed on both machines with where to look, eight failures, the screenshots in the order to open them, and 124 lines of the night's reports that ask for a ruling, as 70 entries in one list.
- **Sessions 249 and 250 land together,** in this push.

## The note, in short

- **Landed, this machine:** 243 to 248, six merges from 06:39 to 09:07 UTC. 249 and 250 with this push.
- **Landed, the code machine:** 234 (06:29), 235 and 236 together (`aa3addbc`, 09:14). Not landed: 237 (`wip/237-grid`), 238 (`wip/238-research`), 241a (`wip/241a-brand`, pushed 09:16); 239, 240, 241b and 242 had no branch on `origin`.
- **Earlier in the night:** nine merges of the two chains before these, 01:06 to 05:29 UTC.
- **Scheduled jobs:** 12 October's daily run had five failed steps; 13 October had none by 09:30 (234 health rows). Green days in a row: 0.
- **The rulings with a date:** the licenses before 21 October (who writes to NYISO, ISO-NE and MISO), the Research cards built on held grids, the published issues of the Digest and the Roundup, the pages to open.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py` | 0 | six of six |
| `python runs/session250/time_emissions.py 4` (before the index) | 0 | 1 of 4 cancelled (HTTP 500, 57014); 1.72, 0.97, 0.82 s |
| `python runs/session250/explain.py` (before) | 0 | Index Scan using `series_pkey`, 958.8 ms, first page |
| `python warehouse/lock.py run ... -- python warehouse/supabase/apply.py --only 032` | 0 | "applied 032_carbon_hourly_since.sql (Postgres connection)" |
| `python runs/session250/explain.py` (after) | 0 | Index Only Scan using `series_carbon_hourly_since`, heap fetches 0, 22.4 ms; the index is 13 MB |
| the same timing through the site's key, after | not run | refused by the session's permission check; not worked around |
| `python -m unittest tests.test_session250 tests.test_session249` | 0 | 8 and 9 tests |
| `python -m unittest discover -s tests` | 1 | 3,787 tests, 3 failures, 61 skipped: the three this machine always has (`test_session51`, `test_session125`, `test_session165`), on `main` at `aa3addbc` with the files of sessions 249 and 250 |
| `python scripts/freeze.py status` | 0 | no freeze |

## Decisions made without you

1. **An index on the live database, unattended.** It changes no row and no answer, it is 13 MB of a budget of 7,500 MB (the database stood at about 1,430 MB after session 245), and one command drops it. Leaving the fault would have failed the next landing of either machine at random and left `/emissions` drawing "no data" on a cold read.
2. **The index is for this one table,** not a general one on `series`: 156,000 rows of 2.5 million. Another table loaded this large and read the same way would need its own, or the page's read would name its balancing authorities. Ruling 1.
3. **Sessions 249 and 250 land in one push.** Session 249's files are unchanged but for one line at the top of its report saying so.
4. **The note covers the whole night from 00:00 UTC,** not this chain alone: the two chains before midnight Pacific landed nine more merges and left rulings of their own.
5. **Rulings asked before session 200 are not repeated;** `docs/state/rulings_2026-10-11.md` holds them (112 entries). The note says so.
6. **Five rulings are marked closed,** each with the session that closed it, where the files show it.
7. **The count of rulings is held by a test** to the items the list cites, so the two cannot drift.
8. **No screenshot was taken by this chain** (no page edited); the note orders the code machine's.

## For Samuel's ruling

1. **Keep migration 032?** And a rule for the next large load: before a table in the live set grows past, say, ten times its size, time each page's read of it with the site's key (a step of `load.py`, or of the loader's report).
2. **The emissions page's read names no balancing authority.** With the seven ISOs named it would use the primary key well and need no index of its own. One line of `site/app/emissions/page.tsx`, for the code machine.
3. **The landing check retries nothing:** a read cancelled once fails a landing. The reader already retries twice (after 1 and 3 seconds); whether the route check should rebuild once on a "no data" block that production does not show.
4. Everything in the note's list.

## Files

- New: `docs/state/morning_2026-10-13.md`; `warehouse/supabase/migrations/032_carbon_hourly_since.sql`, `warehouse/supabase/rollbacks/032_carbon_hourly_since.sql`; `tests/test_session250.py`.
- Changed: `warehouse/supabase/README.md` (the row of migration 032), `docs/methods/emissions.md` (two sentences on the read and the index), `archive/sessions/SESSION_249_REPORT.md` (one line at its top).
- With this push, from session 249: `docs/howitworks/` (five documents, the index, `computed/`), `tests/test_session249.py`, `docs/state/licenses_2026-10-21.md`, `site/data/license_status.json`, its report.
- On this machine, not in git: `runs/session250/` (the timings, the two plans, the migration's output, the health days).

## The landing of session 249

- Pushed 09:26:12 UTC (`task/249-how-it-works`, `1313a2fb`). The check run 38376287516 failed at 09:35:02 UTC in "Site build and check-routes"; the merge job was skipped. Not landed by that push. It lands with this one.

## The landing

- Freeze: `python scripts/freeze.py status` exit 0, no freeze. Main pulled and merged before the push.
- The before snapshot is `s250-before` (09:54:11 UTC). Against `s249-before` (09:25:38 UTC), across the migration: 25 pages, 0 differences. The push of `task/250-morning-note` followed within the minute.
- The check run, the merge, the deployment's time, the after snapshot and the comparison of this last landing are in no committed file: no later session of the chain is there to record them, and a commit to record them would be one more landing. They are in the session's closing message and in `runs/session250/landing.out` on this machine. Expected: 0 differences on the 25 pages. If the check fails again, the work stays on `wip/250-morning-note` and the closing message says so.
