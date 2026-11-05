# The reports of 20 and 21 October, read as a reviewer

Energy Research Warehouse (ERW), session 449, 21 October 2026, about 07:10 to 07:55 UTC, on portable-laptop (code role), branch `wip/441-450-third`. The chain `queue/done/017-night-21-october-third.md`, "Session 449". No code changed, no pull, no model call. Every judgment below names the report it reads and the evidence that holds it: a commit, a file on a named branch, an exit code the report itself prints.

**36 reports were found for the 76 session numbers 365 to 440.** 25 of them are on `origin/main` (365 to 389), 10 on `wip/015-land` and the session branches (402 to 407, 409, 410, 413, 414), and one on `wip/findings-oct20` (420). Where a report stood in two versions (365, 366 and 381 on `wip/377-reliability` or `wip/381-five-tools` and on main), main's later version was read.

## How it was checked

The mechanical checks are scripts under `runs/chain_oct21_third/s449/` (outside git), each with its output kept:

| Script | What it does | Output |
|---|---|---|
| `find_reports.sh` | every `archive/sessions/SESSION_<n>_REPORT.md` for 365 to 440 on every remote branch, with its blob and last commit | `reports_found.txt` (480 lines), `reports_latest.txt` (36) |
| `hashes.sh` | every commit a report cites in backticks: present, and an ancestor of `origin/main` or not | `hashes.out`: 71 commits, 66 in main, 5 not (402's `0f5a17b5` and `c9ece56d`, 409's `43fd0b46`, 410's `e18cfa90`, 413's `6ead3c28`: all on their unlanded `wip/` branches, as their reports say) |
| `files.sh` | 50 files the reports say they wrote, read on the branch each names | `files.out`: 49 present; 1 absent, `docs/brand/review-403` on `wip/403-s`, which session 403's report says waits under "To finish" |
| (inline) | every `wip/` and `task/` branch: in `origin/main` or how many commits ahead | `branches.out` |
| (inline) | `git merge-tree --write-tree` (read only, no ref moved): `origin/main` with `wip/015-land`, and `wip/015-land` with `wip/401-s` and `wip/408-s` | `mergetree_015.out`, `mergetree_401.out`, `mergetree_408.out`: exit 0 each, no conflict |

The "done" of each session is its paragraph in the chain file that asked for it: `queue/done/012-day-20-october-code.md` (365 to 372), `011-day-20-october-data.md` (373 to 380), `014-night-20-october-code.md` (381 to 383), `013-night-20-october-data.md` (384 to 386), `016-day-21-october-data.md` (387 to 389), `015-day-20-october-code-pm.md` (401 to 415), `016-night-21-october-data.md` (431 to 440). Session 420 was asked by no chain file in the queue; its report names its own brief.

The landings found on `origin/main` since 20 October, by GitHub's merge commits: `e468065a` (`task/365-366`, 19:10 UTC on 20 October), `288ee9a9` (`task/373-379-day`, 21:11), `1885da54` (`task/380-morning`, 21:24), `dfbe8e08` (`task/384-lock`, 21:49), `fcdff2d8` (`task/385-redivis`, 22:05), `7e08c274` (`task/386-morning`, 05:36 UTC on 21 October), `d88b74ed` (`task/387-health`, 06:24), `6134201b` (`task/388-389`, 06:51), `bb49c9e0` (`task/381-382`, 07:05).

## One line a session

Verdict words: **met** (the report's own evidence shows the "done"), **partly** (part of the "done" shown, the rest named as not done or waiting), **not met** (the evidence does not show the "done").

- **365** met: the queue reads a file's `machine:` line; `tests.test_session365` exit 0 (17 tests), the dry runs' outputs named; landed with 366 as `e468065a`, snapshots `s366-before` and `-after` with 25 expected differences.
- **366** met: `wip/345-impact` landed (`e468065a`); suite at `2bbfdc68` exit 0 (4,679 tests); `/impact` 340 of 340 in check-values. The `/impact` floors, part of its "done", were deferred to 367 and written in 381's landing checks (`a94c7f1f`, in main).
- **367** partly: `wip/348-map` is in main (`origin/wip/348-map` and `005b590d` are ancestors of `bb49c9e0`), but its "Landing" section still reads "(written at the landing)" on main: the gate it was asked to pass is recorded nowhere in its own report.
- **368** partly: the route was proven on the local build (`check-download.mjs` exit 0, 10 of 10 whole; nine tables identical byte for byte) and is in main (`a20df49d`); the check against production after the deploy, which the report gives to the orchestrator, is recorded in no report found.
- **369** met: the day both tables hold and the dated event keys; full check-values 6,639 of 6,639 exit 0 on the local build; in main (`13ff2c0b`); todo 008 in `queue/done/`.
- **370** partly: the three fixes are in main (`422228e1`), the cycle run later by session 381 (check-battery-scenarios 0, check-datacenter 0); its own build and checks were not run (stopped by the memory reaper at 19:44 UTC), and its "Landing" reads "(the orchestrator's)".
- **371** partly: `docs/security.md` and the cookie fix are in main (`f4c1566f`); the report lists the CLAUDE.md patch "For Samuel's ruling", but `be202c6f` (19:38 UTC, on `wip/367-372-day`, in main) applied it the same hour, and the report was not brought to say so.
- **372** partly: the day note is on main; the report says the queue file was pushed "with a snapshot before and after: see below", and no snapshot is below.
- **373** met: 71 tables restored from the archive, validator exit 0, coverage `--only` exit 0, `sync.py --check` 201 current; landed in `288ee9a9`.
- **374** partly: the sources check green (338 and 338, commit `0d299d7f`); the load exit 1, 31 tables refused as older than the live copy, explained and not overridden.
- **375** met: the package spliced, `release_v1.py --check` exit 0, suite exit 0 (4,700 tests); `9115b289` in main.
- **376** met: `dm_node_rt` in the daily run, `tests.test_session376` exit 0, the first real run under the lock (22 real-time days); 0 of 40 ERCOT requests; in main (`3b509aba`).
- **377** met: root causes for 6 to 20 October, `tests.test_session377` exit 0; the storage refusal made a skip (reversible, listed).
- **378** met: one verdict word a table, `licenses.py check` exit 0, four letters drafted and not sent, 0 requests of 6.
- **379** not met, by its own gates: probe (a) stopped at `build_status.py --gate` exit 1, as its task file requires; probe (b) found no 2021 intervals in 6 of 6 requests. Both stops are correct and stated.
- **380** met: the morning note and `queue/next/013-night-20-october-data.md` (`3dafca63`); the landing of 373 to 379 with 0 differences.
- **381** partly: the five packs' tables and the new replication (304 of 304 figures equal) are in main via `bb49c9e0`; every check that reads a built site was "not run" (three builds stopped on statement timeouts), and the landing of 367 to 371 it ran stood with five browser checks failing (its decision 2).
- **382** met: the trader path, 32 shots (`docs/brand/review-382/`, 38 files on main), the hold fix `c5c3b806` with a test that fails without it; restricted check-values 240 of 240 on the seller page. The full check-values run timed out (exit 1, stated).
- **383** partly: the night note and the queue step are recorded; two later commits under its name, `1bd23cc8` (the shape-premium draft page and `tests/test_session383.py`) and `accad477` (`check-table-downloads.mjs`), made at 06:17 and 06:25 UTC on 21 October and in main through `bb49c9e0`, are not in its report, which was last written at 03:10 UTC (`922cb154`).
- **384** partly: part (a), the console-close fix, landed (`dfbe8e08`, `tests.test_session384` exit 0, 0 differences); part (c) drafted; part (b) not run (stopped at Samuel's instruction of 05:15 UTC, carried to 387).
- **385** met: `docs/redivis/organization-move.md`, 5 of 20 Redivis requests and 3 of 4 docs requests; `release_v1.py --check` exit 0; landed (`fcdff2d8`).
- **386** met: the night note and `queue/next/016-day-21-october-data.md` (`bfca6f1a`), 0 differences; the suite exit 1 on `test_session166` cured by cherry-picking `b39bada3`; landed (`7e08c274`).
- **387** partly: 21 October's file written at 06:05 UTC with 46 steps and pg_cron's root cause; its "done" asked for the day after GitHub's daily run had ended, and that run is dispatched at 14:00 UTC (the report says so and why).
- **388** met: 4 of 16 requests, two records (83, 84), `licenses.py check` exit 0; the one verdict that would hold a public table drafted, not written.
- **389** met: the note and `queue/next/017-day-21-october-data-pm.md` (`cfcc5928`), 0 differences; landed (`6134201b`).
- **402** partly: 120 of 120 Digest figures traced (two `check_digest.py` runs together), restricted check-values 64 of 64; not landed; the last commit (`925c0fb8`) restructured the day page after the build that passed, and its type check and shots on that commit are under "To finish".
- **403** partly: the explorer runs on `next dev` (check-values 216 of 216); three production builds exit 1 on statement timeouts, no floor, no shots (`docs/brand/review-403` absent on `wip/403-s`), not landed.
- **404** partly: six builds exit 0, check-values 202 of 202 twice, 12 shots; the floor deliberately not committed; not landed.
- **405** partly: build exit 0, check-values 449 of 449, floors written, 8 shots; `/map`'s floor check exit 1 (its one number held since 21 October); not landed.
- **406** partly: the draft and its notes exist (`tests.test_session406` exit 0), but the figures were read from Supabase through the page code, not from the pages, and the three charts were not made. Samuel's ruling of 21 October leaves the draft unused.
- **407** partly: ten posts with 26 keys read equal from Supabase (`read-407.mjs` exit 0); the ten images not made (three builds exit 1).
- **409** partly: `check-methods.mjs` exit 0 offline, 469 of 469 figures named; the whole suite exit 1 with four of its own failures fixed in `43fd0b46`, and the whole suite not run again; the site read of every page's keys waits.
- **410** partly: the Refreshed column and `tests.test_session410` exit 0 (and exit 1 against the old registry, as it should); three builds exit 1, the shots wait.
- **413** met: the review written (`6ead3c28`), 35 of 40 requests logged, `tests.test_session413` exit 0 and exit 1 against a spoiled copy; its own "done" asked only for a push.
- **414** partly: the ledger of 351 to 413 (48 items), `test-waits-ledger.mjs` 212 of 212, `tests.test_session414` exit 0; its check on a built site was not run (three builds exit 1), and on `next dev` 29 of 32.
- **420** partly: ten findings with their files, `hunt_oct20.py check` 10 of 10, `tests.test_session420` exit 0; the whole suite exit 1 with 12 errors and failures listed and none explained, and its precheck was a dry run "run late". Not asked by any chain file in the queue.

## Session numbers with no report found anywhere

40 of the 76 numbers have no report on any remote branch at 07:30 UTC on 21 October:

| Numbers | What the evidence says |
|---|---|
| 390, 391 | queued, not yet run: `queue/next/017-day-21-october-data-pm.md` (written by 389, `cfcc5928`) |
| 392 to 400 | assigned to no chain file in `queue/` |
| 401, 408 | ran, no report: `wip/401-s` holds 2 commits (`c974e64b`, `cbef937f`, 07:06 and 07:10 UTC) and `wip/408-s` 3 (`b7323ad6`, `9e73d992`, `08c023c4`); neither branch is in `wip/015-land` |
| 411, 412, 415 | no branch and no commit naming them (`git log --remotes --grep`): the 015 chain's performance pass, accessibility pass and evening note were not run, so no `docs/state/review_2026-10-20_evening_code.md` |
| 416 to 419, 421 to 430 | reserved for the code machine's self-written chains (the 016 night chain's opening); no such chain file exists |
| 431 to 440 | the data machine's night chain, taken by lab-desktop at 07:06 UTC (`d25da8d8`); no report pushed when read |

## Where a report claims more than its checks show

1. **The landing of `task/381-382` (`bb49c9e0`, 07:05 UTC on 21 October) has no record.** It carried sessions 367 to 372, 381, 382 and the two unreported 383 commits to main; no report found gives its landing checks or the rule 8 snapshot pair (the 383 note's "To finish" names `s383-before` and `s383-after`; no report holds their comparison). Reports 368 to 371 still say "(the orchestrator's)" and 367 "(written at the landing)".
2. **Session 383's report covers a note and a queue step**; the branch it landed on also carries a page change and a check change under its name (`1bd23cc8`, `accad477`).
3. **Session 371 lists the CLAUDE.md patch for Samuel's ruling**, while `be202c6f` applied it; session 414's ledger reads the report, so the page lists a ruling already acted on.
4. **Session 372 says "see below" for a snapshot pair** that is not below.
5. **Session 409's "469 of 469"** stands on the offline keys file; the whole suite after its four fixes was not run again (the nine modules near the change were, exit 0).
6. **Session 420's suite exit 1** (12 errors and failures, among them `test_session49`, `51`, `78`, `80`, `164`, `273`, `308`) is listed without a cause for any; the report's file list is long and its checks do not separate failures of this machine's tables from failures of its code.
7. **Session 402's build exit 0 was at `c9ece56d`**; the report's last commit `925c0fb8` changed the day page after it, and the type check on that commit is under "To finish", not done.
8. **Session 381's landing step 3 reads "check-values 0"** beside five browser checks that failed; the report says so and decides to land anyway (decision 2), so the claim is stated, but a reader of the table alone sees a green gate.

## Where two sessions' decisions conflict

1. **`erw:iso_queue_statistics`'s license.** Session 374 wrote it into Supabase's `sources` table as `internal` (the live table takes no "unsettled"); session 381's merge kept the code machine's row, `public`, in `sources.csv` (on main now); session 405 reads the table as held for review and not in the catalogue; the release package lists it "no" (license needed). Until the next load of the sources, the live set and main's registry disagree on one source.
2. **`nyiso_load_queue`.** Session 375 kept it public in coverage against the builder's `internal`; session 410 found its header "public, with a caution", the registry `internal` and `license_status.csv` "license needed". Three sessions (375, 380's note, 410) ask the same ruling three ways.
3. **The check-values floors.** Session 404 did not commit its floor so that the branches would not conflict; session 405 committed its floor in the same place; session 408 added two more floors (`08c023c4`) and is not in `wip/015-land`; session 403 changed the floor-writing rule that 408 took "as written" (`b7323ad6`). Four branches edit `check-values.mjs` (403, 404, 405, 408) and two the floor file (405, 408). Git merges them without a conflict today (`mergetree_*.out`, exit 0); the disagreement is of method: one explorer's floor is on the branch, another's is a file in `runs/`, and the third's waits under "To finish".
4. **The session numbers.** The 016 night chain reserves 416 to 430 for the code machine's self-written chains; session 420 took 420 for the portable laptop's findings run and left "room for 416 to 419" only.
5. **What happened to session 386.** Session 434's paragraph (`016-night-21-october-data.md`) says 386 never ran ("no note, no next file"); 386's report, its note `docs/state/morning_2026-10-21_night.md` and its landing `7e08c274` at 05:36 UTC say it did. 434 would write a page on a stop that the record says ended at 05:15 UTC.
6. **The cause of the database's timeouts.** The 016 night chain names "this machine's loads of 20 October" as the likely cause; session 374's load ended at 20:50 UTC, 2 hours 40 minutes before the timeouts began (about 23:30 UTC, 383's note); session 387 found pg_cron's 47 "job startup timeout" failures over the same 23:30 to 05:15 UTC window and says the cause is not visible from inside the database. The builds of the 015 sessions failed from 03:13 to 05:14 UTC (406, 407, 409, 410, 414) and passed from 05:34 UTC (404, 405), the same hour pg_cron's runs succeeded again (05:30 UTC, 387).
7. **The license hold on the periodicals.** Session 402 holds the Digest's story sections while `news_index` is held; it lists the home page's Digest stories, the Roundup and the e-mailed Digest as not held. One table is held on one page and shown on three others.
8. **Two sets of LinkedIn material.** Session 407 drafted ten posts from `series|` keys; session 420 made ten findings with square charts "for LinkedIn". 420's claim check at 01:10 UTC found 407 "not started"; 407 ran from 04:29 UTC. Neither knows the other's set. (Their one shared figure agrees: ERCOT's peak premium, 14.52 USD per MWh in 2025, in 403 and 420.)
9. **The held-table freshness line.** Session 404 built `HeldFreshness` for a table held for review and named `iso_queue_statistics` as the other user; session 405 used the shared `Freshness`, which says "not in the site's catalogue" for the same case.

## The five items that most need Samuel's eyes before the landings pile up

1. **Record the landing of 07:05 UTC before the next one.** `bb49c9e0` put sessions 367 to 372, 381 to 383 on main with no report of its checks or its rule 8 comparison (above, claims 1 and 2). The next landing will merge on top of it; once it does, the before and after of this one cannot be separated. Evidence: `git log origin/main` (`bb49c9e0`), reports 367 to 371 and 383 on main.
2. **The 015 chain stopped short, and 13 unlanded branches touch the same files.** `wip/015-land` holds 402 to 407, 409, 410, 413 and 414 (40 commits ahead of main); `wip/401-s` and `wip/408-s` hold work with no report; 411, 412 and 415 never ran. Git merges `wip/015-land` into main, and 401 and 408 into it, without a conflict (`mergetree_*.out`, exit 0), but four of the branches edit `check-values.mjs`, three `site/lib/release.ts`, and of the ten in `wip/015-land` only 402 (before its last commit), 404 and 405 passed a check on a production build: 403 and 414 were checked on `next dev`, 409 offline, 406, 407 and 410 not at all, and 413 changes no page. One combined gate, run once the database answers, is what stands between them and main. Evidence: `branches.out`, `mergetree_015.out`, conflict 3.
3. **The database before 14:00 UTC.** The timeouts and pg_cron's failed starts share one window (23:30 to about 05:30 UTC); today's daily is dispatched through pg_cron at 14:00 UTC; session 387 asks for `cron.use_background_workers` or a look at the project's resource graphs, which no session can reach. Evidence: reports 383, 387, 404 to 410 (the build times), conflict 6.
4. **The license record disagrees with itself in four places while the holds are in force on the site.** `iso_queue_statistics` (public on main, internal in Supabase), `nyiso_load_queue` (three records, three answers), `impact_tax_rules` (388's draft verdict would hold it, 41 to 42), and the periodicals (402: stories held on `/digest`, shown on the home page, the Roundup and the e-mail). Evidence: conflicts 1, 2 and 7; reports 374, 375, 388, 402, 410.
5. **Two chain premises the record contradicts.** The data machine's night chain will run 434 on "386 never ran", which 386's landing disproves; and the portable laptop ran session 420 as a data machine (`.erw/machine.json` role `data`, its report's first line) while tonight's chain names it a code machine, and 420 sits in the code machine's reserved numbers. Evidence: conflicts 4 and 5; reports 386 and 420; `queue/done/016-night-21-october-data.md`.
