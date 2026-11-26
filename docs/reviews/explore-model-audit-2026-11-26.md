# The signature explorers: audited as a hostile expert would

Session 10231, 26 November 2026, chain 710 (part D), the old laptop. Platform tool 5 (`docs/platform-tools.md`): `/explore/ercot-peak-premium`, `/explore/demand-growth`, `/explore/interconnection`, and `/explorer/ercot-peak-premium`, which redirects to the ERCOT tab of `/prices` (`site/next.config.ts`). Read as an economist checking the peak premium's definition and as a planner using the three explorers, both wanting to find them wrong. In the form of `docs/reviews/queues-model-audit-2026-11-26.md` and `demand-model-audit-2026-11-26.md`.

- Nothing changed on main but this file, its folder of evidence (`docs/reviews/explore-model-audit-2026-11-26/`) and the session report. No table written, no lock taken, no default moved, no model called, no live service asked, no web read.
- Not repeated: the faults and reads of 16 November (`ercot-peak-premium-faults-2026-11-16.md`, `-read-`, `demand-growth-faults-`, `-read-`, `interconnection-faults-`, `-read-`), the ruling files of 17 November (`ruling-impact-*`, `ruling-alternatives-*`: a mean or the traded block beside the medians, CAISO's 2023 as the opening year, ERCOT's "agreement signed", the share by MW, California's charging, a growth for the newest year's months), and tonight's consumption and queue audits, whose findings on the same tables are cited where an explorer carries them.
- Each finding has its own branch, `wip/audit-explore-<n>`. Branches 1, 3, 4, 5, 6, 7 and 8 change words only and are for landing; branch 2 is a test for the owner's ruling. No data request blocks a finding; one is returned.

## In short

- **The arithmetic is right in all three.** The peak premium: every annual and monthly row of HB_HUBAVG for 2015 to 2025 restated from ERCOT's 15-minute prices with the standard library alone (no numpy, no time zone library), 308 of 308 and 3,696 of 3,696 equal at six decimals; the default view's 64 figures, as the page's own code draws them, 64 of 64 as written. The ERCOT tab of `/prices`: 30 of 30. Demand growth: 94 of 94 figures and hovers of the default view. Interconnection: 201 of 212 figures of the default view from the queue tables held here; the other 11 are rows whose input the table read from a later pull (19 October, here 26 September), not a fault found.
- **The two addresses agree.** `/explorer/ercot-peak-premium` (the ERCOT tab of `/prices`) and `/explore/ercot-peak-premium` read the same rows and write them by the same rule: the 29 figures they share are the same text, and the tab's one more (the all-interval IQR, 17.07) restates equal. The tab carries no decisions block, so no sentence of this audit's fixes reaches it.
- **The dollars are each year's own, and the page never says so (finding 1).** The default view sets 2015 beside 2025 across a 32.5 percent rise in the GDP price index; 2015's peak-block IQR of 7.64 USD/MWh is 10.12 in 2025 dollars, so the IQR grew 3.37 times, not 4.47. Words for landing; constant dollars are the owner's (2015's thesis figures move by a third).
- **"How much higher" is a difference of two medians, not the typical day's gap (finding 2).** Each day's peak mean less its midday mean: the median day is 18.59 USD/MWh in 2025 (the page: 14.52) and -0.44 in 2015 (-0.16); the evening ran above midday on 95.3 percent of 2025's days and 44.7 percent of 2015's. The page says this of two hubs, not of two blocks. Words for landing.
- **The thesis survives every rule changed one at a time; its size does not.** From near zero in 2015 to well above it in 2025 under every block, averaging, market, day set and weighting tried: the premium of 2025 is 9.59 (peak 15:00 to 20:00) to 22.38 (19:00 to 21:00, the market monitor's tightest hours now), 18.37 day-ahead, 15.42 on weekdays without holidays, 14.51 without the clock-change days, 14.27 weighted by load. 88 percent of the rise is the evening's median rising (+12.91), not midday's falling (-1.77). In 2015 the day-ahead market already priced a premium of 2.22 where real time shows -0.16.
- **The demand growth explorer carries two sentences tonight's consumption audit found false on `/demand`, which its branches leave on the explorer (findings 4, 5).** "Nothing is filled" (EIA's adjusted demand holds EIA's estimates: 351 hours, MISO's highest hour of 2025 among them, which the explorer prints) and 2019 as "the first whole year the warehouse holds" (EIA's workbooks hold 2018 whole; the builder reads it). Words for landing.
- **Smaller, all words.** The storm's 645 intervals at or above 1,000 USD/MWh read as February's; they are 2021's, 608 of them February's, and the year's 99.9th percentile is 1,058.53 without February, not 9,000.85 (finding 3). Every interconnection figure's hover says "as the ERW last pulled it" while the table is older than the last pull (finding 6, open since 16 November). The shared note says every explorer is stale after three days; two use 35 and 8 (finding 7).
- **No held grid reaches a figure:** the peak premium is ERCOT's (public); demand growth reads ISO-NE, MISO and NYISO only through EIA-930 (public domain); the interconnection explorer reads only CAISO's, ERCOT's and SPP's rows (the drawing's reads: `like.caiso:queue_*` and `in.(caiso:queue_2023,ercot:queue_2023,spp:queue_2023)`), and its download of the table is refused while the table is held by grid.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/explore/ercot-peak-premium/page.tsx`, `Decisions.tsx` | The peak premium explorer: filters in the address (hub, period, two years, a second hub), three headline numbers, the thesis chart (box a block and a year), the five numbers of each block, the thesis's figures, the two-hub section, two line charts, the eleven decisions with default and source on hover. Computes nothing |
| `site/lib/explore/peakpremium.ts` | The blocks' names and hours, the figures drawn, a year's and a month's full count of intervals, the period label, the header's last input interval |
| `site/app/explorer/ercot-peak-premium/view.tsx`, `Explorer.tsx` | The ERCOT tab of `/prices` (where `/explorer/ercot-peak-premium` redirects): one hub and one year, chosen in the browser; ten headline figures, the box chart and its rows, the peak-block IQR and the median by year, the monthly medians of the three blocks |
| `warehouse/derived/ercot_peak_premium.py`, `docs/methods/ercot_peak_premium.md` | The builder and its note: blocks by the local hour an interval starts (overnight 21:00 to 12:00, midday 12:00 to 16:00, peak 16:00 to 21:00), numpy's linear percentile, no cap, a past period whole or nothing written, the year to date |
| `site/app/explore/demand-growth/page.tsx`, `Decisions.tsx`, `site/lib/explore/demandgrowth.ts` | The demand growth explorer: a grid and a window (the whole year's average or highest hour, the year so far, a month, an hour of the day); growth since 2019 by grid; the grid's years; sixteen decisions. Reads `eia930_demand_growth` (`warehouse/derived/demand_growth.py`, `docs/methods/demand_growth.md`) |
| `site/app/explore/interconnection/page.tsx`, `Decisions.tsx`, `site/lib/explore/interconnection.ts` | The interconnection explorer: a queue (six; three held), positions or MW, two entry years; entered, operating and withdrawn share headlines, the stacked chart, the share and wait lines, the table of years, the six queues side by side; twelve decisions. Reads `iso_queue_statistics` (`warehouse/derived/queue_statistics.py`, `docs/methods/energy_projects.md`, `docs/methods/interconnection_explorer.md`) |
| `site/lib/explore/source.ts`, `index.ts`, `site/components/explore/Explore.tsx` | Shared: every figure's hover words from its key, the address helpers, the frame and the freshness line |
| `docs/methods/explorers.md` | The note the three share |
| `site/scripts/peak-premium-figures.mjs`, `demand-growth-figures.mjs`, `interconnection-figures.mjs` | Each page drawn to HTML with its own code, every read of the live set answered from a table file; used here for the default views |
| Read from the main copy, never written | `ercot_all_hub_prices_history`, `iso_rtm_hub_prices`, `iso_dam_hub_prices` (HB_HUBAVG's 15-minute real-time and hourly day-ahead prices: 519,576 rows kept, `extract.out`); `ercot_peak_premium_annual` and `_monthly` (built 29 September 2026); `eia930_demand_growth`; `iso_queue_statistics` (built 21 October 2026); the CAISO, ERCOT and SPP queue tables (pulled 26 September 2026); `ercot_zone_load_hourly` (ERCOT's system load); `site/data/forecast/deflator.json` (in git) |

## How every number here was computed

- **The pages:** drawn with their own code, no build, no server: `peak-premium-figures.mjs --opening` (128 views, `peak_default_view.html`), `demand-growth-figures.mjs --opening --grids=ercot,miso` (81 views), `interconnection-figures.mjs` (284 views; NYISO, MISO and ISO-NE held and not read); the ERCOT tab's client component in its first state by `draw_explorer.mjs` (`ercot_tab_first_state.html`).
- **The restatements**, each written from the method notes with the standard library alone: `restate_peak.py` (Central time placed by the United States' rule since 2007, a linear percentile at (n - 1) p / 100), `restate_dg.py` (growth from the table's levels; the levels themselves were restated from EIA-930's hours by tonight's consumption audit, 24,204 values equal), `restate_ic.py` (status by each ISO's own word, entry year from the queue date, the wait in days over 365.25), `compare_tabs.py`.
- **One rule at a time:** `measures_peak.py` (blocks, averaging, day-ahead, days, dollars, the traded block), `measures_load.py` (weighted by ERCOT's system load), `checks_peak.py` (the decisions' quoted figures).
- Copies of every script and printout in `docs/reviews/explore-model-audit-2026-11-26/` (written to run from `runs/c10231/` of a worktree).

## The default views re-done, to the digit

### ERCOT peak premium (HB_HUBAVG, the whole year, 2015 against 2025)

| Figure | Page | Restated |
|---|---|---|
| Peak-block IQR | 34.12 (2015: 7.64) | the same |
| Peak median minus midday median | 14.52 (2015: -0.16) | the same |
| Median, all intervals | 25.68 (2015: 20.49) | the same |
| The five numbers of four blocks, two years (40) | e.g. 2025 peak 16.13 below zero, 24.91, 37.04, 59.03, 2,350.31; overnight maximum 3,553.10 | 40 of 40 |
| The thesis's figures, two years (18) | 99.9th percentile 583.96 and 311.80; multiple 28.50 and 12.14; midday minimum -3.98 and -18.25; at or above 1,000: 5 and 9; at or below 0: 297 and 959; intervals 35,040 and 35,040 | 18 of 18 |
| Every row of HB_HUBAVG, 2015 to 2025 | 308 annual, 3,696 monthly | equal at six decimals |

- A full local year has 7,300 peak, 5,840 midday and 21,900 overnight intervals in 2015 and 2025; the clock-change days have 92 and 100 intervals (8 March and 1 November 2015, 9 March and 2 November 2025), as the decisions say, and only the overnight block changes.
- 2025's highest interval, 3,553.10, is at 06:45 local on 7 April, in the overnight block; 2015's, 1,538.66, at 18:15 on 8 February.
- The decisions' quoted figures restate: 2021's plain mean 148.19 and median 24.60; 2024's plain mean 26.83; 2021's 645 intervals at or above 1,000 and 99.9th percentile 9,000.85 (but see finding 3).
- The median of 2025's peak block is 37.035 at six decimals and is written 37.04: the tie away from zero the note describes (the faults of 16 November, row 13).

### The ERCOT tab of /prices (HB_HUBAVG, 2025, as it first draws)

- 30 checked figures: 30 of 30 equal the restatement; 29 are also on `/explore`'s default view, with the same text; the 30th is the all-interval IQR, 17.07, which only the tab draws.

### Demand growth (ERCOT, the whole year's average hour)

- 94 of 94 figures and hover lines equal, from the table's levels: growth +27.22 percent (43,798 to 55,717 MW); the year so far +33.34; the eight bars and the "Every grid" table (ERCOT, SPP, Lower 48, PJM, CAISO, MISO, ISO-NE, NYISO: +27.22, +11.14, +7.03, +5.37, +4.45, +2.20, -2.54, -2.73); seven years of averages, growths, year on year and hours used; the hovers of both bar charts. The table's 48 growth rows equal growth from its levels at two decimals. The fewest hours used of a whole year are CAISO's 2019, 8,725 of 8,760, as the decision says.

### Interconnection (CAISO, positions, 1999 to 2023)

- 201 of 212 distinct figures equal from the queue tables held here (the CAISO, ERCOT and SPP pulls of 26 September), the header's count of CAISO positions with no queue date (0) among them. The 11 others: one CAISO position of entry year 2019 withdrawn in the table and waiting in the pull held here (100 against 99 withdrawn, 30 against 31 waiting, a share of 0.72 against 0.71), and eight cells of ERCOT's and SPP's 2023 in the six queues' table, whose pulls change weekly. The table read the pulls of 19 October; this machine does not hold them. Not a fault found; a data request below.
- The opening year stands on 4 CAISO positions (2022 on 2): the faults of 16 November, rows 1 and 2, and the ruling alternatives' line 2. Not repeated.

## One rule changed at a time (the peak premium)

The base: HB_HUBAVG, real time, every interval of every day, medians; the premium (peak median less midday median) and the peak-block IQR, 2015 and 2025 (`measures_peak.out`, `measures_load.out`).

| Rule | The page | Changed to | Premium 2015, 2025 | Peak IQR 2015, 2025 | Said on the page? |
|---|---|---|---|---|---|
| The page | | | -0.16, 14.52 | 7.64, 34.12 | |
| The peak block's hours | 16:00 to 21:00 | 17:00 to 21:00 / 18:00 to 22:00 / 19:00 to 21:00 | -0.28, 17.49 / -1.02, 18.30 / -0.65, 22.38 | 6.87, 38.09 / 6.05, 37.39 / 6.03, 41.96 | the hours, yes; that both of the market monitor's windows sit inside the block, yes |
| The same | | 15:00 to 20:00 / 16:00 to 20:00 | 0.13, 9.59 / 0.02, 12.91 | 8.81, 29.67 / 8.13, 32.04 | |
| The midday block's hours | 12:00 to 16:00 | 10:00 to 15:00 / 13:00 to 16:00 | 0.87, 16.14 / -0.50, 13.97 | unchanged | the hours, yes |
| The averaging | medians of every interval | plain means | -2.68, 24.68 | | "no mean", yes (the alternatives of 17 November) |
| The same | | the median of each day's peak mean less its midday mean | -0.44, 18.59 | | no (finding 2) |
| The same | | means weighted by ERCOT's system load of the hour | -4.20, 24.09 | | not load-weighted, yes |
| The same | | medians weighted by that load | -0.80, 14.27 | | |
| The market | real time, 15 minutes | day-ahead, hourly | 2.22, 18.37 | 11.24, 31.22 | "not the day-ahead price", yes |
| The days | every day | weekdays / weekdays without NERC's six holidays | -0.41, 15.25 / -0.45, 15.42 | 7.55, 35.78 / 7.52, 35.72 | "weekends and holidays included", yes |
| The same | | without the two clock-change days | -0.18, 14.51 | 7.68, 34.09 | yes |
| The same | | June to September only | -2.58, 12.89 | 7.88, 33.40 | |
| The dollars | each year's own | 2025 dollars (GDP price index, x1.3251 for 2015) | -0.21, 14.52 | 10.12, 34.12 | no (finding 1) |
| The block | 16:00 to 21:00, every day | the traded on-peak block, 06:00 to 22:00 on weekdays | real-time on-peak median 22.96 and 27.23; off-peak median 18.91 and 24.88 | | not computed, yes |

- **What moves the premium:** from 2015 to 2025 the premium rose 14.68 = the peak median's +12.91 less the midday median's -1.77. The rise is the evening's, not midday's fall.
- **"Wider than at midday"** (the ruling asked on 16 November, default the sentence stays): the midday block's IQR is 9.33 in 2015 and 14.35 in 2025, so the peak block was narrower than midday in 2015 (7.64) and 19.78 wider in 2025. Measured, not repeated as a finding.
- **Means disagree in sign with medians before 2020:** the plain means' difference is -2.68 (2015) to -17.49 (2019) while the medians' is -0.16 to +0.49, and 79.58 in 2023 against 6.50. The page shows medians and says why.

## Each claim against the code

| Claim | Where | What the code does | Verdict |
|---|---|---|---|
| "how much higher and how much wider ERCOT's real-time price runs from 16:00 to 21:00 than at midday: the peak median minus the midday median, and the peak block's interquartile range" | the definition line | `peak_minus_midday_median` = P50(peak) - P50(midday), `peak_iqr` = P75(peak) - P25(peak), over every interval of the period | **Right as computed.** "Higher": a difference of two pooled medians, not a typical day (finding 2). "Wider": the ruling of 16 November |
| "every 15-minute interval with no cap or exclusion, blocks by the local (America/Chicago) hour an interval starts" | the source line | as said; 92 and 100 intervals on the clock-change days | **Right** |
| "These hours on every day of the year, weekends and holidays included" | decision `blocks` | no day filter | **Right**; worth 0.90 in 2025 (weekdays without holidays) |
| "the tightest hours ... 4 to 5 p.m. in the past and 7 to 9 p.m. now: both are inside the peak block" | decision `blocks`, source | true; the block's width dilutes the second: 22.38 over 19:00 to 21:00 against 14.52 | **Right as stated**; measured |
| "a mean is moved by a few very high intervals (... 148.19 ... 24.60)" | decision `premium` | restated | **Right** |
| "Real time ... not the day-ahead price" | decision `price` | real time | **Right**; day-ahead measured: 2.22 and 18.37 |
| The dollars | nowhere on the page | nominal; the note's section 4 says "No adjustment for inflation" | **Finding 1** |
| "645 intervals at or above 1,000 USD/MWh ... and a 99.9th percentile of 9,000.85" | decision `no-cap` | the year's figures | **Finding 3** |
| "The day the clocks go forward has 92 intervals and the day they go back 100; only the overnight block changes" | decision `local-time` | restated | **Right** |
| "a year is complete at 35,040 intervals ... a month at its days times 96, four fewer in March and four more in November" | decision `years`, `fullMonth` | as said | **Right** |
| "Stale after three days" | decision `freshness`, the frame | `staleAfterDays = 3` | **Right** for this page; the shared note says three for all (finding 7) |
| The ERCOT tab: "How ERCOT real-time prices spread across the day, for each hub and each year since 2015"; "Each point is one ERCOT operating year; the last year is partial" | `view.tsx`, `Explorer.tsx` | the same rows; the line's last point is 2026 so far | **Right** today (the second sentence is unconditional and true while the newest year is partial) |
| "Nothing is filled." | demand explorer, decision `hours-used` | EIA's adjusted demand holds EIA's estimates, used as reported hours | **Finding 4** |
| "2019 ... the first whole year the warehouse holds for every area" | demand explorer, decision `base-year` | the builder reads 2018 (`r[t].year >= BASE - 1`); EIA's workbooks hold 2018 whole | **Finding 5** |
| "Every year and month of every area passes: the fewest is CAISO's 2019, 8,725 of 8,760 hours" | demand explorer, decision `whole-year` | the table's `hours_used` | **Right** |
| "Weather is not removed" | demand explorer, the freshness line and the definition | as metered | **Right** |
| "Source: the ISO's own interconnection queue as the ERW last pulled it" | every interconnection figure's hover (`source.ts`) | the table read the pull it was built from; the catalogue on 26 November gives the build as 16 November and CAISO's pull as 23 November | **Finding 6** (open since 16 November, row 11) |
| "On the table as built on 21 October 2026: no CAISO position, 1 of ERCOT's and 48 of SPP's have no queue date" | interconnection decision `entry-year` | the header of that build | **Right** (dated) |
| The statuses in each ISO's own words; the share by count; the wait in days over 365.25 | interconnection decisions | restated (above) | **Right** |
| "A table not computed for more than three days is said to be stale" | `docs/methods/explorers.md` | 3, 35 and 8 days | **Finding 7** |

## Two addresses, one tool

- `/explorer/ercot-peak-premium` redirects permanently to `/prices?tab=ercot` (`site/next.config.ts`), whose tab draws `Explorer.tsx` over the same two tables. With nothing chosen it shows HB_HUBAVG and the newest complete year (2025) alone; `/explore` shows 2015 against 2025. On the figures they share they agree to the digit (29 of 29), by the same writer (`toLocaleString` with two decimals, `price()` in `lib/format.ts`).
- What differs, none of it false today: the tab has no decisions block (`app/prices/page.tsx` draws none on the ERCOT tab), no second year, no month view and no freshness line of its own (the header's last input interval only); its year list would mark "(partial)" a year a hub has no row for (every hub holds every year, so none shows); its Ask link names the old address. The fixes of findings 1 to 3 reach `/explore` only.

## Held grids and the as-of date

- **Held grids.** None reaches a figure of any of the three (In short, last bullet). The interconnection table's header names NYISO's, MISO's and ISO-NE's counts in its "no queue date" line; the page draws only the chosen queue's, and a held queue returns before any read.
- **As of 26 November 2026** (the catalogue, `warehouse/metadata/coverage.csv` on main): the peak premium tables last computed 20 November 18:32 UTC, more than three days ago, so the page reads "Stale since 20 November 2026"; `eia930_demand_growth` 6 November, fresh under its 35 days, its year so far to October 2026; `iso_queue_statistics` 16 November, more than eight days ago, so "Stale since 16 November 2026", CAISO's queue pulled again on 23 November. The default views' peak premium figures (2015, 2025) and demand growth's whole years do not move with a rebuild unless EIA revises; the year so far, the newest month and the interconnection counts do.

## Findings

| # | Severity | Finding | Measured | Branch | Kind |
|---|---|---|---|---|---|
| 1 | Moderate | The peak premium sets 2015 beside 2025 in each year's own dollars and never says so | GDP price index +32.5 percent; 2015's peak-block IQR 7.64 is 10.12 in 2025 dollars; the IQR's growth x4.47 nominal, x3.37 real | `wip/audit-explore-1` (words); `wip/audit-explore-2` (the figure) | words, for landing; figure, the owner's |
| 2 | Moderate | "How much higher" is a difference of two pooled medians, which is not the typical day's gap; the page says so of two hubs, not of two blocks | the median day 18.59 (2025), -0.44 (2015) against 14.52 and -0.16; evening above midday on 95.3 and 44.7 percent of days | `wip/audit-explore-3` | words, for landing |
| 3 | Low | "February 2021 ... is in 2021's figures: 645 intervals" reads as February's count | 645 in the year, 608 in February; the year's 99.9th percentile 9,000.85, 1,058.53 without February | `wip/audit-explore-4` | words, for landing |
| 4 | Moderate | The demand growth explorer says "Nothing is filled"; EIA's adjusted demand holds EIA's estimates, used as reported hours, and the explorer prints MISO's 2025 peak, one of them | 351 hours 2019 to 2025; MISO 120,343 MW (+3.21) against its own reports' 118,106 (+1.29) (the consumption audit's measures) | `wip/audit-explore-5` | words, for landing |
| 5 | Low | The explorer calls 2019 "the first whole year the warehouse holds for every area" | the builder reads 2018's hours; EIA's workbooks hold 2018 whole in all eight areas; on 2018 CAISO's 2025 growth is -0.74 and MISO's -0.63 | `wip/audit-explore-6` | words, for landing |
| 6 | Low | Every interconnection figure's hover says "as the ERW last pulled it"; the table is older than the last pull | built 16 November; CAISO pulled 23 November (the catalogue of 26 November) | `wip/audit-explore-7` | words, for landing |
| 7 | Very low | The explorers' shared note gives three days as every explorer's stale day | 3, 35 and 8 days in the pages | `wip/audit-explore-8` | words, for landing |

### 1. The dollars

- **Where.** `site/app/explore/ercot-peak-premium/Decisions.tsx`, decision `price`; the page has no word on dollars; `docs/methods/ercot_peak_premium.md` section 4 says "No adjustment for inflation".
- **Why it matters.** The default view is a ten-year comparison and its strongest number is a ratio of two years' dollars. An economist reads "34.12 against 7.64" as a quadrupling; in constant dollars it is a little over three times.
- **How much.** BEA's GDP implicit price deflator as EIA's Short-Term Energy Outlook carries it (`site/data/forecast/deflator.json`, the forecast tool's): 97.28 in 2015, 128.90 in 2025. In 2025 dollars, 2015's median 27.15 (20.49), 99.9th percentile 773.82 (583.96), peak IQR 10.12 (7.64), premium -0.21 (-0.16), midday minimum -5.27 (-3.98). Ratios and counts do not move.
- **The tests.** `tests/test_audit_explore_1.py` (the index, the IQR in 2025 dollars where the table is held, no adjustment in the page; the words fail on main). `tests/test_audit_explore_2.py` on `wip/audit-explore-2`: 2015's thesis figures in 2025 dollars (passes on main where the table is held).
- **The fix on the branch, words only.** The decision on the price adds: "The dollars are each year's own (nominal): nothing is adjusted for inflation. By the GDP price index, prices rose 32.5 percent from 2015 to 2025, so 2015's peak-block IQR of 7.64 USD/MWh is 10.12 in 2025 dollars, and the IQR grew 3.37 times in real terms where the page's figures give 4.47." Its source names the index. Drawn and read (`b1_drawn_words.txt`): pass.
- **For the owner.** Writing 2015 to 2024 in 2025 dollars moves every price figure of those years (2015's by x1.3251). Default: left as it is.

### 2. Two medians, not a typical day

- **Where.** The definition line and decision `premium`; the two-hub tip says the same of two hubs.
- **How much.** `measures_peak.py`: each local day's peak-block mean less its midday-block mean; median over the 365 days 18.59 in 2025 and -0.44 in 2015; the mean of the days equals the means' difference (24.68, -2.68); the evening above midday on 348 of 2025's days (95.3 percent) and 163 of 2015's (44.7).
- **The test.** `tests/test_audit_explore_3.py` (the days' gaps where an extract of the prices is named; the words fail on main).
- **The fix on the branch, words only.** The decision on the premium adds: "The difference of the two blocks' medians is not the typical day's gap, as the difference of two hubs' medians is not theirs: taking each day's peak-block mean less its midday-block mean, the median day at the hub average is 18.59 USD/MWh in 2025, where the page's figure is 14.52, and -0.44 in 2015, where it is -0.16; the evening ran above midday on 95.3 percent of 2025's days and on 44.7 percent of 2015's." Drawn and read (`b3_drawn_words.txt`): pass.

### 3. Whose 645

- **Where.** Decision `no-cap`.
- **How much.** `checks_peak.py`: 2021, 645 intervals at or above 1,000 USD/MWh, 608 of them in February (the monthly table: 608; January 0); the year's 99.9th percentile 9,000.85, 1,058.53 without February.
- **The test.** `tests/test_audit_explore_4.py` (the tables' rows; the percentile without February where the prices are named; the words fail on main).
- **The fix on the branch, words only.** "February 2021 (Winter Storm Uri) is in 2021's figures: the year has 645 intervals at or above 1,000 USD/MWh at the hub average, 608 of them in February, and a 99.9th percentile of 9,000.85, which would be 1,058.53 without February." Drawn and read (`b4_drawn_words.txt`): pass.

### 4. EIA's estimates on the explorer

- **Where.** `site/app/explore/demand-growth/Decisions.tsx`, decision `hours-used`. The consumption audit's branch `wip/audit-demand-1` changes `/demand`'s page, `lib/decisions.ts` and the note, not this file; the explorer draws MISO's 2025 peak at `?grid=miso&window=peak` (120,343 MW, +3.21 percent, the table's row, restated here).
- **The test.** `tests/test_audit_explore_5.py` (the table's MISO row where held; the words fail on main).
- **The fix on the branch, words only.** The line reads "Nothing is filled here, but EIA's adjusted demand already holds EIA's own estimate for an hour an operator reported nothing for or reported implausibly, and such an hour is used as a reported one." The default adds the 351 hours by operator and MISO's peak on its own reports (118,106 MW, +1.29). Drawn and read (`b5_drawn_words.txt`): pass. The figure (reading the operator's own Demand) is the consumption audit's `wip/audit-demand-2`, not repeated.

### 5. 2018 is held

- **Where.** Decision `base-year`; `warehouse/derived/demand_growth.py` line 102 reads hours from `BASE - 1`.
- **The test.** `tests/test_audit_explore_6.py` (the builder's lines; the words fail on main).
- **The fix on the branch, words only.** "2019, the last whole year before the pandemic and the first year the table writes. It is not the first whole year the warehouse holds: EIA's workbooks are whole for 2018 in every area, and the table's builder reads 2018's hours for its test of each hour." with the two signs that turn on 2018. Drawn and read (`b6_drawn_words.txt`): pass. The base itself is the consumption audit's `wip/audit-demand-8`, not repeated.

### 6. The pull the table was built from

- **Where.** `site/lib/explore/source.ts` line 37; `docs/methods/explorers.md` (the interconnection section). Found on 16 November (`interconnection-faults-2026-11-16.md`, row 11) and left open because the file is shared; tonight no sibling session edits it.
- **The test.** `tests/test_audit_explore_7.py` (the catalogue's two dates; the words; a figure's hover as `sourceOf` writes it, with node where `site/node_modules` is, skipped otherwise).
- **The fix on the branch, words only.** "the ISO's own interconnection queue as the ERW held it when the table was built (<iso>_interconnection_queue), computed by the ERW"; the shared note says the same and why it can be older; the explorer's note records the change. The test of session 2200 holds only the words' start, which is unchanged. Drawn and read (`b7_drawn_words.txt`): pass.

### 7. Each explorer's stale day

- **Where.** `docs/methods/explorers.md`, "Live, not a frozen file".
- **The test.** `tests/test_audit_explore_8.py` (the three pages' rules; the words fail on main).
- **The fix on the branch, words only, in the note.** The line gives three days on the peak premium explorer, 35 on demand growth and eight on interconnection, each with its reason. A note only: no component to draw.

## The branches

Each from `origin/main` (`e9e70cf12`), pushed. The seven words branches merge together onto it with no conflict (a local trial, not pushed, so no `wip/audit-explore-words`); on that merge the branches' own tests and every test file that reads the changed files (`test_session1496`, `2200`, `2201`, `2202`, `2204`, `7507_peak_premium`, `7508_demand_growth`, `7517_demand_growth_read`) pass: 87 passed, none skipped (`merged_tests.out`, the data tests run against the main copy's tables and the audit's price extract). Each words test fails on origin/main; each data test passes there.

| Branch | Head | Kind | Files | Test | Drawn and read |
|---|---|---|---|---|---|
| `wip/audit-explore-1` | `14b2fa2d0` | words, for landing | `site/app/explore/ercot-peak-premium/Decisions.tsx` | `tests/test_audit_explore_1.py` | pass |
| `wip/audit-explore-2` | `90dcef513` | figure, not for landing | test only | `tests/test_audit_explore_2.py` | not drawn (no words) |
| `wip/audit-explore-3` | `0588a2d65` | words, for landing | `site/app/explore/ercot-peak-premium/Decisions.tsx` | `tests/test_audit_explore_3.py` | pass |
| `wip/audit-explore-4` | `118957ed5` | words, for landing | `site/app/explore/ercot-peak-premium/Decisions.tsx` | `tests/test_audit_explore_4.py` | pass |
| `wip/audit-explore-5` | `37239e2d7` | words, for landing | `site/app/explore/demand-growth/Decisions.tsx` | `tests/test_audit_explore_5.py` | pass |
| `wip/audit-explore-6` | `d6565b9a7` | words, for landing | `site/app/explore/demand-growth/Decisions.tsx` | `tests/test_audit_explore_6.py` | pass |
| `wip/audit-explore-7` | `c1cd7bc6d` | words, for landing | `site/lib/explore/source.ts`, `docs/methods/explorers.md`, `docs/methods/interconnection_explorer.md` | `tests/test_audit_explore_7.py`, `tests/audit_explore_7_source.mjs` | pass |
| `wip/audit-explore-8` | `15f76f034` | words, for landing | `docs/methods/explorers.md` | `tests/test_audit_explore_8.py` | a note only |

## Data requests (rows for the data machine)

1. **The interconnection default view on the pulls the live table read.** From the CAISO, ERCOT and SPP queue pulls that `iso_queue_statistics`' build of 16 November names in its "Inputs read" line: the default view's figures (CAISO, positions, entry years 1999 to 2023, and the three queues' entry year 2023), set beside the table's rows; and which CAISO position of entry year 2019 is withdrawn there and waiting in the pull of 26 September. To close the 11 of 212 figures this machine could not restate.

## What was checked and found right

- The blocks' rule on the local hour, the clock-change days, the linear percentile, no cap, a past period whole, the six-decimal rows and the page's writing of them, the tie away from zero.
- The demand explorer's selection of each grid's last whole year and newest year, the ordering of the bars, growth from the levels, the year so far's months in the labels.
- The interconnection statuses in CAISO's words, the share by count, the median wait, the header count, the held queues not read.
- The two addresses' agreement.

## Not covered, or left open

- The peak premium's other five hubs and its month views were not restated here; the replication of 16 November met 25,704 of 25,704 rows for all six.
- The ERCOT tab was drawn in its first state only (a client component: no click was run).
- The year so far of 2026 and the partial month were not restated (they depend on the build's cut).
- The Ask link was not run (it calls a model).
- No layout at 390 px, no browser.
