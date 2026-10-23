# Sunlight measured on the ground near California's and Texas's solar fleets, a month (NOAA, U.S. Climate Reference Network, monthly01)

Energy Research Warehouse (ERW), method note written in session 2116 (chain 069) for a table first written on 23 October 2026 (session 2107).

Tables: `noaa_uscrn_solar_monthly`

## Publisher and address

National Oceanic and Atmospheric Administration (NOAA), National Centers for Environmental Information (NCEI), U.S. Climate Reference Network (USCRN), the monthly01 product: one fixed-width file a station, with the product's `headers.txt` read to check the columns:

`https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/headers.txt`
`https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/CRNM0102-<station>.txt`

The column kept is SOLRAD_MONTHLY_AVG, the month's average of daily total global solar radiation. The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `noaa:uscrn_monthly01`. Connector: `warehouse/connectors/noaa_uscrn.py` (session 2107), its only table. NCEI's robots file disallows `/data*` and `/orders*`, not `/pub/` (the docstring and session 2107's report). The file asked for NASA POWER's daily point API; session 2107 did not ask it for data, because power.larc.nasa.gov's robots file disallows `/api/` for every reader, and took NOAA's own network in its place.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2116), and `run_status.csv` holds no row for it. It was written once, by run `20261023T213319Z` on the data machine.

## Vintage and revision

April 2003 to September 2026 (`ts_utc` 2003-04-01 to 2026-09-01), from each station's first valid month. The station files were retrieved from 2026-10-23T21:31:00Z to 21:31:03Z by the session's probe and reused by the write run; the rows' `vintage` (the files' Last-Modified) is 2026-10-02T10:36:54Z (1,022 rows) or 10:36:57Z (1,003). `coverage.csv` gives the same 2,025 rows, 8 entities and the same first and last `ts_utc`.

Each run writes the whole table again (`ip.write_snapshot`). NOAA's months are local standard time; `ts_utc` is the month's first day written at 00:00 UTC.

## Shape and variables

Series, 2,025 rows, eight stations, one variable. `entity` `uscrn:<WBAN number>`; `variable` `solar_radiation`; `unit` `MJ/m2-day` (megajoules a square meter a day, Decision 64; 1 MJ/m2-day is 0.2778 kWh/m2-day), NOAA's unit kept, not converted; `freq` P1M; `geo` US-CA or US-TX; `ba` the grid the station sits in (`ciso` or `erco`); `node` the station's name; `x_station` the file's name; `x_lat`, `x_lon` (WGS-84, one place a station); `x_logger` the datalogger program's version.

| Station (`entity`, `ba`) | Months | First | Last | Mean | Lowest | Highest |
|---|---|---|---|---|---|---|
| Fallbrook 5 NE (`uscrn:53151`, ciso) | 221 | May 2008 | Sep 2026 | 18.16 | 4.7 (Dec 2012) | 28.9 (Jun 2014) |
| Merced 23 WSW (`uscrn:93243`, ciso) | 257 | Apr 2004 | Sep 2026 | 18.56 | 3.5 (Dec 2025) | 30.9 (Jun 2010) |
| Stovepipe Wells 1 SW (`uscrn:53139`, ciso) | 266 | Jun 2004 | Sep 2026 | 19.23 | 7.5 (Dec 2019) | 30.5 (Jun 2008) |
| Redding 12 WNW (`uscrn:04222`, ciso) | 278 | Apr 2003 | Sep 2026 | 16.84 | 3.8 (Dec 2010) | 29.9 (Jul 2009) |
| Monahans 6 ENE (`uscrn:03047`, erco) | 278 | Jun 2003 | Sep 2026 | 18.85 | 5.5 (Dec 2008) | 29.6 (Jun 2005) |
| Austin 33 NW (`uscrn:23907`, erco) | 224 | Feb 2008 | Sep 2026 | 16.64 | 6.2 (Dec 2014) | 27.3 (Jun 2011) |
| Bronte 11 NNE (`uscrn:03072`, erco) | 236 | Jan 2007 | Sep 2026 | 17.56 | 7.7 (Dec 2016) | 27.6 (Jun 2011) |
| Edinburg 17 NNE (`uscrn:12987`, erco) | 265 | Mar 2004 | Jun 2026 | 16.97 | 6.7 (Nov 2015) | 25.9 (Jul 2009) |

All values in MJ/m2-day. The eight stations' mean is 17.87; the California stations' 18.18 (1,022 rows) and the Texas stations' 17.55 (1,003). Over all the rows held, the month with the highest mean is June in both grids (California 27.35, Texas 23.95, with July 23.61); session 2107's report gives July for Texas (23.8) from its cross-check's months from 2015 on, a narrower window. Months missing inside a station's span (NOAA's -9999.0, no row): Merced 13 (August 2021 to January 2022, January to July 2026), Redding 4 (July to October 2018), Edinburg 3 (November 2017, December 2020, January 2021), Monahans 2 (April 2004, March 2007), Stovepipe Wells 2 (September and October 2005), Bronte 1 (October 2016), Fallbrook and Austin none. The header's counts (Merced 15, Edinburg 8, Redding 6, Monahans 4, Stovepipe Wells 4, Bronte 3, Fallbrook 2, Austin 1) also count months before a station's first row or after its last. The counts were computed in session 2116 from the rows, read past the 10 header lines; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- Before any request, NCEI is checked against `warehouse/metadata/paused_sources.csv` by connector and by host; a paused publisher stops the run with no request. NCEI is not paused.
- `headers.txt` must name the 15 columns as read, or the run stops.
- A line that does not split into 15 fields, a year and month that does not read, a station's WBAN number or place changing within its file, a month given twice, a negative value other than -9999.0, or a station with no valid month stops the run, and nothing is written.
- A month NOAA writes -9999.0 (its note H: valid only with fewer than 4 consecutive and at most 5 total days missing) has no row and is counted in the header. Nothing is filled.
- Ceiling: nine requests a run (`headers.txt` and the eight stations' files), by the code's shape rather than a counter. Each address is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried. One second after each request.

## The cross-check

Session 2107 set the mean of each grid's stations against California's and Texas's monthly solar generation (`state_generation_mix_monthly`), ranked within each year, in `runs/c069/s2107/cross.py` (on the data machine, not in git). In California the Spearman correlation is 0.86 to 0.99 in every year from 2015 to 2025; in Texas it is 0.70 to 0.94 in every year but 2016 (0.10), when Texas's fleet grew within the year and generation peaked in October.

## License

The header: "License: may be public (NOAA NCEI: a work of the U.S. government; its restriction concerns the non-U.S. data in ISD, not USCRN; see license_verdicts.csv). Cite NOAA NCEI, U.S. Climate Reference Network." `license_verdicts.csv` gives NOAA NCEI "may be public" (read 9; the same if the ERW sells anything), and `docs/licenses.md` gives the ERW verdict public. `coverage.csv`: public. Session 2107's report holds the table in the live set's catalogue hold and the release's storage hold.

## Found while writing this note

- The docstring says the files are "saved in warehouse/raw/noaa_uscrn/ and reused offline". The code calls `ip.fetch_raw` without `fresh`, which reuses a saved copy on every run, offline or not: a later run reads the files of 23 October 2026 again and gains no month until the raw files are moved.
- Session 2107's report gives the table as running to September 2026; Edinburg's last row is June 2026 (the saved file writes -9999.0 for July to October 2026, among its 8 months without a row).
**Acted on in session 2116:** the connector now asks for its documents again unless `--offline` (`fresh=not args.offline`), so a later run sees a newer month; the source registry's license word is now `public`. Session 2107's range is corrected in an addendum to its report (Edinburg's last row is June 2026).

## What it does not hold

- Daily or hourly radiation: monthly01 only (USCRN's daily files are one a station a year).
- Temperature, precipitation and the other columns of the same files: read and not written.
- Stations outside California and Texas, and any satellite or modelled radiation (NASA POWER is not asked).
