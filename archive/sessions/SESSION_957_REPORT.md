# Session 957 report: where the coal goes (EIA's Annual Coal Distribution Report)

23 October 2026, from 12:47 UTC, on lab-desktop (the data machine), a session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`, the first of its two sessions of a source of its own choosing. Model spend USD 0. Pulls: 5 requests of 20 (www.eia.gov's robots file, asked in a call of its own and read first: it allows `/coal/distribution/`; the report's page twice, by the probe and by the trial; its two workbooks).

## Read these first

- **Why this source:** the ERW holds coal mined (`eia_coal_production_annual`, `eia_coal_mine_production_annual`), its prices, and each plant's receipts (`eia_coal_receipts_annual`), but not the flows between states: which basin feeds which state's plants, by rail, river or truck. EIA's Annual Coal Distribution Report gives them, public, in two small workbooks.
- **One table written, validated, archived, in coverage (sector coal, public), in the release package, both holds:** `eia_coal_distribution_quarterly`, 1,207 rows, 2024 by quarter (the latest final year; the next release is due this month): each coal-origin state or region (EIA's 23, among them Kentucky (East) and (West), West Virginia (Northern) and (Southern), Pennsylvania (Anthracite) and (Bituminous)) to each destination state, by consuming sector (electric power, industrial, coke plants, commercial and institutional) and transportation mode (railroad, truck, river, tramway and conveyor, tidewater piers), in short tons, with EIA's U.S. rows as the total level.
- **The cross-checks:** the U.S. rows sum to 393.9 million short tons, EIA's own "total domestic coal distribution" for 2024; Wyoming's shipments 190.7 and Texas's receipts 45.7, as the report's highlights say. The electric power sector's shipments by destination state against `eia_coal_receipts_annual`'s 2024 plant receipts: within 5 percent in 29 of the 34 states above a million tons (Texas 45.5 in both; 354.6 and 351.5 million tons in all). The destination workbook holds the same 1,207 rows as the origin workbook, row for row.

## Decisions made without you

- **One year, 2024:** earlier years' workbooks sit under the report's previous editions, which this session did not open.
- **`geo` the destination state,** where the coal is burned; the origin is EIA's own state or region name in `x_origin`.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_coal_distribution.py`, `tests/test_session957.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c054/s957/`, `runs/license_reads/s957/`, `runs/s957*`, `warehouse/raw/eia_coal_distribution/`.
