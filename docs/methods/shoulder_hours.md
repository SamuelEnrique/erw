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

## The second measure and the worst days (session 80)

Session 75's shoulder runs to midnight in California and, since 2025, in Texas, and it describes only the average day. Two additions, both in the same table.

**A second measure, meant to end inside the evening** (`shoulder2_*`). The evening peak is net load's highest hour from the shoulder's start to midnight. The second shoulder is the run of hours around that peak in which net load is above the midpoint between its daily mean and the peak; its MWh are the sum, over those hours, of net load less the midpoint. `shoulder2_hours_covered` and `shoulder2_hours_needed` set the fleet against it as against the first. It starts no earlier than the first shoulder and holds no more energy than the evening holds above the mean. It is flagged (`shoulder2_runs_to_midnight`) when net load is still above the midpoint in the day's last hour.

**The worst days** (`worst_rank` and `day_*`, freq P1D; `year_worst10_*`, freq P1Y). Each complete day of 24 local hours is measured as the average day is, on its own hours and against its own mean. For each grid and local year the ten days with the most shoulder energy above the mean are ranked. For each:

- the shoulder by both measures;
- `day_shoulder_hours_needed`: its energy above the mean over the fleet's MW of that month. Where EIA has not yet published the month's fleet it is not written, and the year's mean of the ten is written only when all ten have it;
- what the batteries did, where every hour of the day holds their output: `day_battery_discharge_mwh` (their output in the shoulder's hours, discharging only), `day_battery_peak_mw`, and `day_battery_hours`, that discharge over the fleet's MW.

A day of 23 or 25 local hours is not ranked.

**California has two sources, as two entities, never mixed.** `iso:caiso` is EIA-930 through November 2025, as before. `iso:caiso_own` is CAISO's own supply by fuel (`caiso_fuel_supply`) from June 2025: solar and wind are CAISO's, battery output is its batteries source, and demand is the sum of its thirteen sources (imports and batteries net), the load the supply serves. The two overlap from June to November 2025 and differ there: CAISO's own solar is larger than EIA's (`docs/methods/eia930_caiso_break.md`), and the sum of CAISO's sources is not EIA's demand.

**A machine without the EIA workbooks** cannot rebuild an EIA grid. It keeps that grid's rows as they stand and adds only the second measure of its average days, computed from the average day the table already holds (it first checks that the first measure recomputed that way equals the held one). That grid's worst days are then not written.

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
- `year_end_<fleet_mw, fleet_mwh, fleet_hours>` at the year's last month held that has a fleet (EIA-860M is published a month or two behind).

## The month the page opens on

With no month named, `/shoulder` opens on the latest month that holds every figure its summary sentence and headline numbers state (session 90). The newest month held usually lacks the fleet, and with it the hours covered and needed, because EIA-860M is published a month or two behind; that month stays in the panel and the page says it is incomplete. A grid with no complete month opens on its newest.

## What it cannot see

- **The worst day.** The average day smooths away the cloudy week, the calm evening and the heat wave.
- **The transmission grid and local constraints.**
- **Capacity accreditation.**
- **Everything else that serves the shoulder:** gas, imports, hydro, demand response.
- **The choice of the mean as the level.** In CAISO, and in ERCOT since 2025, net load stays above its daily mean through midnight, so the shoulder as defined ends at midnight. A shoulder measured against a higher level (half the evening peak's rise, say) would be shorter. That is a definition for Samuel to rule on.
