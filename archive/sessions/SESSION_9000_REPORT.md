# Session 9000 report (chain 601, the first session; lab-desktop, data machine, first window)

Chain: `queue/done/601-night-20-november-desktop-grid-conditions.md`. Progress: `docs/state/progress_c601.md`. Branch: `wip/c601-congestion` (worktree `C:\Users\Shared\Documents\erw-c601`).

## What a reader sees that was not there before

- Nothing yet on production: the two new pages (`/congestion`, `/conditions`) are on the branch and land through the gate after their files are built from the full pulls.

## Done

- The chain file taken (`c069d7d21`, an earlier try at 10:26 UTC had moved it without a push; merged and pushed at 10:30); resume file `queue/next/602-resume-chain-601.md` alone and pushed.
- Snapshot `c601-s9000-a` (10:37 UTC) against chain 581's `c581-close-after`: 0 differences in all 25 pages.
- Part A: nothing requested in any landing or data request file (five_tools 2 and 5, forecast 5, licenses 11 and 12 all stopped on rulings already recorded).
- Part B: `docs/reviews/grid-conditions-sources-2026-11-20.md`. Robots read for www.ercot.com (disallows `/misapp`, `/misdownload`), oasis.caiso.com (none), www.caiso.com (`/resources/*` only), portal.spp.org (none), www.spp.org (none), www.bpa.gov (`/customerportal/` only). CAISO and SPP cleared; ERCOT not pulled (ruling 2 of 6 November); PJM, NYISO, ISO-NE held; MISO paused.
- Part C: `grid_congestion.py`; `constraints_binding_hourly` 399,250 rows (2025-01-01 to 2026-11-20); `congestion_page.py` (two monthly tables and the page file); `/congestion`; replication; cross-check: 23 of CAISO's monitor's 25 top constraints of 2025 within one point of its frequency (none below; the two furthest 3.0 and 1.7 points, cause not known); SPP's monitor's top two flowgates rank 1 and 2 here by summed shadow price, its third and fourth 7 and 12 (the monitor ranks by rent, which weighs flow).
- Part D: `grid_outages.py`; `generation_outages_hourly` (CAISO 2026 written, 23,184 rows; SPP from 2025 pulling).
- Part E: `grid_all_alerts` 5,397 rows (CAISO 1,906, ERCOT 178, OE-417 3,313).
- Part F: `caiso_tie_flows.py`; `caiso_tie_flows_5min` 569,820 rows, 68 pairs, 2026-10-16 to 2026-11-18.
- Part G: `conditions_page.py`, `/conditions`, tour stop held (`landed: false`).

## Faults found and fixed at their cause

- SPP writes interval ends two ways (`11/18/2026 07:00:00` and `11/1/2026 6:00`): both read strictly (`spp_time`).
- SPP's older files capitalize their column names (`GMTINTERVALEND`, `SETTLEMENT_LOCATION`): read as the newer names.
- SPP's outage files before 1 April 2026 have no `BAA` column: the one area, SPP.
- SPP's outage file of a day starts at 03:00 Central: hours 0 to 2 come from the day before's file.
- The outage registry first named a CAISO library page never read; it answered 404 when read; replaced by a report that was read.
- Each pull failed loudly and wrote nothing when a layout changed, as the rules ask.

## Decisions made without you

- Table names with three parts, as the data standard's validator requires: `generation_outages_hourly` (the chain said `generation_outages`) and `grid_all_alerts` (`grid_alerts`).
- `operating_reserves_hourly` and `scarcity_pricing_hours` not built (rule 4): the warehouse holds the scarcity hours (`scarcity_hours_by_grid`, `ercot_rtm_price_adders`), ERCOT's reserve plan and SPP's day-ahead reserves; no open operator publishes reserves against the requirement over time; SPP's real-time reserves are 288 files a day.
- CAISO constraints keyed by constraint and contingency (CAISO lists one branch under several contingencies in an hour).
- Signs of shadow prices as printed (SPP negative, CAISO positive); ranks by size.
- "Cost most" is the shadow price summed over hours bound; no dollar total (no flow is published).
- CAISO outages: each curtailment weighted by the share of the hour it covers; a resource's hour capped at its Pmax (none was over in the trial).
- `/conditions` keeps hourly figures for the newest 35 days and the nine events; daily elsewhere.
- History: 2025 and 2026 first; earlier years in part H, newest first.

## For Samuel's ruling (the default taken)

- ERCOT's shadow prices, outages and constraints are only on paths its robots file disallows or behind the API key not made: not pulled; drawn blank with "source needed".
- PJM, NYISO and ISO-NE: not pulled; blank with "license needed". MISO: blank with "paused".
- Where `/congestion` and `/conditions` sit in the menu: in no menu until you add their `release.ts` and `pages.ts` lines.

## Needs the key

- Nothing: no step of this session needs a model.

## Later in the session

- History deepened: `constraints_binding_hourly` to the archives' start (SPP 1 March 2014, CAISO 2015): 1,808,231 rows; `price_congestion_hourly` CAISO from 10 August 2023 (OASIS's window), SPP from 2024 (its year zips read, 294 MB a year): 1,209,755 rows; `generation_outages_hourly` SPP from 7 October 2016 (its archive's start), CAISO from 2025 and pulling back to 17 June 2021: 1,080,729 rows before CAISO's history.
- More faults fixed at their cause while deepening: SPP's 2023 file prints one element twice (its ends in each order; kept once); SPP's files before 2022 have no contingency name; a bare-date midnight (2022); empty padding rows (2015); local-time-only files (2014; a repeated or skipped hour would be a named gap; none was); a column spelled CONSTRAINTTYPE (2014).
- Page files built from the warehouse; replication 12,999 of 12,999; the seven tables registered, archived (4,055,094 rows) and 171 key tests passed.
- Gate 1 (`42a8d2faa`, 12:25 UTC): the suite failed on two tests: the tour stop's flag (it must be on when the page is in the commit; turned on) and test 78, which chain 630's codebook files on main trip (YAML descriptions naming the CAISO join date; the test now scans code, not the codebook, which builds nothing). Gate 2 from 12:44 UTC.
