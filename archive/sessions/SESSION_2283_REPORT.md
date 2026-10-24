# Session 2283 report: Argentina: not taken (CAMMESA resets every connection); U.S. gas storage by type (EIA) in its place

24 October 2026, from 05:16 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/104-day-7-november-data-portugal-italy-japan-argentina.md`, unattended. Model spend USD 0. Pulls: 2 requests to CAMMESA, then EIA's API, 4 requests (below).

## Read these first

- **CAMMESA's hosts reset the connection** at their robots files: cammesaweb.cammesa.com (read 498) and api.cammesa.com (read 499). Neither is asked again, so Argentina is not taken.
- **U.S. underground gas storage by type in its place,** under the queue file's rule: the split between salt caverns and other fields, which the ERW did not hold. Its regional and weekly storage tables have no such split. EIA's verdict is on record.
- **One table written, validated, archived, in coverage (sector gas), in the release package, both holds:** `eia_gas_storage_type_monthly`, December 1973 to July 2026, 8,367 rows, 18 series, in MMcf (already in the vocabulary).
  - Base gas, working gas, total, injections, withdrawals and net withdrawals, for all fields and for salt and non-salt.
  - Each row carries the time EIA served its page (chain 101's session 2247 fix, inherited from its template).
- **The cross-check** (`runs/c104/s2283/cross.py`, `cross.out`):
  - **EIA's arithmetic closes within its rounding** over the 391 months with the split: salt plus non-salt equals all fields, base plus working equals total, and withdrawals less injections equals net. The largest gap is 1,072 MMcf, EIA's figures rounded to the bcf in some months.
  - **The U.S. working gas equals `eia_gas_storage_state_monthly`'s U.S. total** exactly in all 307 months both hold.
  - Salt caverns' share of working gas rose from 3.6% (1995 mean) to 10.3% (2025).

## The pulls

1. cammesaweb.cammesa.com/robots.txt (read 498): the connection reset.
2. api.cammesa.com/robots.txt (read 499): the connection reset.
3. EIA's route metadata (1973-01 to 2026-07) and one page of 2025.
4. The trial's two pages. The write reused them (0 requests).

## Errors

- None.

## Decisions made without you

- **EIA's storage by type in Argentina's place,** for the reasons above.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_gas_storage_type.py`, `tests/test_session2283.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (498, 499)
  - the coverage, sources, archive manifest and license files
  - `docs/redivis/release-v1/`
- On the data machine only: `runs/c104/s2283/`, `runs/license_reads/s2283/`, `runs/s2283_*`, `warehouse/raw/eia_gas_storage_type/`.
