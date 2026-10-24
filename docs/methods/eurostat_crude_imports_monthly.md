# Eurostat's monthly crude oil imports by country of origin: 35 European countries and the EU, 173 partners, January 2016 to September 2026 (nrg_ti_oilm, crude oil)

Energy Research Warehouse (ERW), method note written in session 2424 (chain 115) for a table first written on 24 October 2026 (session 2369 of chain 110, `archive/sessions/SESSION_2369_REPORT.md`), after chain 110's notes session (2366). Eurostat's terms, the countries they allow and the shared country lists are described in `docs/methods/eurostat_renewable_capacity_annual.md` (session 2129). The same publisher's monthly oil balance, whose crude imports this table's partner totals are checked against, is `docs/methods/eurostat_oil_monthly.md`. EIA's crude imports by origin cover the United States only.

Tables: `eurostat_crude_imports_monthly`

## Publisher and address

Eurostat (Statistical Office of the European Union), "Oil and petroleum products imports - monthly data" (`nrg_ti_oilm`), page `https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_oilm/default/table`, through the statistics API without a key, as JSON-stat 2.0:

- `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_oilm?format=JSON&lang=EN&siec=O4100_TOT&sinceTimePeriod=2016-01`

The whole data set (every product) is too large for one extract: the SDMX query of session 2369 was answered HTTP 413 with 29.8 million rows against a limit of 5 million. Filtered to crude oil (`O4100_TOT`), the statistics API still answers asynchronously: its first answer is HTTP 413 "ASYNCHRONOUS_RESPONSE", and the same address asked again later answers with the data.

Source id `eurostat:nrg_ti_oilm_crude` (`sources.csv`: license public). The answer is 8,559,300 bytes (sha256 `a8bc9de7...`). Its dimensions are `freq, siec, partner, unit, geo, time` of sizes 1, 1, 174, 1, 39 and 129 (January 2016 to September 2026). It holds 571,013 values and 1,221 statuses, with "updated" 2026-10-23T23:00:00+0200.

Saved answer: `warehouse/raw/eurostat_crude_imports_monthly/nrg_ti_oilm_crude.json`, one file, written by session 2369's retry script (`runs/c110/s2369/retry.py`), not by the connector; the connector writes the same file when it fetches. ec.europa.eu's robots file, read in that session, disallows the old `/eurostat/SDMX/diss-web/rest/` path and the search pages, not `/eurostat/api/dissemination/`, and names no AI agent.

Connector: `warehouse/connectors/eurostat_crude_imports.py` (session 2369), `[--offline] [--out-dir DIR]`. Ceiling: the address asked at most 10 times, a minute apart, until it answers with the data (a JSON body beginning `{"version"`).
- **Kept:** the importing areas in `eurostat_res_capacity.KEPT`; every partner.
- **Values:** Eurostat's thousand tonnes times 1,000.
- **Stops:** dimensions other than the six named, a product other than crude oil, a unit other than THS_T, a frequency not monthly, a period not a month, a value that is not a number, or a key given twice.
- **Offline:** on `--offline` the saved answer is read, and `retrieved_at` is the file's modification time.

## Schedule and records

Schedule: none. No shell script under `warehouse/`, no workflow, no file in `scripts/` and not `warehouse/scheduled.py` names it.

Records:
- `runs/status/eurostat_crude_imports_monthly.json` holds the run by hand.
- `archive_manifest.csv`: 565,941 rows, run `20261024T095322Z-local`, `data_sha256` `69ca05e4...`.
- `coverage.csv`: sector oil, 173 nodes, validator pass, public.
- Release: listed as held in `docs/redivis/release-v1/tables.csv` (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).
- Live set: under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded.
- Not yet in the Stanford Redivis draft (`docs/reviews/redivis-v1-release-note-2026-10-23.md`, chain 110's section).
- Package: `package/src/erw/data/tables.csv` has its row since session 2370.

Readers: none. `tests/test_session2369.py` tests the connector on JSON-stat built in the test.

## Vintage and revision

One write, run `20261024T095301Z`, offline from the saved answer: 565,941 rows new, 0 replaced. `retrieved_at` is 2026-10-24T09:40:02Z in every row. `vintage` is blank; Eurostat's update time is on header line 4.

Eurostat flags 1,133 rows "p" (provisional): 2016 205, 2017 467, 2018 54, 2019 149, 2020 165, 2022 66, 2023 27, none since. By area the Netherlands 420, Germany 270, Sweden 255, Greece 74, Norway 39, Portugal 21. A revised month replaces the old figure on a later run; no earlier version is kept.

## Shape and variables

Series, 565,941 rows, 17 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_geo_code, x_partner, x_partner_name, x_flag`), 10 header lines.
- **`entity`:** `eurostat_crude_imp:<Eurostat geo code>:<partner code>`, 6,379 values.
- **`variable`:** `imports`; `unit` t; `freq` P1M.
- **`geo`:** the importing area's ISO alpha-2 code (Eurostat's EL written GR, 16,960 rows), blank for EU27_2020 and EA21 (23,183 rows).
- **`node`:** "Crude oil imports from <partner's English name>".
- **`market` and `vintage`:** blank.
- **Values:** every value is a whole number of tonnes, and 536,445 rows are zero.
  - Eurostat publishes a zero for most partners of most areas in most months, and the zeros are kept.
  - The largest value is the EU's imports from all partners in August 2018, 46,193,000 t.
- **Areas, 37:**
  - 35 countries (the 27 members, Norway, Albania, Georgia, Moldova, Montenegro, North Macedonia, Serbia and Turkiye) and the two aggregates;
  - the most rows: EU27_2020 18,157, Sweden 17,500;
  - the fewest: France 11,060, Moldova 10,010, Montenegro 7,326, EA21 5,026.
  - The United Kingdom is in the answer and left out by Eurostat's terms (5,072 values); Iceland is in the answer with no value.
- **Partners, 173:**
  - the countries of origin, and Eurostat's aggregates: `TOTAL`, `EU27_2020`, `EU28`, `EUR_OTH`, `AFR_OTH`, `AME_LAT`, `AME_OTH`, `ASI_NME`, `ASI_NME_OTH`, `ASI_OTH`, `EX_SU_OTH` (other countries of the former Soviet Union), `CN_X_HK` (China except Hong Kong) and `NSP` (not specified);
  - the answer's 174th partner, `EX_YU_OTH`, has no value in the areas kept.
- **A sum over partners double counts:** the aggregates overlap the countries.
- **Partner `NA` is Namibia:** a reader that turns "NA" into a missing value (pandas by default) loses it. Read with `keep_default_na=False`.

## Checks

From session 2369 (`archive/sessions/SESSION_2369_REPORT.md`):
- **Against the oil balance:** imports from all partners (`TOTAL`) equal `eurostat_oil_monthly`'s crude oil imports (`flow:IMP`, `O4100_TOT`) to the tonne in 4,161 of 4,196 area-months, and within 1 percent in 4,185.
- **The EU's crude imports from the United States,** Mt a year: 2.8 (2016), 12.0 (2018), 35.7 (2020), 49.3 (2022), 67.3 (2023), 69.6 (2024), 60.0 (2025).

Counted again in session 2424 from `warehouse/output` (`runs/c115/s2424/check_tables.py` and `crude_facts.out`):
- the row, entity, partner and area counts above;
- no key given twice;
- every value a number;
- every `retrieved_at` 2026-10-24T09:40:02Z;
- every `source_url` the address above.

The header's 173 partners, its "left out: UK", and its unit and geo rules agree with the table.

## What it cannot say

- **Crude oil only:** the other products of `nrg_ti_oilm` are not read, since the whole data set exceeds Eurostat's extraction limit.
- **Quantities, not prices.**
- **How Eurostat assigns the country of origin** is not read here; its metadata page for `nrg_ti_oilm` would say.
