# The API gravity and sulfur content of the crude oil U.S. refineries run, a month from 1985: the U.S., the five PADDs and ten refining districts (EIA, Petroleum Supply Monthly)

Energy Research Warehouse (ERW), method note written in session 2247 (chain 101) for a table first written on 24 October 2026 (session 2244 of chain 101, its report `archive/sessions/SESSION_2244_REPORT.md`; written again offline in session 2245, `archive/sessions/SESSION_2245_REPORT.md`).

Tables: `eia_crude_quality_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, crude oil input qualities, through EIA's API v2, route `petroleum/pnp/crq` (the route's metadata names its parent "EIA petroleum gas survey data" and gives monthly and annual frequencies, 1985-01 to 2026-07). The header's page is the route itself, `https://api.eia.gov/v2/petroleum/pnp/crq/`; the access line is `https://api.eia.gov/v2/petroleum/pnp/crq/data/?frequency=monthly&data[]=value&facets[process][]=YCG&facets[process][]=YCS&start=1985-01`, in pages of 5,000 records, with EIA's key (read from `.env`, never saved; `REDACTED` in every saved address and in each row's `source_url`). Source id `eia:petroleum/pnp/crq`.

Two processes, both of product EPC0 "Crude Oil": YCG "Refinery Inputs, Average API Gravity" (unit "D") and YCS "Oil Refinery Inputs, Average Sulfur Content" (unit "%"). Sixteen areas: NUS (the U.S.), the PADDs R10 to R50, and the refining districts R2A, R2B, R2C, R3A to R3E, RAP (Appalachian No. 1) and REC (East Coast). Session 2244 read the route's metadata (`runs/c101/s2244/meta.json`) and a page of 2025 (`sample.json`, 384 records, these two processes and sixteen areas only). No page of EIA's was saved under `runs/license_reads/`; EIA's verdict is read 1. The four data pages are in `warehouse/raw/eia_crude_quality/20261024T033903Z/`.

Connector: `warehouse/connectors/eia_crude_quality.py` (session 2244): `[--from 1985-01] [--offline | --fresh] [--out-dir DIR]`, at most 10 requests a run, 3 seconds apart; a page saved in `warehouse/raw` is reused unless `--fresh`. A process, unit or area not in its map, or a key given twice, stops the run; a record without a number has no row. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

The four pages were fetched by session 2244's trial (run `20261024T033903Z`) at 2026-10-24T03:39:07Z, 03:39:11Z, 03:39:15Z and 03:39:18Z (the raw manifest). Session 2244 wrote the table from them at 03:40:01Z (run `20261024T034001Z`); session 2245 wrote it again offline (run `20261024T034353Z`, "0 requests of 10") after replacing a guessed page address in the header and `sources.csv` with the route: "File holds 15968 rows, one snapshot; the previous file held 15968 rows." The rows did not change.

`retrieved_at` is 2026-10-24T03:43:53Z in every row, the second write's start, not the pages' time (disagreement 1); `vintage` is blank. EIA's pages carry no preliminary or revision flag. The table is a snapshot: a run replaces the whole file, so a value EIA revises or withdraws is revised or gone at the next run.

## Shape and variables

Series, 15,968 rows, 32 entities `eia_crude_quality:<series>` (EIA's series id), two variables: `api_gravity` in `degAPI` (Decision 73) and `sulfur_content` in `pct` (percent by weight), 7,984 rows each; `freq` P1M, `geo` US, `market` blank, `node` EIA's series description. Every series holds all 499 months from 1985-01 to 2026-07. EIA gives the values as text with at most two decimals ("33.07"; 14,403 with two, 1,416 with one, 149 with none); the table keeps each value, written as a number.

| Area (series ids) | API gravity: mean | lowest (month) | highest (month) | Sulfur, percent: mean | lowest (month) | highest (month) |
|---|---|---|---|---|---|---|
| U.S. (MCRAPUS2, MCRS1US2) | 31.527 | 29.75 (2004-11) | 34.43 (2025-10) | 1.289 | 0.86 (1985-05) | 1.51 (2013-12) |
| East Coast, PADD 1 (MCRAPP12, MCRS1P12) | 32.942 | 29.41 (1986-04) | 37.90 (2019-03) | 0.908 | 0.50 (2010-02) | 1.43 (1999-06) |
| East Coast district (MCRAPEC2, MCRS1EC2) | 32.907 | 28.47 (1986-04) | 38.46 (2019-03) | 0.869 | 0.42 (2010-02) | 1.45 (1999-06) |
| Appalachian No. 1 district (MCRAPAP2, MCRS1AP2) | 33.944 | 25.29 (2000-12) | 42.44 (1985-11) | 1.284 | 0.10 (1985-11) | 2.14 (2004-08) |
| Midwest, PADD 2 (MCRAPP22, MCRS1P22) | 33.432 | 31.12 (2004-12) | 36.33 (1985-02) | 1.272 | 0.80 (1985-05) | 1.62 (2026-01) |
| Indiana, Illinois, Kentucky (MCRAP2A2, MCRS12A2) | 33.282 | 30.48 (2016-08) | 36.88 (1985-03) | 1.310 | 0.74 (1985-02) | 1.84 (2025-07) |
| Minnesota, Wisconsin, North and South Dakota (MCRAP2B2, MCRS12B2) | 28.686 | 23.98 (2021-01) | 33.34 (1995-03) | 2.006 | 1.15 (2019-10) | 3.16 (1992-04) |
| Oklahoma, Kansas, Missouri (MCRAP2C2, MCRS12C2) | 36.630 | 33.55 (2004-12) | 40.65 (2023-03) | 0.755 | 0.43 (1985-05) | 1.47 (2007-05) |
| Gulf Coast, PADD 3 (MCRAPP32, MCRS1P32) | 31.849 | 28.68 (2011-01) | 35.57 (2025-10) | 1.376 | 0.77 (1985-05) | 1.79 (2008-12) |
| Texas Inland (MCRAP3A2, MCRS13A2) | 38.351 | 33.61 (2013-04) | 41.67 (2021-08) | 0.738 | 0.44 (2018-03) | 1.25 (1993-01) |
| Texas Gulf Coast (MCRAP3B2, MCRS13B2) | 31.490 | 26.74 (2013-08) | 36.61 (2021-02) | 1.470 | 0.75 (1985-07) | 2.08 (2008-12) |
| Louisiana Gulf Coast (MCRAP3C2, MCRS13C2) | 30.666 | 27.42 (2011-01) | 34.48 (2025-05) | 1.402 | 0.67 (1985-02) | 1.82 (2005-12) |
| North Louisiana, Arkansas (MCRAP3D2, MCRS13D2) | 31.154 | 26.47 (2001-10) | 35.78 (1991-10) | 1.548 | 0.85 (2023-04) | 2.16 (2002-03) |
| New Mexico (MCRAP3E2, MCRS13E2) | 38.753 | 30.64 (2011-07) | 41.38 (2010-01) | 0.733 | 0.30 (2009-02) | 1.93 (2011-07) |
| Rocky Mountains, PADD 4 (MCRAPP42, MCRS1P42) | 33.783 | 31.29 (2023-06) | 37.36 (1985-03) | 1.265 | 0.62 (1989-01) | 1.63 (2023-06) |
| West Coast, PADD 5 (MCRAPP52, MCRS1P52) | 27.124 | 23.99 (1998-06) | 30.49 (2020-09) | 1.240 | 0.97 (2026-07) | 1.76 (2019-08) |

Means over the 499 months, rounded to 3 decimals; where a lowest or highest value recurs, its first month is given.

The U.S. figure, a year's mean of its months: API gravity 32.46 in 1985, its lowest 30.18 in 2004 (30.20 in 2005, 30.21 in 2008), 33.75 in 2025; sulfur 0.91 percent in 1985, its highest 1.455 in 2008 (1.452 in 2014, 1.420 in 2005), 1.30 in 2025. July 2026: 33.71 degrees API and 1.24 percent.

These are weighted averages, weighted by the crude each area runs: an area's figure is not the sum or plain mean of its parts, as the header says, and a reader combining areas weights them by volume (`eia_refinery_inputs_monthly` holds the PADDs' crude input).

## Placing values in time, and what is filled

`ts_utc` is the first day of EIA's `period` (YYYY-MM) at 00:00:00Z (Decision 11), a label for the month. Every key of the four pages matches a row and every row a key; no record lacked a number, so nothing was left out and nothing is filled.

## License

Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly")." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 1 (EIA's copyrights and reuse page, `https://www.eia.gov/about/copyrights_reuse.php`), "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", if the ERW sells anything "may be public"; EIA asks for the acknowledgment "Source: U.S. Energy Information Administration" with the date. The table's row: flag public, "agrees", ERW verdict public.

## Checks (session 2247)

The figures in this note were computed from the rows of `warehouse/output/eia_crude_quality_monthly.csv`, read past its 10 header lines (counted), and from the saved pages, read only (scripts `runs/c101/s2247/eia.py`, `eia_trial.py` and the yearly means in `eia2.out`, outputs beside them).

- 15,968 rows, months 1985-01 to 2026-07, "15,968 records of EIA's, 15,968 rows", as header line 3 states; 32 series, 16 areas times two measures; no (entity, variable, ts_utc) twice; no blank value; units degAPI and pct, 7,984 rows each, as the header names them; each row's `node` is the page's series description.
- **Against the pages:** EIA's `total` is 15,968 on each of the four pages (5,000, 5,000, 5,000 and 968 records); every record has a number; the table's keys and values are the pages', with 0 differences.
- **The trial against the table:** `runs/c101/s2244/trial/eia_crude_quality_monthly.csv` has the same keys and the same values in every column but `retrieved_at` (03:39:03Z in the trial, 03:43:53Z in the table); its header named the guessed page `https://www.eia.gov/dnav/pet/pet_pnp_crq_dcu_nus_m.htm`, the table's names the route.
- Session 2244's cross-check (`runs/c101/s2244/cross.py`), run again from the main checkout with the written table as argument 1: its output is identical to the saved `cross.out`, which was run on the trial. The U.S. against the five PADDs weighted by their crude input (`eia_refinery_inputs_monthly`), over the 259 months both tables hold: API gravity a median 0.023 apart (at most 0.090), sulfur 0.003 (at most 0.010); the U.S. outside its PADDs' range in 0 of 499 months for both. Its yearly means: 1985 32.46 and 0.91, 1995 31.30 and 1.13, 2005 30.20 and 1.42, 2010 30.48 and 1.39, 2015 31.46 and 1.40, 2020 33.03 and 1.34, 2025 33.75 and 1.30.

## Where the description and the data disagree

1. **`retrieved_at` is the run's start, not the retrieval.** Header line 10 says "Per row, source, source_url and retrieved_at say where it came from". The connector sets `retrieved_at` to the moment the run starts, whether it asks EIA or reuses a saved page; the table's rows say 2026-10-24T03:43:53Z, a run that asked nothing ("0 requests of 10"), while EIA served the pages at 03:39:07Z to 03:39:18Z. Header line 4 likewise names the offline run. The pages' own times are in `warehouse/raw/eia_crude_quality/20261024T033903Z/manifest.csv`. The gap is four minutes here; a later offline write from old pages would make it larger.
Compared besides, with no contradiction found: the header's and docstring's counts, span, series, areas, processes, units and "a blank has no row" against the rows and pages. The docstring's address omits the `facets[process][]` the requests carry; the 2025 page session 2244 asked without them (`sample.py`) held only YCG and YCS, so the answer is the same.

Not acted on: this note changes no file but itself.

Acted on in session 2247. The connector now stamps each row with the time EIA served its page (a reused page's first download, kept by `ip.raw_cached`), not the time the write began; the table was written again offline (no request, the same rows), and its rows now carry EIA's serving times. Session 2247's report corrects session 2244's 2004 low and 2008 sulfur peak.

## The session report against the table

Every figure of `SESSION_2244_REPORT.md` checked against the table, the saved pages and the rerun cross-check holds (January 1985 to July 2026, 15,968 rows, 32 series for the U.S., the five PADDs and the refining districts, EIA's unit "D", sulfur in percent by weight, 259 months both tables hold, a median 0.023 degrees API at most 0.090, 0.003 percent sulfur at most 0.010, the U.S. never outside its PADDs' range in 499 months, 32.46 degrees API in 1985 and 33.75 in 2025, 1.30 percent sulfur in 2025, 6 requests, the guessed page address replaced and the table written again with the same 15,968 rows), except:

- "went from 32.46 degrees API in 1985 down to 30.20 in 2005": 30.20 is 2005's mean, but the low is 2004's 30.18; the cross-check printed only every fifth year from 1995.
- "Sulfur peaked near 1.42% in 2005": 2005's mean is 1.420, below 2001 to 2004 (1.417 to 1.432); the highest yearly mean is 2008's 1.455, then 2014's 1.452, and the highest month 1.51 in December 2013.

## What it does not hold

- The volumes that weight these averages (the PADDs' crude input is `eia_refinery_inputs_monthly`), refining districts within PADDs 4 and 5, the route's annual figures, months before 1985 and after July 2026, and the quality of crude by source or import.
