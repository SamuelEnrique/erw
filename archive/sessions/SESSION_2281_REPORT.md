# Session 2281 report: Italy's production by type and load (Energy-Charts; Terna's terms close Terna's own data)

24 October 2026, from 04:57 UTC, on lab-desktop (the data machine), the second session of `queue/done/104-day-7-november-data-portugal-italy-japan-argentina.md`, unattended. Model spend USD 0. Pulls: 12 requests of 15 (below).

## Read these first

- **Terna's own data are not taken.**
  - Its robots file disallows `/Portals/` and other site paths, allowing its download API (read 488).
  - **Its legal notice** (read 490) gives a new verdict, needs written permission in both columns: "The reproduction of documents published on these websites is authorised exclusively for personal and non-commercial use, provided that the source is cited correctly."
- **Energy-Charts in its place,** as chain 104's file allows and chain 103's agent suggested (chain 102 holds Hungary, Romania, Greece and Bulgaria, chain 103 Austria, Switzerland and the Czech Republic, so Italy overlaps neither).
  - api.energy-charts.info has no robots file (read 491).
  - The API's description (read 492) states: "Unless stated otherwise, the data provided by the Energy-Charts API is licensed under the CC BY 4.0 license. Proper attribution to Energy-Charts.info as the source is required." It allows 2 requests a minute; the year requests were 31 seconds apart.
  - Chain 102's session 2257 read the same sentence on its branch; the chain landing second keeps one verdict row.
- **One table written, validated, archived, in coverage (sector power), in the release package, both holds:** `energy_charts_italy_power`, 2020 to 22 October 2026, 1,329,375 rows.
  - Twenty production types and load, in MW: fossil gas, coal, oil and coal-derived gas, hydro (run-of-river, reservoir, pumped storage and its consumption), wind, solar, geothermal, biomass, waste, batteries, others, cross-border trading.
  - The API's description gives MW ("the public net electricity production in Megawatt (MW)").
  - Each file's own interval: hourly to 2025, quarter-hourly in 2026.
  - Residual load and the renewable shares, which the API derives, are not taken.
- **The cross-check** (`runs/c104/s2281/cross.py`, `cross.out`):
  - A UTC year's load is a steady 0.876 to 0.890 of Ember's Italian demand from 2020 to 2025 (2025: 277.248 against 311.60 TWh). Public net production and load leave out self-consumption and what the API does not count; the ratio's level is not tested further here.
  - Production, storage and trading less load is a median 169 MW, 0.54% of load.
  - Solar rose from 20.4 TWh in 2020 to 33.9 in 2025.

## The pulls

1. www.terna.it/robots.txt (read 488).
2. Terna's English home page (read 489), for the legal notice's address.
3. The legal notice (read 490).
4. api.energy-charts.info/robots.txt (read 491): HTTP 404.
5. The API's description (read 492).
6. to 12. Italy's public power, a year a request, 2020 to 2026 (to 22 October), 31 seconds apart. They were seeded into the raw store, and the trial and the write read them offline.

## Errors

- None.

## Decisions made without you

- **Energy-Charts in Terna's place,** for the reasons above.
- **Each file's interval kept** (hourly, then quarter-hourly), not averaged.

## For Samuel's ruling

- **Terna's data** need its consent, as Swissgrid's, Eskom's and XM's do.

## Files

- New: `warehouse/connectors/energy_charts_italy.py`, `tests/test_session2281.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (488 to 492), `warehouse/metadata/license_verdicts.csv` (Terna, Energy-Charts)
  - the coverage, sources, archive manifest and license files
  - `docs/redivis/release-v1/`
- On the data machine only: `runs/c104/s2281/`, `runs/license_reads/s2281/`, `runs/s2281_*`, `warehouse/raw/energy_charts_italy/`.
