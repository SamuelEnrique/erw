# EIA state electricity profiles: each state's electricity supply and disposition, a year

Energy Research Warehouse (ERW), method note written in session 674 (chain 043) for a table first written on 21 October 2026.

Tables: `eia_state_source_disposition_annual`

Connector: `warehouse/connectors/eia_state_disposition.py` (session 544).

## Publisher and report

U.S. Energy Information Administration (EIA), State Electricity Profiles, supply and disposition, read through EIA's API v2, route `electricity/state-electricity-profiles/source-disposition`, whose records carry every column of a state's year.

- Page: `https://www.eia.gov/electricity/state/`
- API: `https://api.eia.gov/v2/electricity/state-electricity-profiles/source-disposition/data/?frequency=annual&data[]=<each column>&start=1990`, the 21 columns named one by one, in pages of 5,000 records sorted by year and state. The key is read from `EIA_API_KEY` and is redacted from every `source_url`.

Ceiling: 6 requests a run, 3 seconds apart; a 429 or a 5xx is asked once more after 60 seconds. A page an earlier run saved in `warehouse/raw/eia_state_disposition/` is reused unless `--fresh`; `--offline` asks nothing (the run that wrote the present file asked 0 of 6).

## Vintage and revision rule

Years 1990 to 2024: 1,820 records of EIA's (52 areas, 35 years), 37,738 rows. The start year is fixed at 1990 in the code. The table is written by `write_snapshot`: each run replaces the whole table. The connector checks that the records read equal EIA's count, and stops if they do not.

## Shape

Series (`docs/datastandard.md`).

- `entity`: `eia_state_disposition:<state>`, the 50 states, DC and US.
- `variable`: EIA's column with "-" as "_". Unit MWh, except `net_trade_index` (ratio). Any other unit stops the run.
  - Supply, generation: `electric_utilities`, `independent_power_producers`, `combined_heat_and_pwr_elect`, `elect_pwr_sector_gen_subtotal`, `combined_heat_and_pwr_comm`, `combined_heat_and_pwr_indust`, `indust_and_comm_gen_subtotal`, `total_net_generation`.
  - Supply, the rest: `total_international_imports`, `total_supply`.
  - Disposition: `full_service_providers`, `energy_only_providers`, `facility_direct`, `total_elect_indust`, `direct_use`, `total_international_exports`, `estimated_losses`, `net_interstate_trade`, `unaccounted`, `total_disposition`.
  - `net_trade_index`, ratio.
- `ts_utc`: the year's 1 January at 00:00:00Z; `freq` P1Y; `geo` US-<state>, US for the U.S.; `node` the state's name.

Subtotals and totals are EIA's own: `elect_pwr_sector_gen_subtotal`, `indust_and_comm_gen_subtotal`, `total_net_generation`, `total_supply`, `total_elect_indust` and `total_disposition`. A sum leaves them out. A record with no state stops the run, and so does a key given twice.

## License

ERW verdict: public (`docs/licenses.md`). The header's License line: public, a work of the U.S. government; cite "U.S. Energy Information Administration, State Electricity Profiles" (EIA, record 1 of `license_reads.csv`).

## Cross-check

None in the connector. Session 544's report: each state's `total_net_generation` against `eia_state_generation_monthly` summed by year, 1,224 state-years (2001 to 2024): a median ratio of 1.0000, all within 1%. The U.S. in 2024 is 4,308.6 TWh, the total session 524 compared `eia923_plant_fuel_annual` against.

## What it does not hold

- A blank has no row; nothing is filled. Most columns have all 1,820 state-years; `facility_direct` has 1,507, `total_international_exports` 1,736, `total_international_imports` 1,738 and `direct_use` 1,817.
- Generation by fuel: that is in other tables (for example `eia_state_generation_monthly`).
- Months: the connector asks for the annual frequency only.
