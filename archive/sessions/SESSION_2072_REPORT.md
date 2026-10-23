# Session 2072 report: every sector's emitters (EPA's Greenhouse Gas Reporting Program)

23 October 2026, from 20:13 UTC, on lab-desktop (the data machine), the third session of `queue/done/067-day-25-october-data-neighbours-emitters-disasters-world-oil.md`. Model spend USD 0. Pulls: 2 requests of 20 (www.epa.gov's robots file, asked in a call of its own and read first; the program's data sets page, which still links the 2023 summary, posted in October 2024). The summary zip itself was already on this machine (`warehouse/raw/ghgrp/`, saved on 21 October by `ghgrp_power.py`, the same address) and was reused, not asked again. EPA's verdict stands (read 55).

## Read these first

- **One table written, validated, archived, in coverage (sectors carbon, power, oil and gas, public), in the release package, both holds:** `epa_ghgrp_facility_emissions`, 70,338 rows: every reporting facility's total reported emissions a year, 2015 to 2023, in metric tons of CO2 equivalent, from the six emitting segments of EPA's by-year workbook: direct point emitters (8,205 facilities: power plants, refineries, chemicals, waste, metals and the rest), onshore oil and gas production (830), gathering and boosting (476), transmission pipelines (240 facility-states), local distribution companies (189) and SF6 from electrical equipment (137). Each row carries the facility's FRS id, NAICS code, industry types by subpart and sector, basin and county.
- **A new unit, `tCO2e`** (metric tons of CO2 equivalent, AR4 global warming potentials, Decision 61), added to `docs/datastandard.md` and the validator together; the write ran with the branch's validator, kept through the coverage step (the row reads "pass"). The held power table, `epa_ghgrp_power_co2`, kept CO2 alone for want of this unit (session 492); it is not changed.
- **Pipelines and distribution companies are listed a row a state** where the emissions occur: their entity is `ghgrp:<facility id>:<state>`, with `x_emission_state`; a distribution company that names no such state keeps `ghgrp:<facility id>`, its geo the reported state: one row of the table, `ghgrp:1008674` in 2015 (seven rows of the workbook name no state; the others have no value from 2015, found by session 2079).
- **Not taken:** the suppliers' sheet (the greenhouse gas in fuels and gases supplied, not emitted), CO2 injection and geologic sequestration (quantities, not emissions), and the years before 2015 (the workbook holds 2011 on).

## The cross-check

The direct emitters against `epa_ghgrp_power_co2`'s non-biogenic CO2 for the same facilities and years (`runs/c067/s2072/cross.py`): 10,071 facility-years of 1,284 power plants, 2015 to 2023. **CO2e over CO2: median 1.0010, 5th percentile 1.0010, 95th 1.0081; no facility-year has CO2e below its CO2.** Summed, 1,930.6 against 1,919.5 million tons in 2015 and 1,445.4 against 1,439.1 in 2023: a power plant's methane and nitrous oxide add a tenth of a percent to its CO2.

## Errors

- **Three trials stopped before the fourth wrote:** a transmission pipeline given a row a state (the key now includes the state), a state written as a code where the others give names (both accepted now), and the distribution companies that name no state (they keep the facility's id; one row of the table, session 2079).

## Decisions made without you

- **`tCO2e` as a unit of its own** (Decision 61), never summed with `tCO2`.
- **One series table** with the facility's attributes in each row, not a separate entities table.
- **From 2015,** as the chain file asked.
- **The saved zip reused,** the page asked again to confirm it is still the newest.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/ghgrp_facilities.py`, `tests/test_session2072.py` (3 tests), this report.
- Changed: `docs/datastandard.md` (Decision 61), `warehouse/validate/erw_validate.py`, `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (228), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c067/s2072/`, `runs/license_reads/s2072/`, `runs/s2072*`, `warehouse/raw/ghgrp/` (the page's copy of today).
