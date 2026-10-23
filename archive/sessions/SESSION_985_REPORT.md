# Session 985 report: EPA's eGRID subregions

23 October 2026, from 14:13 UTC, on lab-desktop (the data machine), the second of `queue/done/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md`'s two sessions of a source of its own choosing. Begun by the chain's first agent, which wrote the connector, its test and a trial and committed them with session 986's report (`13c8bfc8`), then stopped at 14:19 UTC while the daily run held the data lock; the write and this report are a second agent's, from 16:20 UTC, when the lock was free. Model spend USD 0. Pulls: none (the eGRID2023 workbook `egrid.py` saved on 21 October).

## Read these first

- **Why this source:** the ERW holds eGRID's plants (`egrid_power_plants`) but not the regional figures readers quote, the subregions' emission rates and resource mix, which come from the same workbook's subregion sheet.
- **One table written, validated, archived, in coverage (sectors power and carbon, public), in the release package, both holds:** `egrid_subregions_annual`, 540 rows: the 27 eGRID subregions' nameplate capacity, net generation, CO2 and CO2-equivalent emissions (tCO2), total, CO2e and non-baseload output emission rates (kgCO2/MWh), and resource mix (13 shares), data year 2023. 4,191.0 TWh and 1,458.5 million tCO2 in all.
- **The cross-check:** against `egrid_power_plants` summed by subregion, net generation, CO2 and nameplate capacity agree within 0.5 percent in all 27 subregions, and the totals both ways (4,191.0 TWh, 1,458.5 million tCO2).
- **Its method note** is `docs/methods/egrid_subregions_annual.md`, written by chain 056's session 2009 (session 987 could not: the table was not yet written).

## Decisions made without you

- **eGRID's units converted** (short tons to metric tons by 0.90718474, lb/MWh to kg/MWh by 0.45359237), as the ERW's carbon units require; the resource mix as a fraction.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/egrid_subregions.py`, `tests/test_session985.py` (3 tests; committed with session 986), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml` (with session 986), `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c055/s985/`, `runs/s985*`.
