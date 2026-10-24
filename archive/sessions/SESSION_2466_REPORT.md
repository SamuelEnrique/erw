# Session 2466 report: six held tables named in their family notes

24 October 2026, from 13:05 UTC, on lab-desktop (the data machine), a session of `queue/done/119-day-19-november-data-kyrgyzstan-cote-divoire-jamaica-laos.md`. Precheck passed (`runs/c119/precheck_2466.out`). Model spend USD 0. Pulls: none.

## Read these first

- **The finder:** `runs/c119/s2466/find_unnoted.py`, session 2424's script pointed at this worktree, main, and chains 117's and 118's branches. It listed 31 tables with no `Tables:` line or note named for them:
  - **Two source tables:** this chain's own, which session 2471 describes.
  - **The rest:** derived and model-extracted tables, most described in family notes under other names.
- **Six derived tables given a `Tables:` line** in their family notes, with a checks section of counts from the table on this machine (`runs/c119/s2466/check_tables.py`):
  - **`cost_of_power_monthly`, `cost_of_power_hourly_profile`, `cost_of_power_carbon`** (`cost_of_power.md`): 2,304, 4,368 and 712 rows, the same 7 hubs.
    - The note says "three derived tables" and describes the first under its Formulas section as "the monthly table" without naming it; its name is the builder's (`MONTHLY` in `warehouse/derived/cost_of_power.py`).
    - The checks say so.
  - **`storage_buildout_monthly`** (`storage_buildout.md`): 21,229 rows, 2015 to August 2026, 9 entities, 26 variables.
  - **`price_years_by_window`** (`price_years.md`): 2,754 rows, 19 entities, 470 variables, 13 window lengths (P4M to P141M).
  - **`caiso_reliability_daily`** (`california_reliability.md`): 20,624 rows, 1998 to 17 October 2026, CAISO's own and EIA-930's entities.
- **The six Method cells link their notes** (`runs/c057/method_cells_locked.sh`).
  - The build also refreshed two rows' "Last run" cell from this machine's newer daily run.
  - That change was put back so that the page keeps step with `coverage.csv`; only cell 16 changed in each row.
- **The finder again:** 24 tables, none of the six.
- **No contradiction found** between a note and its table, beyond the unnamed monthly table above.

## Errors

- **The Method cells' build carried a newer "Last run" into two rows.** It was put back to the branch's value, keeping only the Method cell.

## Decisions made without you

- **`Tables:` lines in the existing family notes** rather than new notes, as sessions 2361 and 2424 did.

## For Samuel's ruling

- None new.

## Files

- Changed: `docs/methods/cost_of_power.md`, `storage_buildout.md`, `price_years.md`, `california_reliability.md`; `docs/coverage.md` (six Method cells).
- New: this report.
- On the data machine only: `runs/c119/s2466/`.
