# Eurostat's monthly crude oil imports by field of production: the EU as a whole, 818 crude streams and the total, volume, value, price, API gravity and sulphur, January 2016 to September 2026 (nrg_ti_coifpm, EU_V)

Energy Research Warehouse (ERW), method note written in session 2429 (chain 115) for a table first written on 24 October 2026 (session 2427 of chain 115, `archive/sessions/SESSION_2427_REPORT.md`, commit `2926e490`). Eurostat's terms, the countries they allow and the shared country lists are described in `docs/methods/eurostat_renewable_capacity_annual.md` (session 2129). The same publisher's crude oil imports by country of origin, whose EU total this table's volumes are checked against, are `docs/methods/eurostat_crude_imports_monthly.md`; its monthly oil balance is `docs/methods/eurostat_oil_monthly.md`. EIA's crude imports and crude stream prices cover the United States only.

Tables: `eurostat_crude_imports_by_field_monthly`

## Publisher and address

Eurostat (Statistical Office of the European Union), "Crude oil imports by field of production - monthly data" (`nrg_ti_coifpm`), page `https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_coifpm/default/table`, through the statistics API without a key, as JSON-stat 2.0, filtered to the EU aggregate `EU_V`:

- `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_coifpm?format=JSON&lang=EN&geo=EU_V&sinceTimePeriod=2016-01`

The statistics API answers this query asynchronously: its first answer (2026-10-24T11:29:11Z) is HTTP 413, "ASYNCHRONOUS_RESPONSE. Your request will be treated asynchronously. Please try again later.", and the same address asked again at 11:31:26Z answered with the data (`runs/c115/s2427/probe.csv`, `retry.csv`). Eurostat's table of contents (read in session 2426) lists `nrg_ti_coifpm` from 2005-01 to 2026-09, updated 23.10.2026.

Source id `eurostat:nrg_ti_coifpm_eu` (`sources.csv`: license public, first and last seen 2026-10-24). The answer is 2,015,581 bytes (sha256 `d1fecd74...`). Its dimensions are `freq, crudeoil, indic_nrg, geo, time` of sizes 1, 819, 6, 1 and 129 (January 2016 to September 2026), with freq `M` and geo `EU_V` only, "European Union (aggregate changing according to the context)". It holds 103,535 values, label "Crude oil imports by field of production - monthly data", "updated" 2026-10-23T23:00:00+0200:

| Indicator | Code | Values | Of them 0 | Confidential (no value) |
|---|---|---|---|---|
| Volume, thousand barrels | VOL_THS_BBL | 30,394 | 27,634 | 15,584 |
| Sulphur content, percent | SULPH_PC | 26,292 | 18,279 | 0 |
| API gravity, degree | API_DEG | 26,269 | 18,278 | 0 |
| Average price, USD per barrel | AVGPRC_USD_BBL | 17,920 | 15,260 | 8,420 |
| Value, thousand USD | VAL_THS_USD | 2,660 | 0 | 5,405 |
| Reporting companies, number | CMPY_NR | 0 | 0 | 0 |

It holds 29,412 statuses: 29,409 confidential (status `|C`, each on a cell with no value) and 3 "b" (break in series).

Saved answer: `warehouse/raw/eurostat_crude_imports_by_field_monthly/nrg_ti_coifpm_eu.json`, one file, written by session 2427's retry script (`runs/c115/s2427/retry.py`, which also kept the same bytes as `runs/license_reads/s2427/04_nrg_ti_coifpm_eu.json`), not by the connector; `retry.csv`'s sha256 is the saved file's. The connector writes the same file when it fetches. ec.europa.eu's robots file, read in that session (sha256 `fc082fc2...`), disallows the old `/eurostat/SDMX/diss-web/rest/` path and the search pages, not `/eurostat/api/dissemination/`, and names no AI agent.

Session 2427 made 4 requests of 20: the robots file, `nrg_ti_coifpm` from August 2026 for every area to read its dimensions (1,786,391 bytes), the EU's query (413) and the same query again (2,015,581 bytes). The trial and the write ran offline.

Connector: `warehouse/connectors/eurostat_crude_by_field.py` (session 2427), `[--offline] [--out-dir DIR]`. Ceiling: the address asked at most 10 times, a minute apart, until it answers with the data (a JSON body beginning `{"version"`).
- **Kept:** every crude oil code, `TOTAL` among them; volume, value, price, API gravity and sulphur.
- **Values:** volume as Eurostat's thousand barrels; value Eurostat's thousand USD times 1,000; price, API gravity and sulphur as published; rounded to 0.001.
- **Zeros:** a volume or value of 0 is kept; a price, API gravity or sulphur of 0 is not taken (Eurostat writes 0 there for a stream with no import or a confidential volume), and header line 3 counts them.
- **Stops:** dimensions other than the five named, a frequency not monthly, a geo other than `EU_V`, an indicator not among the six, a reporting companies value, a period not a month, a value that is not a number, or a key given twice.
- **Offline:** on `--offline` the saved answer is read, and `retrieved_at` is the file's modification time.

## Schedule and records

Schedule: none. No shell script under `warehouse/`, no workflow in `.github/workflows/`, no file in `scripts/` and not `warehouse/scheduled.py` names it.

Records:
- `runs/status/eurostat_crude_imports_by_field_monthly.json` holds the run by hand: run `20261024T113637Z`, ok, "51718 rows". `run_status.csv`: no row.
- `archive_manifest.csv`: 51,718 rows, run `20261024T113642Z-local`, archived 2026-10-24T11:36:42Z, `data_sha256` `c6f14662...`.
- `coverage.csv`: sector oil (`build_coverage.py`'s rule of session 2427), 819 nodes, P1M, 2016-01-01 to 2026-09-01, last run 2026-10-24T11:36:37Z, validator pass, public, tier source.
- License: `license_tables.csv`, Eurostat, "the source registry"; `docs/licenses.md`, verdict "may be public", flag public, "agrees", ERW verdict public.
- Release: listed as held in `docs/redivis/release-v1/tables.csv` (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`); `variables.csv` has its five variables and units.
- Live set: under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded.
- Not yet in the Stanford Redivis draft: no row in `redivis_uploads.csv` or `redivis_uploads_stanford.csv`.
- Package and site: rows in `package/src/erw/data/tables.csv`, `site/data/table_citations.json` and `site/data/table_verdicts.json` since session 2431.

Readers: none. `tests/test_session2427.py` (3 tests) tests the connector on JSON-stat built in the test.

The write (`runs/c115/s2427/write.out`, 11:36:36 to 11:36:47): connector, validator, coverage and archive exit 0; "metadata to the branch exit=1", the patch conflict the report names, after which one row each was put in by key. The trial waited for the data lock from 11:34:29 to 11:36:31. The report records that chain 114's branch copies of the metadata files may have stood in the main checkout from about 11:33 to 11:36 UTC, and that neither patch holds a row of chain 114's tables.

## Vintage and revision

One write, run `20261024T113637Z`, offline from the saved answer; header line 10: "This run wrote 51718 rows: 51718 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs." `retrieved_at` is 2026-10-24T11:31:26Z in every row, the saved file's modification time and the retry's fetch. `vintage` is blank in every row; Eurostat's update time, 2026-10-23T23:00:00+0200, is on header line 4.

Eurostat flags 3 rows "b" (a break in series): the total's volume, value and price in December 2019 (332,357 kbbl, USD 22,018,069,000, USD 66.25 a barrel). A revised month replaces the old figure on a later run; no earlier version is kept.

## Shape and variables

Series, 51,718 rows, 16 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_crudeoil, x_indic_nrg, x_flag`), 10 header lines.
- **`entity`:** `eurostat_crude_field:EU:<Eurostat crude oil code>`, 819 values: `TOTAL` and 818 streams (among them `UNK`, "Unknown", and a "Miscellaneous" code for each origin, such as `US_MSC`).
- **`node`:** the stream's name as Eurostat gives it ("United States Texas - West Texas Intermediate (WTI)"; "Total" for `TOTAL`).
- **`ts_utc`:** the month's first day; `freq` P1M; 124 months of the answer's 129 have a row.
- **`geo`, `market` and `vintage`:** blank in every row (the EU is an aggregate).
- **Variables:**

  | Variable | Unit | Indicator | Rows | Zeros | Streams with a row, besides the total | Largest |
  |---|---|---|---|---|---|---|
  | `volume` | kbbl | VOL_THS_BBL | 30,394 | 27,634 | 815 | TOTAL, July 2019, 360,778 |
  | `sulphur` | pct | SULPH_PC | 8,013 | 0 | 302 | Venezuela Miscellaneous, October 2020, 7.78 |
  | `api_gravity` | degAPI | API_DEG | 7,991 | 0 | 302 | Kazakhstan CPC Blend, March 2024, 593.179 |
  | `price` | USD/bbl | AVGPRC_USD_BBL | 2,660 | 0 | 209 | United Kingdom Miscellaneous, July 2022, 178.984 |
  | `value` | USD | VAL_THS_USD | 2,660 | 0 | 209 | TOTAL, April 2026, 38,679,118,314 |

  The largest value in the table is the total's value in April 2026, USD 38,679,118,314. No value is negative. Volumes carry up to three decimals (93.8 percent are whole); values are whole dollars.
- **Rows by year:** 36 in each of 2016 to 2019, then 8,828 (2020), 8,381, 8,525, 6,395, 7,331, 7,115 and 4,999 (2026, to September).
- **Streams with a volume above zero:** 222 and the total; 2,637 stream-months.
- **Not taken:** price 15,260, API gravity 18,278 and sulphur 18,279 zeros (header line 3); the reporting companies indicator, which has no value; confidential cells (29,409).
- **A sum over streams is the total only where nothing is confidential:** 15,584 volumes and 5,405 values are confidential and have no row.

## Checks

From session 2427 (`archive/sessions/SESSION_2427_REPORT.md`), each counted again in session 2429 from `warehouse/output` in the main checkout, read past its 10 header lines with `keep_default_na=False` and every column as text, and from the saved answer. No request was made.

- **Against the answer:** the answer's 103,535 values less the 51,817 zero prices and grades (15,260 + 18,278 + 18,279) are 51,718, the table's rows, the same keys, none on one side only; every value is the answer's (value times 1,000), largest difference 2e-6; every flag is the answer's.
- **Table:** no (entity, variable, ts_utc) twice; every `entity` built from `x_crudeoil` and every `node` Eurostat's label; one `retrieved_at` and one `source_url`, the address above; each variable has one unit and one indicator.
- **Value against volume times price times 1,000:** 2,402 stream-months have all three (123 of them the total). 2,395 agree within 1 percent and 2,357 within 0.1 percent. The seven others: Cameroon Lokele, February 2026 (USD 60,696,000 against 219 kbbl at 72.97, 15,980,430: 74 percent); Senegal Miscellaneous, February 2026 (34 percent); Libya Zueitina, March 2025 (2.6 percent); Neutral Zone Miscellaneous, July 2025, Canada Hibernia, November 2022, Gabon Lucina Marine, January 2025, and Tunisia Zarzaitine, April 2020 (1.5 to 1.8 percent).
- **The total volume against the EU's crude imports in tonnes** (`eurostat_crude_imports_monthly`, entity `eurostat_crude_imp:EU27_2020:TOTAL`): 121 months have both (to June 2026, the last month of the tonnes). Barrels a tonne:

  | Year | Months | Billion bbl | Mt | Annual sums | Median month |
  |---|---|---|---|---|---|
  | 2016 | 12 | 3.959 | 505.9 | 7.83 | 7.87 |
  | 2017 | 12 | 4.038 | 523.0 | 7.72 | 7.69 |
  | 2018 | 12 | 4.014 | 512.8 | 7.83 | 7.78 |
  | 2019 | 12 | 4.019 | 507.8 | 7.91 | 7.91 |
  | 2020 | 10 | 2.715 | 367.0 | 7.40 | 7.38 |
  | 2021 | 11 | 2.977 | 405.9 | 7.33 | 7.39 |
  | 2022 | 10 | 2.965 | 396.7 | 7.47 | 7.46 |
  | 2023 | 12 | 3.751 | 471.8 | 7.95 | 7.99 |
  | 2024 | 12 | 3.737 | 471.2 | 7.93 | 7.92 |
  | 2025 | 12 | 3.703 | 455.8 | 8.12 | 8.15 |
  | 2026 | 6 | 1.770 | 221.3 | 8.00 | 8.18 |

  A single month runs from 6.61 (February 2026) to 9.12 (March 2026). The total's volume, all months, is about 4.0 billion barrels a year in 2016 to 2019 and 3.7 billion in 2023 to 2025. The report reads the higher 2016 to 2019 volumes as `EU_V` then including the United Kingdom; Eurostat's label says only "aggregate changing according to the context", and this note did not test it.
- **The zeros left out:** price 15,260, API gravity 18,278, sulphur 18,279, as header line 3 and the run's printed line in `runs/c115/s2427/write.out` say.
- **U.S. streams:** 26 codes begin `US_`, all in the table (each with at least a zero volume); 8 have a volume above zero. Million barrels a year (2026 to August):

  | Stream | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
  |---|---|---|---|---|---|---|---|
  | West Texas Intermediate (`US_TXA_WTI`) | 91.1 | 115.1 | 158.7 | 423.3 | 451.2 | 386.1 | 253.2 |
  | Miscellaneous (`US_MSC`) | 48.2 | 59.6 | 88.1 | 115.4 | 103.3 | 100.3 | 124.9 |
  | North Dakota Sweet (`US_ND_SW`) | 2.1 | 2.2 | 3.9 | 0 | 0 | 0 | 0 |
  | Bakken (`US_ND_BKK`) | 9.0 | 0 | 0 | 0 | 0 | 0 | 0 |
  | Eagle Ford (`US_TXA_EGF`) | 0.7 | 0 | 0 | 1.8 | 0 | 0 | 0 |
  | Mars (`US_XJB`) | 0 | 0 | 0 | 1.4 | 1.1 | 0 | 0 |
  | Light Louisiana Sweet (`US_LGHT_LUA_SW`) | 0 | 0 | 0 | 0 | 0.7 | 0 | 0 |
  | Heavy Louisiana Sweet (`US_HVY_LUA_SW`) | 0 | 0 | 0 | 0 | 0 | 0 | 0.8 |
  | All 26 | 190.4 | 205.1 | 296.2 | 541.9 | 556.4 | 486.4 | 378.9 |

  West Texas Intermediate's share of the total's volume: 3.4 percent (2020), 3.9, 5.4, 11.3, 12.1, 10.4 (2025) and 10.4 (2026 to August). Its price, USD a barrel, as the mean of the monthly prices and as value over volume: 2020 43.8 and 43.8; 2021 70.2 and 76.3; 2022 103.9 and 104.2; 2023 85.4 and 85.5; 2024 83.2 and 83.2; 2025 71.4 and 71.4; 2026 95.5 and 96.4. August 2026: 36,538.901 kbbl at 94.356, API gravity 42.861, sulphur 0.158.

When this note was drafted, the description and the data disagreed here; each is acted on below:
1. **"819 streams."** Header line 3 counts 819 crude oil codes, `TOTAL` among them; the report says "819, plus TOTAL". The table holds 818 streams and the total (819 entities).
2. **"A month from January 2016"** (the docstring: each stream's volume, value, price and grades). Streams begin in January 2020. In 2016 to 2019 the table holds only the total's volume, value and price (144 rows, 36 a year), and no API gravity or sulphur.
3. **"January 2016 to September 2026."** Five months have no row at all: September and December 2020, October 2021, May and August 2022 (the total's volume included). September 2026 holds only 57 API gravity and 58 sulphur rows: the last volume, value and price are August 2026.
4. **Barrels a tonne.** The report's figures (7.4 to 8.2 by year, 2020 to 2022 at 7.4 to 7.5, 2025 at 8.15) are medians of the monthly ratios. Annual sums give 7.33 for 2021 and 8.12 for 2025. 2023 to 2025 (7.93 to 8.12) run higher than 2016 to 2019 (7.72 to 7.91), which the report does not say.
5. **The West Texas Intermediate prices** in the report (43.8, 103.9, 85.4, 83.2, 71.4, 95.5) are the means of the monthly prices, not weighted by volume (value over volume: 104.2 for 2022, 96.4 for 2026). Its "2026 (to September)" volume ends in August.
6. **API gravity.** 533 rows exceed 70 degrees API and 321 exceed 100, the highest 593.179 (Kazakhstan CPC Blend, March 2024); all fall in twelve months (May 2023, and December 2023 to November 2024 but for September 2024), 40 to 53 streams in each. The total's API gravity (53 months) stays between 29.5 and 35.8. These are Eurostat's figures as printed; nothing here corrects them, and neither the connector nor the report says so.
7. **The release package's reason.** `docs/redivis/release-v1/tables.csv` gives the held reason "written 21 October 2026, session 489", the shared `STORAGE_HELD` text; this table was written on 24 October 2026 by session 2427.

The header's units, its rule for zeros and its counts of the zeros left out agree with the table.

## What it cannot say

- **The EU as a whole only:** no member's imports by stream; `EU_V` is the member states of the month, as Eurostat defines it.
- **Streams from 2020 only,** and the total from 2016; the months from 2005 that Eurostat publishes before 2016 are not read.
- **Confidential cells:** 15,584 volumes, 8,420 prices and 5,405 values have no figure, so a stream's volume or value is missing where few importers buy it, and the streams do not add up to the total.
- **No zero price or grade:** a missing price, API gravity or sulphur may be a month with no import, a confidential volume or a figure Eurostat did not give.
- **The number of reporting companies:** not given for the EU.
- **How Eurostat assigns a cargo to a field,** and how it builds the average price and grades, are not read here; its metadata page for `nrg_ti_coifpm` would say.

## Acted on in session 2429

The two helpers who drafted this chain's notes made no request and changed no other file; every point was read and acted on or recorded:

- **Items 1 to 3 and 6:** the connector's header now gives 818 streams and their total, the month the streams begin (2020-01, before it the total's volume, value and price only), the five months with no row, the last month of volume, value and price (2026-08) and of the grades (2026-09), and the API gravity figures above 70 degrees (533, the highest 593.2), kept as Eurostat prints them. The table was written again offline (run `20261024T115307Z`): the same 51,718 rows, its metadata rows replaced by key; the archive's data hash is the same (`c6f14662...`).
- **Items 1, 4 and 5:** session 2427's report is corrected, saying so: 818 streams and the total; the barrels a tonne as medians of the months (annual sums 7.33 for 2021, 8.12 for 2025); the WTI prices as means of the monthly prices, with value over volume beside them (104.2 for 2022, 96.4 for 2026), and its 2026 volume to August.
- **Item 7:** as for the coal table: `release_v1.py`'s one held reason for every table, left as it is and named in the chain's note.
