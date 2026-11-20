# Chain of 20 November 2026, night: sessions 9000 to 9199, data machine (lab-desktop), first window, unattended, until the weekly limit: where the grid is tight and where it is congested (the master plan's seventh tool), and the landing desk for three other windows

machine: data

Written by Claude in chat with Samuel on 20 November 2026 at about 02:10 PST and uploaded by him to `queue/next`. It is not a machine's successor file, and no machine writes a successor to it. Folder: `C:\Users\Shared\Documents\erw`. Model: Opus 5.5. Run it unattended, to its last session. Do not stop to ask questions. Model spend USD 0: call no model API. No heredocs or long inline scripts: use the Edit and Write tools, and put scripts in `runs/`.

## Why this chain

The site now shows the whole country: by region, by balancing authority and by state. What it still cannot tell a reader is the thing a trader, a developer and an AI lab's siting team ask first of a grid: is it tight, and is it congested. The master plan's seventh tool, grid conditions, was to show load against capacity, scarcity and congestion. The pieces the warehouse holds are scattered (California's alerts, a few outage tables), and congestion, the reason power costs more on one side of a wire than the other, is not in the warehouse at all. Several operators publish every binding constraint and its price in the open. This chain builds the tool from them. Samuel reviews over the weekend and wants this machine building until the allowance resets: nothing here waits on a ruling.

## Rules

- **The rules of chain 581 hold word for word** (`queue/done/581-evening-19-november-desktop-states-curtailment-map-layers.md`, and through it chains 505 and 501 and the owner's rules of 16 November), with these changes:
- **Session numbers** 9000 to 9199, each checked free on origin/main and every branch first.
- **Three other windows work tonight** and this window is the only one that lands: the desktop's second window (chain 630, in `C:\Users\Shared\Documents\erw-w2`, `docs/state/landing_request_window2.md`), the old laptop (chain 610) and the personal laptop (chain 620). The desk reads every `docs/state/landing_request_*.md` and every `docs/state/data_requests_*.md` at the start of every session and after each numbered step. This window never kills a process it did not start, never works in the second window's folder, and every site build goes through `scripts/buildlock.py`.
- **`/grid` is not edited by this chain.** The personal laptop reads it in a browser tonight and fixes what it finds. This chain writes files and its own new pages.
- **What exists is read before anything is built** (rule 4): each part starts by listing in the progress file what the warehouse and the site already hold of it. What exists is extended, never built twice.
- **Licenses first.** For each operator and each feed: the robots file and the terms are read before any pull, and `docs/licenses.md` decides what a page may show. A feed the terms forbid to automated readers is not pulled. A feed under a hold is pulled only as far as the hold allows and is drawn as a blank with the hover "license needed". No hold is lifted or worked around. Each such feed is one plain line under "For Samuel's ruling", with the default taken.
- **Add, never change. No default moves. No ruling is taken for Samuel.** Every page stays in review; a new page is in no menu and is listed on `/in-review`.
- **No model of the ERW's own, no advice, no view.** A page says what the operators published.
- **History:** each new table is pulled back as far as the operator's public archive goes, in whole years, newest first, so that a short table is useful at once and deepens as the chain runs. No pull calls a paid service.
- **Never end idle.** After part G, part H, until the weekly limit.

## Restart safety and the progress file

- The first session writes `queue/next/602-resume-chain-601.md`, committed alone and pushed. Its text is the lines between BEGIN and END below, without those two words. A session that takes a resume file first writes the same text under the next number up (to 609). The chain's last session removes it.
- `docs/state/progress_c601.md`: one line a landing, request, feed, table, file or view, its state and session, pushed after each.

BEGIN
# Resume of chain 601

machine: data

Chain 601 was interrupted. First put this same text back in queue/next/ as the next number up to 609, named NNN-resume-chain-601.md, committed alone and pushed. Then read queue/done/601-night-20-november-desktop-grid-conditions.md whole and docs/state/progress_c601.md, and continue chain 601 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
END

## Part A: the desk and the requests

As part A of chain 501, unchanged, at the start of every session and after each numbered step below.

## Part B: the ground (long end 0:45)

For each of the seven grids, and for the large balancing authorities outside them that publish anything of the kind: what the operator publishes in the open about (1) binding transmission constraints and their shadow prices, day-ahead and real time; (2) the congestion part of a hub's or zone's price; (3) generation out of service, planned and forced; (4) operating reserves, scarcity adders and the hours scarcity pricing was on; (5) alerts, watches and emergency notices; (6) flows on its ties at five minutes. For each: the address, the archive's depth, the robots file, the terms, the verdict of `docs/licenses.md`, and what the warehouse already holds. Written to `docs/reviews/grid-conditions-sources-2026-11-20.md`. Parts C to F take the feeds this file clears, the clearest and deepest first.

## Part C: congestion

1. **The tables:** `constraints_binding_hourly` (one row a constraint that bound, an hour, a market: the operator's own name for it, the elements it names, its shadow price, its limit and flow where published) and `price_congestion_hourly` (the congestion part of each hub's and zone's price where the operator publishes the split). Validated, registered, archived, method notes, in the daily run.
2. **The roll-ups and the page file:** for each constraint, the hours it bound and its mean and highest shadow price by month and year; for each hub and zone, the share of its price that was congestion by month; the hour of day against month grid for a chosen place. A contract first, in `docs/state/page_files_conditions.md`.
3. **The view, `/congestion` (new, in review):** the constraints that bound most and cost most, by operator and year; when in the day and the year a chosen constraint binds; the hubs and zones where congestion adds most and takes most off the price; two places side by side. Every figure sourced on hover. A constraint is named as the operator names it, with no guess at where it is on a map.
4. To the done line in the form of `queue/done/303-night-16-november-portable-trackers-done-line.md`, with a cross-check against the operators' own market monitor reports where they print a figure of the same kind.

## Part D: what is out of service

1. `generation_outages` (by operator, by day or hour as published: megawatts out, planned and forced, by source where the operator gives it), and the held table of reactor status joined beside it for nuclear.
2. Page file in the contract; shown in part G's page.

## Part E: reserves, scarcity and alerts

1. `operating_reserves_hourly` (reserves held against the requirement, by product where published), `scarcity_pricing_hours` (the hours an operator's scarcity adder was above zero, and its size), and `grid_alerts` (every alert, watch and emergency notice an operator has issued, with its kind in the operator's words, its start and its end), California's alert history folded into it without changing `/grid/caiso/alerts`.
2. Page files in the contract.

## Part F: the ties at five minutes (files only)

For each operator whose five-minute tie flows the ground cleared: a table of the last thirty-five days at five minutes and a page file of the last day, in the contract, for a later "now" on the Grid map. `/grid` itself is not edited here.

## Part G: one page, "Grid conditions" (`/conditions`, new, in review)

For a chosen operator, now and through its history: demand against what was available, reserves against the requirement, megawatts out of service, the constraints binding, the alerts in force, each as its own strip on one time axis, so that a tight day reads at a glance. Pick any day in history; pick one of the nine events of `/events` and the page opens on it. Two operators side by side. An operator or a strip that a license holds is drawn blank with "license needed". Charts that answer to the mouse, every figure sourced on hover, downloads as the other pages have them. To the done line, with a tour stop held by its flag.

## Part H: after part G, until the weekly limit

- The history of each new table deepened, a year at a time, oldest year last.
- Each new view read as its reader (five real cases: a power trader on a congested day, a developer choosing a node, a utility planner after an emergency notice, an AI lab's siting analyst, a student of one storm), every gap a numbered row, every fault fixed at its cause with a test.
- Every page file written tonight traced to its rows by `check-values`.
- Part A after each.

## The last session

- `docs/state/note_2026-11-20_data_c601.md` in short bullets: every landing with what a reader now sees; each new page with its address and what to click to see it; each table with its operators, span, rows and license; every feed not pulled and why; what waits for Samuel with the default taken, in plain words.
- The resume file removed; `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. No file: part H goes on.
