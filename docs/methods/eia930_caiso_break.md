# Method note: the break in EIA-930's California generation series (16 December 2025)

Energy Research Warehouse (ERW), sessions 73, 78 and 82. Status: **ruled and live from session 82** (4 October 2026). Session 73 found the break and changed nothing. Samuel ruled on it; session 78 built the join below; session 82 put it into the daily run and the live tables, and found and corrected a second fault in the same series, the late hours (below). Code: `warehouse/derived/caiso_join.py` (the join, the late hours, and their constants), `warehouse/analysis/caiso_join_before_after.py` (every affected figure both ways), `warehouse/analysis/caiso_hour_offset.py` (the evidence for the late hours), `warehouse/analysis/eia930_break.py` (session 73's daily sums from the saved EIA-930 workbooks); CAISO's own figures: `caiso_fuel_supply` (`warehouse/connectors/caiso_fuel_supply.py`, pulled daily from session 82).

## The join (the ruling)

From the hour starting **2025-12-16T08:00:00Z** (midnight Pacific; the constant `JOIN` in `warehouse/derived/caiso_join.py`, and nowhere else), California's generation, its generation mix and the generation side of its carbon figures come from CAISO's own supply by fuel. EIA-930 stays the source before that hour, and for interchange and demand on both sides.

**What changes in the tables: California's carbon intensity of generation** (`intensity_generation` of `eia930:CISO` in `carbon_intensity_hourly`, `_daily` and `_monthly`).

| | Before the join | From the join |
|---|---|---|
| CO2 generated | EIA's estimate | EIA's estimate |
| Net generation | EIA-930's | CAISO's own: every source of its supply but imports, batteries net |
| The row's `source` | `erw:carbon_intensity` | `erw:carbon_intensity_caiso` |

- **Why the CO2 stays EIA's.** CAISO's supply carries no emissions. And from the join EIA's California gas series is CAISO's own: EIA's gas CO2 over CAISO's gas MWh is 0.4049 tCO2/MWh over the 6,609 hours from the join to 2026-09-30, against EIA's own factor of 0.4051 (EIA's gas CO2 over EIA's gas generation, the 864 hours both tables held on 2026-10-03). What was wrong after the break is the denominator. The build repeats that check every run and stops if the ratio leaves the factor by more than 2 percent.
- **What was wrong with the denominator.** On the 888 hours both tables hold from the join (2026-08-26 to 2026-10-02), EIA's gas, geothermal, hydro, nuclear and coal equal CAISO's own to within 1 MW on average; EIA's solar is 944 MW lower (7,029 against 7,973), its wind 473 MW lower (2,719 against 3,192), and its total 1,740 MW lower (22,618 against 24,358).
- **What it does to the figure.** Over the 6,657 hours from the join that both hold, California's intensity of generation is 110.80 kgCO2/MWh on EIA's generation and 100.91 on CAISO's own. By month the change is 7 to 11 percent down.
- **Never mixed.** A period is written from one source or not at all. An hour from the join rests on CAISO's generation or is absent, never on EIA's. The UTC day 2025-12-16 and the month 2025-12 lie on both sides and are not written. A day needs its 24 hours and a month every day, so a day CAISO's supply does not hold completely costs that day and its month: CAISO's file was empty or short on 2026-08-21 and 2026-09-22, and the connector could not place the clock-change day 2026-03-08, so March, August and September 2026 have no monthly figure.
- **What does not change: the consumed intensity** (`intensity_demand`, CO2 consumed over demand). Its numerator is EIA's CO2 generated plus imported less exported, and its denominator EIA's demand; neither is a generation series, so it keeps EIA's rows on both sides. Its fall across the date (201 to 115 kgCO2/MWh in session 73's periods) is still partly the reporting change, and the pages say so.
- **In the daily run from session 82:** `caiso_fuel_supply` is pulled each day (the last three Pacific days, merged), `carbon_intensity.py` no longer writes California's `intensity_generation` from the join, and `caiso_join.py --apply` writes it. `cost_of_power.py` builds `cost_of_power_carbon`'s California figure the same way.
- **Not built yet: the mix pages.** `/mix`, `/grid` and the California grid page still read EIA-930's generation by fuel for California. Their sentence says that plainly. Switching them needs `caiso_fuel_supply` in the daily run and in the live set.

## What changed

EIA-930 is the hourly report each balancing authority sends the US Energy Information Administration. For the California ISO (`CISO`), from the hour starting 2025-12-16 08:00 UTC (midnight Pacific, the start of CAISO's operating day):

- **A geothermal series appears** (`GEO`), about 17.5 GWh a day. EIA's CISO data had none before.
- **Natural gas falls by more than the geothermal amount.** Daily means: 251.7 GWh before (2025-06-02 to 2025-12-15), 118.3 GWh after (2025-12-16 to 2026-09-29).
- **Total net generation falls**, and stays the sum of the fuels: 554.1 GWh a day before, 454.3 after.
- **Demand and interchange do not step** with it. So EIA's own balance for California (demand less net generation less net imports) was within about 1 percent of demand before (4.7 GWh a day) and is about 12 percent after (80.7 GWh a day). EIA defines a BA's demand as its metered net generation less its net interchange, so after the break California's reported figures no longer satisfy that identity.

## CAISO's own figures

CAISO publishes its supply by fuel source every five minutes (Today's Outlook). The ERW pulled it hourly from 2025-06-01 (`caiso_fuel_supply`, 151,320 rows) to set beside EIA's. Daily means, GWh (UTC days):

| | EIA, before | CAISO, before | EIA, after | CAISO, after |
|---|---|---|---|---|
| Natural gas | 251.7 | 178.3 | 118.3 | 119.1 |
| Geothermal | (none) | 17.8 | 17.4 | 17.6 |
| Large and small hydro | 56.6 | 56.7 | 59.1 | 59.4 |
| Nuclear | 49.0 | 49.1 | 53.5 | 53.8 |
| Solar | 149.4 | 172.2 | 150.6 | 172.7 |
| Wind | 51.7 | 56.7 | 60.5 | 76.6 |
| Generation, all sources (CAISO: imports excluded) | 554.1 | 534.2 | 454.3 | 501.3 |
| Net imports | 97.2 | 84.2 | 111.0 | 97.6 |

Read across the break: **after 2025-12-16, EIA's gas and geothermal equal CAISO's own to within 1 percent; before it, EIA's "natural gas" was about 73 GWh a day above CAISO's**, of which about 18 is the geothermal that was then not separated. Solar runs about 22 GWh a day below CAISO's own on both sides of the break: a standing difference, not this break.

## What the evidence supports, and no more

- **A reporting change on 2025-12-16, not a change in the grid.** The step is in one hour, in the fuel categories, with demand and interchange unmoved.
- **The same day, EIA's fuel categories changed elsewhere too.** ERCOT's "unknown energy storage" (`UES`) series ends on 2025-12-15. That suggests a change in EIA-930's categories, not one California made alone; EIA states none in the workbook's notes. EIA's known-issues page answered HTTP 403 to a plain request on 2026-10-03 and was not read.
- **From the break, EIA's California generation by fuel matches CAISO's own; its total no longer balances EIA's demand.** About 55 to 80 GWh a day that EIA's demand still counts is in no fuel. Before the break it was in EIA's "natural gas", above CAISO's own figure.
- **Not settled by these data:** what that generation is. It could be resources CAISO's own fuel mix does not show, or a definition of demand that changed less than generation did.

## Other grids

The same checks on the other six ISOs, October 2024 to September 2026: no break of this kind. Monthly balance residual as a share of demand:

- ERCOT, ISO-NE and NYISO: 0.
- MISO: a steady -1.7 to -2.9 percent throughout.
- SPP: within 1 percent.
- **PJM: -1 to -5.4 percent since May 2025**, varying month to month rather than one step. Smaller, and flagged here.

## Figures affected

See `archive/sessions/SESSION_73_REPORT.md`, "The audit", for the list of tables and pages and the size of each effect. In short:

- California's carbon intensity of generation (EIA's CO2 over EIA's generation) was 188 kg/MWh before the break against 139 on CAISO's own generation (EIA's own gas emission factor applied to CAISO's gas), and 110 against 101 after. EIA's figure ran about 49 kg/MWh high before and about 9 high after. A comparison across 2025-12-16 overstates the fall, and EIA's consumed intensity (201 to 115 kg/MWh) moves with it.
- The import share measured as demand less net generation reads about 12 points high from the break.

## The late hours: 1 November 2023 to 2 December 2025 (session 82)

Session 80 saw that California's average day from EIA-930 sat one hour later than CAISO's own. Session 82 found where and corrected it.

**What is wrong.** In EIA's CISO workbook, every hourly value from the row whose "UTC time" (the hour's end) is 2023-11-01T00:00 to the row whose UTC time is 2025-12-02T23:00 belongs to the hour before the one it is stamped with. Before and after, the stamps are right.

**The evidence** (`warehouse/analysis/caiso_hour_offset.py`; the workbook as EIA serves it and `caiso_fuel_supply`):

- **Against CAISO's own 5-minute data, day by day.** EIA's solar matches CAISO's best at a shift of one hour on each of the 182 days from 2025-06-02 to 2025-12-02 (correlation about 0.9997 by month at one hour, 0.93 to 0.95 at none), and at no shift on each of the 298 days from 2025-12-03 to 2026-10-02. Wind agrees. Before June 2025 CAISO's data is not held.
- **Against the sun.** The clock time of solar's centre of mass, day by day through the whole workbook, in Pacific standard time: about 11.9 when the stamps are right (2026: 11.65 to 12.07 by month). It steps one hour later between 30 October and 1 November 2023 (11.56, then 12.58), sits between 12.5 and 13.0 in every month from November 2023 to November 2025, and steps back on 3 December 2025. Texas's stays where it was throughout.
- **The afternoon of 31 October 2023** shows the start: the morning ramp is the day before's, the evening tail runs an hour past sunset.
- **It is in EIA's values, not in the ERW's reading.** The workbook's "Local time" and "UTC time" columns differ by Pacific time's own offset in every month (7 hours in summer, 8 in winter), on both sides of both dates. The same reading is right for Texas and for California after 2 December 2025.

**What is not known:** why. Both changes fall on a UTC day boundary of EIA's stamps, which suggests how the hours were labelled when they were submitted or loaded, not a change in the grid. EIA's workbook states none.

**Also seen, and not corrected:** from July 2018 to mid-June 2022 the same measure sits about half an hour early (11.0 to 11.45), with a step of about 0.7 hours on 15 June 2022. That is not a whole hour and there is no second source to check it against, so nothing is done about it.

**The correction** (`caiso_join.true_hours`, the bounds `LATE_FROM` and `LATE_TO`): a California hour in that period is read one hour earlier. The first late row would land on an hour that already holds its own value and is dropped; the hour 2025-12-02T22:00Z is then empty and is not filled. It is applied where California's EIA hours are set against a clock or a price:

| Reader | Table | What changes |
|---|---|---|
| `warehouse/derived/merchant_revenue.py` | `merchant_revenue_monthly` (the seller tab) | California solar and wind, September 2024 to December 2025: solar revenue 10.3 percent lower over those 16 months (USD 45,617 to 40,916 per MW); wind 0.5 percent lower. A solar shape an hour late sold into the evening ramp. After the correction June 2025's capture price is USD 15.96 per MWh, against 15.97 on CAISO's own solar |
| `warehouse/derived/cost_of_power.py` | `cost_of_power_monthly`, `cost_of_power_carbon` | California's load weights, November 2023 to December 2025 |
| `warehouse/derived/shoulder_hours.py` | `shoulder_hours_monthly`, `iso:caiso` | the average day and the ranked days of those months: the shoulder now starts at the hour CAISO's own data gives |

**Not corrected, and why:** `eia930_all_emissions` and the hourly carbon tables keep EIA's stamps for those months. They are EIA's rows as EIA dates them, and each intensity is a ratio within one EIA row, so its value does not change; only its hour is one late. Daily and monthly sums by Eastern or UTC day (`ba_supply_monthly`, `ai_power_regions`, `event_window_daily`) move by one hour at a day's edge and were left.

## The ruling

For California from 2025-12-16, CAISO's own supply by fuel source (`caiso_fuel_supply`) is the source for generation, generation mix and the generation side of the carbon figures, with EIA-930 kept for interchange. EIA-930 stays before the break, and the join is stated on every page that crosses it. Session 73 recommended this; Samuel ruled for it; "The join" above is how session 78 built it.
