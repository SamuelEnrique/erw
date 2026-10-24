# Session 2397 report: a third source of the session's own choosing (Iceland's public power plants, Statistics Iceland), public

24 October 2026, from 10:11 UTC, on lab-desktop (the data machine), chain 113, unattended. Precheck passed (`runs/c113/pre2397.out`). Model spend USD 0. Pulls: 16 requests of 20 (12 by the probe, 4 by the fetch the connector reads offline).

## Read these first

- **Why this source:** the ERW held Iceland only inside Eurostat's renewable capacity table and, from 2017, in `eurostat_electricity_monthly`. Iceland is not among the countries of chains 113, 114 and 115, and no chain or connector named Statistics Iceland, Orkustofnun or Landsnet (main and the wip branches of chains 110 and 114 searched). Estonia, the first thought, is held (`statee_electricity`).
- **The hosts:**
  - px.hagstofa.is (the PxWeb API) has no robots file (HTTP 404, read 691).
  - www.hagstofa.is's robots file asks a crawl delay of 10 seconds and closes system paths only (read 698). The two requests to it were 10 seconds apart.
  - statice.is, which answers the English pages, has no robots file (read 701).
  - No rule names an AI agent.
- **A new table, `hagstofa_iceland_power_annual`** (series, 88 rows, `power`): the public power plants' installed capacity at the year's end (MW) and annual generation (MWh), 1976 to 2019, table IDN02101. Statistics Iceland gives its source as the National Energy Authority's documents OS-2018-T006-01 and OS-2019-T006-01. Written, validated (0 errors, 0 warnings), archived, and held from the Redivis storage and the live set like the chain's other tables.
- **Public, under CC BY 4.0.** Statistics Iceland's terms of use (read 702): "All published content on the Statistics Iceland website may be reused, copied, and shared in any format or medium for any purpose as long as Statistics Iceland is credited as the author in accordance with the Creative Commons Attribution 4.0 International (CC BY 4.0) license." `license_verdicts.csv` gains Statistics Iceland, "may be public".
- **Not taken:**
  - **IDN02100 (1904 to 1975).** It was fetched, but its figures run about twice IDN02101's where the two meet: 1975 has 992.4 MW and 4,591 GWh, 1976 has 502.7 MW and 2,421.4 GWh. Neither table explains the step, so they are not joined. The parser reads either table; `TABLES` names IDN02101 only.
  - **IDN02103 (heavy industry's use) and IDN02104 (use by sector).** An empty query returned one default series of each, not the whole table. Asking for their metadata and a full query would have passed the ceiling. Both tables stop in 2018 or 2019.
  - IDN02101's second unit ("Hlutfall", 100 in every cell).
- **Every table in the folder ends by 2020** (updated 2008 to 2021). The table is a history, not a current series.

## Cross-checks

- Generation over `owid_ember_electricity_annual`'s demand for Iceland: 1.007 to 1.021, 2000 to 2019. Iceland has no interconnector, so generation and demand should nearly agree.
- Over `eurostat_electricity_monthly`'s net production for Iceland (twelve months, 2017 to 2019): 1.000.
- Generation TWh: 1976 2.42, 1990 4.45, 2000 7.68, 2010 17.06, 2019 19.49. Capacity 502.7 MW in 1976, 2,923.4 MW in 2019.

## Requests (16 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | px.hagstofa.is/robots.txt | 404 |
| 2 | a guessed energy folder | 400 |
| 3 to 7 | the PxWeb API's databases and folders | 200: Umhverfi, Energy, Production and consumption, six tables |
| 8 | www.hagstofa.is/robots.txt | 200: crawl delay 10 s |
| 9 | the English home page | 200, answered by statice.is |
| 10 | the open data page on www.hagstofa.is | its error page |
| 11 | statice.is/robots.txt | 404 |
| 12 | statice.is, Open data access | 200: CC BY 4.0 |
| 13 to 16 | IDN02100, IDN02101, IDN02103, IDN02104 (the fetch, one POST each) | 200 |

Reads recorded: 691 to 702.

## Decisions made without you

- **The table's coverage, sources and archive manifest rows went in with session 2394's commit (25f25640).** The write had staged them in the branch when that commit was made a second later; their content is the write's, and they are not committed twice.

- **Public under Statistics Iceland's CC BY 4.0,** Statistics Iceland credited in the header.
- **IDN02100 left out** for its step against IDN02101, rather than joined.
- **A historical table taken** although it ends in 2019: Iceland had no ERW table of its own, and the history back to 1976 is not in Ember's or Eurostat's tables.

## For Samuel's ruling

- None.

## Files

- New: `warehouse/connectors/hagstofa_iceland_electricity.py`, `tests/test_session2397.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`;
  - the license record (reads 691 to 702, Statistics Iceland's verdict, `license_tables.csv`, `docs/licenses.md`) and `docs/redivis/release-v1/` (the table's rows).
- On the data machine only: `runs/c113/s2397/`, `warehouse/raw/hagstofa_energy/`, `warehouse/output/hagstofa_iceland_power_annual.csv`.
