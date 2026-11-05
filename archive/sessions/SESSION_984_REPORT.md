# Session 984 report: how hard the fleet runs (EIA's Electric Power Annual, capacity factors and heat rates)

23 October 2026, from 14:06 UTC, on lab-desktop (the data machine), a session of `queue/done/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md`, the first of its two sessions of a source of its own choosing. Model spend USD 0. Pulls: 4 requests of 20 (www.eia.gov's robots file, asked in a call of its own and read first: it allows `/electricity/`; three workbooks).

## Read these first

- **Why this source:** the ERW holds every plant's generation and capacity (EIA-923, EIA-860), and Berkeley Lab's wind capacity factors, but not EIA's own published fleet capacity factors and heat rates, the figures a reader quotes. The Electric Power Annual gives them, revised 19 October 2026.
- **Three tables written, validated, archived, in coverage (sector power, public), in the release package, both holds:**
  - `eia_capacity_factors_annual` (374 rows, 17 series, 2015 to 2025) and `eia_capacity_factors_monthly` (1,224 rows, January 2023 to December 2025), from Tables 4.8.A and 4.8.B: the capacity factor and time-adjusted capacity of coal, natural gas (combined cycle, gas turbine, steam turbine, internal combustion), petroleum (three technologies), geothermal, hydroelectric, nuclear, other biomass, other fossil gas, solar (photovoltaic, thermal), wind and wood. 2025: nuclear 0.911, natural gas combined cycle 0.587, coal 0.488, wind 0.338, solar PV 0.240.
  - `eia_heat_rates_annual` (44 rows, 2015 to 2025), from Table 8.1: the average operating heat rates of coal, petroleum, natural gas and nuclear plants, EIA's Btu per kWh written as MMBtu/MWh (the same figure over 1,000; 2025: coal 10.647, natural gas 7.781).
- **The cross-check:** wind's 2025 capacity factor, 0.338 by EIA, against `lbnl_wind_capacity_factors`' capacity-weighted 0.340 for 1,210 land-based plants (session 944).

## Decisions made without you

- **Annual and monthly capacity factors as two tables:** a year's row and its January share `ts_utc`, so one table cannot hold both.
- **Technology "all"** where EIA gives a fuel without one (coal, hydro, nuclear, wind and the rest).

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_epa_tables.py`, `tests/test_session984.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c055/s984/`, `runs/license_reads/s984/`, `runs/s984*`, `warehouse/raw/eia_electric_power_annual/`.
