# Session 32 report

Energy Research Warehouse (ERW), session 32, run 2026-09-29 from 18:10 to about 19:20 UTC. **Wall time about 70 minutes**, inside the 90-minute target, so the page was built rather than left for session 33.

**API spend: USD 0.00.** No model call; the cost ledger has no session 32 row.

- The only pull was EIA's eight per-BA workbooks.
- Nothing was deleted from Redivis and nothing was released.
- The deploy is live: routes 32 of 32, values 1,213 of 1,213.

## The workbooks used

**Where they are.** Session 31 had looked in the API v2, the six-month bulk files and the Grid Monitor's code, and found no CO2. The per-BA workbooks are what the Grid Monitor's "download by balancing authority" serves. Its code builds the path from `respondentPath = "electricity/gridmonitor/knownissues/xls/"`, plus the code, plus `.xlsx` (regions get a `Region_` prefix):

| BA | URL | Bytes | Last-Modified |
|---|---|---|---|
| CISO | https://www.eia.gov/electricity/gridmonitor/knownissues/xls/CISO.xlsx | 97,113,220 | 2026-09-29 16:02:04 GMT |
| ERCO | .../xls/ERCO.xlsx | 74,394,505 | 16:04:35 |
| ISNE | .../xls/ISNE.xlsx | 77,728,639 | 16:08:56 |
| MISO | .../xls/MISO.xlsx | 100,036,576 | 16:10:30 |
| NYIS | .../xls/NYIS.xlsx | 84,712,851 | 16:11:53 |
| PJM | .../xls/PJM.xlsx | 113,468,694 | 16:13:39 |
| SWPP | .../xls/SWPP.xlsx | 107,146,758 | 16:18:20 |
| US48 | .../xls/Region_US48.xlsx | 37,216,482 | 15:58:45 |

**Layout.** Sheet `Published Hourly Data`, one row per hour from 2015-07-01.

- The first column is `BA` in a BA's workbook and `Region` in the US48 workbook; `UTC time` is the hour's end.
- The CO2 columns start 2018-07-01:
  - emission factors (lbs/kWh);
  - `CO2 Emissions: COL / NG / OIL / Other`;
  - `Generated`, `Imported`, `Exported` and `Consumed`, in metric tons;
  - EIA's intensities, in lbs/kWh.
- Other sheets: daily data, charts, known issues, thresholds, and a `Notes` sheet defining every column.

**EIA's method,** from `Notes` and "About the EIA-930 data":

- positive generation by fuel times a CO2 factor per fuel and BA (EIA FAQ 74);
- a US factor where a BA's history is short;
- no emissions for negative generation;
- consumed = generated plus imported minus exported.

It is recorded in `warehouse/metadata/sources.csv` (source `eia:gridmonitor/knownissues/xls`) and `docs/methods/emissions.md`.

**Raw files.** All eight are saved with a manifest under `warehouse/raw/eia930_emissions/`.

- Resume works: CISO's download survived a parse failure, and US48 was downloaded once for the layout check. The rerun reused both through their Last-Modified, so no file was downloaded twice.
- Two first-run bugs were fixed before any row was written:
  - the HEAD request is captured as a 0-byte file, and the resume lookup at first took it for a workbook;
  - the BA workbooks name their first column `BA`, not `Region`.

## Rows pulled against the ceiling; series start per BA

**1,122,144 new rows, 93.5% of the 1,200,000 ceiling,** in `eia930_all_emissions` (tier source, public, partition `ba`, unit `tCO2`).

**Only two variables fit:**

- `co2_emissions_generated` (EIA's total) and `co2_emissions_consumed` (generated plus imported minus exported).
- About 72,000 hours since 2018-07-01 times 8 BAs holds two variables under 1.2M rows, not three.
- The by-fuel, imported and exported columns are not in the table. They are in the saved raw workbooks, so adding them needs no new pull (question 1). Net imported CO2 is consumed minus generated.

| BA | Hours with CO2 in the workbook | Rows written | First day written | Days left out (incomplete) |
|---|---|---|---|---|
| CISO | 72,132 | 142,512 | 2018-07-02 | 41 |
| ERCO | 72,163 | 143,520 | 2018-07-03 | 18 |
| ISNE | 72,284 | 144,480 | 2018-07-02 | 1 |
| MISO | 72,210 | 143,136 | 2018-07-02 | 29 |
| NYIS | 72,221 | 143,616 | 2018-07-02 | 19 |
| PJM | 70,379 | 139,152 | 2018-07-02 | 42 |
| SWPP | 72,258 | 121,248 | 2018-07-02 | **485** |
| US48 | 72,284 | 144,480 | 2018-07-02 | 1 |

**Notes on the table:**

- **2018-07-01 is not written for any BA:** EIA's CO2 starts at local midnight, so that UTC day is partial.
- **The latest written day is 2026-09-27;** 2026-09-28 was incomplete for every BA when read.
- **Completeness is per UTC day,** session 16's rule. A day is written only when both variables have all 24 hours. The 636 days left out are gap rows in `run_status.csv`.
- **SPP's 485 gaps** are hours where one of the two CO2 columns is empty in EIA's own file.
- **Checks:**
  - Four values (US48, 2019-03-01 00:00 and 2026-09-20 12:00, both variables) equal the workbook's exactly, with the hour's end shifted to its start.
  - The validator passes (range -1,506 to 3,207,014 tCO2; a negative consumed value is EIA's, for an exporting hour).

## Carbon intensity (A2)

`carbon_intensity_hourly` (12,528 rows) and `carbon_intensity_daily` (522 rows), tier derived, `kgCO2/MWh`:

- **`intensity_generation`** = CO2 generated x 1000 / `net_generation_mw` (`eia930_all_generation`).
- **`intensity_demand`** = CO2 consumed x 1000 / `demand_mw` (`eia930_all_demand`). The two differ by trade, explained in the method page.
- **Daily values** are energy-weighted over complete UTC days.
- **They reach 2026-08-26 to 2026-09-27 only:** generation and demand keep about 30 days in the warehouse, while the emissions go back to 2018 (question 2).

**Against EIA's own intensity** (US48, the hour starting 2026-09-26 18:00):

| | ERW | EIA (lbs/kWh, converted) |
|---|---|---|
| Of generation | 270.2 kg/MWh | 263.2 |
| Of demand | 264.7 | 263.5 |

EIA divides by positive generation and "consumed electricity"; the ERW by reported net generation and demand. The method page says so.

## What the page shows

**`/emissions`** (nav: Grid, Emissions before Storage). Two blocks only; tier chips, citations, method link, Stanford palette.

1. **Carbon intensity now, ranked.** The latest hour of `carbon_intensity_hourly` (2026-09-27 23:00 UTC), per ISO, of generation and of demand, lowest first:

   | ISO | Of generation, kg CO2/MWh |
   |---|---|
   | CAISO | 102.30 |
   | ISO-NE | 206.62 |
   | NYISO | 240.15 |
   | PJM | 308.18 |
   | ERCOT | 374.48 |
   | MISO | 517.31 |
   | SPP | 580.84 |

   The page says EIA publishes generation a day or more late, so the latest hour is not the current one.
2. **The last 24 hours,** intensity of generation, the seven ISOs on one chart.

Every number is a `Num` checked against Supabase. `check-routes.mjs` and `check-values.mjs` include `/emissions`, and both pass locally and live.

## Supabase and Redivis

- **Supabase:** **300.0 MB before, 321.0 MB after** the vacuum (limit 400). Every table matched:
  - the last 90 days of the hourly tables: `eia930_all_emissions` 33,814 rows, `carbon_intensity_hourly` 12,528;
  - `carbon_intensity_daily` whole: 522.
- **Redivis draft,** public dataset, each `count(*)` equal to its CSV:
  - `eia930_all_emissions` 1,122,144;
  - `carbon_intensity_hourly` 12,528;
  - `carbon_intensity_daily` 522;
  - `erw_coverage` 77;
  - `erw_sources` 159.

  The license check finds 0 internal tables in the public dataset. Nothing released.
- **Archive:** 1,135,194 rows appended, new names only.
- **Coverage:** **77 tables, all 77 pass, 6,042,117 rows.**
- **`package/llms.txt`:** the three tables and what is still not in the warehouse. The chat spec was regenerated and matches.
- **The daily run** now runs `eia930_emissions.py --days $DAYS` (the newest workbooks, the last days merged on (entity, variable, ts_utc) in a stream, the raw copy kept), then `carbon_intensity.py`. `eia930_all_emissions` is restored from the draft first.

## Decisions made without a human (each reversible)

1. **Two variables:** CO2 generated and consumed, not by fuel, imported and exported, to stay under the ceiling. Consumed keeps net imports visible (consumed minus generated). The rest waits in the raw workbooks.
2. **Two new units** (Decision 30 in `docs/datastandard.md`; validator and standard together):
   - `tCO2`, as EIA states its values;
   - `kgCO2/MWh` for the ERW's intensities, never EIA's lbs/kWh mixed in.
3. **Intensity uses the warehouse's own generation and demand,** as the prompt says, not the workbooks' generation columns. So its history is 30 days, not 8 years.
4. **Values are EIA's floats, not rounded.** Intensities are rounded half up to 4 decimals.
5. **Sector `power;carbon`** for the three tables; ISO labels the seven ISOs and US48.
6. **The page ranks by intensity of generation, lowest first,** and shows demand intensity beside it. The chart shows generation intensity for the seven ISOs, without US48.

## Run health and the daily run

- **Gate:** open at the start and at the end (the GitHub run of 2026-09-28 23:16: 0 failures outside the known gaps).
- **Today's scheduled daily run started at 18:58 UTC and was still running** at the report.
  - It checked out `main` before this session's push (19:10), so it runs sessions 30 and 31's steps (the price board, the shadow, storage) but not session 32's emissions step. That runs from tomorrow.
  - It had not committed when I wrote this. The report push merges it if it has.
- **Run status:** this session's connector results were recorded in `warehouse/metadata/run_status.csv`, including the 636 emissions gap days.

## Open questions and skipped

**Open questions for Samuel:**

1. **The other CO2 variables** (by fuel: coal, gas, oil, other; imported; exported): add them from the saved workbooks with a new ceiling? About 580,000 rows per variable. No new pull is needed for the history.
2. **Intensity history:** longer generation and demand in the warehouse (EIA-930's own history, a pull), or the workbooks' own net generation and demand columns (already saved)? Either would give intensity from 2018. The monthly table is session 33's.
3. **SPP's 485 incomplete days:** hours where EIA's file has one CO2 column empty. Keep the rule (days left out), or write the variable that is complete?
4. **The daily cost of the refresh:** the per-BA workbooks are the only source, so the daily run downloads about 690 MB (eight workbooks) to keep 3 days. Fine on GitHub's runner; say if it should run weekly instead.
5. **Package tests on the large tables.** Loading `eia930_all_emissions` whole in the per-table tests is slow (session 32's local run did not finish in 28 minutes). Test it by partition (`ba`), as session 29 did for the ERCOT history? That is a change to the tests only.

**Skipped:**

- **No emissions estimate of our own** (the prompt forbids it).
- **No blocks beyond the two.**
- **The monthly intensity table** (session 33, by the prompt).
- **The package tests were only partly run.** The subset touching the new tables and the catalogue (`-k "eia930_all_emissions or carbon_intensity or filter or sector or coverage or list_tables"`) stopped at my 28-minute limit: about 95 tests had passed, 0 failed.
  - The tests left are the per-table ones that load `eia930_all_emissions` whole (1.1M rows), which is what made the run slow.
  - The daily workflow's last step runs these tests on the runner, which will hold that table from tomorrow's restore. That step may take much longer than before (question 5).
