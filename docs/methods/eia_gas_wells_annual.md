# Producing natural gas and gas condensate wells by state, a year (EIA)

Energy Research Warehouse (ERW), method note written in session 676 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_gas_wells_annual`

The table is built by `warehouse/connectors/eia_gas_wells.py` (session 604). It holds EIA's number of producing gas and gas condensate wells by state, the federal Gulf and the U.S., a year, 1989 to 2020 as EIA publishes it.

## Source

- Publisher: U.S. Energy Information Administration (EIA).
- Report, as the header names it: Natural Gas Annual, number of producing gas wells (API v2, route `natural-gas/prod/wells`), source id `eia:natural-gas/prod/wells`, page `https://www.eia.gov/naturalgas/annual/`.
- Address: `https://api.eia.gov/v2/natural-gas/prod/wells/data/?frequency=annual&data[]=value&facets[process][]=XDG&start=1989`, in pages of 5,000 rows sorted by period and series. The key is read from `EIA_API_KEY` and is redacted in every address the table and the log keep.

## Vintage and revision rule

- The file on the data machine covers the years 1989 to 2020. Its header counts 1,084 records of EIA's and 1,062 rows; it was written by run `20261022T003707Z` (22 October 2026, UTC) from pages an earlier run saved, 0 requests of 9.
- The docstring says EIA publishes this series for 1989 to 2020 only, so a later run is not expected to add years.
- The table is written with `ip.write_snapshot`: each run replaces the whole table with what EIA's API returns, so a figure EIA revises is replaced and a row EIA no longer gives leaves the table. Earlier vintages stay in the raw files (`warehouse/raw/eia_gas_wells/`, not in git).
- A page an earlier run saved in `warehouse/raw` is reused whenever its address is the same, with no age limit, so a later run takes EIA's revisions only with `--fresh`. `--offline` asks nothing and fails on a page not saved.
- `--from YYYY` sets the first year (default 1989). `--out-dir` writes a trial table elsewhere.
- Ceiling: 9 requests a run, 3 seconds apart; an HTTP 5xx or 429 is asked once more after 60 seconds, then the run stops.

## Shape

Series (`docs/datastandard.md` v0), one row per area and year.

- `entity`: `eia_gas_wells:XDG:<area>`, EIA's process (XDG) and area: `S<state>`, `NUS` for the U.S., `R3FM` the federal Gulf.
- `variable`: `gas_wells` (XDG), unit `count`.
- `ts_utc`: the year's 1 January at 00:00:00Z; `freq` `P1Y`.
- `geo`: `US-<state>` for a state, `US` otherwise. `market` is blank. `node`: EIA's series name (for example "U.S. Natural Gas Number of Gas and Gas Condensate Wells (Count)").
- `source`, `source_url` (the page's address with the key redacted), `retrieved_at`, `vintage` (blank).

The file holds 36 entities; a year has between 31 and 36 of them.

## License

- ERW verdict (`docs/licenses.md`, "Every table"): public.
- Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Annual")."

## Cross-check

None in the connector. The run does check its own reading: the rows read must equal the total EIA's API counts, a process or unit not in the map stops it, and a key given twice with two values stops it. A row EIA gives twice with the same value is kept once; the header counts 0 such rows in this file.

## What it does not hold

- A figure EIA withholds has no row; nothing is filled. The header's two counts differ by those figures.
- No year after 2020, and none before 1989.
- No oil wells, no wells drilled or completed, no well-level detail: the count of producing gas and gas condensate wells by area only.
- The U.S. row sits beside the states and the Gulf: a sum over areas must leave it out.
