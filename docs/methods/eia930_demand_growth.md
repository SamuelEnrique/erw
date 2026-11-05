# Demand growth since 2019: the ERW's yearly, monthly and hourly means and peaks of EIA-930's hourly demand for the seven ISO balancing authorities and the Lower 48, local years 2019 to 2025 and January to September 2026

Energy Research Warehouse (ERW), method note written in session 2298 (chain 105) for a table first written on 4 October 2026 (session 97, `archive/sessions/SESSION_97_REPORT.md`, the demand growth explorer, commit `8ea37bd3`). Its method, the rule for the hours used, the variables and the page are in `docs/methods/demand_growth.md`, which this note does not repeat; the screen is stated once in `docs/methods/impossible_hours.md`; California's late hours and the break of December 2025 in `docs/methods/eia930_caiso_break.md`. `grid_peak_vs_capacity` reads its peaks (`docs/methods/grid_peak_vs_capacity.md`), and the siting tool its growth (`docs/methods/siting.md`).

Tables: `eia930_demand_growth`

## Publisher and address

Computed by the ERW: source id `erw:demand_growth` (`sources.csv`: publisher "Energy Research Warehouse (ERW), derived", report "Demand growth since 2019: annual and peak demand from EIA-930 hourly demand", `source_url` the method note in every row). No request is made. The input is U.S. Energy Information Administration (EIA), Form EIA-930 (Hourly Electric Grid Monitor): the per-area workbooks `https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx` (CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP) and `Region_US48.xlsx`, as the emissions connector saved them under `warehouse/raw/eia930_emissions/<run>/`, sheet `Published Hourly Data`, column `Adjusted demand` for a balancing authority and `Demand` for the Lower 48, whose workbook has no adjusted column. This build read the eight workbooks of run `20261019T172418Z` (header line 6; Last-Modified 19 October 2026, 16:08 to 16:29 GMT). It does not read `eia930_all_emissions` or any other ERW table.

Builder: `warehouse/derived/demand_growth.py` (session 97), with `impossible_hours.screen` (the rule, session 103; its range test, session 118) and `caiso_join.true_hours` (California's late hours). It rebuilds the table whole each run and, with `--snapshot`, the site's copy `site/data/demand_growth.json`.

What it computes, per area, from the hours used (held, above zero, within 25 percent of the median of the four adjacent hours, and within a third to three times the area's median hour), in the area's local time: for each whole local year 2019 to 2025 with at least 95 percent of its hours used, the mean and the highest hour (no highest hour for US48) and their growth since 2019 and on the year before; for every year, the same over 1 January to the end of the newest year's last whole month (September), so that 2026 is compared with the same months; the mean of each calendar month with 95 percent of its hours, of each local hour of the day, and of each hour of each month with 90 percent of its hours; and on the last whole year's row, the change of each of those from 2019, in MW and percent.

Schedule: the monthly job, `warehouse/run_monthly.sh` (`soft_step demand_growth ... warehouse/scheduled.py demand_growth`, which runs `demand_growth.py --snapshot` when the eight workbooks are on the machine), started by the first daily run on or after the third day of each month (`.github/workflows/daily-prices.yml`, input `monthly`; `scheduled.py --monthly-due` reads the site copy's built stamp). No daily step of `run_daily.sh`, and no step of `run_data_machine.sh` or `run_data_machine_tables.sh`, runs it. The present table was built on 21 October 2026 at 08:07 UTC by session 438 without `--snapshot` (`SESSION_438_REPORT.md`: "4 values revised (US48 August and September from EIA's revisions; the year's growth 10.25% to 10.26%)"); the site's copy is the monthly job's of 5 October. `run_status.csv`: no row. `archive_manifest.csv`: 24,108 rows as of run `20261021T081015Z-local`. Live set: `full` (`'^eia930_demand_growth$'`), under `review_hold` (catalogue row "review"), and its source under `sources_hold`. Readers: `warehouse/derived/grid_peak_vs_capacity.py`, `warehouse/replication/siting.py`, `warehouse/analysis/watch.py`; the site's copy for `/demand`, the siting tool and the cost of power page (`site/lib/demandgrowth.ts`, `site/lib/siting.ts`, `site/app/cost-of-power/model.ts`); the live set for `/explore/demand-growth` (`site/lib/explore/demandgrowth.ts`) and the chat (`site/lib/chat/pagefiles.ts`, `ready.ts`).

## Vintage and revision

One build, one retrieval time: `retrieved_at` 2026-10-21T08:07:02Z in all 24,108 rows (header line 4: run `20261021T080702Z`; header line 8: "This run wrote 24108 rows: 24108 new, 0 replacing ... 0 rows are kept from earlier runs"). `vintage` is blank. EIA revises its hours and each build reads the newest workbook, so a figure can move from one build to the next; the year to date also moves with the last whole month (header line 3: "1 January to the end of 09/2026 of each year").

## Shape and variables

Series, 24,108 rows, 14 columns: the series columns and `x_at` (the hour of a peak, its start in UTC; set on the 49 `peak_demand_mw` rows and the 56 `ytd_peak_demand_mw` rows only). `freq` P1Y; units MW, pct and count; `market`, `node` and `vintage` blank; `geo` US-TX (ERCO), US-CA (CISO), US-NY (NYIS) and US for the other five. 985 distinct variables; 3,017 rows an area (2,989 for US48, which has no peak). Rows a year: 2,654 (2019), 2,692 (each of 2020 to 2024), 7,876 (2025, with the 5,184 change rows) and 118 (2026: the year to date and the months to September).

| Family | Rows | Years |
|---|---|---|
| `avg_demand_mw`, `hours_used`, `hours_in_year` | 56 each | 2019 to 2025 |
| `peak_demand_mw` | 49 | 2019 to 2025, not US48 |
| `avg_demand_growth_since_2019_pct`, `avg_demand_growth_yoy_pct` | 48 each | 2020 to 2025 |
| `peak_demand_growth_since_2019_pct` | 42 | 2020 to 2025 |
| `ytd_avg_demand_mw`, `ytd_hours_used`, `ytd_hours_in_window` | 64 each | 2019 to 2026 |
| `ytd_peak_demand_mw` | 56 | 2019 to 2026, not US48 |
| `ytd_avg_demand_growth_since_2019_pct` | 56 | 2020 to 2026 |
| `ytd_peak_demand_growth_since_2019_pct` | 49 | 2020 to 2026 |
| `avg_demand_mw_mMM` | 744 | every month of 2019 to 2025, January to September 2026 |
| `avg_demand_mw_hHH` | 1,344 | 2019 to 2025 |
| `avg_demand_mw_mMM_hHH` | 16,128 | 2019 to 2025, all 288 cells |
| `growth_mw_` and `growth_pct_` of `mMM`, `hHH`, `mMM_hHH` | 96, 192, 2,304 each | 2025 |

Every month, hour and cell that could be written is: no month or year of any area falls under its threshold. The fewest hours used in a year: CISO 2019, 8,725 of 8,760 (99.6 percent). `hours_in_year` is 8,760 or 8,784; `ytd_hours_in_window` 6,551 (6,575 in leap years), the spring clock change taking one hour.

| Area | Mean 2019, MW | Mean 2025 | Growth, percent | Peak 2019 (hour, UTC) | Peak 2025 (hour, UTC) | Growth | Jan to Sep 2026 against 2019 |
|---|---|---|---|---|---|---|---|
| ERCO | 43,797.6 | 55,717.2 | 27.22 | 74,533 (2019-08-12T21) | 83,597 (2025-08-18T22) | 12.16 | 33.10 |
| SWPP | 30,763.9 | 34,190.8 | 11.14 | 50,511 (2019-08-19T21) | 54,411 (2025-07-29T21) | 7.72 | 16.08 |
| PJM | 91,353.9 | 96,257.2 | 5.37 | 152,315 (2019-07-19T21) | 160,560 (2025-06-23T21) | 5.41 | 8.25 |
| CISO | 24,475.8 | 25,565.1 | 4.45 | 43,849 (2019-08-16T00) | 43,860 (2025-08-22T01) | 0.03 | 10.18 |
| MISO | 74,147.0 | 75,780.0 | 2.20 | 116,600 (2019-07-19T20) | 120,343 (2025-07-24T20) | 3.21 | 4.80 |
| ISNE | 13,502.8 | 13,159.8 | -2.54 | 23,973 (2019-07-30T21) | 25,898 (2025-06-24T22) | 8.03 | -0.87 |
| NYIS | 17,789.4 | 17,304.1 | -2.73 | 30,397 (2019-07-20T20) | 31,857 (2025-06-24T22) | 4.80 | -3.37 |
| US48 | 458,599.1 | 490,819.4 | 7.03 | none | none | | 10.26 |

## Placing values in time, and what is filled

`ts_utc` is the first day of the local year written as midnight UTC: a label, not an instant. Years, months and hours of the day are the area's local time (America/Chicago for ERCO, MISO and SWPP; America/Los_Angeles for CISO; America/New_York for PJM, NYIS, ISNE and US48); `x_at` is the peak's hour start in UTC. EIA's `UTC time` is the hour's end, and one hour is subtracted. California's hours stamped from 2023-10-31T23:00Z to 2025-12-02T22:00Z are moved one hour earlier, and the hour that leaves empty (2025-12-02T22:00Z) is not filled. Nothing is filled: an hour not used is in no mean. Hours held and not used, from 2019 to the workbook's end: CISO 38, PJM 7, SPP 2, US48 1 (each apart from the hours around it) and NYIS 12 (zero); the range test removes none in this build. Blank in the workbook to the end of September 2026: ERCO 24 hours (all of 5 December 2025, Central), CISO 24 (all of 2 November 2024, Pacific) and PJM 3 (23:00 Eastern on the fall clock-change days of 2023 to 2025); none for the others.

## License

Header line 7: "License: public (EIA publications are in the public domain)". `coverage.csv` and `sources.csv`: public. `license_verdicts.csv`, EIA (read 1): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", "may be public", if the ERW sells anything "may be public", with the acknowledgment "Source: U.S. Energy Information Administration". `docs/licenses.md`, the table's row: EIA, "may be public", flag public, "agrees", ERW verdict public. `license_tables.csv`: "by hand: its header: EIA publications". No row in `license_status.csv`.

## Checks (session 2298)

The figures in this note were computed from the rows of `warehouse/output/eia930_demand_growth.csv`, read past its 8 header lines (counted), by `runs/c105/s2298/check_eia930_demand_growth.py` and `check_eia930_demand_growth_detail.py`; EIA's hourly demand was read from the eight workbooks named in header line 6 by `wb_demand.py` into `wb_<BA>.csv` (outputs beside them).

- 24,108 rows and the range 2019-01-01 to 2026-01-01, as header line 8 states; no (entity, variable, ts_utc) twice; every `ts_utc` a 1 January.
- **Its arithmetic:** all 5,427 growth values, recomputed from the table's own means and peaks (since 2019, on the year before, and the 5,184 changes in MW and percent), equal the table's.
- **Computed again from EIA's workbooks,** with the rule written out in the check script rather than by importing the builder: all 24,108 values and all 105 `x_at` equal the table's. The hours left out are those `demand_growth.md` names (its table "As built"), the California check across 16 December gives its seven rows (2025: 24,766.8 and 24,196.6 MW, ratio 0.9770), and ERCOT's 2023 peak is 85,432 MW (2023-08-10T22:00Z).
- **Against EIA's hourly route** (`eia930_all_demand`, EIA's API, from 2026-08-26): EIA's hourly demand there equals the workbook's on every common hour for CISO, PJM, MISO, SWPP, NYIS and ISNE, on 1,178 of 1,181 for ERCO, and on 666 of 1,300 for US48. September 2026: the mean of that table's hours equals `avg_demand_mw_m09` of 2026 for CISO (30,255.4), PJM, MISO and ISNE, which hold all 720 hours there; ERCO, NYIS and SWPP lack two days of that month in that table (ratios 0.9994, 0.9898 and 1.0082); US48 0.9999.
- **Against EIA's daily route** (`eia930_daily_demand`, EIA's Eastern day): the daily value equals the workbook's hourly Demand summed over the Eastern day on 2,752 to 2,808 of about 2,850 days for each ISO, and on 1,361 of 2,848 for US48. The mean MW of an Eastern year from that table, against this one's local-year mean: 2019, ERCO 43,797.6 and 43,797.6, ISNE 13,502.8 and 13,502.8, the others within 0.12 percent; growth 2019 to 2025, that table against this one: ERCO 27.40 and 27.22, SWPP 11.42 and 11.14, PJM 5.31 and 5.37, CISO 4.60 and 4.45, MISO 2.59 and 2.20, ISNE -2.55 and -2.54, NYIS -2.77 and -2.73, US48 7.01 and 7.03. The daily route (its rows of 2025 pulled on 4 October 2026) and the workbooks of 19 October disagree on 39 to 84 days of 2025 for each grid, many of them in November and December: MISO's daily values exceed the workbook's Adjusted demand summed on 48 days by 2,487,424 MWh in all, about 284 MW over the year, nearly all of MISO's gap of 283.3 MW. The screen, the adjusted column and the local year make the rest (CISO's 38 hours left out in 2019, for one).
- **Against the site's copy** (`site/data/demand_growth.json`, built 2026-10-05T02:07:23Z): 24,104 of its 24,108 values equal the table's. The four that differ are US48's of 2026: `ytd_avg_demand_mw` 516,203.6 there and 516,235.6 here, `avg_demand_mw_m08` 592,625.6 and 592,629.3, `avg_demand_mw_m09` 541,210.6 and 541,498.5, `ytd_avg_demand_growth_since_2019_pct` 10.25 and 10.26.

## Where the description and the data disagree

1. **The rule as written leaves out its range test.** Header line 3 ("An hour is used when its demand is above zero and within 25% of the median of the four hours around it"), the builder's docstring, `demand_growth.md` ("Which hours are used") and `faults.yaml` state three tests. The builder calls `impossible_hours.screen(d, JUMP)`, which since session 118 also leaves out an hour outside a third to three times the area's median hour (`RANGE`). In this build that test removes no hour, so no figure depends on it.
2. **"Parts of 5 to 14 December 2025."** `demand_growth.md` ("Texas, December 2025") and SESSION_97_REPORT say EIA's file is blank for ERCOT for parts of 5 to 14 December. In the workbook the table was built from, the 24 blank hours are one whole Central day, 5 December 2025 (2025-12-05T06:00Z to 2025-12-06T05:00Z). The count (8,736 of 8,760 hours of 2025) holds.
3. **"Blank" counts the workbook's empty tail.** The table "As built" in `demand_growth.md` (ERCOT 48, CAISO 48, PJM 27, the others 24), the site copy's `screened.blank`, and `faults.yaml` for PJM ("27 more hours are blank") count, for every area, the 24 empty rows the workbook carries after its last reported hour (2026-10-19 and 20). The blanks inside the record are 24 for ERCO, 24 for CISO, 3 for PJM and none for the other five.
4. **Coverage calls it a source table of an ISO named DEMAND.** `coverage.csv` gives `iso` "DEMAND" (the fallback of `build_coverage.iso_of` for a name beginning `eia930_`), `derived` no and `tier` source. It holds the seven ISO balancing authorities and US48 and is computed by the ERW (`sources.csv`: "Energy Research Warehouse (ERW), derived"; the docstring: "One derived table").
5. **The site's copy and the table differ.** `demand_growth.md` ("Checks": "the site's copy equal to the table") and SESSION_97_REPORT ("The site's copy equal to the table, row for row") describe the two as equal. Since session 438's rebuild without `--snapshot`, four US48 values of 2026 differ, so `/demand` (the copy) shows US48's growth so far at 10.25 percent and `/explore/demand-growth` (the live set) at 10.26.
6. **The faulty hours' times in `impossible_hours.py`.** Its docstring gives "PJM at 224,345 MW at 18:00 UTC on 13 July 2020" and "SPP at 1,505 MW at 04:00 UTC on 21 June 2025". The hours are 22:00 and 09:00 UTC; 18:00 and 04:00 are the local times, as `demand_growth.md` and `faults.yaml` give them.
7. **"The two before and the two after that are held."** `demand_growth.md` and the docstring describe the four hours around an hour this way, which can be read as the nearest held hours. The rule takes the two hours before and the two after; one that is blank or not above zero drops out of the median and is not replaced by a further hour (`impossible_hours.py` says so: "those of them that are held and above zero").

Not acted on: this note changes no file but itself.

## The session report against the table

- `SESSION_97_REPORT.md`: 24,108 rows, eight areas; its table of means, peaks, growth and the year so far: every figure holds to its rounding, except US48's growth so far, 10.25 then and 10.26 now (session 438). ERCOT's cells ("every one of the 288 cells grew; the most in January at 02:00 (+42.55 percent, 15,250 MW) and the least in September at 14:00 (+14.29 percent)") hold: 288 cells, none below zero, 42.55 percent and 15,250.2 MW, 14.29 percent. The hours left out ("7 hours of PJM, 38 of California ... 12 hours of zero in New York, 2 of SPP") hold. The blank days of ERCOT's December 2025 are item 2 above.
- `SESSION_438_REPORT.md`: the rebuild of 21 October 08:07 UTC with four US48 values revised: these are the four values that differ from the site's copy.

## What it does not hold

- A weather adjustment (`eia930_demand_weather`, `docs/methods/demand_weather.md`); balancing authorities outside the seven ISOs; a peak for US48; whole years before 2019 or a whole 2026; any hour (`eia930_all_demand` from 26 August 2026; EIA's daily route `eia930_daily_demand` from 2019); EIA's unadjusted demand for a balancing authority; the instant peak an operator measures over minutes; earlier builds of the table (each build replaces it whole).
