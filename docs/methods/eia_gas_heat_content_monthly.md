# The heat content of the natural gas delivered to consumers, a month from 2013: the U.S., every state and DC (EIA, Natural Gas Monthly)

Energy Research Warehouse (ERW), method note written in session 2247 (chain 101) for a table first written on 24 October 2026 (session 2245 of chain 101, its report `archive/sessions/SESSION_2245_REPORT.md`).

Tables: `eia_gas_heat_content_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), Natural Gas Monthly, heat content of natural gas delivered to consumers, through EIA's API v2, route `natural-gas/cons/heat` (the route's metadata names its parent "EIA natural gas survey data" and gives monthly and annual frequencies, 2012-01 to 2026-07). The header's page is the route itself, `https://api.eia.gov/v2/natural-gas/cons/heat/`; the access line is `https://api.eia.gov/v2/natural-gas/cons/heat/data/?frequency=monthly&data[]=value&facets[process][]=VGTH&start=2012-01`, in pages of 5,000 records, with EIA's key (read from `.env`, never saved; `REDACTED` in every saved address and in each row's `source_url`). Source id `eia:natural-gas/cons/heat`.

One process, VGTH "Heat Content Delivered to Consumers", product EPG0 "Natural Gas", unit "BTU/CF"; 52 areas, NUS (the U.S.) and EIA's `S<state>` for the fifty states and DC. Session 2245 read the route's metadata (`runs/c101/s2245/meta.json`) and a page of 2025 asked without a process (`sample.json`, 624 records: this process and these 52 areas only). No page of EIA's was saved under `runs/license_reads/`; EIA's verdict is read 1. The two data pages are in `warehouse/raw/eia_gas_heat_content/20261024T034444Z/`.

Connector: `warehouse/connectors/eia_gas_heat_content.py` (session 2245, made from the crude quality connector): `[--from 2012-01] [--offline | --fresh] [--out-dir DIR]`, at most 10 requests a run, 3 seconds apart; a page saved in `warehouse/raw` is reused unless `--fresh`. A process, unit or area not in its map, or a key given twice, stops the run; a record without a number has no row. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

The two pages were fetched by session 2245's trial (run `20261024T034444Z`) at 2026-10-24T03:44:48Z and 03:44:52Z (the raw manifest). The table is run `20261024T034555Z`, written from them with "0 requests of 10": "File holds 8476 rows, one snapshot; the previous file held 0 rows."

`retrieved_at` is 2026-10-24T03:45:55Z in every row, the write's start, not the pages' time (disagreement 1); `vintage` is blank. EIA's pages carry no preliminary or revision flag. The table is a snapshot: a run replaces the whole file, so a value EIA revises or withdraws is revised or gone at the next run.

## Shape and variables

Series, 8,476 rows, 52 entities `eia_gas_heat_content:NGA_EPG0_VGTH_<area>_BTUCF` (EIA's series id), one variable `heat_content` in `Btu/ft3` (Decision 74), `freq` P1M, `geo` US or `US-<state>`, `market` blank, `node` EIA's series description. Every series holds all 163 months from 2013-01 to 2026-07. EIA gives whole numbers.

| Area | geo | Mean | Lowest (month) | Highest (month) |
|---|---|---|---|---|
| U.S. | US | 1,035.2 | 1,026 (2013-01) | 1,041 (2021-02) |
| Alabama | US-AL | 1,028.2 | 1,014 (2013-02) | 1,036 (2026-06) |
| Alaska | US-AK | 992.2 | 937 (2018-08) | 1,023 (2024-06) |
| Arizona | US-AZ | 1,031.5 | 1,017 (2026-04) | 1,050 (2016-03) |
| Arkansas | US-AR | 1,019.5 | 1,011 (2014-11) | 1,031 (2026-03) |
| California | US-CA | 1,031.7 | 1,015 (2026-04) | 1,049 (2023-01) |
| Colorado | US-CO | 1,064.1 | 1,023 (2013-01) | 1,109 (2019-07) |
| Connecticut | US-CT | 1,027.8 | 1,011 (2013-03) | 1,049 (2015-05) |
| Delaware | US-DE | 1,040.5 | 1,030 (2026-07) | 1,067 (2013-11) |
| District of Columbia | US-DC | 1,034.6 | 1,014 (2013-04) | 1,051 (2016-01) |
| Florida | US-FL | 1,023.6 | 1,015 (2013-02) | 1,031 (2024-08) |
| Georgia | US-GA | 1,027.6 | 1,014 (2013-01) | 1,051 (2025-10) |
| Hawaii | US-HI | 948.3 | 912 (2020-08) | 1,057 (2013-03) |
| Idaho | US-ID | 1,028.0 | 984 (2014-07) | 1,069 (2017-06) |
| Illinois | US-IL | 1,035.3 | 1,013 (2013-01) | 1,052 (2026-04) |
| Indiana | US-IN | 1,045.7 | 1,011 (2013-01) | 1,064 (2024-06) |
| Iowa | US-IA | 1,060.0 | 1,025 (2013-01) | 1,090 (2023-09) |
| Kansas | US-KS | 1,034.4 | 1,016 (2013-11) | 1,059 (2019-07) |
| Kentucky | US-KY | 1,041.3 | 1,015 (2015-03) | 1,062 (2023-12) |
| Louisiana | US-LA | 1,021.0 | 1,013 (2013-02) | 1,038 (2014-12) |
| Maine | US-ME | 1,036.8 | 1,016 (2014-10) | 1,054 (2025-01) |
| Maryland | US-MD | 1,043.2 | 1,027 (2013-04) | 1,062 (2013-09) |
| Massachusetts | US-MA | 1,030.4 | 1,027 (2015-05) | 1,038 (2013-10) |
| Michigan | US-MI | 1,048.0 | 1,015 (2014-07) | 1,066 (2019-09) |
| Minnesota | US-MN | 1,047.3 | 1,020 (2013-01) | 1,076 (2024-07) |
| Mississippi | US-MS | 1,027.5 | 1,013 (2013-01) | 1,039 (2016-03) |
| Missouri | US-MO | 1,022.1 | 1,011 (2014-05) | 1,033 (2019-08) |
| Montana | US-MT | 1,045.6 | 1,019 (2015-05) | 1,072 (2025-11) |
| Nebraska | US-NE | 1,057.4 | 1,029 (2013-07) | 1,085 (2019-07) |
| Nevada | US-NV | 1,039.9 | 1,027 (2020-07) | 1,061 (2022-12) |
| New Hampshire | US-NH | 1,032.4 | 1,026 (2016-07) | 1,050 (2025-01) |
| New Jersey | US-NJ | 1,039.5 | 1,031 (2020-05) | 1,052 (2022-01) |
| New Mexico | US-NM | 1,031.7 | 1,008 (2026-04) | 1,055 (2016-08) |
| New York | US-NY | 1,031.9 | 1,029 (2016-05) | 1,035 (2013-06) |
| North Carolina | US-NC | 1,032.4 | 1,010 (2013-05) | 1,054 (2026-03) |
| North Dakota | US-ND | 1,070.5 | 1,013 (2013-09) | 1,140 (2013-07) |
| Ohio | US-OH | 1,062.7 | 1,033 (2013-02) | 1,077 (2015-11) |
| Oklahoma | US-OK | 1,037.1 | 1,022 (2019-01) | 1,053 (2016-09) |
| Oregon | US-OR | 1,053.8 | 1,010 (2013-02) | 1,089 (2023-05) |
| Pennsylvania | US-PA | 1,039.7 | 1,034 (2021-10) | 1,054 (2013-11) |
| Rhode Island | US-RI | 1,029.4 | 1,023 (2014-06) | 1,034 (2013-05) |
| South Carolina | US-SC | 1,029.5 | 1,017 (2013-06) | 1,041 (2026-05) |
| South Dakota | US-SD | 1,066.1 | 1,028 (2013-01) | 1,095 (2023-09) |
| Tennessee | US-TN | 1,025.7 | 1,012 (2013-02) | 1,044 (2023-12) |
| Texas | US-TX | 1,023.0 | 1,013 (2025-11) | 1,036 (2014-08) |
| Utah | US-UT | 1,044.5 | 1,029 (2020-07) | 1,057 (2023-01) |
| Vermont | US-VT | 1,033.9 | 1,009 (2014-02) | 1,051 (2019-12) |
| Virginia | US-VA | 1,048.8 | 1,028 (2013-04) | 1,061 (2018-12) |
| Washington | US-WA | 1,077.0 | 901 (2019-10) | 1,108 (2024-09) |
| West Virginia | US-WV | 1,087.9 | 1,046 (2022-05) | 1,133 (2018-10) |
| Wisconsin | US-WI | 1,040.3 | 1,023 (2013-08) | 1,058 (2025-12) |
| Wyoming | US-WY | 1,054.6 | 1,025 (2014-07) | 1,082 (2020-04) |

Btu/ft3; means over the 163 months rounded to one decimal; where a lowest or highest value recurs, its first month is given.

- The U.S. figure moves little: a year's mean of its months is 1,026.8 in 2013, 1,031.2 in 2014, between 1,035.8 and 1,037.2 from 2015 to 2025, and 1,035.1 in January to July 2026; it never changes by more than 5 Btu/ft3 from one month to the next. July 2026: 1,033.
- The states spread a median 157 Btu/ft3 a month, lowest to highest. Washington's figure spans 207 Btu/ft3 (901 to 1,108), Hawaii's 145, North Dakota's 127; New York's only 6.
- It is an average, as the header says: never summed across states, and weighted by volume when areas are combined (session 2245's cross-check weights the states by their deliveries).

## Placing values in time, and what is filled

`ts_utc` is the first day of EIA's `period` (YYYY-MM) at 00:00:00Z (Decision 11), a label for the month. The pages hold 8,488 records (EIA's `total`): 8,476 with a number, which are the table's rows (0 keys and 0 values differ), and 12 without, the U.S. series for January to December 2012, which have no row. No state has a record before 2013. Nothing is filled.

## License

Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Monthly")." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 1 (EIA's copyrights and reuse page, `https://www.eia.gov/about/copyrights_reuse.php`), "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", if the ERW sells anything "may be public"; EIA asks for the acknowledgment "Source: U.S. Energy Information Administration" with the date. The table's row: flag public, "agrees", ERW verdict public.

## Checks (session 2247)

The figures in this note were computed from the rows of `warehouse/output/eia_gas_heat_content_monthly.csv`, read past its 10 header lines (counted), and from the saved pages, read only (scripts `runs/c101/s2247/eia.py`, `eia_trial.py`, `gas2.py` and `gas_table.py`, outputs beside them).

- 8,476 rows, months 2013-01 to 2026-07, "8,488 records of EIA's, 8,476 rows", as header line 3 states; 52 series, the U.S., fifty states and DC; no (entity, variable, ts_utc) twice; no blank value; unit Btu/ft3 throughout; each row's `node` is the page's series description, and each state's `geo` matches the state its description names.
- **Against the pages:** EIA's `total` is 8,488 on both pages (5,000 and 3,488 records); the table's keys and values are the pages', with 0 differences.
- **The trial against the table:** `runs/c101/s2245/trial/eia_gas_heat_content_monthly.csv` has the same keys and the same values in every column but `retrieved_at` (03:44:44Z in the trial, 03:45:55Z in the table).
- Session 2245's cross-check (`runs/c101/s2245/cross.py`), run again from the main checkout with the written table as argument 1: its output is identical to the saved `cross.out`, which was run on the trial. The U.S. against the states weighted by their deliveries to consumers (residential, commercial, industrial and electric power, `eia_gas_consumption_state_monthly`), over 163 months: a median 0.30 Btu/ft3 apart, at most 1.58; a median 51 states a month; the U.S. outside the states' range in 0 of 163 months. SEDS's implied figure (`eia_seds_state_energy`, total consumption in TBtu over the year's consumption in MMcf) against the U.S. figure's plain yearly mean: 1,026.4 and 1,026.8 (2013) to 1,036.6 and 1,036.2 (2024), the largest gap 1.3 Btu/ft3, in 2020 (1,037.5 and 1,036.2).

## Where the description and the data disagree

1. **`retrieved_at` is the run's start, not the retrieval.** Header line 10 says "Per row, source, source_url and retrieved_at say where it came from". The connector sets `retrieved_at` to the moment the run starts, whether it asks EIA or reuses a saved page: the table's rows say 2026-10-24T03:45:55Z, a run that asked nothing ("0 requests of 10"), and the trial's say 03:44:44Z, four seconds before its first page; EIA served the pages at 03:44:48Z and 03:44:52Z. Header line 4 likewise names the offline run. The pages' own times are in `warehouse/raw/eia_gas_heat_content/20261024T034444Z/manifest.csv`.

Compared besides, with no contradiction found: the header's and docstring's counts, span, series, areas, unit, geo, "a blank has no row" and the docstring's arithmetic (MMcf times Btu/ft3, divided by 1,000, is billion Btu) against the rows, the pages and the route's metadata.

Not acted on: this note changes no file but itself.

Acted on in session 2247. The connector now stamps each row with the time EIA served its page (a reused page's first download, kept by `ip.raw_cached`), not the time the write began; the table was written again offline (no request, the same rows), and its rows now carry EIA's serving times.

## The session report against the table

Every figure of `SESSION_2245_REPORT.md` checked against the table, the saved pages and the rerun cross-check holds (January 2013 to July 2026, 8,476 rows, 52 series for the U.S., every state and DC, geo from EIA's `S<state>` areas, the route's metadata from 2012-01 and the first value 2013-01, EIA's unit "BTU/CF", a median 0.30 Btu/ft3 at most 1.58 over 163 months, never outside the states' range, SEDS within 1.3 Btu/ft3 in every year 2013 to 2024, 2024's 1,036.2 against 1,036.6, 4 requests, the crude table's guessed address replaced and that table written again with the same rows). None found that does not hold. The comparison with SEDS uses the plain mean of the year's months, not a mean weighted by each month's volume.

## What it does not hold

- The heat content of gas at other stages (the route's 2025 page holds only gas delivered to consumers), the route's annual figures, a state's figure by consuming sector, months before 2013 and after July 2026, and the volumes that turn it into energy (`eia_gas_consumption_state_monthly` holds the states' deliveries in MMcf).
