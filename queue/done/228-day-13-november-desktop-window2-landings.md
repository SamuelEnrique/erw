# Chain of 13 November 2026: lab-desktop, second window (the landing desk), sessions 4000 to 4049, unattended: the laptops' landing requests, and the fallback (an 8 GB suite gate, the scheduled runs' failures, main kept green)

machine: lab-desktop-window2

Written by the owner's prompt of 13 November 2026 (about 09:30 UTC), as the desktop's second Claude Code window. The `machine:` line names no role and no machine on purpose: the chain worker and window A (the data chain, queue 227 and its successors, sessions 38xx, branches `wip/c2xx-data`) never take this file; it is taken by name in this window with `chain_queue.take(who='lab-desktop-window2', file=...)`, since `next --file` refuses a window's name on a data machine (chain 183's command). Sessions 4000 to 4099 were checked free on origin's main and every branch at 09:26 UTC. Model: Opus 5.5, high effort. A third window (licensing, sessions 4100 to 4199) starts after this one.

## Rules for every session

The rules of the newest data chain in `queue/done` (`queue/done/226-day-18-november-data-continued.md`, and through it chains 223, 221, 218, 216, 215, 212, 147 and 157) hold word for word where they apply: precheck first; `git fetch origin` and `origin/main` merged before work; landings through `scripts/land_check.py`, every printed command its own command with its exit read, never between 14:00 and 16:15 UTC, the snapshots before and after the only touch of production; the build lock, one build at a time on this machine, shared with window A; default-neutral; `site/lib/release.ts` untouched; nothing sent or posted; no warehouse data written by this window; no backfill; no layout redesign; no brand work; model spend under the owner's key at USD 2 a session and USD 20 the chain; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash. Also:

- **Never stop to ask.** A reversible choice goes under "Decisions made without you"; anything that waits for Samuel goes under "For Samuel's ruling" with a default, and the chain continues. The weekly limit is the only stop.
- **The main checkout is window A's.** This window never changes its branch or working files (except the queue commits this queue's step makes). All work happens in git worktrees beside it named `erw-w2-<N>`, with `C:\Users\Shared\Documents\erw\.venv\Scripts\python.exe`; `.env` is copied into a worktree only when a gate needs it (git-ignored, never committed). Window A's branches are never touched.
- **No step waits idle.** When no landing request is ready, the fallback below; the request files are read again at the start of every session.
- **A gate that fails on a real test failure** is fixed on the requesting branch's stack only when the fix is small and plainly correct; otherwise the failure is written into the request row and the desk moves on.
- **A commit at least every 25 minutes** (the chain worker closes a quiet session at 30); never on a branch while its gate runs.
- **The queue step is by name**, never bare `next`.

## Session 4000: the next file, the ground, the old laptop's row 9

Long end 1:30. The next file first (`queue/next/<first free number at or above 229>-day-13-november-desktop-window2-landings-continued.md`, the same machine line and goal, sessions 4050 upward, at least fourteen sessions), committed alone and pushed. Then precheck, `git fetch`, memory and disk free. Then `docs/state/landing_request_oldlaptop.md` row 9, `wip/1905-revert` (head `77e8916a0`, task `1944-revert`, port 3944): `origin/main` merged into it, then the lander exactly as the row's notes say. It restores the datacenter grids view's default (Samuel's ruling, `datacenter-faults-2026-11-11.md` row 4). The row marked landed with the commit.

## Session 4001: the portable laptop's row 16

`docs/state/landing_request_portable.md` row 16, `wip/3701-sellable`: session 3718's three changes as the row says; landed, or exactly what stops it written.

## Sessions 4002 to 4048: the landing desk

At every session start: `git fetch`, then `docs/state/landing_request_oldlaptop.md`, `landing_request_portable.md` and any other `landing_request_*.md` read for rows marked requested. Three laptop windows append rows today: the old laptop (sessions 1972 to 1999, periodicals), and the portable laptop's windows P1 (5000 to 5099, the five tools), P2 (5100 to 5199, security and analytics) and P3 (5200 to 5299, the AI chat). Each requested row landed in order of request (several from one stack land as one), marked landed with the commit, pushed.

Between landings, the fallback, roadmap items 1 and 6:

- **(a)** the full suite gate runnable on a machine with 8 GB (split, ordering, the memory-heavy modules found and fixed), so the laptops can land again;
- **(b)** the root cause of every failed scheduled run of the last 14 days, written in `queue/summary/`;
- **(c)** main kept green: any red test on main fixed first.

## Session 4049: the note, the next file, the queue

`docs/state/note_<date>_desktop_window2.md` (short bullets: every landing with its commit, every row that waits and why, the fallback's results, what waits for Samuel with defaults). Then the next file updated with what is unfinished, pushed alone, and the queue step by name.
