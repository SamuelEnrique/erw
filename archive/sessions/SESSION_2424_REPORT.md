# Session 2424 report: six held tables given notes

24 October 2026, from 11:08 UTC, on lab-desktop (the data machine), a session of `queue/done/115-day-16-november-data-zambia-botswana-mongolia-cambodia.md`. Precheck passed (`runs/c115/precheck_2424.out`). Model spend USD 0. Pulls: none.

## Read these first

- **The finder:** `runs/c115/s2424/find_unnoted.py`, session 2361's script pointed at this worktree, main, and chains 114's and 117's branches. It listed 41 tables with no `Tables:` line or note named for them:
  - **Source tables, five:**
    - this chain's four (Zambia, Botswana, Mongolia, Georgia), which session 2429 describes;
    - chain 110's `eurostat_crude_imports_monthly`, written after chain 110's notes session.
  - **The rest, derived and model-extracted tables,** most named in notes under other names.
- **One new note:** `docs/methods/eurostat_crude_imports_monthly.md`, in the form of chain 110's Eurostat notes. It covers:
  - the address, and the asynchronous answer;
  - the saved answer's size and hash, and the connector's ceiling and stops;
  - its records;
  - the 1,133 provisional rows by year and area;
  - the shape: 37 areas, 173 partners and their aggregates, Namibia's `NA`, 536,445 zero rows;
  - session 2369's checks;
  - what it cannot say.
- **Five derived tables named in their family notes,** each with a `Tables:` line and a checks section of counts from the table on this machine (`runs/c115/s2424/check_tables.py`):
  - **`storage_owners_monthly`** (`storage_owners.md`): 9,540 rows, August 2026, 948 entities, 108 variables, 9 grids.
  - **`shoulder_hours_monthly`** (`shoulder_hours.md`): 27,197 rows, 2019 to 6 October 2026, by entity and freq.
    - The note's table section says "`iso:ercot` or `iso:caiso`".
    - Its later section names the third entity, `iso:caiso_own`, which holds 2,709 rows.
    - The checks say so.
  - **`flex_alert_model` and `flex_alert_effects`** (`flex_alert_scorecard.md`):
    - the model: 881 rows, 297 daily and 584 with no freq, all of the latter dated 1 July 2018, the sample's first day;
    - the effects: 2,973 rows, hourly, daily and yearly.
  - **`grid_stress_yearly`** (`grid_stress.md`): 2,394 rows, against 2,002 when built on 5 October; seven grids.
- **The six Method cells link their notes** (`runs/c057/method_cells_locked.sh`). Only cell 16 changed in each row.
- **The finder again:** 35 tables, none of the six.
- **No contradiction found** between a note and its table, beyond the shoulder table's third entity, which the note's own later section names.

## Errors

- **My first check line for the flex model** said its undated rows are keyed "as section 11 keys them". The note says only that 1 July 2018 is the sample's first day (section 2). Corrected before the commit.
- **A last bullet of the crude note claimed how Eurostat records the country of origin,** which I had not read. It was replaced with a pointer to Eurostat's metadata page.

## Decisions made without you

- **The derived tables given `Tables:` lines** in their existing family notes rather than new notes, as session 2361 did for FERC EQR.
- **This chain's four source tables left to session 2429,** whose task they are.

## For Samuel's ruling

- None new.

## Files

- New: `docs/methods/eurostat_crude_imports_monthly.md`, this report.
- Changed: `docs/methods/storage_owners.md`, `shoulder_hours.md`, `flex_alert_scorecard.md`, `grid_stress.md`; `docs/coverage.md` (six Method cells).
- On the data machine only: `runs/c115/s2424/`.
