# Retail prices of regular gasoline and No. 2 diesel by region, state and city, a week, from 2019 (EIA, Gasoline and Diesel Fuel Update)

Energy Research Warehouse (ERW), method note written in session 2180 (chain 097) for a table first written on 6 October 2026 (session 132).

Tables: `eia_regional_retail_fuel_prices`

## Publisher and address

U.S. Energy Information Administration (EIA), the Gasoline and Diesel Fuel Update, its weekly survey of retail prices (`https://www.eia.gov/petroleum/gasdiesel/`, named in the header and not asked), read through EIA's open data API v2, route `petroleum/pri/gnd`, products EPMR (regular gasoline, all formulations) and EPD2D (No. 2 diesel), every area EIA lists:

`https://api.eia.gov/v2/petroleum/pri/gnd/data/?frequency=weekly&data[0]=value&facets[product][]=EPMR&facets[product][]=EPD2D&start=2019-01-01` (sorted by period and series, 5,000 rows a page, 0.4 seconds between pages)

The key (`EIA_API_KEY`) is sent apart from the address the rows cite, so `source_url` holds no key. The connector sends no User-Agent of its own (the requests library's default). api.eia.gov has no robots file: it answers `/robots.txt` with HTTP 403 for want of a key (reads 151, 160 and 262 of `warehouse/metadata/license_reads.csv`).

Source id `eia:petroleum/pri/gnd:regional`: the suffix keeps the registry row of `eia_retail_fuel_prices` (`warehouse/connectors/eia_series.py`, the U.S. series of the same route) as it is. Connector: `warehouse/connectors/eia_board.py` (session 132), which writes `eia_crude_stream_prices` and `eia_power_plant_fuel_costs` in the same run. The table was built for the price board (`/board`, in review); `site/lib/pages.ts` names it, with `eia_retail_electricity_prices`, as a source of the EV game's file (`site/data/ev_prices.json`). `warehouse/supabase/live_set.yaml` holds it out of the live catalogue (`catalogue_hold`, session 132: "nothing reads them from Supabase").

Schedule: `warehouse/refresh_board.sh` runs the connector (step `eia_board`, under `warehouse/health.py run` and a pull budget of 15 minutes, `warehouse/pull_budget.py`). `warehouse/run_daily.sh` calls that script every day (step `board`), and `.github/workflows/daily-prices.yml` runs `run_daily.sh` on GitHub's runner. `warehouse/metadata/run_status.csv` holds 13 runs for the table, all on GitHub and all ok: the first `20261007T144447Z`, the last `20261023T150534Z`.

## Vintage and revision

Survey Mondays 7 January 2019 to 19 October 2026 (`ts_utc`), 407 weeks, in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261022T152428Z-github`, with the header of the connector's run `20261022T150605Z`. The rebuild keeps a row's `retrieved_at` from the run that first archived its value: 16,159 rows carry 6 October 2026 (weeks to 28 September 2026), and 40 rows each 7, 14 and 22 October (the weeks of 5, 12 and 19 October). `vintage` is empty. `coverage.csv` gives the same 16,279 rows and the same first and last `ts_utc`; its last run, 2026-10-23T15:05:34Z, is one day newer than the copy on the data machine.

The first date is from the rows (the earliest `retrieved_at` is 2026-10-06T08:18:26Z), from the commit that added the connector (`be12706e`, 6 October 2026, 08:21 UTC), from session 132's report (16,159 rows, 40 series) and from `sources.csv`, which first saw the source on 2026-10-06.

Every run asks for the whole history from 2019 and writes the table anew: `build()` deletes the held file (`os.remove`) before `ip.write_csv`, so a revision EIA makes is taken at the next run and a week EIA stops giving leaves the table.

## Shape and variables

Series, 16,279 rows, 40 entities, one variable. `entity` `eia:<EIA series id>`; `variable` `retail_price`; `unit` USD/gal (EIA's $/GAL, value unchanged); `freq` P1W; `ts_utc` EIA's date at 00:00:00Z (every row is a Monday); `geo` US for the nation, US-<state> for a state, empty for a PADD, a sub-PADD, PADD 5 except California and a city; `market` empty; `node` EIA's area name (29 names, gasoline and diesel sharing them); `source_url` the page of the API's answer (four pages); `vintage` empty. There are no `x_` columns.

- Regular gasoline (`eia:EMM_EPMR_PTE_<area>_DPG`), 29 areas: the U.S.; PADDs 1, 1A, 1B, 1C, 2, 3, 4 and 5, and PADD 5 except California; nine states (California, Colorado, Florida, Massachusetts, Minnesota, New York, Ohio, Texas, Washington); ten cities (Boston, Chicago, Cleveland, Denver, Houston, Los Angeles, Miami, New York City, San Francisco, Seattle).
- No. 2 diesel (`eia:EMD_EPD2D_PTE_<area>_DPG`), 11 areas: the U.S., the same nine PADD rows and California.

Every series holds all 407 weeks except Houston's gasoline, 406: it has no row for 8 July 2024, the one date the header counts as listed with no value. No (entity, variable, ts_utc) is given twice. The U.S. gasoline price runs from 1.773 USD/gal (27 April 2020) to 5.006 (13 June 2022), and was 4.284 on 19 October 2026; U.S. diesel from 2.372 (2 November 2020) to 6.529 (21 September 2026), and 6.276 on 19 October 2026. The lowest value in the table is Ohio's gasoline, 1.397 (27 April 2020); the highest California's diesel, 8.246 (21 September 2026).

The two U.S. series also stand, under the same `entity`, in `eia_retail_fuel_prices`: of their 814 shared (entity, variable, ts_utc), none differs in value.

The counts in this note were computed in session 2180 with pandas from the rows of `warehouse/output/eia_regional_retail_fuel_prices.csv`, read past its 12 header lines.

## Checks the connector makes

- No pause check: `eia_board.py` does not call `iso_prices.paused()` or `paused_host()` before its requests. EIA is not in `warehouse/metadata/paused_sources.csv`.
- The route is read page by page until the rows read reach the `total` the API reports; a different count stops the table.
- Each row's unit must be $/GAL, or the table stops.
- A date EIA lists with no value (empty, W, NA, --, null or None) is not written and is counted in the header ("not written: 1" in the run of 22 October). Any other value that is not a number stops the table. Nothing is filled.
- An (entity, variable, ts_utc) given twice stops the table.
- The newest week must be at most 21 days old on the day of the run, or the table is not written.
- Ceiling: a counter starts at 1,300 (`EXPLORED`, session 132's probes) and adds the rows the API returns to this run, across the connector's three tables; past 1,500,000 the run stops. The run of 22 October returned 16,280 rows for this table.
- Each page is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`), with no retry once the pull budget has passed. Any answer but HTTP 200 is an error and is retried.
- A table that fails does not stop the others; each table's result is written to `run_status.csv`. `--out-dir` writes a trial elsewhere; `--table` runs one table.

## License

The header: "License: public. U.S. government publications are in the public domain (EIA, Copyrights and Reuse); these are EIA's own surveys. Credit: U.S. Energy Information Administration." `license_verdicts.csv` gives EIA "may be public" (read 1; the same if the ERW sells anything), asking for the acknowledgment "Source: U.S. Energy Information Administration". `license_tables.csv` names EIA as the table's one publisher (from the source registry), and `docs/licenses.md` gives the ERW verdict public. `coverage.csv`: public.

## Found while writing this note

- `CLAUDE.md` says every connector that reaches a publisher's servers asks `iso_prices.paused()` first. This one does not.
- `build()` deletes `warehouse/output/eia_regional_retail_fuel_prices.csv` before calling `ip.write_csv`, and the data lock is checked inside `ip.write_csv`. A run without the lock therefore removes the held table and then stops (`lock.require` raises `SystemExit`, which `main()`'s `except Exception` does not catch, so no status row is written either). Any other failure of the write after the deletion also leaves no table.
- The docstring sets the ceiling at "1,500,000 rows for session 132's pulls in all". The code counts one run: the counter starts again at 1,300 on every run, and the run is daily.
- The header's shape line speaks of "a monthly value's the first day of the month" and of "stream" names, written for the connector's monthly tables; this table is weekly and has areas only.

## What it does not hold

- Midgrade and premium gasoline, gasoline by formulation (conventional, reformulated), and diesel for the cities and for any state but California.
- Weeks before 2019: the connector starts there (`START`). The two U.S. series are in `eia_retail_fuel_prices` from 20 August 1990 (gasoline) and 21 March 1994 (diesel).
- Taxes or any part of the price: the price as EIA's survey gives it.
