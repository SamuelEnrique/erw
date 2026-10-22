# Offshore oil and gas production by lease, a month, the Gulf of America (BOEM OGOR-A)

Energy Research Warehouse (ERW), method note written in session 677 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `boem_ogor_lease_production_monthly`

Connector: `warehouse/connectors/boem_ogor.py` (session 611; session 619 changed the ceiling and the repeated lines).

## Publisher and report

Bureau of Ocean Energy Management (BOEM), Oil and Gas Operations Reports Part A (OGOR-A), well production, from BOEM's Data Center (`https://www.data.boem.gov/Main/OGOR-A.aspx`; record layout `https://www.data.boem.gov/Main/HtmlPage.aspx?page=ogorA`). One delimited file a year, each a zip holding one text file:

- `https://www.data.boem.gov/Production/Files/ogora<year>delimit.zip` for a past year;
- `https://www.data.boem.gov/Production/Files/ogoradelimit.zip` for the current year (its name has no year: session 611 found `ogora2026delimit.zip` answering an HTML page).

The connector asks `ip.paused` and `ip.paused_host` first and stops if BOEM's host is paused.

## Vintage and revision rule

The header gives years 1996 to 2026, months 1996-01 to 2026-06, 4,654 leases, 1,131,562 rows. `--from` and `--to` set the years (defaults 2015 and the current year); this table was written with years from 1996. `vintage` on each row is the year's file's Last-Modified time, in UTC.

The table is written with `ip.write_snapshot`: each run replaces the whole table, and the header says the previous file held 245,710 rows. A year's file an earlier run saved in `warehouse/raw/boem_ogor/` is reused unless `--fresh`; `--offline` asks nothing. A year BOEM revises therefore reaches the table only when its file is asked again. Ceiling: 21 requests a run (a saved file is no request), 3 seconds apart.

## Why OGOR-A

Session 611 read BOEM's record layout and code pages. OGOR-B gives a lease's dispositions under 48 codes, and BOEM's pages do not say which make the lease's production, so a sum of them would be the ERW's reading. OGOR-A gives each completion's production as BOEM defines it.

## Shape

Series. One row per lease, variable and month.

- `entity`: `boem_lease:<lease number>` (BOEM's LEASE_NUMBER, for example `boem_lease:00016`), or `boem_unit:<unit agreement number>` for rows BOEM gives under a unit agreement with no lease number (15 such entities).
- `variable`: `oil_production`, unit `kbbl`, and `gas_production`, unit `MMcf`: the sum over the lease's completions and producing intervals of BOEM's MON_O_PROD_VOL (barrels) and MON_G_PROD_VOL (thousand cubic feet), divided by 1,000. 565,781 rows of each.
- `ts_utc`: the production month's first day at 00:00:00Z; `freq` `P1M`; `geo` `US` (federal offshore, no state); `market` empty.
- `node`: the lease's operators that month, as BOEM names them, joined by "; ".
- `source` `boem:ogor_a`, `source_url` the year's file, `retrieved_at`, `vintage`.

## License

ERW verdict: public (`docs/licenses.md`). Header: License: public (a work of the U.S. government; cite "Bureau of Ocean Energy Management, OGOR-A Well Production").

## Cross-check

None run by the connector. Session 611 found the sum of OGOR-A for the Federal Gulf equal to EIA's Federal Offshore Gulf of America crude oil production in January 2024 (54,389 kbbl in both), as the docstring records. The connector checks each file: the field count of every line, each month read as YYYYMM and within the file's year, whole-number volumes, a lease or a unit agreement on every row, and no completion, interval and month given twice; any failure stops the run.

## What it does not hold

- Water and injection volumes are not taken.
- Dispositions (OGOR-B) and well-level rows: completions are summed to the lease.
- A completion's zero is kept (a reported month with no production); nothing is filled.
- A line BOEM repeats in every field is kept once (1 such line, counted in the header); a key repeated with any field different stops the run.
- Months BOEM has not yet published for the current year (the table ends at 2026-06).
