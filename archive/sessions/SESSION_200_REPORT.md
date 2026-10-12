# Session 200 report: what the roadmap needs to know, on lab-desktop

lab-desktop (data role), 12 October 2026 from 01:43 UTC (11 October, 18:43 Pacific). Unattended, one session. Branch `task/200-roadmap-inputs`. Model spend USD 0, no model call. No pull from any publisher. Nothing deleted. No page, test, schedule, scanner or release gate file touched.

## Read these first

- **The two documents are written, every number from a command.**
  - `docs/state/data_2026-10-11.md`: 198 tables, 37,036,977 rows, all on this machine, each `current` against Redivis.
  - `docs/state/rulings_2026-10-11.md`: 181 items waiting for you in 25 reports after session 171, merged into 107 entries.
- **NOT LANDED at the first push (02:13 UTC).** GitHub's check of `task/200-roadmap-inputs` failed at "Tests (tests/)" and the merge was skipped (run 38194934007), as it did for `task/198-battery-data` and as sessions 195 to 197 report: `main` itself fails that step since `483c412d`. The branch is on GitHub, complete. Nothing was deployed. What happened after is in "The landing".
- **The storage offers mismatch is repaired, and it will come back tomorrow.**
  - Before: the daily offers table held 11 August days, the monthly offers and awards tables 10. `limit_mwh` of August 2026: 5,362,152.4 summed from the daily table, 4,873,801.6 in the monthly one. 76 of 693 month and variable sums differed.
  - After: 11 days in all three, 5,362,152.4 in both, 0 of 693 differ. `tests.test_session116` `Records.test_the_tables_on_this_machine_add_up`: exit 1 before, exit 0 after.
  - Why it was so: the runner builds all four tables every day and uploads them. This machine's sync restores a table only when Redivis holds more rows or a newer timestamp. A monthly table rewritten whole has neither, so the file of 10 October stayed.
  - **Is the step part of tomorrow's daily run? On the runner, yes; on this machine, no.** After tomorrow's sync the daily table gains a day and the monthly ones do not. For your ruling, first item.
- **The quantities step is not in this machine's daily run.** It is on `task/198-battery-data`, whose check failed (GitHub run 38172045438), so it is not on `main`. `ercot_as_quantities` stands at 4,800 rows to 13 October 04:00 UTC and falls a day behind each day from then.
- **ERCOT's ceiling: 2,477,352 of 3,000,000 load zone rows, 82.6 percent, 522,648 of room.** The table gains 576 rows a day: about 907 days at that pace.
- **72 of 198 tables are over their cadence.** 40 are stuck or on no schedule; 32 were refreshed in the last three days and their publisher gave nothing newer. Each with its reason where a file gives one.
- **The runner's run of 11 October failed two store steps** (`supabase_load` and `redivis_upload`, exit 1, in its commit `ceafacf8`). One table shows it: `price_board_spreads`, 2,285 rows here and in Redivis (10 October), 2,283 in coverage and the archive (11 October).
- **Of the 107 ruling entries, 9 look done or already answered and 5 ask nothing.** They are marked, not removed. 93 are open.

## What to review

On `main` once the branch lands; until then put `task/200-roadmap-inputs` in place of `main` in each address.

- The state of every table: https://github.com/SamuelEnrique/erw/blob/main/docs/state/data_2026-10-11.md
  - "Read these first" is written by hand (https://github.com/SamuelEnrique/erw/blob/main/docs/state/data_2026-10-11_notes.md); everything under it is generated.
  - The reasons written by hand, eight tables, each with its evidence: https://github.com/SamuelEnrique/erw/blob/main/docs/state/data_2026-10-11_reasons.csv
- Every open ruling: https://github.com/SamuelEnrique/erw/blob/main/docs/state/rulings_2026-10-11.md
- The lab desktop today, section "The lab desktop, as it stands (session 200)": https://github.com/SamuelEnrique/erw/blob/main/docs/machines.md
- The generator: https://github.com/SamuelEnrique/erw/blob/main/scripts/data_state.py
- The two small helpers of the rulings document: https://github.com/SamuelEnrique/erw/blob/main/scripts/waits_list.mjs and https://github.com/SamuelEnrique/erw/blob/main/scripts/check_rulings.py
- What you see today of the same list, 146 items (the branch reports are not on `main`): https://erw-flame.vercel.app/internal/waits

## What was done

1. **`docs/state/data_2026-10-11.md`.** A row per table of `coverage.csv`: rows, first and last timestamp, days since the last row, interval, license and whether it may reach the site (with what the live set does with it), the script that writes it, coverage's last run, whether a daily run refreshes it, the archive and Redivis state. Then ERCOT's ceiling, and "Stale or stuck" in three lists.
   - The cadence rule, mine: the finest interval coverage gives a table sets how old its last row may be (5 minutes to a day: 3 days; a week: 14; a month: 62; a quarter: 184; a year: 730). An event or snapshot table is listed when nothing has rewritten it for 8 days.
   - A reason is written only where a file gives one: `paused_sources.csv`, `known_gaps.csv`, the table's newest row of `run_status.csv`, the file's own header, or the reasons file. Otherwise the line says what the files do say: the writer, the run script that names it, the newest run.
2. **`docs/state/rulings_2026-10-11.md`.** The item set is the page's own: `site/scripts/build-waits.mjs`, run on `main`'s reports (146 items in 21 reports) and on those plus the four branch reports (181 in 25). Grouped in eleven areas, duplicates merged, each entry with its report and line, what is asked, and a recommendation. No ruling is made.
3. **The rollup.** Under the data lock, 01:47 UTC, held under a minute: `ercot_storage_dam_awards.py`, then `ercot_storage_dam_offers.py`. Two tables written on this machine, 252 and 819 rows, the same counts as before.
4. **`docs/machines.md`.** A new section, "The lab desktop, as it stands (session 200)", in short lines; and one line under the older bullet that said this machine cannot push.

## Checks, with exit codes

None piped; each long output is in `runs/session200/` on this machine.

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 200"` | 0 | 6 of 6; on duty |
| `scripts/freeze.py status` | 0 | no freeze (read at the start and before the push) |
| `runs/session200/storage_state.py warehouse/output` (before) | 0 | August: 11 days daily, 10 monthly; 76 of 693 sums differ |
| `python -m unittest tests.test_session116.Records.test_the_tables_on_this_machine_add_up` (before) | 1 | the failure session 198 reported |
| `ercot_storage_dam_awards.py --out-dir runs/session200/trial` | 0 | a trial: 252 rows, 249 days |
| `warehouse/lock.py acquire --task "session 200: storage monthly rollup" --minutes 30 --wait 10` | 0 | taken by `lab-desktop/8405ee8f` |
| `warehouse/derived/ercot_storage_dam_awards.py` | 0 | 252 rows, 9 months, 249 days |
| `warehouse/derived/ercot_storage_dam_offers.py` | 0 | 819 rows, 9 months, 249 days |
| `warehouse/lock.py release` | 0 | released |
| `warehouse/validate/erw_validate.py` on the two monthly tables and the daily one | 0 | pass, 0 errors, 0 warnings |
| `storage_state.py` (after) | 0 | 11 days in all; 0 of 693 differ |
| the same test (after) | 0 | OK |
| `scripts/sync.py --check --no-git --tables '^ercot_storage_dam_\|^ercot_dam_esr_awards$'` | 0 | current: 4 |
| `warehouse/archive/restore.py <table> --from-bucket --out runs/session200/archive_copy/...`, both monthly tables | 0, 0 | the archive's newest state, read only |
| `runs/session200/compare_archive.py` | 0 | both tables equal the archive's value for value; `retrieved_at` differs on 87 and 23 rows |
| `scripts/sync.py --check --no-git` (all tables) | 0 | "tables in coverage: 198; current: 198; missing: 0; behind: 0; ahead: 0; diverged: 0; not on Redivis: 0; unread: 0" |
| `scripts/data_state.py --data-root . ...` | 0 | 198 tables, 37,036,977 rows, 72 over their limit (40 and 32), 5 with no cadence and an old run |
| `node scripts/waits_list.mjs ... .` (main) | 0 | 21 of 24 reports, 146 items |
| `node scripts/waits_list.mjs ... runs/session200/waits_repo` (with the branch reports) | 0 | 25 of 28 reports, 181 items |
| `scripts/check_rulings.py` | 0 | 181 of 181 named, none over; 107 entries; 0 em dashes |
| `python -m unittest discover -s tests` in the branch's worktree, `ERW_LOCK_EXEMPT=1` | 1 | 3,328 tests: 10 failures, 1 error, 245 skipped. None reads a file this session wrote; see below |

- The suite's 11: `test_session153` (1), `test_session183_replication` (2), `test_session190` (1), `test_session190_replication` (1): the five session 195 names. `test_session182_flow` (5) and `test_session149` (1) also fail in this worktree: the first reads the analysis templates, the second expects a role file a worktree does not have ("role is 'not set'"). Not looked into further: no test was touched.
- The first run of the full sync check was started in the background and its exit code was not read; it printed the same line. The second run's exit code is the one above.

## The landing

- No freeze (`scripts/freeze.py status`, exit 0, read at 02:13 UTC before the push). No force push. `main` had not moved (`fd079835`).
- **First push, 12 October 02:13 UTC.**
  - `node site/scripts/snapshot-live.mjs take before200`: exit 0, 25 pages, 0 failed, 02:13:07 UTC.
  - `git push origin task/200-roadmap-inputs` (commits `847d7418`, `852d1292`): exit 0, 02:13:20 UTC.
  - Vercel on `852d1292`: "Canceled by Ignored Build Step". No deployment was made for the push.
  - GitHub's check, run 38194934007: step "Tests (tests/)" failed at 02:17 UTC; "Site build and check-routes" skipped; job "merge" skipped. The same step failed for `task/198-battery-data` (run 38172045438). The run's log needs a sign-in the machine does not use, so the failing tests' names are not read here. On this machine the suite fails 11 tests in the branch's worktree (above): the five of session 195's list among them, and none that names a file this branch changed.
  - `take after200`: exit 0, 25 pages, 0 failed, 02:18:12 UTC.
  - `compare before200 after200`: exit 0. **"0 differences in all" on the 25 pages.** Expected: no page changed and nothing was deployed.
- **What came after the first push** is added below by later pushes.

## To finish

Only if the branch is still unmerged when you read this. Once `main` passes GitHub's check, from `C:\Users\Shared\Documents\erw-200` on lab-desktop, each its own command:

```
git fetch origin
git merge --no-edit origin/main
C:\Users\Shared\Documents\erw\.venv\Scripts\python.exe C:\Users\Shared\Documents\erw\scripts\freeze.py status
node C:\Users\Shared\Documents\erw\site\scripts\snapshot-live.mjs take before200b
git push origin task/200-roadmap-inputs
node C:\Users\Shared\Documents\erw\site\scripts\snapshot-live.mjs take after200b
node C:\Users\Shared\Documents\erw\site\scripts\snapshot-live.mjs compare before200b after200b
```

- The after snapshot is taken once GitHub's run has merged the branch and Vercel says the deployment has completed. Expected: 0 differences, no page changes.
- If `warehouse/metadata/sources.csv` conflicts in the merge (the runner rewrites it each day), take `main`'s copy: this branch's two lines only move a `last_seen` date.
- The same commits are on `wip/200-roadmap-inputs`.

## Decisions made without you

- **A worktree, `C:\Users\Shared\Documents\erw-200`, holds the branch.** The main checkout stayed on `main` and clean: the daily task commits there at 17:00 UTC, and its sync does not fast-forward a checkout with changes.
- **The rollup wrote two tables, not one.** The offers builder checks each month against the monthly awards table and refuses when they disagree; the awards table was a day behind too. So the awards table was rebuilt first. Both earlier files are kept in `runs/session200/before/`.
- **No coverage, archive or Redivis write after the rollup.** Those stores already hold the runner's tables of 11 October; the rebuilt files equal the archive's value for value. The files' `Retrieved:` lines now name this session's run, so the loader's check on this machine lists the two tables, as it listed them before (their headers were of 10 October).
- **The source registry's two lines travel on the branch.** The builders moved `last_seen` of the two storage sources to 12 October in `sources.csv`. I carried that change to the branch and put the main checkout's file back as committed, instead of a data commit on `main`.
- **The cadence rule and its limits are mine** (above). The split into "stuck" and "refreshed, nothing newer" is mine too.
- **Eight reasons are written by hand**, each from a file's header or a line of session 178's report; the rest are generated.
- **The item set is the page's own script's, not my reading.** So the document holds lines the script lists that ask nothing (5 entries) and rows a report marks closed (entry C16).
- **Session 195's report is read from `wip/195-decisions-one-system`**; the copy on `wip/196-cross-checks` is the same file.
- **An eleventh area, "the three tools together",** beside the ten you named: the hurdle rate, degradation, the usage count and scenario A are asked on all three pages.
- **Entries the files show as done are marked "Looks done" or "Looks answered", with the evidence.** None is removed, and `LAST_ANSWERED` is untouched.
- **Three scripts are new under `scripts/`**: `data_state.py`, `waits_list.mjs`, `check_rulings.py`. They read; none writes a table.
- **`docs/machines.md`: nothing removed.** The older bullet "cannot push" got one line pointing to the new section.
- **The suite's residue was left**: `warehouse/output/raw/madeup_as_prices/` in the main checkout (from session 198's run) and in this session's worktree.
- **GitHub's public API was read** to see the check of `task/198-battery-data` and of this branch (no token; `gh` is not on this machine).

## For Samuel's ruling

- The monthly storage tables fall a day behind on the data machine after every sync. Add the two rollup commands to `warehouse/run_data_machine.sh` after its sync, or have `scripts/sync.py` compare the hash both records already keep (`data_sha256`)?
- The same blind spot is wider: 32 tables' archived file is not, byte for byte, the uploaded one, and the sync reads all as current. Is a hash comparison in the sync wanted?
- `task/198-battery-data` did not land, so the quantities step is not in the daily run. Land it with 195 to 197 once `main` passes?
- The runner's run of 11 October ended with `supabase_load` and `redivis_upload` at exit 1. Have a session read that run's log?
- `ercot_all_hub_prices_history` ends on 26 August 2026 and no run has rewritten it since 26 September; the data machine's page files read it. Is it meant to be refreshed, and by which run?
- `ercot_rtm_node_prices` holds one week and stopped on 5 October; ERCOT lists seven days. Approve the node price pull now (entry B7 of the rulings document), or let the weeks go?
- Which of the 40 stuck tables should be on a schedule? The list is in the data document, "Stuck, or not on a schedule".
- The suite writes `warehouse/output/raw/madeup_as_prices/` into the checkout it runs in. Have a session move that to a temporary folder?
- `archive/sessions/LAST_ANSWERED` stands at 171. After the review, which number?
- The cadence limits of the data document (3, 14, 62, 184 and 730 days): keep them, or name yours?

## The prompt

"Session 200: what the roadmap needs to know, on lab-desktop", pasted on 11 October 2026 at about 18:43 Pacific: seven rules (precheck first; unattended; landing with freeze status and snapshots, no cutoff; data writes under the lock, no pull, model spend USD 0, nothing deleted, no em dashes; no page, test, schedule, scanner or release gate; this report; the chain queue as the last step) and four pieces of work (the state of every table; every open ruling in one place; the storage offers rollup; the lab-desktop section of `docs/machines.md`).
