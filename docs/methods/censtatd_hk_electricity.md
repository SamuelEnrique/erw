# Hong Kong's electricity: consumption by type of user a month from January 1979, and generation, imports, exports, own use and losses a quarter from 2013 (C&SD, Hong Kong Energy Statistics)

Energy Research Warehouse (ERW), method note written in session 2326 (chain 108) for a table first written on 24 October 2026 (session 2323 of chain 108, its report `archive/sessions/SESSION_2323_REPORT.md`).

Tables: `censtatd_hk_electricity`

## Publisher and address

Census and Statistics Department, Hong Kong (C&SD), Hong Kong Energy Statistics, two web tables listed on DATA.GOV.HK (the catalogue search `https://data.gov.hk/en-data/api/3/action/package_search?q=electricity&rows=50`, read 517, lists tables 915-91201 to 915-91203; the header's page is 915-91201's, `https://data.gov.hk/en-data/dataset/hk-censtatd-tablechart-915-91201`). The table reads C&SD's web table API, one request a table:

- `https://www.censtatd.gov.hk/api/get.php?id=915-91201&lang=en&full_series=1`, "Monthly statistics on consumption of electricity and gas by type of users"
- `https://www.censtatd.gov.hk/api/get.php?id=915-91203&lang=en&full_series=1`, "Electricity production, imports, exports, and consumption"

Source id `censtatd:hong_kong_energy_statistics`. Each answer is JSON with a header (status "Success", code 0, the title, the table notes and the source) and a `dataSet` of records (`sv` the series, `freq` M, Q or Y, `period`, `svDesc` "Terajoule" on every record, `figure`, `sd_value`, and in 91201 `USER_TYPE` with its description). Table 91201 holds 6,190 records: electricity (`ELEC_LOCAL`) for the total and user types 1 Domestic, 2 Commercial, 3 Industrial and 4 Street lighting, exports to the Mainland (`ELE_EX_CHN`) and town gas (`GASC_LOCAL`), 572 months and 47 years each. Table 91203 holds 335: `ELEC_LOCAL`, `ELE_GEN_LOCAL`, `ELE_IM_CHN`, `ELE_EX_CHN` and `ELE_IND_OWN`, 54 quarters and 13 years each.

The notes, as C&SD gives them: "Figures in the table may not add up to the total due to rounding"; local consumption is "Excluding industry own use and losses, i.e. consumption of energy by power companies and energy losses in electricity transformation and distribution, and exports of electricity to Chinese Mainland"; own use and losses are "Including (a) consumption of energy by power companies; and (b) energy losses in electricity transformation and distribution"; "Some consumption in March 2023 was included in the figure in April 2023 due to delay in billing"; "- Not applicable". 91201's source is "CLP Power Hong Kong Limited, The Hongkong Electric Company, Limited and The Hong Kong and China Gas Company Limited" (the last for town gas), 91203's the two power companies.

Session 2323's probe (`runs/c108/s2323/probe.csv`) made 15 requests to the web hosts, nine of them for Thailand (not taken) and six for this table: DATA.GOV.HK's robots file (HTTP 404, read 515), its terms and conditions (read 516), the catalogue search (read 517), www.censtatd.gov.hk's robots file (read 518), and the two tables (HTTP 200, 68,397 bytes for 91203 at 2026-10-24T06:44:04Z, 1,628,358 bytes for 91201 at 06:44:05Z, neither with a Last-Modified). All 15 are saved in `runs/license_reads/s2323/`.

Connector: `warehouse/connectors/censtatd_hk_electricity.py` (session 2323): `[--offline] [--out-dir DIR]`, at most two requests. A status not success, a series or user type not in its map, a unit not terajoules, a period not of its frequency's form, a value that is not a number or a key given twice stops the run; the years and town gas are skipped. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public, and it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

One write, run `20261024T065035Z` ("This run wrote 3699 rows: 3699 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the two tables as session 2323's trial had fetched them. `retrieved_at` is each table's download time: 2026-10-24T06:44:05Z for 91201's rows, 06:44:04Z for 91203's. `vintage` is blank in every row: C&SD's answers carry no Last-Modified.

C&SD's records carry no provisional or revised flag (`sd_value` is empty on every record but three). A later run merges by (entity, variable, ts_utc), so a revised month or quarter replaces the old figure, and a period C&SD stops printing keeps its earlier value.

## Shape and variables

Series, 3,699 rows, two entities named after the tables, `node` Hong Kong, `geo` HK, `unit` MWh (C&SD's terajoules times 1,000,000/3,600), `market` blank. 10 variables; `exports_mainland` is in both entities.

| Entity | Variable | C&SD's series | freq | Rows | First | Last |
|---|---|---|---|---|---|---|
| censtatd:915-91201 | consumption_total | ELEC_LOCAL, Total | P1M | 572 | 1979-01 | 2026-08 |
| censtatd:915-91201 | consumption_domestic | ELEC_LOCAL, Domestic | P1M | 572 | 1979-01 | 2026-08 |
| censtatd:915-91201 | consumption_commercial | ELEC_LOCAL, Commercial | P1M | 572 | 1979-01 | 2026-08 |
| censtatd:915-91201 | consumption_industrial | ELEC_LOCAL, Industrial | P1M | 572 | 1979-01 | 2026-08 |
| censtatd:915-91201 | consumption_street_lighting | ELEC_LOCAL, Street lighting | P1M | 572 | 1979-01 | 2026-08 |
| censtatd:915-91201 | exports_mainland | ELE_EX_CHN | P1M | 569 | 1979-04 | 2026-08 |
| censtatd:915-91203 | local_consumption | ELEC_LOCAL | P3M | 54 | 2013 Q1 | 2026 Q2 |
| censtatd:915-91203 | local_generation | ELE_GEN_LOCAL | P3M | 54 | 2013 Q1 | 2026 Q2 |
| censtatd:915-91203 | imports_mainland | ELE_IM_CHN | P3M | 54 | 2013 Q1 | 2026 Q2 |
| censtatd:915-91203 | exports_mainland | ELE_EX_CHN | P3M | 54 | 2013 Q1 | 2026 Q2 |
| censtatd:915-91203 | industry_own_use_and_losses | ELE_IND_OWN | P3M | 54 | 2013 Q1 | 2026 Q2 |

The months by year (TWh, the sum of each year's months in the table, `runs/c108/s2326/notes/hk.out`):

| Year | Total | Domestic | Commercial | Industrial | Street lighting | Exports |
|---|---|---|---|---|---|---|
| 1979 | 9.878 | 2.099 | 3.823 | 3.924 | 0.033 | 0.251 |
| 1990 | 23.833 | 5.288 | 11.550 | 6.926 | 0.069 | 1.797 |
| 2000 | 36.299 | 8.953 | 22.318 | 4.936 | 0.090 | 1.182 |
| 2010 | 41.862 | 10.929 | 27.746 | 3.078 | 0.111 | 2.609 |
| 2019 | 44.803 | 11.927 | 29.768 | 3.004 | 0.104 | 0 |
| 2024 | 46.275 | 12.655 | 30.431 | 3.122 | 0.067 | 0 |
| 2025 | 45.676 | 12.353 | 30.236 | 3.024 | 0.063 | 0 |

The quarters by year (TWh, the same source):

| Year | Generation | Imports | Exports | Own use and losses | Local consumption |
|---|---|---|---|---|---|
| 2013 | 39.063 | 9.969 | 1.650 | 4.826 | 42.556 |
| 2018 | 36.460 | 12.599 | 0.556 | 4.304 | 44.199 |
| 2019 | 36.795 | 12.381 | 0 | 4.373 | 44.803 |
| 2024 | 38.521 | 11.365 | 0 | 3.611 | 46.276 |
| 2025 | 36.311 | 12.681 | 0 | 3.317 | 45.676 |
| 2026 (Q1, Q2) | 16.277 | 7.010 | 0 | 1.590 | 21.697 |

- **Shares.** In 2025 commercial users take 66.2 percent of local consumption, domestic 27.0, industrial 6.6 and street lighting 0.14; industry's share was 39.7 percent in 1979. The highest month is July 2022 (4,985,556 MWh), the lowest February 1979.
- **Exports end in 2018.** Monthly exports are 0 in 97 months: two before September 2018, the last month with exports, and every month from October 2018. Quarterly exports are 0 in the 31 quarters from the fourth of 2018. C&SD prints them as 0, not as not applicable.
- **Precision.** Most figures are whole terajoules, but 326 of 91201's electricity figures carry decimals (65 a year in 2023, 2024 and 2025, 40 in 2026; March 2023's total is 11,446.5024 TJ), and 3 of 91203's. Each MWh value is the TJ figure times 277.777..., so most values are not whole MWh (269,444.44444444444 MWh for February 1979's commercial use).
- **Delayed billing.** By C&SD's note, some of March 2023's consumption is in April 2023's figure (the totals: 11,446.5024 TJ in March, 11,902.3956 TJ in April); the table keeps both as published.

## Placing values in time, and what is filled

`ts_utc` is the period's first day at 00:00:00Z: a month's first day (C&SD's `period` YYYYMM), and for a quarter the first day of its first month (C&SD's period is the quarter's last month, 201303 for the first quarter of 2013, written 2013-01-01). `freq` is P1M or P3M. The three records C&SD marks "-" (not applicable), exports in January, February and March 1979, have no row; no other record lacks a number, and nothing is filled. C&SD's years (47 in 91201, 13 in 91203) are not taken, being sums of the months and quarters; neither is town gas.

## License

Header: "License: public, DATA.GOV.HK's terms of use (commercial and non-commercial use free of charge, with the source identified and attributed). Cite: Census and Statistics Department, Hong Kong Energy Statistics (DATA.GOV.HK)." DATA.GOV.HK's terms and conditions (read 516): "You are allowed to browse, download, distribute, reproduce, hyperlink to, and print the Data for both commercial and non-commercial purposes on a free-of-charge basis on condition that:-" the user complies with the terms, identifies the source and acknowledges the Government's and the Relevant Organisations' ownership, indemnifies them, and gives "proper attribution to the Government, the Relevant Organisations and DATA.GOV.HK". `warehouse/metadata/license_verdicts.csv`: "Census and Statistics Department, Hong Kong (C&SD)", read 516, verdict "may be public", if the ERW sells anything "may be public". www.censtatd.gov.hk's robots file allows every path to every agent and names anthropic-ai, Claude-Web and ClaudeBot each with `Allow: /` (read 518); DATA.GOV.HK has none (read 515, HTTP 404). `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", ERW verdict public.

## Checks (session 2326)

The figures in this note were computed from the rows of `warehouse/output/censtatd_hk_electricity.csv`, read past its 10 header lines (counted), and from the two saved tables, read only (scripts `runs/c108/s2326/notes/hk.py`, `hk2.py` and `hk_raw.py`, outputs `hk.out`, `hk2.out` and `hk_raw.out` beside them).

- 3,699 rows, 10 variables, months January 1979 to August 2026 and quarters 2013 to the second of 2026, as header lines 1, 3 and 10 state; no (entity, variable, ts_utc) twice; no blank or negative value; unit MWh and geo HK throughout.
- **Against the tables:** an independent parse of the saved answers (the monthly electricity records less the three marked "-", the quarterly records) gives 3,699 keys, every one in the table and none extra, values equal within 5e-10 MWh. 5 x 572 + 569 + 5 x 54 = 3,699.
- **The trial against the table:** `runs/c108/s2323/trial/censtatd_hk_electricity.csv` has the same 3,699 keys with 0 differences in value or `retrieved_at`.
- Session 2323's cross-check (`runs/c108/s2323/cross.py`, `cross.out`, run on the trial): the user types against the total within 1.7748 TJ, 35 months over 1 TJ; generation plus imports less exports less own use and losses against local consumption within 1 TJ in all 54 quarters; the months' sums against 91203's local consumption within 1.2252 TJ and its exports within 1.0 TJ over 54 quarters; 91203's years against their quarters within 2 TJ.
- Session 2326's own: 91201's years against the sums of their months differ by up to 5 TJ (the total in 1981; 4 TJ in 1996, 3 TJ in 1993's exports and in the totals of 1997, 1998 and 1999, 2.474 TJ in 2022's total), 7 of 282 year-series over 2 TJ. Generation plus imports less exports against `owid_ember_electricity_annual`'s `owid_energy:HKG` demand (which ends in 2024): -1.43 percent in 2013, 0.13 (2014), 0.12 (2015), 0.06 (2016), -0.04 (2017), -0.22 (2018), -0.29 (2019), 1.56 (2020), 1.53 (2021), -0.02 (2022: 48.439 against 48.45 TWh), -0.45 (2023) and 2.20 (2024: 49.886 against 48.81 TWh).

## The session report against the table

Every figure of `SESSION_2323_REPORT.md` checked against the table, the saved tables and `cross.out` holds (3,699 rows, January 1979 to August 2026 for the months, 2013 to the second quarter of 2026 for the quarters, terajoules times 1,000,000/3,600, the user types within 1.8 TJ with 35 months over 1 TJ, the quarters balancing within 1 TJ in all 54, the months' sums within 1.3 TJ and the exports within 1 TJ, 2024's 49.89 against 48.81 TWh, own use and losses 3.3 to 4.4 TWh a year over 2019 to 2025, exports zero in every quarter from 2019, the license sentence and the robots files, 15 requests to the web hosts), except:

- "generation plus net imports is 0.3 to 2.2 per cent from Ember's, 2019 to 2024": 2022 is 0.02 percent (point 1).
- "C&SD's years are the sums of its months and quarters (within 2 TJ)": the months' years differ by up to 5 TJ (point 2).

## What it does not hold

- C&SD's years (sums of what is here), town gas, consumption by user type before 1979 or by quarter, generation, imports and own use before 2013 or by month, generation by fuel or by company, capacity, peak demand and prices; and CLP's and HK Electric's own figures.

## Points for the session to act on

1. **The report's range against Ember starts too high.** The report says generation plus net imports "is 0.3 to 2.2 per cent from Ember's, 2019 to 2024". Over those years the gaps are -0.29, 1.56, 1.53, -0.02, -0.45 and 2.20 percent; 2022 is 48.439 against 48.45 TWh (`cross.out` prints 48.44 and 48.45). The range is 0.02 to 2.2 percent.
2. **The months' years are not within 2 TJ.** The report says "C&SD's years are the sums of its months and quarters (within 2 TJ)". `cross.py` tests only 91203's years against its quarters (2 TJ). 91201's years differ from the sums of their months by up to 5 TJ (the total in 1981), and 7 of 282 year-series by more than 2 TJ (`hk2.out`). Leaving the years out is still right; the figure in the report should read "within 2 TJ (quarters) and 5 TJ (months)".

Compared besides, with no contradiction found: the header's and docstring's counts, tables, series, user types, unit and factor, "a quarter's period is its last month", "Local consumption excludes the power companies' own use, losses and the exports to the Chinese Mainland", the March 2023 note, "A cell C&SD marks not applicable has no row; nothing is filled" (three cells, January to March 1979's exports) and the robots and license claims against the rows, the two answers and the saved pages. Exports are zero from the fourth quarter of 2018, so the report's "from 2019" holds and understates it.

Acted on in session 2326: session 2323's report now gives the gap to Ember as 0.02 to 2.2 per cent, and the years as within 2 TJ of the quarters and 5 TJ of the months. No change to the connector or the table was needed.
