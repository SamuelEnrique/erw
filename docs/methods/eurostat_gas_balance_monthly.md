# Europe's monthly natural gas balance, January 2015 to September 2026: production, trade, stock changes, inland consumption and its uses by country (Eurostat, nrg_cb_gasm)

Energy Research Warehouse (ERW), method note written in session 2331 (chain 108) for a table first written on 24 October 2026 (session 2329 of chain 108, its report `archive/sessions/SESSION_2329_REPORT.md`).

Tables: `eurostat_gas_balance_monthly`

## Publisher and address

Eurostat (Statistical Office of the European Union), "Supply, transformation and consumption of gas, monthly data" (`nrg_cb_gasm`; the data browser page `https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_gasm/default/table`), through the SDMX 2.1 dissemination API, one request without a key:

- `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_gasm?format=SDMX-CSV&compressed=false&startPeriod=2015-01`

Source id `eurostat:nrg_cb_gasm`. The answer is SDMX-CSV with the columns `DATAFLOW, LAST UPDATE, freq, nrg_bal, siec, unit, geo, TIME_PERIOD, OBS_VALUE, OBS_FLAG, CONF_STATUS`: 108,947 lines, one product (SIEC G3000, natural gas), two units (54,493 lines in TJ_GCV, terajoules of gross calorific value, and 54,454 in MIO_M3, million cubic metres), 16 balance items, 40 areas, and "LAST UPDATE" 23/10/26 23:00:00 on every line. The 40 areas are the 27 members, Norway (the only member of EFTA present), eight candidates (Albania, Georgia, Moldova, Montenegro, North Macedonia, Serbia, Turkiye written TR, Ukraine), EU27_2020, EA21, the United Kingdom and Kosovo; there is no line for EA20, Bosnia and Herzegovina, Switzerland, Iceland or Liechtenstein.

Session 2329's probe (`runs/c108/s2329/probe.csv`) made 3 requests, at least 3 seconds apart: ec.europa.eu's robots file (read 583), the data set (HTTP 200, 9,230,088 bytes, at 2026-10-24T07:26:34Z, no Last-Modified) and the NRG_BAL codelist (451,140 bytes, for the items' names). All three are saved in `runs/license_reads/s2329/`; the data set was seeded into `warehouse/raw/eurostat_gas_balance/20261024T072623Z_probe/`, and the trial and the write read it offline.

Connector: `warehouse/connectors/eurostat_gas_balance.py` (session 2329): `[--offline] [--out-dir DIR]`, one request. Only the TJ_GCV lines are taken, each times 1,000,000/3,600 (277.7778) and rounded to 0.001 MWh; only the EU's members, EFTA's, the official candidates and the aggregates EU27_2020, EA21 and EA20 are kept. A header not Eurostat's SDMX-CSV, a unit, frequency, product or balance item not expected, a value that is not a number, a period that is not a month or a key given twice stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public, and it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

One write, run `20261024T072838Z` ("This run wrote 53214 rows: 53214 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"). `retrieved_at` is 2026-10-24T07:26:34Z in every row, the download time. `vintage` is blank in every row: the answer carries no Last-Modified, and the connector does not read the file's own "LAST UPDATE" (23/10/26 23:00:00 on every line).

Eurostat flags 277 rows "p" (provisional), 45 of them in September 2026, the last month; 128 "e" (estimated) and 25 "n". A later run merges by (entity, variable, ts_utc), so a revised month replaces the old figure, and a month Eurostat stops printing keeps its earlier value.

## Shape and variables

Series, 53,214 rows, 38 entities `eurostat_gas_balance:<geo>`, `unit` MWh, `freq` P1M, `market` blank, `geo` ISO alpha-2 (Eurostat's EL written GR, 1,486 rows) and blank for EU27_2020 and EA21, `node` "<geo> natural gas <code>", `x_geo_code`, `x_nrg_bal`, `x_flag` and `x_conf_status` (blank in every row: each of the 120 confidential cells is also blank and has no row). 16 variables:

| Variable | Eurostat's code | Rows | Zeros |
|---|---|---|---|
| indigenous_production | IPRD | 4,609 | 1,512 |
| imports | IMP | 4,848 | 394 |
| exports | EXP | 4,679 | 1,301 |
| stock_change | STK_CHG_MG | 4,758 | 1,076 |
| stock_change_cushion_gas | STK_CHG_CG | 1,485 | 1,400 |
| transfer_from_other_sources | TOS | 2,585 | 1,708 |
| inland_consumption_calculated | IC_CAL_MG | 4,871 | 225 |
| inland_consumption_observed | IC_OBS | 4,868 | 229 |
| transformation_input_electricity_heat_main | TI_EHG_MAP | 4,813 | 677 |
| final_consumption_industry | FC_IND | 779 | 504 |
| final_consumption_other | FC_OTH | 854 | 541 |
| distribution_losses | DL | 4,542 | 1,473 |
| international_maritime_bunkers | INTMARB | 2,484 | 2,017 |
| flared | FLARE | 2,126 | 1,741 |
| vented | VENT | 2,126 | 1,843 |
| statistical_differences | STATDIFF | 2,787 | 1,570 |

From the table (`runs/c108/s2331/notes/eu.out`). Zeros: 18,211 in all, as header line 3 says.

EU27_2020, TWh, the sum of a year's months where all twelve are given (`eu2.out`):

| Year | Production | Imports | Exports | Stock change | Inland consumption (calculated) | Inland consumption (observed) | Power and heat (main producers) |
|---|---|---|---|---|---|---|---|
| 2015 | 927.3 | 6,220.0 | 3,332.7 | -41.0 | 3,855.6 | 3,845.0 | 562.8 |
| 2018 | 763.3 | 7,135.8 | 3,647.4 | 90.3 | 4,161.4 | 4,155.6 | 779.1 |
| 2021 | 488.6 | 6,856.0 | | | 4,401.3 | 4,395.5 | 961.8 |
| 2022 | | 6,405.0 | | 361.9 | 3,807.0 | 3,803.5 | 949.5 |
| 2023 | 370.2 | 5,135.3 | 1,954.2 | 32.4 | 3,535.3 | 3,534.5 | 799.7 |
| 2024 | 324.3 | 4,747.2 | 1,702.7 | -170.8 | 3,555.2 | 3,547.0 | 759.8 |
| 2025 | 334.8 | 5,144.9 | 1,959.5 | -110.7 | 3,644.9 | 3,637.0 | 850.2 |

A blank is a year with a month missing: the EU's production has no row in 33 months (most of 2019, 2020 and February to December 2022), its exports none in 24. The EU's imports and exports count the members' trade with each other.

- **Signs.** 2,275 rows are negative: stock changes (1,703), statistical differences (485), cushion gas (75), distribution losses (9) and inland consumption calculated (3). A stock change is positive when gas goes into storage: the EU's 2024 months run from -190.5 TWh in January through 38.5 to 93.1 TWh from April to August, 21.9 and 18.0 in September and October, to -167.2 in December.
- **Sparse items.** `final_consumption_industry` and `final_consumption_other` begin in January 2019 and are given for 25 areas (the EU's own from 2024 in full years); the other items run from 2015.
- **Last months.** Most areas end in September 2026; EU27_2020 ends in August 2026, as do Turkiye, Sweden, Serbia, Georgia and Moldova; Albania and North Macedonia end in July 2026; Ukraine ends in January 2022.

## Placing values in time, and what is filled

`ts_utc` is the month's first day at 00:00:00Z (Eurostat's TIME_PERIOD, YYYY-MM), January 2015 to September 2026 (141 months). Of the TJ lines for the 38 areas kept, 292 have no value (120 marked confidential, 172 flagged "m"); they have no row. Zeros are kept as Eurostat prints them. The United Kingdom's and Kosovo's 987 TJ lines are left out under Eurostat's terms, and every MIO_M3 line. Nothing is filled.

## License

Header: "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_cb_gasm. Eurostat bears no responsibility for this reshaping (TJ written as MWh)." `warehouse/metadata/license_verdicts.csv`: Eurostat (Statistical Office of the European Union), read 280, "Reuse of statistical data, metadata, publications, and other dissemination tools published on this website for commercial or non-commercial purposes is authorised provided the source is acknowledged. [...] [Not for commercial reuse:] Data for countries other than: Member States of the European Union (EU) Member States of the European Free Trade Association (EFTA) official EU acceding and candidate countries.", verdict "may be public", if the ERW sells anything "may be public" (session 2123). ec.europa.eu's robots file disallows the old SDMX path and the search pages, not `/eurostat/api/dissemination/`, and names no AI agent (read 583). `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", ERW verdict public.

## Checks (session 2331)

The figures in this note were computed from the rows of `warehouse/output/eurostat_gas_balance_monthly.csv`, read past its 10 header lines (counted), and from the saved data set, read only (scripts `runs/c108/s2331/notes/eu.py`, `eu2.py` and `trials.py`, outputs `eu.out`, `eu2.out` and `trials.out` beside them).

- 53,214 rows, 38 areas, 16 items, January 2015 to September 2026, as header lines 1, 3 and 10 state; no (entity, variable, ts_utc) twice; no blank value; MWh throughout.
- **Against the data set:** 54,493 TJ lines; 53,506 for the 38 areas kept and 987 for the United Kingdom and Kosovo; 53,506 less 292 without a value is 53,214.
- **The trial against the table:** `runs/c108/s2329/trial/eurostat_gas_balance_monthly.csv` has the same 53,214 keys with no cell differing.
- Session 2329's cross-check (`runs/c108/s2329/cross.py`, `cross.out`, run on the trial): its first lines, the ones `cross.py` as saved prints, add the stock change (879 and 933 of 4,494 area-months within 0.5 percent); the lines after them subtract it (below, and point 2). Imports against `eurostat_gas_imports_monthly`'s TOTAL partner: 4,422 of 4,431 area-months within 0.1 percent, 5 over 5 percent.
- Session 2331's own: inland consumption calculated against production plus imports less exports less the stock change, 4,494 area-months with all five items: 3,866 within 0.5 percent (3,596 within 1 MWh), 4,078 with transfers from other sources added, 4,093 with transfers added and cushion gas subtracted. Of the 628 not within 0.5 percent without transfers, 225 are months whose calculated consumption and gap are both 0, which a relative test cannot pass, and 373 of the other 403 have transfers from other sources. With transfers added, 416 are outside, the same 225 and 191 others, mostly the Netherlands (50), Spain (36), Sweden (29), Finland (21) and Belgium (19); the largest gaps are the EU's and the euro area's in April to June 2026, 1.48 to 1.67 TWh.

## The session report against the table

Every figure of `SESSION_2329_REPORT.md` checked against the table, the saved data set and `cross.out` holds (53,214 rows, 2015 to September 2026, 16 balance items, MWh from TJ of gross calorific value, the million cubic metres not taken, 18,211 zeros kept, 292 blanks, the EU's stock change positive from April to October 2024 and -190.5 TWh in January 2024, the identity within 0.5 percent in 3,866 of 4,494 area-months and in 4,078 with transfers, observed plus statistical differences in 4,219 of 4,868, imports against the imports table in 4,422 of 4,431, 5 over 5 percent, the EU's inland consumption 3,855.6, 4,401.3, 3,807.0, 3,535.3, 3,555.2 and 3,644.9 TWh, production 927.3 TWh in 2015 and 334.8 in 2025, read 583, 3 requests of 20), except:

- "40 areas (the EU's members, EFTA's and the candidates, with EU27_2020, EA21 and EA20)": the table has 38, and no EA20 (point 1).
- "The EU's imports (6,220 to 7,319 TWh)": 4,747.2 to 7,319.0 TWh over the complete years (point 3).
- "The rest are cells Eurostat leaves blank or marks confidential, and it rounds": the comparison takes only area-months where every item is given (point 2).
- "Production: 927.3 (2015) falling to 334.8 (2025)": the lowest complete year is 2024's 324.3 TWh.

## What it does not hold

- The million cubic metres, products other than natural gas (the data set has none), the annual balances (`nrg_bal_c`), consumption by industry or household before 2019, the United Kingdom and Kosovo, the areas the data set does not give (EA20, Bosnia and Herzegovina, Switzerland, Iceland, Liechtenstein), imports by partner (`eurostat_gas_imports_monthly`), and storage levels.

## Points for the session to act on

1. **The report's count of areas, and the header's and docstring's EA20, are not the table's.** The report says "40 areas (the EU's members, EFTA's and the candidates, with EU27_2020, EA21 and EA20)"; header line 3 says 38, which the table bears out. The data set has 40 areas, two of them (the United Kingdom and Kosovo) left out, and no EA20 at all. Header line 2 ("blank for EU27_2020, EA21 and EA20") and the docstring name EA20 as an aggregate the table holds. Of EFTA's members only Norway is in the data set. The report and header line 2 should say 38 areas and drop EA20.
2. **`cross.out` is not the output of `cross.py` as saved, and the report explains the misses wrongly.** `cross.py` adds the stock change ("production + imports - exports + stock change": 879 of 4,494 within 0.5 percent, median gap 1,275,833 MWh). The lines after its output, from which the report takes 3,866, 4,078 and 4,219, subtract it and come from a script not saved. The report then says "The rest are cells Eurostat leaves blank or marks confidential, and it rounds". The comparison takes only area-months where every item is given, so blanks and confidential cells are not among them. Of the 628 misses, 225 are months whose calculated consumption and gap are both 0, which the relative test cannot pass, and 373 of the remaining 403 carry transfers from other sources. The script that printed the report's figures should be saved as `cross.py`, and the explanation corrected.
3. **The report's range for the EU's imports holds only to 2022.** "The EU's imports (6,220 to 7,319 TWh) are larger than its consumption". The complete years give 6,220.0 (2015) to 7,319.0 (2019) through 2022, then 5,135.3 (2023), 4,747.2 (2024) and 5,144.9 (2025). Imports still exceed consumption in every year, so the point stands; the range should read 4,747.2 to 7,319.0 TWh.
4. **`vintage` is blank although the file states its update.** Every line of the data set carries "LAST UPDATE" 23/10/26 23:00:00, Eurostat's own date for the release; the answer has no Last-Modified, so `vintage` is empty in all 53,214 rows. The connector could write 2026-10-23T23:00:00 (the file gives no time zone) as `vintage`.
5. **`x_conf_status` is empty in every row.** The docstring and header line 2 describe Eurostat's confidentiality status (C), but all 120 cells marked C are blank and have no row, so the column never carries a value. The docstring could say so, or the column could be dropped.

Compared besides, with no contradiction found: the header's and docstring's row, zero and blank counts, the 16 items and their codes, the factor 277.7778, "EL is GR", the stock change's sign, "Areas left out by Eurostat's terms: UK XK", "Nothing is filled" and the license against the rows and the data set.

Acted on in session 2331: session 2329's report now gives 38 areas without EA20, the imports' range 4,747.2 to 7,319.0 TWh, and the misses of the identity as this note explains them; `runs/c108/s2329/cross.py` is saved in the form that printed the report's figures and reads the written table. Header line 2 no longer names EA20; header line 3 names Eurostat's last update (23/10/26 23:00:00, as the file gives it, no time zone) and says a confidential cell has no row; the docstring says the same of `x_conf_status`. `vintage` stays blank: the file's update carries no time zone. The table was written again offline: the same rows.
