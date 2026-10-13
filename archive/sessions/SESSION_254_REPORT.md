# Session 254 report: each grid's own scarcity signal

13 October 2026, 18:38 to 19:15 UTC, unattended, on lab-desktop (the data machine), the second of three sessions (251, 254, 255). Branch `task/254-scarcity-signal`. Model spend USD 0: no model call. Pulls: one request, to CAISO, for its Grid Emergencies History Report. Writes, all under the data lock: `caiso_grid_emergencies` (refreshed, the same rows), the new table `scarcity_hours_by_grid`, their coverage rows, the archive and the Redivis draft (nothing released). No load into the live set, no page.

## Read these first

- **The new table `scarcity_hours_by_grid` holds, for ERCOT and CAISO and every hour of October 2023 to September 2026, the USD 1,000 price count and the grid's own signal:** 178,886 rows, validated. Its rule: `docs/methods/scarcity_hours_by_grid.md`.
- **The two counts do not say the same thing.** ERCOT: the price was at or above USD 1,000 in 12 hours of the 36 months; its reserve adder was above zero in 759 of the 19,097 hours it was published in (it ended on 4 December 2025). In 10 of the 11 hours with both, the adder was on. CAISO: 1 hour at or above USD 1,000 in the 25 months of prices held, and one Energy Emergency Alert in 36 months (an EEA Watch, 24 July 2024, seven hours).
- **The rows are not in Supabase tonight, on purpose.** The live-set rule lands with this session and the data machine's daily load carries the table tomorrow. I did not load 179,000 rows into the live set four hours before the demo for a table no page reads yet. One command loads it tonight (under "To finish").
- **CAISO's notices table was refreshed and the queued task about it is answered and closed.** The report had been behind: on 9 and 10 September 2026 CAISO declared Restricted Maintenance Operations (no Flex Alert, no EEA). The table runs to 8 October 2026, 1,906 rows.
- **For the code machine:** the two reads of the table, with the values a check should find, and one sentence on `/grid/caiso/alerts` that is now wrong. Below.

## What to review

- The rule on GitHub: https://github.com/SamuelEnrique/erw/blob/main/docs/methods/scarcity_hours_by_grid.md
  1. "The table": four variables, and the line "An hour without a row is not held. It is not a zero."
  2. "Each grid's own signal": what makes ERCOT's and CAISO's signal 1, and what does not (restricted maintenance, transmission emergencies).
  3. "What the first run holds": the table of counts.
- No page changed.

## For the code machine: the lines that read it

In `site/lib/datacenter/answers.ts`, beside the two reads of `ercot_rtm_price_adders` (the block that begins "session 236: ERCOT's own signal"), with the same `y`, `m`, `behind` and `iso`:

```ts
const own = { table_name: "eq.scarcity_hours_by_grid", entity: `eq.iso:${grid}`, variable: "eq.own_signal", order: "ts_utc" };
const since = `gte.${iso(Date.UTC(y, m, 1) + behind * 3600_000)}`;
const [ownHeld, ownOn] = await Promise.all([
  rows("series", { select: "ts_utc", ...own, ts_utc: since }),               // the hours the grid's own signal is held for
  rows("series", { select: "ts_utc", ...own, value: "eq.1", ts_utc: since }), // the hours it was in force
]);
```

- **What a check should find,** default case, October 2025 to September 2026 in the grid's standard time. ERCOT: 1,558 hours held (1 October to 4 December 2025), 44 in force. CAISO: 8,760 hours held, 0 in force.
- **The price rows of the same table** (`variable` `rt_hour_ge_1000` or `da_hour_ge_1000`, `value` `eq.1`): ERCOT 1 real-time hour (28 January 2026, from 07:00 Central standard) and 14 day-ahead hours; CAISO 1 real-time hour (26 August 2026, from 21:00 Pacific standard) and 0 day-ahead. They are at the hub (`HB_HUBAVG`, `TH_SP15_GEN-APND`); the page's own count is of its region's price and stays the page's.
- **`x_detail` is not in the live set:** the loader carries no extra column of a series table. ERCOT's level of USD 100 still needs `ercot_rtm_price_adders`, and the names of CAISO's notices still need `caiso_grid_emergencies`. In the CSV and on Redivis `x_detail` holds both.
- **The table is not loaded until the data machine's next daily run** (or the command under "To finish"). Until then both reads return no row.
- **A sentence now wrong:** `site/app/grid/caiso/alerts/page.tsx`, line 312: CAISO's report "runs to 2025-04-30, so the 2025 season has none here". It runs to 8 October 2026, and CAISO printed no notice between 30 April 2025 and 9 September 2026.
- **`docs/methods/datacenter_pays_algorithm.md`, 4.15,** says twice that `caiso_grid_emergencies` runs to 30 April 2025. The page's own line follows the table's newest notice; the note's two sentences do not.

## The table, in short

| | ERCOT (`HB_HUBAVG`) | CAISO (`TH_SP15_GEN-APND`) |
|---|---|---|
| Hours in the window | 26,304 | 26,304 |
| Real-time hours held | 26,304 | 18,191 (from 1 September 2024) |
| Real-time hours at or above USD 1,000 | 12 (49 intervals) | 1 (11 intervals in 6 hours) |
| Day-ahead hours at or above USD 1,000 | 22 | 0 |
| Own signal: hours held | 19,097 (to 4 December 2025) | 26,304 |
| Own signal: hours in force | 759 | 7 |

## Pulls

| Host | Requests | Result |
|---|---|---|
| `www.caiso.com` | 1: the Grid Emergencies History Report, through `caiso_emergencies.py` | HTTP 200; revision of 9 October 2026; 1,906 rows, the same as the data machine's run of 17:31 UTC |

- No paused publisher was asked. No request to NYISO, ISO-NE, MISO, SPP or PJM.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py --what "session 254"` | 0 | six of six; on duty |
| `lock.py run -- caiso_emergencies.py` | 0 | 18:40 UTC; 1,906 rows; 0 rows differ from the earlier file apart from the retrieval time |
| `lock.py run -- scarcity_hours_by_grid.py` (three times) | 0, 0, 0 | 178,886 rows each time; the rows of the third build are byte for byte those of the first |
| `python warehouse/validate/erw_validate.py` on the two tables | 0 | pass, pass |
| `python warehouse/metadata/build_coverage.py --only ...`, first run | 1 | the gate worked: a new table needs a sector rule. Added (`power`) |
| `lock.py run -- table_stores.py scarcity_hours_by_grid caiso_grid_emergencies` | 0 | the validator, the coverage row, the archive (178,886 rows new), the Redivis draft; nothing released |
| the same for the new table after the third build | 0 | 0 rows new or changed in the archive |
| `python warehouse/supabase/load.py --dry-run --only ...` | 0 | the rule selects the table: 178,886 rows, series, whole, public. Nothing sent |
| `python -m unittest tests.test_session254` | 0 | 12 tests |
| `python -m unittest discover -s tests`, first run | 1 | 3,985 tests, 4 failures: this machine's usual three and one of mine (decision 6) |
| `tests.test_session254 tests.test_session103` after the fix | 0 | 28 tests |
| `python -m unittest discover -s tests`, final | 1 | 3,985 tests, 3 failures, 44 skipped, 465 s in the foreground: the three this machine always has (`test_session51`, `test_session125`, `test_session165`); none in what this session wrote |
| `python scripts/freeze.py status` | 0 | no freeze |

## Decisions made without you

1. **Two grids, ERCOT and CAISO.** They are the two with a table of their own signal, and their prices are public. NYISO, ISO-NE, SPP and MISO are left out: their price tables need a license from 21 October or are held, and a table that mixed them in would need one too. Adding a grid is one entry in `GRIDS` (ruling 1).
2. **ERCOT's signal is the adder above zero, as the prompt says,** and the adder's hourly mean is beside it in `x_detail`. The datacenter page counts the adder at USD 100, because above zero is mostly fractions of a cent: 759 hours against a handful. Both can be read (ruling 2).
3. **CAISO's signal is an EEA (Watch, 1, 2, 3) or a Flex Alert.** Restricted maintenance and transmission emergencies are named in `x_detail` and do not make the signal 1: the first asks plants to put off maintenance, the second is local. In the 36 months that leaves one EEA Watch (ruling 3).
4. **The window is 36 whole months in each grid's standard time,** as the datacenter page counts its months, not the month under way. The table is rebuilt once a month.
5. **A monthly step of the data machine's run** (`dm_scarcity_hours`, the block of session 247) and a rule of the live set with both holds, as session 244 did for the adders. Session 247's test of that block pinned nine steps; it now holds ten.
6. **The suite caught a rule I broke.** The builder first read its tables with the comment character, which cuts a row at a "#" in a value (session 103's rule). It now skips the header by its line count. The rows came out the same, byte for byte.
7. **No load into the live set tonight.** Reversible by one command. Reasons in "Read these first".
8. **Step 3 of the queued task was not done:** CAISO's live notices page was not fetched. The history report answers the question for 8 to 10 September, and the live page shows today's notices. The task is moved to `queue/done/` with its report, so that no worker runs it again.
9. **A row that comes out as it was keeps its retrieval time,** so the monthly rebuild rewrites only new or changed rows in the live set and the archive (the data standard's rule for a derived table recomputed from a window).
10. **`docs/methods/california_reliability.md` is corrected** (1,900 rows to April 2025 was session 58's figure). The datacenter page's note and the alerts page are the code machine's and are listed above.

## For Samuel's ruling

1. NYISO's, ISO-NE's and SPP's price counts in `scarcity_hours_by_grid` (the USD 1,000 count alone; no table of their own signal is held): add them once their licenses are answered?
2. ERCOT's own signal on the page: the adder above zero (759 hours in 26 months) or at or above USD 100 (the page's count today)? The table carries the first; the mean is beside it in the CSV.
3. CAISO's own signal: an EEA or a Flex Alert only (7 hours in 36 months), or restricted maintenance too (578 hours with any notice)?
4. ERCOT has published no adder since 5 December 2025: its own signal ends there. Pull its real-time ancillary service prices, the report that replaced it?
5. Load `scarcity_hours_by_grid` into the live set tonight, or let tomorrow's daily run do it?
6. The findings' shared reader (`findings_common.read_table`, session 170) still reads tables with the comment character. No table the hunt reads holds a "#" before a column it needs; move it to the header's line count all the same?

## To finish

- To load the table into the live set tonight (the data machine, from the repository root), with a snapshot before and after:
  `node site/scripts/snapshot-live.mjs take s254-load-before`
  `.venv\Scripts\python.exe warehouse\lock.py run --task "load scarcity_hours_by_grid" -- C:\Users\Shared\Documents\erw\.venv\Scripts\python.exe warehouse\supabase\load.py --no-vacuum --only "^scarcity_hours_by_grid$"`
  `node site/scripts/snapshot-live.mjs take s254-load-after` and `node site/scripts/snapshot-live.mjs compare s254-load-before s254-load-after`
- Otherwise nothing: the data machine's daily run loads it (`dm_live_set`).

## Files

- New: `warehouse/derived/scarcity_hours_by_grid.py`; `docs/methods/scarcity_hours_by_grid.md`; `tests/test_session254.py`; this report.
- Changed: `warehouse/metadata/build_coverage.py` (the sector rule); `warehouse/supabase/live_set.yaml` (the rule and the two holds); `warehouse/run_data_machine_tables.sh` (the monthly step, and the table in the daily load's list); `tests/test_session247.py` (ten steps); `docs/methods/california_reliability.md` (one sentence added); the metadata the stores wrote (`coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, `redivis_uploads.csv`).
- Moved: `queue/todo/006-data-caiso-notices-2026.md` to `queue/done/`, with its report.
- On this machine, not in git: `warehouse/output/scarcity_hours_by_grid.csv` (40 MB), `warehouse/raw/caiso_emergencies/20261013T184029Z/`, `runs/session254/`.

## The landing of session 251

- Freeze: exit 0, no freeze. Main had moved (the code machine's `e01f397d`); merged into the branch before the push.
- Before snapshot `s251-before`: 18:38:03 UTC, 25 pages, 0 failed. Pushed 18:38:19 UTC (`task/251-findings-engine`, `9580ab44`).
- Check run 38448369324: success (its last update 18:47:14 UTC); it merged the branch as `ceac3a77` at 18:47:10 UTC. Deployment of `ceac3a77`: success at 18:50:09 UTC.
- After snapshot `s251-after`: 18:50:41 UTC, 25 pages, 0 failed. `compare s251-before s251-after`: exit 0, **0 differences in all**, on each of the 25 pages. Expected: session 251 added a module, a document's section, a method section, scripts and tests.

## The landing

- The before snapshot, the push, the check run, the merge, the deployment and the after snapshot with its comparison are in session 255's report, under "The landing of session 254". Expected: 0 differences on the 25 pages (a builder, a rule, a test, a monthly step, a live-set rule that selects a table not yet loaded, metadata; no page, no load).
