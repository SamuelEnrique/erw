# Chain of 15 November 2026: sessions 4270 to 4289, lab-desktop fourth window, unattended: the economic forecasting tool continued (master plan tool 17)

machine: lab-desktop-window4

Written on 13 November 2026 at about 17:40 UTC by session 4269 (chain 240) as that chain's next file. Model: Opus 5.5, high effort. It takes sessions 4270 to 4289; its first session checks each is free on origin's main and on every branch, skips a taken one upward and says so.

Take it by name with this window's name (the role file names the desktop `lab-desktop`, a data machine, so `chain_queue.py next --file` refuses a file marked for a window): from the main checkout, after `git pull --ff-only origin main`, run `.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'scripts'); import chain_queue; sys.exit(chain_queue.take(who='lab-desktop-window4', file='<this file>'))"`, then push the move.

## Who else runs on this machine

- **Window A** (worker-started): the data chain, sessions 38xx, branches `wip/c2xx-data`. It holds the data lock.
- **Window B**: the landing desk, sessions 4000 to 4099 and its continuations. It lands every branch.
- **Window C**: the licensing sweep, sessions 4100 to 4199 and its continuations.
- **This window** never changes the main checkout's branch or working files (except the queue commits), never touches their branches, never runs `scripts/land_check.py` and never writes warehouse data. It may build the site to read its pages, always through the build lock (`scripts/buildlock.py`), one build at a time; serving a build already made needs no lock. All its work is in git worktrees beside the main checkout named `erw-w4-<N>`, on `wip/4200-forecast` stacks, with `C:\Users\Shared\Documents\erw\.venv\Scripts\python.exe`. A stack ready to land gets a requested row in `docs/state/landing_request_desktop_w4.md` (moved on main through a detached worktree of `origin/main`, never in the main checkout); window B lands it.

## Rules for every session

The rules of chain 239 (`queue/done/239-day-13-november-desktop-window4-forecast.md`) hold unchanged: precheck first; `git fetch origin` and `origin/main` merged before work; default-neutral; `site/lib/release.ts` untouched; nothing sent or posted; no backfill; no brand work; model spend at most USD 2 a session and USD 20 the chain; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash; never stop to ask; the weekly limit is the only stop. Accuracy is the whole game: every multiplier, rate and default traces to a public, cited source, never invented; a paid or missing source is flagged in the method note and as a ruling; a new warehouse table is a request row in `docs/state/data_requests_forecast.md` for window A. Samuel's standing tool rules (inputs left, results right, grey defaults with source tips, editable in place, A and B side by side, neutral, hover values, tips only, Stata and Python replication, the method note internal, plain-noun names). No step waits idle. A commit at least every 25 minutes (the build lock was held by other windows for up to an hour at a time on 13 November: commit a report draft while waiting). The queue step always by name. Every web request through a probe log of the chain's own (`runs/w4/probe.py` writes `runs/w4/probe.csv`; chain 240 ended at request 107 of its ceiling of 120: start a new log or raise the ceiling with a note), robots files first, crawl delays slept.

## What chain 240 left (session 4269, 13 November 2026, about 17:40 UTC)

Chain 240 ran sessions 4250 to 4263 and 4266 to 4268 (`docs/state/note_2026-11-13_desktop_window4_c240.md`). Property tax statutes now held: Minnesota, South Dakota, North Dakota, Nebraska, Iowa, Kansas, Oregon, Wyoming, Florida, Arizona, North Carolina, Michigan, Vermont, Wisconsin, Nevada. The cross-check holds six studies of seven projects (a gas plant among them) and a tax check. The review pack `docs/reviews/packs/impact.md` describes the forecast. Faults 1 to 21; 13 and 21 a ruling (the shared chart's spacing). Landing row 4 (`wip/4250-forecast`, at `c84bc11aa` or a later commit of reports and notes) holds rows 2 and 3; row 1 landed. Data requests 1 to 5 still requested. Fifteen rulings in the note.

## Session 4270: the ground

Long end 1:00. Precheck (from the main checkout), `git fetch`, the health gate noted. Read the landing request file: which rows landed, which wait, which failed and why (the gate's own log under `runs/land_check/`). Read the data requests file: which rows window A did. Read the note's rulings: any Samuel answered (in chat files, `docs/state/`, or the queue). Into the report: what of the list below is still to do, in order.

## Sessions 4271 to 4285: in this order, until done

Long end 1:00 each. Every change on a new stack (`wip/4270-forecast`) built on the newest landed or requested one; every fault a numbered row of the fault file, fixed with a test; a build read (under the build lock, port 4210 or upward, never 4200 while window B's gate uses it) and check-values on the six `/impact` addresses before each landing row.

1. **A failed landing** of row 4: fixed first, the row moved. Once row 4 lands, read the live page after the deploy as the snapshot rule asks (the page is in review, so the internal view).
2. **Window A's tables**: for each data request row done, the page reads the table instead of `site/data/forecast/` (the deflator, JEDI's cost, the property rules, the parameters); check-values follows; the site data file kept until the table is in the live set.
3. **Rulings answered**: each applied (the name, Iowa's solar exemption, Texas's exemption share, Oregon's rate, Virginia's revenue share with a price forecast, the shared chart's spacing of faults 13 and 21, Vermont's education tax, Wisconsin's line and caps).
4. **More statutes**, each read from the state's own page, robots first, where a statute fixes the figure: Idaho's tax on wind and geothermal gross earnings (63-3502B) needs an electricity price the tool does not hold, so it is a ruling before it is a rule; Maryland, Tennessee, Oklahoma and South Carolina to be looked at; Illinois and Ohio only if their sites can be read without bypassing a refusal. Wisconsin's gas plant payment once "baseload" is read (79.04(7)(b)).
5. **A solar study**: a published statewide JEDI study of a utility solar project with its own numbers (ideally a stated property tax in a state whose rule is held), run through `site/scripts/forecast-crosscheck.mjs`. Chain 240's two searches found none readable.
6. **Stata**: if a machine with Stata can run the downloaded do-file, run it against a page run; else leave the do-file's structure tests.

## Sessions 4286 and 4287: a last read

Long end 1:00 each. A fresh read of the page at 1280 and 390 on a local production build, every figure against check-values; faults fixed the same way.

## Session 4288: the note

Long end 1:00. `docs/state/note_<date>_desktop_window4_c<chain>.md` in short bullets: what changed since chain 240's note, what waits in which landing row, the sources missing or paid, the rulings waiting with defaults.

## Session 4289: the next file, the queue

Long end 1:00. A next file for this window (the same form, sessions 4290 upward) only if work remains; pushed alone; then the queue step by name, as this file's opening says.
