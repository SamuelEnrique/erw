# Session 2110 report: six held ISO New England tables described

23 October 2026, from 22:21 UTC, on lab-desktop (the data machine), a session of `queue/done/069-day-27-october-data-public-lands-sunlight-spending-streams.md`. Model spend USD 0. Pulls: none, and 3 to Supabase for the lock.

## Read these first

- **159 tables in `coverage.csv` had no method note** (by `build_coverage.method_notes()`, after main's merge with chain 067, this chain's four new tables left to session 2116). This session wrote six, ISO New England's source tables, none described before:

| Note | Rows | Entities, variables | First and last hour | First written |
|---|---|---|---|---|
| `docs/methods/isone_as_prices.md` | 55,964 | 1, 4 | 1 March 2025 to 5 October 2026 | 4 October 2026, session 85 |
| `docs/methods/isone_dam_cleared_energy.md` | 960 | 1, 1 | 1 September to 11 October 2026 | 6 October 2026, session 136 |
| `docs/methods/isone_dam_zone_prices.md` | 12,744 | 9, 1 | 26 August to 24 October 2026 | 25 September 2026, session 2 |
| `docs/methods/isone_rtm_zone_prices.md` | 40,608 | 9, 1 | 27 August to 23 October 2026 | 25 September 2026, session 3 |
| `docs/methods/isone_zone_load_hourly.md` | 131,319 | 9, 1 | 1 January 2025 to 1 September 2026 | 7 October 2026, session 138 |
| `docs/methods/isone_ddg_undelivered_monthly.md` | 840 | 1, 14 | January 2018 to September 2026 | 7 October 2026, session 149 |

- **Written by a helper agent in the chain's worktree, checked by this session.** Every row count, entity and variable count and first and last hour was recomputed from the tables, and all are as written; each agrees with its `coverage.csv` row. Each note has its `Tables:` line, and there is no em or en dash. Two of the contradictions below were checked in the code. The six Method cells are filled (`runs/c057/method_cells_locked.sh`).
- **Found while writing the notes, each written in its note and left in the code for a code chain** (no figure, rule or request changed):
  1. `isone_rtm_zone_prices`: gridstatus reads ISO-NE's preliminary five-minute files (`histRpts/5min-rt-prelim/`, checked), while the connector and `sources.csv` cite the final five-minute report page.
  2. The same table's header line says a missing five-minute price "fails the file" (checked in `iso_prices.py`), but since session 13 the check is by day and only the short day is left out. The table is missing 10 of its 57 days, and 14 and 15 October have no gap row in `run_status.csv`.
  3. `iso_as_common.py`'s docstring says a 404 is a gap; ISO-NE's fetch raises a plain error, so a 404 is retried four times and stops the run.
  4. `iso_as_common.py`'s docstring names spec keys the code does not read (`regions`, `variables`, a document's `days`).
  5. `isone_zone_load.py`'s `--days` chooses which years' workbooks are read, not how many days are written. Its stale-at-source test can fire only on an empty workbook. The connector also drops a text cell silently where the other ISO-NE connectors stop the run.
  6. `isone_ddg_undelivered.py`'s docstring gives the ruling as "about 1,000 rows" (checked); the table holds 840.
- **`isone_as_prices` and `isone_ddg_undelivered_monthly` are on no schedule**, as the notes say.

## Errors

- None.

## Decisions made without you

- **ISO New England's six,** a coherent group of source tables, chosen among the 159.
- **The contradictions left in the code,** as session 2060 left its CAISO ones: they change words a code chain should weigh, not data.

## For Samuel's ruling

- None new.

## Files

- New: the six notes above, this report.
- Changed: `docs/coverage.md` (the six Method cells), `warehouse/metadata/coverage.csv` (line endings only).
