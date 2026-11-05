# Europe's imports of natural gas and LNG by partner country, a month, from 2015 (Eurostat nrg_ti_gasm)

Energy Research Warehouse (ERW), method note written in session 2218 (chain 098) for a table first written on 24 October 2026 (session 2213 of chain 098, `archive/sessions/SESSION_2213_REPORT.md`). Eurostat's renewable capacity table, under the same terms, is `docs/methods/eurostat_renewable_capacity_annual.md`.

Tables: `eurostat_gas_imports_monthly`

## Publisher and address

Eurostat (Statistical Office of the European Union), data set `nrg_ti_gasm`, "Imports of natural gas by partner country, monthly data", page `https://ec.europa.eu/eurostat/databrowser/view/nrg_ti_gasm/default/table`. The SDMX 2.1 dissemination API (no key) answers this data set with a queued job: the query `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ti_gasm?format=SDMX-CSV&compressed=false&startPeriod=2015-01` names a job, `.../api/dissemination/1.0/async/status/<job id>` reports it, and `.../api/dissemination/1.0/async/data/<job id>` serves the SDMX-CSV. This run's job is `7330e3ef-4d8a-41e6-af23-bdfd15c46fd7`; its result is 188,289,607 bytes, 2,368,830 lines (1,184,417 in TJ_GCV, 1,184,413 in MIO_M3). Source id `eurostat:nrg_ti_gasm`. The result is saved under `warehouse/raw/eurostat_gas_imports/20261024T014004Z_probe/` (session 2213's probe copy, seeded into the raw store; the trial and the write read it offline).

Connector: `warehouse/connectors/eurostat_gas_imports.py` (session 2213): `[--job ID --offline] [--out-dir DIR]`; one request to submit, at most twelve status polls 20 seconds apart, one to fetch. It takes the terajoules of gross calorific value (TJ_GCV) only, times 1,000,000 / 3,600 (277.7778), rounded to 3 decimals, as MWh; the million cubic metres are not taken. Importing countries kept: the EU's members, EFTA's and the official candidates, with the aggregates EU27_2020, EA21 and EA20; the United Kingdom and Kosovo are left out under Eurostat's terms. Every partner is kept. A zero and a blank have no row. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

One run, `20261024T014631Z`, written offline from the job's result retrieved at 2026-10-24T01:40:51Z (`retrieved_at` on every row). `vintage` is blank on every row: the result carried no Last-Modified (the raw manifest's field is empty), and Eurostat's own "LAST UPDATE" column, "23/10/26 23:00:00" on every line of the file, is not kept. Eurostat's flags are kept in `x_flag`: "p" on 148 rows (months from 2015-06 to 2026-09), "e" on 6 (all 2026-09), blank on 34,751; `x_conf_status` is blank on every row.

Eurostat revises earlier months. A later run merges by (entity, variable, ts_utc): a revised value replaces the old one, but a month Eurostat later revises to zero or blank writes no row, so the earlier non-zero row would be kept.

## Shape and variables

Series, 34,905 rows, 865 entities `eurostat_gas_imports:<geo code>:<SIEC>:<partner>`, `variable` imports, `unit` MWh, `freq` P1M, 141 months from 2015-01 to 2026-09. `x_siec` G3000 natural gas (25,625 rows) or G3200 liquefied natural gas (9,280), a part of G3000: every G3200 row has a G3000 row for the same importer, partner and month, and none is larger. `node` "<geo> <SIEC> from <partner>".

- Importers: 36 codes, 34 countries and the aggregates EU27_2020 (6,439 rows) and EA21 (1,092); `geo` is the ISO alpha-2 code (Eurostat's EL written GR), blank for the two aggregates. EA20, Cyprus, Switzerland, Iceland, Liechtenstein, Bosnia and Herzegovina and Montenegro are kept by the connector but have no row.
- Partners: 78 codes, six of them not countries: TOTAL (6,269 rows), NSP (not specified, 1,139), AFR_OTH, AME_OTH, ASI_NME_OTH and EUR_OTH. An importer's TOTAL counts every partner, other EU members among them.
- Values: 0.278 to 673,357,583.333 MWh (the EU's total natural gas imports, January 2017); none zero or negative.

Importers start and end in different months. 28 start in 2015-01; Norway in 2015-07, Malta and Serbia in 2017-01, Georgia in 2018-01, Moldova in 2020-01, Albania in 2023-01, EA21 in 2025-01; Ukraine runs from 2020-02 to 2022-01 only. 19 importers reach 2026-09; 13 end in 2026-08 (EU27_2020 and EA21 among them) and 3 in 2026-07 (Spain, North Macedonia, Albania). 2026-09 holds 120 rows, against 310 to 388 in each month from 2026-02 to 2026-08.

The EU aggregate (EU27_2020) has its TOTAL in every month of 2015 to 2018 and 2021 to 2026-08, but:

- **2019:** 73 natural gas rows and 31 LNG rows over 10 months, no TOTAL. Eurostat's file holds 134 natural gas and 134 LNG lines for the aggregate that year (61 and 103 of them zero) and no TOTAL line.
- **2020:** the TOTAL alone, 12 rows; no partner and no LNG row. Eurostat's file holds nothing else for the aggregate in 2020.

The EU's natural gas imports (TOTAL, G3000) a year, TWh: 6,220.0 (2015), 7,135.8 (2018), 6,843.6 (2020), 6,405.0 (2022), 5,135.3 (2023), 4,747.2 (2024), 5,124.4 (2025). From Russia: 929.7 (2021), 624.8 (2022), 327.9 (2023), 315.3 (2024), 305.8 (2025). Its LNG from the United States (G3200): 177.4 (2021), 417.3 (2022), 437.9 (2023), 312.4 (2024), 570.0 (2025), 377.6 (January to August 2026).

## Placing values in time, and what is filled

`ts_utc` is the month's first day at 00:00:00Z. A month without a row is a zero or a blank in Eurostat's file, or a line the file does not have (the EU aggregate in 2019 and 2020); the table cannot tell which. 1,127,867 zeros and 2,604 blanks of the kept lines have no row (the header's count). Nothing is filled.

## License

Header: "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_ti_gasm. Eurostat bears no responsibility for this reshaping (zeros left out, TJ written as MWh)." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 280 (session 2123), "Reuse of statistical data ... for commercial or non-commercial purposes is authorised provided the source is acknowledged", with data for countries other than the EU's, EFTA's and the official candidates' not for commercial reuse; verdict "may be public", if the ERW sells anything "may be public"; the table's row: flag public, "agrees", ERW verdict public. The connector applies the restriction to the importing country (the United Kingdom and Kosovo left out), as session 2123 did; the table keeps every partner, the United States, Russia, Qatar and the United Kingdom among them, and the record's verdict does not discuss partners.

## Checks (session 2218)

The figures in this note were computed from the rows of `warehouse/output/eurostat_gas_imports_monthly.csv`, read past its 10 header lines, and from the saved job result, read only (scripts `runs/c098/s2218/eurostat.py`, `eurostat2.py`, `eurostat3.py` and `eurostat_raw.py`, outputs beside them).

- 34,905 rows, `ts_utc` from 2015-01-01T00:00:00Z to 2026-09-01T00:00:00Z, as the header states; G3000 25,625 and G3200 9,280, as the header states; no (entity, variable, ts_utc) twice; the EU's LNG from the United States last in 2026-08, as the header states.
- The saved result, counted again with the connector's country list: 34,905 non-zero, 1,127,867 zero and 2,604 blank TJ_GCV lines of the kept importers, and importers left out UK and XK, as the header states. 1,127,867 of the 1,162,772 non-blank kept lines are zero, 97.0 percent.
- The trial's table (`runs/c098/s2213/trial/eurostat_gas_imports_monthly.csv`) has the same rows, byte for byte.
- Session 2213's cross-check (`runs/c098/s2213/cross.py`), run again on the table from the main checkout: its output is identical to the saved `cross.out`. (1) "72 months, single partners over TOTAL median 0.9654, min 0.0000, max 0.9999": the 72 months are 2020 to 2025, since 2019 has no EU TOTAL row, and the twelve months of 2020 have no partner row, so each gives 0. Without them, 60 months of 2021 to 2025: median 0.9844, lowest 0.4036 (2024-03), highest 0.9999. (2) The EU's LNG from the United States against EIA's LNG exports by vessel to EU members (`eia_gas_trade_country_monthly`): MWh per MMcf 224 (2017), 178, 56 (2019), 213 (2021), 208, 194, 169, 188 (2025); correlation 0.987 over those eight years. 2020 has no Eurostat row.

## Where the description and the data disagree

1. **The EU aggregate's missing years.** The header gives one span, "2015-01 to 2026-09", and says zeros and blanks have no row. For EU27_2020, 2019 has no TOTAL and only some partners in 10 months, and 2020 has the TOTAL alone; Eurostat's file has no other lines for the aggregate in those years, so these are not the zeros and blanks the header counts. A series of the EU's imports from any partner has a hole in 2019 and 2020.
2. **Months that end early.** Only 19 of the 36 importers reach 2026-09, the header's last month; the EU aggregate and 12 others end in 2026-08, three in 2026-07. A sum over importers in 2026-07 to 2026-09 is incomplete. The header names the EU's latest LNG month from the United States only.
3. **Two aggregates or three.** The docstring keeps "the two aggregates"; the code keeps EU27_2020, EA21 and EA20. The table holds only the first two, so no row is affected.
4. **A wrong cross-reference in the license record.** Read 351 (session 2213, the robots file read again) says "/eurostat/api/dissemination/ not disallowed, as read 242 found"; read 242 is the U.S. Department of Agriculture's robots file. Eurostat's earlier robots read is 278 (session 2123).

Acted on in session 2218: the connector's docstring now names the aggregates it keeps (EA20 with no rows) and says an aggregate is as complete as Eurostat's file, EU27_2020 without TOTAL in 2019 and with TOTAL alone in 2020, the countries' last months differing (disagreements 1 to 3); the table is not written again, since its rows are right and its header changes at the next run. Read 351's text now cites read 278 (disagreement 4). Session 2218's report corrects session 2213's two claims below.

## The session report against the table

Every figure of `SESSION_2213_REPORT.md` checked against the table, the saved job result and the rerun cross-check holds (34,905 rows, 25,625 and 9,280, January 2015 to September 2026, 1,127,867 zeros and 2,604 blanks, 97 percent zeros, the United Kingdom and Kosovo left out, the result of 188 MB, the correlation 0.987 over 2017 to 2025, 169 to 224 MWh per MMcf outside 2019; the 5 requests are not testable from the table), except:

- "the EU's single-country partners make up a median 96.5% of its TOTAL natural gas imports over 72 months of 2019 to 2025 (... one month's partners are all zero beside a TOTAL)": the 72 months are 2020 to 2025, 2019 having no EU TOTAL row, and twelve months, all of 2020, have no partner row, not one. Without them the median is 98.4 percent over 60 months.
- "2019 and 2020 stand apart (2020 has no row: Eurostat's partner for those cargoes is another or not specified). Partner attribution, not units, explains the gap": in 2020 the EU aggregate has no partner row at all, only its TOTAL, so no partner is named for any cargo; in 2019 it holds the United States' LNG in 3 months only. Both years stand apart because the aggregate is incomplete in Eurostat's file, not because of how cargoes are attributed. For the other years the table cannot test the report's reason.

## What it does not hold

- The million cubic metres, Eurostat's exports and its annual tables, imports of the United Kingdom and Kosovo, the "LAST UPDATE" stamp, and months before 2015.
