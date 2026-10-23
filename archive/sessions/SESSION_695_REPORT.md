# Session 695 report: distribution reliability by utility, a public source the ERW did not hold

23 October 2026, from 00:40 UTC, on lab-desktop (the data machine), a session of `queue/done/045-evening-22-october-data-resumed.md`. Model spend USD 0.

## Read these first

- **No reading of NERC's terms is recorded** (record 89 of `license_reads.csv` says "not read"; no verdict row), so NERC was not asked and the session took a public source the ERW did not hold, as the chain says.
- **First choice, set aside:** EIA's Electric Power Annual once republished NERC's capacity margins by region (its old tables 4.1 and 4.2); the current edition's index (1 request) holds no such table, so reserve margins have no public source yet.
- **`eia861_utility_reliability` is written: 90,705 rows, 1,215 distribution utilities in 1,288 utility-states, 2015 to 2025**: SAIDI, SAIFI and CAIDI under the IEEE 1366 standard (with and without major event days, and with loss of supply removed) and under the utility's own method, with the customers each covers. From the reliability file inside the EIA-861 zips already saved (no request for the data). Validated, archived, in coverage (sector power, public), in the release package, both holds; method `docs/methods/eia861_utility_reliability.md`, linked from coverage's Method column.
- **Why this source:** a site's grid reliability is a siting question the warehouse could not answer, and it joins `eia861_utility_sales` and `utility_service_territories` on EIA's utility number.
- **Three units join the vocabulary (Decision 51):** `minute/customer` (SAIDI), `interruption/customer` (SAIFI), `minute/interruption` (CAIDI), in the validator and `docs/datastandard.md` together.
- **The cross-check** against EIA's own State Totals sheet (2023 to 2025, customer-weighted IEEE figures by state): 2023 and 2024 agree (SAIDI within 1 percent in all 51; customers within 1 percent in 96 to 98 percent). **2025 does not**: EIA's 2025 totals cover fewer customers than its 2025 utility rows in several states (Missouri 1,335,817 against 2,780,993, while the 2025 rows match 2024's 2,767,867). The table holds the utility rows as EIA gives them; the method note says so.
- The layouts changed twice (2019 a Short Form column; 2021 on, a heading row for the events); every column is found by its headings, and EIA's 2015 to 2020 "CAIDI Minus MED" is read as the IEEE loss-of-supply CAIDI where 2021 on puts it.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.eia.gov | 1 of 20 | the Electric Power Annual's index (no capacity-margin table) |
| none | 0 | the reliability data: the EIA-861 zips saved on 21 October |

## Decisions made without you

- Distribution reliability in place of reserve margins, which have no public source the ERW can read.
- Decision 51's three units, named as EIA's indices are defined (per customer, per interruption, over the row's year).
- The 2015 to 2020 "CAIDI Minus MED" heading read as the IEEE loss-of-supply CAIDI.
- EIA's State Totals sheet used for the cross-check only, not taken as rows.
- The connector reads an `/archive/` year only from a zip already saved (EIA's robots file disallows the path).
- The connector shares `eia861_sales.py`'s page, zip and years helpers (a second connector needed them; the territories connector already imports the first three).

## For Samuel's ruling

- None new. (NERC's terms, read in a browser, stay on the list for reserve margins.)

## Files

- New: `warehouse/connectors/eia861_reliability.py`, `docs/methods/eia861_utility_reliability.md`, `tests/test_session695.py` (5 tests), this report. Changed: `warehouse/validate/erw_validate.py` and `docs/datastandard.md` (Decision 51), `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c045/s695/`, `runs/s695_*`, `runs/license_reads/s695/`.
