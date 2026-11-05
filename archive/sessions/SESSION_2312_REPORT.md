# Session 2312 report: six held tables linked to the notes that describe them (carbon intensity, the storage fleet and its daily cycle, ERCOT's storage awards by month)

24 October 2026, from 06:16 UTC to 06:26 UTC, on lab-desktop (the data machine), chain 106, unattended, while session 2311's request to ADME ran. Model spend USD 0. Pulls: none.

## Read these first

- **How the tables were chosen:** 76 tables have an empty Method cell in `docs/coverage.md` on this branch, on main and on chains 104's and 105's branches (`runs/c106/empty.py`). Chain 105's agent confirmed no overlap with its session 2298 (which took six EIA-930, futures and MISO tables).
- **Six `Tables:` lines,** in notes that already describe each table, each checked against the table read past its header lines:
  - `carbon_intensity_hourly`, `carbon_intensity_daily` and `carbon_intensity_monthly` in `docs/methods/emissions.md`: 1,127,945, 46,980 and 1,275 rows, eight balancing authorities, kgCO2/MWh, from 2018-07-02. The note's two variables are the tables' two.
  - `storage_daily_cycle` and `storage_capacity` in `docs/methods/storage.md`:
    - the cycle: 14,503 rows, five variables, CAISO's rows from 2025-08-24 marked `erw:storage_daily_cycle_caiso`, as the note says;
    - the fleet: 1,137 operating units with 150,437.6 MWh and 8 retired with 1,236.1 MWh, exactly the note's figures.
  - `ercot_storage_dam_awards_monthly` in `docs/methods/ercot_storage_dam_awards.md`: 252 rows, 28 variables, December 2025 to August 2026. The `_per_mw` variables are covered by the note's "each `revenue_*` also `_per_mw`".
- **The six Method cells set** by `build_coverage.py`'s own `method_cell`.

## Contradictions found, written into the notes

1. **`emissions.md`'s month counts are dated.** It gives SPP 45 complete months and US48 97; the table now holds 46 and 98. The note keeps its sentence and adds today's counts.

## Checks

- `tests.test_session674`, `1000` and `1001`: OK.

## Decisions made without you

- `Tables:` lines rather than new notes, as sessions 2228 and 2270 did.

## For Samuel's ruling

- None new.

## Files

- Changed: `docs/methods/emissions.md`, `storage.md`, `ercot_storage_dam_awards.md`, `docs/coverage.md` (six Method cells). New: this report.
