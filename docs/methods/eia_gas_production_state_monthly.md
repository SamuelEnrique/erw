# Natural gas production by state: withdrawals, marketed and dry production, venting and flaring, shale gas, a month (EIA)

Energy Research Warehouse (ERW), method note written in session 676 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_gas_production_state_monthly`

The table is built by `warehouse/connectors/eia_gas_production_state.py` (session 528). It holds EIA's monthly natural gas production by state and offshore area: gross withdrawals, marketed production, dry production, gas vented and flared, and shale gas withdrawals.

## Source

- Publisher: U.S. Energy Information Administration (EIA).
- Report, as the header names it: Natural Gas Monthly, production by state (API v2, route `natural-gas/prod/sum`), source id `eia:natural-gas/prod/sum`, page `https://www.eia.gov/naturalgas/monthly/`.
- Address: `https://api.eia.gov/v2/natural-gas/prod/sum/data/?frequency=monthly&data[]=value&facets[process][]=FGW&facets[process][]=VGM&facets[process][]=FPD&facets[process][]=VGV&facets[process][]=FGS&start=2001-01`, in pages of 5,000 rows sorted by period and series. The key is read from `EIA_API_KEY` and is redacted in every address the table and the log keep.

## Vintage and revision rule

- The file on the data machine covers January 2001 to July 2026. Its header counts 59,195 records of EIA's and 47,805 rows taken; it was written by run `20261021T211419Z` (21 October 2026, UTC) from pages an earlier run saved, 0 requests of 30.
- The series end at different months in this file: gross withdrawals and marketed production run to July 2026 for 19 of their 37 entities and to December 2024 for the other 18; dry production runs to July 2026 for the U.S. only, to December 2024 for 35 entities and to December 2015 for `R98`; `vented_flared` and `shale_withdrawals` end in December 2024 everywhere. Most states' dry production begins in January 2006, and most `shale_withdrawals` series in January 2007.
- The table is written with `ip.write_snapshot`: each run replaces the whole table with what EIA's API returns, so a month EIA revises is replaced and a row EIA no longer gives leaves the table. Earlier vintages stay in the raw files (`warehouse/raw/eia_gas_production_state/`, not in git).
- A page an earlier run saved in `warehouse/raw` is reused whenever its address is the same, with no age limit, so a later run takes EIA's revisions and new months only with `--fresh`. `--offline` asks nothing and fails on a page not saved.
- `--from YYYY-MM` sets the first month (default 2001-01). `--out-dir` writes a trial table elsewhere.
- Ceiling: 30 requests a run, 3 seconds apart; an HTTP 5xx or 429 is asked once more after 60 seconds, then the run stops.

## Shape

Series (`docs/datastandard.md` v0), one row per series and month.

- `entity`: `eia_gas_production:<area>:<series stem>`, EIA's area code and its series code less its last character (for example `eia_gas_production:SAK:N9010AK`). Areas: `S<state>`, `NUS` for the U.S., `R3FM` the federal Gulf of America, and `R98`, EIA's "Other States", a sum of small states also given one by one. Any other area stops the run.
- `variable` and EIA's process code, every one in `MMcf` (EIA's million cubic feet in the month):
  - `gross_withdrawals` (FGW)
  - `marketed_production` (VGM)
  - `dry_production` (FPD)
  - `vented_flared` (VGV)
  - `shale_withdrawals` (FGS), which is within gross withdrawals
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`.
- `geo`: `US-<state>`, or `US` for the U.S., the offshore and `R98` (session 528: the states and the Gulf of America sum to the U.S.). `market` is blank. `node`: EIA's series name (for example "Alaska Natural Gas Gross Withdrawals (MMcf)").
- `source`, `source_url` (the page's address with the key redacted), `retrieved_at`, `vintage` (blank).

The connector's docstring and header call `dry_production` "the U.S. only"; the file as written holds it for 37 entities, the U.S. (`N9070US`) and the states, the Gulf and `R98` under EIA's `NA1160_` series. The file holds 184 entities in all.

## License

- ERW verdict (`docs/licenses.md`, "Every table"): public.
- Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Monthly")."

## Cross-check

None in the connector. The run does check its own reading: the rows read must equal the total EIA's API counts, a process, unit or area not in the map stops it, and an (entity, variable, ts_utc) given twice stops it.

## What it does not hold

- A figure EIA withholds has no row; nothing is filled.
- EIA's per-day series (MMcf/d) are not taken: the vocabulary has no MMcf/d, and they are the month's volume over its days. Those and the withheld figures are the difference between the header's two counts.
- EIA's other withdrawals (from gas, oil and coalbed wells), repressuring, nonhydrocarbons removed and extraction loss are not taken.
- `R98` repeats states given one by one, and the U.S. repeats the states and the Gulf: a sum must leave them out.
