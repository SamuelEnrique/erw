# Natural gas vehicle fuel, pipeline fuel and deliveries by state, and lease and plant fuel for the nation, a year (EIA Natural Gas Annual)

Energy Research Warehouse (ERW), method note written in session 2171 (chain 094) for a table first written on 24 October 2026 (session 2164, `archive/sessions/SESSION_2164_REPORT.md`).

Tables: `eia_gas_other_uses_state_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), Natural Gas Annual, consumption by end use and state (`https://www.eia.gov/naturalgas/annual/`), through API v2, route `natural-gas/cons/sum`, annual, four processes: `https://api.eia.gov/v2/natural-gas/cons/sum/data/?frequency=annual&data[]=value&facets[process][]=VDV&facets[process][]=VGL&facets[process][]=VGP&facets[process][]=VGT&start=2001` (the key redacted in every saved address). Source id `eia:natural-gas/cons/sum:annual`, its own, so the monthly table's row of `sources.csv` is untouched. Pages saved under `warehouse/raw/eia_gas_other_uses_state/`.

Connector: `warehouse/connectors/eia_gas_other_uses_state.py` (session 2164): `[--from 2001] [--offline | --fresh]`, pages of 5,000, ceiling 15 requests, a saved page reused unless `--fresh`. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

One run, `20261024T002902Z`, from the saved page ("0 requests of 15"); every row's `retrieved_at` is 2026-10-24T00:29:02Z; `vintage` empty. The table is a snapshot: a run replaces it whole. EIA counted 3,871 records; 3,838 have a value.

## Shape and variables

Series, 3,838 rows, 157 series, 52 areas (the 50 states, DC and the nation), 2001 to 2025, `unit` MMcf, `freq` P1Y, `geo` US-<state> or US, `node` EIA's series name. `entity` `eia_gas_other_uses:<process>:<area>` (area S<state> or NUS).

| `variable` | EIA process | Series | Rows |
|---|---|---|---|
| delivered_to_consumers (residential, commercial, industrial, electric power and vehicle fuel together: leave it out of a sum) | VGT | 52 | 1,291 |
| consumption_vehicle_fuel | VDV | 52 | 1,277 |
| consumption_pipeline_fuel (pipeline and distribution use) | VGP | 52 | 1,245 |
| consumption_lease_and_plant_fuel (one figure) | VGL | 1 (the nation) | 25 |

The nation in 2025: delivered 30,181,736 MMcf, lease and plant fuel 2,038,482, pipeline fuel 1,295,483, vehicle fuel 53,149.

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z. A figure EIA withholds (a blank in the API) has no row; nothing is filled. 95 values are zero (vehicle fuel 92, pipeline fuel 3); none is negative. Missing area-years: pipeline fuel for every state in 2025 (51) and for one area in each of 2001, 2002, 2003 and 2019; delivered for 9 states in 2025 (CO, IA, KY, MD, NJ, NV, PA, WA, WV); vehicle fuel for 23 area-years from 2006 to 2018.

## License

Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Annual")." The docstring names EIA's record 1 of `license_reads.csv`.

## Checks (session 2171)

The figures in this note were computed from the rows of `warehouse/output/eia_gas_other_uses_state_annual.csv`, read past its 10 header lines (scripts in `runs/c094/s2171/`).

- 3,838 rows, `ts_utc` from 2001-01-01T00:00:00Z to 2025-01-01T00:00:00Z; no (entity, variable, ts_utc) twice.
- The states against the nation: for delivered, vehicle fuel and pipeline fuel, the states sum to within 0.1 percent of the nation in every year from 2001 to 2024 (to 1 MMcf in 11 to 12 of the 25 years); in 2025 the states hold no pipeline fuel and their delivered volumes sum to 0.8473 of the nation's, nine states being withheld. Vehicle fuel never exceeds delivered.
- Session 2164's cross-check (`runs/c094/s2164/cross.py`), run again: its output is identical to the saved `cross.out`.
  - Delivered plus lease and plant plus pipeline fuel against the nation's total consumption (`eia_gas_consumption_state_monthly`, VC0 summed over full years; the nation only): equal to 1 MMcf in 17 of 25 years, within 0.5 percent in the other 8 (2020: 30,602,565 against 30,574,245; 2017: 27,139,699 against 27,142,481).
  - Delivered against the monthly table's residential, commercial, industrial and electric power summed to the year plus vehicle fuel: 1,214 state-years, median 1.0000, from 0.9994 to 1.1987.

## Where the description and the data disagree

1. **Lease and plant fuel is the nation's only.** The docstring and header describe the four processes by state (entity `<process>:<area>`, area S<state> or NUS); EIA's route gives lease and plant fuel for the nation alone in this table: 1 series, 25 rows, `eia_gas_other_uses:VGL:NUS`. No state's total consumption can be rebuilt from this table.
2. **The cross-check named.** The docstring says total consumption equals the three parts "(eia_gas_balance_annual's total_consumption, session 2164's cross-check)"; the cross-check compares with `eia_gas_consumption_state_monthly`'s VC0 (the report's errors record the switch from `eia_gas_balance_annual`).
3. **2025 is partial.** The header gives "Years 2001 to 2025" without saying that 2025 holds no state pipeline fuel and lacks nine states' deliveries (97 rows against 157 in each of 2022 to 2024).

## The session report against the table

The figures of `SESSION_2164_REPORT.md` checked against the table, the code and the rerun cross-check hold (3,838 rows, 157 series, 2001 to 2025, MMcf, the nation's 2025 figures, 17 of 25 years to 1 MMcf and 8 within 0.5 percent with 2020's 30,602,565 against 30,574,245, median 1.0000 over 1,214 state-years from 0.9994 to 1.1987, 2 requests), except:

- "natural gas by end use and state ... the same route's four other processes, a year ... 157 series (the states, DC and the nation)": three processes are held by state; lease and plant fuel only for the nation (the 157 series are 52 + 52 + 52 + 1).

Acted on in session 2171: the docstring and header now say lease and plant fuel is the nation's only and the latest year may be partial (the header counts the last two years' rows), and the docstring names the cross-check's table; the table was written again offline, its rows unchanged; session 2164's report is corrected.

## What it does not hold

- Residential, commercial, industrial and electric power use (`eia_gas_consumption_state_monthly`), lease and plant fuel by state, and months.
