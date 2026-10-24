# Session 2253 report: Belgium's production and load (Energy-Charts, in place of Elia)

24 October 2026, from 03:44 UTC, on lab-desktop (the data machine), a session of `queue/done/102-day-5-november-data-poland-belgium-new-zealand-columbia.md`. Model spend USD 0.

Pulls: 13 requests of 15:
- opendata.elia.be's robots file;
- APG's robots address (`markttransparenz.apg.at`, sent on to `markt.apg.at`), `markt.apg.at`'s robots file, and `transparency.apg.at`'s robots address (no answer, a connection timeout);
- api.energy-charts.info's robots address (HTTP 404) and its OpenAPI description;
- Belgium's public power for 2020 to 2026, seven requests, 35 seconds apart.

The trial and the write ran offline. Also Supabase, for the locks and the archive.

## Read these first

- **Elia's open data is closed to the ERW's reader.** opendata.elia.be's robots file disallows `/api/` and every download path to every reader but Google (`User-agent: *`, `Disallow: /api/`, `/explore/download`, `/explore/dataset/*/download`), as chain 101 found for `odre.opendatasoft.com`. Elia's data was not asked.
- **Austria's APG was tried next and is closed too:** its market pages carry no data file, and the host of its transparency API (`transparency.apg.at`) does not answer.
- **Belgium's figures come from Energy-Charts instead** (Fraunhofer ISE). Its API publishes each European country's public net production by type, and states its data license: "Unless stated otherwise, the data provided by the Energy-Charts API is licensed under the CC BY 4.0 license. Proper attribution to Energy-Charts.info as the source is required." It allows 2 requests a minute for each client, which the connector keeps (35 seconds apart).
- **One series table, `energy_charts_belgium_hourly`:** 908,600 hourly figures, 1 January 2020 to 23 October 2026 (Belgian days; UTC 23:00 on 31 December 2019 to 21:00 on 23 October 2026), in MW:
  - 13 production types (nuclear, gas, oil, solar, offshore and onshore wind, biomass, waste, run-of-river, pumped storage and its consumption, battery from 2025, others);
  - load, residual load, and cross-border trading as Energy-Charts gives it.
- **Not taken:**
  - Energy-Charts' two renewable shares, which are its own percentages;
  - 2,928 blank nuclear hours in 2026, counted.
- **The cross-check** (`runs/c102/s2253/cross.py`):
  - **Against Eurostat's monthly figures for Belgium** (chain 099's table, 77 months), the medians are: nuclear 1.004, load 1.059 of the supply available for the internal market, wind 0.95, solar 0.98.
  - **Against Ember's yearly demand,** load is 92 to 94 percent (80.2 against 86.6 TWh in 2025).
- **License: internal** until the licenses' round (session 2257) records Energy-Charts' verdict from the license sentence above (read 6 of this session's probe).
- **Registered:** the sector rule (`power`), the live-set hold, the license tables (licenses check: 0 problems). No row is given twice. The test is `tests/test_session2253.py` (4 tests).

## Errors

- **Two requests went to APG's hosts** before they were found closed.

## Decisions made without you

- **Energy-Charts in place of Elia,** as the chain file asks when a source bars the reader. Belgium stays the country, and a publisher that states an open license is the source.
- **The current year asked to the last ended Belgian day** (`--last-day`, yesterday by default).

## For Samuel's ruling

- None new. Elia's robots file is a bar, like the others on the chains' list.

## Files

- New: `warehouse/connectors/energy_charts_belgium.py`, `tests/test_session2253.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c102/s2253/`.
