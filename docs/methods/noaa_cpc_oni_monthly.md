# The Oceanic Nino Index and the Nino 3.4 sea surface temperature, a three-month season a row (NOAA's Climate Prediction Center)

Energy Research Warehouse (ERW), method note written in session 2094 (chain 068) for a table first written on 23 October 2026 (session 2092).

Tables: `noaa_cpc_oni_monthly`

## Publisher and address

NOAA National Weather Service, Climate Prediction Center (CPC), the Oceanic Nino Index (ONI), "Cold and Warm Episodes by Season" (`https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php`, `PAGE`), read from CPC's text file `https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt` (`URL`): a first line `SEAS YR TOTAL ANOM`, then one line a three-month season (DJF, JFM, and so on to NDJ) and year. One request, a pause of 1 second, timeout 60 seconds, with the ERW's user agent (`UA`). Source id `noaa:cpc_oni`. Connector: `warehouse/connectors/noaa_cpc_oni.py` (session 2092).

## Vintage and revision

The file on the data machine was written by run `20261023T213208Z` (23 October 2026), which reused the file session 2092's trial saved in `warehouse/raw/noaa_cpc_oni/` (its run log says so). `retrieved_at` is 2026-10-23T21:29:32Z and `vintage`, the file's Last-Modified, 2026-10-03T18:32:01Z, on all 1,840 rows.

CPC revises the ONI's recent seasons as its base period moves. Each run builds the table whole and replaces the file (`ip.write_snapshot`), and a run that is not offline asks for the file fresh, since it keeps its address as it grows; so CPC's revisions are taken. No age check is made.

## Shape and variables

Series, 1,840 rows: one entity, `cpc:oni_nino34`, two variables of 920 months each, January 1950 (DJF 1950) to August 2026 (JAS 2026). No month between them is missing.

- `oni_anomaly`: CPC's ANOM, the index itself, in `degC` (Decision 62 of `docs/datastandard.md`, added with this table). From -2.04 (NDJ 1973) to +2.59 (NDJ 2015); 234 seasons at or above +0.5, 238 at or below -0.5.
- `nino34_sst`: CPC's TOTAL, the season's mean sea surface temperature in the Nino 3.4 region, in `degC`; from 24.39 to 29.15.
- `ts_utc` the first day of the season's middle month (`SEASON_MID`): DJF is January, NDJ is December. CPC's YR is the middle month's year, so DJF 1950 is January 1950 and NDJ 1950 is December 1950. `x_season` CPC's three letters.
- `freq` P1M; `geo` and `market` empty; `node` "Nino 3.4".

Each row is a three-month running mean, so neighbouring months share two of their three months; a row is not one month's value. The newest seasons: AMJ 2026 +0.95, MJJ 2026 +1.39, JJA 2026 +1.80, JAS 2026 +2.16 (Nino 3.4 at 29.12 degC).

## Reading the source

- A file whose first line is not `SEAS YR TOTAL ANOM` stops the run (`parse`).
- A line not of the form season, year, total, anomaly (`LINE`) stops the run; blank lines are passed over.
- A season not one of CPC's twelve (`SEASON_MID`), or a season and year given twice, stops the run; so does a month given twice.
- Nothing is filled.
- The request is tried up to 4 times (`iso_prices.with_retries`), waiting 5 seconds times the attempt number after each failure; HTTP 404 is a `SourceGap`, not retried; any answer but HTTP 200 is a failure.
- Ceiling: one request a run. No row ceiling is set in the code.
- Any failure is recorded as a failure, and no file is written.
- The connector does not call `iso_prices.paused()`; NOAA is not in `warehouse/metadata/paused_sources.csv`.
- CPC's probabilistic ENSO outlook is not taken: it is published in the ENSO discussion, not as a data file.

## License

Public. `sources.csv` has `public` for `noaa:cpc_oni`; the header: "License: public (National Weather Service: "in the public domain, unless specifically noted otherwise"; cite "NOAA Climate Prediction Center")." `license_tables.csv` maps the table to the National Weather Service, as for `noaa_cpc_degree_days_daily`. `license_verdicts.csv`, NWS, read 8 (the National Weather Service's disclaimer, `https://www.weather.gov/disclaimer`): "The information on National Weather Service (NWS) Web pages are in the public domain, unless specifically noted otherwise, and may be used without charge for any lawful purpose so long as you do not: 1) claim it is your own [...], 2) use it in a manner that implies an endorsement or affiliation with NOAA/NWS, or 3) modify its content and then present it as official government material." Verdict: may be public, and may be public for commercial use.

Robots: the robots read of session 2092 found no robots file on `www.cpc.ncep.noaa.gov` (HTTP 404).

## Cross-checks (session 2094)

- The counts above were computed from the rows, read past the header lines; they equal the header's (1,840 rows, 1950-01 to 2026-08, the latest season JAS 2026 at +2.16). No (entity, variable, ts_utc) appears twice, and every season letter sits on its one middle month.
- Session 2092 set the DJF ONI against the winter (December to February) temperatures of `noaa_climdiv_state_monthly`, as departures from NCEI's 1901 to 2000 means, for the winters of 2001 to 2026. Recomputed here from the two tables, with the same result. In the three strong El Nino winters (DJF ONI at or above +1.0: 2010, 2016, 2024) the North (Minnesota, North Dakota, Montana) averaged +6.16 F, against -0.33 F in the two strong La Nina winters (DJF ONI at or below -1.0: 2008, 2011) and +3.02 F in the other 21. The DJF ONI's correlation with the North's winter departure is 0.37. The South (Texas, Florida, Louisiana) shows no such split: +0.62 F, +0.54 F and +1.75 F, correlation -0.06.

## What it does not hold

- CPC's ENSO outlook and its probabilities, and the ENSO alert status.
- Other Nino regions, the weekly or monthly Nino 3.4 values, and other indices (the Southern Oscillation Index among them).
- Seasons before DJF 1950.
- Temperatures and degree days on land: those are `noaa_climdiv_state_monthly` and `noaa_cpc_degree_days_daily`.
