# Chain of 8 November 2026: sessions 2918 to 2931, data machine (lab-desktop), unattended: chain 151's unfinished steps, the siting gaps still open, the daily run's week, the records

machine: data

Written by session 2904, the first session of `queue/done/151-day-7-november-data-large-load-continued.md`, at that file's instruction ("at least fourteen sessions numbered from the first free numbers after 2917"). The next free number in `queue/next`, `queue/todo`, `queue/parked` and `queue/done`, on origin's main and on every branch, was 153 (149 and 150 the code machine's, 152 the personal laptop's). This file takes sessions 2918 to 2931; none was named by a commit or a file on origin's main or its branches when this was written. The first session checks again, skips a taken one upward and says so. Session 2931 of chain 151 updates this file at chain 151's end: sessions 2918 to 2920 then hold the steps chain 151's note says did not finish, in chain 151's order. Model: Opus 5.5, high effort. This machine runs one Claude Code session, this chain, and nothing else.

## Why this chain

Chains 147, 148 and 151 repaired the daily run, landed the stuck branches, started the large-load dataset and finished the Ask evaluation. This chain finishes what chain 151 did not, takes the siting gaps rows still open that a public US source can close without a ruling, reads the daily run's week, and brings the records up to date. The owner's rule of 24 October and 5 November holds first: no new foreign country's or foreign operator's source.

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

Read first: `docs/state/review_2026-10-31_portable.md`, `docs/state/review_2026-10-30_code_ask_board.md`, `docs/state/review_2026-10-29_portable.md`, `docs/state/review_2026-10-29_code.md`, `docs/reviews/siting-gaps.md` (its table and its last state section), `queue/summary/2026-11-04-health.md`, `docs/machines.md` ("The landing gate", "The chain worker"), `CLAUDE.md`.
In the rules above, read "Session 2862" as session 2918 and "session 2885" as session 2931 (the rules are chain 147's, carried word for word).

Also read first: chain 151's note (`docs/state/note_<its day>_data_c151.md`), chain 148's (`docs/state/note_2026-11-07_data_c148.md`), chain 147's (`docs/state/note_2026-11-06_data_c147.md`), and the three chains' session reports under `archive/sessions/`.

Updated by session 2917 of chain 151 at its end: chain 151's note is `docs/state/note_2026-11-06_data_c151.md`. Its list of steps not finished names the session of this file that takes each (2918, 2920 to 2925, 2927, 2928); one more step joins session 2927: the monthly builds' page files (`site/data/mix/`, `site/data/curtailment_profile.json`) held to their tests after `run_monthly.sh`, as session 2913 held the board's, before the run of 3 December.

## Session 2918: the next file, the ground, chain 151's first unfinished step

Long end 1:30. Pulls: GitHub only.

1. Write the successor file for this machine in this file's form (`machine: data`, Opus 5.5 high effort, at least fourteen sessions numbered from the first free numbers after 2931, the first free file number on origin's main and every branch): every step of this chain that its note says did not finish, then the siting gaps rows still open that a public US source can close without a ruling, then the daily run's seven days and the records; these rules word for word. Commit it alone, push it to main, `git status -sb`.
2. `scripts/precheck.py` from the main checkout; memory and disk free; `scripts/freeze.py status`; the Anthropic key's state as chain 147's session 2862 read it.
3. **Chain 151's first unfinished step, the board's five questions regraded** (its session 2886): `warehouse/chat/eval/expected_s1122.py` run for today's keys (the live set, the anon key, reads only), `eval_s1113.py --grade --set s1122` on them, and the run's row of `runs.json` and `ask-history.md` written again. k03's fault in the route ("Cannot read properties of undefined (reading 'aggregation')") is the code machine's: say so in the note, do not fix site code here.

## Sessions 2919 and 2920: chain 151's other unfinished steps

Long end 2:30 each. Pulls: as the step of chain 148 says. **Session 2919, the controllable load's path, read where ERCOT states it** (chain 151's session 2893; at most 10 requests to www.ercot.com, robots first, never `/misapp` or `/misdownload`): the Planning Guide's Section 9 and ERCOT's large-load interconnection page under `/services/` or `/gridinfo/`, for a stated step or duration of a Controllable Load Resource's connection; into `large_load_connection_rules` with session 2924 if one is stated.

**Session 2920, the TPIT refresh** (chain 151's session 2891; at most 10 requests, robots first): the newest Transmission Project and Information Tracking workbook on ERCOT's allowed pages, against `ercot_transmission_projects`' July 2026 base; a newer one written with the locked write scripts and `nodes.json` rebuilt. A step that waits on a ruling is not done: its question goes to this chain's note.

## Session 2921: the tariff registry, the utilities still missing

Long end 2:00. Pulls: at most 25 requests, robots and terms first.

The utilities chains 147 to 151 could not read, each tried once more where a public route now exists (a commission's filed copy, a filing named in another filing), and the next utilities under the All grids tab's rows: Duquesne Light, Con Edison, Eversource, PG&E. Into `warehouse/sources/large_load_tariffs/`, each figure with its page; the table written with `runs/c147/write_table.sh`.

## Session 2922: ERCOT's four coincident peaks of summer 2026

Long end 1:30. Pulls: at most 10 requests.

Siting gaps row "ERCOT | Transmission and 4CP | the four peaks of summer 2026": ERCOT's Four Coincident Peak calculation (NP9-83-M), due by 1 December 2026, through ERCOT's public pages that its robots file allows. If it is not posted, or only behind `/misapp` or `/misdownload`, say so; the row waits.

## Session 2923: the tab wired to what chains 147 to 151 hold

Long end 2:00. Pulls: none.

Every held table that fills a cell of the All grids tab (`tariffs.json` once a tab row's utility is in the registry; the node wires utility, county and TPIT where chain 148 wired them), on a branch, every figure keyed to its table and row, `docs/methods/siting.md` extended, `siting_page.py` and `gaps.json` rebuilt; the gate; the push. The tab at 390 and 1280 read with the internal cookie: every new cell a figure or "not held", never a blank.

## Session 2924: the connection rules, continued

Long end 2:00. Pulls: at most 25 requests.

`large_load_connection_rules` (chain 151's session 2888): the grids and utilities it did not reach, only stated figures, a process that states no duration with its words and no number.

## Session 2925: interruptible riders, continued

Long end 1:30. Pulls: at most 20 requests.

Chain 151's session 2898 for the utilities added since.

## Session 2926: the siting gaps file and the records

Long end 1:30. Pulls: none.

A new dated state section in `docs/reviews/siting-gaps.md`, every row this chain moved; `package/tools/build_tables.py --check` and the tests of sessions 1001, 1008 and 1009, rebuilt if stale; `scripts/licenses.py tables/write/check` and `warehouse/redivis/release_v1.py --check` after every new table (chain 147's session 2885 found both stale after a daily run added a table); this chain's tables' method notes checked against their code.

## Session 2927: the daily run's seven days

Long end 1:00. Pulls: GitHub's API, at most 30 requests.

As chain 147's session 2884: each scheduled job's last seven days, the daily run's runs opened one by one, each failed step with its first error line, a fault of this repository's code fixed with its test; the "Stale on main" line of the newest summary quoted. **And the page files the runner rebuilds:** compare `site/data/mix/*`, `site/data/board.json`, `site/public/board/` and `site/data/curtailment_profile.json` on main with the data machine's own build (`warehouse/run_data_machine.sh`'s page steps): a file the runner thinned (fewer months, years or rows than the history holds; chain 147's session 2885 put 164 back) is put back and the runner's builder fixed so it never writes a thinner file than the one committed.

## Session 2928: the data machine's own run

Long end 1:00. Pulls: none.

`runs/data_machine_status.txt` and the `dm_` rows of `erw_health` for the week: each failed step opened, a fault of this repository's code fixed with its test (chain 147's session 2884 fixed `dm_test_findings`).

## Session 2929: the Stanford draft

Long end 2:00. Pulls: Redivis's API only, at most 150 requests, the branch merged with main first.

As chain 147's session 2882: `--reconcile`; this chain's public tables into the Stanford draft in a plain upload, under the data lock and never in the background; `--reconcile`; `docs/state/redivis_v1_ready.md` and `release_v1.STORAGE_HELD` brought to what the draft holds. Nothing released.

## Session 2930: the note

Long end 1:00. Pulls: none.

`docs/state/note_<the day>_data_c153.md` in chain 147's note's form: what landed, what did not and why, the decisions made without the owner, the questions for his ruling, the cost of any model calls.

## Session 2931: the next file, the landing, the queue

Long end 1:00.

1. The successor file (written by session 2918) updated with what this chain did not finish, first in its order; pushed to main alone.
2. Land this chain's own data branch: merge origin/main, the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a `task/` branch, not between 14:00 and 16:15 UTC.
3. Then `python scripts/chain_queue.py next`, and run the file it prints the same way.
