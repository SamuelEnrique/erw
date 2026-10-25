# Eurostat's monthly solid fuels supply: hard coal, brown coal, coke oven coke, peat and oil shale, every flow of the monthly balance, 37 European countries and the EU, January 2016 to September 2026 (nrg_cb_sffm)

Energy Research Warehouse (ERW), method note written in session 2366 (chain 110) for a table first written on 24 October 2026 (session 2364 of chain 110, `archive/sessions/SESSION_2364_REPORT.md`, commit `3e9d0deb`). Eurostat's terms, the countries they allow and the shared country lists are described in `docs/methods/eurostat_renewable_capacity_annual.md` (session 2129); the same publisher's monthly oil, written the session before, is `docs/methods/eurostat_oil_monthly.md`, and its monthly gas balance `docs/methods/eurostat_gas_balance_monthly.md`.

Tables: `eurostat_solid_fuels_monthly`

## Publisher and address

Eurostat (Statistical Office of the European Union), "Supply and transformation of solid fuels - monthly data" (`nrg_cb_sffm`), page `https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_sffm/default/table`, through the SDMX 2.1 dissemination API without a key, one request answered at once:

- `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_sffm?format=SDMX-CSV&compressed=false&startPeriod=2016-01`

Source id `eurostat:nrg_cb_sffm` (`sources.csv`: license public, first and last seen 2026-10-24). The answer is SDMX-CSV with the columns `DATAFLOW, LAST UPDATE, freq, nrg_bal, siec, unit, geo, TIME_PERIOD, OBS_VALUE, OBS_FLAG, CONF_STATUS`: 216,280 lines, 18,032,221 bytes, five fuels, 16 balance items, unit THS_T and frequency M on every line, periods 2016-01 to 2026-09, "LAST UPDATE" 23/10/26 23:00:00 on every line. It holds 40 areas: the 27 members, Norway, nine candidates (Albania, Bosnia and Herzegovina, Georgia, Moldova, Montenegro, North Macedonia, Serbia, Turkiye written TR, Ukraine), EU27_2020, the United Kingdom and Kosovo. There is no line for Switzerland, Iceland, Liechtenstein or a euro area aggregate.

Raw files: `warehouse/raw/eurostat_solid_fuels_monthly/20261024T085807Z_probe/`, the answer (retrieved 2026-10-24T08:58:15Z, HTTP 200, sha256 `2c79edfd...`, no Last-Modified) and its manifest, seeded from session 2364's probe (`runs/license_reads/s2364/02_...`, the same bytes); `20261024T085944Z/` (an empty manifest) and `20261024T090009Z/` (the write's lock check only). Session 2364 made 3 requests: ec.europa.eu's robots file (sha256 `fc082fc2...`, as reads 278, 351, 383 and 583 in `license_reads.csv`: the old SDMX path and the search pages are disallowed, `/eurostat/api/dissemination/` is not), the data set and the SIEC codelist (`runs/license_reads/s2364/`).

Connector: `warehouse/connectors/eurostat_solid_fuels_monthly.py` (session 2364), `[--offline] [--out-dir DIR]`, one request, reused from the raw files (`ip.fetch_raw`). Kept: the areas in `eurostat_res_capacity.KEPT` (the EU, EFTA, the official candidates and Eurostat's aggregates) and all five fuels; each value is Eurostat's thousand tonnes times 1,000, rounded to 0.001 t. A header not Eurostat's, a unit other than THS_T, a frequency not monthly, a fuel or flow not among those named, a period not a month, a value that is not a number or a key given twice stops the run. A later run merges by (entity, variable, ts_utc).

Schedule: none. No shell script under `warehouse/`, no workflow in `.github/workflows/`, no file in `scripts/` and not `warehouse/scheduled.py` names it. `run_status.csv`: no row (the run by hand wrote `runs/status/eurostat_solid_fuels_monthly.json`: run `20261024T090009Z`, ok, "209040 rows"). `archive_manifest.csv`: 209,040 rows, run `20261024T090017Z-local`, `data_sha256` `a38ff642...`, the hash of the file on this machine. `redivis_uploads.csv` and `redivis_uploads_stanford.csv`: no row; `docs/redivis/release-v1/tables.csv` lists it as held (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`). Live set: under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded. `coverage.csv`: sector coal, 49 nodes, validator pass. Readers: none; `tests/test_session2364.py` tests the connector on SDMX-CSV built in the test. `package/src/erw/data/tables.csv`, `site/data/table_citations.json` and `site/data/table_verdicts.json` have no row for it.

## Vintage and revision

One write, run `20261024T090009Z`, offline from the saved answer; header line 10: "This run wrote 209040 rows: 209040 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs." `retrieved_at` is 2026-10-24T08:58:15Z in every row, the download time in the manifest. `vintage` is blank in every row: the answer carried no Last-Modified, so `ip.vintage_of` returns nothing; Eurostat's "LAST UPDATE" 23/10/26 23:00:00 is on header line 4, with no time zone.

Eurostat's flags on the rows: "e" (estimated) 3,965, "n" (not significant) 933, "p" (provisional) 904, "b" (break in series) 814, "d" (definition differs) 172, "u" (low reliability, all 67 Bosnia and Herzegovina's), "be" 12, "bn" 5. A revised month replaces the old figure on a later run; no earlier version is kept.

## Shape and variables

Series, 209,040 rows, 18 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_geo_code, x_siec, x_nrg_bal, x_flag, x_conf_status`), 10 header lines. `entity` `eurostat_sff:<Eurostat geo code>:<SIEC code>`, 190 (38 areas, five fuels); `variable` `flow:<NRG_BAL code>`, 16; `unit` t; `freq` P1M; `geo` the ISO alpha-2 code (Eurostat's EL written GR, 5,735 rows), blank for EU27_2020 (5,681 rows); `node` "<fuel>: <flow>", 49 values (the fuel-flow pairs held, as `coverage.csv` says); `market` and `vintage` blank; `x_conf_status` C in 6 rows that have a value (Turkiye's hard coal to iron and steel, six months of 2017, each 0) and blank in the rest. Every value is a whole number of tonnes. 122,990 rows are zero.

Flows by fuel (rows):

| Flow | Hard coal C0100 | Brown coal C0200 | Coke oven coke C0311 | Peat P1100 | Oil shale and oil sands S2000 |
|---|---|---|---|---|---|
| IPRD indigenous production | 4,575 | 4,509 | 4,497 | 4,466 | 4,192 |
| IMP imports | 4,588 | 4,583 | 4,502 | 4,570 | 4,192 |
| IMP_FROM_NEU imports from outside the EU | 4,120 | 0 | 4,041 | 0 | 0 |
| EXP exports | 4,467 | 4,576 | 4,484 | 4,519 | 4,192 |
| STKOP_NAT, STKCL_NAT opening, closing stocks | 4,515, 4,514 | 4,507, 4,507 | 4,576, 4,576 | 384, 384 | 4,192, 4,192 |
| STK_CHG change in stock | 4,576 | 4,580 | 4,588 | 4,481 | 4,204 |
| RCV_RCY recovered and recycled | 4,575 | 0 | 0 | 0 | 0 |
| GID_OBS gross inland deliveries observed | 4,199 | 0 | 0 | 0 | 0 |
| GID_CAL gross inland deliveries calculated | 4,580 | 4,580 | 4,592 | 4,494 | 4,204 |
| STATDIFF statistical differences | 4,192 | 0 | 0 | 0 | 0 |
| TI_EHG_MAP input to main power and heat producers | 4,529 | 4,580 | 0 | 4,576 | 4,192 |
| TI_CO input to coke ovens | 4,413 | 0 | 0 | 0 | 0 |
| FC_IND final consumption, industry | 4,358 | 0 | 0 | 0 | 0 |
| FC_IND_IS of which iron and steel | 4,112 | 0 | 4,573 | 0 | 0 |
| FC_OTH final consumption, other sectors | 4,442 | 0 | 0 | 0 | 0 |

Rows a fuel: hard coal 70,755, coke oven coke 40,429, brown coal 36,422, oil shale and oil sands 33,560, peat 27,874.

- **Areas and months.** 37 countries and EU27_2020; every fuel is given for all 38. The first month is 2016-01 except Bosnia and Herzegovina, Moldova, Turkiye and Ukraine (2017-01), Georgia (2018-01) and Albania (2022-01). The last month is 2022-01 for Ukraine; 2026-06 for EU27_2020 and the Netherlands; 2026-07 for 23 areas; 2026-08 for Cyprus, Denmark, Estonia, Greece, Croatia, Latvia, Moldova, Montenegro, Norway, Portugal and Turkiye; 2026-09 only for Malta (47 rows).
- **2016 is shorter.** Rows a year: 13,824 (2016), then 19,402 to 20,658 a year from 2017 to 2025, 12,373 for 2026. Observed deliveries, statistical differences, imports from outside the EU and iron and steel's hard coal begin in January 2017.
- **Imports from outside the EU are within imports** in 4,107 of 4,120 area-months for hard coal and in all 4,041 for coke; iron and steel's hard coal is within industry's in 3,960 of 3,961.
- **The EU's production**, Mt a year: hard coal 82.3 (2016), 75.3, 71.1, 65.1, 56.5 (2020), 57.2, 54.6, 40.8 (2023, ten months: the EU has no row for November and December 2023), 45.3 (2024), 44.1 (2025), 21.2 for January to June 2026; brown coal 388.0 (2016), 384.3, 368.3, 307.3, 244.3 (2020), 274.8, 294.3, 224.4, 196.6 (2024), 179.7 (2025), 89.5 for January to June 2026; coke oven coke 25.1, peat 0.7 and oil shale and oil sands 10.8 in 2024.
- **The largest value** is the EU's opening stock of hard coal in January 2016, 42,801,000 t.

**The stock change is a draw from stock: the opposite of the oil table.** STK_CHG equals opening less closing stocks in 4,471 of 4,514 area-months for hard coal, 4,485 of 4,507 for brown coal, 4,543 of 4,576 for coke, and all 384 and 4,192 for peat and oil shale (closing less opening holds only where the two are equal). Calculated deliveries equal production + recovered products + imports - exports + STK_CHG within 1 t in 4,521 of 4,563 area-months for hard coal, 4,493 of 4,509 for brown coal, 4,400 of 4,494 for coke, 4,435 of 4,445 for peat and all 4,192 for oil shale. So a positive STK_CHG here is coal taken out of stock and delivered, while in `eurostat_oil_monthly` and `eurostat_gas_balance_monthly` a positive stock change is fuel put into stock. Opening stocks equal the previous month's closing stocks in 4,249 of 4,471 consecutive area-months for hard coal and 4,330 of 4,465 for brown coal.

**Observed and calculated deliveries** are both given only for hard coal (4,196 area-months): equal within 0.5 t in 2,120, calculated above observed in 1,192 and below in 884, within 1 percent in 2,609 and within 5 percent in 3,250; the statistical difference equals calculated less observed in 4,003 of 4,192. The EU's hard coal, Mt a year, observed against calculated: 212.5 and 223.5 (2017), 202.6 and 215.5, 168.9 and 176.0, 140.9 and 140.3 (2020), 159.3 and 160.9, 160.8 and 160.4, 126.7 and 127.9, 105.6 and 107.4 (2024), 103.7 and 106.4 (2025).

**Negative values.** 5,182 rows. Change in stock 4,299 (hard coal 1,665, coke 1,364, brown coal 978, oil shale 174, peat 118; the lowest the EU's hard coal in November 2022, -2,828,701 t): expected, a build. Statistical differences 880, all hard coal (the lowest Ukraine's in February 2017, -1,014,800 t): expected. Calculated deliveries 2 (the Netherlands' hard coal in September 2016, -191,000 t, and one row of Ukraine's peat): they follow from the balance. Indigenous production 1 (Sweden's peat in September 2017, -2,848 t): not expected; Eurostat's figure as printed.

## Placing values in time, and what is filled

`ts_utc` is the month's first day at 00:00:00Z (Eurostat's TIME_PERIOD, YYYY-MM), a label for the month, not an instant: 129 months, January 2016 to September 2026. Of the answer's 211,101 lines for the 38 areas kept, 2,061 have no value and no row: 1,464 marked C (confidential), 372 flagged "u", 216 flagged "m" (missing), 6 "bu" and 3 "b" with C. Zeros are kept as Eurostat prints them. The United Kingdom's 2,594 lines and Kosovo's 2,585 are left out under Eurostat's terms. Nothing is filled: a month an area does not report has no row.

## License

Header line 9: "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_cb_sffm. Eurostat bears no responsibility for this reshaping (the rows filtered by country and renamed, the values unchanged but for the thousand tonnes written as tonnes)." `warehouse/metadata/license_verdicts.csv`: Eurostat (Statistical Office of the European Union), read 280 (session 2123): "Reuse of statistical data, metadata, publications, and other dissemination tools published on this website for commercial or non-commercial purposes is authorised provided the source is acknowledged. [...] [Not for commercial reuse:] Data for countries other than: Member States of the European Union (EU) Member States of the European Free Trade Association (EFTA) official EU acceding and candidate countries.", verdict "may be public", if the ERW sells anything "may be public". `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", if the ERW sells anything "may be public", ERW verdict public; it is in the list "Public now". `license_tables.csv`: Eurostat, "the source registry". No row in `license_status.csv`.

## Checks (session 2366)

The figures in this note were computed from the rows of `warehouse/output/eurostat_solid_fuels_monthly.csv` in the main checkout, read past its 10 header lines (counted, never parsed as comments), and from the saved answer, by `runs/c110/s2366/check_eurostat_solid_fuels_monthly.py` and `check_eurostat_solid_fuels_monthly_2.py` (outputs beside them, `.out`). No request was made.

- 209,040 rows and 2016-01-01 to 2026-09-01, as header line 10 states; no (entity, variable, ts_utc) twice; no blank value; every `ts_utc` a month's first day at midnight; `entity`, `variable` and `node` built from the `x_` columns in every row; the file's data hash is the archive manifest's.
- **Against the answer:** its 209,040 lines with a value for the areas kept and the table's rows are the same keys, none on one side only; every value is the answer's thousand tonnes times 1,000 (largest difference 4e-9 t), and every flag is the answer's. Ten rows drawn at random, for example: the EU's hard coal into coke ovens, November 2022, 3203.703 kt and 3203703.0 t; Finland's hard coal opening stock, August 2023, 1668.000 kt and 1668000.0 t; Spain's coke opening stock, November 2017, 39.000 kt and 39000.0 t. Kept: the 37 countries and EU27_2020; left out: the United Kingdom and Kosovo.
- **The EU against its members, production.** Hard coal: the EU has a row in 124 months (2016-01 to 2026-06, none for November and December 2023 and July to September 2026); in all 124 it equals the sum of the members that have a row, to the tonne. All 27 have a row in 88 of them; the other 36 lack Malta alone. Brown coal: 126 months; equal within 0.5 t in 124, and 1 t apart in December 2023 and May 2024; all 27 present in 78 (Malta has no row in 36 months, Greece in 12).
- **The EU against its members, every fuel and flow.** Of the 5,681 EU rows, 5,194 equal the members' sum within 0.5 t and 428 more differ by 1 t (rounding). 59 differ by more than 1.5 t, 38 of them with all 27 members present: hard coal 33, coke 19, brown coal 7, mostly in 2016 and 2017 (33) and 2023 to 2026 (22). The largest are hard coal into power and heat producers in January 2019 (the EU 10,625,014 t, 25 members 9,698,014 t), hard coal's closing stock that month (827,001 t apart), and the EU's calculated hard coal deliveries in 2016 (up to 214,000 t a month apart with all 27 present). Unlike the oil table, the EU row here is not always the members' sum.
- **Stocks, deliveries, negatives:** as above.

## Where the description and the data disagree

1. **"Summed over the 27 members ... in every month (124 and 126 months)."** `SESSION_2364_REPORT.md` says hard and brown coal production summed over the 27 members equal Eurostat's EU27 figure in every month. All 27 have a row in only 88 of hard coal's 124 months and 78 of brown coal's 126; in the rest the EU equals the sum of the members that report (Malta is missing in 36 months of each, Greece in 12 of brown coal's). Brown coal is 1 t apart in two months (December 2023, May 2024).
2. **"`vintage` is the shared fetch helper's (`ip.vintage_of`)."** The report implies a value. `vintage` is blank in all 209,040 rows, because the answer had no Last-Modified.

Not acted on: this note changes no file but itself.

## The session report against the table

`SESSION_2364_REPORT.md`, checked against the table, the saved answer and the run records: "209,040 figures, public": holds. "January 2016 to September 2026, 37 European countries and the EU27 aggregate": holds as a range; only Malta reaches September 2026, the EU ends in June 2026 and Ukraine in January 2022. "Fuels: hard coal, brown coal, coke oven coke, peat, and oil shale and oil sands": holds. "Flows: every one the file gives, 16 balance items": holds (49 fuel-flow pairs; observed deliveries, statistical differences, recovered products, coke ovens' intake and final consumption for hard coal only). "Unit: t": holds to the tonne. "Left out by Eurostat's terms: the United Kingdom and Kosovo, named in the header": holds (header line 3: "UK XK"). "Members against the EU": equal to the reporting members in every month, but not all 27 (disagreement 1). "The EU in 2024: it produced 45.3 Mt of hard coal and 196.6 Mt of brown coal": holds. "3 requests of 20": three answers in `runs/license_reads/s2364/`. "Errors: None": the write log `runs/c110/s2364/write.out` ends "done, fail=0". "Not in the Stanford draft yet": still so (no row in `redivis_uploads_stanford.csv`).

## What it does not hold

- Solid fuels other than these five (the monthly set gives no other), such as patent fuel, brown coal briquettes or coal tar, and the annual solid fuels balance (`nrg_cb_sff`); consumption by any sector but industry, iron and steel and "other sectors", which are given for hard coal (and iron and steel for coke) only; power plants' intake of coke.
- The United Kingdom and Kosovo (Eurostat's terms); Switzerland, Iceland, Liechtenstein and the euro area, which the answer does not give; Ukraine after January 2022; months before 2016; any month an area does not report.
- Coal prices, trade by partner country, and the ERW's United States coal tables (`eia_coal_*`, `msha_*`).
- Earlier versions of a revised month.

Acted on in session 2366, the table written again offline (the same 209,040 rows): the header now says that stock change is positive when coal is taken out of stock, the opposite of the oil table's, and that EU27_2020 is the reporting members' sum; session 2364's report is corrected (the members' sum; `vintage` empty).
