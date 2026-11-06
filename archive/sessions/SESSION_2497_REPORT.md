# Session 2497 report: Saint Lucia's electricity output and consumption, 2010 to 2023 (CSO Saint Lucia, LUCELEC's figures), the second own choice, internal

24 October 2026, from about 15:14 UTC to 15:18 UTC for the reads and the connector; the table written under the data lock at 16:29 UTC. On lab-desktop (the data machine), chain 121, unattended. Precheck passed (`runs/c121/pre2497.out`). Model spend USD 0. Pulls: 10 requests of 20 (9 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Why Saint Lucia:** a national grid the ERW did not hold and no chain had planned, whose statistics office, on the same frame as Grenada's, publishes an Open Licence Agreement.
- **The Central Statistical Office of Saint Lucia (CSO):** stats.gov.lc's robots file disallows nothing (read 847). Its search lists five electricity pages (read 849), the newest "Electricity Output and Consumption in Kilowatt Hours (KWh) Thousands, 2010 to 2023" (last updated 28 May 2024).
- **A new table, `slu_cso_electricity_annual`** (series, 139 rows, 7 entities, `power`):
  - units generated or purchased (`generation`), sales by class (`sales`), internal use (`own_use`), transmission losses (`losses`), in MWh (thousands of kWh);
  - the available capacity (`available_capacity`), from kW to MW.
  - The commercial row's figures marked "*" include hotels (2013 on); those without exclude them (2010 to 2012). They are two entities, so a sum over classes never counts hotels twice by accident.
  - Not written: one cell out of form (2016's commercial, "194,66*") and cells "..", counted.
  - Written by run `20261024T163001Z`, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set.
- **Internal.** The CSO's Open Licence Agreement (read 852) grants "a worldwide, royalty-free, non-exclusive licence to freely use the information ... for commercial and non-commercial purposes", but it "is limited solely to CSO data and shall not extend to any third party data". The table's source is LUCELEC.
  - LUCELEC: www.lucelec.com's robots file asks a crawl delay of 10 seconds, kept (read 853). Its home page reads "Copyright © 2025 St. Lucia Electricity Services Limited. All Rights Reserved." (read 854). Its website terms disclaim liability and grant no reuse (read 855).
  - Two verdicts: the CSO may be public (its own data); LUCELEC needs written permission. The source registry names both publishers for the table, so the license record's worst verdict, and the table's flag, is internal.

## Cross-checks

- Units generated or purchased over `owid_ember_electricity_annual`'s demand for Saint Lucia: 0.95 to 1.06 (2010 to 2023).
- The CSO's 2011 to 2017 page (read 848) agrees on domestic and industrial sales and on generation within 1 MWh. Its commercial row includes hotels every year (2011: 190,846 = 122,098 + 68,749), which bears out the reading of the "*".

## Requests (10 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | stats.gov.lc/robots.txt | 200: nothing closed |
| 2 | the 2011 to 2017 page | 200 |
| 3 | the site's search for electricity | 200 |
| 4 | the 2010 to 2023 page | 200 |
| 5 | the terms and conditions | 200 |
| 6 | the Open Licence Agreement | 200 |
| 7 | www.lucelec.com/robots.txt | 200: a crawl delay of 10 seconds |
| 8 | LUCELEC's home page (10 seconds after) | 200 |
| 9 | LUCELEC's website terms (10 seconds after) | 200 |
| 10 | the 2010 to 2023 page (the fetch) | 200 |

Reads recorded: 847 to 855 (on this branch).

## Decisions made without you

- **Saint Lucia as the second own choice.**
- **Internal under LUCELEC,** though the CSO's licence is open: the licence excludes third-party data, and the table names LUCELEC as its source.
- **The commercial row split into two entities** by the CSO's "*".
- **Test 205's bound raised by 40** for this chain's reads (they passed 802 here).

## For Samuel's ruling

- **LUCELEC's consent,** if Saint Lucia's table is wanted public.

## Files

- New: `warehouse/connectors/slu_cso_electricity.py`, `tests/test_session2497.py`, this report.
- Changed: the registration; the metadata files (two source rows, one a publisher); the license record (reads 847 to 855, two verdicts); `tests/test_session205.py` (its bound).
- On the data machine only: `runs/c121/s2497/`, `warehouse/raw/slu_cso_electricity/`, `warehouse/output/slu_cso_electricity_annual.csv`.
