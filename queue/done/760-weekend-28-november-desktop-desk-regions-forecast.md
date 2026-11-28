# Chain of 28 November 2026, weekend: sessions 11200 to 11399, data machine (lab-desktop), one window, unattended, nonstop until the weekly limit or until Samuel stops it: the desk for the two laptops, the data for "where can the next gigawatts go", the energy equities kept current, and the ERW forecast's open list

machine: data

Written by Claude in chat with Samuel on 28 November 2026 at about 02:00 PST and uploaded by him to `queue/next`. It is not a machine's successor file, and no machine writes a successor to it. Folder: `C:\Users\Shared\Documents\erw`. Model: Opus 5.5, high effort. ONE Claude Code window on the desktop this weekend: chains 701, 730 and 740 are stopped and this chain replaces all three. Run it unattended. Do not stop to ask questions. Model spend USD 0: call no model API (the key returns on 1 December). No heredocs or long inline scripts: use the Edit and Write tools, and put scripts in `runs/`.

## Why this chain

Samuel reviews on Sunday 29 November, through the day, and answers by the evening. The machines run nonstop meanwhile, one window each. This desktop is the only machine that lands and the only one that writes warehouse tables, so it is the desk for the old laptop (chain 770) and the personal laptop (chain 780). Its own build is the data under the question an AI lab's siting team, a developer and an investor all ask first: where in the US can the next gigawatts of load go, and what does each region's grid look like on every count that bears on it. The warehouse now holds every count (prices, congestion, grid conditions, queues, the large-load rules, carbon, interchange, the forecast); no page sets them side by side. Samuel agreed on 2 October that this is a flagship analysis, and ruled on 22 October that it lives on the datacenter page's All grids tab, not on a page of its own. Then the equities and the forecast, which landed this week, are kept current and deepened.

## The three machines this weekend (who owns what)

| Machine | Chain | Folder | Owns |
|---|---|---|---|
| Desktop (this one) | 760 | `C:\Users\Shared\Documents\erw` | every landing; the data lock and every warehouse table; the daily run; `site/data/siting/regions/` and its contract `docs/state/page_files_siting_regions.md`; `site/data/equities/`; `warehouse/predict/` and `site/data/predict/` |
| Old laptop | 770 | `C:\Users\lossa\Documents\erw` | `docs/reviews/weekend-2026-11-28.md`; the audits of `/forecast`, `/equities` and `/impact` (branches `wip/audit-forecast-*`, `wip/audit-equities-*`, `wip/audit-impact-*`); the ruling branches it readies (`wip/ready-*`) |
| Personal laptop, overnight only | 780 | `$HOME\Documents\erw` | the new section of the All grids tab (`site/app/cost-of-power/` files it adds for it, and edits to `AllGridsView.tsx` for that section only); the browser read of everything landed since 26 November, its fixes on `wip/c780-*` |

A machine edits only what it owns. A fault found in another machine's files is a row for that machine, never an edit. Branch names carry the chain's number (`wip/c760-*` here).

## Rules

- **The rules of chain 701 hold word for word** (`queue/done/701-night-26-november-desktop-repairs-equities-large-load.md`, and through it chain 601 and the owner's rules of 16 November as `queue/done/301-day-16-november-desktop-open-faults.md` has them), with these changes:
- **Session numbers** 11200 to 11399, each checked free on origin/main and every branch first.
- **One window.** No second Claude Code window and no background agent that edits files is started on this machine. Research agents that only read and return text are allowed, as chain 701 used them.
- **No waiting, and no watching.** A commit whose only content is that the window is watching or waiting for something (a landing, a lock, GitHub's checks, a publisher) is a fault of this chain: chain 740 made one every 20 minutes for a day. While a gate's suite or GitHub's checks run, the window works on the next item in another worktree and comes back. A progress line is written when something is done, found or decided.
- **The desk comes first** at the start of every session and after each numbered step: every row marked requested in `docs/state/landing_request_oldlaptop.md`, `docs/state/landing_request_portable.md` and `docs/state/landing_request_portable_w2.md`, and every row marked requested in the `docs/state/data_requests_*.md` files, in order of request. A requested row older than two numbered steps of this chain is a fault.
- **No ruling is taken for Samuel.** No `wip/alt-*`, `wip/switch-*`, `wip/audit-*` or `wip/ready-*` branch is landed unless its row is marked requested by the machine that owns it, and the old laptop requests a `wip/ready-*` branch only after Samuel's ruling for it is written in chat and pasted to it. No default moves.
- **No score, no rank, no advice in part B.** Each count is what its publisher published, or a plain arithmetic of it (a share, a sum, a mean) written in the method note. No composite, no weighting of one count against another, no "best region". How a reader sorts the regions is the reader's choice on the page.
- **Never end idle.** After part E, part F, until the weekly limit or until Samuel stops the window.

## The start (session 11200, long end 1:00)

1. Precheck. `git fetch origin`. This folder's `main` brought to `origin/main`; anything not on origin is pushed first as `wip/c760-local-2026-11-28`, untracked and ignored files listed and left. Free disk and memory written down.
2. This chain's file taken (`queue/next/760-...` to `queue/done/`), if the command that started the session has not already done it.
3. **Chains 701, 730 and 740 are closed** (Samuel stopped their windows before starting this one). For each: its progress file read; its open items copied, one line each, into this chain's progress file under "Taken over"; its note brought to its end with one line saying chain 760 took it over; its resume file (`702-resume-chain-701.md`, `731-resume-chain-730.md`, `741-resume-chain-740.md`) removed from `queue/next/` in one commit. A branch any of them left unlanded is listed with its state; nothing is landed without its row.
4. The resume file `queue/next/761-resume-chain-760.md`, committed alone and pushed, its text the lines between BEGIN and END below without those two words. A session that takes a resume file first writes the same text under the next number up (to 769). The chain's last session removes it.
5. `docs/state/progress_c760.md`: one line a landing, request, table, file or view, its state and session, pushed after each.
6. Part A, then part B, in this same session.

BEGIN
# Resume of chain 760

machine: data

Chain 760 was interrupted. First put this same text back in queue/next/ as the next number up to 769, named NNN-resume-chain-760.md, committed alone and pushed. Then read queue/done/760-weekend-28-november-desktop-desk-regions-forecast.md whole and docs/state/progress_c760.md, and continue chain 760 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
END

## Part A: the desk

As the rule above says, at the start of every session and after each numbered step. Chain 701's way of landing holds: gates through `scripts/land_check.py`, the whole suite, a build, a snapshot before and after each landing with every difference marked expected or not, no landing between 14:00 and 16:15 UTC or on Sunday between 22:30 and 23:45 UTC.

## Part B: where the next gigawatts can go, the data (the contract within this chain's first two hours)

1. **The contract first:** `docs/state/page_files_siting_regions.md`, in the form of `docs/state/page_files_conditions.md`, pushed to main: the files this chain writes under `site/data/siting/regions/` (an index of places; one file a place; one file of every place's counts side by side for the table), each field with name, type, unit, source table, license and an example row; how a held value is written (null with a `held` reason). One small example file of each kind, its values null, pushed with it. The personal laptop builds the section against it tonight.
2. **The places:** the 13 EIA regions, the 7 market operators and the balancing authorities of at least 5,000 MW, as the Grid tool and the forecast already name them (no new list of places).
3. **The counts, each for each place, each from a table the warehouse already holds, with its period and its source on hover:**
   - **Price:** day-ahead and real-time at the place's hubs, the last 12 months' mean, the 95th percentile and the hours above USD 100 and below zero, where the prices are public.
   - **Congestion:** the share of the hub's price that was congestion, the constraints that bound most hours and cost most, where published (`price_congestion_monthly`, `constraints_binding_monthly`).
   - **How tight the grid runs:** peak demand and its growth; the hours of alerts, watches and emergencies (`grid_all_alerts`); megawatts out of service at peak; reserves against the requirement where published.
   - **What is waiting to connect:** active megawatts in the interconnection queue by fuel, the share withdrawn historically, the median years from request to operation, from the queue tables already held.
   - **Large loads:** the large-load rules of the place's utilities (count, smallest load, minimum term, collateral, exit fee, study time, as held), the large-load queue totals and their period, the state laws held.
   - **What the power is made of and what it emits:** the mix and the carbon intensity, the year and the hour of day.
   - **What it leans on its neighbours for:** net imports as a share of demand, at the peak hours and over the year; the top three partners.
   - **What is spare:** curtailed megawatt-hours of wind and solar, the hours of negative price.
   - **How well its demand is forecast:** the operator's forecast error and the ERW forecast's, from the forecast's score file.
   - **Datacenters already there:** the facilities and announced projects held, with their megawatts as stated.
4. **To the done line:** tests, `check-values` for every file, a replication under `replication/siting_regions/` that rebuilds every figure from the public tables, a method note `docs/methods/siting_regions.md` (internal, with a decisions block), a daily step so the files stay current. Landing through the desk.

## Part C: the equities kept current and deepened

`equity_universe` (307 companies) and `equity_fundamentals_quarterly` (146,923 rows on this machine) are registered and in the daily run, and their page files current; coverage on main agrees with the tables (it showed 243 rows on 28 November). The segment roll-ups by the contract of chain 701; a sample of share counts and one statement line a company cross-checked against the filings; the replication under `replication/equities/` run. Share prices stay blank with "license needed": no paid source.

## Part D: the ERW forecast's open list

Chain 730's open items, as part of the start copied them: each in chain 730's form (walk-forward backtest, nothing known early, scores with the losses shown, tests, replication, a dated line in `docs/state/page_files_predict.md` and one line for the personal laptop in `docs/state/landing_request_portable.md`). Data request 20 (the one making without figures) first.

## Part E: the scheduled jobs green

Every failed step of the daily runs since 26 November, its cause in one line and its fix with a test; a streak of green days visible on `/internal/health`. Done once, at the cause; never a session of its own when part B, C or D has work.

## Part F: after part E, until the weekly limit or until Samuel stops the window

- Part B's histories deepened (five years where the tables hold them), a year at a time.
- Each new view read as its reader (five real cases each: an AI lab's siting analyst, a developer choosing between two regions, a utility planner, an investor, a student), every gap a numbered row, every fault of this machine's files fixed at its cause.
- The old laptop's audit rows that need the data machine, in order of request.

## The last session

- `docs/state/note_2026-11-28_data_c760.md` in short bullets: every landing with what a reader now sees and its full address; each new file and table; every count held and why; what waits for Samuel with the default taken, in plain words. Kept current while the chain runs, so that the old laptop can copy it into the review page.
- The resume file removed; `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. No file: part F goes on.
