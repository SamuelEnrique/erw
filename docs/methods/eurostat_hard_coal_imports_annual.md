# Eurostat's annual hard coal imports by country of origin: 39 European countries and two aggregates, 167 partners, 2010 to 2024 (nrg_ti_sff, hard coal)

Energy Research Warehouse (ERW), method note written in session 2429 (chain 115) for a table first written on 24 October 2026 (session 2426 of chain 115, `archive/sessions/SESSION_2426_REPORT.md`, commit `4602544b`). Eurostat's terms, the countries they allow and the shared country lists are described in `docs/methods/eurostat_renewable_capacity_annual.md` (session 2129). The same publisher's monthly solid fuels balance, whose hard coal imports this table's partner totals are checked against, is `docs/methods/eurostat_solid_fuels_monthly.md`; its crude oil imports by partner are `docs/methods/eurostat_crude_imports_monthly.md`. EIA's coal tables cover the United States only.

Tables: `eurostat_hard_coal_imports_annual`

## Publisher and address

Eurostat (Statistical Office of the European Union), "Solid fossil fuels imports" (`nrg_ti_sff`), page `https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_sff/default/table`, through the statistics API without a key, as JSON-stat 2.0:

- `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_sff?format=JSON&lang=EN&siec=C0100&sinceTimePeriod=2010`

Hard coal is Eurostat's SIEC `C0100`: anthracite, coking coal, other bituminous coal and sub-bituminous coal. Eurostat publishes solid fuel imports by partner a year only: its table of contents, read in session 2426 (`runs/license_reads/s2426/03_...`), lists `nrg_ti_sff` (imports) and `nrg_te_sff` (exports), both 1990 to 2024, updated 09.10.2026, and no monthly set; the guessed monthly code `nrg_ti_sffm` was answered HTTP 404, "not available for dissemination".

Source id `eurostat:nrg_ti_sff_c0100` (`sources.csv`: license public, first and last seen 2026-10-24). The answer was given at once (HTTP 200, no asynchronous step). It is 1,454,579 bytes (sha256 `4b9cfd1b...`). Its dimensions are `freq, siec, partner, unit, geo, time` of sizes 1, 1, 167, 1, 43 and 15 (2010 to 2024), with freq `A`, siec `C0100` and unit `THS_T` only. It holds 103,415 values and no status at all (the answer has no `status` member), with label "Solid fossil fuels imports" and "updated" 2026-10-09T23:00:00+0200.

Saved answer: `warehouse/raw/eurostat_hard_coal_imports_annual/nrg_ti_sff_c0100.json`, one file. Its bytes are session 2426's probe request 4 (`runs/c115/s2426/probe.csv`, at 2026-10-24T11:22:52Z, the same sha256, and the same bytes kept as `runs/license_reads/s2426/04_...bin`), and its modification time is that request's second, 11:22:52Z. It was not fetched by the connector; the step that put it in `warehouse/raw` is not recorded in `runs/c115/s2426/` (`runs/c115/seed_raw.py` writes to a `_probe` folder, which this folder does not have). ec.europa.eu's robots file, read in that session (sha256 `fc082fc2...`, the same as session 2369's), disallows the old `/eurostat/SDMX/diss-web/rest/` path and the search pages, not `/eurostat/api/dissemination/`, and names no AI agent.

Session 2426 made 4 requests of 20: the robots file, `nrg_ti_sffm` (404), the table of contents (1,975,318 bytes) and `nrg_ti_sff` (1,454,579 bytes). The trial and the write ran offline.

Connector: `warehouse/connectors/eurostat_coal_imports.py` (session 2426), `[--offline] [--out-dir DIR]`. Ceiling: the address asked at most 10 times, a minute apart, until it answers with the data (a JSON body beginning `{"version"`).
- **Kept:** the importing areas in `eurostat_res_capacity.KEPT`; every partner.
- **Values:** Eurostat's thousand tonnes times 1,000, rounded to 0.001 t.
- **Stops:** dimensions other than the six named, a product other than `C0100`, a unit other than THS_T, a frequency not annual, a period not a year, a value that is not a number, or a key given twice.
- **Offline:** on `--offline` the saved answer is read, and `retrieved_at` is the file's modification time.

## Schedule and records

Schedule: none. No shell script under `warehouse/`, no workflow in `.github/workflows/`, no file in `scripts/` and not `warehouse/scheduled.py` names it.

Records:
- `runs/status/eurostat_hard_coal_imports_annual.json` holds the run by hand: run `20261024T112444Z`, ok, "99288 rows". `run_status.csv`: no row.
- `archive_manifest.csv`: 99,288 rows, run `20261024T112451Z-local`, archived 2026-10-24T11:24:51Z, `data_sha256` `528355a7...`.
- `coverage.csv`: sector coal (`build_coverage.py`'s rule of session 2426), 167 nodes (the partners), P1Y, 2010-01-01 to 2024-01-01, last run 2026-10-24T11:24:44Z, validator pass, public, tier source.
- License: `license_tables.csv`, Eurostat, "the source registry"; `docs/licenses.md`, verdict "may be public", flag public, "agrees", ERW verdict public.
- Release: listed as held in `docs/redivis/release-v1/tables.csv` (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`); `variables.csv` has its one variable, `imports`, unit t.
- Live set: under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded.
- Not yet in the Stanford Redivis draft: no row in `redivis_uploads.csv` or `redivis_uploads_stanford.csv`.
- Package and site: rows in `package/src/erw/data/tables.csv`, `site/data/table_citations.json` and `site/data/table_verdicts.json` since session 2431.

Readers: none. `tests/test_session2426.py` (3 tests) tests the connector on JSON-stat built in the test.

The write (`runs/c115/s2426/write.out`): connector, validator, coverage and archive exit 0; "metadata to the branch exit=1", the patch conflict the report names, after which `runs/c102/add_own_rows.py` put in one row each.

## Vintage and revision

One write, run `20261024T112444Z`, offline from the saved answer; header line 10: "This run wrote 99288 rows: 99288 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs." `retrieved_at` is 2026-10-24T11:22:52Z in every row, the saved file's modification time and the probe's fetch. `vintage` is blank in every row; Eurostat's update time, 2026-10-09T23:00:00+0200, is on header line 4.

No row carries a flag: the answer has no statuses. A revised year replaces the old figure on a later run; no earlier version is kept.

## Shape and variables

Series, 99,288 rows, 17 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_geo_code, x_partner, x_partner_name, x_flag`), 10 header lines.
- **`entity`:** `eurostat_coal_imp:<Eurostat geo code>:<partner code>`, 6,845 values.
- **`variable`:** `imports`; `unit` t; `freq` P1Y; `ts_utc` the year's 1 January, 15 years, 2010 to 2024.
- **`geo`:** the importing area's ISO alpha-2 code (Eurostat's EL written GR, 2,477 rows), blank for EU27_2020 and EA21 (5,010 rows).
- **`node`:** "Hard coal imports from <partner's English name>".
- **`market`, `vintage` and `x_flag`:** blank in every row.
- **Values:** every value is a whole number of tonnes, none negative, and 93,045 rows are zero (6,243 are not).
  - Eurostat publishes a zero for most partners of most areas in most years, and the zeros are kept.
  - The largest value is the EU's imports from all partners in 2011, 175,699,086 t.
- **Areas, 41:**
  - 39 countries: the 27 members, Iceland, Liechtenstein, Norway, Albania, Bosnia and Herzegovina, Georgia, Moldova, Montenegro, North Macedonia, Serbia, Turkiye and Ukraine; and the two aggregates EU27_2020 and EA21;
  - most areas have 2,477 rows (all 15 years); EU27_2020, EA21, Ireland, Romania and Sweden 2,505;
  - the fewest: Georgia 1,982 (2013 to 2024), Bosnia and Herzegovina and Liechtenstein 1,817 (2014 to 2024), Ukraine 1,815 (2010 to 2020).
  - The United Kingdom (1,650 values) and Kosovo (2,477 values) are in the answer and left out by Eurostat's terms (header line 3: "UK XK").
- **Partners, 167, in every year:**
  - 159 countries of origin, and 8 of Eurostat's aggregates: `TOTAL`, `NSP` (not specified), `AFR_OTH`, `AME_OTH`, `ASI_NME_OTH`, `ASI_OTH`, `EUR_OTH` and `EX_SU_OTH` (other countries of the former Soviet Union);
  - 82 countries of origin have a value above zero somewhere.
- **A sum over partners double counts:** `TOTAL` and the "other" groups sit beside the countries.
- **Partner `NA` is Namibia** (600 rows): a reader that turns "NA" into a missing value (pandas by default) loses it. Read with `keep_default_na=False`.

## Checks

From session 2426 (`archive/sessions/SESSION_2426_REPORT.md`), each counted again in session 2429 from `warehouse/output` in the main checkout, read past its 10 header lines with `keep_default_na=False` and every column as text, and from the saved answer. No request was made.

- **Against the answer:** the 99,288 values of the 41 areas kept and the table's rows are the same keys, none on one side only; every value is the answer's thousand tonnes times 1,000 (largest difference 7e-9 t). 103,415 values less the United Kingdom's 1,650 and Kosovo's 2,477 is 99,288.
- **Table:** no (entity, variable, ts_utc) twice; every `entity` and `node` built from the `x_` columns; one `retrieved_at` and one `source_url`, the address above.
- **The EU against its members:** the EU's imports from all partners equal the sum of the 27 members' within 1 t in all 15 years.
- **Against the monthly balance** (`eurostat_solid_fuels_monthly`, entity `eurostat_sff:<geo>:C0100`, variable `flow:IMP`, twelve months summed): 321 country-years have all twelve months and an annual figure (38 areas, 2016 to 2024; Bosnia and Herzegovina's 2017 and 2018, with 8 and 5 months, are left out). Of the 321, 37 agree to the tonne, 102 within 1,000 t, 133 within 1 percent of the annual figure (134 of the monthly sum), and 147 within 1,000 t or 1 percent of the annual figure; the median gap is 2.1 percent of the monthly sum. The largest gaps: the Netherlands in 2016 (16.35 Mt annual against 42.38 Mt monthly, 61 percent under), Germany in 2016 to 2019 (17 to 30 percent over). For the EU, the annual figure against the monthly sum, Mt:

  | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
  |---|---|---|---|---|---|---|---|---|
  | 160.3 / 172.3 (-7.0%) | 163.5 / 154.5 (+5.9%) | 154.4 / 149.0 (+3.6%) | 125.4 / 122.0 (+2.8%) | 87.7 / 88.8 (-1.2%) | 104.1 / 105.7 (-1.5%) | 126.7 / 126.2 (+0.4%) | 92.4 / 92.9 (-0.6%) | 67.7 / 68.6 (-1.4%) |

  Eurostat's annual and monthly collections are separate; neither table is corrected.
- **The EU's hard coal imports,** Mt a year:

  | | 2010 | 2012 | 2018 | 2020 | 2022 | 2023 | 2024 |
  |---|---|---|---|---|---|---|---|
  | All partners | 164.5 | 174.8 | 154.4 | 87.7 | 126.7 | 92.4 | 67.7 |
  | From the United States | 25.2 | 36.1 | 26.7 | 13.4 | 20.9 | 20.3 | 17.1 |
  | From Russia | 36.8 | 35.3 | 61.0 | 43.1 | 27.2 | 0.8 | 0.2 |

  From the United States the high is 36.1 Mt (2012) and the low 13.4 Mt (2020). In 2024 the EU's largest origins were Australia 19.2 Mt, the United States 17.1, Colombia 8.8, Kazakhstan 5.0, Poland 4.1 and South Africa 4.0.

When this note was drafted, the description and the data disagreed here; each is acted on below:
1. **"147 within 1 percent."** The report's 147 is the count within 1,000 t or within 1 percent of the annual figure. Within 1 percent alone it is 133 (134 against the monthly sum).
2. **"Within 2 percent from 2019."** The report says the EU's annual figure is within 2 percent of the monthly sum from 2019. In 2019 it is 2.8 percent over (125.4 against 122.0 Mt); it is within 2 percent from 2020.
3. **The United States in 2010.** The report gives 25.3 Mt; the table holds 25,247,655 t, 25.2 Mt to one decimal.
4. **"TOTAL, the EU, extra-EU and the like."** The docstring and header line 3 name the EU and extra-EU among the partner aggregates. The answer has neither: its 8 aggregates are `TOTAL`, `NSP` and six "other" groups. (The EU and the euro area are importing areas, not partners.)
5. **The release package's reason.** `docs/redivis/release-v1/tables.csv` gives the held reason "written 21 October 2026, session 489", the shared `STORAGE_HELD` text; this table was written on 24 October 2026 by session 2426.

The header's 39 countries, 167 partners, "left out: UK XK", "zeros kept" and its unit and geo rules agree with the table.

## What it cannot say

- **Hard coal only:** lignite, coke, peat and the other solid fuels of `nrg_ti_sff` are not read; nor are exports (`nrg_te_sff`).
- **A year only,** from 2010: Eurostat has no monthly imports by partner, and the years 1990 to 2009 are not read. Months come from the balance (`eurostat_solid_fuels_monthly`), without partners.
- **Quantities, not prices** or qualities.
- **Not the United Kingdom or Kosovo** (Eurostat's terms).
- **How Eurostat assigns the country of origin,** and why its annual and monthly imports differ, are not read here; its metadata page for `nrg_ti_sff` would say.

## Acted on in session 2429

The two helpers who drafted this chain's notes made no request and changed no other file; every point was read and acted on or recorded:

- **Items 1 to 3:** session 2426's report is corrected, saying so: 102 within 1,000 t and 133 within 1 percent (147 either); the EU within 2 percent from 2020 (2019: 2.8 percent over); the United States in 2010, 25.2 Mt.
- **Item 4:** the connector's docstring and header now name the partner aggregates read from the answer (`AFR_OTH, AME_OTH, ASI_NME_OTH, ASI_OTH, EUR_OTH, EX_SU_OTH, NSP, TOTAL`), say what `TOTAL` and `NSP` are, and that `TOTAL` and every group whose code does not end in `_OTH` overlap the named countries. The table was written again offline (run `20261024T115231Z`): the same 99,288 rows (0 new, 99,288 replacing the same), its metadata rows replaced by key; only the header changed, and the archive's data hash is the same (`528355a7...`).
- **Item 5:** the release package's held reason is `release_v1.py`'s one text for every table in `STORAGE_HELD`, written for session 489's tables; it is not this table's date. Left as it is: changing it would change every held table's reason, a code session's work. Named in the chain's note.
