# EIA state electricity profiles: each state's meters by technology and sector, a year

Energy Research Warehouse (ERW), method note written in session 674 (chain 043) for a table first written on 21 October 2026.

Tables: `eia_meters_state_annual`

Connector: `warehouse/connectors/eia_meters.py` (session 570).

## Publisher and report

U.S. Energy Information Administration (EIA), State Electricity Profiles, advanced metering (Form EIA-861's advanced metering), read through EIA's API v2, route `electricity/state-electricity-profiles/meters`.

- Page: `https://www.eia.gov/electricity/state/`
- API: `https://api.eia.gov/v2/electricity/state-electricity-profiles/meters/data/?frequency=annual&data[]=meters&start=2013`, in pages of 5,000 records. The key is read from `EIA_API_KEY` and is redacted from every `source_url`.

Ceiling: 8 requests a run (two of session 570's 10 went to its probe), 3 seconds apart; a 429 or a 5xx is asked once more after 60 seconds. A page an earlier run saved in `warehouse/raw/eia_meters/` is reused unless `--fresh`; `--offline` asks nothing (the run that wrote the present file asked 0 of 8).

## Vintage and revision rule

Years 2013 to 2024: 8,580 records of EIA's, 8,578 rows (two records had no value). The start year is fixed at 2013 in the code. The table is written by `write_snapshot`: each run replaces the whole table.

## Shape

Series (`docs/datastandard.md`).

- `entity`: `eia_meters:<state>:<technology slug>:<sector>`.
  - State: the 50 states, DC and US.
  - Technology, EIA's as a slug: `all_meters`, and its kinds `advanced_meter_infrastructure` (AMI), `automatic_meter_reading` (AMR) and `standard_meters`.
  - Sector: RES, COM, IND, TRN, and TOT (all sectors).
- `variable` `meters`, unit count (EIA's "number of meters"; any other unit stops the run).
- `ts_utc`: the year's 1 January at 00:00:00Z; `freq` P1Y; `geo` US-<state>, US for the U.S.; `node` EIA's names of state, technology and sector.

A sum takes one level: the kinds of meter or `all_meters`, and the sectors or TOT. A record with no state, technology or sector stops the run, and so does a key given twice.

## License

ERW verdict: public (`docs/licenses.md`). The header's License line: public, a work of the U.S. government; cite "U.S. Energy Information Administration, State Electricity Profiles" (EIA, record 1 of `license_reads.csv`).

## Cross-check

None in the connector. Session 570's report: AMI, AMR and standard meters sum to all meters every time, and residential meters are a median 1.015 of EIA-861's residential customers (510 state-years).

## What it does not hold

- The kinds of meter after 2019: the table holds AMI, AMR and standard meters for 2013 to 2019 only; from 2020 it holds `all_meters` alone.
- Two of EIA's records with no value (the header's 8,580 records against 8,578 rows); a blank has no row and nothing is filled.
- Meters by utility: the profiles are by state.
