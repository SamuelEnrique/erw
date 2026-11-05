# EIA state electricity profiles: utilities' energy efficiency programs, savings and costs by state and sector, a year

Energy Research Warehouse (ERW), method note written in session 674 (chain 043) for a table first written on 21 October 2026.

Tables: `eia_energy_efficiency_state_annual`

Connector: `warehouse/connectors/eia_energy_efficiency.py` (session 560, a public source chosen by the chain's rule after PHMSA's pipeline incident data answered HTTP 403).

## Publisher and report

U.S. Energy Information Administration (EIA), State Electricity Profiles, energy efficiency (Form EIA-861's demand-side management), read through EIA's API v2, route `electricity/state-electricity-profiles/energy-efficiency`.

- Page: `https://www.eia.gov/electricity/state/`
- API: `https://api.eia.gov/v2/electricity/state-electricity-profiles/energy-efficiency/data/?frequency=annual&data[]=energy-savings&data[]=potential-peak-savings&data[]=customer-incentive&data[]=all-other-costs&start=2013`, in pages of 5,000 records. The key is read from `EIA_API_KEY` and is redacted from every `source_url`.

Ceiling: 17 requests a run (three of session 560's 20 went to its probes), 3 seconds apart; a 429 or a 5xx is asked once more after 60 seconds. A page an earlier run saved in `warehouse/raw/eia_energy_efficiency/` is reused unless `--fresh`; `--offline` asks nothing (the run that wrote the present file asked 0 of 17).

## Vintage and revision rule

Years 2013 to 2024: 4,935 records of EIA's, 19,740 rows. The start year is fixed at 2013 in the code. The table is written by `write_snapshot`: each run replaces the whole table.

## Shape

Series (`docs/datastandard.md`).

- `entity`: `eia_efficiency:<state>:<time period slug>:<sector>`.
  - State: the 50 states, DC and US.
  - Time period, EIA's own, as a slug: `reporting_year` and `expected_life_cycle_of_programs`, as EIA names them.
  - Sector: RES, COM, IND, TRN, and TOT (all sectors).
- `variable` and `unit`:
  - `energy_savings`, MWh;
  - `potential_peak_savings`, MW;
  - `customer_incentive` and `all_other_costs`, USD (EIA's thousand dollars times 1,000).
- `ts_utc`: the year's 1 January at 00:00:00Z; `freq` P1Y; `geo` US-<state>, US for the U.S.; `node` EIA's names of state, time period and sector.

A sum over sectors leaves TOT out, and the two time periods are not added together. A unit not in the map stops the run, and so does a record with no state, time period or sector, or a key given twice.

## License

ERW verdict: public (`docs/licenses.md`). The header's License line: public, a work of the U.S. government; cite "U.S. Energy Information Administration, State Electricity Profiles" (EIA, record 1 of `license_reads.csv`).

## Cross-check

None in the connector. Session 560's report, internal: the sectors sum to EIA's all-sector figure in all 987 state-periods, and the states sum to the U.S. in every year. The U.S. reporting-year savings run from 24.7 TWh (2013) to 28.6 TWh (2019).

## What it does not hold

- The reporting year after 2019: EIA gives the time period "Reporting Year" for 2013 to 2019 only; "Expected Life Cycle of Programs" runs 2013 to 2024.
- Utilities one by one: the profiles are by state.
- Any column beyond the four the connector names.
- A blank has no row; nothing is filled.
