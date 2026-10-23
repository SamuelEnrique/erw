# Session 851 report: ERCOT's capacity, demand and reserves report

23 October 2026, from 01:38 UTC, on lab-desktop (the data machine), a session of `queue/done/046-night-22-october-data-sources-gaps.md`. Model spend USD 0.

## Read these first

- **`ercot_cdr_reserve_margins` is written: 1,600 rows**, the newest Capacity, Demand and Reserves report (December 2025, posted 19 December 2025): 20 seasons (summer, fall, winter and spring, 2026 to 2030), each at the peak load hour and the peak net load hour, with 40 rows of ERCOT's Seasonal Summary: the load forecast and each adjustment, the capacity counted by kind (thermal, hydro, wind and solar by region at their ELCCs, storage, private use networks, DC ties, planned additions), the firm peak load, the total capacity and the reserve margin (pct). Validated, archived, in coverage (sector power, public), in the release package, both holds. This fills reserve margins for ERCOT (`siting-open-2026-10-23.md`, item 20), with no need of NERC's terms.
- **What it says:** the summer reserve margin at the peak load hour is 18.3 percent in 2026, 11.4 in 2027, then negative: -1.3 in 2028, -5.8 in 2029, -12.7 in 2030, as ERCOT's load forecast (with its large loads) outruns the capacity with signed agreements.
- **The cross-checks:** in every one of the 40 columns, ERCOT's own arithmetic holds in the table to the rounding of the sheet (the reserve margin recomputed from total capacity and firm peak load; the firm peak load from the forecast and its adjustments; each total from its parts). Against the warehouse: the summer 2026 normal-weather load (95,419 MW) is 1.14 times EIA-930's 2025 ERCOT peak (83,597 MW, `grid_peak_vs_capacity`); the capacity the CDR counts (104,850 MW) is 0.64 of the nameplate `grid_peak_vs_capacity` lists (164,685 MW), the difference being the ELCC derating of wind, solar and storage.
- The page and the workbook are under `/gridinfo/` and `/files/docs/`, which ERCOT's robots file allows (it disallows `/misapp` and `/misdownload`, session 850).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.ercot.com | 4 of 6 | the probe's page and workbook (the robots file was read by session 850 this night), then the trial's page and workbook into `warehouse/raw/ercot_cdr/`, which the write reused |

## Decisions made without you

- Each season's row dated at its first day (summer 1 June, fall 1 September, winter 1 December of its first year, spring 1 March), `freq` `P3M`; the hour ERCOT names kept in `x_hour`.
- The reserve margin stored in pct (ERCOT's fraction times 100), the rest in MW as printed.
- The report's "Difference" columns left out (they are the two hours' difference).
- A row label the connector's map does not know stops the run, so a changed report is never misread.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/ercot_cdr.py`, `tests/test_session851.py` (4 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c046/s851/`, `runs/s851_*`, `runs/license_reads/s851/`.
