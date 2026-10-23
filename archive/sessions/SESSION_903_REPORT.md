# Session 903 report: a source the ERW did not hold: the Electric Power Annual's heat rates and operating costs

23 October 2026, from 06:55 UTC, on lab-desktop (the data machine), a session of `queue/done/049-day-23-october-data-margins-schedules-emissions.md`. Model spend USD 0. Pulls: EIA, 4 requests of 20 (the four workbooks; EIA's robots file and the annual's page were read by session 895).

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `eia_power_costs_annual`, 550 rows, 2015 to 2025, from the Electric Power Annual's chapter 8:
  - average operating heat rate by energy source, and average tested heat rate by prime mover and energy source (MMBtu/MWh, EIA's Btu per kWh divided by 1,000);
  - the major investor-owned utilities' revenue and expenses, line by line: operation (production with fuel and purchased power, transmission, distribution, customer accounts and service, sales, administration), maintenance, depreciation, taxes and net operating income (USD);
  - their power plants' operation, maintenance, fuel and total expenses by plant type: nuclear, fossil steam, hydroelectric, gas turbine and small scale (USD/MWh, EIA's mills per kWh).
- **Why this source:** the platform's cost of power tools have had no federal series of what it costs to run each kind of plant, and of a utility's costs by function. In 2025, a nuclear plant's total expense was 23.89 USD/MWh, a fossil steam plant's 42.12, a gas turbine's 28.22.
- **The cross-checks:**
  - Table 8.3's parts sum to their totals in all 11 years: revenues, electric expenses, and production.
  - Table 8.1's 2025 heat rates against EIA-923's 2025 plants (session 897's table), fuel used for electricity over net generation: nuclear 10.443 against 10.445 MMBtu/MWh; natural gas 7.781 against 7.636, about 2 percent apart. EIA does not state how it weights the annual figure, so the gap is reported as found.

## Decisions made without you

- **Mills per kWh as USD/MWh,** the same number. Btu per kWh as MMBtu/MWh, the unit the standard has (Decision 26).
- **Table 8.3's lines as a path of their parents,** read from the dots EIA indents them with, so a sum takes one level.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_epa_costs.py`, `tests/test_session903.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c049/`, `runs/s903*`.
