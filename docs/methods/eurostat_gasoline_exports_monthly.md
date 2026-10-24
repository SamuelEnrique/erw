# Eurostat's monthly motor gasoline exports by destination: 35 European countries and the EU, 174 partners, January 2016 to September 2026 (nrg_te_oilm, motor gasoline)

Energy Research Warehouse (ERW), method note written in session 2471 (chain 119) for a table first written on 24 October 2026 (session 2468 of chain 119, `archive/sessions/SESSION_2468_REPORT.md`), a source of the session's own choosing. Eurostat's terms, the countries they allow and the shared country lists are described in `docs/methods/eurostat_renewable_capacity_annual.md` (session 2129). The same publisher's crude oil imports by origin, whose connector this one was built from, are `docs/methods/eurostat_crude_imports_monthly.md`; the monthly oil balance, whose gasoline exports this table's partner totals are checked against, is `docs/methods/eurostat_oil_monthly.md`.

Tables: `eurostat_gasoline_exports_monthly`

## Publisher and address

Eurostat (Statistical Office of the European Union), "Oil and petroleum products exports - monthly data" (`nrg_te_oilm`), page `https://ec.europa.eu/eurostat/databrowser/view/nrg_te_oilm/default/table`, through the statistics API without a key, as JSON-stat 2.0, filtered to motor gasoline without its biofuel portion (SIEC `O4652XR5210B`):

- `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_te_oilm?format=JSON&lang=EN&siec=O4652XR5210B&sinceTimePeriod=2016-01`

The API answers asynchronously: its first answer is HTTP 413 (142 bytes, `runs/c119/s2468/probe.csv`, 13:11:04 UTC), and the same address asked again answers with the data (`runs/c119/s2468/retry.csv`, 13:15:11 UTC, HTTP 200). The report says "two minutes later"; the two records are 4 minutes 7 seconds apart.

Source id `eurostat:nrg_te_oilm_gasoline` (`sources.csv`: license public, first and last seen 2026-10-24). The answer is 8,407,254 bytes (sha256 `73945cbb...`, the same in `retry.csv` and recomputed in session 2471). Its dimensions are `freq, siec, partner, unit, geo, time` of sizes 1, 1, 175, 1, 39 and 129 (January 2016 to September 2026). It holds 562,085 values and 1,412 statuses (1,406 "p", 6 "|C" with no value), with "updated" 2026-10-23T23:00:00+0200.

Saved answer: `warehouse/raw/eurostat_gasoline_exports_monthly/nrg_te_oilm_gasoline.json`, one file, written by session 2468's retry script (`runs/c119/s2468/retry.py`), not by the connector; the connector writes the same file when it fetches.

Session 2468 made 4 requests of 20: www.enecho.meti.go.jp's robots address (HTTP 403, read 835: Japan's statistics, the first choice, left), ec.europa.eu's robots file (read 836: disallows the old `/eurostat/SDMX/diss-web/rest/` path and the search pages, not `/eurostat/api/dissemination/`, and names no AI agent), and the address above twice.

Connector: `warehouse/connectors/eurostat_gasoline_exports.py` (session 2468, made from session 2369's crude imports connector by `runs/c119/s2468/make_connector.py`), `[--offline] [--out-dir DIR]`. Ceiling: the address asked at most 10 times, a minute apart, until it answers with the data (a JSON body beginning `{"version"`).
- **Kept:** the exporting areas in `eurostat_res_capacity.KEPT`; every partner.
- **Values:** Eurostat's thousand tonnes times 1,000.
- **Stops:** dimensions other than the six named, a product other than `O4652XR5210B`, a unit other than THS_T, a frequency not monthly, a period not a month, a value that is not a number, or a key given twice.
- **Offline:** on `--offline` the saved answer is read, and `retrieved_at` is the file's modification time.

## Schedule and records

Schedule: none. No shell script under `warehouse/`, no workflow in `.github/workflows/`, no file in `scripts/` and not `warehouse/scheduled.py` names it.

Records:
- `runs/status/eurostat_gasoline_exports_monthly.json` (main checkout): run `20261024T132315Z`, ok, "557429 rows". `run_status.csv`: no row.
- `archive_manifest.csv`: 557,429 rows, run `20261024T132335Z-local`, `data_sha256` `6ce1f4b9...` (not recomputed here).
- `coverage.csv`: iso `eurostat`, 174 nodes, P1M, 2016-01-01 to 2026-09-01, 557,429 rows, last run 2026-10-24T13:23:15Z, validator pass, license public, sector oil, tier source.
- Release: held (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`; `docs/redivis/release-v1/tables.csv`, "held: not yet on Redivis ... after the storage is settled").
- Live set: under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded.
- Stanford Redivis draft (`erw:b9wm`): uploaded by session 2471 at 13:45:07 UTC (`redivis_uploads_stanford.csv`), 557,429 rows; nothing released.
- Package: `package/src/erw/data/tables.csv` has its row (public) since session 2473; `site/data/table_citations.json` and `table_verdicts.json` each name it.
- `license_tables.csv`: Eurostat, "the source registry". `docs/licenses.md`, the table's row: "may be public", flag public, "agrees".

Readers: none. `tests/test_session2468.py` (3 tests) tests the connector on JSON-stat built in the test.

## Vintage and revision

One write, run `20261024T132315Z`, offline from the saved answer; header line 10: "This run wrote 557429 rows: 557429 new, 0 replacing earlier rows ...". `retrieved_at` is 2026-10-24T13:15:11Z in every row. `vintage` is blank; Eurostat's update time is on header line 4.

Eurostat flags 1,324 rows "p" (provisional): 2016 292, 2017 442, 2018 64, 2019 204, 2020 165, 2022 124, 2023 33, none in 2021 or since 2023. By area the Netherlands 594, Sweden 268, Germany 156, Norway 100, Greece 95, Estonia 30, Portugal 17, Denmark 16, Italy 14, Ireland 11, Slovakia 7, Czechia 6, Hungary 6, North Macedonia 2, Poland 2. The answer's other 82 "p" are the United Kingdom's, left out. A revised month replaces the old figure on a later run; no earlier version is kept.

The latest month differs by area. Of the 37 areas' exports to all partners, the last month is September 2026 for 2 (Denmark, Finland), August for 11, July for 21, and June for 3 (Greece, EU27_2020 and EA21). The EU aggregate thus ends in June 2026.

## Shape and variables

Series, 557,429 rows, 17 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_geo_code, x_partner, x_partner_name, x_flag`), 10 header lines.
- **`entity`:** `eurostat_gasoline_exp:<Eurostat geo code>:<partner code>`, 6,411 values.
- **`variable`:** `exports`; `unit` t; `freq` P1M; `ts_utc` the month's first day, 129 months.
- **`geo`:** the exporting area's ISO alpha-2 code (Eurostat's EL written GR, 16,562 rows), blank for EU27_2020 and EA21 (22,776 rows).
- **`node`:** "Motor gasoline exports to <partner's English name>".
- **`market` and `vintage`:** blank.
- **Values:** every value is a whole number of tonnes, and 518,359 rows are zero (Eurostat publishes a zero for most partners of most areas in most months; the zeros are kept).
  - The largest value is the EU's exports to all partners in April 2019, 6,887,991 t.
  - **14 values are negative,** as published: Germany to Slovenia (1 month) and to Slovakia (2); the Netherlands to Spain (2), to France (August 2025, -7,520 t) and to "not specified" (5, the largest -244,289 t in September 2021); the EU to "not specified" (3: June 2020 -86,426, September 2021 -206,289, November 2021 -50,551 t). Neither the connector nor the report mentions them.
- **Areas, 37:**
  - 35 countries (the 27 members, Norway, Albania, Georgia, Moldova, Montenegro, North Macedonia, Serbia and Turkiye) and the two aggregates;
  - the most rows: EU27_2020 17,750, Sweden 17,721;
  - the fewest: Moldova 10,010, Montenegro 7,326, EA21 5,026 (from January 2024).
  - The United Kingdom is in the answer and left out by Eurostat's terms (4,656 values); Iceland is in the answer with no value.
- **Partners, 174:**
  - 160 two-letter codes, and Eurostat's aggregates: `TOTAL`, `EU27_2020`, `EU28`, `EUR_OTH`, `AFR_OTH`, `AME_LAT`, `AME_OTH`, `ASI_NME`, `ASI_NME_OTH`, `ASI_OTH`, `EX_SU_OTH`, `CN_X_HK` (China except Hong Kong), `NSP` (not specified) and `TW_CAP` (labelled "Taipei"; `TW` is also a partner, and how the two relate is not read);
  - the answer's 175th partner, `EX_YU_OTH` (other countries of former Yugoslavia, before 1992), has no value in the areas kept.
- **A sum over partners double counts:** the aggregates overlap the countries.
- **Partner `NA` is Namibia** (2,465 rows): a reader that turns "NA" into a missing value (pandas by default) loses it. Read with `keep_default_na=False`.

The EU's (EU27_2020) gasoline exports, Mt a year:

| Year | To all partners | To the United States |
|---|---|---|
| 2016 | 69.9 | 9.17 |
| 2017 | 72.6 | 9.70 |
| 2018 | 72.4 | 10.76 |
| 2019 | 72.9 | 10.99 |
| 2020 | 61.6 | 11.00 |
| 2021 | 69.7 | 16.16 |
| 2022 | 68.9 | 13.04 |
| 2023 | 67.0 | 13.07 |
| 2024 | 66.5 | 10.15 |
| 2025 | 62.4 | 8.81 |
| 2026, January to June | 31.0 | 2.61 |

## Checks

Counted in session 2471 from the table in the main checkout (`C:\Users\Shared\Documents\erw\warehouse\output`), read past its 10 header lines with `keep_default_na=False` and every column as text, and from the saved answer, by scripts outside the repository. No request was made.

- The row, entity, partner and area counts above; no (entity, variable, ts_utc) twice; no blank value; every `retrieved_at` 2026-10-24T13:15:11Z; every `source_url` the address above.
- **The answer against the table:** 562,085 values less the United Kingdom's 4,656 is 557,429, the table's rows. The 6 "|C" (confidential) cells, all Finland's, carry no value and have no row.
- **Against the oil balance** (`eurostat_oil_monthly`, entity `eurostat_oil:<geo>:O4652XR5210B`, variable `flow:EXP`): the table has 4,282 area-months of exports to all partners (`TOTAL`), and the balance 4,246; 4,243 are in both.
  - Equal to the tonne in 4,107, within 1 percent in 4,212, as the report states.
  - The 31 outside 1 percent: EU27_2020 8, Finland 6, Croatia 5, France 3, Greece 2, Czechia 2, North Macedonia 2, Albania, Georgia and the Netherlands 1 each. The largest: the EU in March 2026, 4,645,399 t against 4,971,725; the EU and the Netherlands in December 2019, each 307,000 t under the balance.
  - Not compared: 39 area-months in this table only (EA21 30, Moldova 8, Montenegro 1), and 3 in the balance only (Albania November 2021, Hungary February 2025, Spain March 2026).
- **The EU's exports to the United States,** Mt a year: the report's 9.2 (2016), 11.0 (2020), 16.2 (2021), 13.0 (2022), 10.2 (2024) and 8.8 (2025) hold (table above). Its "2.6 (2026 to September)" is 2.61 Mt, but the EU rows end in June 2026: six months, not nine.
- The header's 174 partners, its "left out by Eurostat's terms: UK", its 14 named aggregates, and its unit and geo rules agree with the table.

## What it cannot say

- **Motor gasoline only:** the other products of `nrg_te_oilm` (diesel, jet fuel and the rest) are not read.
- **Quantities, not prices or values.**
- **The months not yet reported** by each area (above): the latest months are not a total for Europe.
- **How Eurostat assigns the partner country,** and why some values are negative: its metadata page for `nrg_te_oilm` would say; not read here.
- **The importer's side:** the United States' own record of these imports is in EIA's tables, not compared here.

## Acted on in session 2471

- **The report** (`SESSION_2468_REPORT.md`) carries a correction:
  - the retry came 4 minutes 7 seconds after the 413, not two minutes;
  - the EU's 2026 figure is January to June;
  - the 14 negative values are named.
- **The connector and the header are not changed.** They make no false claim: the header gives the table's own first and last month, and the values are as published. A table's latest months are named above.
- **`TW_CAP` against `TW`** is left unread. Eurostat's code list would say how the two relate; asking it is a request for a later session.
