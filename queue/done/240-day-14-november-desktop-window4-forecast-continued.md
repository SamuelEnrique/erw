# Chain of 14 November 2026: sessions 4250 to 4269, lab-desktop fourth window, unattended: the economic forecasting tool continued (master plan tool 17)

machine: lab-desktop-window4

Written on 13 November 2026 at about 10:10 UTC by session 4200 (chain 239) as that chain's next file; session 4249 updates it with what chain 239 did not finish. Model: Opus 5.5, high effort. It takes sessions 4250 to 4269; its first session checks each is free on origin's main and on every branch, skips a taken one upward and says so.

Take it by name with this window's name (the role file names the desktop `lab-desktop`, a data machine, so `chain_queue.py next --file` refuses a file marked for a window): from the main checkout, after `git pull --ff-only origin main`, run `.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'scripts'); import chain_queue; sys.exit(chain_queue.take(who='lab-desktop-window4', file='<this file>'))"`, then push the move.

## Who else runs on this machine

- **Window A** (worker-started): the data chain, sessions 38xx, branches `wip/c2xx-data`. It holds the data lock.
- **Window B**: the landing desk, sessions 4000 to 4099 and its continuations. It lands every branch.
- **Window C**: the licensing sweep, sessions 4100 to 4199 and its continuations.
- **This window** never changes the main checkout's branch or working files (except the queue commits), never touches their branches, never runs `scripts/land_check.py` and never writes warehouse data. It may build the site to read its pages, always through the build lock (`scripts/buildlock.py`), one build at a time. All its work is in git worktrees beside the main checkout named `erw-w4-<N>`, on `wip/4200-forecast` stacks, with `C:\Users\Shared\Documents\erw\.venv\Scripts\python.exe`. A stack ready to land gets a requested row in `docs/state/landing_request_desktop_w4.md`; window B lands it.

## Rules for every session

The rules of chain 239 (`queue/done/239-day-13-november-desktop-window4-forecast.md`) hold unchanged: precheck first; `git fetch origin` and `origin/main` merged before work; default-neutral; `site/lib/release.ts` untouched; nothing sent or posted; no backfill; no brand work; model spend at most USD 2 a session and USD 20 the chain; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash; never stop to ask; the weekly limit is the only stop. Accuracy is the whole game: every multiplier, rate and default traces to a public, cited source, never invented; a paid or missing source is flagged in the method note and as a ruling; a new warehouse table is a request row in `docs/state/data_requests_forecast.md` for window A. Samuel's standing tool rules (inputs left, results right, grey defaults with source tips, editable in place, A and B side by side, neutral, hover values, tips only, Stata and Python replication, the method note internal, plain-noun names). No step waits idle. A commit at least every 25 minutes. The queue step always by name.

## What chain 239 left (session 4249, 13 November 2026, about 13:45 UTC)

Chain 239 finished its plan by session 4229: `/impact` is "Local impact", built and read at 1280 and 390, check-values 633 of 633, faults 1 to 18 in `docs/reviews/forecast-faults-2026-11-13.md` (17 fixed with tests, fault 13 a ruling), the note `docs/state/note_2026-11-13_desktop_window4.md`. Three landing rows on main (`docs/state/landing_request_desktop_w4.md`): row 3 (`wip/4225-forecast` at `925e9e481`) holds rows 1 and 2. Five data requests for window A (`docs/state/data_requests_forecast.md`). Twelve rulings for Samuel in the note.

## Session 4250: the ground

Long end 1:00. Precheck (from the main checkout), `git fetch`, the health gate noted. Read the landing request file: which rows landed, which wait, which failed and why (the gate's own log under `runs/land_check/`). Read the data requests file: which rows window A did. Read the note's rulings: any Samuel answered (in chat files, `docs/state/`, or the queue). Into the report: what of the list below is still to do, in order.

## Sessions 4251 to 4265: in this order, until done

Long end 1:00 each. Every change on a new stack (`wip/4250-forecast`) built on the newest landed or requested one; every fault a numbered row of the fault file, fixed with a test; a build read (under the build lock, port 4210 or upward, never 4200 while window B's gate uses it) and check-values before each landing row.

1. **A failed landing** of rows 1 to 3: fixed first, the row moved.
2. **Window A's tables**: for each data request row done, the page reads the table instead of `site/data/forecast/` (the deflator, JEDI's cost, the property rules, the parameters); check-values follows; the site data file kept until the table is in the live set.
3. **Rulings answered**: each applied (the name, Iowa's solar exemption, Texas's exemption share, Oregon's rate, Virginia's revenue share with a price forecast, the shared chart's spacing).
4. **More statutes**, each read from the state's own page, robots first: sales tax exemptions of South Dakota, North Dakota and Nebraska for generating equipment; Texas's Comptroller rulings for an exempt share (if one is stated); property tax rules of Montana, Colorado, Arizona, New Mexico and Wyoming where a statute fixes the figure. Illinois and Ohio only if their sites can be read without bypassing a refusal.
5. **The cross-check to five studies**: two more published impact studies with their own numbers (a gas plant and a solar project, ideally with a stated property tax), run through `site/scripts/forecast-crosscheck.mjs`.
6. **Stata**: if a machine with Stata can run the downloaded do-file, run it against a page run; else leave the do-file's structure tests.

## Sessions 4266 and 4267: a last read

Long end 1:00 each. A fresh read of the page at 1280 and 390 on a local production build, every figure against check-values; faults fixed the same way.

## Session 4268: the note

Long end 1:00. `docs/state/note_<date>_desktop_window4.md` (a new date) in short bullets: what changed since chain 239's note, what waits in which landing row, the sources missing or paid, the rulings waiting with defaults.

## Session 4269: the next file, the queue

Long end 1:00. A next file for this window (the same form, sessions 4270 upward) only if work remains; pushed alone; then the queue step by name (`chain_queue.take(who='lab-desktop-window4', file=...)`, as this file's opening says).
