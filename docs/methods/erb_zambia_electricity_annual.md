# Zambia's electricity a year from the Energy Regulation Board's Statistical Bulletin 2025: generation by power station 2013 to 2025, consumption by economic sector 2015 to 2025, exports and ZESCO's imports 2024 and 2025, installed capacity by technology 2025

Energy Research Warehouse (ERW), method note written in session 2429 (chain 115) for a table first written on 24 October 2026 (session 2420 of chain 115, `archive/sessions/SESSION_2420_REPORT.md`, commit `67ab07a4`). The license verdict is session 2425's (`archive/sessions/SESSION_2425_REPORT.md`). Ember's yearly demand for Zambia, against which session 2420 compared it, is in `owid_ember_electricity_annual` (entity `owid_energy:ZMB`).

Tables: `erb_zambia_electricity_annual`

## Publisher and address

Energy Regulation Board, Zambia (ERB), Statistical Bulletin 2025, listed on `https://www.erb.org.zm/statistics`, one PDF asked by GET without a key:

- `https://www.erb.org.zm/wp-content/uploads/files/statBullet2025.pdf`

Source id `erb_zm:statistical_bulletin` (`sources.csv`: license internal, first and last seen 2026-10-24). The bulletin has 42 pages. The connector reads its tables 12 to 19 and 26 with pdfplumber: the text lines of tables 12 to 15, 17 to 19 and 26, and table 16 (the 14 independent power producers) from pdfplumber's table extraction, whose header must be ERB's exactly. Table 12 (national generation, 2025) is a check only.

Saved bulletin: `warehouse/raw/erb_zambia/20261024T103831Z_probe/probe_05_w_erb_org_zm_wp_content_uploads_files_statbullet2025_pdf.bin`, 1,193,636 bytes, sha256 `03fa6051...`; its manifest records HTTP 200 at 2026-10-24T10:39:35Z and Last-Modified "Fri, 31 Jul 2026 11:40:33 GMT". It was fetched by session 2420's probe (the folder ending `_probe`), not by the connector: the connector's two run folders (`20261024T104525Z`, an empty manifest, and `20261024T104711Z`) hold only the data-lock check (`erw_lock_check`, 4 bytes), so both runs were offline. Session 2420 made 8 requests of its ceiling of 15, all to www.erb.org.zm (the report). www.erb.org.zm's robots file (read 703 in `docs/licenses.md`) disallows only `/wp-admin/` and names no AI agent.

Connector: `warehouse/connectors/erb_zambia.py` (session 2420), `[--offline] [--out-dir DIR]`.
- **Ceiling:** one request; online the bulletin is fetched again (`fresh`), `--offline` reads the saved one. A paused `erb_zm` or host www.erb.org.zm is never asked.
- **Values:** ERB's GWh times 1,000, written as MWh rounded to 0.001; installed capacity in MW as printed.
- **ERB's "-":** no row. A printed "0" is kept.
- **Stops:** a header not ERB's, a station or label not in the map, a value that is not a number, a year twice, a table whose rows do not add to its printed total within 0.1 GWh (0.1 MW), the four groups' 2025 totals not equal to table 12's national total within 0.1, or a key given twice. One gap is allowed: table 17's power traders' total for 2025, which leaves out Africa GreenCo's row (Checks).

## Schedule and records

Schedule: none. No shell script under `warehouse/`, no workflow in `.github/workflows/`, no file in `scripts/` and not `warehouse/scheduled.py` names it.

Records:
- `runs/status/erb_zambia.json` (main checkout): run `20261024T104711Z`, ok, "515 rows". `run_status.csv`: no row.
- `archive_manifest.csv`: 515 rows, run `20261024T104724Z-local`, `data_sha256` `5fe334c2...`, which is the data hash of the file in the main checkout (recomputed in session 2429).
- `coverage.csv`: iso `erb`, 59 nodes, P1Y, 2013-01-01 to 2025-01-01, 515 rows, last run 2026-10-24T10:47:11Z, validator pass, license internal, sector power, tier source.
- Live set: listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded.
- Release: no row in `docs/redivis/release-v1/tables.csv`, `redivis_uploads.csv` or `redivis_uploads_stanford.csv`.
- Package: `package/src/erw/data/tables.csv` has its row since session 2431 (internal, "needs written permission"); `site/data/table_citations.json` and `table_verdicts.json` have none.
- `license_tables.csv`: Energy Regulation Board, Zambia (ERB), "the source registry".

Readers: none. `tests/test_session2420.py` (4 tests) tests the reader on text and a table 16 built in the test.

License: `license_verdicts.csv`, read 705 (session 2420's read of the home page's footer): "Copyright 2026 All Rights Reserved", verdict "needs written permission", the same if the ERW sells anything (session 2425). `docs/licenses.md`, the table's row: verdict "needs written permission", flag internal, "agrees", ERW verdict internal; under "Permission needed", ERB: "Write to: no person or address on the page read." Header line 10 and the docstring said "internal until a ruling" until session 2429 (Checks).

## Vintage and revision

One write, run `20261024T104711Z`, offline from the saved bulletin; header line 11: "This run wrote 515 rows: 515 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs." `retrieved_at` is 2026-10-24T10:39:35Z in every row, the probe's fetch as its manifest records it. `vintage` is 2026-07-31T11:40:33Z in every row, the PDF's Last-Modified.

The address is the 2025 bulletin's, written in the code; a later bulletin is not found by the connector. A later run of the same bulletin replaces rows by (entity, variable, ts_utc); no earlier version is kept. Earlier bulletins (2020 and 2022) were read in session 2420 only to check table 19's 2019 column; their figures for other years are not compared.

## Shape and variables

Series, 515 rows, 15 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_group, x_table`), 11 header lines. `ts_utc` the year's 1 January; `freq` P1Y; `geo` ZM; `market` blank; `x_table` the bulletin's table ("Table 13" and so on).

- **`entity`, 60:** 30 stations (`erb_zm:station:<slug>`: ZESCO's 3 large hydro, 6 mini hydro and 7 diesel plants, and 14 independent power producers), 4 groups (`erb_zm:group:<group>`, each table's printed total), 12 sectors (11 and `total`), 7 exporters (4 power traders, their total, ZESCO and `total`), 1 importer (`erb_zm:importer:zesco`) and 6 technologies (5 and `total`).
- **`node`, 59 values:** the exporter and the importer ZESCO share the node "ZESCO", which is why `coverage.csv` counts 59 nodes for 60 entities.
- **`Itezhi Tezhi (diesel)`** (`erb_zm:station:itezhi_tezhi_diesel`, x_group zesco_diesel) is ZESCO's diesel plant; `erb_zm:station:itezhi_tezhi_power_corporation` (x_group ipp) is the independent hydro plant.

| Variable | Unit | Rows | Entities | Years | Table |
|---|---|---|---|---|---|
| generation | MWh | 381 | 34 | 2013 to 2025 | 13 (52 rows), 14 (81), 15 (53), 16 (195) |
| consumption | MWh | 114 | 12 | 2015 to 2025, not 2019 | 19 |
| exports | MWh | 12 | 7 | 2024, 2025 | 17 |
| imports | MWh | 2 | 1 | 2024, 2025 | 18 |
| capacity | MW | 6 | 6 | 2025 | 26 |

- **Values:** every MWh value is a whole number; the four capacity values with decimals are MW (hydro 3,176.14, solar 307.77, diesel 194.80, total 4,118.71; coal 330, heavy fuel oil 110). No negative value.
- **Zeros, 98 rows,** all station generation: independent producers in the years before they ran (for example Solar century and United Capital Fertiliser 2013 to 2024, Chisamba 2013 to 2024, Kafue Gorge Mini Hydro 2013 to 2024, Dangote and the CEC emergency generators 2013 to 2023, Kafue Gorge Lower 2013 to 2020), and Ndola Energy Corporation in 2022.
- **Stations with fewer than 13 years** (ERB's "-", no row): Chama 2020 to 2023, Itezhi Tezhi (diesel) 2015 and 2016, Kabompo 2013 to 2017, Luangwa 2013 to 2020, Lundazi 2020 to 2023, Shang'ombo 2014 to 2025, Zambezi 2013 to 2017, Lusiwasi Upper 2021 to 2025, Shiwan'gandu 2014 to 2025, Musonda Falls every year but 2016. Every independent producer has 13 rows.
- **Consumption by sector:** 11 rows a year in 2015 to 2018, 2021 and 2022, 12 in 2020 and 2023 to 2025. The difference is `psa`, which ERB prints as "-" in the other years: 52.40 GWh (2020), 729.20 (2023), 844.24 (2024), 935.47 (2025). What ERB's "PSA" stands for is not read here. Mining is the largest sector: 4,650.10 GWh in 2024 and 9,785.37 in 2025.
- **National generation** (the four groups' totals), GWh: 13,289.83 (2013), 14,444.30, 13,425.70, 11,684.30 (2016), 14,457.40, 16,190.46, 15,040.74, 15,497.78, 16,795.45, 19,399.13 (2022), 19,372.93, 13,565.92 (2024), 14,560.23 (2025). Large hydro is 12,780.00 GWh in 2013 and 7,282.57 in 2024.
- **Consumption total**, GWh: 11,449.90 (2015), 10,857.50, 12,192.00, 13,080.10, 11,481.10 (2020), 12,831.30, 13,778.00, 14,642.40, 10,436.32 (2024), 15,470.60 (2025), the largest value in the table.
- **Trade:** total exports 2,555,250 MWh (2024) and 2,235,150 (2025), ZESCO's 2,069,330 and 1,690,980; ZESCO's imports 2,467,020 and 2,119,700.

## Checks

Counted in session 2429 from the table in the main checkout (`C:\Users\Shared\Documents\erw\warehouse\output`), read past its 11 header lines with `keep_default_na=False`, and from the saved bulletin's text read with pdfplumber, by scripts outside the repository. No request was made.

- 515 rows, 2013-01-01 to 2025-01-01, as header line 11 states; no (entity, variable, ts_utc) twice; no blank value; one `retrieved_at`, one `vintage` and one `source_url` in every row.
- **Stations add to their group's printed total** in all 52 group-years within 0.1 GWh: 50 to the MWh, and the IPP stations are 50 MWh under table 16's total in 2024 and 10 MWh under in 2025.
- **Sectors add to the Grand Total** to the MWh in all 10 years written.
- **Exports:** in 2024 the four traders' rows add to the traders' total (485,920 MWh). In 2025 they add to 557,130 MWh against the printed 544,170, a gap of 12,960, Africa GreenCo's row; the connector allows that one gap. In both years the traders' total plus ZESCO's equals the grand total exactly.
- **Capacity:** the five technologies add to the total, 4,118.71 MW.
- **Table 12:** the four groups' 2025 totals add to 14,560.23 GWh, table 12's printed total. Read from the saved bulletin, table 12's own five lines (major hydro 8,511.89, mini hydro 171.37, diesel 1.30, IPPs 5,873.17) add to 14,557.73, 2.50 under that printed total; table 16's IPP total is 5,875.67. The docstring and header say this (the CEC emergency generators' 2.50 GWh).
- **2019 consumption:** in the saved bulletin's table 19 the 2019 column equals the 2021 column in every sector (Grand Total 12,831.30 GWh in both); the table has no 2019 consumption row. The 2022 bulletin's figure (12,831,360.78 MWh as 2021's) is the report's; that bulletin is not saved under `warehouse/raw/erb_zambia/` and was not read here.
- **Against Ember** (`owid_ember_electricity_annual`, `owid_energy:ZMB`, `electricity_demand`, MWh; Ember has 2000 to 2024, no 2025): national generation is 0.888 (2016) to 1.204 (2023) times Ember's demand over 2013 to 2023, as the report says (0.89 to 1.20), and 0.817 in 2024. For 2024, generation less total exports plus ZESCO's imports is 13,477.69 GWh against Ember's 16,600, 19 percent under; for 2025 it is 14,444.78 GWh against ERB's own consumption total of 15,470.60. The report reads both gaps as the power traders' imports, which the bulletin charts (figure 6) but does not table.
- **License wording:** header line 10 and the connector's docstring say "internal until a ruling"; session 2425 has since recorded the verdict "needs written permission" for ERB (read 705). The flag (internal) and the verdict agree; only the wording was older. Changed in session 2429 (below).

## What it cannot say

- **Months:** the bulletin gives years only.
- **The power traders' imports:** only ZESCO's imports are tabled (table 18); the traders' are charted in figure 6, not taken. So generation less exports plus imports understates supply in 2024 and 2025.
- **2019 consumption:** not taken (above). Consumption before 2015, trade before 2024, and installed capacity before 2025 or by station are not in the tables read.
- **System peak demand:** not in the bulletin; session 2420 found none in the 2025 Energy Sector Report either.
- **Losses, own use and a balance:** consumption is by sector as ERB tables it; the table does not reconcile generation, trade and consumption.
- **Earlier bulletins' figures** for the same years, and any revision between bulletins.

## Acted on in session 2429

The two helpers who drafted this chain's notes made no request and changed no other file; every point was read and acted on or recorded:

- **The license wording:** the connector's docstring and header line 10 now give session 2425's verdict, "needs written permission". The table was written again offline (run `20261024T115446Z`): the same 515 rows, its metadata rows replaced by key; only the header changed, and the archive's data hash is the same (`5fe334c2...`).
- **Nothing else to act on:** the other checks agree with the connector, its header and session 2420's report.
