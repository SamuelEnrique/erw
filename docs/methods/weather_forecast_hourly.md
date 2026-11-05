# NWS hourly forecast of temperature and wind at one airport per ISO

Energy Research Warehouse (ERW), method note written in session 696 (chain 045) for a table first written on 28 September 2026.

Tables: `weather_forecast_hourly`

## Publisher and address

National Weather Service (NWS, NOAA), the hourly gridpoint forecast of its API, api.weather.gov (no key; the request
names the ERW and its repository in its User-Agent). For each station the connector asks
`https://api.weather.gov/stations/<station>` for its coordinates, then `https://api.weather.gov/points/<lat,lon>`, then
the `forecastHourly` address that answer gives, with `units=si`. Connector: `warehouse/connectors/weather_nws.py`
(session 24), run daily by `warehouse/run_daily.sh` (step `weather_nws`). Documentation:
`https://www.weather.gov/documentation/services-web-api`. Every answer is saved under
`warehouse/raw/weather_nws/<run_id>/` (not in git).

Stations, one airport per ISO load center (a choice made in the connector), and the forecast grid each one maps to:

| ISO (`node`) | Station (`entity`) | `geo` | Forecast address (`source_url`) |
|---|---|---|---|
| ERCOT | `nws:KDFW` | US-TX | `https://api.weather.gov/gridpoints/FWD/81,109/forecast/hourly?units=si` |
| CAISO | `nws:KLAX` | US-CA | `https://api.weather.gov/gridpoints/LOX/149,41/forecast/hourly?units=si` |
| NYISO | `nws:KLGA` | US-NY | `https://api.weather.gov/gridpoints/OKX/37,46/forecast/hourly?units=si` |
| ISO-NE | `nws:KBOS` | US-MA | `https://api.weather.gov/gridpoints/BOX/73,101/forecast/hourly?units=si` |
| PJM | `nws:KPHL` | US-PA | `https://api.weather.gov/gridpoints/PHI/48,75/forecast/hourly?units=si` |
| MISO | `nws:KIND` | US-IN | `https://api.weather.gov/gridpoints/IND/54,67/forecast/hourly?units=si` |
| SPP | `nws:KOKC` | US-OK | `https://api.weather.gov/gridpoints/OUN/94,90/forecast/hourly?units=si` |

## Vintage and revision

Each run reads the forecast as it stands (about 156 hours ahead) and merges it over the table, keyed on `entity`,
`variable` and `ts_utc`: a newer run replaces the value for the same hour. So an hour still ahead holds the latest
forecast, and an hour already past holds the last forecast read before the ERW stopped reading it. `vintage` is the
forecast's `updateTime` (else its `generatedAt`); `retrieved_at` is when the ERW read it. Earlier vintages of an hour are
not kept.

As of 23 October 2026: 158 vintages, from 2026-09-28T06:26:20Z to 2026-10-22T14:15:42Z. The last run
(`20261022T143359Z`) wrote 2,184 rows (336 new, 1,848 replacing) and kept 8,094. No row carries a vintage dated 2 October
or 16 to 18 October 2026. Of the 8,108 rows for hours up to 2026-10-22T14:00Z, 2,376 hold a forecast made more than 24
hours before the hour, and 350 more than 72 hours before (hours of 18 and 19 October; the longest 100.8 hours). 66 rows
carry a vintage later than the hour's start.

## Shape and variables

Series, `freq` `PT1H`. Key: `entity`, `variable`, `ts_utc`. `ts_utc` is the forecast hour's start (UTC). `market` is
empty; `source` is `nws:forecast_hourly` on every row.

| Variable | Unit | From the NWS field |
|---|---|---|
| `temperature_f` | `degF` | `temperature` in C (the run fails if NWS gives another unit), times 9/5 plus 32, rounded to 0.1 |
| `wind_speed_mph` | `mph` | `windSpeed` in km/h, the first (lower) number when NWS gives a range, divided by 1.609344, rounded to 0.1 |

As of 23 October 2026: 10,278 rows, 14 series (7 stations, 2 variables), 5,139 rows a variable, `ts_utc`
2026-09-28T09:00:00Z to 2026-10-29T01:00:00Z (737 hours). KLAX holds 737 hours, KBOS 722 (from 2026-09-29T00:00Z), the
other five 736 each (from 2026-09-28T10:00Z). No station misses an hour inside its span. 2,170 rows are for hours after
the last read (2026-10-22T14:34:21Z). Temperature runs from 33.8 to 102.2 degF; wind from 0.0 to 28.0 mph.

## License

The ERW verdict in `docs/licenses.md`: public. The row reads: publisher NWS; verdict today "may be public"; flag in
`coverage.csv` public; flag and verdict "agrees"; if the ERW sells anything "may be public"; ERW verdict "public". The
header says: public (US government work; attribution: "Weather data: National Weather Service").

## Cross-check

None in the code, beyond a guard: a station's forecast whose temperature unit is not C fails the run for that station.
Session 373 restored the table from the archive and recorded 9,480 rows before and 9,480 after (run
`20261020T063359Z-github`).

## What it does not hold

- No observations: the measured hourly values at the same stations are in `weather_obs_hourly`.
- No other forecast fields (dew point, humidity, precipitation, sky cover, wind direction or gusts).
- No earlier forecast of an hour: only the latest one read.
- One point per ISO, the gridpoint of one airport; not an average over the ISO's area.
- No hour before 2026-09-28T09:00Z.
