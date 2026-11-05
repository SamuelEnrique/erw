# U.S. refinery utilization and capacity a month, January 1985 to July 2026: gross input, operable, operating and idle capacity, and utilization, for the U.S., the PADDs and the refining districts (EIA, Petroleum Supply Monthly)

Energy Research Warehouse (ERW), method note written in session 2331 (chain 108) for a table first written on 24 October 2026 (session 2334 of chain 108, its report `archive/sessions/SESSION_2334_REPORT.md`).

Tables: `eia_refinery_utilization_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, refinery utilization and capacity, through EIA's API v2, route `petroleum/pnp/unc`. The route's metadata (`runs/c108/s2334/meta_petroleum_pnp_unc.json`) gives monthly and annual frequencies, the facets duoarea, product, process and series, and the months 1985-01 to 2026-07. The header's page is the route itself, `https://api.eia.gov/v2/petroleum/pnp/unc/`; the access line is `https://api.eia.gov/v2/petroleum/pnp/unc/data/?frequency=monthly&data[]=value&start=1985-01`, with the five processes YIY, YRL, YRO, YRI and YUP as facets, sorted by period and series, in pages of 5,000 records, with EIA's key (read from `.env`, never saved; `REDACTED` in every saved address and in each row's `source_url`). Source id `eia:petroleum/pnp/unc`.

EIA's answer holds 36,672 records (its `total`), units "MBBL/D" and "%", none without a value. The eight pages are saved in `warehouse/raw/eia_refinery_utilization/20261024T073336Z/`, served from 2026-10-24T07:33:40Z to 07:34:07Z (the raw manifest; 5,000 records a page, 1,672 on the last), without a Last-Modified. Session 2334 made 12 requests to api.eia.gov: three routes' metadata (`petroleum/cons/refmg`, `petroleum/stoc/typ`, `petroleum/pnp/unc`), a year's sample of `pnp/unc` (`runs/c108/s2334/sample_unc.json`, 2025) and the first trial's eight pages. No page of EIA's was saved under `runs/license_reads/` for this table; EIA's verdict is read 1.

Connector: `warehouse/connectors/eia_refinery_utilization.py` (session 2334, written by `runs/c108/s2334/make_connector.py` from `eia_gas_storage_type.py`): `[--from 1985-01] [--offline | --fresh] [--out-dir DIR]` (the docstring's usage line omits `--out-dir`), at most 12 requests a run, 3 seconds apart; a page saved in `warehouse/raw` is reused unless `--fresh`. A process not asked for, an area not in its map (the U.S., five PADDs, ten districts), a unit not in its map, a key given twice or a count of records other than EIA's total stops the run; a record without a number has no row. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public, and it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

The pages were fetched by session 2334's first trial (`runs/c108/s2334/trial.out`: 8 requests). The second trial (`trial2.out`) and the write, run `20261024T073523Z` ("0 requests of 12"; "File holds 36672 rows, one snapshot; the previous file held 0 rows"), read them from `warehouse/raw`. `retrieved_at` is the time EIA served each row's page, 2026-10-24T07:33:40Z to 07:34:07Z (5,000 rows each for the first seven pages, 1,672 for the eighth); `vintage` is blank.

EIA's records carry no preliminary or revision flag. The table is a snapshot: a run replaces the whole file, but a run reuses saved pages unless `--fresh`, so a revision reaches the table only on a run that asks the pages again.

## Shape and variables

Series, 36,672 rows, 80 entities `eia_refinery_utilization:<series>` (EIA's series id, one a measure and area), `geo` US in every row, `freq` P1M, `market` blank, `node` EIA's series description. 16 areas: the U.S. (NUS), PADDs 1 to 5 (R10 to R50) and ten refining districts: East Coast (REC) and Appalachian No. 1 (RAP) in PADD 1; Indiana, Illinois, Kentucky (R2A), Minnesota, Wisconsin, North and South Dakota (R2B) and Oklahoma-Kansas-Missouri (R2C) in PADD 2; Texas Inland (R3A), Texas Gulf Coast (R3B), Louisiana Gulf Coast (R3C), North Louisiana-Arkansas (R3D) and New Mexico (R3E) in PADD 3.

| Variable | EIA's process | Unit | Series | Rows |
|---|---|---|---|---|
| gross_input | YIY, gross inputs to refineries | kbbl/d | 16 | 7,984 |
| operable_capacity | YRL, operable capacity | kbbl/d | 16 | 7,984 |
| operating_capacity | YRO, operating capacity | kbbl/d | 16 | 7,984 |
| idle_capacity | YRI, idle operable capacity | kbbl/d | 16 | 4,736 |
| utilization | YUP, utilization of operable capacity | ratio (EIA's percent / 100) | 16 | 7,984 |

The U.S., yearly means of the months (`runs/c108/s2331/notes/ref.out`):

| Year | Gross input | Operable | Operating | Idle | Utilization |
|---|---|---|---|---|---|
| 1985 | 12,160.8 | 15,670.8 | 14,513.1 | 1,157.6 | 0.776 |
| 1990 | 13,611.0 | 15,623.5 | 14,973.8 | 649.4 | 0.871 |
| 2000 | 15,295.5 | 16,524.9 | 16,250.3 | 275.0 | 0.926 |
| 2010 | 15,173.2 | 17,574.8 | 16,909.3 | 665.2 | 0.863 |
| 2019 | 16,986.6 | 18,808.0 | 18,437.5 | 370.8 | 0.903 |
| 2020 | 14,725.3 | 18,662.9 | 17,989.6 | 673.3 | 0.789 |
| 2024 | 16,601.3 | 18,348.4 | 18,172.2 | 176.3 | 0.905 |
| 2025 | 16,724.8 | 18,181.0 | 18,033.2 | 147.7 | 0.920 |
| 2026 (January to July) | 16,748.6 | 18,064.6 | 17,996.4 | 68.1 | 0.927 |

kbbl/d, except utilization. The U.S.'s highest month is August 1998 (0.999), its lowest April 2020 (0.702). In July 2026 the U.S. ran at 0.965 (17,420 of 18,044 kbbl/d); the Texas Gulf Coast district at 0.967 (5,219 of 5,399), New Mexico at 0.547 (60 of 110).

- **Utilization above 1.** 483 area-months have utilization above 1.000, gross input above operable capacity: 133 in district R2B, 101 in Appalachian No. 1, 59 in New Mexico, 53 in R2C, 44 in Texas Inland, and in PADDs 1 to 4 (3, 19, 6 and 13); the highest is New Mexico's 1.126 in June 2017. PADD 2 is above 1 in June and July 2026 (1.006 and 1.009). The U.S. never is.
- **Idle capacity is given only where it is not zero, mostly.** `idle_capacity` has 4,736 rows against 7,984 for the other measures. In each of the 3,248 area-months without one, operable capacity equals operating capacity, so the idle capacity is nil; EIA prints a 0 in 457 other area-months. The U.S.'s series is complete; New Mexico's ends in August 2020, North Louisiana-Arkansas's in March 2024.
- **Two wordings of gross input.** Four series' descriptions read "Gross Inputs to Atmospheric Crude Oil Distillation Units" (PADD 1 and the R2C, R3B and R3E districts), the others "Gross Inputs to Refineries"; all are process YIY, and PADD 1 equals East Coast plus Appalachian No. 1 in every month.
- **Levels overlap.** The districts are parts of their PADDs and the PADDs of the U.S. (header line 2: "a sum takes one level").

## Placing values in time, and what is filled

`ts_utc` is the month's first day at 00:00:00Z (EIA's `period`, YYYY-MM), January 1985 to July 2026 (499 months). Every area has gross input, operable and operating capacity and utilization in all 499 months; EIA serves no record for the missing idle-capacity months, so EIA's 36,672 records are the table's 36,672 rows. Nothing is filled.

## License

Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly")." `warehouse/metadata/license_verdicts.csv` and `docs/licenses.md`: read 1 (EIA's copyrights and reuse page), "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", if the ERW sells anything "may be public"; EIA asks for "Source: U.S. Energy Information Administration" with the date. The table's row: flag public, "agrees", ERW verdict public.

## Checks (session 2331)

The figures in this note were computed from the rows of `warehouse/output/eia_refinery_utilization_monthly.csv`, read past its 10 header lines (counted), and from the eight saved pages, read only (scripts `runs/c108/s2331/notes/ref.py`, `ref2.py`, `ref3.py` and `trials.py`, outputs `ref.out`, `ref2.out`, `ref3.out` and `trials.out` beside them).

- 36,672 rows, 80 series, January 1985 to July 2026, "36,672 records of EIA's, 36,672 rows", as header line 3 states; no (entity, variable, ts_utc) twice; no blank or negative value; kbbl/d on the four capacity and input measures and ratio on utilization; geo US throughout.
- **Against the pages:** 36,672 records, the `total` of each page, none without a value; each row's area read from its series' `duoarea`.
- **The trial against the table:** `runs/c108/s2334/trial/eia_refinery_utilization_monthly.csv` (the second trial) has the same 36,672 keys with no cell differing.
- Session 2334's cross-check (`runs/c108/s2334/cross.py`, `cross.out`, run on the second trial at 07:35, after utilization became a ratio): utilization against gross input over operable capacity in 7,984 area-months, 7,819 within 0.006, the largest gap 0.0501 (Texas Gulf Coast, February 1995; 84 of the 165 misses are New Mexico's and 77 Appalachian No. 1's); operable against operating plus idle in 4,736, 4,713 within 1 kbbl/d, the largest gap 96; PADD 1 against its two districts in all 499 months within 1; PADD 2 against its three in 475 of 499 (gross input, the largest gap 65 kbbl/d; operable capacity 475, 67); PADD 3 against its five in 489 (gross input, largest 2) and 477 (operable capacity, largest 2); the U.S. against the five PADDs in 494 and 493; the PADDs' utilization against the mean of `eia_refinery_weekly`'s weeks in 970 PADD-months (June 2010 to July 2026), median gap 0.0112, 694 within 0.02, the largest 0.2023.
- Session 2331's own: the 63 PADD-months more than 0.05 from the weekly mean; the six largest are PADD 1's (0.2023 in June 2020, 0.1987 in February 2012, 0.1968 in May 2020, 0.1927 in January 2012, 0.174 in July 2020, 0.1472 in April 2025).

## The session report against the table

Every figure of `SESSION_2334_REPORT.md` checked against the table, the saved pages and `cross.out` holds (36,672 rows, 80 series, January 1985 to July 2026, the U.S., five PADDs and ten districts, kbbl/d and utilization as a ratio, 7,819 of 7,984 within 0.006 with the largest gap 0.050, 4,713 of 4,736, PADD 1 in all 499 months, PADD 3 in 489 with the largest gap 2, PADD 2 in 475 with the largest gap 65 kbbl/d, the U.S. in 494, 694 of 970 PADD-months within 0.02 with a median of 0.011, utilization 0.776, 0.926, 0.903, 0.789, 0.905 and 0.920 and operable capacity 15,671 and 18,181 kbbl/d, the three routes, 12 requests of 20), with no exception. What it leaves out is in points 1, 2 and 4.

## What it does not hold

- The annual figures of the same route, crude oil and other inputs by type, refinery production, downstream charge capacity, capacity by refinery (`eia_refinery_capacity_annual`), the weekly estimates (`eia_refinery_weekly`), months before 1985, and refinery districts' names as EIA's `area-name` (it is "NA" for every district; the names are in `node`).

## Points for the session to act on

1. **A missing idle capacity means nil, and the header does not say so.** `idle_capacity` has no row in 3,248 area-months, and in every one of them operable capacity equals operating capacity (`ref3.out`), so EIA leaves the record out where idle capacity is zero, while printing 0 in 457 others. Header line 3's "A blank has no row; nothing is filled" reads as if those months were unknown. A clause saying an absent `idle_capacity` month has operable equal to operating would let a reader treat it as 0.
2. **Utilization above 1 is not described.** 483 area-months have utilization above 1.000, as high as 1.126 (New Mexico, June 2017), and PADD 2 is above 1 in June and July 2026. The header and docstring call it "the utilization of operable capacity" without saying it can exceed 1 (gross input above operable capacity). It is EIA's figure as published, but a reader or a check that bounds a ratio at 1 would reject these rows.
3. **`cross.py`'s docstring names the wrong comparison.** It says it checks "the U.S. utilization against the month's mean of eia_refinery_weekly's"; the code compares the five PADDs, as its own printed line says ("the weekly table has the PADDs only"). The report states it rightly.
4. **The PADD comparison's spread is not reported.** The report gives the median (0.011) and 694 of 970 within 0.02, but not the largest gap, 0.2023, which `cross.out` prints, nor that the 63 PADD-months over 0.05 are led by PADD 1 (0.2023 in June 2020, 0.1987 in February 2012). A reader joining the weekly and monthly tables for PADD 1 should know the two can differ by 20 points of utilization.

Compared besides, with no contradiction found: the header's and docstring's counts, processes, areas, units, the ratio, "a sum takes one level", "Each row carries the time EIA served its page", "A blank has no row; nothing is filled" (EIA serves no blank) and the license against the rows and the pages. The docstring's usage line omits `--out-dir`, which the code accepts.

Acted on in session 2331: the docstring and header line 3 now say that utilization exceeds 1 in 483 area-months and that an absent `idle_capacity` month has operable equal to operating capacity (nil, not unknown). `runs/c108/s2334/cross.py`'s docstring names the PADD comparison, and it now prints the 63 PADD-months over 0.05 and the largest (PADD 1, 0.2023 in June 2020); session 2334's report carries both. The table was written again offline: the same rows.
