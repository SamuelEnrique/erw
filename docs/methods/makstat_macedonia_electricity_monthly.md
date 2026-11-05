# North Macedonia's electricity a month by indicator, January 2012 to July 2026 (MakStat table 125_Ene_Mk_EEmes_ml)

Energy Research Warehouse (ERW), method note written in session 2366 (chain 110) for a table first written on 24 October 2026 (session 2357, `archive/sessions/SESSION_2357_REPORT.md`, "queue file 112 first; Pakistan closed, North Macedonia's electricity in its place (MakStat)", commit `f21b3e69`). Eurostat's monthly figures for North Macedonia, the table this one is checked against, are in `eurostat_electricity_monthly` (`docs/methods/eurostat_electricity_monthly.md`). Moldova's monthly balance, read the same way in the next session, is `statbank_moldova_electricity_monthly` (`docs/methods/statbank_moldova_electricity_monthly.md`). Read first: the line MakStat calls "Gross inland consumption" is imports less exports in every month, not a consumption (below, and disagreement 1).

Tables: `makstat_macedonia_electricity_monthly`

## Publisher and address

State Statistical Office of North Macedonia, MakStat (PxWeb), Energy, Monthly energy statistics, table 125_Ene_Mk_EEmes_ml, "Electricity in MWh, by months", page `https://makstat.stat.gov.mk/PXWeb/pxweb/en/MakStat/MakStat__Energija__MesecEnergetStatistiki/125_Ene_Mk_EEmes_ml.px/`. Read through the PxWeb API (no key) at `https://makstat.stat.gov.mk/PXWeb/api/v1/en/MakStat/Energija/MesecEnergetStatistiki/125_Ene_Mk_EEmes_ml.px`: the table's metadata by GET (3,580 bytes) and one JSON-stat 2.0 query by POST for every cell (27,727 bytes). The metadata has two variables, `Индикатор` (Indicator, 21 values, codes 0 to 20) and `Година и месец` (Year and Month, 175 values, 2012M01 to 2026M07). The answer's `source` is "State Statistical Office", its `extension` `{'px': {'decimals': 0}}`. Source id `makstat:125_Ene_Mk_EEmes_ml`; `sources.csv`: publisher "State Statistical Office of North Macedonia (MakStat)", report "MakStat table 125_Ene_Mk_EEmes_ml: Electricity in MWh, by months", license internal, first and last seen 2026-10-24.

The requests, all of 24 October 2026:

- session 2357's probe read the metadata at 08:25:16Z (read 593; copy `runs/license_reads/s2357/11_...125_ene_mk_eemes_ml_px.bin`);
- the connector's first trial, run `20261024T082615Z`, read it again at 08:26:16Z and stopped on a month label (`runs/c110/s2357/trial/logs/`);
- the second trial, run `20261024T082652Z` (with `--out-dir runs/c110/s2357/trial`), read it at 08:26:53Z and sent the query at 08:26:55Z. Its log: "POST ...: 27727 bytes, saved with the metadata as ...\query_125_Ene_Mk_EEmes_ml.json".

The saved file, `warehouse/raw/makstat_macedonia/query_125_Ene_Mk_EEmes_ml.json` (`retrieved_at` 2026-10-24T08:26:55Z, the query, the metadata and the answer), is what every later run reads. Both raw copies of the metadata (run folders `20261024T082615Z` and `20261024T082652Z`) and the probe's copy equal its metadata, and the raw copy of the answer (`20261024T082652Z/..._00002_125_Ene_Mk_EEmes_ml.px`) equals its answer. The run that wrote the table, `20261024T082751Z`, read it offline ("saved metadata and answer reused", `warehouse/output/logs/makstat_macedonia_20261024T082751Z.log`); its raw folder holds only the data lock's check. makstat.stat.gov.mk has no robots file (HTTP 404, read 589).

Connector: `warehouse/connectors/makstat_macedonia.py` (session 2357), `--offline` and `--out-dir`. It asks `iso_prices.paused` and `iso_prices.paused_host("makstat.stat.gov.mk")` first; neither names MakStat. It stops if the metadata does not have two variables, if the indicator texts (leading dots and spaces removed) are not the 21 expected, if a month label is not `YYYYMmm`, `YYYY_mm` or `YYYY` with the Cyrillic letter Em and `mm`, if the answer's dimensions are not the two or its values not their size, or if an indicator and month come twice. Each value is MakStat's figure as published; `vintage` is the answer's `updated` field. The file is a snapshot (`write_snapshot`). Ceiling: two requests a run.

Schedule: none. No run script, workflow, step of `warehouse/scheduled.py` or file in `scripts/` names the connector.

`run_status.csv`: no row (the run wrote `runs/status/makstat_macedonia.json`, run `20261024T082751Z`, "ok", "3669 rows"; disagreement 7). `archive_manifest.csv`: 3,669 rows, run `20261024T082755Z-local`, data hash `46fd1ea5...`, which equals the hash of the file on this machine. `redivis_uploads.csv` and `redivis_uploads_stanford.csv`: no row. Live set: in `catalogue_hold` of `warehouse/supabase/live_set.yaml` (not loaded). Readers: none. `build_coverage.py` gives it the sector `power`, and `tests/test_session2357.py` tests the parse (3 tests).

## Vintage and revision

One retrieval: every row's `retrieved_at` is 2026-10-24T08:26:55Z. Every row's `vintage` is 2013-04-23T12:00:00Z, the answer's `updated` field, a date before every month from May 2013 to July 2026 that the table holds; it is not when these figures were published (disagreement 2). MakStat's API gives no other date. The file is a snapshot: a later run replaces it, and MakStat's revisions of a month, if any, would show only by comparing with the archive's copy. Nothing earlier is kept.

## Shape and variables

Series, 3,669 rows, 14 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_code`), 10 header lines. One entity, `makstat:mk`; unit MWh; `freq` P1M; `geo` MK; `market` blank; `node` the indicator's text with MakStat's leading dots removed; `x_code` MakStat's code. Every value is a whole number (MakStat's decimals: 0). 21 variables, 2012-01 to 2026-07 (175 months):

| x_code | Variable | MakStat's text | Months | Mean | Lowest (month) | Highest (month) | Negative, zero |
|---|---|---|---|---|---|---|---|
| 0 | `imports` | Imports | 175 | 196,820.4 | 65,447 (2023-01) | 409,589 (2020-12) | 0, 0 |
| 1 | `exports` | Exports | 175 | 42,971.0 | 0 (2012-10) | 177,822 (2024-08) | 0, 21 |
| 2 | `gross_inland_consumption` | Gross inland consumption | 175 | 153,849.4 | -60,362 (2023-03) | 368,419 (2014-01) | 13, 0 |
| 3 | `gross_production_total` | Total Gross Electricity production | 175 | 487,690.6 | 254,678 (2014-08) | 751,553 (2023-01) | 0, 0 |
| 4 | `gross_production_thermal_power_plants` | ..Thermal Power Plants | 175 | 268,310.7 | 111,836 (2018-05) | 514,510 (2013-01) | 0, 0 |
| 5 | `gross_production_chp_and_autoproducer_thermal` | ..CHP plants and Autoprod. thermal power stations | 174 | 68,557.2 | 0 (2012-06) | 172,991 (2021-10) | 0, 30 |
| 6 | `gross_production_hydro` | ..Hydro Power Plants | 175 | 120,606.7 | 31,956 (2020-11) | 247,406 (2015-04) | 0, 0 |
| 7 | `gross_production_solar` | ..Solar Plants | 175 | 17,527.5 | 106 (2012-01) | 181,914 (2025-06) | 0, 0 |
| 8 | `gross_production_wind` | ..Wind power plants | 175 | 9,871.4 | 0 (2012-01) | 34,784 (2025-10) | 0, 27 |
| 9 | `gross_production_biogas` | ..Biogas plants | 172 | 3,251.0 | 0 (2012-01) | 6,610 (2023-12) | 0, 37 |
| 10 | `net_production_total` | Total Net Electricity production | 175 | 457,654.6 | 237,290 (2014-08) | 705,161 (2023-01) | 0, 0 |
| 11 | `net_production_thermal_power_plants` | .. Thermal Power Plants | 175 | 241,236.9 | 99,467 (2018-05) | 469,506 (2013-01) | 0, 0 |
| 12 | `net_production_chp_and_autoproducer_thermal` | .. CHP plants and Autoprod. thermal power stations | 175 | 66,109.2 | -1,170 (2016-03) | 168,665 (2021-10) | 39, 0 |
| 13 | `net_production_hydro` | .. Hydro Power Plants | 175 | 119,745.4 | 31,499 (2020-11) | 245,891 (2015-04) | 0, 0 |
| 14 | `net_production_solar` | .. Solar Plants | 175 | 17,527.5 | 106 (2012-01) | 181,914 (2025-06) | 0, 0 |
| 15 | `net_production_wind` | .. Wind power plants | 175 | 9,866.1 | -5 (2014-03) | 34,784 (2025-10) | 1, 26 |
| 16 | `net_production_biogas` | .. Biogas plants | 173 | 3,206.1 | 0 (2012-01) | 6,258 (2023-12) | 0, 37 |
| 17 | `energy_branch_consumption` | Consumption of the energy branch | 175 | 9,238.5 | 3,774 (2024-07) | 19,198 (2012-02) | 0, 0 |
| 18 | `distribution_losses` | Distribution losses | 175 | 85,989.6 | 38,664 (2022-09) | 192,111 (2012-01) | 0, 0 |
| 19 | `available_for_final_consumption` | Available for final consumption | 175 | 516,274.5 | 323,974 (2024-09) | 724,454 (2012-01) | 0, 0 |
| 20 | `final_consumption_households` | Final electricity consumption in households | 175 | 260,722.2 | 94,574 (2018-05) | 426,367 (2017-01) | 0, 0 |

MWh a month. MakStat writes the gross plants with two dots and the net plants with two dots and a space; the table's `node` drops both, so a gross plant and its net plant share one `node` (15 distinct texts for 21 indicators; disagreement 3).

By year, TWh (2026 is January to July):

| | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Gross production | 6.262 | 6.094 | 5.374 | 5.646 | 5.630 | 5.600 | 5.607 | 5.870 | 5.347 | 5.532 | 5.828 | 6.826 | 5.685 | 6.472 | 3.574 |
| Net production | 5.798 | 5.672 | 4.976 | 5.278 | 5.284 | 5.227 | 5.283 | 5.501 | 5.033 | 5.228 | 5.419 | 6.433 | 5.361 | 6.163 | 3.433 |
| Imports | 2.741 | 2.491 | 3.073 | 2.656 | 2.191 | 2.294 | 2.297 | 2.411 | 2.965 | 2.837 | 1.936 | 1.470 | 2.067 | 2.087 | 0.929 |
| Exports | 0.072 | 0.062 | 0.113 | 0.143 | 0.160 | 0.311 | 0.377 | 0.583 | 0.639 | 0.359 | 0.523 | 1.319 | 1.356 | 1.164 | 0.338 |
| "Gross inland consumption" | 2.669 | 2.428 | 2.960 | 2.513 | 2.031 | 1.983 | 1.920 | 1.828 | 2.327 | 2.478 | 1.413 | 0.150 | 0.710 | 0.923 | 0.592 |
| Households | 3.263 | 3.065 | 3.046 | 3.142 | 3.057 | 3.097 | 2.999 | 3.040 | 3.191 | 3.317 | 3.080 | 2.996 | 3.149 | 3.221 | 1.965 |

The gross production row equals header line 3's figures to two decimals.

- **"Gross inland consumption" is net imports.** In all 175 months it equals imports less exports exactly. It is negative in the 13 months in which exports exceed imports (2022-09 -50,225; 2023-01 -35,829; 2023-02 -46,496; 2023-03 -60,362; 2023-04 -21,494; 2023-06 -50,658; 2023-08 -13,622; 2023-10 -21,717; 2024-06 -39,871; 2024-07 -37,322; 2024-08 -51,959; 2025-07 -36,989; 2025-09 -18,222), and Eurostat's imports less exports for North Macedonia are negative in the same 13 months with the same figures (Checks). Households' final consumption is above it in 156 months. So these months are months of net export, not impossible values (disagreement 1).
- **The balance closes on net production.** Available for final consumption equals net production plus that line less the energy branch's consumption and distribution losses within 1 MWh in 174 of 175 months; December 2015 is 240 MWh short.
- **The plants against MakStat's totals.** Gross total less its six plants (an empty plant counted as 0): 0 in 99 months, 1 MWh either way in 69, 2 MWh in 6, and January 2016 +2,382 MWh. Net: within 2 MWh in every month. In January 2016 the gross biogas cell is 0 while net biogas is 2,382 MWh, the size of the gap; it is the only plant and month whose net is above its gross. So the gross biogas figure of that month is most likely missing, written as 0.
- **Net and gross by plant.** Over all months held in both, net over gross: thermal power plants 0.8991, CHP and autoproducers 0.9698, hydro 0.9929, wind 0.9995, biogas 0.9919, solar 1.0000 (net equals gross in all 175 months).
- **Negative net output.** Net CHP and autoproducers' output is negative in 39 months from 2012-04 to 2026-06 (lowest -1,170 MWh, 2016-03). In 30 of them their gross is 0 and in one (2026-06) their gross cell is empty, so their own use is above their output. Net wind is -5 MWh in 2014-03, with gross 0, the month before wind's first output.
- **When each kind begins.** Wind is 0 until 2014-03 and above 0 from 2014-04. Biogas is 0 to 2014-12, empty (gross) or 0 (net) in 2015-01, above 0 from 2015-02, and 0 again only in gross 2016-01. Solar is above 0 in every month from 2012-01.
- **Imports and exports are not Eurostat's.** In 2016 the year's sums equal Eurostat's (2.191 and 0.160 TWh). From 2017 Eurostat's imports are 2.27 to 4.92 times MakStat's a year and its exports 5.11 to 14.15 times. The difference, net imports, agrees. The files do not say what MakStat's two lines leave out; transit or exchange flows counted by one and not the other would fit.

## Placing values in time, and what is filled

MakStat labels months `YYYYMmm` (168 labels), `YYYY_mm` (6: 2019_09, 2020_07, 2020_08, 2020_12, 2021_03, 2023_09) or, once, `2026` with the Cyrillic letter Em (U+041C) and `01`. The 175 labels run in order with no month skipped. `ts_utc` is the month's first day at 00:00Z; the figures are calendar months, and no hour is implied.

Of the answer's 3,675 cells (21 by 175), 6 are empty, each with status `..`, and have no row: gross CHP and autoproducers 2026-06; gross biogas 2015-01, 2022-10 and 2022-11; net biogas 2022-10 and 2022-11. Nothing is filled.

## License

Header line 9: "License: internal until the licenses' round reads the State Statistical Office's terms. Source: State Statistical Office of North Macedonia." `coverage.csv` and `sources.csv`: internal. `license_tables.csv`: "State Statistical Office of North Macedonia (MakStat)", "the source registry". `docs/licenses.md`, the table's row: "not settled (needs written permission by default)", not read: State Statistical Office of North Macedonia (MakStat), flag internal, "not settled", if the ERW sells anything "may be public" (disagreement 5), ERW verdict internal; and in its list, "not read: State Statistical Office of North Macedonia (MakStat)". No row in `license_verdicts.csv`, `license_status.csv` or `paused_sources.csv`.

`license_reads.csv`: reads 589 to 593 (session 2357: the robots address, HTTP 404; three listings of the API; the table's metadata), 617 (session 2362: www.stat.gov.mk's robots address, HTTP 404) and 618 (session 2362: the office's English home page, `https://www.stat.gov.mk/Default_en.aspx`, "read: (c) State Statistical Office; no terms of reuse linked"). Session 2362 wrote no verdict: "a copyright mark alone is not terms".

## Checks (session 2366)

The figures in this note were computed by `runs/c110/s2366/check_makstat_macedonia_electricity_monthly.py` (output `check_makstat_macedonia_electricity_monthly.out` beside it). It reads the rows of `warehouse/output/makstat_macedonia_electricity_monthly.csv` in the main checkout past its 10 header lines (counted, never parsed as comments), the saved metadata and answer, the raw copies, and `eurostat_electricity_monthly` (entity `eurostat_elec:MK`, past its 11 header lines). No request was made.

- **The table:** 3,669 rows, 2012-01-01T00:00:00Z to 2026-07-01T00:00:00Z, as header lines 1 and 3 state; no (entity, variable, ts_utc) twice; rows in (variable, ts_utc) order; every `ts_utc` a month's first day; no blank value; `coverage.csv` agrees (3,669 rows, the same range, `n_nodes` 15, validator pass, last run 2026-10-24T08:27:51Z).
- **Against the saved answer:** the answer has 3,669 cells with a value and the table 3,669 rows, the same (code, month) pairs both ways, and no value differs. The table's 13 negative months of gross inland consumption equal header line 3's list.
- **Against Eurostat's net production for North Macedonia** (`net_production:TOTAL`, 2016-01 to 2026-08), the table's `net_production_total` over Eurostat's, in the 127 months both hold (2016-01 to 2026-07): median 1.0000 (10th percentile 0.9985, 90th 1.0047); 90 months within 0.1 percent and 121 within 1 percent. The six months off by more than 1 percent: 2018-08 1.1893 (441,962 against 371,625 MWh), 2018-11 1.0208, 2021-05 1.0119, 2021-12 1.0145, 2022-10 0.9868 and 2022-11 0.9892. By year from 0.9973 (2022) to 1.0152 (2018). Gross production over Eurostat's net: median 1.0639.
- **By kind, net, against Eurostat's:** hydro (RA100) median 1.0000, 111 of 127 months within 0.1 percent, 0.9894 to 1.0309; wind (RA300) median 1.0000, 114 of 127, 0.9542 to 1.0692; solar (RA400, from 2017-01) median 1.0000, 89 of 115, but its 90th percentile is 1.6634 and its highest 2.2469 (2021-06: 5,851 against 2,604 MWh). Thermal power plants, CHP and autoproducers and biogas together against combustible fuels (CF): median 1.0000, 91 of 127 within 0.1 percent, highest 1.4495 (2016-09); thermal power plants alone are a median 0.7236 of CF. Distribution losses against Eurostat's (DL, from 2017-01): median 1.0000, 111 of 115 within 0.1 percent, lowest 0.7023 (2020-07).
- **Net imports against Eurostat's imports less exports** (`flow:IMP` less `flow:EXP`): within 1 MWh in 110 of 127 months and within 1,000 MWh in 125. The other two are November 2025 (-89,462 MWh) and December 2025 (+89,462 MWh), the same quantity in the next month.
- **The raw copies:** listed under the address above; each equals the saved file's metadata or answer.

## Where the description and the data disagree

1. **"Gross inland consumption" negative, "impossible".** Header line 3 ("Gross inland consumption is negative, as published, in 13 month(s)"), the connector's comment on that line ("impossible, kept as published"), the variable name `gross_inland_consumption` in the docstring and header line 2, and `SESSION_2357_REPORT.md` ("Values that cannot be right, kept as published: gross inland consumption is negative in 13 months"). MakStat's line equals imports less exports in all 175 months, and Eurostat's flows give the same 13 negative months with the same figures: they are months of net export. Suggested: say in the header and docstring "MakStat's line 'Gross inland consumption' equals imports less exports in every month (net imports; negative in the 13 months of net export, as in Eurostat's flows)", and either rename the variable `net_imports` or keep the name with that sentence beside it.
2. **`vintage` 2013-04-23.** Every row's `vintage` and header line 4 ("updated 2013-04-23T12:00:00Z") carry the answer's `updated` field. `docs/datastandard.md` defines `vintage` as "When the source published the document the value came from"; the table holds months to July 2026. Suggested: leave `vintage` blank, as `statbank_moldova.py` does with StatBank's equally stale `updated`, and say in the header "the answer's updated field (2013-04-23) is not a publication date".
3. **`node` "the indicator as MakStat writes it".** The docstring and header line 2. The table removes MakStat's leading `..` (gross plants) and `.. ` (net plants), so a gross plant and its net plant share one `node`, and `coverage.csv` and `docs/coverage.md` count 15 nodes for 21 indicators. Suggested: "node the indicator's text without MakStat's leading dots (a gross and a net plant share it; x_code tells them apart)", or keep the dots.
4. **"Retrieved: 20261024T082751Z ... by warehouse/connectors/makstat_macedonia.py".** Header line 4 names the run that wrote the file as the retrieval; that run made no request (its raw folder holds only the lock check). The metadata and the answer were fetched at 08:26:53Z and 08:26:55Z by the trial run `20261024T082652Z`. Suggested: "Written: 20261024T082751Z (UTC), offline, by warehouse/connectors/makstat_macedonia.py, from the metadata and answer fetched at 08:26:53Z and 08:26:55Z by run 20261024T082652Z".
5. **"May be public" if the ERW sells anything.** `docs/licenses.md`, the table's row, gives "may be public" in that column for a publisher whose terms are "not settled". Suggested: "not settled" there too.
6. **"Not read".** `docs/licenses.md` lists the office as "not read", though reads 617 and 618 (session 2362) read its robots address and English home page and found no terms. Suggested: "read (617, 618): no terms of reuse found".
7. **No record of the run.** `CLAUDE.md` describes `run_status.csv` as "every run and every gap"; it holds no row of this table, only `runs/status/makstat_macedonia.json`. Suggested: record the run with `run_status.py record`.
8. **"The table's metadata, twice".** `SESSION_2357_REPORT.md`'s list of pulls. The metadata was fetched three times: by the probe (08:25:16Z, read 593) and by the two trial runs (08:26:16Z and 08:26:53Z). The report's total of 14 requests holds; its list names 13. Suggested: "the table's metadata, three times (the probe, and two trials, the first stopped on a month label)".

Not acted on: this note changes no file but itself.

## The session report against the table

`SESSION_2357_REPORT.md`:

- "3,669 figures, January 2012 to July 2026, in MWh as published": holds.
- "Variables (21)": holds; 15 distinct `node` texts (disagreement 3).
- "MakStat writes some months as `2019_09` and one with a Cyrillic letter (`2026М01`)": holds, six of the first form.
- "Net production against Eurostat's monthly net production ... median ratio 1.0000 over 127 months, 90 within 0.1 percent, the range 0.987 to 1.189": holds (0.9868 to 1.1893).
- "One month is off, gross January 2016 by 2,382 MWh": holds; the gap is the gross biogas cell, 0 against a net of 2,382.
- "Gross inland consumption is negative in 13 months from September 2022 to September 2025, down to -60,362 MWh": the months and figures hold; "values that cannot be right" does not (disagreement 1).
- "Net production of CHP and autoproducers' thermal plants is negative in 39 months, which is their own use above their output": holds (30 of the 39 with gross 0).
- "The test, `tests/test_session2357.py` (3 tests)": holds.

## What it does not hold

- Final consumption other than households' (industry, services, transport), which this MakStat table does not give; consumption by region; prices.
- Months before January 2012 and after July 2026; the six empty cells named above.
- Gross imports and exports as Eurostat counts them (from 2017 Eurostat's are several times MakStat's; `eurostat_electricity_monthly` holds them).
- A gross inland consumption: MakStat's line of that name is net imports. Eurostat's supply available for the internal market (`flow:AIM`) is in `eurostat_electricity_monthly`.
- MakStat's earlier figures for a month it has revised, and any publication date (`vintage` carries a stale field).

Acted on in session 2366, the table written again offline (the same 3,669 rows): the header and docstring now say that MakStat's gross_inland_consumption equals imports less exports in every month (net imports, negative in the 13 months of net exports, kept under MakStat's name); `vintage` is empty (MakStat's "updated" said 2013-04-23); `node` is said to be the indicator without MakStat's leading dots; the header's retrieval line says that an offline run reads the saved answer; session 2357's report is corrected (net imports, the metadata fetched three times). Recorded, not changed: the run's status is in `runs/status/` only, as for every connector; `docs/licenses.md`'s commercial column for a publisher with no verdict is `licenses.py`'s rule.
