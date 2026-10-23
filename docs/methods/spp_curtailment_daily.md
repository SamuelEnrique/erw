# SPP's wind and solar curtailment by balancing authority area, a day (SPP's VER Curtailments)

Energy Research Warehouse (ERW), method note written in session 2088 (chain 068) for a table first written on 27 September 2026 (session 18).

Tables: `spp_curtailment_daily`

What each grid's curtailment figure means, and how the site uses this table, is in `docs/methods/curtailment.md` (session 18 and later); this note describes the code and the rows as they stand.

## Publisher and address

Southwest Power Pool (SPP), "VER Curtailments" (`https://portal.spp.org/pages/ver-curtailments`), files served by `https://portal.spp.org/file-browser-api/download/ver-curtailments`: five-minute MW of wind and solar curtailed, by balancing authority area (BAA). Annual zips to 2024 (`?path=/<year>/<year>.zip`), daily files since (`?path=/<year>/<month>/VER-Curtailments-<yyyymmdd>.csv`). Source id `spp:ver_curtailments`. Connector: `warehouse/connectors/curtailment.py` (session 18), function `run_spp`; the same connector writes `caiso_curtailment_daily` and `ercot_wind_solar_hsl_daily`.

## Vintage and revision

1 March 2014 to 22 October 2026 in the file on the data machine. The file was rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github`, carrying the header of run `20261023T144531Z` (23 October 2026): "This run wrote 152 rows: 16 new, 136 replacing earlier rows ... A BAA's day is written only with every 5-minute interval; 1 BAA-days were not complete in this run."

The daily run asks for the daily files of the 10 days before today (Central), so SPP's changes to those days are taken; `--history` reads the annual zips of 2014 to 2024 (`range(2014, SPP_FIRST_DAILY_YEAR)`) and every daily file from 1 January 2025. The table is merged into the one held (`iso_prices.write_csv`). `vintage` is empty. In the file, 37,912 rows (1 March 2014 to 17 September 2026) say `retrieved_at` 2026-09-27T08:42:33Z; the other 520 rows, the days from 18 September to 22 October 2026, say one of 19 later runs, 29 September to 23 October 2026. 671 `source_url` values: the 11 annual zips and 660 daily files.

## Shape and variables

Series, 38,432 rows: 2 entities, 16 series. `unit` MWh; `freq` P1D; `ts_utc` the Central (America/Chicago) date of the intervals' starts at 00:00:00Z (Decision 11); `geo`, `market` and `node` empty. MWh is the five-minute MW times 5/60, summed over the day.

| Variable | SPP's column |
|---|---|
| `curtailed_wind_redispatch_mwh` | WindRedispatchCurtailments |
| `curtailed_wind_manual_mwh` | WindManualCurtailments |
| `curtailed_wind_economic_mwh` | WindCurtailedForEnergy ("curtailed for energy") |
| `curtailed_wind_mwh` | the sum of the three wind variables |
| `curtailed_solar_redispatch_mwh`, `curtailed_solar_manual_mwh`, `curtailed_solar_economic_mwh`, `curtailed_solar_mwh` | the same for solar |

| Entity | Days | First | Last |
|---|---|---|---|
| spp:SPP | 4,618 | 2014-03-01 | 2026-10-22 |
| spp:SWPW | 186 | 2026-04-02 | 2026-10-22 |

Each entity holds all 8 variables on each of its days. spp:SWPW is SPP's western area; a file without a BAA column, or a blank BAA, is SPP's (`spp_frame`).

Wind curtailed in spp:SPP, MWh a year: 287,193 (2014, from March), 295,944 (2015), 760,917 (2016), 1,694,988 (2017), 838,555 (2018), 1,189,172 (2019), 2,134,391 (2020), 6,353,740 (2021), 11,235,614 (2022), 11,423,441 (2023), 15,568,332 (2024), 13,389,378 (2025), 10,548,229 (2026 to 22 October). The highest day: 225,848.743 MWh on 12 April 2025. Solar curtailed in spp:SPP: 7,163 (2022), 37,874 (2023), 83,860 (2024), 107,902 (2025), 174,250 (2026); in spp:SWPW in 2026: 166,895 solar and 38,395 wind.

## Reading the source

- A BAA's day is written only when it holds every five-minute interval: 288, or 276 or 300 on a day the clocks change (`expected_intervals`). The others are logged (the first 20) and counted in the header. The newest day, still filling, is never written short.
- A line with no interval time is dropped; an interval time in any other format than `%m/%d/%Y %H:%M:%S.%f` stops the table. The day is the Central date of the interval's start (`GMTIntervalEnding` less 5 minutes).
- A column of `SPP_COLS` that a file lacks is taken as 0, and so is a value that is not a number (`spp_frame`). These zeros are not counted.
- In the annual zips, the monthly files (which repeat the daily rows) are not read, and an interval given in two daily files (same `GMTIntervalEnding` and BAA) is kept once, from the later file; the repeats are logged.
- HTTP 404 for a zip or a day is logged and skipped. Any other answer that is not HTTP 200 is tried up to four times (`iso_prices.with_retries`, the waits growing by 5 seconds), timeout 300 seconds, then stops the table. Daily files are asked 0.3 seconds apart.
- No file read, or no complete day, stops the table (`iso_prices.SourceGap`), and the other two tables of the run go on. The code counts no row ceiling, and `run_spp` does not consult `paused_sources.csv`.

## License

Public, with citation; not for a commercial publication without SPP's written authorization. `license_verdicts.csv` records SPP, read 6 (`https://www.spp.org/terms-conditions/`, 12 October 2026): "may be public"; for commercial use, "needs written permission". The sentence: "Permission is implicitly granted to copy and distribute (via computer network or printed form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication (printed or otherwise) or when the author(s) or SPP will be quoted in commercial materials, forums or publications." `sources.csv` flags `spp:ver_curtailments` public; `license_tables.csv` lists the table under SPP.

## Cross-checks (session 2088)

- The counts above were computed from the rows, read past the header lines. No (entity, variable, ts_utc) is given twice.
- Each `curtailed_<fuel>_mwh` equals the sum of its three parts to within 0.001 MWh, the rounding of the values to three decimals.
- spp:SPP misses one day of its range: 4 November 2018, the day the clocks went back. spp:SWPW misses 18 days of its range: 22 and 25 April; 14 and 20 May; 9, 12 and 23 June; 1 and 9 July; 18 August; 4, 9, 15, 18 and 23 September; 7, 10 and 21 October 2026. The code leaves a day out only when no file holds it or its intervals are not all there.
- Every solar variable of spp:SPP is 0 on every day before 27 October 2022, the first day with solar curtailment (redispatch); wind economic curtailment also begins on 27 October 2022, solar economic on 3 November 2022 and solar manual on 30 April 2024. Since the code writes 0 for a column a file lacks, a 0 before those days does not show that SPP published a 0.

## What it does not hold

- The five-minute values: they are summed by day when read and not kept.
- Wind and solar output: the file gives curtailment only (`docs/methods/curtailment.md` says how a share is built from EIA-930).
- A day of a BAA without every interval, and days before 1 March 2014.
- Other grids: CAISO's curtailment is `caiso_curtailment_daily`, ERCOT's output below its High Sustained Limit `ercot_wind_solar_hsl_daily`.
