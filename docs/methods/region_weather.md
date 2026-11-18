# Weather for EIA's thirteen regions: the stations, their hours, and each region's weighted temperature

Energy Research Warehouse (ERW). Session 7803, chain 401 part C, tables 6 and 7. Internal tier: registered, validated, archived and in coverage; read by no page and not in the live set. Public data (NOAA NCEI, U.S. Census Bureau, EIA). Connector: `warehouse/connectors/noaa_region_weather.py`.

## Tables

| Table | What |
|---|---|
| `noaa_region_stations` | one row per county chosen: entity the county, `station_weight` its weight in its region, `node` its station (USAF-WBAN), with the station's name, distance, local standard time offset and the July 2025 agreement of its two products |
| `noaa_region_station_hourly_<year>` | `temperature_f` at every chosen station and UTC hour, one table a UTC year (2018 from July) |
| `region_weather_hourly` | each region (`eia930:<region>`) and UTC hour: `temperature_f`, the weighted mean of its stations |

## The rule

1. **Counties.** A region's counties are those whose primary region in `eia_county_region` is that region. They are taken in order of population (`census_county_population`, the estimate of 1 July 2025) until 80 percent of the region's population is covered, at most 25 counties.
2. **A county's point.** The county's center of population in the 2020 census (the Census Bureau's `CenPop2020_Mean_CO.txt`).
3. **A county's station.** The nearest station to that point among NOAA's stations in `isd-history.csv` with a WBAN number (the Local Climatological Data are keyed by it) whose ISD-Lite files hold at least 95 percent of the hours of each year: 2018 from 1 July, 2019 to 2024, and 2025 to the end of ISD-Lite on 31 July, and whose Local Climatological Data line up with it (an offset agreeing in at least 80 percent of July 2025, below), so that it has hours after the seam. When the nearest falls short the next nearest is tried, up to 150 km; a county with none within 150 km has no station and the region is weighted without it.
4. **Weights.** A county's weight is its population over the population of its region's chosen counties. A station chosen by several counties carries the sum of their weights.

## The hours

- **ISD-Lite to 31 July 2025** (NOAA's Integrated Surface Database ended on 27 August 2025): one file per station and year, the hour's observation by ISD-Lite's own rule (from ten minutes before the hour up to the hour, the closest to it).
- **Local Climatological Data v2 from 1 August 2025**, through NCEI's Access Data Service: every report, dated in local standard time, put on ISD-Lite's hour rule (the readers of `noaa_grid_weather.py`).
- **A station's local standard time offset** is read from the data, since the stations carry no time zone here: over July 2025, held by both products, the offset among 5, 6, 7 and 8 hours behind UTC under which the two agree to a tenth of a degree Celsius in the most hours. The offset and that share are in `noaa_region_stations`. Under 80 percent agreement the station is passed over in the choice (session 7803: nine stations were, among them Raleigh-Durham's first candidate, before this rule left their regions without hours from August 2025).
- **Gaps.** A run of at most three missing hours between two measured hours is interpolated on a straight line (`noaa_grid_weather.py`'s rule). Nothing longer is filled.
- **Files already saved** by `noaa_grid_weather.py` are read from the raw files, not asked again.

## A region's hour

The weighted mean of the region's stations, written only for an hour every one of them holds after the gap rule (`x_stations`: how many). The run log counts each region's hours left out. Temperatures are in degrees Fahrenheit (`degF`), two decimals.

## Build

    python warehouse/connectors/noaa_region_weather.py --fetch-only     # the pulls, no lock
    python warehouse/lock.py run --task <task> -- <python> warehouse/connectors/noaa_region_weather.py

Not in the daily run.
