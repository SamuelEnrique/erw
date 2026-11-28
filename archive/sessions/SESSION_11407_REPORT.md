# Session 11407 report (chain 770, part C, old laptop, 28 November 2026)

Lines 164 to 175 of `docs/reviews/weekend-2026-11-28.md` (main at 3321f3092): every choice readied as a branch `wip/ready-*` cut from origin/main, with its test `tests/test_ready_<name>.py`, its figures measured before and after. Nothing requested; no landing file, no `docs/state/` file, no weekend page edited. Work done by eight workers (A to H), each in its own worktree `../erw-c770-g1` to `g8`, all removed; detail files in the main copy's ignored `runs/c770/11407/agent_A.md` to `agent_H.md`, summed up here.

## The table

| Line | Item | Branch | Head | Before (origin/main) | After (branch) | Test |
|---|---|---|---|---|---|---|
| 164 | Winter bill at winter prices | wip/ready-learn-bill-season | 38fbab553 | PG&E 26.91 USD, 11.72% (September 2026, 44.85 USD/MWh) | 18.54 USD, 8.08% (October 2025 to May 2026, 30.91) | test_ready_learn_bill_season.py |
| 165 | Footprint counts joint plants once | wip/ready-companies-footprint | f1c1b37fc | 106 companies' joint plants counted twice (62,736 MW) | 5 of the top 10 move (41 of the top 50; 2 leave) | test_ready_companies_footprint.py |
| 165 | Power marketer in Kind filter | wip/ready-companies-marketer | 160b215d6 | 8 kinds, 439 marketers not offered | "power marketer (439)" offered | test_ready_companies_marketer.py |
| 166 | Battery ends as full | wip/ready-play-battery-full | 0de7d4868 | best score, Normal 2.0882, Uri 240.2274, calm 0.4406 | 1.7809 (-14.7%), 181.7193 (-24.4%), 0.3041 (-31.0%) | test_ready_play_battery_full.py |
| 166 | EV gasoline at 52-week average | wip/ready-play-ev-gas | 44b7c9287 | US USD 3,887, payback 3.6 years, 2 places below zero | USD 2,946, 4.1 years, 6 below zero (MA, NH, NY, RI turn) | test_ready_play_ev_gas.py |
| 166 | ERCOT cap year | wip/ready-play-cap-year | fc80c2192 | "since 2023" | "since 2022" (words only) | test_ready_play_cap_year.py |
| 167 | Each quarter from its file | wip/ready-contracts-quarters | f6efd2225 | 2025 Q3 power rows 273 | 2,129 (Q4 311 to 2,209; 2026 Q1 396 to 701); default view 227 unchanged | test_ready_contracts_quarters.py |
| 167 | Filer's description beside number | wip/ready-contracts-descriptions | 37b6bac9b | 0 cells with words | 1,110 of 1,317 power numbers in the window (178 name an index or adder) | test_ready_contracts_descriptions.py |
| 168 | Weather share inside baseline | wip/ready-events-weather-share | ae5e7dbfe | Uri 80.56, CAISO 2020 70.47, PJM 65.33 | none, 63.86, none | test_ready_events_weather_share.py |
| 168 | Net demand on CAISO 2020 | wip/ready-events-caiso-net-demand | c9ed1a049 | no net demand figure | 14 August highest, 54,390 MW (18th 52,013) | test_ready_events_caiso_net_demand.py |
| 168 | Hydro-gap rule on events | wip/ready-events-hydro-gap | 91b6ca04c | 14 CAISO 2020 carbon days (highest 305.93) | 0 days; COVID-19 also loses 92 CISO days | test_ready_events_hydro_gap.py |
| 168 | Uri on weekday baseline | wip/ready-events-uri-weekday | 502e015a0 | largest shortfall -186,530.50 (21 February) | largest -140,891.00 (24 February); 21 February -37,630.50 | test_ready_events_uri_weekday.py |
| 169 | California gas from CAISO | wip/ready-supply-caiso-gas | 4d688891e | California on the year -22.8%; seven grids +3.49% | +0.8%; +6.46% | test_ready_supply_caiso_gas.py |
| 170 | Twelve months beside one | wip/ready-industry-twelve-months | 3c64d03a4 | total -1.9% (one month only) | +0.4% beside it | test_ready_industry_twelve_months.py |
| 170 | Each region's shares | wip/ready-industry-region-shares | cc4fe0cbd | no regional shares | South chemicals 32.8% (West 42.4, Midwest 22.1, Northeast 16.1) | test_ready_industry_region_shares.py |
| 171 | Not held unless twelve held | wip/ready-states-twelve-held | 2b3037f4b | DC natural gas 40.05% | solar 21.83% (19 sources in 17 places not held) | test_ready_states_twelve_held.py |
| 171 | Round once | wip/ready-states-round-once | 721957e7c | Texas homes 15.98 cents | 15.99 (34 cells move one digit) | test_ready_states_round_once.py |
| 171 | Capacity without Puerto Rico | wip/ready-states-capacity-no-pr | be521b082 | 1,423.5 GW | 1,417.0 GW (September 860M) | test_ready_states_capacity_no_pr.py |
| 172 | Printed digits kept | wip/ready-ai-energy-digits | ec1a7d0a0 | 0.1 Wh; 9e-7 shows as 0 | 0.10 Wh; 9e-7 shown (2 of 23 rows look different, no value moves) | test_ready_ai_energy_digits.py |
| 172 | Filter grouped | wip/ready-ai-energy-filter-groups | 7ea52c6a9 | 13 choices | 8 choices | test_ready_ai_energy_filter_groups.py |
| 172 | The page's name | none | | | | a blank: needs Samuel's word (no other name in the audit, page, note or tour; 7 of 23 rows are per query) |
| 173 | Rebuild the comparison now | none | | | | cannot be readied here: a rerun on the desk, no code change (below) |
| 173 | Load-weighted beside simple | wip/ready-prices-load-weighted | 340b509f5 | SP15 day-ahead 12 months 30.27; NP15 34.11 | 31.42 (+3.8%); 35.15 (+3.0%) | test_ready_prices_load_weighted.py |
| 174 | Screen impossible hours | wip/ready-conditions-screen-hours | 400b56cc8 | PJM COVID-window peak 215,682 MW (9 April 2020) | 108,513 MW (26 May 2020) | test_ready_conditions_screen_hours.py |
| 174 | Count alerts by notice | wip/ready-conditions-alerts-by-notice | 273a76c04 | CAISO 2020 heat wave 79 rows | 24 notices | test_ready_conditions_alerts_by_notice.py |
| 174 | CAISO's other time formats | wip/ready-conditions-caiso-times | c20e9aeb8 | 15 notices without a start | 14 gain one (main already reads the 15th), 0 left | test_ready_conditions_caiso_times.py |
| 174 | Adder from USD 1 | wip/ready-conditions-adder-one | 54ee56cd2 | 20 hours (16 March 2020) | 6 hours (8 April 2020) | test_ready_conditions_adder_one.py |
| 175 | Places of the chosen operator | wip/ready-congestion-places | bafab5828 | SPP view 9 rows | 2 rows (CAISO view 9 to 7) | test_ready_congestion_places.py |
| 175 | An element's keys joined | wip/ready-congestion-keys | 0041017fe | TEXAS_CO_TXPS_TXCO_PHSHFT_PS 60,293 h | 92,128 h (CAISO 2025 largest sum 553,893.0 to 605,826.7) | test_ready_congestion_keys.py |
| 175 | Days on the operator's clock | wip/ready-congestion-operator-clock | 110ec8fa5 | UTC days | 182 of 614 SPP and 125 of 480 CAISO dates move back a day | test_ready_congestion_operator_clock.py |

28 branches pushed; 2 choices not readied. Each branch's own test passes, and every test file importing what it changed; failures seen are also on a clean origin/main (named below) or are by design until the desk rebuilds a file.

## Measured figures that differ from the page

- **Line 168, Uri weekday:** -37,630.50 is 21 February's new value and the largest only over the 15 of 18 days the published table can compare. With the three missing baseline days (read from the extract, not written), the largest is -140,891.00 on 24 February. The branch does all 18 days.
- **Line 168, weather share:** the line's words ("only where the event's weather lies inside the baseline's") and its figures are two different rules. The branch follows the figures (baseline-only fit). Under the words' range rule CAISO 2020 would also show none. Two pages the line does not name also move: CAISO 2022 84.09 to 94.22, ERCOT 2023 50.70 to 69.68.
- **Line 174, alerts:** 24, not 23. The audit's key (kind, start, end) merges the two Stage 3 outages of 14 and 15 August 2020, which have no start; the branch keys a notice without a start by kind and day. With the audit's key, CAISO 2022 would also fall 44 to 35.
- **Line 174, CAISO times:** 14 notices gain a start, not 15 (main already reads the Flex Alert of 1 October 2020, session 7050).
- **Line 175:** the page file was rebuilt on 28 November; SPP North is already 1 of 9, not 2 of 9. The clock moves 182 of 614 SPP dates, not 187.
- **Line 173, load-weighted:** "4.0 to 7.1 percent higher" compares both averages over hours holding price and load. Against the simple average the page prints (every hour): SP15 +3.8%, NP15 +3.0%. The load-weighted values (31.42, 35.15) match the audit.
- **Line 171:** 19 named sources go "not held" today, not 20 (DC's headline matches). Capacity: 1,423.5 to 1,417.0 on this machine's September EIA-860M; the page files carry October, 1,428.1 to 1,421.6 GW (-0.45% either way).
- **Line 166, battery:** "15 to 31 percent lower" holds on four of eight days; heat -0.4%, CAISO ramp -4.8%, CAISO noon -5.9%.
- **Line 167, descriptions:** 1,110 cells gain words, not "up to 178"; 178 is the part whose words change how the number reads.
- **Line 165, footprint:** RWE Americas (13th to 10th) replaces PacifiCorp in the top 10, not DTE Electric as the audit said (company files rebuilt 26 November). The audit's own test `wip/audit-companies-8` now fails on its DTE line.
- **Line 164:** SCE also moves, 10.28% to 6.53%. SDG&E stays on the latest month: its season change is not read as a date anywhere.

## Not readied

- **Line 172, the page's name:** a blank, needs Samuel's word. Neither the audit nor the page, its method note or the tour names another.
- **Line 173, rebuild the comparison:** the builder from origin/main reproduces the site's file exactly on this machine's tables (SPP 552 of 744 October hours here), so the code is not at fault. Ready it on the desk under the lock: `python warehouse/lock.py run --task price_compare -- python warehouse/derived/price_compare.py --snapshot`, then commit `site/data/price_compare.json`. From today's board hourly files, SPP North October real time 34.35, SPP South 25.30 (744 hours each). ZP26 stays 45.35 on 720 hours: 15 October is missing from the real-time table on every machine; reaching 744 needs `price_compare.py` to also read `iso_zone_prices_history` (not made: it may add other rows, not measured).

## What landing needs (for the desk, when Samuel chooses)

- **Site files rebuilt at landing by the desk:** companies-footprint (company page files; `test_session3304_companies` fails until then, by design), play-ev-gas (`site/data/ev_prices.json`; this machine's gasoline table ends 2 November, so the desk's figure will move slightly), supply-caiso-gas (`site/data/supply.json`), events-hydro-gap and events-uri-weekday (`event_window_daily`, plus `replication/events/page_figures.json` and `replicate.py`'s rules), states-twelve-held and states-capacity-no-pr (`site/data/states/`), prices-load-weighted (`site/data/price_compare.json`; ERCOT's load table ends 1 October here, under the 95% floor), conditions-screen-hours, conditions-caiso-times (the daily run rebuilds `caiso_grid_emergencies` first) and conditions-adder-one, congestion-keys (`constraints_binding_hourly` is not on this machine).
- **contracts-quarters** changes the loader (`load.py`, `live_set.yaml`): the page moves after the data machine's next load.
- **play-battery-full** moves the game rules to version 6 and adds migration `040_game_v6.sql`, which a person applies before the deploy (renumber if 040 is taken by then).
- **play-cap-year:** the warehouse's hub real-time maximum was 9,051.55 in 2021 and 5,101.55 in 2022, nothing above 9,000 from 2022 on; the Commission's own date was not read (no web read): a person confirms it before landing.
- **learn-bill-season:** `site/scripts/check-methods-keys.json` not updated (a recorded site read for the desk to rewrite).
- **Branches that clash if more than one lands:** states-twelve-held with states-round-once (same line of `site/app/states/page.tsx`); conditions-screen-hours, alerts-by-notice and adder-one (each adds "decision 8" to `docs/methods/grid_conditions.md`); the three congestion branches (`page.tsx`, `Decisions.tsx`, the method note).
- **Not drawn to HTML** (no memory for node): conditions-alerts-by-notice, states-twelve-held, the AI energy branches, the events branches. One draw each before landing.
- **Existing tests edited to the new behaviour:** `test_audit_states_3`, `test_audit_states_7`, `test_audit_events_5`, `test_session118`, `test_audit_congestion_2`, `test_audit_congestion_3`, and older game tests pinning version 5.

## Rows for the main session

- **Data request:** the comparison rerun on the desk (line 173), command above.
- **Data request:** `docs/state/page_files_states.md` gains one line for states-twelve-held (`generation.last12`) and one for states-capacity-no-pr (line 12, Puerto Rico), if either is chosen.
- **For the page:** the figures above beside each item; the differing figures noted.

## Failures also on clean origin/main (not these branches')

`test_session7534` (kept figures, the network snapshot changes daily), `test_session8901` (16 edition-link checks), `test_session148` (the `/ask` speed test), `test_session7540_compare_read` (61 of 73 checks on both).

## Slips

- Three workers each ran one `python -c` of a few words that only read a file (C, F, H); one typed an empty heredoc that wrote nothing (B). None needed a permission prompt.
- Worker A's `git add -u` picked up `replication/problem_sets/country_inputs.csv`, rewritten by a test run; a second commit restores it, so the branch's net change excludes it. No force push.
- Worker E edited `docs/state/page_files_states.md` once and reverted it before any commit; it is on no branch.
- Every branch's net diff was checked: no `runs/`, `warehouse/output/`, `docs/state/`, queue or instruction file, no em dash.
- No model call, no build, no browser, no table written, no lock, nothing pushed to main or a task branch.
