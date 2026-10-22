# EIA state electricity profiles: each state's net-metered capacity and customers by sector, a year

Energy Research Warehouse (ERW), method note written in session 674 (chain 043) for a table first written on 21 October 2026.

Tables: `eia_net_metering_state_annual`

Connector: `warehouse/connectors/eia_net_metering.py` (session 545).

## Publisher and report

U.S. Energy Information Administration (EIA), State Electricity Profiles, net metering, read through EIA's API v2, route `electricity/state-electricity-profiles/net-metering`.

- Page: `https://www.eia.gov/electricity/state/`
- API: `https://api.eia.gov/v2/electricity/state-electricity-profiles/net-metering/data/?frequency=annual&data[]=capacity&data[]=customers&start=2013`, in pages of 5,000 records. The key is read from `EIA_API_KEY` and is redacted from every `source_url`.

Ceiling: 6 requests a run, 3 seconds apart; a 429 or a 5xx is asked once more after 60 seconds. A page an earlier run saved in `warehouse/raw/eia_net_metering/` is reused unless `--fresh`; `--offline` asks nothing (the run that wrote the present file asked 0 of 6).

## Vintage and revision rule

Years 2013 to 2024: 8,580 records of EIA's, 16,226 rows (1,031 series). The start year is fixed at 2013 in the code. The table is written by `write_snapshot`: each run replaces the whole table.

## Shape

Series (`docs/datastandard.md`).

- `entity`: `eia_net_metering:<state>:<technology slug>:<sector>`.
  - State: the 50 states, DC and US.
  - Technology, EIA's as a slug: `all_technologies`, and for 2013 to 2019 also `photovoltaic`, `wind` and `other_technologies`.
  - Sector: RES, COM, IND, TRN, and TOT (all sectors).
- `variable` and `unit`:
  - `capacity`, MW (EIA's megawatts);
  - `customers`, count (EIA's number of customers).
- `ts_utc`: the year's 1 January at 00:00:00Z; `freq` P1Y; `geo` US-<state>, US for the U.S.; `node` EIA's names of state, technology and sector.

A sum over sectors leaves TOT out, and a sum over technologies leaves `all_technologies` out. A unit not in the map stops the run, and so does a record with no state, technology or sector, or a key given twice.

The connector's docstring says "all_technologies" is the technology "in every year EIA gives"; session 545's report and the table itself show EIA giving four technologies a year from 2013 to 2019 and only "All Technologies" from 2020.

## License

ERW verdict: public (`docs/licenses.md`). The header's License line: public, a work of the U.S. government; cite "U.S. Energy Information Administration, State Electricity Profiles" (EIA, record 1 of `license_reads.csv`).

## Cross-check

None in the connector. Session 545's report, internal: the five sectors sum to EIA's all-sector figure in all 624 state-years (within 0.5%), and the states sum to the U.S. every year. No table the ERW holds measures net-metered capacity, so no external check was made; the behind-the-meter owners in the EIA-861 tables report sales, not capacity.

## What it does not hold

- Technologies after 2019: from 2020 the table holds `all_technologies` alone.
- A blank has no row; nothing is filled. So `capacity` (8,118 rows) and `customers` (8,108 rows) do not carry a row for every record.
- Net-metered energy or generation: only capacity and customers are read.
- Utilities one by one: the profiles are by state.
