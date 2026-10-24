# Session 2343 report: a second source of the session's own choosing (Switzerland's electricity balance, the Federal Office of Energy)

24 October 2026, from 07:51 UTC to 07:57 UTC, on lab-desktop (the data machine), chain 109, unattended. Model spend USD 0. Pulls: 8 requests of 20 (7 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Slovakia first, then Croatia, neither taken:**
  - Statistics Slovakia's DATAcube timed out at its robots file (read 555).
  - Croatia's data portal (podaci.dzs.hr) has no robots file (read 556), but it is not a PxWeb database, and a guessed API address answered 404. No more requests were spent guessing.
- **Switzerland's Federal Office of Energy in their place.** Its monthly balance adds what session 2272's hourly Energy-Charts table lacks: imports, exports, pumping, consumption and losses. No ERW table held it. Swissgrid's data need consent (chain 101); this is SFOE's own publication.
- **A new table, `bfe_switzerland_electricity_monthly`** (series, 4,000 rows, `power`): SFOE's "ENSTAT: Elektrizitätsbilanz der Schweiz - Monatswerte-CSV" on opendata.swiss, January 2000 to August 2026. It holds 15 lines:
  - generation by kind: run-of-river, storage hydro, nuclear; "other" until thermal, wind and solar begin;
  - national generation, pumping, net generation, imports, exports, national consumption, losses and final consumption.

  The values are in MWh (the file's GWh times 1,000). The months of 2026 are provisional (`x_final` 0). The vintage is the file's Last-Modified, 7 October 2026. Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set, its release rows added.
- **The license:** opendata.swiss's "Open use. Must provide the source", the term the dataset's resource names (read 558). Commercial use is allowed, and the author, title and link must be given; the header gives them. This session wrote the verdict: **may be public**, sold or not.
- **Cross-checks:**
  - Within the table, exactly (0 MWh) in every month:
    - the kinds sum to national generation;
    - national generation less pumping is net generation;
    - net generation plus imports less exports is national consumption;
    - consumption less losses is final consumption.
  - Against session 2272's `energy_charts_central_europe` (Switzerland, 2023 to 2025): nuclear, solar and run-of-river are 1.000 of SFOE's every year: for these three, Energy-Charts' figures equal SFOE's.
  - National consumption over `owid_ember_electricity_annual`'s demand: 0.956 to 0.967, 2016 to 2025.

## Requests (8 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | data.statistics.sk/robots.txt | connection timed out |
| 2 | podaci.dzs.hr/robots.txt | 404 |
| 3 | a guessed PxWeb address at DZS | 404 |
| 4 | opendata.swiss/robots.txt | the portal's 404 page |
| 5 | opendata.swiss's catalogue search | 200: three SFOE data sets |
| 6 | opendata.swiss's terms of use | 200: the four terms |
| 7 | www.bfe-ogd.ch/robots.txt | 404 |
| 8 | the monthly CSV (the fetch) | 200 |

Reads recorded: 555 to 559.

## Decisions made without you

- **English variable names from SFOE's German columns,** each German name kept as `node`.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/bfe_switzerland_electricity.py`, `tests/test_session2343.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record (reads 555 to 559, one verdict).
- On the data machine only: `runs/c109/s2343/`, `warehouse/raw/bfe_electricity/`, `warehouse/output/bfe_switzerland_electricity_monthly.csv`.
