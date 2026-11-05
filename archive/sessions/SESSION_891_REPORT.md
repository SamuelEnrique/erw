# Session 891 report: method notes for chain 048's tables, and what their checks corrected

23 October 2026, from 05:21 UTC, on lab-desktop (the data machine), a session of `queue/done/048-night-23-october-data-utility-files-products.md`. Model spend USD 0 (the notes were drafted by three helper agents of this session and checked here). Pulls: none.

## Read these first

- **Eight new method notes and one extended:** `eia861_efficiency.md`, `eia861_operations.md`, `eia861_distribution.md` (two tables), `eia860_schedules.md` (four tables), `eia_international_electricity_annual.md`, `cer_electricity_trade.md`, `frb_utility_output_monthly.md`, `uspvdb_solar_facilities.md`, and `eia_petroleum_exports_by_destination.md` with a section on session 884's seven products. Coverage's Method column links each of the thirteen tables (`tests/test_session891.py`).
- **The notes' checks found four faults in the tables or their headers, each fixed, tested and written again (the same rows):**
  - `eia861_distributed_generation`: the column written as `x_data_type` ("A actual, E estimated") holds EIA's column "Type", AC or DC; renamed `x_capacity_type`. EIA's "Storage" became "Battery", with "Battery Energy (MWh)" and a state-level sheet, in 2023, not 2025.
  - `eia_petroleum_exports_by_destination`: the connector stamped every row with the run's time, even the rows of pages session 860 fetched two and a half hours earlier. A reused page now carries the time it was really fetched (a test added); crude oil's and the total's rows carry 02:15:57 to 02:16:39 UTC again.
  - `frb_utility_output_monthly`: the header's list of codes left out `G221111A4T8` and called `N2212T` (gas transmission) a sale; the header now also gives each series' last month (the detailed series end in July 2026, the aggregates in September).
  - `uspvdb_solar_facilities`: not "every ground-mounted facility of 1 MW (AC) and more". 52 are under 1 MW AC and 619 are rooftop, canopy or floating; the header counts both.
- **Eight reports corrected** (881 to 886, 889, 890), each with a closing section "Corrected by session 891" that leaves its text as written. Among them: session 889's utilization figures belong to electric power (`G2211`), not to the utilities' series; the operational data's NERC region is empty in 44,256 rows; the exports' "73 of 12,311" is 88 by any amount, 73 beyond the check's tolerance.
- **Two stale coverage rows mended:** `eia861_utility_reliability` and `eia_coal_receipts_annual` stood on main as "blocked (1 errors)", written by coverage builds that ran with a validator not yet knowing their units (Decisions 51 and 52). Both pass; their rows were built again.

## Decisions made without you

- The notes drafted by helper agents in parallel with session 892, each told to take every number from the connector, the report or the table and to list every contradiction it found; every contradiction listed was checked here against the table and acted on.
- A report is corrected by an added section, not by rewriting what the session wrote.
- The owners' ZIP codes that lost their leading zeros (EIA's cells are numbers) are kept as read and named in the note, not padded.

## For Samuel's ruling

- None new.

## Files

- New: the eight notes above, `tests/test_session891.py`, this report.
- Changed:
  - `docs/methods/eia_petroleum_exports_by_destination.md`
  - `warehouse/connectors/eia861_distributed_generation.py`, `eia_petroleum_exports.py`, `frb_utility_output.py`, `uspvdb.py`
  - `tests/test_session883.py`, `tests/test_session884.py`
  - `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `docs/redivis/release-v1/`
  - the eight reports
- On the data machine only:
  - `runs/c048/` (the fix scripts, `ours_with_theirs_table.py`, `correct_reports.py`)
  - `runs/s891*`
