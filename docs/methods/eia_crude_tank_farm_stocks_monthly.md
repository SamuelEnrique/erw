# Crude oil stocks at tank farms and pipelines, a month from 1981: the U.S. and the five PADDs, and Cushing, Oklahoma's ending stocks from 2004 (EIA, Petroleum Supply Monthly)

Energy Research Warehouse (ERW), method note written in session 2289 (chain 104) for a table first written on 24 October 2026 (session 2286 of chain 104, its report `archive/sessions/SESSION_2286_REPORT.md`).

Tables: `eia_crude_tank_farm_stocks_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, crude oil stocks at tank farms and pipelines, through EIA's API v2, route `petroleum/stoc/cu` (the route's metadata, `runs/c104/s2286/meta.json`, names its parent "EIA petroleum gas survey data" and gives monthly and annual frequencies, 1981-01 to 2026-07). The header's page is the route itself, `https://api.eia.gov/v2/petroleum/stoc/cu/`; the request asks `data/?frequency=monthly&data[]=value&facets[process][]=STT&facets[process][]=SAE&start=1981-01`, in pages of 5,000 records, with EIA's key (read from `.env`, never saved; `REDACTED` in every saved address and in each row's `source_url`). Source id `eia:petroleum/stoc/cu`.

Two processes of product EPC0 "Crude Oil", unit "MBBL" on every record: STT "Stocks at Tank Farms" for the U.S. (NUS) and the PADDs (R10 to R50), and SAE "Ending Stocks" for Cushing (YCUOK, whose `area-name` on the page is "NA"). Session 2286's sample (`runs/c104/s2286/sample.json`, a page of 2025 asked without facets) held 84 records: STT 72 (six areas, twelve months) and SAE 12 (Cushing), nothing else. The one data page is in `warehouse/raw/eia_crude_tank_farm_stocks/20261024T052124Z/`. No page of EIA's was saved under `runs/license_reads/` for this table; EIA's verdict is read 1.

Connector: `warehouse/connectors/eia_crude_tank_farm_stocks.py` (session 2286): `[--from 1981-01] [--offline | --fresh] [--out-dir DIR]` (the docstring's usage line omits `--out-dir`), at most 10 requests a run, 3 seconds apart; a page saved in `warehouse/raw` is reused unless `--fresh`. A process, unit or area not in its map, or a key given twice, stops the run; a record without a number has no row. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. `warehouse/supabase/live_set.yaml` lists it under `catalogue_hold`.

## Vintage and revision

The page was fetched by session 2286's trial (run `20261024T052124Z`) at 2026-10-24T05:21:28Z (the raw manifest). The table was written at run `20261024T052216Z` from it ("0 requests of 10"): "File holds 3553 rows, one snapshot; the previous file held 0 rows." `retrieved_at` is 2026-10-24T05:21:28Z in every row, the time EIA served the page; `vintage` is blank.

EIA's page carries no preliminary or revision flag. The table is a snapshot: a run replaces the whole file, so a value EIA revises or withdraws is revised or gone at the next run.

## Shape and variables

Series, 3,553 rows, 7 entities `eia_crude_tank_farm_stocks:<series>` (EIA's series id), `unit` kbbl (EIA's "MBBL", thousand barrels), `freq` P1M, `market` blank, `node` EIA's series description. Every value is a whole number of kbbl.

| Area (series) | Variable | geo | Rows | Months | Mean | Lowest (month) | Highest (month) | July 2026 |
|---|---|---|---|---|---|---|---|---|
| U.S. (MCRSFUS1) | tank_farm_pipeline_stocks | US | 547 | 1981-01 to 2026-07 | 239,764.5 | 148,094 (2003-02) | 432,034 (2020-06) | 320,569 |
| East Coast, PADD 1 (MCRSFP11) | tank_farm_pipeline_stocks | US | 547 | 1981-01 to 2026-07 | 1,605.5 | 533 (2000-08) | 6,965 (2016-08) | 1,286 |
| Midwest, PADD 2 (MCRSFP21) | tank_farm_pipeline_stocks | US | 547 | 1981-01 to 2026-07 | 73,200.2 | 37,528 (2003-02) | 144,496 (2017-04) | 87,337 |
| Gulf Coast, PADD 3 (MCRSFP31) | tank_farm_pipeline_stocks | US | 547 | 1981-01 to 2026-07 | 124,613.5 | 76,251 (2004-01) | 252,286 (2020-06) | 187,433 |
| Rocky Mountain, PADD 4 (MCRSFP41) | tank_farm_pipeline_stocks | US | 547 | 1981-01 to 2026-07 | 12,884.9 | 7,594 (1996-09) | 23,797 (2020-06) | 20,081 |
| West Coast, PADD 5 (MCRSFP51) | tank_farm_pipeline_stocks | US | 547 | 1981-01 to 2026-07 | 27,460.4 | 20,082 (2002-09) | 39,323 (1987-12) | 24,432 |
| Cushing, Oklahoma (MCRST_YCUOK_1) | ending_stocks | US-OK | 271 | 2004-01 to 2026-07 | 34,865.1 | 11,294 (2004-03) | 69,414 (2017-03) | 21,337 |

kbbl; means rounded to one decimal; where a lowest or highest value recurs, its first month is given.

- **Levels.** Cushing is part of PADD 2 and the PADDs are parts of the U.S. (the header: "a sum takes one level"). The five PADDs sum to the U.S. exactly in every month; Cushing is 22.6 to 50.3 percent of PADD 2's tank farm and pipeline stocks (median 38.4), never above them.
- **Two measures.** The PADDs' and the U.S.'s series are tank farm and pipeline stocks (STT); Cushing's is EIA's "Ending Stocks" (SAE), a different process. The header and docstring say so; a reader comparing Cushing with PADD 2 compares two measures EIA publishes separately.
- Cushing at the end of December: 16,557 kbbl in 2004, 35,645 in 2009, 31,944 in 2014, 35,866 in 2019, 20,428 in 2024.

## Placing values in time, and what is filled

`ts_utc` is the first day of EIA's `period` (YYYY-MM) at 00:00:00Z, a label for the month; each value is a stock at the month's end (the header and docstring). EIA's page holds 3,553 records (its `total`), every one with a number, so every key of the page is a row and nothing is left out or filled. Each series holds every month of its span: the six STT series all 547 months from 1981-01 to 2026-07, Cushing all 271 from 2004-01.

## License

Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly")." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 1 (EIA's copyrights and reuse page, `https://www.eia.gov/about/copyrights_reuse.php`), "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", if the ERW sells anything "may be public"; EIA asks for the acknowledgment "Source: U.S. Energy Information Administration" with the date. The table's row: flag public, "agrees", ERW verdict public.

## Checks (session 2289)

The figures in this note were computed from the rows of `warehouse/output/eia_crude_tank_farm_stocks_monthly.csv`, read past its 10 header lines (counted), and from the saved page, read only (scripts `runs/c104/s2289/eia.py` and `eia_ext.py`, outputs `eia_tank_farm.out` and `tank_farm_ext.out` beside them).

- 3,553 rows, months 1981-01 to 2026-07, "3,553 records of EIA's, 3,553 rows", as header line 3 states; 7 series; no (entity, variable, ts_utc) twice; no blank value; unit kbbl throughout; geo US-OK on Cushing's 271 rows and US on the rest; each row's `node` the page's series description; no series all zero or constant, none with a month missing inside its span.
- **Against the page:** EIA's `total` is 3,553; every record has a number; the table's keys and values are the page's, with 0 differences.
- **The trial against the table:** `runs/c104/s2286/trial/eia_crude_tank_farm_stocks_monthly.csv` has the same rows past its header, byte for byte, `retrieved_at` included; the headers differ only in the run's name, its log and "1 requests of 10" against "0 requests of 10".
- Session 2286's cross-check (`runs/c104/s2286/cross.py`), run again from the main checkout with the written table as argument 1 (output `runs/c104/s2289/tank_farm_cross.out`): identical to the saved `cross.out`, which was run on the trial. The PADDs less the U.S.: 547 months, largest gap 0 kbbl; Cushing above PADD 2's tank farms in 0 of 271 months, a median 38.4 percent of them; the monthly Cushing figure against the month's last weekly figure of `eia_petroleum_supply_weekly` (its series `eia:W_EPC0_SAX_YCUOK_MBBL`): 199 months, a median gap of 1.30 percent, at most 10.58; Cushing in December 2004, 2009, 2014, 2019 and 2024 as listed above. (The script's docstring still names "the U.S. tank farm stocks against the ending stocks", the first reading the report corrects; its code compares Cushing with PADD 2.)

## Where the description and the data disagree

None found. Compared: the header's and docstring's counts (3,553 records and rows), span (1981-01 to 2026-07; Cushing from 2004), series, processes (STT "Stocks at Tank Farms", SAE "Ending Stocks", as the page names them), areas, unit, geo (US, US-OK for Cushing), the month-end stock, "a sum takes one level", "Each row carries the time EIA served its page" and "nothing is filled" against the rows and the page; the docstring's correction (the "ending stocks" series is Cushing's, from January 2004) holds on the page, where SAE appears only for YCUOK.

Not acted on: this note changes no file but itself.

Nothing to change.

## The session report against the table

Every figure of `SESSION_2286_REPORT.md` checked against the table, the saved page and the rerun cross-check holds (January 1981 to July 2026, 3,553 rows, kbbl, the U.S. and the five PADDs 547 months each, Cushing from 2004 with 271 months and geo US-OK, each row carrying the time EIA served its page, the PADDs summing to the U.S. exactly in all 547 months, Cushing never above PADD 2's tank farms and a median 38.4 percent of them, a median 1.30 percent from the month's last weekly figure over 199 months and at most 10.58, Cushing 16,557 kbbl at the end of 2004, 35,866 at the end of 2019 and 20,428 at the end of 2024, the route's metadata 1981-01 to 2026-07, 3 requests of the session's 20, the write reusing the trial's page). No claim was found that does not hold.

## What it does not hold

- Crude stocks at refineries, in leases and in the Strategic Petroleum Reserve, total crude stocks, Cushing before 2004 and its tank farm and pipeline split, the weekly figures (`eia_petroleum_supply_weekly`), storage capacity, the route's annual figures, and months before 1981 and after July 2026.
