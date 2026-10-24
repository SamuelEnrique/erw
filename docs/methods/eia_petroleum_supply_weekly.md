# The United States' petroleum stocks, crude production, refinery runs and trade, a week, from 2010 (EIA, Weekly Petroleum Status Report)

Energy Research Warehouse (ERW), method note written in session 2180 (chain 097) for a table first written on 6 October 2026 (session 134).

Tables: `eia_petroleum_supply_weekly`

## Publisher and address

U.S. Energy Information Administration (EIA), the Weekly Petroleum Status Report (`https://www.eia.gov/petroleum/supply/weekly/`, named in the header and not asked), read through EIA's open data API v2, three routes, weekly, from 1 January 2010, each asked for the series the connector names:

- `https://api.eia.gov/v2/petroleum/stoc/wstk/data/`: stocks, source id `eia:petroleum/stoc/wstk:supply`
- `https://api.eia.gov/v2/petroleum/sum/sndw/data/`: supply and disposition, source id `eia:petroleum/sum/sndw`
- `https://api.eia.gov/v2/petroleum/move/wkly/data/`: imports and exports, source id `eia:petroleum/move/wkly:supply`

Each request asks `frequency=weekly`, `data[0]=value`, one `facets[series][]` for each series, `start=2010-01-01`, sorted by period and then series, 5,000 rows a page, 0.4 seconds between pages. The key (`EIA_API_KEY`) is sent apart from the address the rows cite, so `source_url` holds no key. The connector sends no User-Agent of its own (the requests library's default). api.eia.gov has no robots file: it answers `/robots.txt` with HTTP 403 for want of a key (reads 151, 160 and 262 of `warehouse/metadata/license_reads.csv`).

Connector: `warehouse/connectors/eia_supply.py` (session 134), which writes three other tables in the same run (`eia_gas_storage_weekly`, `eia_gas_trade_monthly`, `eia_basin_production_monthly`). `warehouse/connectors/eia_refinery_weekly.py` (session 543) does not write this table; it names it only to say that its own weeks are dated the same way. The table was built for Supply and trade (`/supply`, in review), whose method is `docs/methods/supply_and_trade.md`. `warehouse/supabase/live_set.yaml` holds it out of the live catalogue (`catalogue_hold`, session 134: "nothing reads them from Supabase").

Schedule: `warehouse/refresh_supply.sh` runs the connector (step `eia_supply`, under `warehouse/health.py run` and a pull budget of 15 minutes, `warehouse/pull_budget.py`). `warehouse/run_daily.sh` calls that script on Saturdays (UTC) only, or on any day with `SUPPLY=1`, and `.github/workflows/daily-prices.yml` runs `run_daily.sh` on GitHub's runner. `warehouse/metadata/run_status.csv` holds one run for the table: `20261010T145819Z` on GitHub, ok.

## Vintage and revision

Weeks ending 1 January 2010 to 2 October 2026 (`ts_utc`), 875 weeks, in the file on the data machine (`warehouse/output/` of the main checkout), restored from the Redivis draft by `scripts/sync.py` (its last header line) with the header of run `20261010T145819Z`. Every row's `retrieved_at` falls between 2026-10-10T14:58:24Z and 14:58:32Z; `vintage` is empty. `coverage.csv` gives the same 26,118 rows, 30 nodes, the same first and last `ts_utc`, and last run 2026-10-10T14:58:19Z.

The first date is from the commit that added the connector (`f7af5dc2`, 6 October 2026, 10:46 UTC), from session 134's report (26,088 rows, "two runs") and from `sources.csv`, which first saw the three sources on 2026-10-06.

Every run asks for the whole history from 2010 and writes the table anew: `build()` deletes the held file (`os.remove`) before `ip.write_csv`, so the merge finds nothing to merge with. A revision EIA makes is taken at the next run, and a week EIA stops giving leaves the table. The header's last connector line says so for this run: "26118 new, 0 replacing earlier rows ... 0 rows are kept from earlier runs".

A week's value sits at 00:00:00Z of EIA's date, the Friday the report week ends (every row is a Friday).

## Shape and variables

Series, 26,118 rows, 30 entities, five variables. `entity` `eia:<EIA series id>`; `node` EIA's description of the series with its unit in brackets removed; `freq` P1W; `geo` US; `market` empty; `unit` per row (kbbl, kbbl/d or pct, from EIA's MBBL, MBBL/D and %; values unchanged); `source` the route's source id; `source_url` the page of the API's answer (six pages); `vintage` empty. There are no `x_` columns.

| `variable` | `unit` | Series (`entity` without `eia:`) | Rows |
|---|---|---|---|
| `stocks` | kbbl | WCESTUS1 (crude excluding the SPR), W_EPC0_SAX_YCUOK_MBBL (Cushing, crude excluding the SPR), WCSSTUS1 (crude in the SPR), WGTSTUS1 (total gasoline), WDISTUS1 (distillate fuel oil) | 4,375 |
| `production` | kbbl/d | WCRFPUS2 (U.S. field production of crude), W_EPC0_FPF_R48_MBBLD (Lower 48), W_EPC0_FPF_SAK_MBBLD (Alaska) | 2,625 |
| `utilization` | pct | WPULEUS3 (U.S. percent utilization of refinery operable capacity), W_NA_YUP_R10_PER to W_NA_YUP_R50_PER (PADDs 1 to 5) | 5,140 |
| `crude_input` | kbbl/d | WCRRIUS2 (U.S. refiner net input of crude), WCRRIP12 to WCRRIP52 (PADDs 1 to 5) | 5,250 |
| `flow` | kbbl/d | WCRIMUS2, WCREXUS2, WCRNTUS2 (crude imports, exports, net imports); WRPIMUS2, WRPEXUS2, WRPNTUS2 (total products); WTTNTUS2 (crude and products, net imports); WDIIMUS2 (distillate imports); WDIEXUS2 (total distillate exports); W_EPM0F_IM0_NUS-Z00_MBBLD (finished motor gasoline imports) | 8,728 |

Each series holds every week from 1 January 2010 to 2 October 2026 (875), except the five PADD utilization series and WDIEXUS2, which begin on 4 June 2010 (853 weeks each). No week is missing inside any series' span, and no (entity, variable, ts_utc) is given twice.

Some ranges, in the units above: crude stocks excluding the SPR 301,123 to 540,722 kbbl; the SPR 282,983 to 726,617 kbbl; Cushing 17,899 to 69,420 kbbl; U.S. field production 5,083 to 13,979 kbbl/d; U.S. refinery utilization 56.0 to 98.1 percent. Negative values are net exports, not errors: WRPNTUS2 is below 0 in 801 weeks, WTTNTUS2 in 292 and WCRNTUS2 in 1 (its lowest, -688 kbbl/d). PADD utilization passes 100 percent in 49 weeks (PADD 1 in 7, PADD 2 in 21, PADD 4 in 21; the highest 112.5, PADD 4); the values are EIA's.

The four stock series and five crude and product trade series also stand, under the same `entity`, in `eia_petroleum_stocks_weekly` and `eia_petroleum_trade_weekly` (`warehouse/connectors/eia_series.py`): of 3,500 and 4,375 shared (entity, variable, ts_utc), none differs in value. The five PADD utilization series also stand in `eia_refinery_weekly`, as `eia_refinery:<series>` and as a ratio (EIA's percent divided by 100).

The counts in this note were computed in session 2180 with pandas from the rows of `warehouse/output/eia_petroleum_supply_weekly.csv`, read past its 16 header lines.

## Checks the connector makes

- No pause check: `eia_supply.py` does not call `iso_prices.paused()` or `paused_host()` before its requests. EIA is not in `warehouse/metadata/paused_sources.csv`.
- Each route is read page by page until the rows read reach the `total` the API reports; a different count stops the table.
- Each row's unit must be one the connector maps (BCF, MBBL, MBBL/D, %, MMCF, and the Outlook's two); another stops the table.
- A date EIA lists with no value (empty, W, NA, --, null or None) is not written and is counted in the header ("Dates EIA lists with no value, not written: 0"). Any other value that is not a number stops the table. Nothing is filled.
- An (entity, variable, ts_utc) given twice stops the table.
- The newest week must be at most 21 days old on the day of the run, or the table is not written.
- Ceiling: a counter starts at 6,000 (`EXPLORED`, session 134's probes) and adds the rows the API returns to this run, across the four tables; past 1,200,000 the run stops. This run returned 26,118 rows for this table.
- Each page is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`), with no retry once the pull budget has passed. Any answer but HTTP 200 is an error and is retried.
- A table that fails does not stop the others; each table's result is written to `run_status.csv`. `--out-dir` writes a trial elsewhere; `--table` runs one table.

## License

The header: "License: public. U.S. government publications are in the public domain (EIA, Copyrights and Reuse). Credit: U.S. Energy Information Administration." `license_verdicts.csv` gives EIA "may be public" (read 1; the same if the ERW sells anything), asking for the acknowledgment "Source: U.S. Energy Information Administration". `license_tables.csv` names EIA as the table's one publisher (from the source registry), and `docs/licenses.md` gives the ERW verdict public. `coverage.csv`: public.

## Found while writing this note

- `CLAUDE.md` says every connector that reaches a publisher's servers asks `iso_prices.paused()` first. This one does not.
- `build()` deletes `warehouse/output/eia_petroleum_supply_weekly.csv` before calling `ip.write_csv`, and the data lock is checked inside `ip.write_csv`. A run without the lock therefore removes the held table and then stops (`lock.require` raises `SystemExit`, which `main()`'s `except Exception` does not catch, so no status row is written either). Any other failure of the write after the deletion also leaves no table.
- The docstring sets the ceiling at "1,200,000 rows for session 134's pulls in all". The code counts one run: the counter starts again at 6,000 on every run, so the weekly schedule is not held to a total.
- The docstring says the table holds "distillate and gasoline trade". It holds distillate imports and exports, and gasoline imports only (finished motor gasoline); no gasoline export series is asked for.
- The header carries two lines written for the connector's other tables: "a monthly value's the first day of the month", and "the Outlook's crude is written in thousand barrels a day". This table has neither.
- The refresh is weekly, on Saturdays, but `run_status.csv` holds only the run of Saturday 10 October 2026 for this table, and no row of any connector dated 15, 16 or 17 October. The copy on the data machine ends with the week of 2 October 2026.

## What it does not hold

- Product supplied (EIA's weekly measure of demand), other product stocks (jet fuel, propane, residual fuel; some are in `eia_petroleum_stocks_weekly`), stocks by PADD, and gasoline exports.
- Refinery inputs other than crude, and operable capacity (`eia_refinery_weekly`).
- Weeks before 2010: the connector starts there (`start`).
