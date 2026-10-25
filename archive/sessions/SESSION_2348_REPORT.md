# Session 2348 report: a third source of the session's own choosing (Denmark's monthly electricity supply, the Danish Energy Agency)

24 October 2026, from 08:21 UTC to 08:27 UTC, on lab-desktop (the data machine), chain 109, unattended. Model spend USD 0. Pulls: 7 requests of 20 (6 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Statistics Denmark first.** StatBank's API has no robots file (read 596), and its table list (2,310 tables, one request) holds no monthly electricity table: only prices and annual energy accounts.
- **The Danish Energy Agency in its place.** Energinet's hourly data are held (`energinet_*`), but the agency's monthly statistics add trade by country and domestic supply with losses. ens.dk's robots file allows `Claude-User` by name and every reader but Drupal's own paths (read 597).
- **A new table, `ens_denmark_electricity_monthly`** (series, 27,777 rows, `power`), from the agency's monthly electricity workbook (`/media/8572/download`, an .xls), January 2000 to August 2026, for Denmark and its West and East areas. Each holds 35 columns:
  - gross and net production and their kinds;
  - net exchange;
  - imports, exports and net exports, in all and with Sweden, Norway, Germany, the Netherlands and England;
  - domestic supply with and without losses, and both kinds of loss.

  On the area sheets, columns 13 and 14 are the flows between West and East. The values are in MWh (GWh times 1,000). Only the workbook's monthly block is taken. Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set.
- **The license is not read.** The statistics page states no licence or terms (read 598), and no terms page was found within this session. The table is `internal` until a read settles it. The workbook names Energinet as the source of most of its data.
- **Cross-checks:**
  - **Within the table**, in every month:
    - gross production less own use equals net production within 0.001 MWh;
    - net production plus imports less exports equals domestic supply within 9 MWh;
    - West and East sum to the nation's net production, wind and solar exactly.
  - **Against `eurostat_electricity_monthly` (Denmark), 2016 to 2025:**
    - wind 0.999 to 1.002;
    - imports and exports 1.000 in six of the ten years (exports 0.923 in 2020, the widest);
    - net production 0.999 to 1.031.

## Requests (7 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | api.statbank.dk/robots.txt | 404 |
| 2 | StatBank's table list | 200: 2,310 tables, no monthly electricity |
| 3 | ens.dk/robots.txt | 200: Claude-User allowed by name |
| 4 | a guessed statistics page | 404 |
| 5 | the analyses and statistics index | 200 |
| 6 | the annual and monthly statistics page | 200: the monthly workbooks, no licence stated |
| 7 | the monthly electricity workbook (the fetch) | 200 |

Reads recorded: 596 to 598.

## Decisions made without you

- **`internal` until the agency's terms are read.**
- **The area sheets' columns 13 and 14 named as the flows between the areas,** from their own labels.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/ens_denmark_electricity.py`, `tests/test_session2348.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, the license record (reads 596 to 598).
- On the data machine only: `runs/c109/s2348/`, `warehouse/raw/ens_electricity/`, `warehouse/output/ens_denmark_electricity_monthly.csv`.
