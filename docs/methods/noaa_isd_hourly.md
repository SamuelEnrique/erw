# NOAA ISD station reports around the event windows and California's alert seasons: temperature and dew point at 11 airports

Energy Research Warehouse (ERW), method note written in session 2124 (chain 079) for a table first written on 1 October 2026 (session 49).

Tables: `noaa_isd_hourly`

## Publisher and address

NOAA National Centers for Environmental Information (NCEI), the Integrated Surface Database (ISD, dataset `global-hourly`), asked through NCEI's Access Data Service: `https://www.ncei.noaa.gov/access/services/data/v1?dataset=global-hourly&stations=<USAF+WBAN>&startDate=<UTC>&endDate=<UTC>&dataTypes=TMP,DEW&format=csv&includeStationName=true`, one request a station and contiguous date range. Product page: `https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database`. Source id `noaa:isd_global_hourly` (in `sources.csv`, license public, first and last seen 2026-10-01). Every response is saved under `warehouse/raw/noaa_isd/<run_id>/` with a `manifest.csv`.

Connector: `warehouse/connectors/noaa_isd.py` (session 49), three ways of running:

- `python warehouse/connectors/noaa_isd.py`: every event of its plan; the file is deleted and written whole. Ceiling 100,000 rows returned by NCEI, checked before each request against an estimate of 45 rows a station-day.
- `--event <name> --ceiling N` (session 58): one event's ranges, merged into the table held.
- `--seasons` (session 60): SAC, FAT and LAX, 1 May to 31 October of 2018 to 2025, one request a station and year, merged; ceiling 150,000 rows returned, estimated at 30 a station-day; a response an earlier run saved is read from disk, not asked again.

No schedule runs it: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh` or `.github/workflows/` names it. Readers named in `license_tables.csv`: `event_window_daily`, `flex_alert_effects`, `flex_alert_model`. Methods that use it: `docs/methods/event_study.md`, `docs/methods/flex_alert_scorecard.md`.

## Vintage and revision

The header records three runs and a restore:

| Run | Mode | Rows returned by NCEI | Rows written |
|---|---|---|---|
| `20261001T035443Z` | the event plan | 99,479 of 100,000 | 176,885, the file new |
| `20261001T230110Z` | `--event caiso_heat_2022` (SAC, LAX) | 1,752 of 10,000 | 3,375 new |
| `20261002T044621Z` | `--seasons` | 127,394 of 150,000 (24 requests) | 245,850: 232,175 new, 13,675 replacing |

The last header line: "Restored from the Redivis draft (energy_research_warehouse) by scripts/sync.py". `retrieved_at` takes two values: 2026-10-01T03:55:28Z on 166,585 rows and 2026-10-02T04:48:18Z on 245,850 rows. No row keeps session 58's retrieval: its 3,375 rows (SAC and LAX in late August and September of 2020 to 2022) lie inside the alert seasons and were replaced by the seasons pull (176,885 + 3,375 - 13,675 = 166,585). `vintage` is empty.

## Shape and variables

Series, 412,435 rows. `entity` `noaa:<airport code>`; `variable` `temperature_f` (206,280 rows) or `dew_point_f` (206,155 rows), `unit` degF, value ISD's tenths of a degree Celsius times 9/5 plus 32, rounded to 2 decimals (no value has more); `node` ISD's `REPORT_TYPE`: FM-15 (routine METAR) 314,132 rows, FM-12 (synoptic) 54,851, FM-16 (special) 43,270, SY-MT 182; `ba` the partition column, the grid the station stands for; `x_station_id` ISD's USAF and WBAN; `source_url` the request that returned the row. `freq`, `geo`, `market` and `vintage` are empty in every row.

| `entity` | `x_station_id` | NCEI's name | `ba` | Days asked in | `temperature_f` rows | `dew_point_f` rows | First `ts_utc` | Last `ts_utc` |
|---|---|---|---|---|---|---|---|---|
| noaa:BOS | 72509014739 | BOSTON, MA US | isne | America/New_York | 11,513 | 11,500 | 2018-03-04T05:54:00Z | 2022-12-30T04:54:00Z |
| noaa:DFW | 72259003927 | DAL FTW WSCMO AIRPORT, TX US | erco | America/Chicago | 17,855 | 17,856 | 2018-03-04T06:00:00Z | 2023-09-11T04:53:00Z |
| noaa:FAT | 72389093193 | FRESNO YOSEMITE INTERNATIONAL, CA US | ciso | America/Los_Angeles | 40,850 | 40,822 | 2018-05-01T07:53:00Z | 2025-08-27T06:53:00Z |
| noaa:IAH | 72243012960 | HOUSTON INTERCONTINENTAL AIRPORT, TX US | erco | America/Chicago | 2,916 | 2,915 | 2019-02-07T06:00:00Z | 2022-12-30T05:53:00Z |
| noaa:JFK | 74486094789 | JFK INTERNATIONAL AIRPORT, NY US | nyis | America/New_York | 11,182 | 11,179 | 2018-03-04T05:51:00Z | 2022-12-30T04:51:00Z |
| noaa:LAX | 72295023174 | LOS ANGELES INTERNATIONAL AIRPORT, CA US | ciso | America/Los_Angeles | 47,243 | 47,204 | 2018-05-01T07:50:00Z | 2025-08-27T06:53:00Z |
| noaa:MSP | 72658014922 | MINNEAPOLIS ST. PAUL INTERNATIONAL AIRPORT, MN US | miso | EST (UTC-5 all year) | 10,907 | 10,907 | 2018-03-04T05:53:00Z | 2022-12-30T04:53:00Z |
| noaa:OKC | 72353013967 | OKLAHOMA CITY WILL ROGERS WORLD AIRPORT, OK US | swpp | America/Chicago | 11,718 | 11,709 | 2018-03-04T06:00:00Z | 2022-12-30T05:52:00Z |
| noaa:ORD | 72530094846 | CHICAGO OHARE INTERNATIONAL AIRPORT, IL US | pjm | America/New_York | 1,190 | 1,190 | 2020-12-21T05:51:00Z | 2022-12-30T04:51:00Z |
| noaa:PHL | 72408013739 | PHILADELPHIA INTERNATIONAL AIRPORT, PA US | pjm | America/New_York | 11,161 | 11,152 | 2018-03-04T05:54:00Z | 2022-12-30T04:54:00Z |
| noaa:SAC | 72483023232 | SACRAMENTO EXECUTIVE AIRPORT, CA US | ciso | America/Los_Angeles | 39,745 | 39,721 | 2018-03-04T08:53:00Z | 2025-08-27T06:53:00Z |

The windows the 78 requests (distinct `source_url`) cover, as the connector's plan names them:

- `covid_2020`: 1 March to 31 May 2020 and the same days 364 and 728 days earlier (3 March to 2 June 2019, 4 March to 3 June 2018), at BOS, DFW, JFK, MSP, OKC, PHL and SAC. SAC's May rows were replaced by the seasons pull and carry its address.
- `uri_2021`: 7 to 24 February of 2021, 2020 and 2019, at DFW and IAH.
- `elliott_2022`: 19 to 29 December 2022, 20 to 30 December 2021, 21 to 31 December 2020, at BOS, DFW, IAH, JFK, MSP, OKC, ORD and PHL.
- `ercot_heat_2023`: 1 August to 10 September 2023, 2 August to 11 September 2022, 3 August to 12 September 2021, at DFW.
- `caiso_heat_2020` and `caiso_heat_2022` at SAC and LAX: every row of these windows lies in an alert season and carries the seasons pull's address.
- The alert seasons: 1 May to 31 October, 2018 to 2025, at SAC, FAT and LAX (2025 ends early: see the disagreements).

Left out for the ceiling, as header line 9 lists: IAH for `ercot_heat_2023` and `covid_2020`, LAX and ORD for `covid_2020`. The data agrees: no IAH row in August or September, every LAX row from the seasons pull, no ORD row before 2020-12-21.

## Placing values in time

- `ts_utc` is ISD's `DATE` as NCEI gives it, in UTC, to the minute: each row is one report, not an hour. Minutes of the hour: :53 on 253,132 rows, :00 on 55,395, :54 on 29,765, :51 on 21,565, :52 on 15,462.
- Where two report types share an instant, the FM-15 is kept and the other dropped (`noaa_isd.py`, the rank on `report_type`); a report repeated with the same type is dropped.
- A window is asked as local days: from local midnight of its first day to one second before local midnight after its last, through each station's time zone entry in `STATIONS`. That entry is the grid's clock, not the airport's: ORD (Central time) is asked in Eastern days for PJM, and MSP in `EST`, a fixed UTC-5 all year, MISO's market clock. So MSP's windows begin at 05:00 UTC in winter and summer alike.

## What is and is not filled

- Taken: ISD's `TMP` and `DEW`, the value before the comma and its quality code after it. A value whose absolute size is 9999 or more (9999 is ISD's missing) or whose quality code is 2, 3, 6 or 7 is not written; the other variable of the same report can still be.
- Nothing is filled or interpolated; no hour is made from reports. A report with neither value is no row.

## License

Header: "License: public domain (U.S. Government data, NOAA NCEI)." `license_verdicts.csv` records NOAA NCEI, read 9: "may be public", for public and for commercial use; the sentence read: "IMPORTANT NOTE: The non-U.S. data in ISD are subject to WMO Resolution 40 restrictions, and cannot be redistributed to other users or customers." The table holds U.S. stations only. `docs/licenses.md` lists `noaa_isd_hourly` under NOAA NCEI: "may be public", flag public, ERW verdict public.

## Checks (session 2124)

The figures in this note were computed from the rows of `warehouse/output/noaa_isd_hourly.csv`, read past its 17 header lines.

- 412,435 rows, `ts_utc` from 2018-03-04T05:51:00Z to 2025-08-27T06:53:00Z, as the header's last "File holds" line states. 11 entities, 2 variables.
- No (entity, variable, ts_utc) is given twice, nor (entity, variable, ts_utc, ba). Each entity has one `ba` and one `x_station_id`. Every value is a number; `unit` is degF throughout.
- Temperature: lowest -11.92 F (MSP, 2019-03-03T13:53:00Z), highest 114.08 F (SAC 2022-09-05T22:53:00Z and FAT 2022-09-07T00:53:00Z). Dew point: lowest -20.02 F (MSP, 2022-12-23T11:53:00Z), highest 78.08 F (DFW, 2021-09-05T18:53:00Z).
- Consistency: of the 206,132 instants that hold both variables, none has a dew point above its temperature.
- Silences: at nine stations the longest stretch without a report inside a window is about one hour (OKC 1.08 hours, LAX 1.05). SAC has one of 6.0 hours ending 2019-08-01T11:53:00Z, FAT one of 18.6 hours ending 2021-07-12T00:35:00Z.
- Rows from distinct UTC hours: SAC 37,968, LAX 33,744, FAT 33,713, DFW 11,679, MSP 7,435, BOS, JFK and PHL 7,432 each, OKC 7,431, IAH 2,106, ORD 811. LAX's 47,243 temperature reports fall in its 33,744 hours.
- Instants a calendar year at SAC, FAT and LAX (SAC's 2018 to 2020 include its March and April event rows): 2018 to 2024 between 4,489 (SAC 2022) and 7,001 (LAX 2024) per station; 2025: SAC 2,883, FAT 3,756, LAX 4,343.
- Every row's time lies inside its own request's `startDate` to `endDate`, except 590 rows described below.

## Where the description and the data disagree

1. **The 2025 alert season stops on 27 August.** Header line 15 says the seasons pull covers "May 1 to October 31 of 2018 to 2025 (local days)" and "Left out: nothing." The 2025 rows of SAC, FAT and LAX all end at 2025-08-27T06:53:00Z (requests asked to 2025-11-01T06:59:59). The connector does not check that a response reaches its end date. (`docs/methods/noaa_grid_weather_stations.md` records that NOAA's ISD database ends on 27 August 2025.)
2. **590 rows lie after their request's end.** The docstring and code ask each window as the event's local days. The Elliott baseline window of 20 to 30 December 2021 (asked to 2021-12-31T04:59:59 or 05:59:59 UTC) returned, at all nine of its stations, reports through 2021-12-31T23:51 to 23:54 UTC: 295 instants, 590 rows, the first at 2021-12-31T05:14:00Z (PHL). The connector does not trim rows to the window, so the table holds most of 31 December 2021 at these stations. No other window holds a row outside it.
3. **Eleven stations, not ten.** The module docstring lists ten airports ("a second for ERCOT, CAISO and PJM") and header line 3's "Stations:" names ten. The rows hold eleven: FAT (40,850 and 40,822 rows) is named only in header line 15 and in a code comment; CAISO has three stations.
4. **"Hourly" is not the shape.** The table's name, header line 1 and the docstring say hourly. The rows are every report NCEI returns (FM-15, FM-16 specials, FM-12 synoptic, SY-MT), at irregular minutes, more than one an hour at times; header line 2 says "Irregular observation times".
5. **The title names only the event windows.** Header line 1 says the table is "for the event windows of event_window_daily and their baseline days"; 245,850 of the 412,435 rows (59.6 percent) were written by the alert-season pull, which header line 15 describes.
6. **Local days are the grid's clock.** The docstring and header line 15 speak of local days; the code asks MSP in fixed EST and ORD in Eastern time (the grid's zone in `STATIONS`), which neither the docstring nor the header says.

Acted on in session 2124: the connector's docstring now names the 11 stations, the report grain, the 2025 season's end at NCEI's last report, the untrimmed windows and each grid's clock. The table's header is as its run wrote it.

## What it does not hold

- Any report outside the windows above, any station but the eleven, and anything after 27 August 2025.
- Wind, pressure, humidity or precipitation.
- Hourly grid weather built from NOAA (`noaa_station_weather_hourly`, `noaa_grid_weather_hourly`, `noaa_grid_weather_daily`) and the NWS observations (`weather_obs_hourly`).
