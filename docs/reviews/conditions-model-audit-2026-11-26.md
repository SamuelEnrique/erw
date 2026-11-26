# Grid conditions (`/conditions`): its figures audited as a hostile expert would

Session 10219, chain 710 part D, 26 November 2026, the old laptop. Read as a grid operator's reliability analyst and a trader watching scarcity, who want to find it wrong. Platform tool 7, "Grid stress and real-time conditions": the page `/conditions` (`site/app/conditions/page.tsx`, its decisions in `Decisions.tsx`), its files `site/data/conditions/<operator>.json`, their builder `warehouse/derived/conditions_page.py` and the alerts fold `warehouse/derived/grid_alerts.py`. The Grid tool's figures were audited this morning (`docs/reviews/grid-model-audit-2026-11-26.md`) and the battery fleet's (`docs/reviews/storage-model-audit-2026-11-26.md`); neither is repeated.

- Nothing changed on main but this file and its evidence folder (`docs/reviews/conditions-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no live service asked.
- Each finding has its own branch, `wip/audit-conditions-<n>`. The words-only fixes are for landing; the figure fixes carry a test only and wait for the owner.

## In short

- **The arithmetic is right.** Every figure the default view prints (ERCOT, the newest days) and every operator's opening view came out to the digit in an independent restatement from the page files: the window, the hours drawn, the "at a glance" figures and their days, the alerts count, the status table. Every daily figure the hourly rows can check agrees (15,921 figures) but for the rounding of the hours the file keeps (74 daily means of outages 0.1 MW apart; 143 ERCOT days whose adders above zero round to 0.0 in the hours, finding 6), and the scarcity strip restated from ERCOT's own adder table agrees on all 5,428 daily figures.
- **An impossible hour is printed as the peak (finding 1, a figure).** PJM's "Highest peak demand" over the COVID window reads 215,682 MW (9 April 2020), 2.7 times its forecast and three times the hours around it; the ERW's own rule for impossible hours leaves it out and the figure becomes 108,513 MW (26 May). The page applies no screen. Another such day (224,345 MW, 13 July 2020) is the printed peak for any of 31 chosen days.
- **"Alerts and notices in force (79)" counts rows, not notices (finding 2, words; finding 3, a figure).** A row is one notice, region and day covered, and a notice CAISO reissued is listed again: the August 2020 heat wave's 79 rows are 23 notices; 81 of CAISO's 320 rows since July 2018 repeat another row of the same day, kind, region, start and end. ERCOT's rows include 20 updates that end a notice and 19 statements that announce none.
- **"None held in this window" is a stale source, not a quiet grid (finding 5, words).** No scheduled run reads ERCOT's notices: the table stops at a reading of 19 October, so the default view prints none for 16 October to 20 November whatever ERCOT issued. CAISO's report is held to its revision of 9 October.
- **"Hours the adder was above zero" counts fractions of a cent (finding 6, words; finding 7, a figure).** 55 percent of ERCOT's adder hours above zero since July 2018 were under 5 cents and draw as 0.0 on the page's own hourly chart; the median is 1.6 cents. The COVID window prints 20 such hours on 16 March 2020; at USD 1 it is 6.
- **ERCOT's scarcity did not end on 4 December 2025 (finding 8, words).** Its adder did: scarcity has been priced through the ancillary services' own demand curves since real-time co-optimization began on 5 December 2025, which the page does not draw and does not say.
- **Smaller words (findings 4, 9, 10, 11).** CAISO's Stage 3 rotating outages of 14 and 15 August 2020 and 13 Flex Alerts are drawn with no start or end though CAISO prints them (4, a figure); "constraint-hours" count each constraint once per contingency (9); CAISO's "out of service" holds derates (10); the operator line says hours are in local clock time where the hourly charts are UTC, and the "newest 35 days" hold 36, the last with the forecast only (11).
- **What the page does not print.** No reserve margin, no peak against capacity, no stress score and no scarcity-hour count is on `/conditions`; those are the datacenter page's (the headroom cell, restated here to the digit) and the energy mix's. Held grids reach nothing: ISO-NE, MISO, NYISO and PJM appear by EIA-930's public demand only. Window F's finding, the alerts list cut at 40, **still stands on main** (`rows.slice(0, 40)`; its fix `wip/c750-conditions` is not landed).

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/conditions/page.tsx` | The page. Picker: operator (seven), a second operator, one of nine events, any day from 2018-07-01. With no query it opens on ERCOT, the newest window, no second operator. Per operator: a line naming the window and the clock; "at a glance" (the day of each column's highest figure: peak demand, megawatts out in an hour, constraint-hours, hours with the adder above zero, the last only when above zero); hourly charts for kept windows (demand and EIA's day-ahead forecast; out of service, total, planned, forced; constraints binding and the largest shadow price; the adder); daily charts (peak and forecast peak; out of service mean and highest hour; constraint-hours; hours the adder was above zero); the alerts heading with its count and a table of the first 40; a blank reserves strip. Then "What is held for each grid" (each strip's status, the reason on hover), the decisions, downloads |
| `site/app/conditions/Decisions.tsx` | Eight decisions, the method note's reasoning |
| `site/lib/conditions.ts` | The files' shape; `windowOf`: an event's own days, a chosen day's fifteen days either side (hourly when a kept window holds the day), else the newest window |
| `site/components/TimeChart.tsx`, `LineChart.tsx` | The charts; an hourly axis labels its instants in UTC ("... UTC"), a daily axis the day string |
| `site/data/conditions/<op>.json`, `index.json` | The page files: daily rows from 2018-07-01, hourly rows for the newest window and the nine events, each strip's status, the alerts list. Committed copy built 2026-11-20 19:16 UTC by the data machine's daily run |
| `warehouse/derived/conditions_page.py` | The builder: EIA-930 demand and forecast (`eia930_ba_demand_hourly`), outages (`generation_outages_hourly`: SPP's RTO area, CAISO), constraints (`constraints_binding_hourly`: count of rows and largest absolute shadow price an hour), ERCOT's `rtorpa_mean`, alerts from `grid_all_alerts` (CAISO and ERCOT only); a local day's peak, lowest, mean, highest, count; hourly values rounded to 0.1; the newest window is the build's UTC day less 35 days to that day |
| `warehouse/derived/grid_alerts.py` | `grid_all_alerts`: CAISO's grid emergencies, ERCOT's notices and DOE's OE-417 in one shape, each source's own kind, start and end |
| Inputs | `caiso_grid_emergencies` (`connectors/caiso_emergencies.py`, daily on the data machine), `ercot_grid_notices` (`connectors/ercot_grid_notices.py`, in no scheduled run), `ercot_rtm_price_adders`, `generation_outages_hourly` (`connectors/grid_outages.py`), `constraints_binding_hourly`, `eia930_ba_demand_hourly` |
| Notes | `docs/methods/grid_conditions.md` (the page), `grid_alerts.md`, `grid_outages.md`, `grid_congestion.md`, `caiso_grid_emergencies.md`, `ercot_grid_notices.md`, `ercot_rt_price_adders.md`, `impossible_hours.md`; `grid_stress.md`, `grid_peak_vs_capacity.md`, `scarcity_hours_by_grid.md` (not read by `/conditions`; see "What the page does not print") |

## The default view re-done, to the digit

This machine holds neither the live set nor `eia930_ba_demand_hourly`, `generation_outages_hourly`, `constraints_binding_hourly` or `grid_all_alerts`; the page reads none of them either. It reads its committed files, and every figure below is restated from those files with none of the site's code and none of the builder's (`restate.py`, standard library), from the rules as `page.tsx` and `lib/conditions.ts` state them. Where an input is held in the main copy (read only), the file was restated from it too.

| Figure (no query: ERCOT, the newest window) | Restated | Page's rule gives |
|---|---|---|
| The window | "the newest 35 days, 2026-10-16 to 2026-11-20; days and hours in America/Chicago clock time for days and hours" | the same words |
| Hours drawn | 865 (2026-10-16 05:00 to 2026-11-21 05:00 UTC); EIA's demand to 2026-11-20 05:00 UTC, the forecast a day further | the same |
| Highest peak demand | 65,888 MW, on 2026-11-02 | the same |
| Megawatts out, constraint-hours | not drawn: "source needed", the reason on hover | the same |
| Hours with the adder above zero | not printed (no adder after 4 December 2025; the glance drops a zero) | the same |
| Alerts heading | "(0)"; "None held in this window. The last the file holds is of 2026-10-15." | the same |
| Status table | 7 grids by 6 strips, as `index.json` (which agrees with each file) | the same |

| Each operator's opening view (`?a=`) | Glance | Alerts |
|---|---|---|
| CAISO | peak 34,916 MW (2026-10-16); out 29,078 MW (2026-11-04); constraint-hours 313 (2026-10-16) | 0 (last 2026-10-08) |
| SPP | peak 36,383 MW (2026-10-28); out 30,514 MW (2026-11-05); constraint-hours 740 (2026-11-20) | not read |
| MISO, PJM, NYISO, ISO-NE | peak 79,593 (11-17); 106,646 (11-17); 18,952 (11-13); 15,275 (11-16) | paused; license needed |

- **The daily rows against the hours.** For every local day a kept window holds whole (253 a grid, 252 for MISO and PJM), each of the nine daily figures restated from the hourly rows: 15,921 figures, all equal but 74 out-of-service means (CAISO 9, SPP 65), each 0.1 MW apart, because the file keeps its hours to 0.1 and the builder takes the mean before rounding. And 143 of ERCOT's days count more hours above zero than the hourly rows show (518 hours): the file's hours of 0.0 were adders above zero rounded down (finding 6). Every alerts count by day equals the list (`restate.out`, `diffs.out`).
- **The scarcity strip from its input.** `adder.py` read `ercot_rtm_price_adders` (`rtorpa_mean`, 100,878 hours, 2014-06-01 to 2025-12-05 05:00 UTC) and rebuilt each Central day's hours above zero and highest adder: 5,428 of 5,428 figures equal the file.
- **The alerts list from its inputs.** `alerts.py` folded `caiso_grid_emergencies` and `ercot_grid_notices` as `grid_alerts.py` does: ERCOT's 178 rows equal the file's; CAISO's 1,906 equal it but one, a Flex Alert CAISO's newer revision moved from 30 September 2020 (no times) to 1 October 2020 15:00 to 22:00.
- **The headroom cell (`/cost-of-power`, All grids), from `site/data/siting/headroom.json`:** capacity over peak CAISO 105.89 (shown "106% above peak"), ERCOT 97.00, ISO-NE 36.69, MISO 62.43 and the rest, each `capacity / peak - 1`; ERCOT's planning reserve margin, Summer 2027, 11.428383 = (109,349.8 - 98,134.6) / 98,134.6, shown 11.4 (`measures.out`).

### One rule changed at a time

`measures.py`, `adder.py`, `alerts.py` and `spikes.py`, on the page files and, read only, the main copy's inputs.

| Rule | The page | Changed to | Measured worth |
|---|---|---|---|
| Impossible hours | every EIA-930 hour as published | the ERW's own rule (`impossible_hours.screen`) | in the kept windows 4 hours left out; one printed figure moves: PJM's highest peak in the COVID window 215,682 MW (2020-04-09) becomes 108,513 (2020-05-26). Outside kept windows (daily rows only) PJM's 224,345 MW of 13 July 2020 (its forecast 123,094) is the printed peak for 31 chosen days; NYISO has 5 days whose lowest hour is 0 MW, CAISO one of 14 MW, SPP one of 1,505 |
| What an alert row is | one row a notice, region and day covered, reissues listed again | one a distinct notice (kind, start, end) | CAISO heat 2020: 79 becomes 23; Uri (CAISO): 26 becomes 3; heat 2022: 44 becomes 35; Uri (ERCOT) 6 becomes 4; ERCOT heat 2023: 23 becomes 15 |
| What an alert is | every ERCOT row | without updates (a release ending a notice) and statements (announcing none) | 39 of 178 rows; Uri 2 of 6, heat 2023 1 of 23 |
| The adder's level | above zero | at least USD 1 / USD 100 | hours since July 2018: 10,492 / 2,360 / 356; the glance in the COVID window 20 hours on 2020-03-16 becomes 6 (2020-04-08) / 3 (2020-04-27); Uri 24 / 24 / 22 (2021-02-16); heat 2022 15 / 10 / 6; ERCOT heat 2023 12 / 10 / 2 (2023-08-17) |
| The newest window | the build's UTC day less 35 days, to that day | 35 days ending with the last day of demand | 36 days become 35; the last day (20 November) holds the forecast only (0 of 24 demand hours) on every grid |
| The fall-back day | 25 local hours | 24 | 2026-11-01: SPP's constraint-hours 263 lose 3 (1.1 percent), CAISO's 135 lose 4 (3.0 percent); peaks unchanged |
| Capacity "at the end of 2025" | today's list (August 2026) filtered by first year | add back what retired from January to August 2026 | PJM +608.2 MW (7 units), MISO +49.6, SPP +28.5, ISO-NE 16.0, NYISO 1.0, CAISO and ERCOT none: under 0.3 percent anywhere; not a finding |

## Each claim against the code

- **What "capacity" is.** `/conditions` prints none. The decision "available" says demand is drawn against the day-ahead forecast because no operator whose terms allow it publishes available capacity hour by hour, and the reserves strip is blank with that reason: true of the code. The lead's "Is the grid tight" is answered for ERCOT's default view by demand and forecast alone (outages, constraints and reserves blank, the adder ended); the decision says so, the lead does not. The headroom cell on `/cost-of-power` is net summer capacity of today's list, said in its hover with "Not a reserve margin: no imports, outages or derates, and solar and wind at their ratings"; ERCOT's reserve margin beside it is ERCOT's own, wind, solar and storage at its ELCCs, said. Right.
- **A stress score.** None on `/conditions`; no weights or thresholds anywhere in its code. `grid_stress_yearly` (the evening ramp, the tightest hours, dark and calm stretches) is read by the energy mix and the datacenter page, not here.
- **Alerts: by notice or by event.** By row: one per notice, region and day it covers (both connectors' own rule), a reissued CAISO notice once per issue. The heading says "in force" and the table carries no region: CAISO's Northern California transmission emergencies sit beside system alerts unmarked. **Findings 2 and 3.** The start and end are the source's; 15 CAISO rows since 2018 print times the connector did not read. **Finding 4.** The list is cut at 40 without a word (window F, still on main).
- **"Now" and how stale.** The page is the committed files: "Files built 2026-11-20" is said under the title. The newest window is counted from the build's UTC day, so it holds 36 days, the last with the forecast only, and the operator line does not say where demand stops (**finding 11**). The alerts strip says nothing of how current each source is; ERCOT's has not been read since 19 October (**finding 5**).
- **Daylight saving and time zones.** Days are local (the decision "clock" says so) and a fall-back day has 25 hours, a spring day 23; peaks and highs are unchanged, counts gain or lose an hour's worth (1 to 3 percent of the day's constraint-hours on 1 November 2026), not marked. The operator line says "days and hours in America/Chicago clock time for days and hours" while every hourly chart labels UTC instants (**finding 11**). MISO's file uses America/Chicago (Central with daylight saving), where `/grid` uses MISO's own fixed Eastern Standard; the page's decision says Central, so the page is consistent with itself.
- **A forecast against an actual.** The daily chart sets the day's highest forecast hour beside the day's highest demand hour, two hours that need not be the same; its title says "the forecast's peak". EIA-930's day-ahead forecast is the balancing authority's own, as stated. No forecast error is printed. Right.
- **Scarcity: by price or by reserves.** The strip is ERCOT's online reserve price adder, a price set from reserves by the ORDC; the chart title says so. Counted above zero, however small (**findings 6 and 7**). Its end is said as the adder's, with no word that scarcity is now priced another way (**finding 8**). The other grids are "not published ... in the files read", qualified and true of the files read.
- **Constraints.** "Constraints binding (count)" and the daily hover "(constraint, hour) pairs" count rows of `constraints_binding_hourly`, whose key is constraint and contingency (`grid_congestion.md`, decision 2): a branch binding under two contingencies is two (**finding 9**). The largest shadow price "by size" (SPP's negative) is said. Right.
- **Out of service.** SPP's is generation on outage; CAISO's is every curtailment its report lists, derates included (`grid_outages.md`, decision 3). The page calls both "out of service" (**finding 10**).
- **Held grids.** ISO-NE, MISO, NYISO and PJM reach the page only through EIA-930's demand and forecast (public domain). Their other strips are blank with the reason (license needed, paused). `grid_all_alerts`' OE-417 rows, which name every region, are not read (`x_grid` caiso and ercot only). No held row reaches a figure.

## What an expert's own number would hold that this does not

- **Reserves against the requirement, hour by hour.** The reliability analyst's first figure. ERCOT publishes its physical responsive capability; the page has no source a robots file allows (blank, said). Not measurable here.
- **ERCOT's scarcity since 5 December 2025:** the real-time ancillary service prices and their demand curves. Not in any table this machine holds; the adder table stops on 4 December 2025.
- **The adder at a level that matters:** at USD 1 a day of 20 "scarcity hours" in the COVID slump is 6; at USD 100, 3 (finding 7).
- **Notices as events:** the August 2020 heat wave was 23 notices, not 79 (finding 3), each with its region.
- **A screened peak:** 108,513 MW, not 215,682, for PJM's COVID window (finding 1).
- **Distinct constraints an hour:** how far the count of (constraint, contingency) rows stands above distinct constraints needs `constraints_binding_hourly` (data request a).
- **CAISO's outages without derates:** CAISO's report separates outage kinds by its "nature of work"; the table sums them (data request b).

## Findings

| # | Severity | Finding | Measured | Branch | Kind |
|---|---|---|---|---|---|
| 1 | Major | No screen on EIA-930's demand: impossible hours print as the "Highest peak demand" | PJM COVID window 215,682 MW against 108,513 screened; 224,345 MW (13 July 2020) printed for 31 chosen days | `wip/audit-conditions-1` | figure, the owner's ruling |
| 2 | Major | "Alerts and notices in force (N)": the count is rows (notice, region, day covered, each reissue), with ERCOT's updates and statements, and no word says so | heat 2020 79 rows, 23 notices; 81 of 320 CAISO rows since 2018 repeat; ERCOT 39 of 178 updates or statements | `wip/audit-conditions-2` | words, for landing |
| 3 | Moderate | The alerts count by row, not by notice | heat 2020 79 becomes 23; Uri (CAISO) 26 becomes 3; ERCOT heat 2023 23 becomes 15 | `wip/audit-conditions-3` | figure, the owner's ruling |
| 4 | Minor | CAISO notices drawn with no start or end where CAISO prints them | 15 rows since 2018: the Stage 3 rotating outages of 14 and 15 August 2020, 13 Flex Alerts (2021, 2022); 470 in all since 1998 | `wip/audit-conditions-4` | figure, the owner's ruling |
| 5 | Moderate | "None held in this window" where the source was not read: ERCOT's notices are in no scheduled run | ERCOT's table read 19 October 2026, last notice 15 October; the default view prints none for 16 October to 20 November | `wip/audit-conditions-5` | words, for landing |
| 6 | Moderate | "Hours the adder was above zero" counts adders of fractions of a cent, drawn 0.0 on the page's own chart | 5,799 of 10,492 hours since July 2018 under 5 cents; median 1.6 cents; 518 hours drawn 0.0 that the daily count counts | `wip/audit-conditions-6` | words, for landing |
| 7 | Minor | The adder counted above zero rather than at a level | COVID window's glance 20 becomes 6 at USD 1; 2,360 of 10,492 hours at USD 1 or more | `wip/audit-conditions-7` | figure, the owner's ruling |
| 8 | Moderate | ERCOT's scarcity "ended on 4 December 2025": the adder ended, scarcity moved to the ancillary services' demand curves | the default view (ERCOT) draws no scarcity strip for any day after it | `wip/audit-conditions-8` | words, for landing |
| 9 | Minor | "Constraint-hours" and "(constraint, hour) pairs" count each constraint once per contingency | not sized here (data request a) | `wip/audit-conditions-9` | words, for landing |
| 10 | Minor | CAISO's "out of service" holds derates and curtailments, SPP's outages only | CAISO's trial mean 21,400 MW (note); not separable here (data request b) | `wip/audit-conditions-10` | words, for landing |
| 11 | Minor | The operator line: "days and hours in ... clock time" where hourly charts are UTC; "the newest 35 days" hold 36, the last with the forecast only | 36 days, 0 of 24 demand hours on the last, every grid | `wip/audit-conditions-11` | words, for landing |

The sections for each finding follow, with their tests and branches.
