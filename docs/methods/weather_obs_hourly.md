# NWS observed temperature and wind, hourly, at one airport per ISO

Energy Research Warehouse (ERW), method note written in session 2074 (chain 067) for a table first written on 28 September 2026 (session 24).

Tables: `weather_obs_hourly`

## Publisher and address

National Weather Service (NWS, NOAA), the station observations of its API, `https://api.weather.gov/stations/<station>/observations`, asked with `start` and `end` and followed page by page through the answer's `pagination.next` cursor (no key; the request names the ERW and its repository in its User-Agent). Documentation: `https://www.weather.gov/documentation/services-web-api`. Source id `nws:observations`. Connector: `warehouse/connectors/weather_nws.py` (session 24), which also writes `weather_forecast_hourly`; `warehouse/run_daily.sh` runs it every day (step `weather_nws`). Every answer is saved under `warehouse/raw/weather_nws/<run_id>/`.

| ISO (`node`) | Station (`entity`) | `geo` |
|---|---|---|
| ERCOT | nws:KDFW (Dallas/Fort Worth) | US-TX |
| CAISO | nws:KLAX (Los Angeles) | US-CA |
| NYISO | nws:KLGA (New York LaGuardia) | US-NY |
| ISO-NE | nws:KBOS (Boston) | US-MA |
| PJM | nws:KPHL (Philadelphia) | US-PA |
| MISO | nws:KIND (Indianapolis) | US-IN |
| SPP | nws:KOKC (Oklahoma City) | US-OK |

One airport per ISO's load center is a choice made in the connector.

## Vintage and revision

21 September 2026 09:00 to 23 October 2026 13:00 UTC in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github`; the last run in its header is `20261023T143704Z` (23 October 2026): "This run wrote 2208 rows: 205 new, 2003 replacing earlier rows with the same (entity, variable, ts_utc); 8419 rows are kept from earlier runs." The rows were retrieved from 28 September to 23 October 2026.

Each run asks for the last 30 days, up to the start of the current hour; the NWS serves about the last 7, so the table reaches back only as daily runs merge. The file is never deleted: each run's rows replace the rows of the same (entity, variable, ts_utc), so an hour is restated by every run that still sees it, and hours older than the API's reach stay as last written.

## Shape and variables

Series, 10,627 rows. `variable` `temperature_f` (`unit` degF, 5,332 rows) and `wind_speed_mph` (mph, 5,295 rows), converted from the API's degrees C and km/h and rounded to a tenth; `ts_utc` the start of the UTC hour, and the value the mean of the station's observations whose time falls in that hour; `freq` PT1H; `source_url` and `retrieved_at` those of the last API page read that held one of the hour's observations; `market` and `vintage` empty.

From 1,506 (KBOS) to 1,523 (KPHL) rows a station. Of the 773 hours in the span, each station lacks a temperature in 11 or 12: 7 October 15:00, 20 October 01:00 and the nine hours from 22 October 14:00 to 22:00 at all seven, and one more hour at KDFW (23 October 08:00) and at KLAX (23 October 03:00). An hour with a temperature and no wind occurs 37 times; the reverse never.

Temperature runs from 37.4 F (KBOS, 18 October 10:00) to 100.4 F (KLAX, 3 October 19:00), mean 66.8 F; wind from 0.0 to 29.9 mph, mean 9.3 mph.

## Reading the source

- An observation whose temperature or wind value is null is left out of that variable's mean; an hour with no value is not written.
- Observations outside the window asked are dropped after reading.
- A request answered with anything but HTTP 200 is retried and then fails that station; the other stations continue and the header names the inputs that failed. A station with no observations fails.

- Every non-null value the API returns is taken; its `qualityControl` flag is not read (`weather_nws.py` lines 66 to 68). The docstring and the header's words, which said "quality-controlled", were corrected by session 2074; the header takes the new words at the next run.

## License

`license_verdicts.csv` records the NWS, read 8: "may be public", for public and for commercial use. The sentence: "The information on National Weather Service (NWS) Web pages are in the public domain, unless specifically noted otherwise, and may be used without charge for any lawful purpose so long as you do not: 1) claim it is your own ..., 2) use it in a manner that implies an endorsement or affiliation with NOAA/NWS, or 3) modify its content and then present it as official government material." `license_tables.csv` lists the table under the NWS; `docs/licenses.md` gives "may be public", flag public, ERW verdict public. Attribution, as the NWS asks: "Weather data: National Weather Service".

## Cross-checks (session 2074)

- The counts above were computed from the rows, read past the header lines. No (entity, variable, ts_utc) is given twice; each entity has one `node` and one `geo`.
- Against NOAA's measured hours at the same seven airports (`noaa_station_weather_hourly`, `temperature_f`, through 18 October 2026 03:00): NOAA's hour is the report in the ten minutes up to it, which falls in the hour before here. Paired that way, 4,480 hours differ by 0.67 F on average, 78.6 percent within 1 F and 96.8 percent within 2 F (the largest 7.8 F); paired at the same `ts_utc`, 4,487 hours differ by 0.98 F on average.

## What it does not hold

- Hours before 21 September 2026, and any station but the seven.
- Dew point, humidity, pressure or precipitation.
- The NWS forecast (`weather_forecast_hourly`) and NOAA's station history (`noaa_station_weather_hourly`, `noaa_grid_weather_hourly`).
