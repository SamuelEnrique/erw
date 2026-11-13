# Chain of 18 November 2026: sessions 1958 to 1971, code machine (samueloldlaptop), unattended: chain 224's unfinished steps, the faults files' open rows, the records

machine: code

Written first by session 1944 of chain 224 (`queue/done/224-day-17-november-code-continued.md`) on 13 November 2026 at about 06:50 UTC, as that chain's rules ask, and to be updated by its session 1957 with what chain 224 did not finish. The first queue number free on origin's main and every branch was 225 (223 is the data machine's next chain). It takes sessions 1958 to 1971, fourteen numbers after chain 224's last (1957); session 1958 checks each is free on origin's main and on every branch, skips a taken one upward and says so. Model: Opus 5.5, high effort. One Claude Code window on this machine.

## Why this chain

Chains 220 and 222 each stopped inside their first session, both times while or just after the gate for `wip/1905-revert` ran its suite on this machine with about 0.6 to 1.0 GB of memory free (every failure a `MemoryError`, a commitment-limit exit or a PowerShell timeout). Chain 224 did not try that gate a third time: it asked for the landing in `docs/state/landing_request_oldlaptop.md` (row 9). What chain 224 does not finish comes first here; then every faults file's rows still open; then the records.

## Rules for every session

The rules of `queue/done/224-day-17-november-code-continued.md` hold word for word (they are chain 222's, which are chain 220's, which are chain 219's, which are chain 217's, which are chain 214's, which are chain 213's, which are chain 149's with 213's additions: never stop; the next file written first; a landing waits for green main; the desktop's files not touched; a fault is a quoted line and its replacement; the built site is read, not the code alone; `.venv\Scripts\python.exe` for every python command; precheck first; `git fetch origin` and `origin/main` merged before work; worktrees beside `C:\Users\lossa\Documents\erw`, removed once landed; landings through `scripts/land_check.py`, every printed command its own command with its exit read, never between 14:00 and 16:15 UTC, the snapshots before and after the only touch of production; a gate stopped for memory twice in one session is not tried a third time, a request row appended to `docs/state/landing_request_oldlaptop.md` instead; default-neutral, `site/lib/release.ts` untouched, nothing sent or posted, no warehouse data written, no backfill, no layout redesign, no brand work; the model under the owner's key at USD 2 a session and USD 20 the chain; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash; the weekly limit the only stop).

The addition of chain 219 holds: if the two lists below are still empty when session 1958 starts, chain 224 stopped before its session 1957, and session 1958 rebuilds them from chain 224's reports (`archive/sessions/SESSION_1944_REPORT.md` onward), its branches (`git branch -r | grep -E "wip/19(4|5)"`) and its `runs/s19NN/` folders, and says so.

The addition of chain 224: before a gate on this machine, `grep MemFree /proc/meminfo`; under 2 GB free, the gate is not started and the landing stays a request row in `docs/state/landing_request_oldlaptop.md`, said so (two chains' windows were lost to a gate run at about 1 GB free).

Read first: chain 224's note (`docs/state/note_2026-11-18_code_c224.md`), `docs/state/landing_request_oldlaptop.md`, `docs/reviews/five-tools-read-2026-11-11.md`, the five faults files (`docs/reviews/<tool>-faults-2026-11-11.md`), `docs/reviews/periodicals-faults-2026-11-05.md`, `docs/reviews/board-audit-2026-11-06.md`, `docs/reviews/trader-path.md`, `docs/reviews/lab-path.md`, `docs/reviews/onenergy-walkthrough.md`, `docs/brand.md`, `docs/voice.md`, `CLAUDE.md`.

## Session 1958: the next file, the ground, chain 224's first unfinished step

Long end 1:00. The next file in `queue/next/` for this machine (the first queue number free on origin's main and every branch, `machine: code`, at least fourteen sessions, this chain's unfinished steps first, then the faults files' open rows), committed alone and pushed, `git status -sb`. Then: precheck, `git fetch origin`, `git worktree list` with every worktree of a landed branch removed and the count before and after, memory and disk free, `scripts/freeze.py status`, whether every branch of chain 224 and `wip/1905-revert` is an ancestor of `origin/main`, written to the report. Then the first step chain 224's note lists as not finished.

## Sessions 1959 to 1963: chain 224's other unfinished steps

Long end 1:30 each. One step a session, in chain 224's order, as session 1957 lists them below. A landing is a landing here (the memory check, the gate, the snapshots, the branches deleted once ancestors); a read is a read here (the branch built locally, `python scripts/db_probe.py` first, the pages at 390 and 1280 with the internal cookie, screenshots under `runs/<N>/shots/`, the faults file written or extended). When the list is shorter, the free sessions take the faults below, in order.

### Unfinished steps (written by session 1957 of chain 224)

(To be filled by session 1957: one line a step, in chain 224's order, with the exact commands where the step was a landing.)

## Sessions 1964 to 1968: the faults files' open rows

Long end 1:30 each. One fault a session, in this order: `docs/reviews/deals-faults-2026-11-11.md`, `datacenter-faults-2026-11-11.md`, `policy-faults-2026-11-11.md`, `companies-faults-2026-11-11.md`, `attention-faults-2026-11-11.md`, `periodicals-faults-2026-11-05.md`, `board-audit-2026-11-06.md`, then the faults of the newest walks of `docs/reviews/trader-path.md`, `lab-path.md` and `onenergy-walkthrough.md`, each file's rows in its order; a row whose state is `ruling` or `data machine` is not this chain's and is skipped, said so. Each session: the fault quoted with the page, the cell or the click it faults and what the fix writes instead; the fix with a test; its branch cut from the newest unlanded branch of this chain. **Sessions 1965 and 1968 end by landing the stack through the gate** (after the memory check), the snapshots, the branches deleted once ancestors.

### Open faults (written by session 1957 of chain 224)

(To be filled by session 1957: every faults file's rows whose state is open, one a line, in the files' order; the owner's rows named, not to be decided here.)

## Session 1969: the records and the clean-up

Long end 1:00. Every landed branch of this chain deleted on origin, every worktree of a landed branch removed; every faults file's rows with a state; the tests green on main; `docs/reviews/five-tools-read-2026-11-11.md`'s table updated with the counts after this chain; the package's and the site's records rebuilt if this chain changed a table they read (`python package/tools/build_tables.py --check`).

## Session 1970: the paths walked again

Long end 1:30. The trader path, the lab's path on the datacenter tracker and the On.Energy walkthrough on the battery tool, each walked click by click on the local build only where a fault of chain 224's walk was fixed since, the step's new reading written beside the old; the rest said unchanged.

## Session 1971: the note, the next file, the landing, the queue

Long end 1:00. A note in `docs/state/` (its name checked free first: `note_2026-11-19_code_c225.md`) in chain 149's note's form; the next file (written by session 1958) updated with what this chain did not finish and the faults left open, pushed alone; what is unlanded landed through the gate (after the memory check), not between 14:00 and 16:15 UTC, the snapshots; then `python scripts/chain_queue.py next`, and run the file it prints the same way.
