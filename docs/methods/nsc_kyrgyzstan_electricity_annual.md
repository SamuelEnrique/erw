# Kyrgyzstan's electricity a year from the National Statistical Committee: generation by kind of station (1992 to 2025) and the electricity balance (1990 to 2025), produced, imports, consumption by branch, network losses and exports

Energy Research Warehouse (ERW), method note written in session 2471 (chain 119) for a table first written on 24 October 2026 (session 2462 of chain 119, `archive/sessions/SESSION_2462_REPORT.md`). The license verdict is chain 117's (read 797, session 2436's read, verdict recorded in session 2439), recorded for this table in session 2467's round (`archive/sessions/SESSION_2467_REPORT.md`). Ember's yearly demand for Kyrgyzstan, against which session 2462 compared it, is in `owid_ember_electricity_annual` (entity `owid_energy:KGZ`).

Tables: `nsc_kyrgyzstan_electricity_annual`

## Publisher and address

National Statistical Committee of the Kyrgyz Republic, two dynamic tables of the manufacturing section (`https://www.stat.gov.kg/en/statistics/promyshlennost/`), each an Excel file asked by GET without a key:

- `https://www.stat.gov.kg/en/statistics/download/dynamic/344/`: 1.05.01.03, "Production of electric power on power-stations";
- `https://www.stat.gov.kg/en/statistics/download/dynamic/1248/`: 1.05.01.02, "Electro-balance of the economy".

Each file has two sheets: the old classification (sheet `1.05.01.03`, 1992 to 2013; sheet `1.05.01.02`, 1990 to 2013) and GKED-3 (the sheets named with "(ГКЭД-3)", 2011 to 2025). The English labels are in the third column and the years on row 5. The committee's footnotes are in its Kyrgyz and Russian columns.

Source id `nsc_kg:dynamic_tables` (`sources.csv`: license public, first and last seen 2026-10-24).

Saved files, in `warehouse/raw/nsc_kyrgyzstan/20261024T124819Z_probe/`, fetched by session 2462's probe, not by the connector, each HTTP 200, `application/vnd.ms-excel`, with no Last-Modified:

| Table | Bytes | sha256 | Retrieved (UTC) |
|---|---|---|---|
| 1.05.01.03 (344) | 78,336 | `d0013496...` | 2026-10-24T12:49:01Z |
| 1.05.01.02 (1248) | 88,064 | `81e4776b...` | 2026-10-24T12:49:06Z |

The probe folder's `manifest.csv` holds the two rows; the hashes recomputed in session 2471 agree. The connector's run folders (`20261024T125225Z`, an empty manifest, and `20261024T125233Z`) hold only the data-lock check, so its runs were offline. Session 2462 made 6 requests of 15, all to www.stat.gov.kg (`runs/c119/s2462/probe.csv`): the robots address (HTTP 404, answered at `/kg/robots.txt/`: no robots file), the English home page, the open data page, the manufacturing section and the two files. These are reads 810 to 813 in `docs/licenses.md`; the two data files are not counted there.

Connector: `warehouse/connectors/nsc_kyrgyzstan.py` (session 2462), `[--offline] [--out-dir DIR]`.
- **Ceiling:** two requests, 2 seconds apart; saved files reused with `--offline`. A paused `nsc_kg` or host www.stat.gov.kg is never asked.
- **Joined sheets:** the old sheet gives the years before 2011 and GKED-3 the years from 2011; the overlap (2011 to 2013) must agree within 0.15 million kWh or the run stops.
- **Values:** the committee's million kWh times 1,000, written as MWh rounded to 0.001. A "-" has no row. A footnote mark in a cell ("4293,5 2", manufacturing 2007) is read as the number before it.
- **Checks a year,** within 0.15 million kWh, or 1.05 when every figure of the check is a whole number: hydro, thermal and other add to generation; the branches and the network losses add to consumption; produced and imports equal consumption and exports. A failed check is kept as published and named in header line 3; more than six stop the run.
- **Stops also:** a sheet header not the committee's ("Items"), a label not in the map, a label twice, a year that does not read, a value not a number, or a key given twice.

## Schedule and records

Schedule: none. No shell script under `warehouse/`, no workflow in `.github/workflows/`, no file in `scripts/` and not `warehouse/scheduled.py` names it.

Records:
- `runs/status/nsc_kyrgyzstan.json` (main checkout): run `20261024T125233Z`, ok, "478 rows". `run_status.csv`: no row.
- `archive_manifest.csv`: 478 rows, run `20261024T125238Z-local`, `data_sha256` `8eec471e...` (not recomputed here).
- `coverage.csv`: iso `nsc`, 1 node, P1Y, 1990-01-01 to 2025-01-01, 478 rows, last run 2026-10-24T12:52:33Z, validator pass, license public, sector power, tier source.
- Live set: listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded.
- Release: held (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`; `docs/redivis/release-v1/tables.csv`, "held: not yet on Redivis ... after the storage is settled").
- Package: `package/src/erw/data/tables.csv` has its row (public) since session 2473; `site/data/table_citations.json` and `table_verdicts.json` each name it.
- `license_tables.csv`: National Statistical Committee of the Kyrgyz Republic, "the source registry".

Readers: none. `tests/test_session2462.py` (4 tests) tests the reader on sheets built in the test.

License: the open data page (read 812) publishes the committee's open data under Creative Commons Attribution-NonCommercial-ShareAlike 4.0, "Based on data from the official website of the NSC KR www.stat.kg". `license_verdicts.csv` (read 797): "may be public", "needs written permission" if the ERW sells anything. `docs/licenses.md`, the table's row: verdict "may be public", flag public, "agrees", if it sells "needs written permission". Header line 9 carries the citation.

## Vintage and revision

One write, run `20261024T125233Z`, offline from the saved files; header line 10: "This run wrote 478 rows: 478 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs." `retrieved_at` is the file's fetch: 2026-10-24T12:49:01Z in the 103 rows from 1.05.01.03, 12:49:06Z in the 375 from 1.05.01.02; `source_url` is the file each row comes from. `vintage` is blank in every row: the files carry no Last-Modified.

The committee's later years come with a later online run; a revised figure replaces the old one by (entity, variable, ts_utc); no earlier version is kept.

## Shape and variables

Series, 478 rows, 13 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`), 10 header lines. `entity` `nsc_kg:KG` in every row; `node` Kyrgyzstan; `geo` KG; `unit` MWh; `freq` P1Y; `ts_utc` the year's 1 January, 1990 to 2025; `market` blank.

- **Variables, 16:**
  - from 1.05.01.03: `generation` (34 rows, 1992 to 2025), `generation_hydro` (34), `generation_thermal` (34), `generation_other` (1: 2025, 17,100 MWh);
  - from 1.05.01.02: `produced` (36, 1990 to 2025), `imports` (34: no row in 2009 and 2012, where the sheets print "-"), `consumption` (36), `consumption_manufacturing` (36), `consumption_agriculture` (36), `consumption_transport` (36), `consumption_construction` (36), `consumption_public_utilities` (17, 1990 to 2006: the sheet prints "-" from 2007), `consumption_social_services` (21, 1990 to 2010, the old classification), `consumption_other_activities` (15, 2011 to 2025, GKED-3), `network_losses` (36), `exports` (36).
- **Values:** no blank, no zero, no negative. 55 rows carry a fraction of a MWh (the committee's figures to 0.0001 million kWh in some recent years, for example consumption 2022, 16,138,924.609 MWh).
- **The largest value** is consumption in 2025, 19,116,300 MWh.

Selected years, GWh (the committee's million kWh as written):

| Year | Produced | Generation | Hydro | Thermal | Imports | Exports | Consumption | Network losses | Manufacturing |
|---|---|---|---|---|---|---|---|---|---|
| 1990 | 13,369.7 | | | | 3,220.2 | 7,198.0 | 9,391.9 | 1,035.4 | 3,647.3 |
| 1995 | 12,349.0 | 12,349.0 | 11,118.0 | 1,231.0 | 6,987.0 | 8,355.0 | 10,981.0 | 3,457.0 | 1,778.0 |
| 2000 | 14,931.0 | 14,931.0 | 13,682.0 | 1,249.0 | 6,395.0 | 9,409.0 | 11,918.0 | 3,839.0 | 1,398.0 |
| 2005 | 14,891.3 | 14,891.2 | 13,980.4 | 910.8 | 0.2 | 2,661.5 | 12,230.0 | 4,973.0 | 1,493.0 |
| 2010 | 12,062.9 | 12,062.7 | 11,254.6 | 808.1 | 76.3 | 1,635.4 | 10,503.8 | 3,026.4 | 4,152.1 |
| 2015 | 13,016.6 | 13,016.6 | 11,092.7 | 1,923.9 | 745.8 | 182.2 | 13,580.2 | 2,431.8 | 5,705.7 |
| 2020 | 15,404.2 | 15,404.2 | 13,979.1 | 1,425.1 | 352.6 | 300.1 | 15,456.7 | 2,414.9 | 7,061.8 |
| 2021 | 15,138.0 | 15,138.0 | 12,957.1 | 2,180.9 | 1,682.8 | 546.2 | 16,274.6 | 2,427.6 | 7,940.6 |
| 2022 | 13,882.5 | 13,882.5 | 11,928.6 | 1,953.9 | 2,806.4 | 550.0 | 16,138.9 | 2,388.5 | 7,971.3 |
| 2023 | 13,839.3 | 13,839.3 | 12,030.6 | 1,808.7 | 3,488.8 | 138.4 | 17,189.7 | 2,538.3 | 8,607.0 |
| 2024 | 14,736.1 | 14,736.1 | 12,935.8 | 1,800.3 | 3,841.5 | 158.2 | 18,419.5 | 2,762.3 | 8,421.2 |
| 2025 | 15,420.1 | 15,420.1 | 13,370.2 | 2,032.8 | 3,998.6 | 302.3 | 19,116.3 | 2,758.7 | 8,637.1 |

**The committee's footnotes,** carried into header line 3:
- **Imports** are "actually including flows": transit is inside `imports`; the files give no transit line, and whether it is also inside `exports` is not stated in the footnotes read.
- **Manufacturing** includes, from 2007, the electricity distributed for communal and household needs and to the population. So `consumption_manufacturing` jumps from 1,881.0 GWh (2006) to 4,293.5 (2007), `consumption_public_utilities` ends in 2006, and households' supply has no line of its own from 2007.

## Checks

Counted in session 2471 from the table in the main checkout (`C:\Users\Shared\Documents\erw\warehouse\output`), read past its 10 header lines with `keep_default_na=False`, and from the saved files, by scripts outside the repository. No request was made.

- 478 rows, 1990 to 2025, as header line 10 states; no (entity, variable, ts_utc) twice; no blank value.
- **The kinds add to generation** (hydro + thermal + other, 34 years): equal in 33; in 2019 the kinds are 0.021 GWh under (15,115.179 against 15,115.2).
- **The branches and the network losses add to consumption** (36 years): equal in 33; 0.1 GWh under in 2006, 2008 and 2018.
- **Produced and imports equal consumption and exports** (36 years):
  - equal in 27;
  - 1.0 GWh under in each of 1997, 1998, 1999 and 2000, whole-number years held by the 1.05 allowance;
  - within 0.15 in 2008 (0.1 under), 2020 (0.033 under), 2023 (0.004 over) and 2025 (0.1 over);
  - **one failure, 2001:** 20,029.0 against 19,974.0 GWh, produced and imports 55.0 over, as header line 3 and the report state. Kept as published.
- **Whole-number years:** the balance's four figures are all whole numbers in 1991 to 2002, not 1990 (its figures carry one decimal, produced 13,369.7), so 1990 was held to 0.15 (it agrees exactly). The docstring and the report said "1990 to 2002" (corrected, below); the rule in the code is per year and per check, and the outcome is the same.
- **Produced against generation:** they differ in six years, not three: 2003 (produced 0.2 GWh over), 2004 (0.3 under), 2005 (0.1 over), 2010 (0.2 over), 2023 (0.011 over) and 2024 (0.030 over). The docstring, header line 3 and the report named three years, "up to 0.3 million kWh" (2003, 2004, 2010); the bound holds, the count did not (corrected, below). Both lines are kept as published.
- **The two sheets' overlap,** 2011 to 2013: the run would have stopped had they differed by more than 0.15; it did not stop.
- **Against Ember** (`owid_ember_electricity_annual`, `owid_energy:KGZ`, `electricity_demand`): consumption over Ember's demand is 1.008 (2015), 1.002 (2016), 1.006 (2017), 1.021 (2018), 1.010 (2019), 1.000 (2020), 1.000 (2021), 0.998 (2022), 1.014 (2023), 0.957 (2024) and 0.990 (2025). The report's range, 0.957 (2024) to 1.021 (2018) over 2015 to 2024, holds.
- **The license record elsewhere:** `license_verdicts.csv`'s row for the committee (read 797) still ends "The ERW holds no table of it.", written before this table; observed, not changed.

## Acted on in session 2471

- **The count of years corrected:**
  - The connector's docstring and header line 3 now name the six years where produced and generation differ (2003, 2004, 2005, 2010, 2023 and 2024) and give the whole-number years as 1991 to 2002 (commit `573bae84`).
  - The table was written again offline from the same saved files, its metadata rows replaced by key (commit `83d7fc39`, archive run `20261024T140124Z-local`).
  - Its 478 rows and their `data_sha256` (`8eec471e...`) are unchanged; only the header changed.
  - `SESSION_2462_REPORT.md` carries a correction saying so.
- **The Stanford Redivis draft** (`erw:b9wm`) holds the table from session 2471's upload (13:45:07 UTC, `redivis_uploads_stanford.csv`). That upload was made before the header was corrected, so the draft's `erw_headers` table still holds the old line 3 until the next draft upload. The data are the same.
- **`license_verdicts.csv`:** not changed. A verdict's text is a license round's to write.

## What it cannot say

- **Transit:** inside imports by the committee's footnote, with no line of its own; net imports are not the country's own trade.
- **Households from 2007:** inside manufacturing; the split is not published in these files.
- **Generation before 1992, and "other" stations before 2025:** not in table 1.05.01.03.
- **Months, prices, capacity and plant by plant:** not in these tables.
- **Which figure is wrong** in 2001's balance: the table keeps the committee's figures as published.
- **Earlier versions of a revised year.**
