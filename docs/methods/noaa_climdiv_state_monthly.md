# Each state's temperature and precipitation, a month (NOAA NCEI's nClimDiv)

Energy Research Warehouse (ERW), method note written in session 2052 (chain 059) for a table first written on 23 October 2026 (session 2045).

Tables: `noaa_climdiv_state_monthly`

## Publisher and address

NOAA's National Centers for Environmental Information (NCEI), nClimDiv (Vose et al. 2014), the statewide files behind Climate at a Glance, in the directory `https://www.ncei.noaa.gov/pub/data/cirs/climdiv/`: `climdiv-tmpcst-v1.0.0-<YYYYMMDD>` (temperature), `climdiv-pcpnst-v1.0.0-<YYYYMMDD>` (precipitation) and the two `climdiv-norm-` files of the means of special periods. The newest of each name in the directory's listing is read. Source id `noaa:climdiv`. Connector: `warehouse/connectors/noaa_climdiv_states.py` (session 2045).

## Vintage and revision

January 2000 to September 2026, from the four files processed 6 October 2026 (`vintage` 2026-10-06T00:00:00Z in every row), written by run `20261023T185222Z` (23 October 2026) from the saved files. Header: "This run wrote 31458 rows: 31458 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs."

The table is merged on (entity, variable, ts_utc): a later run replaces a month NCEI restates and keeps the months it no longer reads. The listing is asked fresh each run; a file is reused from `warehouse/raw/noaa_climdiv_states/` when one of that name was saved, and a newly processed file has a new name.

## Shape and variables

Series, 31,458 rows: 49 areas, 2 variables, 321 months each (98 series of 321 rows, none missing). `entity` `noaa_climdiv:<NCEI state code>`, NCEI's own numbering (001 Alabama to 048 Wyoming, 110 the contiguous United States), not FIPS; `node` the state's name; `geo` its ISO 3166-2 code, `US` for 110; `freq` P1M; `ts_utc` the month's first day; `market` empty.

| Variable | Unit | Rows |
|---|---|---|
| `temp_avg` | degF | 15,729 |
| `precip` | in (Decision 60) | 15,729 |

`x_mean_1901_2000` is NCEI's own 1901 to 2000 mean of that state, element and calendar month, read from the normals file's period 0031, not computed; it is the same in each of a series' 27 or 26 rows of a calendar month.

Texas: January 2025 42.8 F (its mean 45.4), July 2025 82.2 F (82.3). The contiguous nation was above its 1901 to 2000 mean in 262 of the 321 months; its warmest whole years here are 2024 (55.48 F, the mean of the twelve months), 2012 (55.27) and 2016 (54.90). The warmest state-month is Oklahoma's July 2011 (89.2 F), the coldest North Dakota's February 2019 (-2.7 F); the wettest Connecticut's October 2005 (15.92 in).

## Reading the source

- Each record is 94 characters: a 3-digit state code, the division digit 0, the element code (01 precipitation, 02 temperature), the year (or, in the normals files, the period code), then twelve 7-character values. A line of another length, a division other than 0 or an element other than the file's stops the run; a state or nation without its 1901 to 2000 mean stops it.
- A code not in the map (Alaska, Hawaii, NCEI's regions) is not taken (lines 96 to 99); the docstring, corrected by session 2052, says so.
- A value equal to NCEI's missing mark (-99.90 for temperature, -9.99 for precipitation) is an omitted row in any year (line 115), and another value at or below the mark stops the run; no month before the latest year's unprocessed ones is marked. The docstring and session 2045's report, corrected by session 2052, say so.
- Ceiling: five requests (the listing and the four files).

## License

`license_tables.csv` lists the table under NOAA NCEI. `license_verdicts.csv` records NOAA NCEI, read 9: "may be public", for public and for commercial use; the sentence read is ISD's restriction on non-U.S. stations, and its note says the page names no license for U.S. data. `docs/licenses.md` lists the table as may be public, flagged public, agreeing.

## Cross-checks (session 2052)

- The counts above were computed from the rows, read past the header lines. No (entity, variable, ts_utc) is given twice; each entity has one `node`; the 321 months run without a gap.
- `x_mean_1901_2000` takes one value per entity, variable and calendar month in all 98 series (no series with two).
- Session 2045's report set each state's temperature against `noaa_cpc_degree_days_daily` summed to the month, January 2024 to September 2026: correlation with cooling degree days June to September median 0.988 (lowest 0.906, California), with heating degree days December to March median -0.982 (weakest -0.923, Washington).

## What it does not hold

- Alaska, Hawaii, NCEI's climate divisions and regions.
- Years before 2000 (the files hold 1895 on; `--first-year` takes them).
- Anomalies: the mean is kept beside each month, the subtraction is left to the reader.
- Any element of the directory but average temperature and precipitation.
