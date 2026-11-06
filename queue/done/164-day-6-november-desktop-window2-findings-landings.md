# Chain of 6 November 2026: sessions 3000 to 3023, lab-desktop, second window, unattended, about fifteen hours: the findings hunt over the whole warehouse, and the landing service for the laptops

machine: lab-desktop-window2

Written by the owner with Claude in chat on 6 November 2026 (Friday, about 03:00 Pacific) and uploaded to `queue/next` by the owner. The `machine:` line names no role and no machine, on purpose: the chain worker and the desktop's first window never take this file; the owner starts it by name in a SECOND Claude Code window on the desktop, beside the chain the first window runs (160, 162 and their successors). It takes sessions 3000 to 3023; session 3000 checks each is free on origin's main and on every branch, skips a taken one upward and says so. Model: Opus 5.5, high effort.

## Why this chain (the owner's words)

The warehouse now holds about 230 tables, the periodicals and Ask read a few dozen of them, and the findings hunt (the owner's ruling of 12 October: automated, it writes everything; a finding appears on /research only after he approves it at /internal/findings, having run the Stata himself; nothing is ever posted or sent by a machine) has run only on the scanner's statistics. Nobody has read the whole warehouse for what it says. This chain does: family by family, every claim with its figure, its chart, its tables and rows, its strength, its reproduction in Python and Stata, written as drafts for the owner's approval and nothing more. The desktop has the memory the laptops lack, so this window also lands what they build, between hunts.

## Rules for every session

The rules of `queue/done/157-day-6-november-data-derived-tables-landings.md` hold word for word, except: this window writes NO warehouse table and takes NO data lock (its outputs are the findings' drafts and documents; a finding that needs a derived table names it for the first window's chain through the note); it never runs the daily run or the backfill; and it shares the machine with the first window, so every build goes through `scripts/buildlock.py` (the gate takes it itself) and this window never kills a process it did not start. Also:

- **Never stop.** No session ends by stopping to ask; any wait over 20 minutes is stopped and the step done directly; the weekly limit is the only stop.
- **Session 3000 writes the next file first** (`queue/next/<first free number at or above 166>-day-7-november-desktop-window2-continued.md`, `machine: lab-desktop-window2`, at least fourteen sessions: this chain's unfinished steps, then the families not yet hunted), commits it alone and pushes it; session 3023 updates it. **This window's queue step is by name** (`python scripts/chain_queue.py next --file <that file's name>`), never bare `next`, so this window never takes the first window's files.
- **Branches:** `wip/<N>-findings` cut from the newest unlanded branch of this chain, 3000's from `origin/main`; `origin/main` merged before work.
- **The landing service.** Sessions 3004, 3008, 3012, 3016 and 3020 each begin by reading, on origin's main, `docs/state/landing_request_portable.md` (the personal laptop's) and `docs/state/landing_request_oldlaptop.md` (the old laptop's second window's): every branch named that is not an ancestor of main is merged with `origin/main` in its own worktree, its suite run, landed through `scripts/land_check.py` with the task name and port the file gives, the file's row marked landed with the commit, the branch deleted once an ancestor. A conflict is resolved by taking the laptop's side and running the suite. The snapshots before and after are the only touch of production; never between 14:00 and 16:15 UTC.
- **A finding** is one sentence that states a fact of the energy system with its figure, unit, geography, period and comparison basis; then its chart (hover with values, the brand's chart style as `docs/brand.md` has it, drawn by the repository's chart code); the tables and rows it rests on (keys the tracers read); its strength (the scanner's robust standard deviations or the test the family's method names); its limits in one sentence; `reproduce.py` and `reproduce.do` (the owner's Stata rules: no line continuation, one empty line between commands outside loops and none inside, every variable destringed with `force`) that recompute the figure from the public downloads. A finding from a held table is drafted with "license needed" on the figure and the table named; a finding the data cannot support is not drafted. No finding states a cause; it states what the data show and names the comparison. No point of view.
- **The drafts** go where the findings hunt already writes (`scanner_drafts`'s store, or `docs/findings/<family>/<slug>.md` with its chart beside it if the store takes only the scanner's form; the session says which and why), each marked draft, never approved; `/internal/findings` lists them; nothing reaches `/research`, nothing is sent.
- **The model** (Opus through the repository's own client, the owner's key): USD 3 a session, USD 35 the chain, every call's cost in the report; the model proposes candidates and writes sentences; every figure in a sentence is computed by code from the tables, never by the model.
- **The report** in chain 147's form, short bullets, "Decisions made without you", "For Samuel's ruling". No em or en dash in any file.

Read first: `docs/roadmap.md`'s rulings of 12 October on the findings; `warehouse/analysis/` (the scanner, `run.py`, the templates, `findings/daily_chart.py`), `docs/methods/` for each family, `warehouse/metadata/coverage.csv`, `docs/state/note_2026-11-07_data_c157.md`, `docs/brand.md` (charts), `CLAUDE.md`.

## Session 3000: the next file, the ground

Long end 0:45. The next file. Then: the findings hunt as it exists (where drafts live, how `/internal/findings` reads them, what the scanner flags today and how many drafts stand), the families of tables with their row counts, licenses and newest dates, written to `docs/reviews/findings-hunt-plan-2026-11-06.md` with the order below and the questions each family can answer.

## Sessions 3001 to 3003: prices

Long end 1:30 each. Pulls: none but the model under the cap. The ISO hub prices (day-ahead and real-time, the seven grids where public), the spreads (day-ahead to real-time, hub to hub, the spark spread against Henry Hub at the standard heat rate, the ERCOT node basis where public), the fuel closes (Henry Hub, regional gas, WTI, Brent, TTF, JKM), carbon. Candidates: the hours and months where a grid's price shape changed (the midday trough, the evening peak, the shoulder hours the owner named), the spread's trend by year, the days that carry most of the year's spread value, the regional gas basis moves. At least ten drafts a session, the ten best by consequence kept, duplicates folded.

## Session 3004: the landing service, then demand

Long end 1:30. The landing request files first. Then EIA-930 demand and the sub-regions (`subregion_demand_growth`): the grids and sub-regions whose peak grew fastest by year, the weekday and hour of the new peaks, the winter peaks that now rival summer, the US48 peak against its year before.

## Sessions 3005 to 3007: generation and the pipeline

Long end 1:30 each. The generation mix by grid and hour (EIA-930), curtailment where held, the EIA-860M pipeline and its monthly moves (`generator_pipeline_by_grid`), EIA-923 back to 2001, the nuclear fleet (`nuclear_fleet_status`): the shares that crossed a line (solar's midday share, gas's evening share, coal's exit by grid), the pipeline's slippage by fuel and grid, the reactors' outage days against their decade, the fleet's uprates.

## Session 3008: the landing service, then gas

Long end 1:30. The landing request files first. Then `gas_balance_weekly`, storage by region, production, consumption, LNG feedgas, the regional hubs: the weeks outside the five-year range, LNG's share of demand by year, the regions whose storage position diverged, the basis blowouts.

## Sessions 3009 to 3011: queues, deals and datacenters

Long end 1:30 each. `iso_queue_snapshot_summary`, the ISO queues held, `energy_deals`, `datacenter_projects` (and the personal laptop's tables if landed): the queue's withdrawal rates by fuel and grid, the months to in-service by year, the deals' disclosed prices by technology and year, the AI-power deals' MW by quarter, the facilities' MW by grid against each grid's peak; a finding from a held queue carries "license needed".

## Session 3012: the landing service, then tariffs and policy

Long end 1:30. The landing request files first. Then `utility_large_load_tariffs`, `large_load_connection_rules`, `policy_actions` and the policy reads, the Texas delivery charges and 4CP: what a 500 MW load's delivery charge spans across the utilities held, which rules state a duration and which do not, the policy actions scored highest by month.

## Sessions 3013 to 3015: oil, products and the world prices

Long end 1:30 each. The petroleum supply and disposition, crude imports by origin, the PADD series, retail products, the IMF PortWatch transits (the Strait of Hormuz among them), Brent against WTI, OPEC: the crack spreads by year, the import origins that moved, the transit counts against price, the products' retail against crude.

## Session 3016: the landing service, then the cross-family findings

Long end 1:30. The landing request files first. Then the findings that need two families: the spark spread against the gas balance, the queue's completions against the pipeline's online MW, datacenter MW against sub-region peak growth, nuclear outages against the hub prices of their grid in those weeks.

## Sessions 3017 to 3019: the drafts checked

Long end 1:30 each. Every draft of this chain read against its tables by a second pass that recomputes the figure from `reproduce.py` in a clean worktree (never from the draft's own numbers): a draft whose figure does not reproduce within its stated tolerance is corrected or removed; every chart's hover checked on a local build of the pages that show them (`/internal/findings`); every draft's limits sentence present; the tracers (`check_values` where a page draws a draft's figure) pass. The count of drafts by family, before and after the check, in the report.

## Session 3020: the landing service, then the ranking

Long end 1:30. The landing request files first. Then every draft ranked by consequence, novelty and strength (the rubric written in the plan file, with the reasoning), the ranking written to `docs/reviews/findings-ranked-2026-11-06.md` with the twenty the owner should read first, each with its one sentence, its figure and its family; nothing approved.

## Session 3021: the Stata files, read

Long end 1:00. Every `reproduce.do` of this chain read line by line against its `reproduce.py` (the owner runs Stata; this machine cannot): the same steps, the same figure named at the top as the expected value, the owner's Stata rules kept; a fault fixed.

## Session 3022: the records and the clean-up

Long end 1:00. The package's and the site's records rebuilt if this chain changed what they read; worktrees of landed branches removed; the plan file's every family with its state.

## Session 3023: the note, the next file, the landing, the queue

Long end 1:00. `docs/state/note_2026-11-07_desktop_window2.md` (chain 147's note's form: the drafts by family with their counts, the twenty to read first, the landings done for the laptops, what did not finish and why, the decisions made without the owner, the questions for his ruling, the cost); the next file updated and pushed alone; this chain's branch landed through the gate (never between 14:00 and 16:15 UTC); `python scripts/chain_queue.py next --file <the next file's name>`, and run the file it prints the same way.
