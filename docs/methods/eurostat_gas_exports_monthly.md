# Eurostat's monthly natural gas and LNG exports by destination: 36 European countries and the EU, 166 partners, January 2016 to September 2026 (nrg_te_gasm)

Energy Research Warehouse (ERW), method note written in session 2471 (chain 119) for a table first written on 24 October 2026 (session 2469 of chain 119, `archive/sessions/SESSION_2469_REPORT.md`), a second source of the session's own choosing. Eurostat's terms, the countries they allow and the shared country lists are described in `docs/methods/eurostat_renewable_capacity_annual.md` (session 2129). The imports side, which this table mirrors, is `docs/methods/eurostat_gas_imports_monthly.md`; the monthly gas balance, whose exports this table's partner totals are checked against, is `docs/methods/eurostat_gas_balance_monthly.md`.

Tables: `eurostat_gas_exports_monthly`

## Publisher and address

Eurostat (Statistical Office of the European Union), "Natural gas exports - monthly data" (`nrg_te_gasm`), page `https://ec.europa.eu/eurostat/databrowser/view/nrg_te_gasm/default/table`, through the statistics API without a key, as JSON-stat 2.0, filtered to terajoules of gross calorific value:

- `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_te_gasm?format=JSON&lang=EN&unit=TJ_GCV&sinceTimePeriod=2016-01`

The API answers asynchronously: its first answer is HTTP 413 (142 bytes, `runs/c119/s2469/probe.csv`, 13:30:34 UTC), and the same address asked again answers with the data (`runs/c119/s2469/retry.csv`, 13:32:42 UTC, HTTP 200). The report says "100 seconds later"; the two records are 128 seconds apart.

Source id `eurostat:nrg_te_gasm` (`sources.csv`: license public, first and last seen 2026-10-24). The answer is 16,439,803 bytes (sha256 `51a64848...`, the same in `retry.csv` and recomputed in session 2471). Its dimensions are `freq, siec, partner, unit, geo, time` of sizes 1, 2 (G3000, G3200), 166, 1, 41 and 129 (January 2016 to September 2026). It holds 1,065,091 values and 2,743 statuses (2,642 "m" with no value, 97 "p", 4 "e"), with "updated" 2026-10-23T23:00:00+0200.

Saved answer: `warehouse/raw/eurostat_gas_exports_monthly/nrg_te_gasm_tj.json`, one file, written by session 2469's retry script (`runs/c119/s2469/retry.py`), not by the connector; the connector writes the same file when it fetches.

Session 2469 made 3 requests of 20: ec.europa.eu's robots file (13:30:26 UTC, 10,827 bytes, the same file session 2468 read as read 836: it disallows the old `/eurostat/SDMX/diss-web/rest/` path and the search pages, not `/eurostat/api/dissemination/`, and names no AI agent), and the address above twice.

Connector: `warehouse/connectors/eurostat_gas_exports.py` (session 2469), `[--offline] [--out-dir DIR]`. Ceiling: the address asked at most 10 times, a minute apart, until it answers with the data (a JSON body beginning `{"version"`).
- **Kept:** the exporting areas in `eurostat_res_capacity.KEPT`; every partner; both products.
- **Values:** Eurostat's TJ of gross calorific value times 277.7778 (1,000,000 / 3,600), written as MWh rounded to 0.001, as `eurostat_gas_imports_monthly` writes them.
- **Stops:** dimensions other than the six named, a product other than G3000 and G3200, a unit other than TJ_GCV, a frequency not monthly, a period not a month, a value that is not a number, or a key given twice.
- **Offline:** on `--offline` the saved answer is read, and `retrieved_at` is the file's modification time.

## Schedule and records

Schedule: none. No shell script under `warehouse/`, no workflow in `.github/workflows/`, no file in `scripts/` and not `warehouse/scheduled.py` names it.

Records:
- `runs/status/eurostat_gas_exports_monthly.json` (main checkout): run `20261024T133549Z`, ok, "1049782 rows". `run_status.csv`: no row.
- `archive_manifest.csv`: 1,049,782 rows, run `20261024T133628Z-local`, `data_sha256` `490a77ee...` (not recomputed here).
- `coverage.csv`: iso `eurostat`, 332 nodes, P1M, 2016-01-01 to 2026-09-01, 1,049,782 rows, last run 2026-10-24T13:35:49Z, validator pass, license public, sector `gas;lng`, tier source.
- Release: held (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`; `docs/redivis/release-v1/tables.csv`, "held: not yet on Redivis ... after the storage is settled").
- Live set: under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded.
- Stanford Redivis draft (`erw:b9wm`): uploaded by session 2471 at 13:45:07 UTC (`redivis_uploads_stanford.csv`), 1,049,782 rows; nothing released.
- Package: `package/src/erw/data/tables.csv` has its row (public) since session 2473; `site/data/table_citations.json` and `table_verdicts.json` each name it.
- `license_tables.csv`: Eurostat, "the source registry". `docs/licenses.md`, the table's row: "may be public", flag public, "agrees".

Readers: none. `tests/test_session2469.py` (3 tests) tests the connector on JSON-stat built in the test.

## Vintage and revision

One write, run `20261024T133549Z`, offline from the saved answer; header line 10: "This run wrote 1049782 rows: 1049782 new, 0 replacing earlier rows ...". `retrieved_at` is 2026-10-24T13:32:42Z in every row. `vintage` is blank; Eurostat's update time is on header line 4.

Eurostat flags 97 rows "p" (provisional): 2017 56, 2019 18, 2024 1, 2025 1, 2026 21; by area the Netherlands 56, France 14, Croatia 11, Romania 7, Italy 5, Czechia 4. It flags 4 rows "e" (estimated): Finland's exports to Norway in September 2026, natural gas and LNG, to Norway and to all partners, 5,500 MWh each. Its 2,642 "m" (missing) cells are all Moldova's and have no row. A revised month replaces the old figure on a later run; no earlier version is kept.

The latest month differs by area. Of the 38 areas' natural gas exports to all partners, the last month is September 2026 for 26, August for 9 (the EU27_2020 and EA21 aggregates among them), July for 2 (Albania, North Macedonia), and January 2022 for Ukraine. A September 2026 row can be a published zero where the balance has a figure (Checks).

## Shape and variables

Series, 1,049,782 rows, 18 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_geo_code, x_siec, x_partner, x_partner_name, x_flag`), 10 header lines. On this machine the file is 327,910,941 bytes.
- **`entity`:** `eurostat_gas_exports:<Eurostat geo code>:<SIEC>:<partner code>`, 12,600 values; every row's entity is built from its `x_` codes.
- **Products (`x_siec`):** G3000 natural gas, 525,288 rows; G3200 LNG, a part of it, 524,494 rows. The two are never added.
- **`variable`:** `exports`; `unit` MWh; `freq` P1M; `ts_utc` the month's first day, 129 months.
- **`geo`:** the exporting area's ISO alpha-2 code (Eurostat's EL written GR, 28,864 rows), blank for EU27_2020 and EA21 (33,355 rows).
- **`node`:** "Natural gas exports to <partner's English name>" or "LNG exports to <partner's English name>", agreeing with `x_siec` in every row.
- **`market` and `vintage`:** blank.
- **Values:** no negative; 1,024,314 rows are zero (G3000 506,576, G3200 517,738), kept as published, which is why the file is large. The largest value is the EU's natural gas exports to all partners in January 2017, 390,480,055.556 MWh.
- **Areas, 38:**
  - 36 countries (the 27 members, Norway, Albania, Georgia, Moldova, Montenegro, North Macedonia, Serbia, Turkiye and Ukraine) and the two aggregates;
  - the most rows: Belgium 36,227, Slovakia 36,149;
  - the fewest: Moldova 19,790 (January 2021 to August 2026), Montenegro 18,780, EA21 6,560 (from January 2025), Ukraine 4,262 (January 2021 to January 2022);
  - EU27_2020 has every month of 2016 to 2018 and 2021 to 2025 and January to August 2026; in 2019 it has 202 rows in four months (January 2, March 98, September 4, November 98) and no exports to all partners; in 2020 it has none.
  - The United Kingdom (6,069 values) and Kosovo (9,240) are in the answer and left out by Eurostat's terms; Iceland is in the answer with no value.
- **Partners, 166:** 158 two-letter codes (the United Kingdom among them, as a destination) and Eurostat's aggregates `TOTAL`, `NSP` (not specified), `AFR_OTH`, `AME_OTH`, `ASI_NME_OTH`, `ASI_OTH`, `EUR_OTH`, `EX_SU_OTH`. Every partner of the answer has a row.
- **A sum over partners double counts:** `TOTAL` overlaps the countries.
- **Partner `NA` is Namibia** (5,246 rows): a reader that turns "NA" into a missing value (pandas by default) loses it. Read with `keep_default_na=False`.

Norway's exports to all partners, TWh a year (sums of the months written):

| Year | Natural gas | LNG (within it) |
|---|---|---|
| 2016 | 1,246 | 65 |
| 2017 | 1,335 | 57 |
| 2018 | 1,318 | 76 |
| 2019 | 1,215 | 57 |
| 2020 | 1,231 | 51 |
| 2021 | 1,206 | 2 |
| 2022 | 1,298 | 30 |
| 2023 | 1,242 | 64 |
| 2024 | 1,349 | 68 |
| 2025 | 1,310 | 46 |
| 2026, January to September | 913 | 47 |

In 2025 Norway's largest destinations were Germany 542.7 TWh, the United Kingdom 302.2, France 167.6, Belgium 165.7 and Denmark 99.9.

## Checks

Counted in session 2471 from the table in the main checkout (`C:\Users\Shared\Documents\erw\warehouse\output`), read past its 10 header lines with `keep_default_na=False` and every column as text, and from the saved answer, by scripts outside the repository. No request was made.

- The row, entity, partner and area counts above; no (entity, variable, ts_utc) twice; no blank value; every `retrieved_at` 2026-10-24T13:32:42Z; every `source_url` the address above.
- **The answer against the table:** 1,065,091 values less the United Kingdom's 6,069 and Kosovo's 9,240 is 1,049,782, the table's rows.
- **LNG never above natural gas:** for the same area, partner and month, both products have a row in 524,478 cases; LNG exceeds natural gas in **0** of them. 16 LNG rows have no natural gas row (all zero), and 810 natural gas rows have no LNG row.
- **Against the gas balance** (`eurostat_gas_balance_monthly`, entity `eurostat_gas_balance:<geo>`, variable `exports`, MWh): the table has 4,312 area-months of natural gas (G3000) exports to all partners, the balance 4,679 (it starts in 2015); 4,289 are in both.
  - Within 1 MWh in 4,247, within 1 percent in 4,277, as the report states.
  - The 12 outside 1 percent: Bulgaria, EA21, EU27_2020 and Spain 2 each; Austria, Czechia, Finland and Norway 1 each. The largest: **Norway in September 2026, 0 in this table against 103.2 TWh in the balance**; Bulgaria in October 2025, 0 against 17.77 TWh, the same 17.77 TWh gap in EU27_2020 and EA21 that month; Bulgaria in September 2026, 0 against 14.21 TWh; Austria in September 2026, 0 against 5.31 TWh.
- **Norway's exports by year:** the report's 1,246 (2016), 1,335 (2017), 1,231 (2020), 1,298 (2022), 1,349 (2024) and 1,310 (2025) TWh hold. Its "913 (2026 to September)" holds as a sum, but all 332 of Norway's rows for September 2026 are zero, so the 913 TWh is January to August; the balance has 103.2 TWh for that September. Neither the report nor the header names it.

## What it cannot say

- **The latest months:** a zero in the newest month may be a month not yet reported (Norway, Bulgaria and Austria in September 2026 against the balance); the table keeps Eurostat's figures as published.
- **The EU aggregate's exports in 2019 and 2020:** the answer has no value for its exports to all partners in either year, and no row at all in 2020.
- **Pipeline gas as such:** G3000 less G3200 is the non-LNG part, not computed here.
- **Quantities, not prices or values;** gross calorific value, not net.
- **The importer's side:** the partners' own record of these flows is in `eurostat_gas_imports_monthly` for the European importers; the two are not compared here.
- **How Eurostat assigns the partner country:** its metadata page for `nrg_te_gasm` would say; not read here.

## Acted on in session 2471

- **The report** (`SESSION_2469_REPORT.md`) carries a correction:
  - the retry came 128 seconds after the 413, not 100;
  - Norway's 913 TWh for 2026 is January to August, with September 2026 a published zero against 103.2 TWh in the balance;
  - Bulgaria's and Austria's zero months against the balance are named;
  - the EU aggregate has no total in 2019 and no row in 2020.
- **The connector and the header are not changed.** The zeros are Eurostat's as published, and the table makes no claim that they are complete.
