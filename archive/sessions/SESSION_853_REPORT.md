# Session 853 report: EIA-861's delivery-only companies, Texas's wires utilities

23 October 2026, from 01:47 UTC, on lab-desktop (the data machine), a session of `queue/done/046-night-22-october-data-sources-gaps.md`. Model spend USD 0. Pulls: none (the saved EIA-861 zips).

## Read these first

- **`eia861_delivery_only` is written: 546 rows, 7 companies, 2020 to 2025**: the delivery revenue (USD), energy delivered (MWh) and customers by sector of the companies EIA files apart, in `Delivery_Companies_<year>.xlsx`: AEP Texas Central, AEP Texas North, CenterPoint Energy, Oncor, Texas-New Mexico Power, the City of Lubbock and Nueces Electric Cooperative. Validated, archived, in coverage (sector power, public), in the release package, both holds. This fills "a Texas wires utility's own revenue" (the ERCOT row of `siting-gaps.md`): CenterPoint's delivery revenue was USD 2.42 billion in 2020 and 3.48 billion in 2025.
- **What the chain assumed and what the files hold:** there is no "Delivery_Only_Service" sheet. EIA's sales file holds part C rows for other states (11,442 rows in `eia861_utility_sales`), and from 2020 puts Texas's delivery companies in a file of their own; 2015 to 2019's zips have none. None of the 7 is in `eia861_utility_sales` (checked key by key in the run, `--check-sales`), so a separate table moves no figure that reads the sales table.
- **The cross-check:** in Texas the retail providers file as part D (power marketers, all in ERCOT). The energy the wires companies deliver is 1.03 to 1.04 times part D's ERCOT sales every year (2025: 350.7 against 338.3 TWh; 2020: 268.0 against 259.1), the rest being Lubbock's and Nueces's own retail customers among the deliveries.
- The reader is `eia861_sales.py`'s own `sheet_rows` (the layouts are the same), so the entity and variables are the sales table's.

## Decisions made without you

- A table of its own rather than rows added to `eia861_utility_sales` (the chain's "no page's default figure moves": the siting tab's stand-in reads the sales table).
- The chain's name `eia861_delivery_only` kept, though EIA calls the file "Delivery Companies".

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia861_delivery.py`, `tests/test_session853.py` (2 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c046/s853*`, `runs/s853_*`.
