# The operators' wind and solar forecasts beside the output that came

Energy Research Warehouse (ERW). Session 8013, chain 505, part D2. Builder: `warehouse/derived/renewable_forecast_error.py`, a step of the data machine's daily run. Page file: `site/data/regions/renewables_forecast.json` (contract: section 12 of `docs/state/page_files_regions.md`). Test: `tests/test_session8013_renewable_forecast.py`.

## What is compared

Two of the seven grids publish a day-ahead forecast of wind and solar output and the output itself under a license the record (`docs/licenses.md`) lets a page show, and the warehouse holds both:

- **CAISO**, `caiso_wind_solar_forecast`: OASIS report SLD_REN_FCST, the day-ahead forecast (market run DAM) beside the actual output (market run ACTUAL), hourly, by trading hub (NP15, SP15, ZP26), from June 2023.
- **ERCOT**, `ercot_wind_solar_forecast`: the short-term forecast as posted a day ahead of the hour (NP4-732-CD for wind, NP4-745-CD for solar) beside the system-wide output, hourly, from 30 September 2026 (ERCOT's public list keeps about a week; the table keeps what it has read since).

An hour is used when it holds both the forecast and the output. CAISO's whole grid is the three hubs summed, for an hour only when all three hold both; ZP26's wind begins on 8 February 2024, so the grid's wind begins then while each hub's own figures start where the hub's do. Nothing is filled.

## The measures

A miss is the forecast less the output: above zero, the forecast was high. Over any set of hours: the mean absolute miss (MW), the mean miss (MW), the absolute misses summed over the output summed (percent, which hours of near-zero output, solar at night, cannot swamp), the misses summed over the output summed (percent), and the mean forecast and output. They are given over every hour, by the local hour of day, by local month, for every whole local day (no hour missing), and over the windows of the nine events of `/events` (zero hours where the table does not reach an event).

## What it is not

No forecast of the ERW's own. The other grids are listed in the file with the reason each is not drawn: SPP's forecasts are not in the warehouse; NYISO's and ISO-NE's are not held and their data needs written permission; PJM's data is held for a license; MISO is paused.

## Limits

ERCOT's comparison covers weeks, not years, until the table grows. CAISO's day-ahead forecast and actual are CAISO's figures by hub, not by plant.
