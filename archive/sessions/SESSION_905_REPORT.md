# Session 905 report: method notes for chain 049's tables, and what their checks fixed

23 October 2026, from 07:03 UTC, on lab-desktop (the data machine), a session of `queue/done/049-day-23-october-data-margins-schedules-emissions.md`. Model spend USD 0 (the notes were drafted by three helper agents of this session and checked here, while session 906 ran). Pulls: none.

## Read these first

- **Seven new method notes and one extended,** each linked from coverage's Method column (`tests/test_session905.py`):
  - `eia411.md`
  - `eia860_environment.md` (three tables)
  - `eia923_monthly.md`, `eia923_receipts.md`
  - `eia_gas_pipeline_projects.md`
  - `eia_power_costs_annual.md`, `eia_uranium_marketing_annual.md`
  - `eia860_schedules.md`, extended with the multifuel table
  - `ercot_node_places.md` was written by session 901.
- **The notes' checks found three faults in the tables, each fixed, tested and the table written again:**
  - `eia411_capacity_margins_annual`: EIA's winter file names RFC with a footnote mark (`RFC[5]`), which split RFC into two entities. The mark is now stripped; 16 areas, not 17.
  - `eia_gas_pipeline_projects`: the dates carried a time, and an id's last part was EIA's year text as given. Dates are now YYYY-MM-DD and the year a slug (`2020_2027_phased`).
  - `eia860_multifuel_generators`: its header named session 885. Each of the five schedules now names its own session.
- **Docstrings corrected where they said what the code does not do:** `eia860_environment.py`, `eia923_monthly.py`, `eia923_receipts.py`, `eia_epa_costs.py`.
- **Six reports corrected,** each with a closing section "Corrected by session 905" that leaves its text as written: 895, 896, 897, 899, 903 and 904. Among them:
  - the boilers' 4,741 "generators" are mentions of 2,296 distinct generators;
  - the uranium spot and long-term contracts exceed the total once (2021);
  - one pipeline project is dated 1903 as EIA gives it.
- **The Stanford draft now holds stale copies of the two rewritten tables:** session 906 uploaded `eia411_capacity_margins_annual` and `eia_gas_pipeline_projects` before these fixes. Chain 051's session 919 uploads them again; chain 049's note and the next file say so.

## Decisions made without you

- **A process fault of mine, mended:** for the second time in this chain, a staged conflict nested a second patch. The nested resolver took main's older row for `eia860_generator_owners`; the branch's row was restored from the last commit, and every metadata change checked against it.
- **A new resolver for flat blocks** (`runs/c049/resolve_theirs_keys.py`): theirs for every table it names, ours for the rest. Used for the schedules' rewrite.
- **A wrapped "Tables:" line** in the schedules note left the multifuel table's Method cell empty, because `build_coverage.py` reads only that line. The line is now one line.

## For Samuel's ruling

- None new.

## Files

- New: the seven notes, `tests/test_session905.py` (4 tests), this report.
- Changed:
  - `docs/methods/eia860_schedules.md`
  - `warehouse/connectors/eia411.py`, `eia_gas_pipeline_projects.py`, `eia860_schedules.py`, `eia860_environment.py`, `eia923_monthly.py`, `eia923_receipts.py`, `eia_epa_costs.py`
  - `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `docs/redivis/release-v1/`
  - the six reports
- On the data machine only: `runs/c049/` (the fix scripts and resolvers), `runs/s905*`.
