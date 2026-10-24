# Session 2413 report: Eurostat's gross electricity production by fuel, a year from 1990 (the second own choice); Taiwan and Chile not taken

24 October 2026, from 10:46 UTC, on lab-desktop (the data machine), the eighth session of `queue/done/114-day-15-november-data-paraguay-panama-guatemala-namibia.md`, unattended. Precheck passed (`runs/c114/pre2413.out`). Model spend USD 0. Pulls: 13 of 20 (below).

## Read these first

- **Two candidates closed before the choice:**
  - **Taiwan (Taipower's daily supply and demand, data.gov.tw dataset 19995):** data.gov.tw's robots file answers HTTP 500, read as disallowing every path (read 747). Taipower's own host has no robots file (read 748), but the page a web search named is its error page (read 749), and no data file was found without more guessing.
  - **Chile (the CNE's Energia Abierta, "Balance Energía Regional"):**
    - the portal's robots file allows the reader (read 750);
    - its downloads are links on a link shortener (read 752), which allows every path (read 753);
    - a HEAD request shows the regional balance's link leads to a SharePoint share (read 754), and `comisionenergia-my.sharepoint.com`'s robots file disallows every path (read 755);
    - so the file was not fetched.
- **The choice:** Eurostat's `nrg_bal_peh`, production of electricity and derived heat by type of fuel. The ERW holds Eurostat's monthly net production (`eurostat_electricity_monthly`, from 2016) and its capacity tables, but not the annual production by fuel back to 1990. No chain has taken it.
- **One public table:** `eurostat_electricity_production_annual`, 73,988 rows, 1990 to 2024. It is written, validated, archived, in coverage (sector power), held from the live set, and listed in the release's held tables:
  - gross electricity production (GEP, all producers, the plants' own use included) for the 58 of the file's 75 SIEC products that have a value (this line first said 75; corrected in session 2415) and 39 areas (the EU's members, EFTA's and the candidates, with EU27_2020; the United Kingdom and Kosovo left out by Eurostat's terms, as `eurostat_gas_balance_monthly` does);
  - in MWh (Eurostat's GWh times 1,000);
  - the products' names from Eurostat's SIEC codelist (read 759);
  - the products are a hierarchy whose levels overlap, which the header says.
- **Eurostat's TOTAL is its top groups plus pumped hydro (RA130)**, which renewables leave out, **and batteries (BA100)**. With batteries, it holds within 1 GWh in all 1,279 country years (the largest gap 0.634 GWh). This line first left batteries out and counted 49 country years, all 2020 to 2024, the largest the EU in 2024 (1,040 GWh); session 2415's note found them, and the check now adds batteries.
- **Zeros and blanks:** 47,987 zeros are kept as Eurostat prints them. 21,179 blanks (flag m, missing) have no row.
- **License: public** (Eurostat's copyright notice, the record's verdict since session 2123). `ec.europa.eu`'s robots file does not disallow `/eurostat/api/dissemination/` and names no AI agent (read 756).
- **Test 205's bound raised by 40** for this chain's reads, which reach 692 on this branch.

## The cross-check (`runs/c114/s2413/cross.py`, `cross.out`; tables read past their header lines)

- **Annual gross production against the year's sum of `eurostat_electricity_monthly`'s net production** (332 country years with all twelve months):
  - Gross is above net by a median 6.1 per cent, and by 0.1 to 16.8 per cent between the 5th and 95th percentiles: the plants' own use (EU 2023: 2,760.9 against 2,572.0 TWh; Germany 1.147; Norway 1.006).
  - Gross is below net in a few country years: Albania from 2018 to 2024 (0.969 to 0.996), Iceland in 2020 (1.000 to three places), Luxembourg in 2021 (0.974) and Moldova in 2020 (0.920) (Iceland added in session 2415). These come from Eurostat's two data sets, and this report does not explain them.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| data.gov.tw | 1 | robots (500) |
| www.taipower.com.tw | 2 | robots (no file), a page (error) |
| energiaabierta.cl | 3 | robots, the home page, the electricity statistics |
| 3b9x.short.gy | 2 | robots, one link (HEAD) |
| comisionenergia-my.sharepoint.com | 1 | robots (disallows every path) |
| ec.europa.eu | 4 | robots, one year of every dimension, the production file (7.4 MB), the SIEC codelist |
| total | 13 of 20 | |

## Errors

- None.

## Decisions made without you

- **A robots file answering HTTP 500 is read as disallowing everything,** so data.gov.tw is not used.
- **A SharePoint share behind a robots file that disallows every path is not fetched,** though the portal linking to it allows the reader.
- **Eurostat's annual production by fuel** as the second own choice: the item `GEP` in GWh only, from 1990.

## For Samuel's ruling

- None.

## Files

- New:
  - `warehouse/connectors/eurostat_electricity_production.py`
  - `tests/test_session2413.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`
  - `warehouse/metadata/license_reads.csv` (747 to 759), `license_tables.csv`, `docs/licenses.md`
  - `tests/test_session205.py` (the bound)
  - the coverage, sources and archive manifest files, and the release README's held line and lists
- On the data machine only: `runs/c114/s2413/`, `runs/license_reads/s2413/`.
