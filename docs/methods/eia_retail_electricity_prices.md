# The average retail price of electricity by state and sector, a month, from 2001 (EIA, Electric Power Monthly, retail sales)

Energy Research Warehouse (ERW), method note written in session 2180 (chain 097) for a table first written on 26 September 2026 (session 8).

Tables: `eia_retail_electricity_prices`

## Publisher and address

U.S. Energy Information Administration (EIA), the average retail price of electricity by state and sector from the Electric Power Monthly (the header names `https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a`, which is not asked), read through EIA's open data API v2, route `electricity/retail-sales`, data column `price`, no facet, the whole history the API offers (no `start`):

`https://api.eia.gov/v2/electricity/retail-sales/data/?frequency=monthly&data[0]=price&sort[0][column]=period&sort[1][column]=stateid&sort[2][column]=sectorid` (each ascending; 5,000 rows a page, 0.5 seconds between pages)

The key (`EIA_API_KEY`) is sent in the address; `source_url` keeps the address with the key written as `api_key=REDACTED` (`ip.redact`). The connector sends no User-Agent of its own (the requests library's default). api.eia.gov has no robots file: it answers `/robots.txt` with HTTP 403 for want of a key (reads 151, 160 and 262 of `warehouse/metadata/license_reads.csv`).

Source id `eia:electricity/retail-sales`, shared with `eia_retail_sales_monthly`. Connector: `warehouse/connectors/eia_series.py` (session 7; this table added in session 8), which writes twelve other EIA tables in the same run. `site/lib/pages.ts` names the table as a source of the EV game's file (`site/data/ev_prices.json`); `docs/methods/cost_of_power.md`, `datacenter_cost.md`, `datacenter_pays_algorithm.md`, `ev_game.md`, `price_board.md` and `eia_retail_sales_monthly.md` mention it.

Schedule: `warehouse/run_daily.sh` runs the connector every day (step `eia_series`, under a pull budget of 15 minutes, `warehouse/pull_budget.py`), and `.github/workflows/daily-prices.yml` runs `run_daily.sh` on GitHub's runner. (`warehouse/refresh_board_v4.sh` also names the connector; it is retired, session 271, and not scheduled.) `warehouse/metadata/run_status.csv` holds 27 runs for the table: the first `20260926T001438Z` (local), the last `20261023T143750Z` (GitHub); 25 ok and two gaps, `20261020T003609Z` and `20261021T143630Z`, each "publisher did not answer within the budget (15 minutes of wall clock)" at the page of offset 5000.

## Vintage and revision

Months January 2001 to August 2026 (`ts_utc` 2001-01-01 to 2026-08-01), 308 months, in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github`, with the header of the connector's run `20261023T143750Z`. The rebuild keeps a row's `retrieved_at` from the run that first archived its value: 110,661 rows carry 29 September 2026 (months to July 2026), 2,939 rows 22 October 2026 (all months of 2025: values the archive took as new or changed that day), and 974 rows 23 October 2026 (months of 2026). `vintage` is empty. `coverage.csv` gives the same 114,574 rows, 372 nodes, the same first and last `ts_utc`, and last run 2026-10-23T14:37:50Z.

The first date is from `run_status.csv` (its first row for the table, run `20260926T001438Z`, local, ok), from session 8's report (114,202 rows, 2001-01 to 2026-07; the session ran from 25 to 26 September 2026 UTC), from the commit of session 8's Task 5 (`25da1ac6`, 26 September 2026, 01:06 UTC) and from `sources.csv`, which first saw the source on 2026-09-26.

Every run asks for the whole history and merges it into the held file on (entity, variable, ts_utc) (`ip.write_csv`): a value EIA revises replaces the one held, and a row EIA stops giving is kept from an earlier run (the header's "Window" line says so).

## Shape and variables

Series, 114,574 rows, 372 entities (62 locations by six sectors), one variable. `entity` `eia:retail_price:<stateid>:<sectorid>`, EIA's location and sector codes; `variable` `retail_price`; `value` EIA's price in cents per kilowatt-hour times 10, rounded to six decimals; `unit` USD/MWh (1 cent/kWh is 10 USD/MWh, exact; the header's conversion line says so); `freq` P1M; `ts_utc` the first day of the month at 00:00:00Z; `market` empty; `node` empty (the header's "Series" line names each entity, as "Alaska, residential"); `source_url` the page of the API's answer (23 pages); `vintage` empty. There are no `x_` columns.

- Locations: the 50 states and DC (`geo` US-<state>), the nation (`US`, `geo` US), and ten census divisions with `geo` empty (ENC East North Central, ESC East South Central, MAT Middle Atlantic, MTN Mountain, NEW New England, PACC Pacific Contiguous, PACN Pacific Noncontiguous, SAT South Atlantic, WNC West North Central, WSC West South Central).
- Sectors: RES residential, COM commercial, IND industrial, TRA transportation, OTH other, ALL all sectors.

Every entity holds all 308 months except `eia:retail_price:AK:RES`, 306: it has no row for August and September 2016, the two dates the header counts as listed without a value. No (entity, variable, ts_utc) is given twice.

The U.S. all-sector price was 67.5 USD/MWh in January 2001 and 148.7 in August 2026; in August 2026 the U.S. residential price was 181.6, commercial 144.7, industrial 96.4 and transportation 148.6. That month's residential prices run from 127.2 (Nevada) to 471.8 (Hawaii). The highest value in the table is Michigan's transportation price of June 2005, 1,166.7; the lowest above 0, DC's industrial price of December 2004, 9.6.

26,055 rows are exactly 0: the other sector (OTH) in every location and every month from January 2003 (17,608 rows, 62 locations by 284 months; it has a price only in 2001 and 2002), and the transportation sector (TRA) in 8,447 rows (every location in every month of 2001 and 2002, and states and months later). In `eia_retail_sales_monthly`, 26,037 of these 26,055 rows have sales of 0 in the same location, sector and month; 18 have sales above 0, all transportation (North Carolina, January to September 2005; Rhode Island, January to April 2012; DC, August 2014, January and February 2022; Ohio, November and December 2022).

The counts in this note were computed in session 2180 with pandas from the rows of `warehouse/output/eia_retail_electricity_prices.csv`, read past its 13 header lines, and of `eia_retail_sales_monthly.csv` for the sales.

## Checks the connector makes

- No pause check: `eia_series.py` does not call `iso_prices.paused()` or `paused_host()` before its requests. EIA is not in `warehouse/metadata/paused_sources.csv`.
- The route is read page by page until the rows read reach the `total` the API reports; a different count stops the table, and so does an answer with no row.
- Every unit in the answer must be one of the eleven the connector maps for its tables (`UNITS`); another stops the table. The price's "cents per kilowatt-hour" is multiplied by 10 (`SCALE`).
- A (series, period) given twice stops the table.
- A value that is empty, "none" or "not available" is omitted, logged and counted in the header ("Dates EIA lists without a value, omitted: 2"). Any other value that is not a number stops the table. A value of 0 is written. Nothing is filled.
- The newest month must be at most 150 days old on the day of the run, or the table is not written.
- No ceiling: the connector counts neither requests nor rows. The pull budget of `run_daily.sh` (15 minutes of wall clock) is the only limit, and it stopped the runs of 20 and 21 October.
- Each page is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`), with no retry once the pull budget has passed. Any answer but HTTP 200 is an error and is retried.
- A table that fails does not stop the others; each table's result is written to `run_status.csv`. `--out-dir` writes a trial elsewhere; `--table` runs one table.

## License

The header: "License: public domain (EIA)." `license_verdicts.csv` gives EIA "may be public" (read 1; the same if the ERW sells anything), asking for the acknowledgment "Source: U.S. Energy Information Administration". `license_tables.csv` names EIA as the table's one publisher (from the source registry), and `docs/licenses.md` gives the ERW verdict public. `coverage.csv`: public.

## Found while writing this note

- `CLAUDE.md` says every connector that reaches a publisher's servers asks `iso_prices.paused()` first. This one does not.
- 26,055 rows are a price of 0 USD/MWh (OTH from 2003, TRA in 2001 and 2002 and elsewhere), and 26,037 of them sit beside sales of 0. The connector writes them as prices. `eia_board.py` drops a cost of exactly 0 from Form EIA-923 for the same reason ("not a price"); this connector does not, and its docstring does not say so. A mean across states or sectors reads them as prices of 0.
- The docstring says "A series whose unit is not the expected one fails the table". The code checks only that each unit is one of the eleven it maps for any of its tables, so a price answered in another known unit (thousand megawatthours, say) would be written as `retail_price` with that unit.
- The source registry row `eia:electricity/retail-sales` in `warehouse/metadata/sources.csv` names the report "Electric Power Monthly: retail sales of electricity and number of customers by state and sector (Form EIA-861M)" and the page `https://www.eia.gov/electricity/data/eia861m/`: those of `eia_retail_sales_monthly`. The two tables share the source id, and the connector runs its tables in sorted order, so the sales table's entry is written last. This table's header names another report and page.

## What it does not hold

- Sales and customers (`eia_retail_sales_monthly`), prices by utility, or any price within a month.
- Months before January 2001: the connector asks for the whole history, and January 2001 is the first month the answer gives.
- A name for each entity in the rows: `node` is empty, and the names are in the header only.
