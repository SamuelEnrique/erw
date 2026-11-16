# The shoulder hours, as a reader meets it (`/shoulder`)

Energy Research Warehouse (ERW). Written by session 7503 (chain 304, 16 November 2026) as the one note for the tool as a reader meets it: every view, every figure with its table and rule, every assumption with its default and source, what the tool does not hold, the replication, the cross-check and what waits for the owner. It points to the tables' own notes and does not repeat them:

- [`shoulder_hours_monthly`](shoulder_hours.md): the table, every rule of its builder, every variable. Where this note and that one differ on a rule, that note governs; on what the page shows and how, this note governs.
- [`eia930_caiso_break.md`](eia930_caiso_break.md): California's two sources and its late hours.
- [`impossible_hours.md`](impossible_hours.md): the hour of demand that is left blank.
- [`storage_buildout.md`](storage_buildout.md): the battery fleet (EIA-860M). [`curtailment.md`](curtailment.md): California's curtailment.

The figures quoted here are of the table as held on the machine that wrote this (built 4 October 2026, 27,201 rows, months to September 2026). The warehouse's copy is newer (27,489 rows, built 3 November 2026): the page on the site shows that one, and every figure below moves with it. `replication/shoulder/replicate.py` runs on whichever copy it is given.

## 1. The views

One page, `/shoulder`, in review (no visitor sees it). Two choices, both in the address, both links in the panel "Choose":

| Choice | Values | Default |
|---|---|---|
| `grid` | `ercot` (ERCOT), `caiso` (CAISO by EIA-930), `caiso-own` (CAISO, its own data) | `ercot` |
| `month` | any month the grid holds, `YYYY-MM` | the latest month that holds every figure of the summary and the headline numbers (section 5, "opening") |

That is 193 views on the copy read: 93 months of ERCOT (January 2019 to September 2026), 81 of CAISO by EIA-930 (January 2019 to November 2025, without February and September 2019), 16 of CAISO's own data (June 2025 to September 2026), and each grid with no month named. On that copy ERCOT opens on August 2026, CAISO by EIA-930 on November 2025 and CAISO's own data on August 2026; September 2026 is in the panel and lacks the fleet.

The page does no arithmetic. Every number it draws is one row of `shoulder_hours_monthly`, carried with its check key (`series|shoulder_hours_monthly|<entity>|<variable>|<date>`).

## 2. How a number is written

- A whole number is written with thousands separators and no decimals; any other number with two decimals (the table holds four).
- An hour of the day is written `HH:00`, the hour's start; an end hour is the first hour after the run, so a run to midnight ends at `24:00` and the summary adds "(midnight)" when `shoulder_runs_to_midnight` is 1.
- A figure the table does not hold is "not held", never zero and never an estimate.
- A value of the average day's chart is shown on hover, rounded to a whole MW.

## 3. Every figure, block by block

`m` is the month drawn, `y` its year. Each name is a variable of `shoulder_hours_monthly` for the grid's entity (`iso:ercot`, `iso:caiso`, `iso:caiso_own`); a monthly row is dated the month's first day, a yearly row the year's first day, a ranked day's row the day.

| Block | Figures (variable) |
|---|---|
| The summary sentence | the shoulder's length (`shoulder_hours`), from (`shoulder_start_hour`) to (`shoulder_end_hour`); the fleet's hours at full power (`fleet_hours`); the hours of the shoulder it covers (`shoulder_hours_covered`); the hours needed on the average day (`shoulder_hours_needed`); the same on the ten worst days of `y` (`year_worst10_mean_shoulder_hours_needed`), or the words that it is not given |
| Headline 1, "The evening shoulder" | `shoulder_hours`; its start and end; `shoulder_mwh_above_mean` |
| Headline 2, "Hours the battery fleet covers" | `shoulder_hours_covered`; `fleet_mw`, `fleet_mwh`; `shoulder_hours_needed` |
| Headline 3, "The midday surplus" | `midday_surplus_mwh`; `midday_surplus_hours`; `midday_low_hour`; California only: `curtailed_mwh_per_day` |
| Chart, "The average day" | for each local hour: demand, net load, solar and, where held, battery output (`avg_<series>_mw_hHH`), on hover; the shoulder shaded from its start to its end; net load's mean dashed (`net_load_mean_mw`, drawn, not written); the days the average is over (`days_held`). Wind is in the table and in net load, and is not drawn |
| Chart, "By month since" the grid's first month | for every month the grid holds: `shoulder_hours` and `shoulder_hours_covered`, on hover |
| Headline 4, "The shoulder, second measure" | `shoulder2_hours`; `shoulder2_start_hour`, `shoulder2_end_hour`; `shoulder2_mwh_above_midpoint` |
| Headline 5, "Hours needed, second measure" | `shoulder2_hours_needed`; `evening_peak_mw`, `evening_peak_hour` |
| Headline 6, "The ten worst days of `y`" | `year_worst10_mean_shoulder_hours_needed`; `year_mean_shoulder_hours_needed`; `year_days_ranked`; `year_worst10_mean_battery_hours` |
| Table, the ten days of `y` | for each ranked day: `worst_rank`, the day, `day_shoulder_mwh_above_mean`, `day_shoulder_hours`, `day_shoulder_start_hour`, `day_shoulder_hours_needed`, `day_shoulder2_hours`, `day_shoulder2_hours_needed`, `day_battery_discharge_mwh`, `day_battery_hours` |
| Table, "The shoulder hours by year" | for each year held: `year_months_held`, `year_mean_shoulder_hours`, `year_mean_shoulder_mwh_above_mean`, `year_mean_midday_surplus_mwh`, `year_end_fleet_mw`, `year_end_fleet_hours`, `year_mean_shoulder_hours_covered`, `year_mean_shoulder_hours_needed` |
| Table, "By year: the second measure and the ten worst days" | `year_mean_shoulder2_hours`, `year_mean_shoulder2_hours_needed`, `year_days_ranked`, `year_worst10_mean_shoulder_mwh_above_mean`, `year_worst10_mean_shoulder_hours_needed`, `year_worst10_mean_shoulder2_hours_needed`, `year_worst10_mean_battery_hours` |

The three opening views on the copy read:

| | ERCOT, August 2026 | CAISO by EIA-930, November 2025 | CAISO's own data, August 2026 |
|---|---|---|---|
| The evening shoulder | 5 hours, 19:00 to 24:00 | 8 hours, 16:00 to 24:00 | 6 hours, 18:00 to 24:00 |
| The fleet's hours at full power | 1.65 | 3.42 | 3.46 |
| Hours of the shoulder it covers | 1.65 | 3.42 | 3.46 |
| Hours needed, the average day | 3.66 | 2.38 | 4.06 |
| Hours needed, the ten worst days of the year | 6.58 | 4.53 | not given: six of the ten days are in months whose fleet EIA has not published |

## 4. The rules, in one place

The full statement is `shoulder_hours.md` ("The average day", "On the average day", "The second measure and the worst days", "Rules stated in full"). In short, on a day of 24 local hours:

1. Net load is demand less solar and wind. Its daily mean is the mean of the 24 values.
2. The midday surplus is the run of hours around net load's lowest hour in which net load is below the mean; its MWh are the mean less net load, summed over the run.
3. The evening shoulder starts at the first hour after solar's highest hour in which solar is below half of that highest value. It ends at the first hour, after net load has risen above the mean, in which net load is back at or below it, or at midnight. Its MWh count only the hours above the mean.
4. The evening peak is net load's highest hour from the shoulder's start to midnight. The second measure is the run around it above the midpoint between the mean and the peak.
5. The fleet's hours are its MWh over its MW. Hours covered: the smaller of the shoulder's length and the fleet's hours. Hours needed: the shoulder's MWh over the fleet's MW.
6. A month is measured on its average day (each hour's mean over the month's complete days). A ranked day is measured on its own hours. A year's figure is the mean over its months held, or over its ten ranked days.

## 5. The assumptions, each with its default and its source

These are the lines of the page's block "Decisions on this page" (`site/app/shoulder/Decisions.tsx`), by key. None is editable on the page: it computes nothing.

| Key | The choice | Default | Source |
|---|---|---|---|
| `level` | The shoulder is measured against net load's daily mean | the daily mean; the second measure uses the midpoint to the evening peak | session 75; the term is the page's |
| `start` | It starts when solar has fallen below half of its highest hour | half | session 75 |
| `end` | It ends when net load is back at the mean, and is cut at midnight when it never is | cut at midnight; in California every month, in Texas every month of 2026 and eleven of the twelve of 2025 | session 75 |
| `energy` | Its energy counts only the hours above the mean; its length counts every hour from its start | hours below the mean add nothing | session 75's builder, stated by session 7503 |
| `second` | The second measure: above the midpoint between the mean and the evening peak | the midpoint | session 80 |
| `average-day` | A month is its average day over its complete days; under 90 percent of days complete, the month is not shown | 90 percent; nothing filled | session 75; EIA Form EIA-930 |
| `net-load` | Net load is demand less solar and wind | SUN plus SNB, WND plus WNB; imports, hydro, gas and batteries not subtracted | EIA Form EIA-930 |
| `local-time` | Hours are the grid's clock hours, daylight saving included | Central, Pacific; a day of 23 or 25 hours is never ranked | sessions 75 and 80 |
| `fleet` | The fleet is the batteries operating that month in EIA's inventory | EIA-860M operating units; a grid operator's own count is larger (section 9) | `storage_buildout_monthly` |
| `covered-needed` | Hours covered and hours needed, as rule 5 | the batteries alone, at rated power, full at the start, no losses, no transmission limit | session 75 |
| `worst-days` | The ten days of each year with the most shoulder energy above the day's own mean | ten; among complete days of 24 hours with a shoulder | session 80 |
| `california` | California from two sources, never mixed | EIA-930 to November 2025; CAISO's own supply by fuel from June 2025 | session 80; `eia930_caiso_break.md` |
| `late-hours` | California's EIA-930 values of 1 November 2023 to 2 December 2025 are read one hour earlier | one hour, that period only | session 82 |
| `impossible-hours` | An impossible hour of demand is a blank and its day is not complete | rule A of `impossible_hours.md` | sessions 103 and 118 |
| `texas-batteries` | Texas's battery output is EIA-930's series as published | discharge only from 23 October 2024 to 15 December 2025, net of charging from then; not adjusted | EIA Form EIA-930, ERCO, Adjusted BAT Gen |
| `curtailment` | California's curtailment is CAISO's own count; Texas's is not held | curtailed solar plus wind over the days held | `caiso_curtailment_daily` |
| `opening` | With no month named, the latest month that holds every figure | the newest month usually lacks the fleet | session 90 |

## 6. The decisions on the page

The block is drawn under the folds, closed to start, one line a choice, each with a tip that holds its default and its source (no grey text). Its keys, in order: `level`, `start`, `end`, `energy`, `second`, `average-day`, `net-load`, `local-time`, `fleet`, `covered-needed`, `worst-days`, `california`, `late-hours`, `impossible-hours`, `texas-batteries`, `curtailment`, `opening`. `tests/test_session7503_shoulder.py` holds this list to the page's.

## 7. What the tool does not hold

- **No price.** The page says how long the evening stretch is and how much energy it holds, not what an hour of it is worth. It holds no count of hours at negative prices and no spread between midday and evening prices; the site's price pages (`/prices`, `/cost-of-power/battery`) are where prices are.
- **Texas's curtailment**, which ERCOT does not publish as CAISO does.
- **California by EIA-930 after November 2025**, and CAISO's own data before June 2025.
- **California's battery output before August 2025** in the EIA-930 view (CAISO's own, held from then), and Texas's before 23 October 2024.
- **A grid operator's count of its batteries** (section 9): the fleet is EIA's.
- **The transmission grid, capacity accreditation, and everything else that serves the evening** (gas, imports, hydro, demand response): `shoulder_hours.md`, "What it cannot see".
- **More than ten days a year**, and more than two grids.

## 8. The replication

`replication/shoulder/`, written from this note, `shoulder_hours.md` and the tables, not from the page's code:

- `replicate.py` sets every figure the page draws beside its own value, for every view. A figure with a rule on public tables is recomputed by the rule (rules 1 to 6 on the table's average day; the fleet from `storage_buildout_monthly`; the curtailment from `caiso_curtailment_daily`; the yearly rows; a ranked day's hours needed and battery hours). A figure whose only source is the hourly data is the table's row. The page's side is the page itself, drawn with the site's code on the same rows (`site/scripts/shoulder-figures.mjs`).
- On the copy read: **20,633 of 20,634 inside the tolerance** (half the page's last shown digit), over 193 views; 4,861 recomputed by the rules, 15,773 the table's rows. The one outside is named: ERCOT, September 2025, the shoulder's MWh, 61,089.58 on the page against 61,089.5749 recomputed, a rounding edge (the table's four decimals carried through a sum of hours).
- `from_hourly.py` recomputes the table's own rows from EIA's hourly workbooks (`ERCO.xlsx`, `CISO.xlsx`, the copies the table's header names): the average day hour by hour, the days held and every measure of each month, the days ranked and each ranked day's measures. **22,092 of 22,092 values equal the table's rows**, every month and year of ERCOT and of California by EIA-930 (`hourly_sample.json`). Not recomputed from hours: California by CAISO's own data (`caiso_fuel_supply`) and California's battery output (`caiso_battery_storage`); their figures stand on the table's rows.
- `page_figures.json` and `page_figures.csv`: the 1,196 figures of the three opening views, the page beside the replication.
- `replicate.do`: the five headline figures of ERCOT's opening month in Stata, expected values at its top; `python replicate.py --headline` prints the same lines. Stata is not on the machine that wrote it: the do-file has not been run.

## 9. The cross-check

Read on 16 November 2026, each host's robots file first: `caiso.com` disallows only `/resources/` and its terms (last updated 2 October 2018) allow use with its notices kept and CAISO credited; `eia.gov` allows `/todayinenergy/` and its publications are in the public domain; `potomaceconomics.com` disallows only `/wp-admin/` and states no terms. Each figure is quoted from the publisher's own document. No figure of ours was adjusted.

| Figure | Ours | Published | Publisher, document, date | Difference | Why |
|---|---|---|---|---|---|
| ERCOT, the fleet's MW, end of 2025 | 13,909 MW (the page, "By year", 2025) | "more than 17,000 MW" | Potomac Economics, *2025 State of the Market Report for the ERCOT Electricity Markets*, June 2026, page ii | at least 3,091 MW lower (18 percent) | Ours is EIA-860M's operating units as their owners report them, published a month or two behind; theirs is ERCOT's own count of installed storage resources. Not adjusted: a ruling (section 10) |
| ERCOT, the fleet's MWh, end of 2025 | 21,579 MWh | "31,500 MWh" | the same, page ii | 9,921 MWh lower (31 percent) | The same |
| ERCOT, the fleet's hours, end of 2025 and of 2024 | 1.55 and 1.43 | "1.83 hours, up from 1.67 hours in 2024" | the same, pages 13 and 21 | 0.28 and 0.24 hours lower | The same |
| ERCOT, the hour of the evening's highest net load, 2025 | by month: 17:00 twice, 18:00 twice, 19:00 three times, 20:00 five times | the net load peak is in "the later evening hours (7 to 9 p.m.)" | the same, page 5 | none in kind: eight of twelve months inside their two hours | Ours is each month's average day, so a winter month, whose sun sets earlier, peaks earlier |
| ERCOT, batteries' highest average hourly output, 2025 | 2,606 MW, at 19:00 (the twelve months' average days, weighted by their days) | "The maximum average hourly discharge across all ESRs in ERCOT increased by 191% to 2,390 MW in 2025" | the same, page 23 | 216 MW higher (9 percent) | Theirs is net injection from ERCOT's own data; ours is EIA-930's battery column, which in 2025 held discharge only, so charging in the same hour is not taken off |
| California, the fleet's MW, end of 2025 | 15,760 MW (the page, CAISO's own data, "By year", 2025) | "over 17 GW of installed battery capacity in the CAISO area" | CAISO Department of Market Monitoring, *2025 Annual Report on Market Issues and Performance*, June 2026, page 23 | at least 1,240 MW lower (7 percent) | As for ERCOT: EIA's inventory against the operator's count |
| California, the fleet's MW, end of 2023 and of 2024 | 8,107 and 11,746 MW (the page, "By year") | "from 8.0 GW in 2023 to 11.6 GW in 2024" | EIA, *Today in Energy*, "Solar and wind power curtailments are increasing in California", 28 May 2025 | 0.1 GW higher each | The same inventory, a later copy: EIA-860M adds units reported late |
| California, the fleet's MW, April 2026 | 15,979 MW | "net battery storage capacity increased 79% to 16 GW" | EIA, *Today in Energy*, "Solar generation in CAISO surpassed natural gas in the first five months of 2026", 16 June 2026 | none at their rounding | The same inventory |
| California, curtailment, 2024 | 3,423,377 MWh (the page's MWh a day times each month's days, twelve months) | "CAISO curtailed 3.4 million megawatthours (MWh) of utility-scale wind and solar output" | EIA, *Today in Energy*, 28 May 2025 | none at their rounding | Both are CAISO's own count |
| California, the hour of the evening's highest net load, 2025 | by month: 17:00 once, 18:00 three times, 19:00 three times, 20:00 four times | "the peak net load consistently occurred in hour-ending 20" (19:00 to 20:00) | CAISO Department of Market Monitoring, the same report, page 43 | none in kind | Theirs is the year's average hour over the whole Western market's footprint; ours is California, month by month |
| The shoulder's length, the hours covered, the hours needed, the midday surplus | section 3 | nothing published | none | none to state | "Shoulder" is this page's term and its measure is its own. No market monitor and no EIA document states the length of the evening stretch or the hours of storage it would take. EIA says only that batteries let "some renewable energy ... be stored and used 4-8 hours later in the day" (28 May 2025), a description, not a measure |
| Hours of negative prices; the spread between midday and evening prices | not on the page | California: negative prices in 7.1 percent of day-ahead hours in 2025, down from 8.8 (CAISO's market monitor, page 140). Texas: evening price spikes were 30 percent of all spikes in 2025 (ERCOT's market monitor, page 6) | the two reports above | nothing of ours to set beside them | The page holds no price (section 7). The published figures are given so that a reader knows where they are |

Not comparable, and why: CAISO's market monitor's 9,100 MW of average battery discharge at hour-ending 20 and its 25,700 MW of batteries are the whole Western market's footprint, not California's; its curtailment of 2025 (about 5,350 GWh) is the footprint's too, and the report's text gives no California total.

## 10. What waits for the owner

1. **Which fleet.** The page sets the shoulder against EIA-860M's operating batteries. ERCOT's market monitor counts more than 17,000 MW and 31,500 MWh at the end of 2025 where the page has 13,909 MW and 21,579 MWh. On the monitor's figures, December 2025's hours needed would be 1.99, not 2.43 (33,810 MWh over 17,000 MW, not over 13,909), and the fleet's hours 1.83, not 1.55. Default taken: EIA-860M stays (one source for both grids, monthly since 2015), and the page's block names the difference.
2. **The level.** `shoulder_hours.md` already asks: the shoulder ends at midnight in California every month and in Texas since 2025. Default taken: both measures stay, the first as the headline.
3. **The page's notes are grey text.** The headline numbers', the charts' and the sections' notes are drawn grey by the tools' shared frame (`site/components/tool/ToolPage.tsx`), against the page standard (hover tips only). Default taken: not changed here, since the frame is shared by every tool; the new block has no grey text.
4. **A and B.** The page shows one grid and one month at a time; a reader comparing Texas with California, or a month with the same month a year before, changes the address. Default taken: not built.

## Sign-off

What is signed for this tool: this note; `shoulder_hours.md`; `replication/shoulder/` (20,633 of 20,634, one rounding edge named; 22,092 of 22,092 from the hours); the cross-check of section 9; the 17 decisions of section 5.

Signed: ____________________  Date: ____________
