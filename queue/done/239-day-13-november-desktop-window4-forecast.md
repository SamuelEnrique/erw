# Chain of 13 November 2026: sessions 4200 to 4249, lab-desktop fourth window, unattended: the economic forecasting tool (master plan tool 17)

machine: lab-desktop-window4

Written on 13 November 2026 at about 10:05 UTC at the owner's instruction for a fourth Claude Code window on lab-desktop: Samuel asked for this tool directly. Model: Opus 5.5, high effort. About 12 hours, through the weekly reset and beyond. It takes sessions 4200 to 4249; its first session checks each is free on origin's main and on every branch, skips a taken one upward and says so. Numbers up to 238 are taken on origin's main, so this file is 239.

## Who else runs on this machine

- **Window A** (worker-started): the data chain, sessions 38xx, branches `wip/c2xx-data`. It holds the data lock.
- **Window B**: the landing desk, sessions 4000 to 4099. It lands every branch.
- **Window C**: the licensing sweep, sessions 4100 to 4199.
- **This window** never changes the main checkout's branch or working files (except the queue commits `scripts/chain_queue.py` makes), never touches their branches, never runs `scripts/land_check.py` and never writes warehouse data. It may build the site to read its pages, always through the build lock (`scripts/buildlock.py`), one build at a time on this machine. All its work is in git worktrees beside the main checkout named `erw-w4-<N>`, on `wip/4200-forecast` stacks, with `C:\Users\Shared\Documents\erw\.venv\Scripts\python.exe`. A stack ready to land gets a requested row in `docs/state/landing_request_desktop_w4.md` (created in the form of `landing_request_portable.md`: branch, head, task name, port 4200 upward, the tests run), committed and pushed; window B lands it.

## Rules for every session

The rules of the newest data chain in `queue/done` hold where they apply: precheck first; `git fetch origin` and `origin/main` merged before work; default-neutral; `site/lib/release.ts` untouched; nothing sent or posted; no backfill; no brand work; model spend under the owner's key at most USD 2 a session and USD 20 the chain; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash. Never stop to ask: a reversible choice goes under "Decisions made without you", anything that waits for Samuel goes under "For Samuel's ruling" with a default, and the chain continues. The weekly limit is the only stop. Also:

- **Accuracy is the whole game.** Every multiplier, rate and default traces to a public, cited source (NREL's JEDI models, BLS QCEW, BEA public tables, Census, state tax statutes and assessor rules, EIA project data already in the warehouse). Never invent a parameter. A source that is paid or missing is flagged in the method note and as a ruling, never faked. A new warehouse table the tool needs is a request row in `docs/state/data_requests_forecast.md` for window A, which holds the data lock.
- **Samuel's standing tool rules.** Inputs in a left box (long lists in collapsible groups), results on the right; every assumption shows its default in grey with its source in a hover tip and is editable in place; two scenarios, A and B, compared side by side, succinct; neutral, no "so what" box and no advice; charts respond to hover with values; explanations only as hover tips; a Stata do-file and a Python replication; the method note internal, never on the page; plain-noun names.
- **No step waits idle**: when blocked, take the next.
- **A commit at least every 25 minutes** in the chain's worktree: the chain worker closes a session with no commit for 30 minutes.
- **The queue step is always by name** (`scripts/chain_queue.py next --file <name>`), never bare `next`.

## Session 4200: the next file, the ground

Long end 1:00. The next file first (`queue/next/<first free number>-day-<day>-november-desktop-window4-forecast-continued.md`, `machine: lab-desktop-window4`, the same goal, sessions 4250 upward, at least 14 sessions), committed alone and pushed. Then the precheck, `git fetch`, the health gate (`python warehouse/metadata/build_status.py --gate`; this tool is Samuel's direct request, so a closed gate is noted, not a stop), and the ground: master plan tool 17 (`docs/master_plan.md`), the existing severance tax and lease tools and the generator and datacenter cost pages (what can be reused: tables, components, the scenario block), and the public sources for each output.

## Sessions 4201 to 4210: the model and its method note

Long end 1:00 each. `docs/methods/forecast.md` (internal), for a project the user picks or types (technology, MW, state and county, capex, construction and operating years):

- construction and operating jobs and earnings (direct, indirect, induced, from JEDI's public parameters by technology and state);
- property tax by state rules (assessment, depreciation, abatements where the statute is public);
- sales and use tax on construction spend;
- severance tax where it applies (reuse the existing severance tool);
- state income tax on earnings;
- all by year over the project's life, with net present value at an editable discount rate.

Each formula tested; a cross-check table of the model against at least three published impact studies, with sources.

## Sessions 4211 to 4235: the page

Long end 1:00 each. The tool's page (default name "Local impact", a ruling for Samuel with that default, placed in the menu where the rulings put Economics tools), read on a local production build at 1280 and 390, every figure a check-values key, every fault a numbered row in `docs/reviews/forecast-faults-2026-11-13.md` fixed with a test; the A/B comparison; the downloads (CSV, Stata, Python) of a run; the replication do-file. Landing request rows as stacks are ready.

## Sessions 4236 to 4247: what remains, three readers

Long end 1:00 each. What remains; then a fresh read of the page as an economic developer, a county assessor and a utility siting analyst would use it, faults fixed the same way.

## Session 4248: the note

Long end 1:00. `docs/state/note_<date>_desktop_window4.md` in short bullets: what the tool does, the cross-check results, what waits in which landing row, the sources missing or paid, the rulings waiting with their defaults.

## Session 4249: the next file, the queue

Long end 1:00. The next file (written by session 4200) updated with what is unfinished and pushed alone; `scripts/chain_queue.py next --file <the next file's name>`, and that file run the same way.
