# Chain of the night of 7 November 2026: sessions 3720 to 3733, personal laptop (portable-laptop), unattended: roadmap items 2, 1 and 6 continued (chain 208's unfinished steps, then the faults its reads leave)

machine: portable-laptop

Written by session 3700, the first session of `queue/done/208-night-6-november-portable-sellable.md` (sessions 3700 to 3719), on 6 November 2026 at about 21:50 UTC, as that file asks: this chain's unfinished steps first, then the faults its reads leave. Numbered 209, the first queue number free on origin's main and every branch after 208. Session 3700 was the first number free at or above 3700 on origin's main and every branch (the highest taken was 3650), so chain 208 holds 3700 to 3719 and this file takes 3720 to 3733; session 3720 checks each is free on origin's main and every branch and skips a taken one upward, saying so. **Session 3719 updates this file** with what chain 208 did not finish (under "Sessions 3721 to 3726") before it is taken. For the personal laptop only (named by its machine name, so no other code machine takes it).

## Rules for every session

The rules of `queue/done/208-night-6-november-portable-sellable.md` (its first paragraph) hold word for word: one Claude Code window, the only one on this machine; `.venv\Scripts\python.exe` for every python command; precheck first; `git fetch origin` and `origin/main` merged before work; worktrees beside the main checkout on `wip/<N>-sellable`, cut from the newest unlanded branch of chain 208 (or from `origin/main` if none is unlanded); no em or en dash in any file; nothing sent or posted; `site/lib/release.ts` untouched; no warehouse data written; no layout or design change to any page (the brand pass waits for the owner's mockups); no point of view in anything written. Landings: `scripts/land_check.py` exactly as `docs/machines.md` says, every printed command run as its own command with its exit read, the snapshots before and after as the only touch of production, never between 14:00 and 16:15 UTC, 2 GB free enough with this the only window (`Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory` first); a gate stopped for memory twice in one session is not tried a third time: a row appended to `docs/state/landing_request_portable.md` on main (branch, head commit, task name, port, tests' result), and the work goes on from a branch cut from the unlanded one. Every three sessions, land or request. Model calls under the owner's key: USD 2 a session, USD 15 the chain. Reports in short bullets with "Decisions made without you" and "For Samuel's ruling". Files other chains own, not touched: the periodicals (`warehouse/news`, `site/app/digest`, `site/app/roundup`), the deals, datacenter, policy, companies, attention and findings code and pages, the price board's builder and page, the large-load and derived tables.

- **Session 3720 writes the next file first** (`queue/next/<first free number at or above 210>-night-8-november-portable-sellable-continued.md`, `machine: portable-laptop`, at least fourteen sessions: this chain's unfinished steps first, then the faults its reads leave), commits it alone and pushes it to main; session 3733 updates it. **The queue step is by name**: `python scripts/chain_queue.py next --file <that file's name>`, never the bare `next`.

Read first: `docs/state/note_2026-11-07_portable_sellable.md` (chain 208's note), `docs/state/roadmap_item2_state_2026-11-06.md`, `docs/state/main_red_2026-11-06.md`, `docs/state/landing_request_portable.md`, `replication/` (battery, generator, datacenter, analysis, grid), `docs/methods/crosschecks/`, `docs/roadmap.md` (items 1, 2 and 6), `.github/workflows/code-branch.yml`, `scripts/land_check.py`, `warehouse/health.py`, `docs/machines.md`.

## Session 3720: the next file, the machine, the chain's state

Long end 0:45. The next file (above), committed alone, pushed. The machine (memory and disk free; worktrees of landed branches removed). Chain 208's branches read: what landed, what waits on a landing request, which of the owner's rulings in its note are answered.

## Sessions 3721 to 3726: chain 208's unfinished steps

Long end 1:30 each. Each session takes the next unfinished step of chain 208 in its order (part one: the replications of Automated Analysis and the Grid tool, their method notes' Replication and Cross-checks sections and decisions blocks, the cross-check tables under `docs/methods/crosschecks/`; part two: the red-main causes, the merge gate's whole suite on a clean checkout, the data machine's suite before its push, a bot's push that would make main red refused, the thin page-file rebuild, the health streak and the one-email rule). Session 3719 lists here what is left; if nothing is left, these sessions take the faults below.

## Sessions 3727 to 3730: the faults chain 208's reads leave

Long end 1:15 each. One fault a session, in the order chain 208's note lists them under "What did not finish", each with its test written first, then the fix, then the test passing on a clean checkout. A fault in a file another chain owns is written into that chain's next file or its note, not fixed here.

## Session 3731: the landing

Long end 1:30. `origin/main` merged; the whole suite; the gate (`land_check.py --ref <the newest branch> --task <its number>-sellable --port 3731`), the printed commands, the snapshots; on memory twice, the landing request file. Branches deleted once ancestors of main; worktrees removed.

## Session 3732: the records

Long end 1:00. `docs/state/roadmap_item2_state_2026-11-06.md` and `docs/state/main_red_2026-11-06.md` brought to the after state, each tool's four items present or not; worktrees of landed branches removed.

## Session 3733: the note, the next file, the landing, the queue

Long end 1:00.

1. `docs/state/note_2026-11-08_portable_sellable.md` in chain 152's note's form.
2. The next file (written by 3720) updated; pushed alone.
3. Land what is unlanded (the rules), or request it.
4. `python scripts/chain_queue.py next --file <the next file's name>`, and run the file it prints the same way.
