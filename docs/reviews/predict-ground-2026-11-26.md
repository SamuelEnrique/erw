# The ERW forecast: the ground (chain 730, part C)

Session 10600, 26 November 2026, lab-desktop's second window. Read only: every figure below was computed from the warehouse's tables in `C:\Users\Shared\Documents\erw\warehouse\output` as they stood at about 11:00 UTC on 26 November 2026, by `runs/c730/ground.py` and `runs/c730/ground_prices.py` (not in git; they use `warehouse/predict/data.py`, which is). Nothing was fetched from any publisher.

## 1. What exists already, read and used (never built a second time)

- **Demand, every authority and region:** `eia930_ba_demand_hourly` (EIA-930 six-month files, public), the source of the demand pages. A region's demand is the sum of its demand-filing authorities, written for an hour only when each active one holds it: `warehouse/derived/region_files.py`, `region_demand`, which the forecast imports unchanged. (`eia930_region_hourly` holds no `demand_mw` for CAR, NW, SE and SW, because it sums every authority of the region, generation-only ones included; the demand pages' sum is the one used.)
- **The operator's own day-ahead forecast:** `eia930_forecast_error_hourly` (session 8012, `docs/methods/forecast_error.md`), which sets each authority's and region's EIA-930 "Demand Forecast (MW)" beside the demand and marks the hours it screens out as filing errors (`x_screened`: a forecast above three times the demand or below a third of it). The forecast uses `x_forecast_mw` of the unscreened hours as "the operator", for every place.
- **The page `/demand`** and its files `site/data/regions/demand/` and `site/data/regions/forecast/` (the operators' errors by hour, season and year): the ERW forecast is scored on the same demand and set beside the same operator forecast, so the two pages agree on every hour they share.
- **Weather:** `region_weather_hourly` (observations, population-weighted per region, 2018-07-01 to 2026-11-07 14:00 UTC, 19 days behind) and `weather_forecast_hourly` (NWS hourly forecasts at seven airports, one per ISO, from 2026-09-28).
- **Prices:** `ercot_all_hub_prices_history`, `iso_hub_prices_history`, `iso_hub_prices_history_2018`, `iso_dam_hub_prices` (day-ahead hub prices); `eia_fuel_spot_prices` (Henry Hub, daily); `caiso_wind_solar_forecast` and `ercot_wind_solar_forecast`.
- **Events:** the nine windows of `/events` (`site/data/regions/events/*.json`).

## 2. What can be forecast, place by place

The places: EIA's thirteen regions, and each balancing authority whose mean demand over the last 365 days held is at least 5,000 MW (sixteen; the threshold is this chain's reading of "large", written once here). Six authorities are each a whole region and appear twice under two names, as on `/demand`: ERCO is TEX, ISNE is NE, NYIS is NY, PJM is MIDA, SOCO is SE, TVA is TEN.

Every place's demand ends at 23:00 local time on 24 November 2026 (the last whole local day before the files' update of 25 November 15:42 UTC). Span and gaps over the last two years (2024-11-25 to 2026-11-25, 17,521 hours):

| Place | Clock | Demand held from | Missing hours, last 2 years | Operator's forecast held beside demand, last 2 years | Mean MW, last 365 days |
|---|---|---|---:|---:|---:|
| region-cal | Pacific | 2018-07-11 | 24 | 17,022 | 32,643 |
| region-car | Eastern | 2018-07-01 | 317 | 16,050 | 27,082 |
| region-cent | Central | 2018-07-01 | 2 | 15,039 | 35,643 |
| region-fla | Eastern | 2018-07-17 | 290 | 16,356 | 31,198 |
| region-mida | Eastern | 2018-07-01 | 5 | 17,445 | 99,169 |
| region-midw | Central | 2018-07-01 | 3 | 17,494 | 84,605 |
| region-ne | Eastern | 2018-07-01 | 3 | 17,518 | 13,375 |
| region-nw | Pacific | 2018-07-01 | 1,563 | 15,220 | 44,019 |
| region-ny | Eastern | 2018-07-01 | 3 | 17,395 | 17,218 |
| region-se | Central | 2018-07-02 | 2 | 17,517 | 28,295 |
| region-sw | Arizona | 2018-07-25 | 1 | 17,382 | 14,289 |
| region-ten | Central | 2018-07-01 | 2 | 17,519 | 19,891 |
| region-tex | Central | 2018-07-02 | 26 | 17,471 | 58,157 |
| ba-bpat | Pacific | 2018-07-01 | 0 | 17,521 | 7,278 |
| ba-ciso | Pacific | 2018-07-01 | 0 | 17,425 | 26,920 |
| ba-cple | Eastern | 2018-07-01 | 5 | 16,987 | 7,398 |
| ba-duk | Eastern | 2018-07-01 | 5 | 17,444 | 12,870 |
| ba-erco | Central | 2018-07-02 | 26 | 17,471 | 58,157 |
| ba-fpc | Eastern | 2018-07-01 | 5 | 17,421 | 6,788 |
| ba-fpl | Eastern | 2018-07-01 | 3 | 17,466 | 17,125 |
| ba-isne | Eastern | 2018-07-01 | 3 | 17,518 | 13,375 |
| ba-miso | Central | 2018-07-01 | 3 | 17,494 | 77,622 |
| ba-nyis | Eastern | 2018-07-01 | 3 | 17,395 | 17,218 |
| ba-pace | Mountain | 2018-07-01 | 1 | 17,424 | 6,138 |
| ba-pjm | Eastern | 2018-07-01 | 5 | 17,445 | 99,169 |
| ba-psco | Mountain | 2018-07-01 | 1 | 17,514 | 5,361 |
| ba-soco | Central | 2018-07-01 | 2 | 17,517 | 28,295 |
| ba-swpp | Central | 2018-07-01 | 2 | 16,968 | 35,620 |
| ba-tva | Central | 2018-07-01 | 2 | 17,519 | 19,891 |

The other 42 authorities that file demand are not forecast under this reading (mean demand below 5,000 MW, or no demand since 2026-04-01: WACM and WAUW were absorbed; BHBA and SWPW began on 2026-04-01). The full list with spans is `runs/c730/ground_places.csv` on the desktop. Every one of them could be added by the same code with one line.

**Prices, day-ahead, hub by hub:**

| Grid | Hub held | Span held | License (coverage) | Published (from the table's `vintage`) | On the page |
|---|---|---|---|---|---|
| ERCOT | HB_NORTH, HB_HOUSTON, HB_SOUTH, HB_WEST, HB_HUBAVG, HB_BUSAVG | 2015-01-01 to 2026-11-26 | public | about 11.4 hours before the delivery day begins (median; at least 9.6) | forecast (HB_NORTH, for TEX and ERCO) |
| SPP | SPPNORTH_HUB (SPPSOUTH_HUB from 2026-08-26 only) | 2018-07-01 to 2026-11-26 | public | not stated in the table | forecast (SPPNORTH_HUB, for CENT and SWPP) |
| CAISO | TH_SP15_GEN-APND, TH_NP15_GEN-APND (ZP26 from 2026-08-26 only) | 2023-07-06 to 2026-11-26 | public | not stated in the table | forecast (SP15, for CAL and CISO) |
| ISO-NE | .H.INTERNAL_HUB | 2024-09-01 to 2026-11-26 | public | about 11.1 hours before the day (median) | forecast (for NE and ISNE) |
| NYISO | N.Y.C. | 2024-09-01 to 2026-11-26 | public | the table's `vintage` is later than the day (a file revised after the market), so not readable from it | forecast (for NY and NYIS) |
| MISO | eight hubs | to 2026-10-04 | public, but paused (`paused_sources.csv`, MISO's terms) | about 10.9 hours before the day | not forecast: `paused` (no price since 4 October can be scored or used) |
| PJM | none held | | needs a paid license (`docs/licenses.md`, PJM's data license) | | not forecast: `license needed` |

Places with no hub of their own (CAR, FLA, NW, SE, SW, TEN and their authorities, and MIDW's MISO): price `not built` (no organised day-ahead market whose hub prices the warehouse holds), MIDW and MISO `paused`, MIDA and PJM `license needed`.

**Weather:** `weather_forecast_hourly` keeps only the latest forecast for each hour ("a newer run replaces the value for the same hour"), so for any past hour it holds the forecast issued shortly before it (median lead of the kept rows 22.7 hours, some under one hour), not the forecast that stood when a day-ahead forecast would have been made. It cannot be used in a backtest without using weather known early. `region_weather_hourly` is observations. **So no dated weather forecast is held, and the headline method uses no weather** (part D (c), the chain's own fallback). A data request asks window A to keep every vintage of the NWS forecast from now on, so that a dated archive grows.

**Calendar:** weekends; US federal holidays by their rules (pandas' `USFederalHolidayCalendar`, a rule, not a table); the day after Thanksgiving, 24 December and 26 to 31 December as "bridge" days; the clock changes are handled by working in each place's local hours (a 23 or 25 hour day keeps its own hours).

## 3. What was known when

| Input | When it is published | Read from |
|---|---|---|
| Demand (EIA-930 six-month files) | Daily: the files were last modified at 15:42 UTC on 25 November and held each authority's hours through 23:00 local on 24 November. The warehouse's copy is refreshed by the data machine's run, retrieved at 18:31 UTC that day | the table's header (`Last-Modified`, `Retrieved`) and its last hours |
| The operator's day-ahead forecast | Filed to EIA the day before; in EIA's files only with the day's own hours | the same files |
| Day-ahead hub prices | The day before the delivery day: ERCOT about 11.4 hours before the day begins, ISO-NE about 11.1, MISO about 10.9 (medians of `vintage`) | the tables' `vintage` |
| Henry Hub | EIA publishes daily spot prices weekly; the table's last day is 17 November, nine days before this read | the table's last row |
| Weather forecasts | Not held as dated vintages (above) | |

**The hours fixed from this:**

- **Demand:** the ERW forecast for a place's day T is made at **20:00 UTC on day T-1**, from demand through 23:00 local on day T-2 (the last whole day the warehouse holds after its EIA-930 refresh of about 18:30 UTC). This is a forecast made between 28 and 52 hours ahead of its hours, from data older than the operator's: the operator files by the morning of T-1 with its own demand of that morning. The comparison is made on these terms and says so.
- **Price:** made at **14:00 UTC on day T-1**, before the earliest day-ahead results of any grid forecast, from the day-ahead prices through day T-1 (published on T-2), demand through 23:00 local on day T-3, and Henry Hub as of ten days before.
- Every method, the simple ones included, is held to the same information: "the same hour yesterday" means the same hour of the latest whole day held when the forecast is made (day T-2 for demand, day T-1 for the price, whose day-ahead prices of T-1 are known on T-2).

## 4. The order of the build

1. Demand, the 29 places above (part D), every method on the same walk-forward backtest from 2019-07-01 (a year of history first) to 2026-11-24, so that the nine events from 2020 on are scored; the choice of method by the last two whole years.
2. Price, the five grids with public, current hub prices (ERCOT, SPP, CAISO, ISO-NE, NYISO; part E). CAISO's history begins in July 2023 and ISO-NE's and NYISO's in September 2024: their backtests are shorter, and each file says its span.
3. Not forecast, with the reason in every file: MISO's price (paused), PJM's price (license needed), the places with no hub of their own (not built), the 42 smaller authorities (below the threshold), weather-driven methods (no dated weather forecast held).
