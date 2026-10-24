# Session 2236 report: a third source of the session's own choosing (Sweden's electricity supply, SCB)

24 October 2026, from 02:58 UTC, on lab-desktop (the data machine), chain 099, unattended. Model spend USD 0. Pulls: 9 requests of 20 (7 by the probe, the metadata and the data by the trial; the write ran offline).

## Read these first

- **Why this source:** with Norway (session 2227), Germany (2230) and the Netherlands (2231), Sweden completes the operator and statistics office data of northern Europe's coupled grids. The ERW did not hold it, and no chain plans it (chains 097, 098 and 101 checked).
- **SCB's old API closed the connection without an answer** (api.scb.se, v1). Its newer PxWebApi v2 (statistikdatabasen.scb.se, which has no robots file) answered. Its search found TAB1011, Electricity supply in Sweden by type of production, monthly 1974M01 to 2026M08, the Swedish Energy Agency's statistics.
- **A new table, `scb_sweden_electricity_monthly`** (series, 6,059 rows, `power`): Sweden's net electricity supply a month from January 1974 to August 2026, across 11 lines:
  - hydro, wind, nuclear, solar;
  - conventional thermal power and its kinds (industrial and district heating back pressure, condensation, gas turbines);
  - imports, and the sum of supply.

  The values are in MWh (the table's GWh times 1,000). SCB's note is in the header: imports include transit through Sweden, and loop flow is excluded. Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set, its release rows added.
- **The license:** CC0, SCB's Open data API page: "We use the licence CC0 for this data". SCB asks that statistics with another agency as their source name it, and the header names the Swedish Energy Agency. **The verdict is added here** (Statistics Sweden, read 403: may be public), so the table is not left unsettled until the next round.
- **`tests/test_session205.py`'s bound raised by 40** for this chain's reads.
- **Cross-check against Eurostat** (`eurostat_electricity_monthly`, Sweden), full years 2016 to 2025:
  - SCB's supply less its imports equals Eurostat's net production within 0.6 percent every year;
  - its imports equal Eurostat's to 0.1 percent;
  - hydro and nuclear within 0.5 percent.
  - The sum of supply runs from 165.8 TWh (2016) to 177.3 (2021) and 173.1 (2025).

## Requests (9 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | api.scb.se/robots.txt | 404 |
| 2 | the v1 API's EN0108 listing | the connection closed, no answer |
| 3 | statistikdatabasen.scb.se/robots.txt | 404 |
| 4 | the v2 table search ("electricity") | 200: TAB1011 among 40 |
| 5 | TAB1011's metadata | 200: 11 lines, 632 months |
| 6 | www.scb.se/robots.txt | 200: no Disallow rule |
| 7 | SCB's Open data API page | 200: CC0 |
| 8, 9 | the metadata and the data (the trial) | 200 |

Reads recorded: 399 to 403.

## Decisions made without you

- **The v2 API in place of v1,** after v1's connection closed.
- **SCB's verdict in this session,** after the round (session 2229) had run.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/scb_electricity.py`, `tests/test_session2236.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record (`license_verdicts.csv` with SCB's row), `tests/test_session205.py`.
- On the data machine only: `runs/c099/s2236/`, `warehouse/raw/scb_electricity/`, `warehouse/output/scb_sweden_electricity_monthly.csv`.
