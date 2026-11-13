# Chain of 13 November 2026: sessions 4100 to 4149, lab-desktop third window, unattended: the licensing sweep (roadmap item 5)

machine: lab-desktop-window3

Written on 13 November 2026 at about 09:30 UTC at the owner's instruction for a third Claude Code window on lab-desktop. Model: Opus 5.5, high effort. It takes sessions 4100 to 4149; its first session checks each is free on origin's main and on every branch, skips a taken one upward and says so. Numbers up to 228 are taken on origin's main, and window B took 228 minutes before this commit, so this file is 229.

## Who else runs on this machine

- **Window A** (worker-started): the data chain, queue 227 and successors, sessions 38xx, branches `wip/c2xx-data`. It holds the data lock.
- **Window B**: the landing desk, sessions 4000 to 4099. It lands every branch.
- **This window** never changes the main checkout's branch or working files (except the queue commits `scripts/chain_queue.py` makes), never touches their branches, never builds the site, never runs `scripts/land_check.py` and never writes warehouse data. All its work is in git worktrees beside the main checkout named `erw-w3-<N>`, on a `wip/4100-licenses` stack, with `C:\Users\Shared\Documents\erw\.venv\Scripts\python.exe`. A piece ready to land gets a requested row in `docs/state/landing_request_desktop_w3.md` (the form of `landing_request_portable.md`: branch, head, task name, port 4100 upward, the tests run), committed and pushed; window B lands it.

## Rules for every session

The rules of the newest data chain in `queue/done` hold where they apply: precheck first; `git fetch origin` and `origin/main` merged before work; default-neutral; `site/lib/release.ts` untouched; nothing sent or posted; model spend under the owner's key at most USD 2 a session and USD 20 the chain; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash. Never stop to ask: a reversible choice goes under "Decisions made without you", anything that waits for Samuel goes under "For Samuel's ruling" with a default, and the chain continues. The weekly limit is the only stop. Also:

- **A license may be tightened** (public to internal) on evidence, freely. **A license is never loosened** (internal to public) by this chain: each such case is a ruling for Samuel with the default "stays internal", its evidence quoted (the terms' exact clause, its URL, the date read).
- **`coverage.csv` is never edited by hand**: changes go through `warehouse/metadata/sources.csv` and `scripts/licenses.py`, which window A's builder reads.
- **No step waits idle**: when one source is blocked (a terms page unreachable, a robots refusal), its row says so and the next is taken.
- **Robots and terms first** for every web read (the memories: robots before the fetch, AI agents named, redirects to an unread host).
- **A commit at least every 25 minutes** in the chain's worktree: the chain worker closes a session with no commit for 30 minutes.
- **The queue step is always by name** (`scripts/chain_queue.py next --file <name>`), never bare `next`.

## Session 4100: the next file, the ground

Long end 1:00. The next file first (`queue/next/<first free number>-day-<day>-november-desktop-window3-licenses-continued.md`, `machine: lab-desktop-window3`, the same goal, sessions 4150 upward, at least 14 sessions), committed alone and pushed. Then the precheck, `git fetch`, and the ground: `docs/licenses.md`, `docs/licenses_holds.csv`, `docs/state/unsettled_licenses_2026-10-19.md`, `warehouse/metadata/sources.csv`, `coverage.csv`, `docs/reviews/licenses/` (the four permission letters). Into the report: the count of tables with no verdict, a stale verdict, or a flag that disagrees with `docs/licenses.md`.

## Sessions 4101 to 4130: roadmap item 5

Long end 1:00 each. Done when `docs/licenses.md` has a verdict for every table with the flag in `coverage.csv` agreeing.

- **Publisher by publisher** (largest table count first): each table's license confirmed against the publisher's current terms page (read with the web, robots and terms respected): verdict public, internal or permission needed; the clause quoted with its URL and the date read; the flag fixed in `sources.csv`; a test that the verdict and the flag agree.
- **The four permission letters** (NYISO, SPP, PJM, MISO) in `docs/reviews/licenses/` brought up to date: the exact tables and fields asked for, the use (an open, citable research warehouse at Stanford, derived figures on a site in review), the right contact address from the publisher's own pages. Ready for Samuel to send; nothing sent.
- **Per publisher, any published price or fee** for redistribution or a data license, with its source, in `docs/licenses_costs.md`.
- **FRED**: its terms forbid database storage. For each FRED-sourced series, the EIA or Federal Reserve primary source named (series id and URL), written as a request row in `docs/state/data_requests_licenses.md` for window A, which holds the data lock. This chain writes no data.

## Sessions 4131 to 4147: the rest of the sweep, the test, the pages

Long end 1:00 each. What remains of the sweep; then a test that fails whenever a table reaches the public site while its verdict is not public (if one does not already exist); then `/data/licenses` and the method notes' license lines checked against the new verdicts (the code and the data files read, nothing built), each disagreement fixed on the stack.

## Session 4148: the note

Long end 1:00. `docs/state/note_<date>_desktop_window3.md` in short bullets: verdict counts before and after, every flag changed, the letters' state, the costs found, the rulings waiting with their defaults.

## Session 4149: the next file, the landing request, the queue

Long end 1:00. The next file (written by session 4100) updated with what is unfinished and pushed alone; the landing request row for the final stack; `scripts/chain_queue.py next --file <the next file's name>`, and that file run the same way.
