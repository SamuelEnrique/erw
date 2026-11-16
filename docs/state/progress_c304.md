# Progress of chain 304: nine more tools to the done line, then each read as its reader (sessions 7500 to 7599, samueloldlaptop)

Energy Research Warehouse (ERW). The chain file: `queue/done/304-day-16-november-oldlaptop-done-line-economics.md`. One line a tool and part, its state and session. This file, the claims, the data requests, the browser reads wanted and the landing request rows are on main; the work is on wip branches, each with its worktree beside the main copy. Model spend: USD 0.

States: `done` with the commit, `needs the key` with the cost, `ruling` with the default taken, `waiting` with what for, `open`.

| Branch | Worktree | Holds | Landing request row |
|---|---|---|---|
| `wip/7500-done-line` | `erw-7500` | the base of every tool's branch: `wip/7200-large-load` (landing row 15, not landed; it holds the tools that draw a page to HTML without a build) with origin/main merged at `a4ba0dbd5` | none of its own |
| `wip/7501-contracts` | `erw-7501` | tool 1, the contracts page | 18 |
| `wip/7502-severance` | `erw-7502` | tool 2, the severance tool | 17 |
| `wip/7503-shoulder` | `erw-7503` | tool 3, the shoulder hours | 19 |
| `wip/7505-battery-awards` | `erw-7505` | tool 5, the battery awards page | 20 |
| `wip/7506-impact` | `erw-7506` | tool 6, the forecast tool | 21 |
| `wip/7507-peak-premium` | `erw-7507` | tool 7, the ERCOT peak premium explorer | 22 |
| `wip/7508-demand-growth` | `erw-7508` | tool 8, the demand growth explorer | 23 |

## The ground (session 7500)

| Step | State | Session |
|---|---|---|
| Queue step by name, the precheck, fetch, memory and disk | done: taken at `d0a6e9ad4`; precheck passed; 1.9 GB of memory free, 85 GB of disk | 7500 |
| Resume files of this machine in `queue/next/` | done: none was there (310 is the data machine's, 350 the portable laptop's) | 7500 |
| The resume file `queue/next/340-resume-chain-304.md` | done `a4ba0dbd5` | 7500 |
| This progress file | done (this commit) | 7500 |
| `docs/state/done_line_claims.md` and row 1 of `docs/state/data_requests_done_line.md` | done before this chain: both written by session 7600 of chain 305 (`e5ba04eb4`, `df15207e5`), read here, nothing to add | 7500 |
| `docs/state/browser_reads_wanted.md` | done (this commit): the file started, no row yet | 7500 |
| The before snapshot of the live pages (rule 8: a push to main deploys) | done: `c304-before`, 25 pages, 0 failed, 10:35 UTC | 7500 |

## Part A: the done line, one tool a session

| # | Tool | State | Session |
|---:|---|---|---|
| 1 | `/contracts` | done `118e668fa` on `wip/7501-contracts` (landing row 18): the note `docs/methods/contracts.md` (the name, price and megawatts rules written out as patterns); the replication from the two source tables, 2,539 of 2,615 figures inside the tolerance and 76 named (one data fault: the megawatts view's "place by contracts" is ranked another way than the largest view's, data requests row 4), 785 of 785 words the same; the cross-check (filers 3,704 and 4,010 against FERC's 3,672 of Order No. 917, a quarter and four quarters earlier; the megawatts ceiling equals EIA-860M's largest station; nothing published stands against the counts by product or the largest parties; `www.ferc.gov` answered 403 and was not worked around); the decisions fold (19 choices); 13 faults: 5 site fixed, 1 note completed, 1 data machine, 6 rulings; browser reads rows 5 to 8. No party's name or row of the internal table is committed | 7501 |
| 2 | `/severance` with `/severance/finder` and `/severance/lease/real` | done `c247ad4e1` on `wip/7502-severance` (landing row 17): the note completed; the replication 612 of 612 figures (the calculator at its default and 46 named cases, the Lease tab's sample, four real leases by totals only); the cross-check (Texas's rates and 20 certified periods equal the Comptroller's to the cent; the base rule on EIA's production is 22 to 23 percent above the Comptroller's oil tax collections, said in the note); the decisions fold (14 choices); 8 faults: 2 site fixed, 3 data machine (data requests rows 2 and 3), 3 rulings; browser reads rows 1 to 4. Not done: the finder's replication (its three files are not on this machine: data request row 3); Louisiana's and New Mexico's collections | 7502 |
| 3 | `/shoulder` | done `7820907a4` on `wip/7503-shoulder` (landing row 19): the note `docs/methods/shoulder.md` and the table's note completed; the replication 20,633 of 20,634 figures over 193 views (1 named, a rounding edge), and 22,092 of 22,092 values of the table recomputed from EIA-930's hourly workbooks for ERCOT and California (the tool holds no price: its table is built from hourly demand, solar, wind and battery output); the cross-check, 12 rows (the fleet is below each market monitor's count at the end of 2025: ERCOT 13,909 MW against "more than 17,000 MW", California 15,760 MW against "over 17 GW", not adjusted, a ruling; California's 2024 curtailment and fleet match EIA's published figures; nothing published stands against the shoulder's length); the decisions fold (18 choices); 16 fault rows: 9 fixed (7 on the page, 2 in the note), 2 data machine (data requests rows 5 and 6), 3 rulings, 2 not faults; browser reads rows 9 to 11. Not done: California by CAISO's own data and California's battery output were not recomputed from hours (2,713 rows stand on the table) | 7503 |
| 4 | `/battery/customer` | open | 7504 |
| 5 | `/cost-of-power/battery/awards` | done `73837e331` on `wip/7505-battery-awards` (landing row 20): the note `docs/methods/battery_awards.md` and two tables' notes completed; the replication: the page 307 of 307 figures, the file `battery_awards_beside.json` 24 of 24, and every row of the two monthly tables recomputed from ERCOT's disclosure rows and the hub's real-time prices, 297 of 297 over nine months (a month's dollar sum agrees inside three cents, named in the script); the cross-check, 8 rows (the fleet 16,392 MW in December 2025 against the market monitor's "more than 17,000 MW"; 21,365 MW in July 2026 against EIA-860M's 18,070 MW; nothing published stands against revenue per kW for these months, the gap's three parts or the node spread; ERCOT's own documents not asked for, its robots file disallows the paths); the decisions fold (15 fixed choices); 9 fault rows: 1 site fixed, 2 notes completed, 1 data machine (data requests row 7), 5 rulings; browser reads rows 12 to 14 | 7505 |
| 6 | `/impact` | done `946db9195` on `wip/7506-impact` (landing row 21): no page code changed (its 23 faults were not read again); the replication 7,593 of 7,593 figures over 17 addresses (the default, ten real planned projects of EIA-860M in eight states, the six addresses the value checker reads), and 414 of 414 compared rows of `forecast_tool_parameters` equal the parameter files; the notes completed (`forecast.md` section 12); the cross-check, 20 rows (NREL's JEDI II paper of 2006, Colorado wind, 680 MW: construction jobs 2,605 against 1,618, operating jobs 140 against 259; Nevada's own fiscal notes for Lone Mountain Geothermal, 36 MW: property tax after the abatement, first year, USD 876,631 against 876,653); 12 fault rows: 0 site, 3 note completed, 2 data machine (data requests rows 10 and 11: Utah's USD 966 credit is stored as a deduction, so Utah's income tax is drawn 18 to 31 percent too high), 7 rulings; browser reads rows 15 to 19. Said by the session: it had read the page's library before writing the replication, so the replication is not blind; `docs.nlr.gov`'s robots address redirects to a page of `www.nlr.gov`, whose robots file allows everything, and that was taken as no rule (for Samuel's ruling) | 7506 |
| 7 | `/explore/ercot-peak-premium` | done `b35e64e9a` on `wip/7507-peak-premium` (landing row 22): the note completed with a section for the tool as a reader meets it; the replication 550 of 550 views and 24,786 of 24,786 figures, and 25,704 of 25,704 rows of the two tables recomputed from the 15-minute prices of all six hubs (2,469,864 hub-intervals); the cross-check (the market monitor's load-weighted real-time average for 2020 to 2024 against the plain mean at the hub average: 12 to 26 percent lower here, the years in the same order; its "hundreds of hours" at or below zero in 2025 against 239.75 hours here; nothing published stands against the peak block's spread, the quartiles or any monthly figure; the 2025 report's Table 1 not read, this machine's PDF reader does not decode its font); the decisions fold (11 choices); 14 fault rows: 5 site fixed, 2 data machine (data requests rows 12 to 13: both tables last computed on 21 October 2026), 4 rulings, 3 not faults; browser reads rows 20 to 23. For another tool: the ERCOT tab of `/prices` draws the same tables and may draw a whole-dollar price without decimals (not read here; the desktop's tool) | 7507 |
| 8 | `/explore/demand-growth` | done `66e294497` on `wip/7508-demand-growth` (landing row 23): the note completed ("The rule in full" and a section for the tool); the replication 35,936 of 35,936 slots of text on 315 views (2,237 differed before the fixes) and 770 of 770 growth figures; 24,060 of 24,062 rows of the table recomputed from EIA's hourly workbooks of 3 October (the two are EIA's own revision; 54 rows need the workbooks of 5 November, which the data machine holds); the cross-check (the Lower 48's growth 2019 to 2025 is +7.03 percent against +7.05 for EIA's retail sales; fourteen highest hours equal EIA's article of 15 October 2026; ERCOT +27.22 against Texas sales +24.20; CAISO +4.45 against California sales -2.96, opposite signs, the cause not established: the one figure to know before standing behind the page; the tool holds no forecast, so the published forecasts are listed for scale only); the decisions fold (16 choices); 19 fault rows: 8 fixed (6 site, 2 note), 2 data machine (data requests rows 14 and 15), 1 in a shared explore file (not changed), 6 rulings, 2 not faults; browser reads rows 24 to 27. For Samuel's ruling among them: PJM's Load Forecast Report is printed "For Public Use" and its file properties carry a "Confidential" label; its figures are cited | 7508 |
| 9 | `/explore/interconnection` | open | 7509 |

## Part B: each tool read as the reader it is for

| # | Tool | State | Session |
|---:|---|---|---|
| 1 to 9 | this machine's nine tools, in the table's order | open | |
| 10 | `/cost-of-power/battery` | open | |
| 11 | `/cost-of-power/seller` | open | |
| 12 | `/cost-of-power` | open | |

## Part C: the other machines' tools read, if parts A and B are done and no new file waits

| Tool | State | Session |
|---|---|---|

## The last session

| Step | State | Session |
|---|---|---|
| The pack `docs/reviews/done-line-pack-oldlaptop-2026-11-16.md` | open | |
| The note `docs/state/note_2026-11-17_oldlaptop_c304.md` | open | |
| The resume file removed; the queue step | open | |
