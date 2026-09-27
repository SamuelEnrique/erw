# Method: wind and solar curtailment by ISO

Energy Research Warehouse (ERW), session 18. Tables: `caiso_curtailment_daily`, `spp_curtailment_daily`, `ercot_wind_solar_hsl_daily` (series, daily, public) and `iso_curtailment_monthly` (derived, series, public). Code: `warehouse/connectors/curtailment.py`, `warehouse/derived/iso_curtailment_monthly.py`. The page that reads them: the site's `/curtailment` (platform tool 22, the curtailment tracker).

**The three ISOs' figures do not mean the same thing.** CAISO and SPP publish curtailment. ERCOT does not; the ERW's ERCOT figure is an estimate built from ERCOT's reported limits. MISO publishes nothing usable. Compare them with care, and never add them up as if they were one measure.

## What each ISO's figure means

| ISO | Table | What the number is | Whose number |
|---|---|---|---|
| CAISO | `caiso_curtailment_daily` | Wind and solar energy CAISO's market dispatch or operators cut, for local congestion or system-wide oversupply: economic bids dispatched down, self-schedules cut, and operator instructions | CAISO's |
| SPP | `spp_curtailment_daily` | Wind and solar energy curtailed by redispatch (congestion), by manual operator curtailment, and "curtailed for energy" (economic dispatch), per balancing authority area | SPP's |
| ERCOT | `ercot_wind_solar_hsl_daily` | Output below the High Sustained Limit (HSL): per hour, how far system-wide wind (or solar) output fell below the HSL the resources reported, summed over the day | the ERW's estimate, from ERCOT's figures |
| MISO | none | MISO publishes no curtailment series. Its market reports list hourly wind output ("Historical Hourly Wind Data") and nothing curtailed (checked 2026-09-27). Its market monitor reports curtailment yearly, in prose | none |
| NYISO, ISO-NE, PJM | none | Not checked in session 18 | none |

## CAISO

**Sources.**
- **Days before 2026-01-01:** "Production and curtailments data" (`https://www.caiso.com/library/production-curtailments-data`), one workbook per period. The Curtailments sheet lists every 5-minute interval with a curtailment, in MW, and since 2024 its reason, Local or System. The Production sheet gives 5-minute ISO solar and wind output in MW, among others. CAISO stopped publishing the workbooks as of June 2025. It then posted a one-time bulk file, named June to December 2025, that has no Production sheet and repeats the 2025 workbook's curtailment rows from 2025-01-01. The 2025 workbook's Production sheet covers the whole year.
- **Days from 2026-01-01:** the Daily Renewable Report (`https://www.caiso.com/library/daily-renewable-reports`), one HTML page per day. Its chart data are JavaScript arrays in the page: the day's hourly curtailment in MWh by fuel and by six categories (economic, self-schedule cut and operator instruction, each local or system), and 5-minute ISO solar and wind telemetry in MW.

**Computation.**
- A 5-minute MW value is 5/60 MWh. A day is the Pacific operating day, the date of the workbook's Date column or the report's chart date. It sits at 00:00:00Z of that date (Decision 11).
- **The workbooks overlap.** The "June to December 2025" file starts on 2025-01-01, so each interval is counted once, from the first workbook in name order that lists it. The session 18 run counted 25,848 curtailment intervals once that both files list.
- **A workbook day with no row for a fuel had none of it curtailed.** CAISO lists only the intervals with a curtailment, so every calendar day between a workbook's first and last curtailment is written, with 0 where nothing was listed.
- **Output** (`solar_generation_mwh`, `wind_generation_mwh`) is written only for a day with every 5-minute value: 288, or 276 or 300 on a daylight saving change day. The session 18 run dropped it for one day, 2019-12-09, which lacks some intervals. On a fall-back day the repeated hour's intervals carry the same local timestamps, and all 300 are counted. CAISO states that the curtailed energy is not counted in its production figures.
- **A report day** is written only from the report whose chart date is that day, and only if all six hourly category arrays for both fuels are complete.

**Variables:**
- `curtailed_solar_mwh` and `curtailed_wind_mwh`;
- `curtailed_<fuel>_local_mwh` and `curtailed_<fuel>_system_mwh`, where CAISO gives the reason (2024 on);
- `solar_generation_mwh` and `wind_generation_mwh`.

**Share of available output curtailed** (on the page): (curtailed solar + curtailed wind) / (curtailed + produced solar and wind). It is given only for a period with every one of the four figures.

## SPP

**Source.** VER Curtailments (`https://portal.spp.org/pages/ver-curtailments`), 5-minute MW by balancing authority area (BAA): wind and solar redispatch curtailments, manual curtailments, and curtailed for energy. The files are annual zips of daily files to 2024 (`.../ver-curtailments?path=/<year>/<year>.zip`), then daily files (`.../<year>/<month>/VER-Curtailments-<yyyymmdd>.csv`).

**Computation.**
- MWh = MW x 5/60.
- A day is the Central (America/Chicago) date of each interval's start, from the file's GMT interval ending minus 5 minutes.
- A BAA's day is written only with every 5-minute interval of it (288, 276 or 300).
- **Entities:** `spp:SPP` and, since SPP's western expansion, `spp:SWPW`. Older files have no BAA column and are SPP's.
- **Variables:** `curtailed_<fuel>_redispatch_mwh`, `curtailed_<fuel>_manual_mwh`, `curtailed_<fuel>_economic_mwh` (SPP's "curtailed for energy"), and their sum `curtailed_<fuel>_mwh`.

**No share.** The ERW holds no SPP wind and solar output for the same intervals and areas, so the page gives no share for SPP.

## ERCOT

**Source.** ERCOT reports NP4-732-CD (wind) and NP4-745-CD (solar), "Power Production, Hourly Averaged Actual and Forecasted Values", read from ERCOT's public MIS document list. Each report covers the 48 hours before it, and the list keeps about a week of reports. From each: system-wide actual output (`SYSTEM_WIDE_GEN`) and system-wide HSL (`SYSTEM_WIDE_HSL`), hourly.

**Computation.**
- Per operating day (Central) and fuel:
  - `<fuel>_generation_mwh` = the sum of hourly GEN;
  - `<fuel>_hsl_mwh` = the sum of hourly HSL;
  - `<fuel>_below_hsl_mwh` = the sum over hours of max(0, HSL - GEN).
- An hour below zero (output above the limit) adds nothing.
- A day is written only with GEN and HSL for every hour (24, or 23 or 25). The newest report wins for an hour in two reports.
- **Why this is not curtailment.** HSL is the output a resource reports it could sustain. Output falls below it when ERCOT dispatches the resource down (congestion, economics, instructions), but also through ramping, telemetry, and the hourly averaging of both figures. ERCOT publishes no curtailment figure. The page calls this "output below HSL" and never "curtailment".
- **Share** (on the page): below-HSL MWh / HSL MWh, wind and solar together.
- **History** starts when the ERW began reading the list, in September 2026. Earlier days would need ERCOT's public API, which requires registration.

## Monthly (`iso_curtailment_monthly`, derived)

- For each entity and variable of the three daily tables, a month's value is the exact decimal sum of its daily values.
- It is written only when every day of the calendar month is present. A month with a day missing is left out, and the log names it. The month in progress is never written; the page shows it from the daily rows.
- Share columns are computed on the page from the monthly sums, as above.

## Live set

- **Daily tables:** Supabase holds the last 100 days of each (`live_set.yaml`, `select`). The page shows the last 90.
- **Monthly table:** held whole.
- **Redivis:** holds every table whole. The CI runner restores the daily tables and the monthly table from the Redivis draft before a run, because each run adds only the latest days.
