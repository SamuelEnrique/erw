# Session 3795 report: the per-reactor outages' incremental pull

Energy Research Warehouse (ERW). Chain 215, data machine (lab-desktop), 12 November 2026 16:36 to 16:45 UTC (taken before 3792 to 3794, which wait on the evening's runs). Opus 5.5. Model spend USD 0. Requests: EIA's API, 2 (one trial, one write).

## Read these first

- **Why the per-reactor outages stopped at 21 October:** the connector saves each page by its address and reuses it.
  - The newest page's address does not change as EIA adds days, so every run after the first read the saved page and never passed its last day.
  - No step ran it anyway (chain 211's session 3767).
- **`--new-days` (new):** asks EIA, fresh, only for the days after the held table's newest day. It checks that the first new day follows the held table with no day missing, and writes the held rows with the new ones; a held row is never changed. A day EIA has not published yet writes nothing and is no failure.
- **Written under the data lock, one request:**
  - `eia_nuclear_outages_generator_daily`: 22 new days, 22 October to 12 November (6,270 rows), none missing; 2,147,676 rows, 107 reactors.
  - `nuclear_fleet_status`: rebuilt on it, now to 12 November (15,048 rows, 123 reactors).
  - Both validated, in coverage, archived (`20261112T164309Z-local`, 19,167 rows).
- **Scheduled:** `warehouse/run_data_machine_tables.sh` gains two daily steps, `dm_nuclear_outages_gen` (the connector with `--new-days`) and `dm_nuclear_fleet` (the fleet table after it).
  - They are appended at the end of the steps list, so every position the tests hold stays.
  - Both tables are in the weekly live-set load's list. The loader takes only the tables a live-set rule names.
- **Tests:**
  - 3795 (new): the new days join the held rows; a gap stops the run; no new day is no failure; the steps' order.
  - 247: counts the two new lines (25).
  - 548, 254, 271, 277, 3006, 310, 314: OK.

## Commits

`98dca936d` (the step and its tests), `9b8b133d6` (the two tables' metadata), on `wip/c215-data`.

## Decisions made without you

- **The steps go at the end of the list, not beside the reactor status step.** The tests hold the list by position. The order that matters (the reactor status, then the outages, then the fleet) is kept and tested.
- **The table stays held from /data and Redivis v1** (as session 548 left it). Only the rows moved.

## For Samuel's ruling

- None.
