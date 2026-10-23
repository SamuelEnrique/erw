# Session 2124 report: six held tables described

23 October 2026, from 23:00 UTC, on lab-desktop (the data machine), the fifth session of `queue/done/079-day-28-october-data-quakes-credits-rates-world-renewables.md`, unattended. Model spend USD 0. Pulls: none. (The notes were drafted by a helper agent beside sessions 2125 to 2128 and checked by this session at 23:18 UTC.)

## Read these first

- **The rule of session 2074** (public source tables of publishers other than EIA and the grid operators that no note describes) leaves one table: `noaa_isd_hourly`. The three grid weather tables beside it are described by `docs/methods/demand_weather.md` (the stations note says so) and lack only a `Tables:` line. So the session widened the rule to the grid operators' public source tables no note names, leaving out those chains 068 and 069 have described on their branches (ISO-NE's tables, the zone loads, SPP's curtailment, CAISO's grid emergencies, ERCOT's 4CP).
- **Six notes written,** each with its checks computed on the table and a section on where the description and the data disagree:
  - `docs/methods/noaa_isd_hourly.md` (412,435 rows, 11 stations, 2018-03-04 to 2025-08-27)
  - `docs/methods/caiso_fuel_supply_history.md` (782,808 rows, 2,509 days of 2018-06-01 to 2025-05-31)
  - `docs/methods/ercot_rtm_price_adders.md` (601,810 rows, 2014-06-01 to 2026-10-18)
  - `docs/methods/ercot_dam_esr_awards.md` (1,969,797 rows, 260 days, 339 resources)
  - `docs/methods/nyiso_as_prices.md` (293,376 rows, 764 days)
  - `docs/methods/spp_as_prices.md` (159,432 rows, 763 days)
- **The helper's claims were checked against the data by this session:** NOAA's 11 stations and the 2025 season's end at 2025-08-27T06:53Z (FAT, LAX, SAC); CAISO's clock-change days without a row (2019-11-03, 2020-03-08 and 2024-11-03 hold none, an ordinary day 312); ERCOT's adders missing 42, 42, 37 and 3 hours within their spans (124); the storage awards' header saying "246 zips" over 261 UTC dates. All hold.
- **Every disagreement acted on:**
  - **Descriptions corrected** (code unchanged): `noaa_isd.py`'s docstring now names the 11 stations, the report grain (each row a report at its own minute, not an hour), the 2025 season's end, the untrimmed windows (590 rows of the December 2021 baseline run to 31 December) and each grid's clock; `caiso_fuel_supply_history.py`'s comment says seven days have a 25th hour (it said eight) and its docstring says no clock-change day is written and that 2020-02-18 is absent from the hydro months; `ercot_rt_adders.py`'s docstring says RTRDPA's first hour begins at 01:00 CST on 5 December 2025 (the hour from midnight has no adder in either file).
  - **Recorded in the notes, not changed:** ERCOT's adder header counts only its own run's gap hours; the storage awards' header zip count is written by the full pull, not the daily append, and the clearing prices are blank where the award is (820,935 rows); NYISO's header says public where the license record holds it under the ruling of 21 October 2026 ("license needed"), and the record governs. SPP's note found none.
- **Internal checks that hold:** NOAA's dew point never above the temperature; ERCOT's hourly adder mean never above its maximum; one clearing price a service an hour in the storage awards; NYISO's reserve products and zones in their price order every hour; SPP's regulation up at least spinning at least supplemental every hour; CAISO's thirteen sources a median 1.66% above `caiso_area_load_hourly`.
- **The Method cells** of the six are filled in `docs/coverage.md`.

## Errors

- **This session's first correction to the CAISO docstring said three more days were missing in the hydro months;** two of the three are clock-change days already counted, and only 2020-02-18 is extra. Corrected before the commit.

## Decisions made without you

- **The rule widened to the grid operators' tables** when session 2074's left one table.
- **Descriptions corrected only where they say something the code or data do not;** run-time header counts left to their runs and recorded.

## For Samuel's ruling

- None new.

## Files

- New: the six notes, this report.
- Changed: `warehouse/connectors/noaa_isd.py`, `caiso_fuel_supply_history.py`, `ercot_rt_adders.py` (descriptions only), `docs/coverage.md` (the six Method cells). With them in the same commit, session 2129's rewrite of `epa_tri_energy_releases_annual` for its header (Decision 66): its older rows dropped from `coverage.csv`, `docs/coverage.md` and `archive_manifest.csv`.
- On the data machine only: `runs/c079/s2124/` (the helper's scripts).
