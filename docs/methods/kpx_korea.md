# South Korea's generation by source a year, 1961 to 2025, and its mean daily peak and base demand a month, from the Korea Power Exchange's EPSIS

Energy Research Warehouse (ERW), method note written in session 2353 (chain 105's 2303) for two tables first written on 24 October 2026 by one connector (session 2297, `archive/sessions/SESSION_2297_REPORT.md`, "South Korea's generation and demand (the Korea Power Exchange's EPSIS)", commit `7290cf11`, on the branch `wip/2294-2307-data`). No other method note covers them. Korea's demand a calendar year, from Ember, is `owid_ember_electricity_annual` (entity `owid_energy:KOR`).

Tables: `kpx_korea_generation_annual`, `kpx_korea_demand_monthly`

## Publisher and address

Korea Power Exchange (KPX), Electric Power Statistics Information System (EPSIS), two of its English pages, each of which writes its whole grid into the page's own script:

- Generation Output by Source, `https://epsis.kpx.or.kr/epsisnew/selectEkgeGepTotChart.do?menuId=060101&locale=eng`, "(Unit : MWh)", source id `kpx:epsis_generation_by_source`;
- Average Peak/Base Demand by Month, `https://epsis.kpx.or.kr/epsisnew/selectEkgeEpsAepChart.do?menuId=030200&locale=eng`, "(Unit : MW)", its two views chosen by a menu reading "peak" and "base", source id `kpx:epsis_peak_base_demand_monthly`.

`sources.csv` (this worktree): publisher "Korea Power Exchange", reports "Generation Output by Source" and "Average Peak/Base Demand by Month", document list `https://epsis.kpx.or.kr/epsisnew/selectMain.do?locale=eng`, license internal, first and last seen 2026-10-24. Other periods come only by POST (`selectEkgeEpsMep.ajax`), which the connector does not send; KPX's sets on data.go.kr need a key the ERW does not hold. www.kpx.or.kr's robots file allows these paths (read 512); epsis.kpx.or.kr has no robots file (its robots address answers with the application's page, read 513).

Raw files on this machine: the two pages under `warehouse/raw/kpx_korea/20261024T053848Z_probe/` (227,374 and 180,798 bytes), fetched by session 2297's probe (`runs/c105/s2297/probe.py`, rows 3 and 5 of its `probe.csv`) at 2026-10-24T05:39:16Z and 05:40:50Z, each 200 with no `Last-Modified`. The probe's third page, EPSIS's daily Peak/Base Demand (`selectEkgeEpsMepChart.do?menuId=030100`, 05:40:47Z, 332,357 bytes), is kept only under `runs/license_reads/s2297/` and is not a table. Three trial folders (`20261024T054610Z`, `...054715Z`, `...054814Z`) hold empty manifests; the two writes' folders, `20261024T054925Z` (generation) and `20261024T054934Z` (demand), hold only the data lock's check.

Connector: `warehouse/connectors/kpx_korea.py` (session 2297), `--offline`, `--out-dir`, `--table generation|demand`. Ceiling: two requests. It stops if a page no longer prints its unit, if a year is given twice, if a column is not one of its 25, or if a subtotal is more than 5 percent from its parts.

Schedule: none. No line of `warehouse/run_daily.sh`, the data machine's scripts, `warehouse/scheduled.py` or a workflow names it; it was run by hand, once a table. `run_status.csv`: no row; `runs/status/kpx_korea.json` holds only the demand run's result ("270 rows", run `20261024T054934Z`), the generation run's having been written over (disagreement 4). `archive_manifest.csv` (this worktree): `kpx_korea_generation_annual` 1,526 rows, run `20261024T054929Z-local`, data hash `1270ccc9...`; `kpx_korea_demand_monthly` 270 rows, run `20261024T054938Z-local`, data hash `24b75380...`; the rows give both hashes again. Neither is in `redivis_uploads.csv` or `warehouse/redivis/config.yaml`. Live set: both in `catalogue_hold`, no rule. Sector `power` for both (`build_coverage.py`). Readers: none; `tests/test_session2297.py` (5 tests) builds page scripts in EPSIS's form.

## Vintage and revision

Each table is one snapshot (header line 10: "one snapshot; the previous file held 0 rows"), written offline from the probe's pages ("raw file reused" in each run log; disagreement 2). `retrieved_at` is one value a table, the page's: 2026-10-24T05:39:16Z (generation) and 05:40:50Z (demand). `vintage` is blank in every row; EPSIS sent no publication time and its pages carry no date or revision mark. A rerun asks for both pages again and replaces each file whole, so a revision by KPX, of 2025's generation for one, would leave no earlier copy here.

## Shape and variables

### `kpx_korea_generation_annual`

Series, 1,526 rows, 15 columns: the series columns and `x_group`, `x_label`; 10 header lines. One entity, `kpx:korea`; unit MWh as published (KPX's figures, to as many as six decimals); `freq` P1Y; `geo` KR; `market`, `node` and `vintage` blank. 25 variables, one a column of KPX's grid, `x_group` and `x_label` its headings ("Hydro" and "General", "Total generation" and "Utilities + Non-utility in common use"; Nuclear, New & Renewable, Group Energy, Internal Combustion, Others and the utilities' Total have no group). 65 years, 1961 to 2025. No value is negative.

The columns include KPX's subtotals (hydro, steam, combined cycle, the utilities' total, the non-utility generators in common use) and its two national totals, so a sum of rows counts the same energy two or three times. The two totals differ: `generation_total_utilities_and_purchased` is the utilities and the power they bought from non-utility generators; `generation_total_utilities_and_non_utility` adds the non-utility generators' own consumption, and is the one Ember's demand matches (below).

| Variable | Rows | Years | First year above 0 | 2025, TWh | Share of the national total, 2025 |
|---|---|---|---|---|---|
| `generation_nuclear` | 65 | 1961 to 2025 | 1977 | 184.69 | 29.11% |
| `generation_steam_bituminous_coal` | 65 | 1961 to 2025 | 1983 | 164.31 | 25.90% |
| `generation_combined_cycle_lng` | 24 | 1961 to 1976 (0), 2018 to 2025 | 2018 | 117.61 | 18.54% |
| `generation_new_and_renewable` | 65 | 1961 to 2025 | 2004 | 62.21 | 9.81% |
| `generation_group_energy` | 65 | 1961 to 2025 | 2004 | 53.60 | 8.45% |
| `generation_hydro_total` | 65 | 1961 to 2025 | 1961 | 8.23 | 1.30% |
| `generation_utilities_total` | 65 | 1961 to 2025 | 1961 | 593.57 | 93.55% |
| `generation_non_utility_total` | 65 | 1961 to 2025 | 1961 | 40.90 | 6.45% |
| `generation_total_utilities_and_purchased` | 65 | 1961 to 2025 | 1961 | 595.65 | |
| `generation_total_utilities_and_non_utility` | 65 | 1961 to 2025 | 1961 | 634.47 | 100% |

- **Columns KPX changed.** Combined cycle is split by type, `general` and `heat_and_electric` (57 rows, 1961 to 2017), then by fuel, `lng` and `oil` (24 rows: 0 in 1961 to 1976, empty from 1977 to 2017, figures from 2018). KPX leaves `generation_others` empty in 2017 (64 rows); it is 0 until 2018 and above 0 from 2019. The 99 empty cells of the page (8, 8, 41, 41 and 1) are the only years missing; every other column holds all 65.
- **Zeros are KPX's.** A 0 is a row: before a source existed (nuclear 0 from 1961 to 1976) and after it ended (steam heavy oil 0 in 2023 to 2025, steam LNG 0 in 2025).
- **The national total** grew from 1.936 TWh (1961) to 40.078 (1980), 290.443 (2000), 495.028 (2010), 577.112 (2020), 617.491 (2023), 627.784 (2024) and 634.470 TWh (2025).
- **Subtotals against their parts.** 58 subtotal-years differ from their parts by more than 0.001 MWh and at most 1 MWh a part (the largest 7.0 MWh). Eight are further, as header line 3 names them: the utilities' total in 1962 (-455.0 MWh), 1963 (-27,708.0, -1.239 percent), 1964 (-217.0), 1967 (-2,258.0), 1968 (-25,816.0, -0.428 percent) and 1997 (-50,001.0); the steam total in 1974 (+10,000.0); the hydro total in 2016 (+13.4). They are kept as KPX publishes them.

### `kpx_korea_demand_monthly`

Series, 270 rows, 14 columns: the series columns and `x_kpx_view`; 10 header lines. One entity, `kpx:korea`; unit MW as published (whole megawatts); `freq` P1M; `geo` KR. Two variables: `peak_demand_daily_mean` (`x_kpx_view` peak), 261 rows, January 2005 to September 2026, and `base_demand_daily_mean` (base), 9 rows, January to September 2026; no month missing inside either.

- **What a figure is.** The month's mean of KPX's daily peak (or base) demand: January 2026's 31 daily peaks on EPSIS's daily page sum to 2,487,141 MW, a mean of 80,230.35, and the table holds 80,230; the base, 60,392.03 and 60,392. January to September 2026 round the same way.
- **The highest monthly means** are August's: 87,799 MW (2024), 85,608 (2026), 85,492 (2025); then 85,033 (July 2025) and 83,943 (July 2026). The lowest, 42,371 (May 2005). Each year's highest month is August, December, January or July; its lowest is April or May (October in 2017).
- **A year's mean of its twelve monthly means** rose from 45,970 MW (2005) to 71,313 (2018), fell to 68,098 (2020) and reached 73,578 (2025).
- **Base over peak in 2026** runs from 0.707 (August) to 0.753 (January).

## Placing values in time, and what is filled

Generation: `ts_utc` the year's 1 January at 00:00:00Z, the calendar year in Korea's time (UTC+9); the stamp is the date, not the instant. Demand: `ts_utc` the month's first day at 00:00:00Z, a month in Korea's time.

Nothing is filled. What the connector leaves out:

- **A cell KPX leaves empty** (99 cells of the generation page, above).
- **A month not ended in Korea's time.** The demand page was read at 14:40:50 on 24 October 2026 in Korea; its October figures (peak 68,469, base 49,704 MW) are the means of 1 to 23 October on the daily page (68,469.43 and 49,703.83), a month to date, and have no row.
- **A month KPX shows as 0**, not published (the base view prints it as "-"): the base view's January to October 2025 and both views' November and December 2026. No month inside the table's span is 0.
- **An ended year KPX publishes in part**, each named in header line 3 of the demand table: the peak view's 1993 to 2004 (one month a year from 1993 to 2001: December 1993, July 1994, August 1995 to 1997, September 1998, August 1999 and 2000, July 2001; three months in 2002, four in 2003, seven in 2004, June to December); and the base view's 2025, November 12,277 MW and December 57,565 MW, the first a fifth of the second.

## License

Header line 9 of each: "License: internal until the licenses' round reads KPX's terms (the page: Copyright(C) 2020 Korea Power Exchange. All Right Reserved.). Source: Korea Power Exchange." `coverage.csv` and `sources.csv`: internal. `warehouse/metadata/license_verdicts.csv`, Korea Power Exchange (read 518, KPX's Korean home page, `https://www.kpx.or.kr/`, read 2026-10-24T06:24:01Z): "COPYRIGHT(C) 2021 KOREA POWER EXCHANGE(KPX) ALL RIGHTS RESERVED", verdict "needs written permission", the same if the ERW sells anything; note: "www.kpx.or.kr links no copyright policy and shows no KOGL (Korea Open Government License) mark, Korean or English; EPSIS's pages carry Copyright(C) 2020 Korea Power Exchange. All Right Reserved. Its sets on data.go.kr may carry a licence there, but need a key the ERW does not hold. kpx_korea_generation_annual and kpx_korea_demand_monthly stay internal." `docs/licenses.md`, both tables' rows: Korea Power Exchange, "needs written permission", flag internal, "agrees", ERW verdict internal; under "Permission needed", "Write to: no person or address on the page read". `license_tables.csv`: "the source registry". No row in `license_status.csv`. `SESSION_2299_REPORT.md` reads KPX's "all rights reserved", with no licence stated, as needing written permission, and leaves "Ask KPX, or read its data.go.kr licence" for Samuel's ruling.

## Checks (session 2353)

The figures in this note were computed by `runs/c105/s2353/check_kpx_korea.py` (output `check_kpx_korea.out` beside it) from the rows of `warehouse/output/kpx_korea_generation_annual.csv` and `kpx_korea_demand_monthly.csv` in the main checkout, each read past its 10 header lines (counted), and from the two saved EPSIS pages and the daily page, parsed there by their own patterns (not the connector's). No request was made.

- Generation: 1,526 rows, no (entity, variable, ts_utc) twice, no blank value; every `ts_utc` a 1 January. Demand: 270 rows, the same; every `ts_utc` a month's first day. Both data hashes equal the archive manifest's.
- **Against the generation page:** 65 years, 1961 to 2025 (none of 2026), 1,526 cells with a figure and 99 empty; every row equals its cell and every figure is a row. 2025 as written in the page's script: national total `c22 = textFormmat("634470449.511898",count)`, utilities and purchased `c21` 595,649,039.387717, nuclear `c14` 184,692,894.09123, bituminous coal `c6` 164,306,395.248529 MWh; the table's rows are the same numbers.
- **Against the demand page:** both views, 34 years each (1993 to 2026); every row equals its cell. Peak, August 2025: the page's `c8 = textFormmat("85492.0",count)`, the table's 85,492.
- **Against the daily page** (2026-01-01 to 2026-10-23, 296 days): the mean of each month's daily peaks and bases, January to September 2026, rounds to the table's figure (largest difference 0.5: June's peak mean 71,508.50, the table 71,508).
- **Against Ember's Korea demand** (`owid_ember_electricity_annual`, `owid_energy:KOR`, `electricity_demand`, 2000 to 2025, which Our World in Data gives to 0.01 TWh): KPX's national total (`generation_total_utilities_and_non_utility`) is within 0.004 percent of Ember's from 2000 to 2020, and the same at Ember's rounding in 2006 to 2010, 2014 to 2017, 2020 and 2023 (11 years); 2000 is 290.4429 against 290.45 TWh. It is not the same in 2021, 601.94 against 607.76 TWh (-0.958 percent), or 2022, 624.60 against 622.59 (+0.323 percent), and is above Ember's in 2024, 627.78 against 625.38 (+0.384 percent), and 2025, 634.47 against 624.66 (+1.571 percent). Utilities and purchased power alone is 3.4 to 8.3 percent below Ember's in every year.
- **Scale.** 2025's national total over 8,760 hours is 72,428 MW, utilities and purchased power 67,996 MW; the mean of 2025's monthly peak means is 73,578 MW. The generation counts gross output, the non-utility generators' own use included; the demand is the load KPX reports. The tables are not reconciled here.

## Where the description and the data disagree

1. **Ember "equal to the MWh".** `SESSION_2297_REPORT.md`: KPX's national total is "equal to Ember's to the MWh in 2000, 2010, 2015, 2020 and 2023". Ember's figures are rounded to 0.01 TWh (10,000 MWh), so no year can be equal to the MWh; at Ember's rounding 2010, 2015, 2020 and 2023 are equal and 2000 is not (290.4429 against 290.45 TWh). Read as "equal from 2000 to 2023", it fails in 2021 (-0.958 percent) and 2022 (+0.323 percent).
2. **"Retrieved: <run>" and "each page asked again unless --offline".** Header line 4 of each table names the run that wrote it, and the docstring says each page is asked again on a run. Both runs were offline and asked for nothing (their raw folders hold only the lock check); the pages were fetched by session 2297's probe at 05:39:16Z and 05:40:50Z, as the second half of line 4 and `retrieved_at` say.
3. **"Internal until the licenses' round reads KPX's terms."** Header line 9 of each table and the docstring; `SESSION_2297_REPORT.md`: "the license tables mark the publisher 'not settled'". Session 2299 read them (read 518): "needs written permission".
4. **No record of the runs.** `CLAUDE.md` describes `run_status.csv` as "every run and every gap"; it holds no row of `kpx_korea`, and `runs/status/kpx_korea.json`, written by each run under one name, keeps only the demand run's result.

Not acted on: this note changes no file but itself.

## The session report against the table

`SESSION_2297_REPORT.md`: "`kpx_korea_generation_annual`: 1,526 figures, 1961 to 2025, in MWh as published" and "Every column of KPX's table is a variable (25)": hold. "`kpx_korea_demand_monthly`: 270 figures": holds, 261 peak from January 2005 and 9 base from January 2026. "January to September 2026 equal the means of the daily page's figures to the megawatt (January: peak 80,230 MW, base 60,392 MW)": holds, as rounded means. "KPX's own table misses that in eight years, 1962 to 2016, at most 1.2 percent (1963's utilities' total)": holds (1.239 percent); "2016's hydro total is 13.4 MWh off its parts": holds. "The base view's 2025, whose first month, November, reads 12,277 MW against December's 57,565": holds. "0.38 percent above in 2024 (627.8 against 625.4 TWh)" and "1.57 percent above in 2025 (634.5 against 624.7 TWh)": hold. "Equal to Ember's to the MWh": disagreement 1.

## What it does not hold

- Generation by month, by plant, by company or by region; installed capacity (on EPSIS's daily page and other pages, not read); 2026's generation (the page holds years to 2025 only).
- Hourly or daily demand (the daily page holds 2026 alone and is not a table); the peak view's months before 2005 and the base view's before 2026; October 2026 and later; the day and hour of a peak; reserve and reserve margin.
- Prices (KPX's system marginal price), fuel costs and trade; any earlier copy of a figure KPX has revised.
