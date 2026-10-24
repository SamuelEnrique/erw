# Session 2391 report: a source of the session's own choosing (Austria's monthly electricity statistics, E-Control), internal

24 October 2026, from 09:26 UTC to 09:32 UTC, on lab-desktop (the data machine), chain 113, unattended. Model spend USD 0. Pulls: 9 requests of 20 (8 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Why this source:** session 2272's Energy-Charts table gives Austria's public net production by the hour. E-Control's monthly statistics add gross generation for all producers, imports and exports by neighbour, consumption, losses and pumping. No ERW table held them. Both agents beside this chain were told.
- **data.gv.at first:** no robots file (read 643). Its old CKAN API is gone (404), its new search finds no E-Control statistics data set, and the "Betriebsstatistik" search gives 0.
- **E-Control's own site:** its robots file closes its services, login and `/home` paths only (read 644). Its download area offers five CSV files of time series; the monthly one is `el_dataset_mn.csv`.
- **A new table, `econtrol_austria_electricity_monthly`** (series, 12,472 rows, `power`): 63 series, January 2010 to August 2026, in MWh.
  - The series: gross generation and its kinds (hydro by type and size, combustibles by fuel, wind, solar, geothermal), own use, pumping, imports and exports in all and with Switzerland, Czechia, Germany, Hungary, Italy, Liechtenstein and Slovenia, inland and gross consumption, losses, final consumption, and the public grid's series.
  - Each keeps E-Control's TS_ID, breakdown, scope and category.
  - Not taken: the generation coefficient (unit "[1]") and two series in kW, counted. Two series the file gives twice (exports and imports, identical columns) are kept once.
  - The file is in Windows-1252, and the connector reads it as such.
  - Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set.
- **The license is not settled.** The impressum carries "Copyright 2026 © E-Control" and grants no reuse (read 645). The table is `internal`.
- **Cross-checks against `eurostat_electricity_monthly` (Austria), 2016 to 2025:**
  - imports and exports 1.000 (1.001 in 2016);
  - wind 1.008 to 1.032;
  - gross generation 1.024 to 1.070 times Eurostat's net production;
  - inland consumption 0.943 to 0.988 of Ember's demand (`owid_ember_electricity_annual`).
  - Within the table, hydro, combustibles and wind, solar and geothermal sum to gross generation within 27.5 GWh a month; E-Control lists a statistical difference series beside them.

## Requests (9 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.data.gv.at/robots.txt | the portal's page, no robots file |
| 2 | data.gv.at's old CKAN search | 404 |
| 3, 4 | data.gv.at's search: E-Control, Betriebsstatistik | 200: no statistics data set |
| 5 | www.e-control.at/robots.txt | 200: services, login and /home closed |
| 6 | a guessed statistics address | 404, the site's menu |
| 7 | E-Control's electricity download area | 200: five CSV files |
| 8 | E-Control's impressum | 200: copyright, no reuse statement |
| 9 | the monthly CSV (the fetch) | 200 |

Reads recorded: 643 to 645.

## Decisions made without you

- **`internal`** under E-Control's copyright notice.
- **A repeated series kept once,** the run stopping if its columns ever differ.

## For Samuel's ruling

- **E-Control's consent,** if Austria's monthly statistics are wanted public.

## Files

- New: `warehouse/connectors/econtrol_austria_electricity.py`, `tests/test_session2391.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, the license record (reads 643 to 645).
- On the data machine only: `runs/c113/s2391/`, `warehouse/raw/econtrol_electricity/`, `warehouse/output/econtrol_austria_electricity_monthly.csv`.
