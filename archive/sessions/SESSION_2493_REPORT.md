# Session 2493 report: Malawi's electricity sales by type of user, 1992 to 2019 (NSO's Statistical Year Book 2023, from ESCOM), internal

24 October 2026, from about 15:02 UTC to 15:07 UTC for the reads and the connector; the table written under the data lock at 16:29 UTC. On lab-desktop (the data machine), chain 121, unattended. Precheck passed (`runs/c121/pre2493.out`). Model spend USD 0. Pulls: 7 requests of 15 (6 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **The ERW held no Malawian source** (`sources.csv`, the connectors and the license record on main and on chains 118's to 120's branches).
- **The hosts:**
  - EGENCO's www.egenco.mw: its certificate fails verification at its robots file (read 832); not asked again;
  - the regulator MERA: mera.mw's robots file closes admin paths and `*/disclaimer/*` and names no AI agent (read 834); its site search finds nothing for "electricity statistics" or "statistics" (reads 836, 837);
  - the National Statistical Office (NSO): www.nsomalawi.mw and cms.nsomalawi.mw answer HTTP 404 for a robots file (reads 833, 835).
- **A new table, `nso_malawi_electricity_sales_annual`** (series, 140 rows, 5 entities, `power`), from table 10.1 of NSO's Statistical Year Book 2023 (source: ESCOM): the units sold a year, 1992 to 2019, in total and to power, general tariff and domestic users and for export.
  - Read by the position of its words: each quantity column is the span of its "Kwh" heading, and a figure's digit groups (thousands written with spaces) are joined within it. The value columns (MWK) between them are not read.
  - Millions of kWh times 1,000 to MWh.
  - Written as printed, and listed in the header: the years whose classes do not sum to the total (2003, 2009, 2010, 2018). In 2010 the power column repeats the total.
  - Written by run `20261024T162927Z`, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set.
- **Internal.** The year book states no terms; NSO's home page reads "Copyright © 2026 National Statistical Office of Malawi. All Rights Reserved" (read 838, session 2495). Verdict: needs written permission.
- **Not what the plan asked:** generation by station, imports and the peak demand. No public source of them was found within the ceiling; the year book's table is sales, and it ends in 2019.

## Cross-checks

- Total sales over `owid_ember_electricity_annual`'s demand for Malawi: 0.70 to 0.79 in most years, 0.92 in 2019.
- **Years that do not fit their neighbours, as printed:** 1998 (1,598.4 GWh) is about twice 1997 and 1999; 2014 and 2015 (722.0 and 768.0 GWh, 0.34 and 0.36 of Ember's demand) are about half of 2013 and 2016; 2012 is 0.59. The year book notes none of them. The method note warns against reading a trend from them.

## Requests (7 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.egenco.mw/robots.txt | the certificate fails verification |
| 2 | www.nsomalawi.mw/robots.txt | 404 |
| 3 | www.mera.mw/robots.txt | 200 (at mera.mw): admin paths closed |
| 4 | cms.nsomalawi.mw/robots.txt | 404 |
| 5 | MERA's site search for electricity statistics | 200: no result |
| 6 | MERA's site search for statistics | 200: no result |
| 7 | the Statistical Year Book 2023 (the fetch) | 200, 16.4 MB |

Reads recorded: 832 to 837 (on this branch). Three web searches found EGENCO's status notices, ESCOM's 2013 report (on a World Bank host, not asked) and NSO's year books; they reached no publisher's host.

## Decisions made without you

- **NSO's sales table for Malawi** rather than no table: it is the publisher's own national statistic, from ESCOM, and its odd years are flagged, not corrected.
- **Figures written as printed** where the classes do not sum to the total; the years are listed.

## For Samuel's ruling

- **NSO's consent,** if Malawi's table is wanted public.

## Files

- New: `warehouse/connectors/nso_malawi_electricity.py`, `tests/test_session2493.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 832 to 837).
- On the data machine only: `runs/c121/s2493/`, `warehouse/raw/nso_malawi_yearbook/`, `warehouse/output/nso_malawi_electricity_sales_annual.csv`.
