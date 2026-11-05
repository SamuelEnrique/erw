# EIA-930's hourly CO2 estimates for the seven ISO balancing authorities and the Lower 48, by fuel and by trade, UTC hours from 2 July 2018

Energy Research Warehouse (ERW), method note written in session 2298 (chain 105) for a table first written on 29 September 2026 (session 32, `archive/sessions/SESSION_32_REPORT.md`, the CO2 connector with carbon intensity, commit `bf38de3e`); the six by-fuel and trade variables were added on 30 September 2026 (session 34, `archive/sessions/SESSION_34_REPORT.md`). EIA's method, the workbooks' layout, the completeness rule and the carbon intensity built on this table are in `docs/methods/emissions.md`, which this note does not repeat; California's late hours and the break of December 2025 are in `docs/methods/eia930_caiso_break.md`; the screening rule the source tables do not apply is in `docs/methods/impossible_hours.md`.

Tables: `eia930_all_emissions`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-930 (Hourly Electric Grid Monitor), `https://www.eia.gov/electricity/gridmonitor/about`. Not in EIA's API: the per-area workbooks of the Grid Monitor, `https://www.eia.gov/electricity/gridmonitor/knownissues/xls/<BA>.xlsx` for CISO, ERCO, ISNE, MISO, NYIS, PJM and SWPP and `.../Region_US48.xlsx` for the Lower 48, sheet `Published Hourly Data`. Source id `eia:gridmonitor/knownissues/xls`. Raw files under `warehouse/raw/eia930_emissions/<run_id>/`: each workbook with a manifest (URL, Last-Modified, sha256) and the extract `<ba>_hours.csv` the rows are built from. Seven run folders are on this machine, from `20261004T021545Z` to `20261019T231435Z`; the newest workbooks here are those of 19 October 2026 (Last-Modified 16:08 to 16:29 GMT).

Connector: `warehouse/connectors/eia930_emissions.py` (session 32; `--from-raw`, `--from-extract`, `--variables` and `--max-new-rows` since session 34). Each run reads the whole workbook of each area, keeps the last `--days N` complete UTC days and merges them by (entity, variable, ts_utc) in a stream. Entity `eia930:<respondent>`, partition column `ba` in lower case. A CO2 column EIA leaves empty in every hour for an area is not a variable of it.

Schedule: the daily run, `warehouse/run_daily.sh`: `pull eia930_emissions ... eia930_emissions.py --days "${EMISSIONS_DAYS:-10}"` (ten days since session 321: "EIA's workbooks carry the CO2 hours some days behind"), after `eia930_storage` and before `caiso_fuel_supply`, `carbon_intensity` and `caiso_join`, on the GitHub runner (`.github/workflows/daily-prices.yml`, cron `0 14 * * *`, started by pg_cron through `workflow_dispatch`). The table is restored first (`warehouse/restore_tables.py --rolling`; `warehouse/redivis/config.yaml`, `'^eia930_all_emissions$'`: "keep their history from 2018-07-01 by merging"). On the data machine, `run_data_machine_tables.sh` runs `eia930_emissions.py --days 3 --dry-run` once a week (`dm_eia930_workbooks`): it saves the workbooks and writes no table. No step of `run_monthly.sh` or `warehouse/scheduled.py` runs the connector. `run_status.csv`: 1,827 rows, 22 ok and 1,805 gap. `archive_manifest.csv`: 4,350,240 rows as of run `20261023T152740Z-github`. Live set: `recent` (35 days), `'^eia930_all_emissions$'`, all eight variables (session 36A). Readers: `warehouse/derived/carbon_intensity.py` (the numerators), `caiso_join.py` (California's gas CO2, the check `F_GAS`), `event_window.py`, the chat's tools (`warehouse/chat/tools.py`), `warehouse/analysis/watch.py`, `warehouse/metadata/build_status.py` (its core pair), `site/lib/gridtables.ts`, the citations of `site/app/events/`, and `package/llms.txt`.

## Vintage and revision

The copy here was rebuilt from the ERW's archive "as of run 20261023T152740Z-github" (header line 1); the newest connector run is `20261023T143148Z` (header line 4), which read workbooks Last-Modified 22 October 2026 (header line 6): "this run 11,352 rows (1,440 new, 9,912 replacing earlier rows with the same key); 4,338,888 rows kept from earlier runs; 20 incomplete BA-day groups left out" (`run_status.csv`). `vintage` is blank in every row. EIA revises its hours, and a day is taken again by the next ten daily runs, then kept.

`retrieved_at` has 39 values, in four groups. The archive keeps a row's `retrieved_at` from the run that first archived its present value (`warehouse/archive/archive.py`, `VOLATILE`), so the date says when a value last changed, not when it was last read:

| retrieved_at | Rows | What |
|---|---|---|
| 2026-09-29, 18:13 to 18:33 | 3,591,874 | session 32's download of the eight workbooks; session 34's six variables were built from the same files (`--from-raw` keeps the workbook's time) |
| 2026-09-30 to 2026-10-15 | 2,898 | the daily runs, 5 to 225 rows each |
| 2026-10-19, 10:27 to 10:29 | 741,323 | session 309's rewrite from the workbooks Last-Modified 17 October 2026 |
| 2026-10-19T20:07 to 2026-10-23 | 14,145 | the runs after session 309 |

Against the two extracts of 19 October on this machine: 4,333,223 of the 4,333,224 values dated before 9 October 2026 agree with the workbooks Last-Modified 17 October to one part in a billion. Against the workbooks Last-Modified 19 October, 11,754 values differ by more: 7,939 on days from 9 October (which the later runs took again from newer workbooks) and the rest on 2 to 4 September, one US48 hour of 28 September, and 7 and 8 October 2026, which EIA revised after the ten-day window had passed them. Of the 14,145 rows of the last four runs, 10,880 agree with neither extract: they come from the workbooks of 20 to 22 October, which are not on this machine.

## Shape and variables

Series, 4,350,240 rows, 14 columns: the series columns and `ba`. Unit `tCO2` (metric tons of CO2, as EIA states them), `freq` PT1H; `market`, `node` and `vintage` blank in every row; `geo` the area's states (ISNE `US-CT,US-MA,US-ME,US-NH,US-RI,US-VT`, PJM and MISO and SWPP their lists, `US` for US48); `source_url` the area's workbook. Eight variables:

| Variable | Rows | EIA's column |
|---|---|---|
| `co2_emissions_generated` | 565,464 | CO2 Emissions Generated |
| `co2_emissions_consumed` | 565,464 | CO2 Emissions Consumed |
| `co2_emissions_coal` | 549,336 | CO2 Emissions: COL |
| `co2_emissions_natural_gas` | 565,200 | CO2 Emissions: NG |
| `co2_emissions_oil` | 408,384 | CO2 Emissions: OIL (no ERCO, no MISO) |
| `co2_emissions_other` | 565,464 | CO2 Emissions: Other |
| `co2_emissions_imported` | 565,464 | CO2 Emissions Imported |
| `co2_emissions_exported` | 565,464 | CO2 Emissions Exported |

| ba | Rows | First day | Last hour | Days with the core pair | Days missing inside the span | Variables |
|---|---|---|---|---|---|---|
| ciso | 562,800 | 2018-07-02 | 2026-10-20T23 | 2,992 | 41 | 8 |
| erco | 506,184 | 2018-07-03 | 2026-10-20T23 | 3,013 | 19 | 7 (no oil) |
| isne | 565,008 | 2018-07-02 | 2026-10-20T23 | 3,033 | 0 | 8 |
| miso | 504,840 | 2018-07-02 | 2026-10-20T23 | 3,005 | 28 | 7 (no oil) |
| nyis | 578,880 | 2018-07-02 | 2026-10-20T23 | 3,015 | 18 | 8 |
| pjm | 560,784 | 2018-07-02 | 2026-10-20T23 | 2,921 | 112 | 8 |
| swpp | 489,408 | 2018-07-02 | 2026-10-20T23 | 2,549 | 484 | 8 |
| us48 | 582,336 | 2018-07-02 | 2026-10-20T23 | 3,033 | 0 | 8 |

Rows a year: 255,744 (2018, from July), 513,648, 515,544, 534,720, 536,304, 538,224, 529,152, 522,936 (2025) and 403,968 (2026 to 20 October).

- **Missing days.** PJM lacks 2018-07-10 to 2018-09-19 (72 days) and the one to three days around most clock changes from November 2018 to March 2026. SPP's 484 fall in 123 runs: 88 of three days, mostly Friday to Sunday (2019 holds 126 of the days and 2020 holds 138), and two long ones, 2025-11-29 to 2026-03-09 (101 days) and 2026-05-20 to 2026-06-09 (21 days); `known_gaps.csv`: "EIA's per-BA workbook for SWPP holds no CO2 value for these hours (for example 12 to 21 March 2021)". ERCO lacks 2018-11-09 to 2018-11-12 and 2025-12-03 to 2025-12-06 among its 19; CISO's 41 include the days around 31 October in 2024 and 2025.
- **The six beside the core pair.** Days that have the core pair but not the variable: CISO coal 281, natural gas 10, oil 195; ISNE coal 389 (no coal after 2026-03-25), natural gas 1 (2021-03-01), oil 332; PJM coal 2 (2022-10-01 and 02). Every other area holds all its variables on every core day. NYIS's coal is 0 in all 72,360 of its rows.
- **EIA's identities,** over the hours with every term held: consumed = generated + imported - exported within 1.2e-10 tCO2 in every hour of every area. Generated = coal + gas + oil + other within 0.01 tCO2 in every hour but 26: MISO's 24 hours of 2021-11-05T05:00Z to 2021-11-06T04:00Z (up to 1,690 tCO2), whose oil EIA gives in those hours only (29,052.8 tCO2 in the extract) and which the table does not write, because they fill no UTC day; and two US48 hours (2026-09-28T22:00Z, 2026-10-16T20:00Z, at most 4.12 tCO2).
- **Values EIA publishes that no grid emitted,** held as published: SPP's CO2 generated (and its coal, gas and other) is 0 in every hour of 2018-07-02 to 2018-08-30 and in 5 hours of 08-31 (1,445 hours), so its consumed CO2 is below zero in 1,300 hours of 2018 (lowest -1,164.8 tCO2). SPP's imported CO2 is 3,193,814.7 tCO2 at 2020-03-17T19:00Z and 3,162,587.4 at 18:00Z, over ninety times SPP's largest hour of CO2 generated (34,041.2); seven hours exceed 50,000 tCO2, on 2020-03-17, 2026-04-23, 2026-07-21, 2026-08-04, 2026-10-04 and 2026-10-06. The first is the day EIA's daily interchange holds SWPP to AECI at -10,746,671 MWh (`docs/methods/eia930_daily_interchange.md`). PJM's consumed is below zero in 5 hours of 2022-10-01 (lowest -1,506.4) and ISO-NE's in one (2026-09-11T17:00Z, -240.8).
- Largest hour: US48 CO2 generated 305,224.3 tCO2 (2021-07-27T21:00Z). US48 CO2 generated a year, million tCO2: 1,557.42 (2019), 1,405.27, 1,516.67, 1,521.57, 1,407.89, 1,419.44, 1,485.27 (2025).

## Placing values in time, and what is filled

`ts_utc` is the start of the hour in UTC: EIA's `UTC time` is the hour's end, and one hour is subtracted. Completeness is by UTC day: every (area, variable, day) held has its 24 hours, no partial day. 2018-07-01 is written for no area (EIA's CO2 begins at local midnight, so that UTC day is partial), and ERCO begins on 2018-07-03. Nothing is filled. California's hours of 1 November 2023 to 2 December 2025 are held as EIA stamped them, one hour late (`warehouse/faults/faults.yaml`, `eia930_ciso_hours_one_hour_late`); the readers that move them do so themselves.

## License

The header has no License line. `coverage.csv`: public. `sources.csv`, the source's row: license public. `license_verdicts.csv`, EIA (read 1): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", "may be public", if the ERW sells anything "may be public", with the acknowledgment "Source: U.S. Energy Information Administration". `docs/licenses.md`, the table's row: EIA, "may be public", flag public, "agrees", ERW verdict public. `license_tables.csv`: "the source registry". No row in `license_status.csv`.

## Checks (session 2298)

The figures in this note were computed from the rows of `warehouse/output/eia930_all_emissions.csv`, read past its 10 header lines (counted), in one streamed pass each by `runs/c105/s2298/check_eia930_all_emissions.py`, `check_eia930_all_emissions_detail.py`, `check_eia930_all_emissions_vintage.py`, `check_eia930_all_emissions_gaps.py` and `check_eia930_all_emissions_missing.py` (outputs beside them).

- 4,350,240 rows, as `coverage.csv` and `archive_manifest.csv` give; no (area, variable, hour) twice; no blank value; every `ts_utc` on the hour; `entity` is `eia930:<BA>` in every row; one unit.
- **Against the ERW's extracts of the workbooks:** as under Vintage and revision.
- **Against EIA's hourly generation** (`eia930_all_generation`, EIA's API, from 2026-08-26): CO2 from natural gas over gas generation, summed over the 1,320 to 1,344 hours both hold, tCO2 per MWh: CISO 0.4056, ERCO 0.4171, ISNE 0.3943, MISO 0.4274, NYIS 0.4598, PJM 0.3899, SWPP 0.4750, US48 0.4103; hour by hour CISO's runs 0.4030 to 0.4094 (1st to 99th percentile), beside the 0.4051 of `caiso_join.py` (`F_GAS`, 864 hours to 30 September). Coal over coal generation: 1.0188 (PJM) to 1.1124 (ERCO). Each is one factor a fuel, as EIA's method says.
- **Through the carbon intensity to EIA's hourly demand:** consumed CO2 x 1000 over `carbon_intensity_hourly`'s `intensity_demand` gives back the demand it was divided by. Against `eia930_all_demand`'s `demand_mw`: every common hour within 0.1 percent for the seven ISOs (1,224 to 1,344 hours each), so the workbooks' demand and EIA's API demand are the same numbers there; US48 1,103 of 1,344 hours within 0.1 percent and 1,337 within 1 percent (largest 2.5 percent, 2026-10-14T20:00Z), as `docs/methods/eia930_all_demand.md` found for US48 against EIA's daily route.
- **Gap rows:** of the days missing inside each area's span, every one is named by a gap row of `run_status.csv` but 73 (below).

## Where the description and the data disagree

1. **"Each day or variable-day left out is a gap row."** Header line 10, the docstring and `docs/methods/emissions.md` ("Every day or variable-day left out is recorded as a gap") say so. 73 days of the core pair are missing with no gap row: PJM's 70 days of 2018-07-11 to 2018-09-18 (the two days at either end have one), ERCO's 2018-11-11 and 2025-12-05, and CISO's 2024-11-02. On each, EIA's workbook has its 24 rows and no CO2 value in any of them; session 32's run, which first met them, recorded only days with some hours (`run_status.csv`, run `20260929T182103Z`: 42 PJM rows), and no later window reaches them. SESSION_32_REPORT's table ("Days left out (incomplete)": PJM 42, ERCO 18) counts those rows, not the days the table lacks (PJM 112 today).
2. **"The last 3 days."** The docstring (`--days 3  # the daily run: the newest workbooks, last 3 days`) and `docs/methods/emissions.md` ("merges their last 3 days") describe the daily run as three days. `run_daily.sh` passes `--days "${EMISSIONS_DAYS:-10}"` since session 321, and the last runs replaced about 9,900 rows each (ten days of eight areas).
3. **Demand in this table.** SESSION_97_REPORT ("`eia930_all_emissions` and anything that reads EIA's hourly demand carry PJM's 224,345 MW and New York's zeros") and `warehouse/faults/faults.yaml` (the faults of PJM's, New York's and the Lower 48's demand list this table among theirs) treat the table as holding demand. It holds CO2 only; EIA's demand is in the extracts beside the raw workbooks, which the carbon intensity reads.
4. **"By balancing authority."** The header title and `emissions.md` say per balancing authority; one of the eight areas is EIA's Lower 48 region (`Region_US48.xlsx`), not a balancing authority.
5. **"From 2018-07-02."** `package/llms.txt` gives the table's start as 2018-07-02 for every area; ERCO's first day is 2018-07-03 (SESSION_32_REPORT says so).

Not acted on: this note changes no file but itself. EIA's impossible values (SPP's zero CO2 of 2018, its imported CO2 of 17 March 2020) are EIA's, recorded, not changed.

## The session report against the table

- `SESSION_32_REPORT.md`: 1,122,144 rows of two variables, ERCO from 2018-07-03, "2018-07-01 is not written for any BA", "range -1,506 to 3,207,014 tCO2", SPP's 485 incomplete days: the start, the first day and the range hold (the two extremes are still PJM's consumed of 2022-10-01T05:00Z and SPP's consumed of 2020-03-17T19:00Z). SPP lacks 484 days today, all named by gap rows; the days-left-out column is item 1 above.
- `SESSION_34_REPORT.md`: 3,195,240 rows added, 4,317,384 in all, coal 545,640, natural gas 560,808, oil 405,576 ("no ERCOT, no MISO"), other, imported and exported 561,072 each; "EIA's identities hold to 1e-11 (PJM, every hour)": the variables, the missing oil and PJM's identities hold, and the rows have grown with the daily runs (coal 549,336, oil 408,384, the four others 565,464). Over all areas the fuel identity fails in MISO's 24 oil hours and two US48 hours.
- `SESSION_309_REPORT.md`: "652 open days, of which 484 are SWPP's", the table rewritten from the workbooks of 17 October (4,343,184 rows): the 741,323 rows dated 19 October 10:27 to 10:29 are that rewrite's changed values.

## What it does not hold

- EIA's emission factors and its own intensities (lbs/kWh), which are in the workbooks; EIA's demand and net generation (in the extracts; `carbon_intensity.py` reads them there); other balancing authorities (EIA publishes a workbook for each; none is read); hours before 2018-07-02; the 73 unrecorded and the other missing days above; MISO's 24 hours of oil; EIA's earlier versions of a revised hour; California's hours moved to their true time.
