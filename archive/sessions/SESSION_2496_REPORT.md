# Session 2496 report: Grenada's electricity produced and consumed by category, 2000 to 2023 (CSO Grenada), the session's own choice, internal

24 October 2026, from about 15:10 UTC to 15:14 UTC for the reads and the connector; the table written under the data lock at 16:29 UTC. On lab-desktop (the data machine), chain 121, unattended. Precheck passed (`runs/c121/pre2496.out`). Model spend USD 0. Pulls: 9 requests of 20 (8 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Why Grenada:** a national grid the ERW did not hold and no chain had planned (`sources.csv`, the connectors and the queue on main and on chains 118's to 120's branches), whose statistics office publishes its electricity table as an HTML table, a year a column, 2000 to 2023. A search for Hungary's KSH tables found it instead.
- **The Central Statistical Office of Grenada (CSO):** stats.gov.gd's robots file disallows nothing (read 839).
- **A new table, `grenada_cso_electricity_annual`** (series, 144 rows, 5 entities, `power`), from "Production and Consumption of Electricity by Category, 2000 to 2023":
  - the volume produced (`generation`);
  - the volume consumed by category (domestic, commercial, industrial, street lights) and its total (`consumption`).
  - Thousands of kWh are MWh. The value section (EC$) is not taken.
  - The consumption total is written as printed; its largest gap from its categories is 0.2 MWh.
  - Written by run `20261024T162952Z`, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set.
- **Internal, not settled.** The site's terms (read 841): the contents "are protected by copyright"; "Access and use of the Data is subject to the requirements set forth under the Open Licence Agreement". The agreement's link points at statsgrd.com, which does not resolve (read 843). Its page on stats.gov.gd has a title and no text (read 845). No verdict is written. Saint Lucia's office, built on the same frame (session 2497), publishes an open licence; Grenada's text was not there to read.

## Cross-checks

- Production over `owid_ember_electricity_annual`'s demand for Grenada: 0.96 to 1.05 (2000 to 2022), 1.09 in 2023.
- Produced, GWh: 133.5 in 2000, 239.1 in 2019, 219.9 in 2020, 261.2 in 2023. The page "Production and Consumption of Electricity, 2000 to 2023" (read 840) gives the same production and total consumption.

## Requests (9 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | stats.gov.gd/robots.txt | 200: nothing closed |
| 2 | the production and consumption page | 200 |
| 3 | the terms and conditions | 200 |
| 4 | the site's search for electricity | 200 |
| 5 | statsgrd.com/robots.txt (where the terms link the licence) | the name does not resolve |
| 6 | the site's search for licence | 200 |
| 7 | the Open Licence Agreement page | 200: a title, no text |
| 8 | the by-category page | 200 |
| 9 | the by-category page (the fetch) | 200 |

Reads recorded: 839 to 846 (on this branch). Two web searches (Hungary's KSH tables; Grenada's office) reached no publisher's host.

## Decisions made without you

- **Grenada as the session's own choice.**
- **Internal** while the open licence's text cannot be read.

## For Samuel's ruling

- **Grenada's Open Licence Agreement:** if the CSO publishes its text (its link points at a dead name), the table may be public. A letter to the CSO would settle it.

## Files

- New: `warehouse/connectors/grenada_cso_electricity.py`, `tests/test_session2496.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 839 to 846).
- On the data machine only: `runs/c121/s2496/`, `warehouse/raw/grenada_cso_electricity/`, `warehouse/output/grenada_cso_electricity_annual.csv`.
