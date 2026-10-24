# U.S. natural gas delivered for the account of others by state and sector, a year, 1982 to 2024: residential, commercial and industrial volumes and their shares of each sector's deliveries (EIA, Natural Gas Annual)

Energy Research Warehouse (ERW), method note written in session 2380 (chain 112) for a table first written on 24 October 2026 (session 2377 of chain 112, its report `archive/sessions/SESSION_2377_REPORT.md`).

Tables: `eia_gas_for_others_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), Natural Gas Annual, natural gas delivered for the account of others, through EIA's API v2, route `natural-gas/cons/acct`. The route's metadata (`runs/c112/s2377/meta_acct.json`) gives the annual frequency only, the facets duoarea, product, process and series, and the years 1982 to 2024. The header's page is the route itself, `https://api.eia.gov/v2/natural-gas/cons/acct/`; the access line is `https://api.eia.gov/v2/natural-gas/cons/acct/data/?frequency=annual&data[]=value&start=1982`, with the six processes as facets, pages of 5,000 sorted by period and series.

| Process | EIA's process name | Variable | Unit as EIA gives it |
|---|---|---|---|
| VRT | Residential Transported | residential_for_others | MMCF |
| VF8 | Delivered to Commercial Consumers for the Account of Others | commercial_for_others | MMCF |
| VFT | Delivered to Industrial Consumers for the Account of Others | industrial_for_others | MMCF |
| VF9 | % Total Residential Consumers Deliveries | residential_share | % |
| VF6 | % of Total Commercial Delivered for the Account of Others | commercial_share | % |
| VFI | % of Total Industrial Delivered for the Account of Others | industrial_share | % |

Source id `eia:natural-gas/cons/acct`. EIA's answer holds 9,382 records (its `total`): 5,249 in MMCF and 4,133 in percent, 137 of them without a value (VF9 118, VFI 17, VF6 2). The two pages are saved in `warehouse/raw/eia_gas_for_others/20261024T090153Z/` (5,000 and 4,382 records, served at 2026-10-24T09:01:59Z and 09:02:05Z, 1,757,644 and 1,538,344 bytes, without a Last-Modified). Session 2377 made 5 requests to api.eia.gov: two routes' metadata (`natural-gas/prod/shalegas`, which ends in 2021, and `natural-gas/cons/acct`), a year's sample of the second (`runs/c112/s2377/sample_acct.json`, 2024: 269 records) and the trial's two pages. No page of EIA's was saved under `runs/license_reads/`.

Connector: `warehouse/connectors/eia_gas_for_others.py` (session 2377, written by `runs/c112/s2377/make_connector.py` from `eia_gas_storage_type.py`): `[--from 1982] [--offline | --fresh] [--out-dir DIR]` (the docstring's usage line omits `--out-dir`), at most 10 requests a run, 3 seconds apart; a page saved in `warehouse/raw` is reused unless `--fresh`. A process not asked for, an area or unit not in its maps, a period that is not a year, a key given twice or a count of records other than EIA's total stops the run; a record without a number has no row. The percent is divided by 100 and written as a ratio. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

The trial (`runs/c112/s2377/trial.out`: 2 requests) fetched the pages; the write, run `20261024T090233Z` ("0 requests of 10"; "File holds 9245 rows, one snapshot; the previous file held 0 rows"), read them from `warehouse/raw` ("raw file reused"). `retrieved_at` is the time EIA served each row's page: 2026-10-24T09:01:59Z for 4,988 rows and 09:02:05Z for 4,257; `vintage` is blank.

EIA's records carry no preliminary or revision flag. The table is a snapshot: a run replaces the whole file, but a run reuses saved pages unless `--fresh`, so a revision reaches the table only on a run that asks the pages again.

## Shape and variables

Series, 9,245 rows, 269 entities `eia_gas_for_others:<series>` (EIA's series id, one a measure and area, as NA1502_NUS_2), `freq` P1Y, `market` blank, `node` EIA's series description (7 series are described in "(Million Cubic Feet)", the rest in "(MMcf)" or "(%)"). `geo` US or US-<state>: 51 areas in all, the U.S. and 49 states and DC; Hawaii has no row.

| Variable | Unit | Series | Rows | First | Zeros | Areas without a series |
|---|---|---|---|---|---|---|
| residential_for_others | MMcf | 36 | 1,237 | 1988 | 490 | HI and 15 states (AK, AR, DE, ID, MN, NC, ND, NV, OR, RI, SC, TN, UT, VT, WA) |
| commercial_for_others | MMcf | 50 | 1,888 | 1987 | 62 | HI, VT |
| industrial_for_others | MMcf | 50 | 2,124 | 1982 | 102 | HI, DC |
| residential_share | ratio | 33 | 476 | 2007 | 133 | the 16 above and IA, MO, SD |
| commercial_share | ratio | 50 | 1,753 | 1989 | 4 | HI, VT |
| industrial_share | ratio | 50 | 1,767 | 1989 | 6 | HI, DC |

Every series ends in 2024. The U.S. rows, from `runs/c112/s2375/notes/gfo.out`:

| Year | Residential, MMcf | Commercial, MMcf | Industrial, MMcf | Residential share | Commercial share | Industrial share |
|---|---|---|---|---|---|---|
| 1982 | | | 867,124 | | | |
| 1990 | 31,302 | 352,521 | 4,544,535 | | 0.134 | 0.648 |
| 2000 | 371,972 | 1,147,565 | 6,529,240 | | 0.361 | 0.802 |
| 2010 | 552,116 | 1,317,138 | 5,651,037 | 0.12 | 0.425 | 0.828 |
| 2020 | 607,816 | 1,478,290 | 7,140,003 | 0.13 | 0.467 | 0.869 |
| 2024 | 532,042 | 1,567,302 | 7,415,212 | 0.12 | 0.472 | 0.864 |

- **The residential share is in whole percents.** All 476 residential share values are whole percents (0.09 to 0.14 for the U.S.), against 179 of 1,753 commercial and 181 of 1,767 industrial values, which EIA gives to a tenth of a percent. So 105 state-years carry a residential volume above 0 and a share of 0.
- **Three ways of having nothing.** For a state and year with no such deliveries, EIA may give a zero (490 residential volume rows, 11 of the 36 residential volume records of 2024), a record without a value (137 records, no row), or no record at all. The table keeps the zeros as rows.
- **No negative value.** The largest share is 0.998 (industrial).

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z, a label for the calendar year; the volumes are the year's totals and the shares the year's. A record without a value has no row; nothing is filled. The series start in different years (table above): EIA has no record for the U.S. residential volume before 1988 (1988 itself is 0), for the shares before 1989, or for the residential share before 2007.

## License

Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Natural Gas Annual")." `warehouse/metadata/license_verdicts.csv` and `docs/licenses.md`: read 1 (EIA's copyrights and reuse page), "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", if the ERW sells anything "may be public"; EIA asks for "Source: U.S. Energy Information Administration" with the date. The table's row: flag public, "agrees", ERW verdict public.

## Checks (session 2380)

The figures in this note were computed from the rows of `warehouse/output/eia_gas_for_others_annual.csv`, read past its 10 header lines (counted), and from the two saved pages, read only (scripts `runs/c112/s2375/notes/gfo.py`, `gfo2.py` and `gfo3.py`, outputs `gfo.out`, `gfo2.out` and `gfo3.out` beside them).

- 9,245 rows, 269 series, 1982 to 2024, as header lines 3 and 10 state; no (entity, variable, ts_utc) twice; MMcf on every volume and ratio on every share row.
- **Against EIA's pages:** the 9,382 records less the 137 without a value are the table's 9,245 rows, key for key, each value EIA's (a percent divided by 100) with 0 differences.
- **The trial against the table:** `runs/c112/s2377/trial/eia_gas_for_others_annual.csv` has the same 9,245 keys with 0 differences in value or `retrieved_at`.
- **The states against the U.S.:** in every year with both, the states add to the U.S. within 3 MMcf (residential, 37 years, exact in 17), 5 MMcf (commercial, 38 years) and 599 MMcf (industrial, 43 years, the largest in 1984).
- **The shares against the volumes**, set against the year's sum of `eia_gas_consumption_state_monthly` (from 2001): commercial within 0.0006 in all 1,200 state-years; residential within 0.005 in all 476, as whole percents allow; industrial within 0.005 in 1,179 of 1,183. The four others are Maine in 2002, 2004, 2005 and 2006, where the monthly table's industrial consumption (23,672, 16,234, 6,500 and 17,515 MMcf) is several times what EIA's volume and share imply (3,276 MMcf at 0.893 in 2002).
- Session 2377's cross-check (`runs/c112/s2377/cross.py`, `cross.out`, run on the trial): the states against the U.S. within 0.5 percent in 36 of 37 residential years (1988, a U.S. figure of 0, the other), 38 of 38 commercial and 43 of 43 industrial; 0 of 3,996 shares outside 0 to 1; the commercial share within 0.01 of the volume over the year's commercial consumption in all 1,200 state-years; the U.S. commercial share 0.461 (2021), 0.452, 0.457 and 0.472 (2024), the same either way.

## The session report against the table

Every figure of `SESSION_2377_REPORT.md` checked against the table, EIA's pages and `cross.out` holds (9,245 rows, 269 series, 1982 to 2024, the three volumes in MMcf and three shares as ratios, the cross-check's counts, 3,996 shares, 1,200 state-years, a median gap of 0.0002, 0.461 and 0.472, shalegas ending in 2021, 5 requests), except:

- "for the U.S., the 50 states and DC": Hawaii has no row (point 1).

## Limits

- **Coverage differs by sector.** Residential deliveries for others have a series for 34 states and DC, and the residential share for 31 states and DC; a sum of states is therefore a sum of the states EIA lists, which the cross-check shows adds to the U.S.
- **The residential share is coarse**: whole percents, so small programs show as 0.
- **The share's denominator is EIA's annual deliveries.** Another ERW table's consumption can differ from it (Maine's industrial, 2002 to 2006).

## What it does not hold

- The volumes delivered by the local distribution companies themselves, the numbers of customers on choice programs (EIA's other Natural Gas Annual tables), prices, months, Hawaii, and the electric power and vehicle fuel sectors.

## Points for the session to act on

1. **Hawaii is missing, and two sectors lack an area.** The report says the table holds "for the U.S., the 50 states and DC" the three volumes and shares. EIA's records name 51 areas (the U.S., 49 states and DC); Hawaii (SHI, in the connector's map) has no record in any process. DC has no industrial series and Vermont no commercial series. The header could name the absent areas.
2. **"EIA gives no record where a state has no such deliveries" is not how EIA answers.** The docstring and header line 3 say so. EIA gives a 0 for many such state-years (490 residential, 102 industrial, 62 commercial volume rows are 0; in 2024, 11 of the 36 residential volume records), a record with no value in 137 cases (118 of them residential shares), and no record at all for 15 states' residential volume. The docstring's "the residential share for 33 of the 51 areas" counts the 2024 records, of which 25 have a value and are rows.
3. **The residential share is in whole percents.** All 476 residential share rows are whole percents, while the commercial and industrial shares are to 0.1 percent; 105 state-years have a residential volume above 0 and a share of 0. Header line 2 could say so.
4. **The usage line omits `--out-dir`.** The docstring's usage line is `[--from 1982] [--offline | --fresh]`; the connector also takes `--out-dir DIR`, which the trial used.

Compared besides, with no contradiction found: the header's and docstring's counts (9,382 records, 9,245 rows), the years, the processes and their variables, the units, the percent divided by 100, "The states are parts of the U.S.: a sum takes one level", "nothing is filled", `retrieved_at` against the raw manifest, and every row against EIA's pages.

Acted on in session 2380: the docstring and header line 3 now say what EIA gives where a state has none (a 0, a record without a value, or no record), name Hawaii's, DC's industrial and Vermont's commercial absences, and say the residential share is in whole percents; the docstring's 2024 counts are gone and its usage line names `--out-dir`. Session 2377's report now says 49 states and DC. The table was written again offline: the same rows.
