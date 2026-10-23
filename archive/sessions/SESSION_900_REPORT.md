# Session 900 report: each plant's fuel receipts and costs (EIA-923 Schedule 2)

23 October 2026, from 06:39 UTC, on lab-desktop (the data machine), a session of `queue/done/049-day-23-october-data-margins-schedules-emissions.md`. Model spend USD 0. Pulls: none (the 2025 zip session 897 saved).

## Read these first

- **One events table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `eia923_fuel_receipts`, 36,733 deliveries to 967 plants, January to December 2025. Each delivery carries its supplier, purchase type and contract expiry, energy source and fuel group, the coal mine (type, state, county, MSHA id, name), quantity in short tons, barrels or Mcf (`x_quantity_unit`), heat, sulfur, ash, mercury, moisture and chlorine content, fuel cost (cents per MMBtu, all costs of purchase and delivery to the plant), transport modes and gas contract types.
- **An id of its own:** EIA gives a delivery no id, so `event_id` is the plant, the month and the first 12 characters of the SHA-1 of the row as EIA gives it. 51 rows repeat with every field the same and are kept once (chain 030's rule); they may be separate deliveries, and the header says so.
- **The cross-check, against `eia_coal_receipts_annual` (session 875, EIA's coal API) by plant for 2025:** the coal deliveries summed equal the annual table within 1 percent for 145 of the 166 plants both hold, and within 5 percent for 147. In total there are 381.0 million short tons here against 372.4 million there, which leaves out records without a key. 201 plants received coal here.
- Session 900 was first planned for BOEM's offshore wind leases, which the ERW already holds (`boem_renewable_leases`); chain 048's session 894 changed it to this.

## Decisions made without you

- **The deliveries as events,** not a series: the page has no key, and a month can carry several deliveries of one fuel from one supplier.
- **`price` and `currency` left empty:** the fuel cost is in cents per MMBtu, which the events shape's price (per MWh) does not fit. It is kept in `x_fuel_cost` with its unit in the header.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia923_receipts.py`, `tests/test_session900.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c049/`, `runs/s900*`.
