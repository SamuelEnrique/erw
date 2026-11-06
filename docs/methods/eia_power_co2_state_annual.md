# EIA state electricity profiles: power plants' CO2 by state and fuel, a year

Energy Research Warehouse (ERW), method note written in session 674 (chain 043) for a table first written on 21 October 2026.

Tables: `eia_power_co2_state_annual`

Connector: `warehouse/connectors/eia_power_co2_state.py` (session 571, reported with sessions 570 to 573 in `SESSION_570_REPORT.md`).

## Publisher and report

U.S. Energy Information Administration (EIA), State Electricity Profiles, emissions by state and fuel: emissions from energy consumption at conventional power plants and combined heat and power plants. Read through EIA's API v2, route `electricity/state-electricity-profiles/emissions-by-state-by-fuel`.

- Page: `https://www.eia.gov/electricity/state/`
- API: `https://api.eia.gov/v2/electricity/state-electricity-profiles/emissions-by-state-by-fuel/data/?frequency=annual&data[]=co2-thousand-metric-tons&data[]=co2-rate-lbs-mwh&start=1990`, in pages of 5,000 records. The key is read from `EIA_API_KEY` and is redacted from every `source_url`.

Ceiling: 8 requests a run (two of session 571's 10 went to its probe), 3 seconds apart; a 429 or a 5xx is asked once more after 60 seconds. A page an earlier run saved in `warehouse/raw/eia_power_co2_state/` is reused unless `--fresh`; `--offline` asks nothing (the run that wrote the present file asked 0 of 8).

## Vintage and revision rule

Years 1990 to 2024: 8,820 records of EIA's, 10,640 rows. The start year is fixed at 1990 in the code. The table is written by `write_snapshot`: each run replaces the whole table.

## Shape

Series (`docs/datastandard.md`).

- `entity`: `eia_power_co2:<state>:<fuel>`, EIA's codes. State: the 50 states, DC and US. Fuel: COL, NG, PET, OTH, and ALL (all fuels).
- `variable` and `unit`:
  - `co2`, tCO2 (EIA's thousand metric tons times 1,000);
  - `co2_rate`, kgCO2/MWh (EIA's pounds per MWh times 0.453592).
- `ts_utc`: the year's 1 January at 00:00:00Z; `freq` P1Y; `geo` US-<state>, US for the U.S.; `node` EIA's names of state and fuel.

A sum over fuels leaves ALL out. A unit not in the map stops the run, and so does a record with no state or fuel, or a key given twice.

## License

ERW verdict: public (`docs/licenses.md`). The header's License line: public, a work of the U.S. government; cite "U.S. Energy Information Administration, State Electricity Profiles" (EIA, record 1 of `license_reads.csv`).

## Cross-check

None in the connector. Session 570's report for session 571: the CO2 runs a median 5% above session 530's electric power sector figures (1,590 state-years), which fits the profiles' inclusion of commercial and industrial combined heat and power plants.

## What it does not hold

- SO2 and NOx: EIA gives them in short tons and pounds per MWh, and the ERW's unit vocabulary has neither unit, so they are not taken (a unit question left open in session 570's report).
- A rate by fuel: in the table, `co2_rate` has a row for ALL only (1,820 rows); the fuels carry `co2` alone. A blank has no row; nothing is filled.
- Plants one by one: for plant-level emissions see `egrid_power_plants` (one data year).
- Emissions other than from energy consumption at power plants and combined heat and power plants.
