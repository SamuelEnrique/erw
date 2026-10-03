# Method: the shoulder hours

Energy Research Warehouse (ERW), session 75. Table: `shoulder_hours_monthly` (series, derived, public). Code: `warehouse/derived/shoulder_hours.py`. Page: `/shoulder`, "The shoulder hours" (in review). Tests: `tests/test_session75.py`.

**The question.** Solar floods the middle of the day and demand peaks in the evening. Does a 4-hour battery cover the stretch between them, or does the grid need longer storage? This table answers it as arithmetic, for ERCOT and CAISO, month by month, from data already held. "Shoulder" is this table's term, defined here, not an industry standard.

## Inputs

- **Hourly demand, solar, wind and battery output:** EIA-930, the per-balancing-authority workbooks the emissions connector saved (`warehouse/raw/eia930_emissions/<run>/<BA>.xlsx`, sheet "Published Hourly Data"). EIA's Adjusted columns are used: solar is SUN plus SNB (solar with integrated storage), wind is WND plus WNB. An hour is dated by its start (EIA's "UTC time" is the hour's end). No request is made.
- **California** stops after November 2025. EIA's generation series for California changed on 16 December 2025 (`docs/methods/eia930_caiso_break.md`). Its solar and wind did not break there, but this table does not mix a changed series in. CAISO's own supply by fuel (`caiso_fuel_supply`) begins in June 2025, too late to carry the history.
- **CAISO's battery output:** `caiso_battery_storage` (CAISO's own, 5-minute, from August 2025), the hour's mean. EIA reports no battery series for California.
- **CAISO's curtailment:** `caiso_curtailment_daily`, curtailed solar plus curtailed wind. ERCOT's is not held.
- **The fleet:** `storage_buildout_monthly`, `battery_operating_mw` and `battery_operating_mwh` of the grid and month (EIA-860M).

## The average day

For each local month from January 2019, for each local hour (0 to 23), the mean over the month's complete days of:

- demand;
- solar;
- wind;
- net load (demand less solar and wind);
- battery output (positive discharging), where held for every hour of every complete day.

A complete day holds every hour of demand, solar and wind. A month with fewer than 90 percent of its days complete is not written (CAISO, September 2019: 26 of 30). Never filled.

## On the average day

- **Midday surplus:** the run of hours around net load's lowest hour in which net load is below its daily mean (the mean of the 24 hourly values). Its MWh are the sum, over those hours, of the mean less net load.
- **Evening shoulder:** from the first hour after solar's highest hour in which solar is below half of that highest value, to the first hour, after net load has risen above its daily mean, in which net load is back at or below that mean.
  - If net load stays above the mean to midnight, the shoulder ends at midnight (`shoulder_runs_to_midnight` 1).
  - If net load does not rise above its mean after the start, the shoulder is 0 hours.
  - Its MWh (`shoulder_mwh_above_mean`) are the sum, over its hours, of net load less the mean.
- **The fleet against it:**
  - `fleet_hours` = MWh over MW, the fleet's average duration;
  - `shoulder_hours_covered` = the smaller of the shoulder's length and `fleet_hours`: the hours the fleet can run at its rated power through the shoulder;
  - `shoulder_hours_needed` = the shoulder's MWh over the fleet's MW: the hours a fleet of that power would have to run at rated power to deliver all of the shoulder's MWh above the mean.

## The table

`shoulder_hours_monthly`: entity `iso:ercot` or `iso:caiso`; `ts_utc` the first day of the local month at 00:00:00Z.

| Variable (P1M) | Unit | |
|---|---|---|
| `avg_<demand,solar,wind,net_load,battery>_mw_hHH` | MW | the average day, local hour HH |
| `net_load_mean_mw` | MW | net load's daily mean |
| `midday_low_hour`, `midday_surplus_hours`, `midday_surplus_mwh` | hour, hour, MWh | the midday surplus |
| `curtailed_mwh_per_day` | MWh | CAISO, the month's curtailment over its days |
| `shoulder_start_hour`, `shoulder_end_hour`, `shoulder_hours`, `shoulder_mwh_above_mean`, `shoulder_runs_to_midnight` | hour, hour, hour, MWh, count | the evening shoulder |
| `fleet_mw`, `fleet_mwh`, `fleet_hours`, `shoulder_hours_covered`, `shoulder_hours_needed` | MW, MWh, hour | the fleet |
| `days_held`, `days_in_month` | count | |

Yearly rows (P1Y, `ts_utc` the year's first day), so the page does no arithmetic:

- `year_months_held`;
- `year_mean_<shoulder_hours, shoulder_mwh_above_mean, shoulder_start_hour, shoulder_runs_to_midnight, midday_surplus_hours, midday_surplus_mwh, curtailed_mwh_per_day, shoulder_hours_covered, shoulder_hours_needed>`, each the mean over the year's months held;
- `year_end_<fleet_mw, fleet_mwh, fleet_hours>` at the year's last month held.

## What it cannot see

- **The worst day.** The average day smooths away the cloudy week, the calm evening and the heat wave.
- **The transmission grid and local constraints.**
- **Capacity accreditation.**
- **Everything else that serves the shoulder:** gas, imports, hydro, demand response.
- **The choice of the mean as the level.** In CAISO, and in ERCOT since 2025, net load stays above its daily mean through midnight, so the shoulder as defined ends at midnight. A shoulder measured against a higher level (half the evening peak's rise, say) would be shorter. That is a definition for Samuel to rule on.
