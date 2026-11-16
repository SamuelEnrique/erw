# Method: the shoulder hours

Tables: `shoulder_hours_monthly`

Energy Research Warehouse (ERW), session 75. Table: `shoulder_hours_monthly` (series, derived, public). Code: `warehouse/derived/shoulder_hours.py`. Page: `/shoulder`, "The shoulder hours" (in review). Tests: `tests/test_session75.py`.

**The question.** Solar floods the middle of the day and demand peaks in the evening. Does a 4-hour battery cover the stretch between them, or does the grid need longer storage? This table answers it as arithmetic, for ERCOT and CAISO, month by month, from data already held. "Shoulder" is this table's term, defined here, not an industry standard.

## Inputs

- **Hourly demand, solar, wind and battery output:** EIA-930, the per-balancing-authority workbooks the emissions connector saved (`warehouse/raw/eia930_emissions/<run>/<BA>.xlsx`, sheet "Published Hourly Data"). EIA's Adjusted columns are used: solar is SUN plus SNB (solar with integrated storage), wind is WND plus WNB. An hour is dated by its start (EIA's "UTC time" is the hour's end). No request is made.
- **California's late hours (session 82, stated here by session 7503).** In EIA's California workbook every value whose hour starts from 2023-10-31T23:00Z up to, not including, 2025-12-02T23:00Z belongs to the hour before the one it is stamped with (`docs/methods/eia930_caiso_break.md`, "The late hours"). Such a value is read one hour earlier; the first of them lands on an hour that holds its own value and is dropped, and the hour 2025-12-02T22:00Z is then empty and is not filled. Texas's stamps are right throughout.
- **An impossible hour of demand is a blank (session 103, stated here by session 7503):** rule A of `docs/methods/impossible_hours.md`, applied to demand over the hours read (stamps of 2018 and later). Its day is then not a complete day. Solar, wind and battery output are not screened.
- **Local time** is the grid's clock time, daylight saving included (America/Chicago, America/Los_Angeles). A day the clocks change has 23 or 25 hours: it counts as a complete day of the month's average when every one of its hours is held (the hour that comes twice enters its local hour twice), and it is never ranked among the worst days.
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
  - Its MWh (`shoulder_mwh_above_mean`) are the sum, over its hours, of net load less the mean, counting only the hours in which net load is above the mean: an early hour of the shoulder in which net load has not yet risen above its mean adds nothing and takes nothing away (session 7503 found the sentence without this clause; the table has always been built this way, and in a winter month the two readings differ: California, December 2022, 31,836 MWh against 30,183, about 5 percent).
  - The shoulder's length counts those early hours: it runs from the start, not from the hour net load rises above the mean.
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

A day of 23 or 25 local hours is not ranked. Nor is a day with no shoulder (0 hours: net load does not rise above the day's mean after the start). `year_days_ranked` counts the days that can be ranked: complete, 24 hours, with a shoulder of at least one hour. It is therefore fewer than the year's complete days (ERCOT 2019: 351 days ranked; 12 further complete days of 24 hours have a shoulder of 0 hours).

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

## The figures on the page and their keys

Each number `/shoulder` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `shoulder_hours_monthly`, `shoulder2_hours`, `shoulder2_start_hour`, `shoulder2_end_hour`, `shoulder2_mwh_above_midpoint`: the second measure on the selected month's average day, its length in hours, its first and last hour, and its MWh above the midpoint, in the first headline of "A shoulder that ends inside the evening, and the worst days".
- `shoulder_hours_monthly`, `evening_peak_mw`, `evening_peak_hour`: the evening peak of the same average day, MW, and its hour, beside the second measure's hours needed.
- `shoulder_hours_monthly`, `year_worst10_mean_shoulder_hours_needed`, `year_days_ranked`, `year_worst10_mean_battery_hours`: the mean hours needed on the ten worst days of the selected month's year, the complete days ranked that year, and the mean hours the batteries ran at rated power in those days' shoulders, in the third headline. The first also closes the page's sentence on the hours needed.
- `shoulder_hours_monthly`, `day_shoulder_mwh_above_mean`, `day_shoulder_hours`, `day_shoulder_start_hour`, `day_shoulder2_hours`, `day_shoulder2_hours_needed`: for each of the ten worst days (freq P1D), its shoulder energy above the day's own mean in MWh, the shoulder's length in hours and its first hour, and the second measure's length and hours needed, in the table of the ten days.
- `shoulder_hours_monthly`, `year_mean_shoulder2_hours`, `year_mean_shoulder2_hours_needed`, `year_worst10_mean_shoulder_mwh_above_mean`, `year_worst10_mean_shoulder2_hours_needed`: by year (freq P1Y), the second measure's length and hours needed, each the mean over the months held, and the ten worst days' mean energy above the mean and mean hours needed by the second measure, in the table "By year: the second measure and the ten worst days", beside `year_days_ranked`, `year_worst10_mean_shoulder_hours_needed` and `year_worst10_mean_battery_hours`.

## Checks against the table (session 2424)

Counted from `warehouse/output` by `runs/c115/s2424/check_tables.py`: `shoulder_hours_monthly` 27,197 rows, January 2019 to 6 October 2026, 192 variables. By entity and freq: `iso:ercot` 11,891 monthly, 1,192 daily, 210 yearly; `iso:caiso` (EIA-930) 10,011, 995 and 189; `iso:caiso_own` (CAISO's own supply by fuel) 2,345, 312 and 52, the two California entities kept apart as the section on California's two sources says. Units MW, MWh, count, hour and ratio; geo US-TX and US-CA; no key given twice, every value a number. The table section's "`iso:ercot` or `iso:caiso`" predates `iso:caiso_own`, which the later section names. The Tables line was added so that the finder of held tables with no note sees it.

## Two definitions to read the batteries by (session 7019, chain 301)

**California's two demands differ by the batteries' charging.** `iso:caiso_own`'s demand is the sum of CAISO's own sources, a charging battery counted as a negative source, so it leaves the fleet's charging out; EIA-930's demand (`iso:caiso`) counts it. On the average day of each month both entities hold, the gap between the two demands beside what the batteries took in (the part of `iso:caiso_own`'s `avg_battery_mw_hHH` below zero, summed over the day), MWh:

| Month | `iso:caiso` less `iso:caiso_own` | The batteries' charging |
|---|---|---|
| June 2025 | 40,282.0 | 40,957.4 |
| July 2025 | 39,531.1 | 41,819.8 |
| August 2025 | 42,465.6 | 42,432.8 |
| September 2025 | 42,241.5 | 41,596.0 |
| October 2025 | 40,950.7 | 44,433.5 |
| November 2025 | 31,939.1 | 35,627.9 |

No figure is wrong by the table's own rule: each entity is computed on its own definition of demand, and the two are not to be set side by side as one series. The register of source faults (`known_data_faults`) holds faults of a publisher's data only, so this difference of definitions is stated here and not there. A second set of variables, one entity on the other's definition, waits for the ruling named in done-line request 25 and for `wip/7503-shoulder`.

**ERCOT's battery column changed meaning on 15 December 2025.** EIA-930's ERCO battery figure (Adjusted BAT Gen) holds discharge only from 23 October 2024 to 14 December 2025, never below zero, and output net of charging from 15 December 2025 (`known_data_faults`, `eia930_erco_battery_column_changes_meaning`). `iso:ercot`'s `avg_battery_mw_hHH`, `day_battery_discharge_mwh`, `day_battery_peak_mw` and `day_battery_hours` are therefore discharge before that day and net output after it, and December 2025's average day mixes the two. They are written as EIA publishes them; whether the months before should become a second variable is the owner's to rule (done-line request 6).

## Rules stated in full (session 7503)

Session 7503 (chain 304, 16 November 2026) recomputed the table two ways without the builder's code: every derived figure from the table's own average day (`replication/shoulder/replicate.py`), and every month and year of the two EIA grids from EIA's hourly workbooks (`replication/shoulder/from_hourly.py`: 22,092 of 22,092 values equal the table's rows). The recomputation needed these rules, which the sections above did not state or stated loosely. They are the builder's, unchanged:

- **Hours.** An hour figure is a local hour of the day, 0 to 23, the hour's start; an end hour is the first hour after the run, so a run to midnight ends at 24 and a length is the end less the start.
- **Ties.** The lowest hour of net load, the highest hour of solar and the evening's highest hour of net load are each the earliest hour that holds the value.
- **The midday surplus** extends hour by hour, both ways from the lowest hour, while net load is below the mean, and stops at the day's edges.
- **The second measure** extends both ways from the evening peak while net load is above the midpoint, backward no further than the first shoulder's start and forward no further than the day's last hour. `shoulder2_level_mw` is the midpoint.
- **The fleet of `iso:caiso_own`** is California's (`iso:caiso` in `storage_buildout_monthly`): one fleet, two sources of hours.
- **`fleet_hours`** is written to four decimals, and the hours covered are the smaller of the shoulder's length and that written value.
- **`curtailed_mwh_per_day`** is the month's curtailed solar plus curtailed wind over the days of the month that `caiso_curtailment_daily` holds.
- **A yearly mean** is over the year's months that hold the figure, each month counted once whatever its length. `year_worst10_mean_shoulder_hours_needed`, `year_worst10_mean_shoulder2_hours_needed` and `year_worst10_mean_battery_hours` are written only when all ten days have the figure.
- **A ranked day's battery figures** are of the shoulder's hours only (`day_battery_discharge_mwh`: the hours in which output is above zero).
- **Texas's battery series changes meaning.** EIA-930's battery column for ERCOT begins on 23 October 2024 and holds discharge only (never below zero) until 15 December 2025; from that day it is net of charging. A month before December 2025 therefore shows no charging in its average day, and December 2025 holds both. California's battery output is CAISO's own and is net throughout.
- **Four decimals.** Every value is written to four decimals. A figure recomputed from the table's own average day can differ from the table's in the fourth decimal of a sum over 24 hours.

The copy of the table on the machine that ran this (built 4 October 2026) holds 27,201 rows: by entity and freq as the section above counts, but 316 daily rows for `iso:caiso_own`. The warehouse's copy is newer (`warehouse/metadata/coverage.csv`: 27,489 rows to 17 October 2026, built 3 November 2026).
