# Eurostat's monthly oil supply: crude oil and six oil products, every flow of the monthly balance, 35 European countries and the EU, January 2016 to September 2026 (nrg_cb_oilm)

Energy Research Warehouse (ERW), method note written in session 2366 (chain 110) for a table first written on 24 October 2026 (session 2363 of chain 110, `archive/sessions/SESSION_2363_REPORT.md`, commit `50bd40ca`). Eurostat's terms, the countries they allow and the shared country lists are described in `docs/methods/eurostat_renewable_capacity_annual.md` (session 2129); the same publisher's monthly gas balance, built the same way, is `docs/methods/eurostat_gas_balance_monthly.md`, and its coal is `docs/methods/eurostat_solid_fuels_monthly.md`. EIA's petroleum tables cover the United States only.

Tables: `eurostat_oil_monthly`

## Publisher and address

Eurostat (Statistical Office of the European Union), "Supply and transformation of oil and petroleum products - monthly data" (`nrg_cb_oilm`), page `https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_oilm/default/table`, through the SDMX 2.1 dissemination API without a key. The extract is too large to be answered at once: the query is answered with a job key, and the job's status and then its data are asked by GET from Eurostat's asynchronous API:

- `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_oilm?format=SDMX-CSV&compressed=false&startPeriod=2016-01`
- `https://ec.europa.eu/eurostat/api/dissemination/1.0/async/status/<key>`, then `.../async/data/<key>`

Source id `eurostat:nrg_cb_oilm` (`sources.csv`: license public, first and last seen 2026-10-24). The answer is SDMX-CSV with the columns `DATAFLOW, LAST UPDATE, freq, nrg_bal, siec, unit, geo, TIME_PERIOD, OBS_VALUE, OBS_FLAG, CONF_STATUS`: 1,868,146 lines, 156,280,458 bytes, 33 products, 26 balance items, unit THS_T (thousand tonnes) and frequency M on every line, periods 2016-01 to 2026-09, "LAST UPDATE" 23/10/26 23:00:00 on every line. It holds 37 areas: the 27 members, Norway, seven candidates (Albania, Georgia, Moldova, Montenegro, North Macedonia, Serbia, Turkiye written TR), EU27_2020 and the United Kingdom. There is no line for Bosnia and Herzegovina, Ukraine, Switzerland, Iceland, Liechtenstein, Kosovo or a euro area aggregate.

Saved extract: `warehouse/raw/eurostat_oil_monthly/nrg_cb_oilm_async.bin`, one file, with no run folder and no manifest. It was fetched by session 2363's own script (`runs/c110/s2363/async_get.py`; `async.csv` records the data at 2026-10-24T08:51:53Z, 156,280,458 bytes, sha256 `2b666926...`, which the saved file matches), not by the connector; the same bytes are in `runs/license_reads/s2363/08_async_data_nrg_cb_oilm.bin`. ec.europa.eu's robots file read in that session (`runs/license_reads/s2363/03_...`) has the sha256 `fc082fc2...` of reads 278, 351, 383 and 583 in `license_reads.csv`: it disallows the old `/eurostat/SDMX/diss-web/rest/` path and the search pages, not `/eurostat/api/dissemination/`.

Connector: `warehouse/connectors/eurostat_oil_monthly.py` (session 2363), `[--offline] [--out-dir DIR]`. Ceiling: one query, its status asked at most 20 times a minute apart, its data once. Kept: the areas in `eurostat_res_capacity.KEPT` (the EU, EFTA, the official candidates and Eurostat's aggregates) and seven of the 33 products; each value is Eurostat's thousand tonnes times 1,000, rounded to 0.001 t. A header not Eurostat's, a unit other than THS_T, a frequency not monthly, a flow not among the 26 named, a period not a month, a value that is not a number or a key given twice stops the run. On `--offline` the saved extract is read and `retrieved_at` is the file's modification time. A later run merges by (entity, variable, ts_utc).

Schedule: none. No shell script under `warehouse/`, no workflow in `.github/workflows/`, no file in `scripts/` and not `warehouse/scheduled.py` names it. `run_status.csv`: no row (the run by hand wrote `runs/status/eurostat_oil_monthly.json`: run `20261024T085433Z`, ok, "457009 rows"). `archive_manifest.csv`: 457,009 rows, run `20261024T085452Z-local`, `data_sha256` `2810cccf...`, the hash of the file on this machine. `redivis_uploads.csv` and `redivis_uploads_stanford.csv`: no row; `docs/redivis/release-v1/tables.csv` lists it as held (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`). Live set: listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded. `coverage.csv`: sector oil, 143 nodes, validator pass. Readers: none; `tests/test_session2363.py` tests the connector on SDMX-CSV built in the test. `package/src/erw/data/tables.csv`, `site/data/table_citations.json` and `site/data/table_verdicts.json` have no row for it.

## Vintage and revision

One write, run `20261024T085433Z`, offline from the saved extract; header line 10: "This run wrote 457009 rows: 457009 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs." `retrieved_at` is 2026-10-24T08:51:54Z in every row, the saved file's modification time (the fetch itself is logged at 08:51:53Z). `vintage` is blank in every row; Eurostat's "LAST UPDATE" 23/10/26 23:00:00 is on header line 4, with no time zone.

Eurostat flags 6,712 rows "p" (provisional) and 9 "e" (estimated: Croatia's international aviation of jet fuel, March and May to December 2025). The provisional rows are not the newest months: they fall in 2016 to 2019, September 2020, March 2022 to February 2023, June and July 2023, and 2025 (32 to 34 a month to August 2025, then 1 a month), none in 2026; by area the Netherlands 2,267, Germany 847, Sweden 817, Norway 783 and Greece 559. A revised month replaces the old figure on a later run; no earlier version is kept.

## Shape and variables

Series, 457,009 rows, 18 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_geo_code, x_siec, x_nrg_bal, x_flag, x_conf_status`), 10 header lines. `entity` `eurostat_oil:<Eurostat geo code>:<SIEC code>`, 252 (36 areas, seven products); `variable` `flow:<NRG_BAL code>`, 26; `unit` t; `freq` P1M; `geo` the ISO alpha-2 code (Eurostat's EL written GR, 13,377 rows), blank for EU27_2020 (14,959 rows); `node` "<product>: <flow>", 143 values (the product-flow pairs held, as `coverage.csv` says); `market` and `vintage` blank; `x_conf_status` blank in every row (the 90 cells marked C have no value and no row). Every value is a whole number of tonnes. 235,919 rows are zero.

| Product | SIEC | Rows |
|---|---|---|
| Crude oil | O4100_TOT | 59,514 |
| Oil products (all) | O4600 | 66,182 |
| Motor gasoline, without its biofuel portion | O4652XR5210B | 64,099 |
| Gas oil and diesel oil, without its biofuel portion | O4671XR5220B | 66,913 |
| Kerosene-type jet fuel, without its biofuel portion | O4661XR5230B | 67,578 |
| Fuel oil | O4680 | 64,681 |
| Liquefied petroleum gases | O4630 | 68,042 |

Flows by product (rows):

| Flow | Crude | O4600 | Gasoline | Diesel | Jet | Fuel oil | LPG |
|---|---|---|---|---|---|---|---|
| IMP imports | 4,199 | 4,315 | 4,301 | 4,315 | 4,192 | 4,267 | 4,300 |
| EXP exports | 4,057 | 4,297 | 4,246 | 4,258 | 4,126 | 4,245 | 4,220 |
| IPRD indigenous production | 4,176 | 0 | 0 | 0 | 0 | 0 | 0 |
| TOS transfer from other sources | 378 | 0 | 0 | 0 | 0 | 0 | 0 |
| DU direct use | 3,894 | 0 | 0 | 0 | 0 | 0 | 0 |
| RI_OBS, RI_CAL refinery intake observed, calculated | 4,230, 2,788 | 0 | 0 | 0 | 0 | 0 | 0 |
| RL refinery losses | 4,180 | 0 | 0 | 0 | 0 | 0 | 0 |
| TO_RPI_RO refinery output | 270 | 4,228 | 4,205 | 4,210 | 4,162 | 4,225 | 4,191 |
| RF refinery fuel | 342 | 4,209 | 3,894 | 3,940 | 3,909 | 4,083 | 4,028 |
| PPR primary product receipts | 3,933 | 4,239 | 3,971 | 3,925 | 3,889 | 3,933 | 3,927 |
| RCV_RCY recovered and recycled | 342 | 4,023 | 3,891 | 3,898 | 3,899 | 3,949 | 3,889 |
| BKFLOW backflows | 434 | 4,113 | 3,952 | 3,957 | 3,904 | 3,954 | 4,021 |
| IT interproduct transfers | 3,928 | 3,958 | 3,979 | 4,031 | 3,989 | 4,023 | 3,975 |
| PT products transferred | 805 | 4,139 | 3,986 | 4,063 | 3,964 | 4,057 | 3,996 |
| STK_CHG change in stock | 4,223 | 4,312 | 4,294 | 4,312 | 4,270 | 4,263 | 4,252 |
| GID_OBS, GID_CAL gross inland deliveries observed, calculated | 3,890, 2,486 | 4,309, 2,868 | 4,309, 4,315 | 4,309, 4,315 | 4,300, 4,308 | 4,267, 4,266 | 4,296, 4,303 |
| STATDIFF statistical differences | 2,485 | 2,714 | 2,687 | 2,703 | 2,669 | 2,671 | 2,654 |
| INTMARB international maritime bunkers | 342 | 4,199 | 3,899 | 4,177 | 3,900 | 4,172 | 3,899 |
| INTAVI_E international aviation | 270 | 0 | 270 | 270 | 4,219 | 289 | 274 |
| FC_TRA_ROAD_E road transport | 270 | 0 | 271 | 270 | 270 | 286 | 4,064 |
| FC_TRA_RAIL_DNAVI_E rail and domestic navigation | 270 | 0 | 270 | 2,529 | 276 | 287 | 273 |
| GD_PI deliveries to the petrochemical industry | 3,922 | 4,146 | 3,967 | 4,008 | 3,940 | 3,977 | 4,077 |
| TI_EHG_MAP input to main power and heat producers | 3,130 | 3,251 | 3,122 | 3,153 | 3,122 | 3,183 | 3,133 |
| ND_TP net deliveries of total products | 270 | 2,862 | 270 | 270 | 270 | 284 | 270 |

- **Areas and months.** 35 countries and EU27_2020. The first month is 2016-01 for 31 areas, 2018-01 for Albania, 2020-01 for Moldova and Serbia, 2020-07 for Georgia, 2023-01 for Montenegro. The last month is 2026-06 for Greece and EU27_2020; 2026-07 for 21 areas; 2026-08 for Austria, Belgium, Bulgaria, Cyprus, Czechia, Germany, Estonia, Georgia, Croatia, Moldova and Montenegro; 2026-09 only for Denmark and Finland (232 rows).
- **2020 is thin.** Rows a year: 38,316 (2016), 38,316, 39,417, 37,798, 26,026 (2020), 47,792, 45,786, 46,962, 51,004, 55,101 and 30,491 (2026, to September). A month has about 3,100 to 3,200 rows in late 2019, 2,070 to 2,480 in 2020 and about 4,000 from January 2021: in 2020 most areas give a part of the flows (Albania 4 rows a month from January to November).
- **O4600 holds the others.** Over the 4,247 area-months where all six have observed deliveries, the five products named are a median 0.835 of oil products in all (10th percentile 0.723, 90th 0.951), above 1 in 2. The EU's observed deliveries in 2024: oil products 461.7 Mt, gas oil and diesel 216.8, gasoline 73.5, jet fuel 46.2, LPG 25.4, fuel oil 7.8.
- **Crude oil's deliveries are mostly zero.** 3,821 of 3,890 GID_OBS rows of crude oil are 0; the rest are Moldova's (33), Denmark's (18), the EU's (17) and one of Serbia's.
- **The EU's crude oil imports**, Mt a year: 505.9 (2016), 523.0, 512.8, 507.8, 440.0 (2020), 446.4, 479.2, 471.8, 469.2 (2024), 454.9 (2025), 225.0 for January to June 2026. The 2020 figure lacks six or seven members (below).
- **The largest value** is the EU's refinery output of oil products in August 2018, 52,091,000 t.

**The stock change is a stock build.** Crude oil: calculated refinery intake equals indigenous production + transfers from other sources + imports - exports + backflows - direct use - STK_CHG within 1 t in 2,558 of 2,574 area-months that give all of them (with + STK_CHG, 598). Products: calculated deliveries equal primary product receipts + refinery output + recovered products + imports - exports - bunkers + interproduct transfers - products transferred - refinery fuel - STK_CHG within 1 t in every area-month for gasoline (4,171), diesel (4,204), jet fuel (4,027), fuel oil (4,151) and LPG (4,152), and in 2,761 of 2,777 for oil products in all. A positive STK_CHG is oil put into stock, as in the gas balance (`eurostat_gas_balance_monthly`); in Eurostat's monthly coal it is the other way round (`eurostat_solid_fuels_monthly`).

**Observed and calculated deliveries differ, by the statistical difference.** GID_OBS is what the country observes delivered to its market; GID_CAL is the balance above. Where both are given:

| Product | OBS rows | CAL rows | Both | Equal (0.5 t) | CAL above | CAL below | Within 1 percent | STATDIFF = CAL - OBS |
|---|---|---|---|---|---|---|---|---|
| Crude oil | 3,890 | 2,486 | 2,426 | 2,421 | 4 | 1 | (mostly zero) | 2,426 of 2,426 |
| Oil products | 4,309 | 2,868 | 2,862 | 1,006 | 899 | 957 | 1,770 | 2,682 of 2,708 |
| Gasoline | 4,309 | 4,315 | 4,309 | 1,969 | 1,217 | 1,123 | 2,492 | 2,665 of 2,681 |
| Diesel | 4,309 | 4,315 | 4,309 | 1,794 | 1,193 | 1,322 | 2,604 | 2,681 of 2,697 |
| Jet fuel | 4,300 | 4,308 | 4,299 | 2,221 | 1,184 | 894 | 2,757 | 2,644 of 2,659 |
| Fuel oil | 4,267 | 4,266 | 4,256 | 2,191 | 1,133 | 932 | 1,820 | 2,634 of 2,650 |
| LPG | 4,296 | 4,303 | 4,296 | 2,290 | 991 | 1,015 | 2,543 | 2,630 of 2,647 |

The difference runs both ways, with a median of 0.18 to 0.40 percent of observed deliveries for gasoline, diesel, oil products and fuel oil (0 for jet fuel and LPG). Over a year it nearly cancels for the EU: diesel 216.8 Mt observed against 215.7 calculated in 2024, oil products 461.7 against 463.3. It is large for small or exporting areas: the sum of the gaps over the sum of observed deliveries of oil products is 0.70 for Norway, 0.45 for Georgia, 0.37 for Finland and 0.28 for Lithuania. Two cautions: calculated deliveries of oil products in all begin in January 2020 for 22 areas (2018-09 to 2019-12 for 11 others, 2020-07, 2020-12 and 2023-01 for three), so the EU's O4600 GID_CAL from September 2018 to December 2019 is the sum of the few areas that give it (0.55 Mt a month in late 2018 and 10 to 17.5 Mt in 2019, against 40 to 45 Mt observed); and crude oil's STATDIFF is the deliveries' difference, not the refinery intake's (STATDIFF equals RI_CAL - RI_OBS in 1,216 of 2,480 area-months, mostly where both are 0).

**Negative values.** 21,073 rows:

| Flow | Rows | Expected | Where, and the lowest |
|---|---|---|---|
| STK_CHG | 13,346 | yes, a draw from stock | every product; lowest the EU's oil products, June 2021, -4,209,062 t |
| STATDIFF | 4,661 | yes | the products (943 for O4600), 1 for crude oil; lowest Norway's oil products, January 2020, -23,830,282 t |
| IT | 2,697 | yes, a product passed to another | every product; lowest the Netherlands' fuel oil, January 2017, -916,000 t |
| GID_CAL | 271 | follows from the balance | Norway 102, Lithuania 60, Sweden 43, Denmark 24, the Netherlands 21, others 21; lowest Norway's oil products, January 2020, -23,152,444 t |
| RL | 38 | a refinery gain, uncommon | crude oil: Germany 11, the Netherlands 10, Norway 7, Denmark 6, Bulgaria 2, the EU 2; lowest Germany, June 2025, -1,368,176 t |
| GID_OBS | 23 | no | Denmark's crude oil in 9 months (2016-03 to 2025-08, -2,000 to -85,000 t) and the EU's same 9, Norway's LPG in 5 |
| RI_CAL | 21 | follows from the balance | Finland 11, Albania 6, Norway 4; lowest Norway, May 2024, -464,225 t |
| DU, PPR | 5, 5 | no | Denmark's crude oil, lowest -10,000 t (July 2025) |
| GD_PI | 3 | no | Germany 2, the Netherlands 1; lowest -6,662 t |
| INTMARB | 2 | no | Norway, lowest -2,389 t |
| RF | 1 | no | the Netherlands' LPG, May 2016, -2,000 t |

Norway's oil products in January 2020 are the outlier: observed deliveries 677,838 t, a stock change of 24,326,348 t, calculated deliveries -23,152,444 t and a statistical difference of -23,830,282 t, with no calculated deliveries of O4600 in the three months before; its observed deliveries run from 636,000 to 929,000 t a month from October 2019 to April 2020. Lithuania's gasoline has negative calculated deliveries in every month from August 2025 to July 2026 (-138,400 to -269,100 t). These are Eurostat's figures as printed; nothing here corrects them.

## Placing values in time, and what is filled

`ts_utc` is the month's first day at 00:00:00Z (Eurostat's TIME_PERIOD, YYYY-MM), a label for the month, not an instant: 129 months, January 2016 to September 2026. Of the extract's 457,099 lines for the areas and products kept, 90 have no value (all marked C, confidential); they have no row. Zeros are kept as Eurostat prints them. Not taken: the United Kingdom's 5,648 lines of the seven products (22,476 lines in all), by Eurostat's terms, and the other 26 products' 1,388,571 lines for the areas kept. Nothing is filled: a month an area does not report has no row, and the EU27_2020 row of such a month is the sum of the members that do report (Checks).

## License

Header line 9: "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_cb_oilm. Eurostat bears no responsibility for this reshaping (the rows filtered by country and product and renamed, the values unchanged but for the thousand tonnes written as tonnes)." `warehouse/metadata/license_verdicts.csv`: Eurostat (Statistical Office of the European Union), read 280 (session 2123): "Reuse of statistical data, metadata, publications, and other dissemination tools published on this website for commercial or non-commercial purposes is authorised provided the source is acknowledged. [...] [Not for commercial reuse:] Data for countries other than: Member States of the European Union (EU) Member States of the European Free Trade Association (EFTA) official EU acceding and candidate countries.", verdict "may be public", if the ERW sells anything "may be public". `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", if the ERW sells anything "may be public", ERW verdict public; it is in the list "Public now". `license_tables.csv`: Eurostat, "the source registry". No row in `license_status.csv`. The United Kingdom is the one area of the extract left out under those terms.

## Checks (session 2366)

The figures in this note were computed from the rows of `warehouse/output/eurostat_oil_monthly.csv` in the main checkout, read past its 10 header lines (counted, never parsed as comments) with only the columns needed, and from the saved extract read in chunks, by `runs/c110/s2366/check_eurostat_oil_monthly.py`, `check_eurostat_oil_monthly_2.py` and `check_eurostat_oil_monthly_3.py` (outputs beside them, `.out`). No request was made.

- 457,009 rows and 2016-01-01 to 2026-09-01, as header line 10 states; no (entity, variable, ts_utc) twice; no blank value; every `ts_utc` a month's first day at midnight; `entity` and `variable` built from the `x_` columns in every row; the file's data hash is the archive manifest's.
- **Against the extract:** the 457,009 lines with a value for the areas and products kept and the table's rows are the same keys, none on one side only; every table value is the extract's thousand tonnes times 1,000 (largest difference 4e-9 t), and every flag and confidentiality status is the extract's. Ten rows drawn at random, for example: Spain's jet fuel, calculated deliveries, November 2019, 496.000 kt and 496000.0 t; the Netherlands' diesel refinery output, April 2023, 1801.177 kt and 1801177.0 t; the EU's fuel oil statistical difference, October 2020, 59.197 kt and 59197.0 t; Slovakia's jet fuel observed deliveries, April 2023, 2.547 kt and 2547.0 t. Kept: the 35 countries and EU27_2020; left out: the United Kingdom only.
- **The EU against its members.** Crude oil imports: the EU has a row in 126 months (2016-01 to 2026-06; none for July to September 2026). In all 126 it equals the sum of the members that have a row, to the tonne. All 27 have a row in 107 of them; in the other 19 one to seven are missing: Estonia in December 2019; Cyprus, Estonia, Luxembourg, Latvia, Malta and Slovenia through 2020, and Croatia as well in November and December 2020; Finland from March to August 2025. Over every product and flow, all 14,959 EU rows equal the sum of the members present within 0.5 t: 10,124 with all 27 and 4,835 with fewer.
- **Observed and calculated deliveries, the stock change, the negatives:** as above.

## Where the description and the data disagree

1. **"Summed over the 27 members."** `SESSION_2363_REPORT.md`: "crude oil imports summed over the 27 members equal Eurostat's EU27 figure in all 126 months." All 27 members have a row in 107 of the 126 months. In the other 19, the EU figure equals the sum of the members that report, so it leaves out up to seven members (six or seven through 2020).
2. **EU27_2020 as the EU's total.** The docstring and header line 2 call EU27_2020 "Eurostat's aggregate", and the report checks it against the 27 members. In this data set it is, in every row, the sum of the members that report that cell. In 4,835 rows that is fewer than 27. The EU's calculated deliveries of oil products from September 2018 to December 2019 add up the few members that give them (one in late 2018, three in June 2019), 0.55 to 17.5 Mt a month against 40 to 45 Mt observed.
3. **"The extract retrieved 2026-10-24T08:51:54Z."** Header line 4 and every `retrieved_at` give the saved file's modification time. Session 2363's own script fetched the extract at 08:51:53Z (`runs/c110/s2363/async.csv`); the connector made no request. With no manifest beside the file, copying or touching it would change every row's `retrieved_at` on the next offline run.
4. **The write's failure is not in the report.** `runs/c110/s2363/write.out` ends "metadata to the branch exit=1" and "done, fail=1". The report's "Errors" names only the first trial's `vintage`. The metadata rows reached main in commit `50bd40ca` all the same.

Not acted on: this note changes no file but itself.

## The session report against the table

`SESSION_2363_REPORT.md`, checked against the table, the saved extract and the run records: "457,009 figures, public": holds. "January 2016 to September 2026, 35 European countries and the EU27 aggregate": holds as a range, though only Denmark and Finland reach September 2026 and the EU ends in June. "Products, seven of the file's 33": holds. "Flows: every one the file gives, 26 balance items": holds (143 product-flow pairs). "Unit: t, Eurostat's thousand tonnes times 1,000": holds to the tonne. "The United Kingdom is left out by Eurostat's terms ... and named in the header": holds (header line 3: "UK"). "vintage is empty. Eurostat's LAST UPDATE is printed as 23/10/26 23:00:00, its clock unstated, so it goes in the header instead": holds. "Members against the EU ... in all 126 months": equal in all 126, all 27 present in 107 (disagreement 1). "The EU imported 469.2 Mt of crude oil in 2024": holds. "its data, once (156 MB)": 156,280,458 bytes. "8 requests of 20": `runs/license_reads/s2363/` holds 7 answers (01 to 06 and 08; the second status answer, 07, is not saved), and `async.csv` and `probe.csv` record the status asked twice. "Not in the Stanford draft yet": still so (no row in `redivis_uploads_stanford.csv`).

## What it does not hold

- The file's other 26 products: crude oil's parts (NGL, refinery feedstocks, additives), naphtha, white spirit, lubricants, bitumen, petroleum coke, other kerosene, aviation gasoline, the gasoline and diesel totals with their biofuel portions and the biofuels themselves; any product below its group.
- The United Kingdom (Eurostat's terms); Bosnia and Herzegovina, Ukraine, Switzerland, Iceland, Liechtenstein, Kosovo and the euro area, which the extract does not give; months before 2016; any month an area does not report, and the EU's total for a month in which members are missing.
- Stock levels (only their change), oil prices, trade by partner country, refinery capacity and Eurostat's annual oil balance (`nrg_cb_oil`); EIA's United States petroleum tables are the ERW's for the United States.
- Earlier versions of a revised month.

Acted on in session 2366, the table written again offline (the same 457,009 rows): the header now says that stock change is positive when oil is put into stock, that EU27_2020 is the reporting members' sum (not the EU's whole in the months members lack a row, the oil products' calculated deliveries of 2018 and 2019 most), and that some flows are negative as Eurostat prints them; session 2363's report is corrected (the members' sum, the write's metadata patch). Recorded, not changed: `retrieved_at` of an offline run is the saved file's time, a second after the fetch.
