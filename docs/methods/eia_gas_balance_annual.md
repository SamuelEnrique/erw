# Natural gas supply and disposition by state, a year (EIA)

Energy Research Warehouse (ERW), method note written in session 676 (chain 043) for a table first written on 21 or 22 October 2026.

Tables: `eia_gas_balance_annual`

The table is built by `warehouse/connectors/eia_gas_balance.py` (session 557). It holds the state balance of EIA's Natural Gas Annual: what a state consumes and produces, what it receives from and delivers to other states, what it puts into and takes out of storage, and EIA's balancing item.

## Source

- Publisher: U.S. Energy Information Administration (EIA).
- Report, as the header names it: Natural Gas Annual, supply and disposition (API v2, route `natural-gas/sum/snd`), source id `eia:natural-gas/sum/snd`, page `https://www.eia.gov/naturalgas/annual/`.
- Address: `https://api.eia.gov/v2/natural-gas/sum/snd/data/?frequency=annual&data[]=value&facets[process][]=<each of ten>&start=1997`, in pages of 5,000 rows sorted by period and series. The key is read from `EIA_API_KEY` and is redacted in every address the table and the log keep.
- The docstring says why the annual route: the monthly form holds only the U.S. balance and the states' storage, which `eia_gas_storage_state_monthly` already holds.

## Vintage and revision rule

- The file on the data machine covers the years 1997 to 2025. Its header counts 11,310 records of EIA's and 11,274 rows; it was written by run `20261021T232138Z` (21 October 2026, UTC) from pages an earlier run saved, 0 requests of 16.
- Not every variable reaches 2025: total consumption, dry production, supplemental fuels and storage injections and withdrawals do; the interstate receipts and deliveries, the in-transit imports and exports and the balancing item end in 2024.
- The table is written with `ip.write_snapshot`: each run replaces the whole table with what EIA's API returns, so a figure EIA revises is replaced and a row EIA no longer gives leaves the table. Earlier vintages stay in the raw files (`warehouse/raw/eia_gas_balance/`, not in git).
- A page an earlier run saved in `warehouse/raw` is reused whenever its address is the same, with no age limit, so a later run takes EIA's revisions and new years only with `--fresh`. `--offline` asks nothing and fails on a page not saved.
- `--from YYYY` sets the first year (default 1997). `--out-dir` writes a trial table elsewhere.
- Ceiling: 16 requests a run, 3 seconds apart; an HTTP 5xx or 429 is asked once more after 60 seconds, then the run stops.

## Shape

Series (`docs/datastandard.md` v0), one row per area, process and year.

- `entity`: `eia_gas_balance:<process>:<area>`, EIA's process code and area. Areas are `S<state>` (for example `SAL`), `NUS` for the U.S. and `R3FM` the federal Gulf of America; EIA's `-Z00` and `-Z0S` forms of an area (for example `SAL-Z00`, `NUS-Z0S`) are kept as EIA gives them.
- `variable` and EIA's process code, every one in `MMcf` (million cubic feet in the year):
  - `total_consumption` (VC0)
  - `dry_production` (FPD)
  - `supplemental_fuels` (OVI)
  - `imports_intransit` (IMI) and `exports_intransit` (EEI)
  - `interstate_receipts` (MIR) and `interstate_deliveries` (MID)
  - `storage_injections` (SAI) and `storage_withdrawals` (SAW)
  - `balancing_item` (VG4)
- `ts_utc`: the year's 1 January at 00:00:00Z; `freq` `P1Y`.
- `geo`: `US-<state>` for a state area, `US` otherwise. `market` is blank. `node`: EIA's series name (for example "Alabama Natural Gas Injections into Underground Storage (MMcf)").
- `source`, `source_url` (the page's address with the key redacted), `retrieved_at`, `vintage` (blank).

## License

- ERW verdict (`docs/licenses.md`, "Every table"): public.
- Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Annual")."

## Cross-check

None in the connector. The run does check its own reading: the rows read must equal the total EIA's API counts, a process or unit not in the map stops it, and a key given twice with two values stops it. A row EIA gives twice with the same value is kept once; the header counts 0 such rows in this file.

## What it does not hold

- A figure EIA withholds has no row; nothing is filled.
- Only the ten processes above are asked for; other lines of EIA's supply and disposition table are not taken.
- No monthly balance: this is the annual route only.
- The U.S. row, the federal Gulf and the `-Z00` and `-Z0S` forms of an area sit beside the states; a sum over areas must take one level.
