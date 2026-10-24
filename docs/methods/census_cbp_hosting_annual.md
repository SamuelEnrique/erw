# Data processing and hosting by state, a year, 2012 to 2023: establishments, employment and payroll (Census Bureau, County Business Patterns, NAICS 518210)

Energy Research Warehouse (ERW), method note written in session 2222 (chain 098) for a table first written on 24 October 2026 (session 2160 of chain 092, `archive/sessions/SESSION_2160_REPORT.md`).

Tables: `census_cbp_hosting_annual`

## Publisher and address

U.S. Census Bureau, County Business Patterns (CBP), the state files: one zip a year, `https://www2.census.gov/programs-surveys/cbp/datasets/<year>/cbp<yy>st.zip`, each holding one comma-separated text file of every state, industry and legal form. Only NAICS 518210 is kept: "data processing, hosting and related services", from 2022 "computing infrastructure providers, data processing, web hosting, and related services". Source id `census:cbp_state_518210`. Files saved under `warehouse/raw/census_cbp_hosting/` (on this machine: a probe folder holding the 2022 file and the run folder `20261024T002451Z` holding the other eleven, 10.2 to 11.9 MB each).

Connector: `warehouse/connectors/census_cbp_hosting.py` (session 2160): `[--offline] [--out-dir DIR] [--first YEAR] [--last YEAR]`, one request a year (2012 to 2023 by default), two seconds apart. Each file's header must name fipstate, naics, emp_nf, emp, ap_nf, ap and est; the line of all legal forms (`lfo` "-") is taken; a state given twice, a figure that is not a whole number or a state code outside the map stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names the connector or the table. The table is in `catalogue_hold` of `warehouse/supabase/live_set.yaml`: not loaded into the live set.

## Vintage and revision

One run, `20261024T002622Z`; the latest file retrieved at 2026-10-24T00:25:35Z (`retrieved_at` has 12 values, 2026-10-24T00:23:53Z to 00:25:35Z, one a file). `vintage` is each file's Last-Modified, one value a year: 2012 2018-09-12T13:55:44Z, 2013 2018-09-13T13:14:51Z, 2014 2017-05-19T11:34:13Z, 2015 2017-05-09T20:25:03Z, 2016 2018-04-19T18:27:42Z, 2017 2019-11-26T18:58:28Z, 2018 2020-06-25T11:01:49Z, 2019 2021-04-22T10:53:32Z, 2020 2022-04-28T10:35:51Z, 2021 2023-04-27T11:41:44Z, 2022 2024-06-27T11:29:29Z, 2023 2025-06-26T12:00:29Z. The docstring says a year's file is released once and is reused; a run writes the whole table again (`write_snapshot`). Whether the Bureau has published 2024 was not checked in this session (no request); the connector's default stops at 2023.

## Shape and variables

Series, 1,836 rows: 51 areas (the 50 states and DC) for each of 12 years and 3 variables, 612 rows a variable, 153 a year. `entity` `census_cbp_518210:<postal code, lower case>`, `node` the postal code, `geo` `US-<code>`, `freq` P1Y, `market` blank. Variables:

- `establishments` (unit count);
- `employment` (count, the pay period including 12 March);
- `annual_payroll` (USD, the Bureau's thousands times 1,000; every value a multiple of 1,000).

Extra columns: `x_emp_noise` and `x_ap_noise`, the Bureau's flags for employment and payroll, repeated on all three variables' rows of a state and year; `x_naics_vintage` 2017 (1,530 rows, 2012 to 2021) or 2022 (306 rows, 2022 and 2023).

Flags as held, employment (rows of all three variables): G 1,089, H 618, J 93, D 18, S 18; payroll: G 1,170, H 588, J 60, D 18. No row carries N.

The nation (the sum of the 51 rows):

| Year | Establishments | Employment | Annual payroll (USD billion) |
|---|---|---|---|
| 2012 | 13,950 | 433,438 | 39.00 |
| 2013 | 14,276 | 478,933 | 42.27 |
| 2014 | 13,903 | 525,043 | 48.16 |
| 2015 | 13,599 | 539,171 | 50.92 |
| 2016 | 13,566 | 462,391 | 44.06 |
| 2017 | 17,597 | 525,528 | 53.80 |
| 2018 | 17,526 | 546,889 | 57.69 |
| 2019 | 17,297 | 552,937 | 62.26 |
| 2020 | 17,273 | 557,409 | 67.05 |
| 2021 | 17,297 | 552,789 | 83.93 |
| 2022 | 17,539 | 570,188 | 83.19 |
| 2023 | 18,544 | 629,527 | 92.96 |

Employment fell 14.2 percent in 2016 and establishments rose 29.7 percent in 2017; the table does not say why. The 2017 file renamed the size-class columns (`f<5` for `f1_4`) and the 2018 file dropped `empflag`. In 2023 the largest employers are California (123,859), Texas (56,290), New York (39,730), Virginia (33,404), Florida (30,385) and Massachusetts (27,905).

## Placing values in time, and what is filled

`ts_utc` is 1 January of the reference year at 00:00:00Z. Employment is the March pay period's count; payroll and establishments are the year's. Nothing is filled. A figure the Bureau withholds is kept as it prints it: a zero with its flag. Eighteen rows are such zeros:

- employment and payroll both 0, flags D: Arkansas 2013, Vermont 2012 and 2013, Wyoming 2012 to 2014 (6 state-years, 12 rows);
- employment 0, flag S, payroll given (flag H): North Dakota and South Dakota, 2012 to 2014 (6 rows).

The 2012 to 2017 files give, beside a withheld employment, a size-class letter (`empflag`, for example E or G); the connector does not keep it, so the table holds a zero where the file holds a range.

## License

Header: "License: may be public (the Census Bureau, see license_verdicts.csv; its name is not to imply endorsement). Cite the U.S. Census Bureau, County Business Patterns." `license_verdicts.csv`, Census Bureau (read 17): "You may use the Census Bureau API to develop a service ... You may not use the Census Bureau name, or the like to imply endorsement of any product, service, or entity, not-for-profit, commercial or otherwise.", verdict "may be public" today and if the ERW sells anything. `docs/licenses.md`: "may be public", flag public, "agrees", ERW verdict public. No row in `license_status.csv`.

## Checks (session 2222)

The figures in this note were computed from the rows of `warehouse/output/census_cbp_hosting_annual.csv`, read past its 10 header lines (scripts in `runs/c098/s2222/`: `check_census.py`, `cbp_heads.py`, `cbp_withheld.py`, `cross_census.py`).

- 1,836 rows, `ts_utc` 2012-01-01T00:00:00Z to 2023-01-01T00:00:00Z; 51 areas in every year, as the header's "States in each year" says; no (entity, variable, ts_utc) twice; no blank value; `geo` and `entity` agree with `node` in every row.
- The saved zips read again (read only): Virginia's all-forms line of every year gives the table's figures (for example 2016: emp 13,307, ap 1,434,832 thousand, est 510; 2023: 33,404, 4,842,578, 641), and the withheld lines above carry D or S with a zero, as held.
- Session 2160's cross-check (`runs/c092/s2160/cross.py`), run again on the table in `warehouse/output`: its output is identical to the saved `cross.out` (Spearman 0.56 and 0.56 against `datacenter_operator_sites` in 2023; Virginia's commercial sales from `eia861_utility_sales` 48.5 TWh in 2015 to 77.7 in 2023, Pearson 0.36 with establishments).
- The same correlation without the row "US" (53 operator sites whose `geo` names no state, with 0 employment by construction): 0.65 for employment and 0.66 for establishments, over 51 areas; 18 areas have no site.

## Where the description and the data disagree

1. **The withheld flag.** The docstring says "A row the Bureau withholds (flag N with zero) is kept as the Bureau prints it", and the header lists the flags as "G low, H moderate, J high, N not available". No row carries N. The withheld rows carry D (in the employment flag of 18 rows and the payroll flag of 18) and S (in the employment flag of 18), which neither names; a reader who drops N rows keeps 18 zeros that are not counts, and a national sum for 2012 to 2014 treats them as zero.
2. **The NAICS edition flag.** The docstring calls `x_naics_vintage` "the NAICS edition the year's file uses"; the connector writes 2017 for every year before 2022, so 2012 to 2016 read 2017. Those files' own vintages run from 2017-05-09 to 2018-09-13, and the Bureau's practice (not checked against its pages in this session) was to use NAICS 2012 for those reference years. The flag records the connector's rule, not the file.

Acted on in session 2222: the connector's docstring now says a withheld figure is a zero with its flag, D or S in these files, not N. The NAICS vintage column and the dropped size-class letter are recorded, not changed; the table is not written again (a docstring changes no row), and a reader takes a zero with flag D or S as withheld.

## The session report against the table

Every figure of `SESSION_2160_REPORT.md` checked against the table and the rerun cross-check holds (1,836 rows; the 50 states and DC in every year from 2012 to 2023; the three variables and the noise flags; Spearman 0.56; Virginia's 48.5 to 77.7 TWh; establishments near 600, 510 to 652; Pearson 0.36; the nation's employment 433,438 in 2012 and 629,527 in 2023), except:

- "California, Texas and Virginia lead both": they lead the operator sites (35, 35 and 33), but in 2023 employment Virginia is fourth (33,404), behind New York (39,730).
- The Spearman 0.56 includes the row "US" (53 sites without a state, 0 employment); without it the figure is 0.65.
- "The nation's 518210 employment grew from 433,438 (2012)": the sum holds, but it counts North Dakota, South Dakota, Vermont and Wyoming, whose 2012 employment is withheld, as zero.

Not testable from the table: "15 requests of 20" and the files' "93 MB of text"; the saved zips are 10.2 to 11.9 MB, not the report's "12 MB".

## What it does not hold

- Counties, metropolitan areas or ZIP codes; legal forms apart (the files' lfo other than "-"); first-quarter payroll; employment size classes and their flags; any NAICS code but 518210; years before 2012 or after 2023.
- Electricity: the industry's workforce, not its load (session 2160's own caution).
