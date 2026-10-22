# Chain of 23 October 2026: sessions 700 to 721, code machine (old laptop), unattended: "Where can a large load go", the All grids tab

machine: code

Twenty-two sessions for the old laptop (`samueloldlaptop`, C:\Users\lossa\Documents\erw), written on the owner's instruction on the night of 22 October. Model: Opus 5.5, high effort. Goal: `/cost-of-power` ("What a datacenter pays") answers, for one chosen region, what a load pays, when it connects, how clean the power is. It gets a second tab, **All grids**, that answers the same questions for every grid, hub and zone the warehouse holds, and every ERCOT node, in one sortable table, with the same model (the same library functions, the same keys), so the two views can never disagree. No new page, no second model. The load is a large load, with four profiles: datacenter (the default: flat, 0.90, never curtails), flexible compute (curtails at the four ERCOT peaks and above a strike price), electrolyzer (runs below a strike, 0.40 to 0.70), heavy industry (0.80, interruptible hours only). A profile sets three inputs (load factor, curtailment rule, interruptible) and nothing else. What makes the tab worth a lab's time, in this order: the ERCOT node set (888 nodes: hub plus basis plus the 4CP charge, firm against curtailing, from the actual peak intervals); time to connect by grid (queue durations, the large-load rules and waits); then the rest.

Session numbers 700 to 721 are this chain's; 722 to 749 are for the next chain this machine writes for itself; the personal laptop holds 800 to 849; a data-machine chain that numbers itself skips 700 to 849. A number found taken when a session starts is skipped upward inside 700 to 749 and said so.

What the warehouse holds, and what the tab says where it does not: node prices only for ERCOT (`node_basis_daily`, 888 nodes, public; `ercot_node_prices_hourly` internal); hub and zone prices for CAISO, NYISO, ISO-NE, SPP and MISO (`iso_dam_hub_prices`, `iso_rtm_hub_prices`, `iso_hub_prices_history`; ISO-NE zone history internal); PJM prices held; capacity prices for PJM, ISO-NE, MISO and NYISO held (`iso_all_capacity_prices`, `pjm_rpm_capacity_prices`: computed, keyed, drawn as "license needed" in place, session 408's rule); no capacity market in ERCOT, CAISO and SPP (said so, not blank); transmission charges held for ERCOT only (`ercot_4cp_intervals`); `large_load_rules` public, `large_load_waits` internal, `ercot_large_load_status` and `nyiso_load_queue` public; queues (`lbnl_interconnection_queue`, `iso_queue_statistics`, the seven ISO queue tables); headroom (EIA-930 demand, `eia860m_planned_generators`, `eia_state_capacity_annual`); carbon (`egrid_power_plants`, `epa_ghgrp_power_co2`); utilities (`eia861_utility_sales`, `eia861m_utility_sales_monthly`). Not held, never invented: large-load tariffs outside ERCOT, utility service territories, reserve margins by zone, connection timelines by utility; the data machine's chain (`queue/next/043-...`) pulls them, and session 718 wires in what has landed. A cell the warehouse cannot fill says why in its hover tip (not held, license needed, no such market), in the words of `docs/brand.md` section 7; no visible grey text (the owner's rule of 14 October). No session writes warehouse data or makes a web request.

Read first: `docs/state/review_2026-10-23_code.md`, `docs/reviews/roadmap-v4-draft.md`, `docs/reviews/research/deep-research-report.md` (what labs hire for), the datacenter tool's note under `docs/methods/`, `docs/brand.md`, `docs/tooling.md`, `queue/done/034-night-22-october-code.md` (never redo a session of it). Files this chain owns: `site/app/cost-of-power/`, `site/lib/cost.ts`, `site/lib/datacenter*.ts`, `site/lib/siting*.ts` (new), `docs/methods/siting.md` (new), `docs/reviews/siting-*.md`; the personal laptop's chain owns `warehouse/news/`, `warehouse/analysis/`, `site/app/digest/`, `site/app/roundup/` and touches none of these.

## Rules for every session

Every python command uses `.venv\Scripts\python.exe` (a worktree uses the main checkout's). Precheck first (exit 1: stop). Unattended: never stop to ask, never wait for a time of day; any wait over 20 minutes (a deploy, a watcher, an agent, a lock) is stopped and the step done directly or left under "To finish"; reversible choices under "Decisions made without you", irreversible ones under "For Samuel's ruling", undone, one item a line so `/internal/waits` lists it. One Claude Code session on this machine at a time. Each session works in its own git worktree beside the main checkout, on its own `wip/<N>-allgrids` branch cut from origin/main, with its own `npm ci` and `MSYS_NO_PATHCONV=1` for page paths in Git Bash; the worktree is removed once its branch has landed. THE DATABASE: `python scripts/db_probe.py` as its own command before a build; exit 1 means no build yet, and the session does its code, tests and documents first and probes again at its end. A build over 30 minutes is stopped and the session goes to `wip/` with "To finish". One heavy process at a time: `python scripts/buildlock.py acquire <who>` and `release <who>`; `python scripts/duty.py beat` before each build. Landing on main when green through the full gate: `python scripts/land_check.py --ref wip/<N>-allgrids`, then the snapshot before as its own command, the push to `task/`, the snapshot after once production shows the new commit, `compare`, every difference listed and marked expected or not. No landing between 14:00 and 16:15 UTC (the daily run and the data machine's prices); a session green in that window beats every 20 minutes and lands after, or leaves the push under "To finish" for the next session, which lands it first. Sessions may land together in one push. Model spend USD 0 for the chain (no test reaches the model's API). No warehouse data written; no web request. Screenshots at 1280 and 390 before and after for every page touched, under `docs/brand/review-<N>/`. tokens.css and the shared components only for style. No default figure of the existing tab moves (check-values proves it, every session). No em dashes anywhere. Reports as the chain of 20 October's: `archive/sessions/SESSION_<N>_REPORT.md`, short bullets, "Read these first", "What to review" with the full address and click-by-click steps, checks with their exits, the landing and its comparison, "Decisions made without you", "For Samuel's ruling". Last step of the last session: the note, the next file, then the queue step.

Every figure of the tab is a check-values key (`allgrids_<column>_<row>`), drawn from a library function with its table, filter and vintage; every column has a one-line source and method in its hover tip. Every assumption shows its default in a grey hover tip with its source and is editable in place; the left box holds every input, the right side only results; long input lists are collapsible. Scenario A drives the headline; A and B compare two rows side by side. The tab expresses no view and ranks nothing by a score: it sorts by the column the reader chooses and says what the sort is.

## Session 700: the inventory, the keys, the tab and the profiles

Long end 2:00. Read `/cost-of-power` and its libraries end to end. Write `docs/methods/siting.md` v0: the eight columns (energy, transmission and 4CP, capacity, time to connect, headroom, carbon, utility, and all-in USD per MWh where the first three are each held or each zero by market design), each with its table, filter, vintage, license, the function of `site/lib/` that already computes it, and the cell's words where it cannot be filled; the four profiles with their three inputs, each default's source. The rows: every hub and zone the price tables hold, grid named; the ERCOT nodes of `node_basis_daily` as a second row set behind a toggle. Build the tab: the existing page's input box gains the profile dropdown (datacenter selected), the tab shows the rows, the toggle, the column heads with tips, and no number but the row count (a key). A test that the row list equals the tables' distinct hubs, zones and nodes; check-values on the existing tab unchanged. Land.

## Session 701: energy, every row

Long end 2:00. The trailing-twelve-month average day-ahead price (real-time beside it where held), USD per MWh, flat, for every row; the last whole month and year in the tip; ERCOT nodes as hub plus basis from `node_basis_daily`, said so; PJM "license needed". The figure for each grid's main hub must equal the existing tab's figure for that grid under the same window: one function, one test. A twelve-month sparkline in the cell on hover (the shared chart). Keys. Land.

## Session 702: the profiles' math

Long end 2:00. The profile's load factor, curtailment rule (none; the four ERCOT peaks; a strike in USD per MWh) and interruptible flag reshape the energy column: the time-weighted price over the hours the load runs, from the hourly tables where held (`iso_hub_prices_history`; ERCOT nodes use the daily table and say "daily"), and the hours lost to curtailment as a second figure in the tip. The all-in column draws when its parts are held or zero by design. Tests on fixtures for each profile. Keys. Land.

## Session 703: transmission and the four peaks

Long end 2:00. ERCOT: the 4CP charge for the load from `ercot_4cp_intervals`, firm (the load's full share of the four intervals) and curtailing (the load off for those intervals: about zero, computed, not assumed), with the method the existing tab uses if it has one; if the TSP rates are not held, the cell says "rates not held" and the gaps file lists them. Every other grid: "not held", the tip naming the utility's large-load tariff as what would fill it. Start `docs/reviews/siting-gaps.md`: one row a cell the warehouse cannot fill, with the source that would. Land.

## Session 704: capacity

Long end 1:30. PJM, ISO-NE, MISO, NYISO: the latest cleared capacity price for the zone, converted to USD per MWh at the load factor (interruptible load pays less; the tip says the rule), computed and keyed, drawn as "license needed" in place. ERCOT, CAISO, SPP: "no capacity market", one line of why in the tip. Land.

## Session 705: time to connect

Long end 2:00. Two figures a row: the median months from queue entry to commercial operation for projects completed in the last three years in the grid (`lbnl_interconnection_queue`, `iso_queue_statistics`); and the large-load path: the grid's rule for loads above 75 MW (`large_load_rules`), the faster path for a controllable load where the rule gives one (ERCOT), and the observed wait where held (`large_load_waits` internal: computed, "license needed"; `ercot_large_load_status`, `nyiso_load_queue` drawn). The tip names the rule's date and document. Keys. Land.

## Session 706: headroom

Long end 2:00. Demand growth, last twelve months over the twelve before, from EIA-930 sub-region demand (`site/lib/demandgrowth.ts` or the Grid tool's function); planned generation with a signed interconnection agreement in the next twelve months, MW, from `eia860m_planned_generators`; the grid's last-year peak against installed capacity where a state maps to one grid (else said so). Reserve margin by zone not held: said so. Keys. Land.

## Session 707: carbon

Long end 1:30. The generation-weighted CO2 rate (kg and lb per MWh) of the eGRID subregion the row sits in, from `egrid_power_plants`, subregion and year in the tip; two subregions weighted where a zone spans them. The electrolyzer profile shows the rate over the hours it runs where hourly carbon is held (`carbon_intensity_hourly`), else annual with "annual" in the tip. A test against three subregion rates the table reproduces. Keys. Land.

## Session 708: the utility

Long end 2:00. From `eia861_utility_sales`: the largest utility by industrial sales in the row's state (territories not held: the tip says so and the gaps file lists them), its industrial revenue per MWh and sales growth, last year held. ERCOT nodes: the TSP where the node tables name one. Keys. Land.

## Session 709: the ERCOT node set

Long end 2:00. The toggle's second row set: 888 nodes in a virtual list, each with hub plus basis, the 4CP charge firm and curtailing, the zone and settlement hub, the TSP; sortable by any column; no figure drawn twice. The build must not add more than one read for the set. Screenshots. Keys. Land.

## Session 710: the screen, A against B

Long end 2:00. Sort by any column (named above the table; default alphabetical by grid then row), filter by grid, load band and "held columns only", the sort and the inputs kept in the address so a reader can send the screen. Two rows picked compare side by side in a panel, every column and the difference, and the year's all-in cost in USD and months to connect for the load set, in the existing tab's A and B form (two columns, succinct, no verdict); A drives one headline line, every figure a key, drawn only when held. Land.

## Session 711: node detail

Long end 2:00. A node row opens a panel: basis distribution over the last year (the shared chart), its 4CP exposure, the nearest planned generation by county (`eia860m_planned_generators`), the county's transmission projects from `texas_transmission_matrix` (internal: computed, "license needed"). Keys. Land.

## Session 712: the method note and the replication

Long end 2:00. `docs/methods/siting.md` v1: every column's formula, table, filter, vintage, license; the four profiles; the decisions block (each choice, dated, reversible or not); the limits. `warehouse/replication/siting.py`: from the live set's anon key only, reproduces every key for three rows and three nodes under each profile and prints them beside the page's figures; run in a new virtual environment in the scratchpad, command and exit code in the report. The note is internal, linked from `/data/methods` in review. Land.

## Session 713: the gaps, complete

Long end 1:30. `docs/reviews/siting-gaps.md` finished: one row a cell the warehouse cannot fill, by grid, the source that would fill it, its license as far as the registry and `docs/licenses.md` say without a web request, the connector it resembles. `/internal/siting-gaps` in review reads it at build time. "For Samuel's ruling": the five gaps that would change the tab most. Land.

## Session 714: 390 pixels, accessibility, links, tips

Long end 2:00. On a build: the tab at 390 by 844 (table scrolls in its container, input box collapses); AccessLint's unattended scan at 1280 and 390, mechanical violations fixed in the shared components; `site/scripts/check-links.mjs`; every tip reachable by keyboard. Counts before and after. No figure moves. Land.

## Session 715: the brand pass

Long end 2:00. The tab restyled to `docs/brand.md` (Source Serif 4 display, IBM Plex Sans text, Plex Mono numbers, white page with fog panels, FT-like charts): structure, density and every number kept; tokens.css and the shared components only; screenshots before and after under `docs/brand/review-715/` for Samuel to rule from. Land.

## Session 716: the reads

Long end 1:30. Time every read the page makes on a build (session 580's wrapper, on for the run); the page's build under 90 seconds on this machine; the twenty slowest listed; an index a read needs goes into session 580's unapplied migration file, not applied. Land.

## Session 717: the lab's path, walked

Long end 2:00. `docs/reviews/siting-path.md`: the questions an infrastructure lead at a lab asks when siting a gigawatt (from the research reports, cited), the click-by-click path on the tab that answers each, walked on a build in the internal view; what the page showed, whether it answered, what broke; fixes that need no ruling made, the rest listed. Screenshots of each step. Land.

## Session 718: the data machine's tables, wired in

Long end 2:00. `python scripts/sync.py`, then read `coverage.csv` for tables added since 23 October that fill a row of the gaps file (large-load tariffs, service territories, timelines, substations, lines): each one there, public or internal, wired into its column by the note's rule, keyed, checked, the gaps file updated. None there: said so, and the energy column gains a three-year window beside the twelve months. Land.

## Session 719: the tracker joins the tab

Long end 2:00. Each facility of the datacenter tracker (`/datacenters`) links to its grid's row on the tab with the facility's MW set as the load, in the address; the tab's A and B panel can take a tracked facility as A. The join is by grid and, for ERCOT, by the node the tracker names where it names one. Keys unchanged. Land.

## Session 720: the research card

Long end 1:30. One card under `/research` in review, in the findings pipeline's format (`site/app/research/card/`): under the datacenter profile, where a 1 GW load pays least and most per MWh among rows with every cost column held, and the range of months to connect; one shared chart with its source line; no verdict. Written, never posted or sent. Keys; check-findings. Land.

## Session 721: the note, the next file, and the queue

Long end 1:00. `docs/state/review_2026-10-24_code.md`: one line a session with its branch, address and screenshots, every decision made without Samuel, every item waiting for him (the map, the migration, the five gaps, the brand screenshots), the state of `queue/next` for this machine. Then `python scripts/chain_queue.py list`: if nothing waits for this machine, write the next file before the queue step, at least twenty sessions, machine: code, numbered 722 to 749 (said so), same goal: the open items of this chain's reports, the walk of session 717, the data machine's tables as they land, the trader's and the utility's path through the same tab; commit and push it to main; say so in the note. Push, then `python scripts/chain_queue.py next`.
