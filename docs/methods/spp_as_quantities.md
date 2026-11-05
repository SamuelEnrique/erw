# SPP's operating reserves cleared in the day-ahead market, by product, an hour, from September 2024 (SPP Marketplace portal, Market Clearing, DA-MC files)

Energy Research Warehouse (ERW), method note written in session 2180 (chain 097) for a table first written on 4 October 2026 (session 100). Session 100's own account of the pull, the products' duration rules and the fleet-limited estimate is `docs/methods/reserve_quantities_nyiso_spp.md`.

Tables: `spp_as_quantities`

## Publisher and address

Southwest Power Pool (SPP), the Marketplace portal's public file browser, folder "Market Clearing" (`https://portal.spp.org/pages/market-clearing`, named in the header and not asked), one CSV an operating day with, by hour and BAA, the MW cleared in the Day-Ahead Market of each operating reserve product (columns RegUP, RegDN, Spin, Supp, RampUP, RampDN, UncUP) among other columns:

- `https://portal.spp.org/file-browser-api/?fsName=market-clearing&path=/<year>&type=folder` (the year's folder list, JSON; asked again on every run to learn whether SPP holds the year as one zip)
- `https://portal.spp.org/file-browser-api/download/market-clearing?path=/<year>/<year>.zip` (a year SPP has archived)
- `https://portal.spp.org/file-browser-api/download/market-clearing?path=/<YYYY>/<MM>/DA-MC-<YYYYMMDD>0100.csv` (a day of a year not archived)

The connector sends no User-Agent of its own (the requests library's default). No reading of portal.spp.org's robots file is recorded in `warehouse/metadata/license_reads.csv`; this note made no request. Session 100's report counts "646 requests to `portal.spp.org` for the table (three folder lists, the 2024 archive, 642 daily files)".

Source id `spp:DA-MC` (in `sources.csv`, license public, first and last seen 2026-10-04). Connector: `warehouse/connectors/spp_as_quantities.py` (session 100), its only table, on the loop the reserve price connectors share, `warehouse/connectors/iso_as_common.py`, with the table's own unit (MW) and ceiling (300,000 rows). `warehouse/connectors/spp_dam_cleared.py` reads this connector's saved daily files for its own table. `warehouse/supabase/live_set.yaml` holds the table out of the live catalogue (`catalogue_hold`, session 102: no page reads it from Supabase).

No schedule runs it: no line of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, the `warehouse/refresh_*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2180), and `run_status.csv` holds no row for it. Session 100's report asked for "one line for spp_as_quantities.py beside spp_as_prices.py wherever that runs"; `spp_as_prices` has no scheduled step either (`license_verdicts.csv`, session 308).

## Vintage and revision

One run, `20261004T113434Z`, on the data machine of that day (session 100's report: the old laptop, `samueloldlaptop`, 4 October 2026, about 11:23 to 12:00 UTC). Operating days 1 September 2024 to 4 October 2026 (Central; `ts_utc` 2024-09-01T05:00:00Z to 2026-10-05T04:00:00Z): the run included the day it ran on, whose day-ahead file was already posted. `retrieved_at` runs from 2026-10-04T11:32:49Z (the 2024 archive) to 11:50:47Z; `vintage` is empty. The file on the data machine was restored from the Redivis draft by `scripts/sync.py` (its last header line). `coverage.csv` gives the same 159,768 rows, two nodes, the same first and last `ts_utc`, and last run 2026-10-04T11:34:34Z.

A day's file is marked settled: once saved in `warehouse/raw/spp_as_quantities/` it is never asked again, so a later run reads it from the machine. The folder lists are asked every run. Each run reads every day from 1 September 2024 again (from the raw files where it can) and merges its rows into the held file on (entity, variable, ts_utc) (`ip.write_csv`).

## Shape and variables

Series, 159,768 rows, two entities, seven variables. `entity` `spp:SPP` and `spp:SWPW`, the file's BAA column as it names them (the file does not say what SWPW stands for); `variable` `quantity_mw_dam_<product>`; `value` the MW of the product cleared for the hour, as the file gives it (every value is a whole number); `unit` MW; `freq` PT1H; `ts_utc` the file's `GMTIntervalEnd` less one hour, the start of the hour; `geo` "US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY" in every row; `market` spp_dam; `node` SPP or SWPW; `source` `spp:DA-MC`; `source_url` the 2024 archive or the day's file (643 addresses: the archive and 642 daily files); `vintage` empty. There are no `x_` columns.

| `variable` | SPP's column | spp:SPP: mean (lowest, highest) MW | spp:SWPW: mean (lowest, highest) MW |
|---|---|---|---|
| `quantity_mw_dam_regup` | RegUP | 482.8 (155, 987) | 120.2 (50, 246) |
| `quantity_mw_dam_regdn` | RegDN | 443.8 (183, 930) | 103.2 (60, 158) |
| `quantity_mw_dam_spin` | Spin | 673.6 (275, 1,105) | 87.2 (16, 168) |
| `quantity_mw_dam_supp` | Supp | 703.5 (364, 1,207) | 104.7 (60, 181) |
| `quantity_mw_dam_rampup` | RampUP | 576.8 (133, 2,010) | 112.0 (0, 243) |
| `quantity_mw_dam_rampdn` | RampDN | 563.2 (200, 1,973) | 116.4 (40, 262) |
| `quantity_mw_dam_uncup` | UncUP | 784.9 (0, 4,970) | 103.3 (0, 549) |

`spp:SPP` holds 18,336 hours of each product: 764 Central days, 1 September 2024 to 4 October 2026, with 25 hours on 3 November 2024 and 2 November 2025 and 23 on 9 March 2025 and 8 March 2026. `spp:SWPW` holds 4,488 hours of each, 187 days from 1 April 2026, when the BAA column first appears. 7 x 18,336 + 7 x 4,488 = 159,768. No hour is missing inside a series and no (entity, variable, ts_utc) is given twice. A quantity of 0 is a quantity and is kept: UncUP is 0 in 6,078 hours of `spp:SPP` and 1,399 of `spp:SWPW`, and SWPW's RampUP in 2.

The counts in this note were computed in session 2180 with pandas from the rows of `warehouse/output/spp_as_quantities.csv`, read past its 13 header lines. They agree with session 100's report and with `reserve_quantities_nyiso_spp.md` (159,768 rows).

## Checks the connector makes

- Before any request, `iso_as_common.run` asks `iso_prices.paused("spp")`; a paused publisher gets no request and its table is not rewritten. SPP is not in `warehouse/metadata/paused_sources.csv`. `paused_host()` is not asked (the host is fixed in the code).
- `--start` may not be before 2024-09-01, the approved start.
- A day's file must hold `GMTIntervalEnd` and the seven product columns, or the run stops. A file with no BAA column must hold one row an hour (it is written as SPP), or the run stops. A file must hold a row named SPP. A BAA other than SPP and SWPW is logged and not kept.
- A file holding an hour outside its operating day stops the run.
- An empty cell gives no row; a cell that is not a number stops the run.
- Never filled: a (BAA, product, operating day) is written only when every hour of the day is there exactly once (24, or 23 and 25 at the clock changes); a shorter one is left out, logged and recorded as a gap. The header: "0 are left out of this run". A day missing from a year's archive is logged and skipped.
- A (BAA, product, hour) given twice, in one file or in two, stops the run.
- Ceiling: 300,000 rows, counted over all the run's rows after the complete-day rule (not the new ones); past it nothing is written.
- Each document is tried up to four times, 5, 10 and 15 seconds apart (`iso_prices.fetch_raw` and `with_retries`); HTTP 404 is not retried and is a gap. One second after each document fetched (none after one read from `warehouse/raw/`).
- `--offline` reads the raw files only; `--until` sets the first day not read; `--out-dir` writes a trial elsewhere.

## License

The header: "License: public, with citation. SPP's terms (https://www.spp.org/terms-conditions/): "Permission is implicitly granted to copy and distribute (via computer network or printed form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication". A commercial use needs SPP's written authorization." `license_verdicts.csv` gives SPP "may be public" (read 6), and "needs written permission" if the ERW sells anything. `license_tables.csv` names SPP as the table's one publisher (from the source registry), and `docs/licenses.md` gives the ERW verdict public. `coverage.csv`: public.

## Found while writing this note

- The docstring's usage line says a run reads "2024-09-01 to yesterday (Central)". The code's default end is tomorrow, not included, so a run reads to today: the run of 4 October 2026 wrote 4 October.
- The header ends with "Method: docs/methods/capacity_and_ancillary.md", a line `iso_as_common.py` writes for every reserve table. That note says its tables "hold prices only: no cleared MW" and does not name this table; the docstring names `docs/methods/reserve_quantities_nyiso_spp.md`.
- The ceiling counts the whole window, which every run reads again from 1 September 2024, not the new rows. From two BAAs, seven products and 24 hours, the window grows by 336 rows a day; from 159,768 rows it passes 300,000 after 418 more days, about 26 November 2027, and from then on every run would write nothing.
- The table has not been refreshed since 4 October 2026: no schedule runs the connector.

## What it does not hold

- Reserve prices (`spp_as_prices`), the file's other columns (generation, demand, virtuals, prices; demand is in `spp_dam_cleared_energy`), and real-time quantities.
- Any day before 1 September 2024 or after 4 October 2026.
