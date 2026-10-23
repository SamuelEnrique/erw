# Session 923 report: chain 053 written first; every country's petroleum and natural gas (EIA's International Energy Statistics)

23 October 2026, from 09:31 UTC, on lab-desktop (the data machine), the first session of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md`, taken right after chain 051 landed. Model spend USD 0. Pulls: none (the bulk file session 909 saved).

## Read these first

- **Chain 053 written and pushed first:** `queue/next/053-day-23-october-data-world-energy-dams-solar-projects.md` (sessions 937 to 950, machine: data), committed alone and pushed to main (`21185a08`, with the queue move of 052) with a snapshot pair (`c052-053-before`, `-after`: 0 differences). Vercel posted no deployment status in ten minutes (its rate limit, as since chain 046).
- **One table written, validated, archived, in coverage (sectors oil and gas, public), in the release package, both holds:** `eia_world_oil_gas_annual`, 448,267 rows, 7,168 series, 1973 to 2025, 265 areas (220 countries, 7 former, 2 parts, 36 regions). Each area's crude oil, NGPL and other liquids production, refinery output and gain, each refined product's production and consumption, crude and LPG trade, biofuels, bunker fuel, stocks, and dry, gross, vented and reinjected natural gas production, consumption and trade. Liquids in thousand barrels a day (`kbbl/d`), gas in billion cubic feet (`bcf`), stocks in thousand barrels (`kbbl`).
- **From the same file as session 909's table, with no request:** `eia_intl_bulk.py` gains a second table (`--table eia_world_oil_gas_annual`); the electricity table, run again from the new code, is the same row for row and the same header.
- **The cross-checks:**
  - **The U.S. against EIA's own U.S. tables:** dry gas production against `eia_gas_balance_annual` within 1 percent in all 28 years held (2024: 37,767 and 37,725 bcf), consumption within 0.08 percent (33,083 and 33,056); crude production against `eia_crude_production_state_monthly`'s months summed within 1 percent in 25 of 25 full years (2024: 13,267 kbbl/d both).
  - **The world against the countries summed:** petroleum consumption and dry gas production and consumption within 0.1 percent in every year (2024: 103,110 kbbl/d of liquids; 148,970 bcf of gas produced). Crude production is not: EIA gives it by country for only 24 countries before 1984 and for 88 in 2001 to 2003 (215 from 2004), so the countries summed fall up to 23 percent short of EIA's world in those years and within 1 percent otherwise. Named in the method note to come, not mended.
- **The file holds no reserves:** the queue file's reserves are not in EIA's bulk file.

## Decisions made without you

- **The bulk file, not the API,** as session 909 decided for electricity; no request was needed.
- **Only one copy of each quantity:** barrels a day for liquids and cubic feet for gas, EIA's own primary units; its cubic metre, tonne, Btu, terajoule and oil-equivalent copies are not taken.
- **Stocks in kbbl** (EIA's million barrels times 1,000), the vocabulary having no million-barrel unit.

## For Samuel's ruling

- None new.

## Files

- New: `tests/test_session923.py` (3 tests), this report; on main, `queue/next/053-day-23-october-data-world-energy-dams-solar-projects.md`.
- Changed: `warehouse/connectors/eia_intl_bulk.py` (the second table), `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c052/s923/`, `runs/s923*`.
