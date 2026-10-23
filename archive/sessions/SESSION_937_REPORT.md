# Session 937 report: chain 054 written first; every country's coal, total energy and CO2 emissions (EIA's International Energy Statistics)

23 October 2026, from 10:57 UTC, on lab-desktop (the data machine), the first session of `queue/done/053-day-23-october-data-world-energy-dams-solar-projects.md`, taken right after chain 052 landed. Model spend USD 0. Pulls: 2 requests of 4 (EIA's robots file, asked in a call of its own and read first; a HEAD of the bulk file, whose Last-Modified, 19 October 2026, and length equal the saved file's).

## Read these first

- **Chain 054 written and pushed first:** `queue/next/054-day-23-october-data-federal-royalties-wind-costs-minerals.md` (sessions 951 to 964, machine: data), committed alone and pushed to main with the queue move of 053 (`e2d5d45c`; `git status -sb` showed nothing ahead), with a snapshot pair (`c053-054-before`, `-after`: 0 differences; Vercel rate-limited the deploy).
- **Two tables written, validated, archived, in coverage (sectors coal and carbon, public), in the release package, both holds,** from the bulk file chain 051 saved, the fourth and fifth tables of `eia_intl_bulk.py`; the three earlier tables, run again from the new code, are the same row for row:
  - `eia_world_coal_annual`: 317,307 rows, 1,854 series, 1980 to 2024: each area's coal and its kinds' (anthracite, bituminous, subbituminous, lignite, metallurgical coal, coke) production, consumption, imports and exports, and coal reserves; in short tons.
  - `eia_world_energy_co2_annual`: 246,988 rows, 3,701 series, 1949 to 2025: total primary energy production and consumption, in all and by source (TBtu), and energy-related CO2 emissions by fuel (tCO2). Before 1980 only the U.S. and the groups that hold it have rows.
- **The cross-checks:**
  - **The U.S. against EIA's U.S. tables:** coal production against `eia_coal_production_annual` equal in 24 of 24 years (2024: 512,540,324 short tons in both); CO2 from all fuels against `eia_co2_state_annual`'s U.S. total within 0.7 percent in 53 of 53 years (2022: 4,938 and 4,934 million tonnes); total energy consumption against SEDS's (`eia_seds_state_energy`) within 0.2 percent in 35 of 35 years (2024: 94,556 and 94,543 TBtu).
  - **The world against the countries summed:** coal production and consumption, total energy consumption and CO2 within 0.04 percent in every year (2023: 9,589 million short tons of coal produced; 592,033 TBtu of energy consumed; 37,315 million tonnes of CO2).

## Decisions made without you

- **Two tables, not one,** as the queue file asked "tables of their own": coal in tons, and energy with emissions.
- **EIA's by-product copies of CO2 (products 1, 5 and 3002) kept beside its totals (4002, 4006, 4010, 4008),** as EIA gives them, each named in the header.

## For Samuel's ruling

- None new.

## Errors

- The second write's metadata patch met the first's in `sources.csv` (both tables of one source); joined by `runs/union_resolve.py` and the duplicate source row merged by hand, as session 929 did. The first `finish_table.sh` run's release check failed only because the second table was not yet in the package; after the second run it passes (0 differences).

## Files

- New: `tests/test_session937.py` (2 tests), this report; on main, `queue/next/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`.
- Changed: `warehouse/connectors/eia_intl_bulk.py` (two tables), `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c053/s937/`, `runs/license_reads/s937/`, `runs/s937*`.
