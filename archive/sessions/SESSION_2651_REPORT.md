# Session 2651 report: Aland's electricity supply by origin a year, 1994 to 2025 (ASUB's PxWeb table MI009), public, a second source of the session's own choosing

25 October 2026, about 08:50 to 08:58 UTC, on lab-desktop (the data machine), chain 132, unattended. Precheck passed (`runs/c132/pre2651.out`). Model spend USD 0. Pulls: 11 requests of 20 (10 by the probe, 1 POST the connector's online trial made; the write reads it offline).

## Why this source

- **The ERW held Aland in no table** of its own (Statistics Finland's national figures include it), and no chain or queue file had taken it. Aland imports most of its power from Sweden, and its own wind production grew from 15 GWh in 2000 to 202 GWh in 2025, more than half its supply.
- **North Macedonia and Moldova** were checked first: both are held already (MakStat, session 2357; StatBank Moldova).

## Read these first

- **The hosts:** www.asub.ax's robots file closes only Drupal's system paths, with no AI agent named (read 1317, read with its comments stripped). pxweb.asub.ax has no robots file (HTTP 404, read 1321).
- **The way in:** ASUB's Miljo och energi page (read 1320) shows seven PxWeb tables, the first "Elanskaffningen pa Aland" (MI009). The PxWeb API (reads 1322 to 1325) gives MI009 for 1994 to 2025 (updated 29 January 2026): GWh and per cent by origin.
- **The terms** (read 1326, ASUB's Anvandarvillkor): the site's material, "texter, tabeller som diagram och infografik", is under CC BY 4.0, free to copy, adapt and spread, with ASUB named as the source and changes stated. Third parties' material, photographs and the logo are excepted; MI009 names ASUB as its source. **Verdict: may be public.** The table is **public**.
- **A new table, `asub_aland_electricity_annual`** (series, 190 rows, 7 entities, `power`), from one JSON-stat POST (the GWh figures, every origin and year):
  - imports from Sweden and Finland (`imports`); oil, wind, bioenergy and solar (`generation`); the total (`supply`). MWh is the table's GWh times 1,000.
  - Supply was 209.4 GWh in 1994 and 350.6 GWh in 2025: wind 202.4, imports from Sweden 127.4, solar 15.8, Finland 4.0, bioenergy 0.9.
  - Each year's origins add to its total within 0.5 GWh. A cell without a number has no row: bioenergy begins in 2008, solar in 2014.
  - ASUB's note: physical production only, not trade (all of it is traded on Nord Pool); solar is estimated from installed panels.
  - `vintage` is empty: the answer's "updated" field is the table's 2008 creation, not its last update.
  - Written by run `20261025T085607Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T085611Z-local`), held from the live set; in the release package (public). The Stanford draft is session 2653's.
- **Not taken:** the per cent rows; MI010 (sales by region and sector), for a later chain.

## Cross-checks

- EIA's world table holds no Aland. ASUB's pocket yearbook (searched, not fetched) gives 2024 as 351 GWh in all, 127 from Sweden, 8 from Finland and about 204 of wind; MI009 gives 351.5, 127.0, 7.5 and 203.5. ASUB's text gives 2023's wind as 172.3 GWh, as MI009 does.

## Requests (11 of 20)

| n | What | Outcome |
|---|---|---|
| 1 to 4 | www.asub.ax's robots file, a guessed page, the statistics index and the Miljo och energi page | 200 (the guess 404) |
| 5 | pxweb.asub.ax's robots file | 404 |
| 6 to 9 | the PxWeb API's databases, subjects, MI tables and MI009's metadata | 200 |
| 10 | ASUB's Anvandarvillkor | 200 |
| 11 | MI009 (the POST, by the connector's online trial) | 200 |

Reads recorded: 1317 to 1326.

## Decisions made without you

- **Aland as the second own choice; public** under ASUB's CC BY 4.0.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/asub_aland_electricity.py`, `tests/test_session2651.py`, this report.
- Changed: the registration; the metadata files; the release package (`docs/redivis/release-v1/`); the license record (reads 1317 to 1326, ASUB's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c132/s2651/`, `runs/license_reads/s2651/`, `warehouse/raw/asub_ax/`, `warehouse/output/asub_aland_electricity_annual.csv`.
