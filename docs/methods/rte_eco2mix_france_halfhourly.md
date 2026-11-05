# France's consumption, production by source and net physical exchanges every half hour, 2020 to August 2026 (RTE's eco2mix national files)

Energy Research Warehouse (ERW), method note written in session 2247 (chain 101) for a table first written on 24 October 2026 (session 2238 of chain 101, its report `archive/sessions/SESSION_2238_REPORT.md`).

Tables: `rte_eco2mix_france_halfhourly`

## Publisher and address

RTE (Reseau de Transport d'Electricite), France's transmission system operator, eco2mix, the national definitive and consolidated files. The page in the header is `https://www.rte-france.com/eco2mix/telecharger-les-indicateurs` (it answers from `https://www.rte-france.com/donnees-publications/eco2mix-donnees-temps-reel/telecharger-indicateurs`, read 362). Its script `eco2mix_dl.js` (read 364) builds the files' addresses, and `https://eco2mix.rte-france.com/curves/getInfoDl` (read 363) lists the definitive years 2012 to 2025. The files:

- `https://eco2mix.rte-france.com/download/eco2mix/eCO2mix_RTE_Annuel-Definitif_<year>.zip`, 2020 to 2025;
- `https://eco2mix.rte-france.com/download/eco2mix/eCO2mix_RTE_En-cours-Consolide.zip`, this year.

Each zip holds one tab-separated text file named `.xls`, in Windows-1252, 40 columns, one line every quarter hour of French local time, 96 lines a day (35,136 lines in 2020 and 2024, 35,040 in 2021, 2022, 2023 and 2025, 23,328 from 1 January to 31 August 2026), and a closing disclaimer line ("RTE ne pourra etre tenu responsable ..."). The measures are filled on the :00 and :30 lines; the :15 and :45 lines carry only the two forecasts and the commercial exchanges. Source id `rte:eco2mix_national`.

Session 2238's probe (`runs/c101/s2238/probe.csv`) made 14 requests. ODRE's robots file closes `odre.opendatasoft.com` to every reader but Googlebot (read 359), so RTE's own host is used; `eco2mix.rte-france.com` has no robots file (read 360, HTTP 404); `www.rte-france.com`'s disallows admin, search, user and filter paths only (read 361). The seven zips (HTTP 200, 955,237 to 1,410,627 bytes) are saved in `runs/license_reads/s2238/` (08 to 14) and seeded into `warehouse/raw/rte_eco2mix/20261024T030508Z_probe/`; the trial and the write read them offline.

Connector: `warehouse/connectors/rte_eco2mix.py` (session 2238): `[--first 2020] [--last 2025] [--offline] [--out-dir DIR]` (the docstring's usage line omits `--last`), one request a year and one for this year. Fifteen of the 40 columns are taken. A header not RTE's, a perimeter not France, a value that is not a number, a date or hour not in RTE's form, or a half hour given twice stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

One run, `20261024T031222Z`, written offline from the seven files retrieved from 2026-10-24T03:06:36Z to 03:06:47Z (`retrieved_at` is each file's): "This run wrote 1647503 rows: 1647503 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs." `vintage` is each zip's Last-Modified:

| File | Rows | `vintage` | `x_nature` |
|---|---|---|---|
| 2020 | 193,204 | 2023-02-09T13:08:49Z | Donnees definitives |
| 2021 | 227,706 | 2024-05-16T15:29:17Z | Donnees definitives |
| 2022 | 262,738 | 2025-06-25T11:26:58Z | Donnees definitives |
| 2023 | 262,740 | 2025-06-25T13:41:41Z | Donnees definitives |
| 2024 | 263,460 | 2026-03-19T04:07:52Z | Donnees definitives |
| 2025 | 262,740 | 2026-10-06T10:02:20Z | Donnees definitives |
| En-cours-Consolide | 174,915 | 2026-10-06T10:02:08Z | Donnees consolidees |

(`x_nature` keeps RTE's accented words; they are written here without accents.) A definitive file is not frozen: each was last modified one to three years after its year ended. The consolidated file holds 1 January to 31 August 2026 and is not yet definitive. A later run merges by (entity, variable, ts_utc): a revised value replaces the old one, but a half hour RTE later prints as "ND" writes no row, so the earlier value would be kept.

## Shape and variables

Series, 1,647,503 rows, one entity `rte_eco2mix:FR`, `node` France, `geo` FR, `unit` MW, `freq` PT30M, `market` blank; `x_local_date` and `x_local_hour` are RTE's date and hour.

| Variable | Rows | First ts_utc | Mean | Lowest (ts_utc) | Highest (ts_utc) | Zeros |
|---|---|---|---|---|---|---|
| consumption | 116,853 | 2019-12-31T23:00Z | 51,014.3 | 29,124 (2020-05-10T05:00Z) | 90,236 (2026-01-06T09:00Z) | 0 |
| nuclear | 116,853 | 2019-12-31T23:00Z | 38,936.3 | 19,164 (2022-09-03T13:00Z) | 56,312 (2025-12-31T08:00Z) | 0 |
| hydro | 116,853 | 2019-12-31T23:00Z | 7,035.3 | 1,532 (2022-09-23T01:00Z) | 17,947 (2023-01-24T18:00Z) | 0 |
| wind | 116,853 | 2019-12-31T23:00Z | 5,047.8 | 43 (2025-12-13T13:00Z) | 20,138 (2025-10-23T11:30Z) | 0 |
| gas | 116,853 | 2019-12-31T23:00Z | 3,172.2 | 131 (2026-06-04T10:00Z) | 10,591 (2022-12-16T16:00Z) | 0 |
| solar | 116,853 | 2019-12-31T23:00Z | 2,644.3 | 0 | 25,068 (2026-08-07T12:00Z) | 40,804 |
| bioenergy | 116,853 | 2019-12-31T23:00Z | 1,183.7 | 863 (2020-10-06T06:30Z) | 3,252 (2021-03-25T14:30Z) | 0 |
| coal | 116,853 | 2019-12-31T23:00Z | 182.2 | 0 | 2,311 (2021-01-11T09:30Z) | 3,599 |
| oil | 116,853 | 2019-12-31T23:00Z | 108.9 | 27 (2023-06-24T20:00Z) | 1,734 (2022-01-25T08:30Z) | 0 |
| pumping | 116,853 | 2019-12-31T23:00Z | -796.4 | -4,086 (2021-12-26T04:00Z) | -3 (2021-01-05T20:00Z) | 0 |
| physical_exchanges | 116,853 | 2019-12-31T23:00Z | -6,438.8 | -21,063 (2025-12-07T19:30Z) | 14,608 (2022-12-08T08:00Z) | 4 |
| wind_onshore | 81,772 | 2021-12-31T23:30Z | 4,941.9 | 53 (2025-12-13T13:00Z) | 18,499 (2024-12-07T11:30Z) | 0 |
| wind_offshore | 81,772 | 2021-12-31T23:30Z | 399.5 | 0 | 1,963 (2026-08-31T01:00Z) | 7,747 |
| battery_charging | 99,288 | 2020-12-31T23:30Z | 0 | 0 | 0 | 99,288 |
| battery_discharging | 99,288 | 2020-12-31T23:30Z | 0 | 0 | 0 | 99,288 |

Means rounded to one decimal; RTE gives whole MW.

- **Signs.** Pumping is negative in every row, as the header says. physical_exchanges is negative in 96,395 half hours and positive in 20,454: negative is a net export, positive a net import (production plus exchanges less consumption is a median 65 MW, the cross-check below). The header says only "(net)".
- **Battery charging and discharging are 0 in every row** (disagreement 3). In the 2020 file both columns are "ND" in every line, so they have no row before 2021.
- **Wind's split.** In 2021 RTE prints 0 for both onshore and offshore beside a total that is not 0; those are left out (disagreement 2). From 2022 the split is kept as published: onshore plus offshore exceeds wind by more than 1 MW in 1,800 of 81,772 half hours (448 in 2022, 703 in 2023, 486 in 2024, 112 in 2025, 51 in 2026, by at most 28 MW) and never falls short of it by more than 1 MW; onshore alone exceeds wind in 2,175 half hours. Offshore is 0 in 7,747 half hours (6,053 of them in 2022, 67 in 2026); its first value above 0 is at 2022-01-06T17:00:00Z.

In 2025 (French local days, 17,516 half hours): consumption 443.788 TWh, nuclear 372.964, hydro 61.925, wind 49.604 (onshore 43.898, offshore 5.706), solar 32.507, gas 16.386, bioenergy 10.876, oil 0.810, coal 0.670, pumping -8.131 and physical exchanges -93.143 (a net export), each the half hours' MW times half an hour.

## Placing values in time, and what is filled

`ts_utc` is the half hour's start in UTC, from RTE's date and hour in French local time (Europe/Paris). Turned back to Paris time, every row's `ts_utc` gives its `x_local_date` and `x_local_hour` (0 rows differ). The rows hold 116,853 distinct half hours from 2019-12-31T23:00:00Z (00:00 on 1 January 2020) to 2026-08-31T21:30:00Z (23:30 on 31 August 2026); the span holds 116,878, so 25 are absent for every variable:

- **The autumn change, 24 half hours.** RTE prints 02:00 and 02:30 once on the last Sunday of October, though French time passes them twice. The connector leaves both lines out, so four UTC half hours, 00:00 to 01:30Z, have no row: on 2020-10-25, 2021-10-31, 2022-10-30, 2023-10-29, 2024-10-27 and 2025-10-26. Which of the two passes RTE's values describe, the files do not say.
- **The spring change.** RTE prints 02:00 and 02:30 on the last Sunday of March, times French time skips. These two lines are left out, and no UTC half hour is lost. In the files the 02:00 line repeats the 03:00 line in all fifteen measures in every year 2020 to 2026; the 02:30 line repeats 01:30 in 2020, 2025 and 2026 and 03:30 in 2021 to 2024.
- **1 January 2026 at 00:00**, 2025-12-31T23:00:00Z: the consolidated file's first line is "ND" in every measure, so no variable has a row there.

Counted from the saved zips (`rte_raw.py`): 14 spring lines (two in each year 2020 to 2026) and 12 autumn lines (two in each year 2020 to 2025), as the header states. The battery series lack 21 half hours inside their span (20 at the autumn changes of 2021 to 2025, and 1 January 2026), the wind split 17 (16 and 1 January 2026).

The files do not say whether a value is the reading at the half hour or the mean over it; the cross-check's energy (MW times half an hour) takes it as the mean. "ND" and a blank have no row; nothing is filled.

## License

Header: "License: public. RTE's legal notice: the data published on www.rte-france.com are public and their reuse is permitted provided the source is cited; their modification is forbidden (values kept as published, reshaped from wide to long). Cite: RTE, eco2mix." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 365 (session 2238, RTE's legal notice, `https://www.rte-france.com/mentions-legales`), "Les donnees publiees sur le portail www.rte-france.com sont publiques et leur reutilisation est permise sous reserve de mentionner la source. Toutefois la modification, la denaturation totale ou partielle du site ou de son contenu, par quelque procede que ce soit, et sur quelque support que ce soit est interdite." (accents and RTE's quotation marks dropped here), verdict "may be public", if the ERW sells anything "may be public"; the table's row: flag public, "agrees", ERW verdict public.

## Checks (session 2247)

The figures in this note were computed from the rows of `warehouse/output/rte_eco2mix_france_halfhourly.csv`, read past its 10 header lines (counted), and from the saved zips, read only (scripts `runs/c101/s2247/rte.py`, `rte2.py`, `rte_raw.py`, `rte_raw2.py` and `rte_raw3.py`, outputs beside them).

- 1,647,503 rows, `ts_utc` from 2019-12-31T23:00:00Z to 2026-08-31T21:30:00Z, as header line 10 states; each variable's rows and first day as header line 3 lists them (its dates are UTC days: the battery series begin at 2020-12-31T23:30:00Z, the wind split at 2021-12-31T23:30:00Z); no (entity, variable, ts_utc) twice; no blank value; unit MW, freq PT30M and geo FR throughout.
- The trial's table (`runs/c101/s2238/trial/rte_eco2mix_france_halfhourly.csv`, run `20261024T031107Z`) has the same rows past its header, byte for byte; the headers differ only in the run's name and log.
- Session 2238's cross-check (`runs/c101/s2238/cross.py`), run again from the main checkout with the written table as argument 1: its output is identical to the saved `cross.out`, which was run on the trial. A year's consumption against Ember's French demand (`owid_ember_electricity_annual`): 0.9259 (2020), 0.9269, 0.9328, 0.9300, 0.9326 and 0.9310 (2025: 443.788 against 476.66 TWh). Production plus physical exchanges less consumption over 116,853 half hours: median 65.0 MW, 5th percentile -1.0, 95th 118.0, a median 0.130 percent of consumption. Wind against onshore plus offshore: 81,772 half hours, at most 28.0 MW apart, 1,800 above 1 MW. Nuclear 335.1, 360.4, 278.8, 320.1, 361.6 and 373.0 TWh, 2020 to 2025.
- From the saved zips (`rte_raw.py`): the counts the header gives, 14 spring lines, 12 autumn lines and 17,520 lines with a zero wind split; the spring lines' repeats (`rte_raw2.py`); the 2020 file's battery and split columns "ND" in all 17,568 filled lines.

## Where the description and the data disagree

1. **The autumn change counts RTE's lines, not the table's gaps.** The header and the report say 12 half hours "of the autumn change that occur twice" are left out. They are 12 of RTE's lines; in UTC time 24 half hours have no row, four on each last Sunday of October from 2020 to 2025. A reader counting half hours finds two hours a year missing, not one.
2. **The zero wind split is not exactly "all of 2021".** The 17,520 half hours the header counts are 17,519 lines of the 2021 file (every filled line but the first, 00:00 on 1 January 2021, whose split is "ND") and one of the 2022 file, its first line (00:00 on 1 January 2022), where onshore and offshore are both 0. Four of the 2021 lines are change-of-hour lines, left out anyway. The table is right either way: the split has no row before 2021-12-31T23:30:00Z.
3. **The battery series hold only zeros.** The header and the report list battery_charging and battery_discharging among fifteen measures in MW; RTE's files give 0 in every one of their 99,288 half hours (2021 to August 2026), and "ND" in 2020. The files do not say whether 0 means no battery operation or a measure not filled; a reader should not take these rows as measured battery output.
4. **Commercial exchanges by border, which are not taken, are not all hourly.** The docstring calls them "hourly values repeated on every quarter hour". In the files the England column is (one hour in 2020 aside), but the Germany-Belgium column changes within the hour in most hours of every year (6,365 of 8,784 in 2020, 8,100 of 8,760 in 2025, every hour of 2026), Switzerland's in 988 to 2,018 hours a year, and Spain's and Italy's in thousands of hours since 2025. It bears only on a column the table leaves out.

Not acted on: this note changes no file but itself.

Acted on in session 2247. The battery charging and discharging columns, 0 in every half hour, are a placeholder and are no longer taken; the table was written again offline, its file removed first under the data lock so that their rows did not stay (1,448,927 rows, 198,576 rows of zeros fewer). The docstring and header now say that the autumn hour's two UTC hours both have no row (RTE's 12 lines, 24 half hours), and that the commercial exchanges by border change within the hour for some borders. The zero wind split's 17,520 lines are 2021's and the first line of 2022 in French time, as the count says; "mainland France" in session 2238's report is withdrawn: the files say France.

## The session report against the table

Every figure of `SESSION_2238_REPORT.md` checked against the table, the saved zips and the rerun cross-check holds (2020 to August 2026, 1,647,503 rows, fifteen measures in MW, the definitive years 2020 to 2025 and this year's consolidated file, 96 quarter hours a day, 14 spring half hours whose values repeat their neighbours', 1,800 of 81,772 half hours more than 1 MW apart and at most 28 MW, 0.926 to 0.933 of Ember's demand, 443.788 against 476.66 TWh, a median 65 MW or 0.13 percent over 116,853 half hours, nuclear 335.1 to 373.0 TWh with 2022's 278.8, 14 requests), except:

- "On the autumn change they print the doubled hour once ... 12 half hours were left out": 12 lines, 24 UTC half hours (disagreement 1).
- "in all of 2021, RTE prints 0 for both onshore and offshore ... (17,520 half hours)": 17,519 in 2021 and one in 2022 (disagreement 2).
- "Fifteen measures in MW every half hour: ... battery charging and discharging": two of the fifteen are 0 throughout (disagreement 3).
- "eco2mix covers mainland France": the files' perimeter is "France"; none of the pages read says mainland.

## What it does not hold

- The day-ahead and same-day forecasts, the CO2 rate (no unit in the files), the commercial exchanges by border and the sub-sources (oil, gas, hydro and bioenergy by kind, among them gas combined cycles and pumped-storage turbining), which the files carry; the regional and metropolitan files, the energy files and the real-time file (`eCO2mix_RTE_En-cours-TR.zip`) that the download script names; the definitive years 2012 to 2019; anything after 31 August 2026; and the four autumn half hours a year that RTE prints once.
