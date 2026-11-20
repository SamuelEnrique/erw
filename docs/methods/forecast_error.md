# The day-ahead demand forecast beside the demand that came (`eia930_forecast_error_hourly`, `eia930_forecast_error_daily`, `site/data/regions/forecast/`)

Session 8012, chain 505 (part D1), 19 November 2026. Builder: `warehouse/derived/forecast_error.py`, a step of the data machine's daily run after the region files. Contract: section 11 of `docs/state/page_files_regions.md`. License: public (derived by the ERW from Form EIA-930, U.S. Energy Information Administration).

## The rule

Form EIA-930 asks every balancing authority for its day-ahead demand forecast for each hour. EIA prints it in the six-month BALANCE files as "Demand Forecast (MW)". The builder reads that column from every saved six-month file from July 2018 on (the newest copy of each, `warehouse/raw/eia930_region_hourly/`) and sets it beside the demand the warehouse holds for the same hour (`eia930_ba_demand_hourly`, the demand the region files and the demand pages use, screened as their method says). The forecast is the authority's own; the ERW fits no forecast and writes no estimate of its own.

- **The miss** is the forecast less the demand, in MW: above zero the forecast was high. In percent it is the miss over the demand.
- **Only hours with both above zero.** An hour whose forecast stands above three times the demand or below a third of it is taken as a filing error (as printed: the Southwestern Power Administration's forecast of 381,892 MW against a demand of 43 MW on 12 June 2023). The hourly table keeps it, marked `x_screened`; no figure counts it, and each page file says how many hours were screened.
- **A region** is the sum of its demand-filing authorities' forecasts beside the sum of their demand, written for an hour only when every authority needed that hour holds both (the region files' rule for a region's demand: an authority is needed from its activation to its retirement).
- **The measures.** MAPE: the mean over the hours of the absolute miss over the demand, percent. WAPE: the absolute misses summed over the demand summed, percent, which a few hours of very small demand cannot swamp (an authority whose demand is tens of megawatts can show a MAPE far above its WAPE). Bias: the mean miss, in MW and over the mean demand in percent. MAE: the mean absolute miss, MW.
- **Days** are local calendar days in the authority's or the region's time zone (the region files' zones), written only when every hour of the day is held and none is screened (23, 24 or 25 hours).

## The page files (`forecast/<region>.json`, `forecast/ba/<code>.json`)

Each holds the record's span, the measures over the whole record, by local hour of day, by season (December to February, March to May, June to August, September to November) and by year; every whole day's MAPE, bias, peak forecast, peak demand and peak miss; the ten hottest and ten coldest days by the region's population-weighted temperature (`region_weather_hourly`, the daily mean of a day with at least 20 of its hours; an authority's file uses its region's temperature); and the nine events of `/events`, each over its window in the file's own time zone.

## What it does not say

- Why a forecast missed. An authority's forecast is made a day ahead from its own weather forecast and its own model; a miss can be the weather forecast's, the model's or the demand's (an outage, a storm).
- Whether an authority filed its forecast late or revised it: EIA prints one forecast for each hour.
- The operators' wind and solar forecasts (part D2): see the method note of those tables when they are written.

## Build

`python warehouse/derived/forecast_error.py` (about two and a half minutes); `--site-dir` writes the page files elsewhere for a trial, `--no-tables` writes the page files only.
