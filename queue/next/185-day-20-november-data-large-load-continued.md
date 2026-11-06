# Chain of 20 November 2026: sessions 3205 to 3218, data machine (lab-desktop), unattended: chain 181's unfinished steps, the siting gaps still open, the daily run's week, the records

machine: data

Written by session 3160, the first session of `queue/done/181-day-18-november-data-large-load-continued.md`, at that file's instruction ("at least fourteen sessions numbered from the first free numbers after 3173"). Sessions 3174 to 3190 are the desktop's second window's and 3191 to 3204 chain 184's, so this file takes 3205 to 3218; none was named by a commit or a file on origin's main or its branches when this was written. The first free file number on origin's main and every branch was 185. It runs after chain 184. The first session checks again, skips a taken one upward and says so. Session 3173 of chain 181 updates this file at chain 181's end: sessions 3205 to 3207 then hold the steps chain 181's note says did not finish, in chain 181's order. Model: Opus 5.5, high effort. This machine runs this chain in its first window; its second window runs its own chains (`machine: lab-desktop-window2`): each works in its own worktrees and takes the data lock for every write, and queue commits are made in a detached worktree and pushed with `HEAD:main`.

## Why this chain

Chains 147 to 181 repaired the daily run, landed the stuck branches, built the large-load dataset and its derived tables, and wired them to the All grids tab where a public source allowed. This chain finishes what chain 181 did not, takes the siting gaps rows still open that a public US source can close without a ruling, reads the daily run's week, and brings the records up to date. The owner's rule of 24 October and 5 November holds first: no new foreign country's or foreign operator's source.

## Rules for every session

The rules of `queue/next/146-day-16-december-data-mepso-cges-kostt-ost.md` (parked by session 2862, readable at `queue/parked/`) and of `queue/done/145-day-15-december-data-seps-ast-ems-nosbih.md` hold, word for word, except where a line below replaces one; among them the robots and terms rule, the closed hosts (not asked again), the keys not held (a session that needs one stops that step and says so, without signing up), `scripts/precheck.py` first from the main checkout, the data lock, the union merge of generated lines, no character typed as an escape, no em or en dash in any file, a push to main never piped and followed by `git status -sb`, the Redivis request cap between tables, a currency other than USD a standing question. Also:

- **No new country or foreign operator source** (above). A source session of this chain takes only US sources (federal, state commission, ISO, utility) and only the ones named.
- **Never stop.** No session ends by stopping to ask the owner; it takes the most reasonable reading, writes it under "Decisions made without you" in its report, and goes on. A session whose step cannot be done writes why and goes to the next step. Any wait over 20 minutes (a deploy watcher, a build that is not building, an agent that has not answered) is stopped and the step done directly. The chain never sleeps until a time of day; where a landing window is closed it does the next session's non-landing work and comes back.
- **Session 2862 writes the next file first** (below), before any other work, and session 2885 updates it. The queue must never be empty for this machine.
- **The python is `.venv\Scripts\python.exe`** in every command; the main checkout is `C:\Users\Shared\Documents\erw`; worktrees go beside it as `C:\Users\Shared\Documents\erw-<task>` and are removed once their branch is an ancestor of main (the old laptop's disk filled from fifty worktrees on 21 October).
- **Landings on this machine** (the owner's ruling of 5 November): a code branch is landed here through `scripts/land_check.py` exactly as `docs/machines.md`, "The landing gate", says, with its printed commands each run as its own command and its exit read; never between 14:00 and 16:15 UTC and never on a Sunday between 22:30 and 23:45 UTC; the build needs 3 GB of memory free (`Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory` before the gate); one landing at a time; the snapshot before and after is the only touch of production (the owner's ruling of 24 October: no `check-values` against production, only against the local build). Each branch is merged with origin/main first, conflicts resolved as the rules say (generated lines as the union with their true count; coverage rows row by row from the side holding the newer row). A gate that fails on a fault of the branch's code is fixed on the branch, with a test, within the session's long end, and run again; a gate that cannot pass by the long end is written up (the step, the first error line, what was tried) in the chain's note and the session moves on. A branch is never landed with `--force`, never by skipping a step, and never with a page's default figure moved.
- **The daily run's steps are repaired, never bypassed:** no test is skipped or marked expected-failure to make the run green; the fault is found and fixed with its test. A warning that became an error (a dependency's new version) is fixed in the code that raises it, and the dependency pinned where the repository pins the others.
- **Default-neutral:** no page's default figure moves, no ruling is made, nothing is released on Redivis, no letter or email is sent, nothing is posted, no page opens to visitors (`site/lib/release.ts` untouched), no backfill of a periodical is run (the owner approves backfills himself).
- **The report of every session** in the form of chain 145's sessions: what it did, with commits; what it found; "Decisions made without you"; "For Samuel's ruling". Short bullets, not prose paragraphs. Each figure the session writes to a table is traced to its source document and page or endpoint.
- **GitHub reads** with this machine's token, at most 60 requests a session; the `gh` CLI where it is signed in, else the API.
- **The weekly Claude limit:** stop at it and resume at its reset, nothing else stops the chain.

Read first: `docs/state/review_2026-10-31_portable.md`, `docs/state/review_2026-10-30_code_ask_board.md`, `docs/reviews/siting-gaps.md` (its table and its last state section), the newest `queue/summary/*-health.md`, `docs/machines.md` ("The landing gate", "The chain worker"), `CLAUDE.md`.
In the rules above, read "Session 2862" as session 3205 and "session 2885" as session 3218 (the rules are chain 147's, carried word for word).

Also read first: chain 181's note (`docs/state/note_<its day>_data_c181.md`), chain 180's (`docs/state/note_2026-11-06_data_c180.md`), chain 177's (`docs/state/note_2026-11-06_data_c177.md`), the owner's chain 157's (`docs/state/note_2026-11-07_data_c157.md`), and the chains' session reports under `archive/sessions/`.

## Session 3205: the next file, the ground, chain 181's first unfinished step

Long end 1:30. Pulls: GitHub only.

1. Write the successor file for this machine in this file's form (`machine: data`, Opus 5.5 high effort, at least fourteen sessions numbered from the first free numbers after 3218, the first free file number on origin's main and every branch): every step of this chain that its note says did not finish, then the siting gaps rows still open that a public US source can close without a ruling, then the daily run's seven days and the records; these rules word for word. Commit it alone, push it to main, `git status -sb`.
2. `scripts/precheck.py` from the main checkout; memory and disk free; `scripts/freeze.py status`.
3. Chain 181's first unfinished step, written by session 3173 of chain 181: chain 181 landed (`e57227f45`, with chains 176, 177 and 180), so the step is session 3206's.

## Sessions 3206 and 3207: chain 181's other unfinished steps

Long end 2:30 each. Pulls: as the step of chain 181 says. Written by session 3173 of chain 181, in chain 181's order:

- **Session 3206: the first daily runs with the guards** (chains 168 to 181). This machine's run from 17:00 UTC on 6 November (`runs/data_machine_status.txt`, the `dm_` rows of `erw_health`; `dm_test_findings` expected to pass), and the runner's run from 14:00 UTC on 7 November. That is the first runner run with chain 151's board guard, since 6 November's was gated (chain 177's session 3109). Read its `board_tests` and `package tests` lines; the latter should pass after sessions 2884 and 3161. Each failed step opened, a fault of this repository's code fixed with its test. If a run has not happened when this session starts, say so, take the next row and come back to it.
- **Session 3207: the owner's rulings, if any are written** (chains 153 to 184's notes, among them ERCOT `/misapp` in the daily run, the deals backfill, the four old wip branches, the pace of the chains): carried out where written in `docs/` or a queue file; with none, say so and take the next row below.

## Session 3208: ERCOT's four coincident peaks of summer 2026, again

Long end 1:30. Pulls: at most 10 requests to www.ercot.com, robots first, never `/misapp` or `/misdownload`.

Siting gaps row "ERCOT | Transmission and 4CP | the four peaks of summer 2026", if chains 153 and 155 did not close it: ERCOT's NP9-83-M is due by 1 December 2026. If posted on an allowed page, `ercot_4cp.py` takes it under the data lock; if not, say so and the row waits.

## Session 3209: the four peak intervals' node prices

Long end 2:00. Pulls: at most 10 requests, only once the four intervals are known.

Siting gaps row "ERCOT nodes | Node panel | a node's price in the four peak intervals": the 15-minute real-time settlement point prices of those four intervals only, from a page ERCOT's robots file allows (NP6-905-CD's own listing is under `/misapp`: if no allowed route holds them, say so and the row waits).

## Session 3210: the tariff registry, the next utilities

Long end 2:00. Pulls: at most 25 requests, robots and terms first.

`utility_large_load_tariffs`: the next utilities under the All grids tab's rows that chains 147 to 155 did not read, each through a commission's public filed copy; each figure with its page; the table written with `runs/c147/write_table.sh`.

## Session 3211: the connection rules and the interruptible riders, continued

Long end 2:00. Pulls: at most 25 requests.

`large_load_connection_rules` and the interruptible riders (chain 153's sessions 2924 and 2925, and chain 160's): the grids and utilities not yet reached, only stated figures.

## Session 3212: the tab wired to what chains 147 to 184 hold

Long end 2:00. Pulls: none.

As chain 153's session 2923: every held table that fills a cell of the All grids tab, on a branch, every figure keyed to its table and row, `docs/methods/siting.md` extended, `siting_page.py` and `gaps.json` rebuilt; the gate; the push.

## Session 3213: the siting gaps file and the records

Long end 1:30. Pulls: none.

As chain 153's session 2926: a new dated state section in `docs/reviews/siting-gaps.md`; `package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009; `scripts/licenses.py tables/write/check` and `warehouse/redivis/release_v1.py --check` after every new table.

## Session 3214: the daily run's seven days

Long end 1:00. Pulls: GitHub's API, at most 30 requests.

As chain 153's session 2927: each scheduled job's last seven days, each failed step with its first error line, a fault of this repository's code fixed with its test; the page files the runner rebuilds compared with the data machine's own build, a thinned file put back and its builder fixed.

## Session 3215: the data machine's own run

Long end 1:00. Pulls: none.

As chain 153's session 2928: `runs/data_machine_status.txt` and the `dm_` rows of `erw_health` for the week, each failed step opened.

## Session 3216: the Stanford draft

Long end 2:00. Pulls: Redivis's API only, at most 150 requests, the branch merged with main first.

As chain 153's session 2929. Nothing released.

## Session 3217: the note

Long end 1:00. Pulls: none.

`docs/state/note_<the day>_data_c185.md` in chain 147's note's form.

## Session 3218: the next file, the landing, the queue

Long end 1:00.

1. The successor file (written by session 3205) updated with what this chain did not finish, first in its order; pushed to main alone.
2. Land this chain's own data branch: merge origin/main, the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC.
3. Then `python scripts/chain_queue.py next`, and run the file it prints the same way.
