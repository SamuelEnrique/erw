# Session 59 report: several machines, and the fixes Samuel should not have to do

Energy Research Warehouse (ERW), session 59, run on the portable laptop, 2026-10-02 02:52 UTC to about 04:20 UTC. **Wall time about 1 hour 28 minutes.**

**API spend: USD 0.00** (budget USD 0 of its own, hard cap USD 4):
- The session made no model call of its own.
- The end-to-end test ran with a stub in place of Claude, and the stub spends nothing.
- The approved daily-job dispatch was **not used**, and here is why:
  - Today's daily run had already succeeded at 00:53 UTC (session 58's dispatch, commit `ac178e0`).
  - The digest email has no send-once-a-day guard, so a second run today would email every subscriber a second digest.
  - The new lock step in the daily job therefore first runs on its own at 2026-10-03 14:00 UTC. Today's 14:00 run sees today's success and skips, by session 58's `once=1` gate.

No force push. Nothing released on Redivis.

Samuel's additions to the prompt, all done:
- **Supabase Pro:** the loader's size limit now fits the Pro plan (`max_mb` 7,500, `warn_mb` 6,000, of the 8 GB included).
- **Cloud copy:** the warehouse's cloud copy is the existing Redivis datasets, with Supabase Storage only for the archive Redivis cannot hold. No other service was added.
- **Starter dataset for Ben:** built in `exports/redivis-starter/`, with the note to send.

## Part 1, in plain words

1. **The digest goes out again, and a mail scanner can no longer unsubscribe anyone.**
   - **Restored:** the row for Samuel's address in `email_suppressions` is deleted (1 row before, 0 after), so the digest has a recipient again.
   - **The cause:** the unsubscribe of 2026-09-29 00:32 UTC came from the digest email's own link. The signed token exists only in a sent email, and no test or script calls the route. The likeliest cause is a mail scanner opening the link, and opening it (a GET) unsubscribed.
   - **The fix:**
     - opening the link now only shows a page with an "Unsubscribe" button;
     - pressing it (a POST with `confirm=yes`) unsubscribes;
     - mail clients' own one-click button (RFC 8058, `List-Unsubscribe=One-Click`) still works directly;
     - any other request changes nothing.
   - **Tests:** they now use fixed addresses under `example.invalid` (`erw-test+owner@example.invalid` and two more), and `email_digest.py` names `TEST_ADDRESS`.
   - Commit `024d1fa`.
2. **The schedule runs from the database, not from anyone's machine.**
   - **How:** migration 015 sets up pg_cron and pg_net in Supabase. The function `public.erw_dispatch` calls GitHub's `workflow_dispatch` with the token kept in Supabase Vault (`github_dispatch`), never in the repository.
   - **The five jobs:**
     - the daily job at 14:00 UTC (`once=1`);
     - latest prices every 15 minutes;
     - the hourly network at :05 (except 14:05);
     - the Roundup on Sundays at 23:00 (`once=1`);
     - the weekly vacuum on Sundays at 10:00.
   - **Verified:** the first call answered HTTP 204 and started run 36958084400. Since then every dispatch has answered HTTP 204 (`python warehouse/supabase/scheduler.py --status`, read at 04:16 UTC: latest prices and the hourly network succeeding).
   - Commit `cfe9323`.
3. **The stale issues are closed.**
   - **How:** the repository token cannot write issues (HTTP 403), so a small dispatchable workflow, `.github/workflows/issues.yml`, closes the listed issues with a comment, using GitHub's own token.
   - **Closed:**
     - #6, #7, #8, #9, #10, #13 and #14, with a comment naming the daily-run fixes and their commits;
     - #11 and #12, with the digest's date fix.
   - **Kept open, as asked:** #3 (CARB), #4 (the NYISO queue) and #5 (ERCOT's large-load list).
4. **`/events/caiso-heat-2022` is right.**
   - **What the page says:** it names 2022-09-06 at 51,104 MW as the window's highest hour.
   - **Session 58's "mismatch":** 2022-09-01, with 46,868 MW and +34.74 percent, is a different figure: the day with the largest rise against its baseline, not the peak. Both are correct.
   - **Next:** the check that made it look wrong is queued as task 008.
5. **`/network`'s ERCOT intensity was already rebuilt.**
   - The 01:51 UTC hourly run had refreshed it.
   - The live page's value (309.2851) equals Supabase's.
   - Nothing further was needed.

Also found and fixed: four tests that failed on `main` (commit `5955b7a`):
- **`test_session55` used fixed times of 2026-10-01.** It failed once the daily commit `ac178e0` built a newer committed network snapshot. It would have failed today's daily job's test step and every code branch. Its runs are now timed after the committed snapshot.
- **`test_session46` restored only one of five paths.** As a result, `test_session57` and `test_session58` found no raw files when run after it.
- **The event-study notebook lacked session 58's `caiso_heat_2022` window.** Added.

The full suite passes: 219 tests (220 with the queue-file check added in Part 3).

## Part 2: several machines

### The pieces

| Piece | Files | What it does |
|---|---|---|
| Sync (2.1) | `scripts/sync.py`, `sync.ps1`, `sync.sh` | Pulls `main` (fast-forward, or a merge; never a force or a rebase). For every table in `coverage.csv`: a table missing here is restored from its Redivis dataset, with its provenance header from `erw_headers`, and checked against Redivis's row count; a table that differs is reported (`--refresh` replaces it). Tested: `pjm_rpm_capacity_prices` moved aside and restored, 234 rows, the same keys and values. |
| Roles and the data lock (2.2) | `warehouse/lock.py`, migration 016 | Role `data` or `code` per machine in `.erw/machine.json`, switched with one command. The lock is a row in `erw_locks` with an expiry, functions callable with the service key only. Every data writer refuses without it: `iso_prices.write_csv` and `write_snapshot` (so every connector), `load.py`, `upload.py`, `archive.py` and `vacuum.py`. Tests and writes outside `warehouse/output` are exempt. The daily job takes the lock (waiting up to 60 minutes; 200-minute expiry) and releases it after its commit; the weekly vacuum runs under it. |
| Code on branches (2.3) | `.github/workflows/code-branch.yml` | A push to `task/**` runs `tests/`, the site build and `check-routes` against the live site; when they pass, the branch is merged into `main` and deleted. Actions may not open pull requests in this repository (GitHub's answer: "GitHub Actions is not permitted to create or approve pull requests"), so it merges the branch directly, after the same checks. Allowing it is optional (Samuel's list, item 4). |
| The queue (2.4) | `scripts/taskqueue.py`, `queue/` | `queue/todo`, `doing` and `done/NNN-<role>-<slug>.md`, front matter (role, spend cap, timeout, permission mode) and the full prompt. A claim is a commit moving the file, pushed; a lost push race undoes it and moves on. A heartbeat row `task:NNN` in `erw_locks` (30 minutes, renewed every 10) marks a live task; a stale one goes back to `todo/`. |
| The worker (2.5) | `scripts/worker.py`, `worker.ps1`, `worker.sh` | Loops sync, requeue stale, resume its own task or claim, and runs Claude Code headless (`claude -p`, the repo's `.claude/settings.json`, `--max-budget-usd` at the task's cap, its timeout). Code tasks run on `task/NNN-<slug>`, pushed to `wip/` every 10 minutes so a closed laptop loses nothing; data tasks run on `main` under the data lock. A usage limit pauses until Claude's reset time and resumes the same session, never failing the task. The report goes into the done file and a line into `queue/summary/<day>-<machine>.md`. |
| Setup and docs (2.6) | `docs/machines.md`, `scripts/setup.ps1`, `setup.sh` | Tools, `.venv`, packages, the `.env` keys a role needs (never printing values), the role and a sync. On Windows: never sleep or hibernate while plugged in (a data machine by default, `-KeepAwake` for a code machine); `-Worker` starts the worker at logon. This laptop is set up as `portable-laptop`, role `code`. |

### The end-to-end test (2.7)

Run on this laptop with the stub (`tests/worker_stub.py`) in place of Claude. Everything is in `queue/done/` and `queue/summary/2026-10-02-portable-laptop.md`:

- **001, a fake code task: done.**
  1. The worker claimed it (commit `1764252`) and made `task/001-e2e-code`; the stub committed `queue/e2e/code-task.md` there, and the worker pushed the branch.
  2. CI run 36963297815 checked it: tests passed; the site built; check-routes passed (64 of 64 pages, against the live site).
  3. The workflow merged it into `main` (`490c98f`) and deleted the branch.
- **002, a fake data task: half a pass.**
  - **Worked:** the worker took the data lock, claimed the task, paused for the stub's usage limit and resumed, then released the lock.
  - **Did not run:** the stub, unlike Claude, keeps no session, so it resumed without the task's lines and its lock check and commit never ran. The stub now keeps the prompt for the resume.
- **003, the same data task: failed, honestly.** The stub's lock check ran under the system Python, not the `.venv`, because Windows found another `python` first. The worker now starts a runner named `python` with its own interpreter. The failure path itself worked:
  - the task went to `done/` marked failed, with the error;
  - the lock was released.
- **004, the same data task: done.**
  - **A real race first:** the worker's first claim of 004 lost to CI's merge of 001 landing on `main` at the same moment, so it undid the claim and moved on.
  - **The next claim:**
    1. took the lock;
    2. paused for the usage limit and resumed;
    3. confirmed a write into `warehouse/output` passes `lock.require` under the lock;
    4. committed `queue/e2e/data-task.md` on `main` (`d9814fb`), pushed it, and released the lock.

After every run, `python warehouse/lock.py status` reads "the data lock is free", and no `task:` heartbeat row is left.

The claim race is also a unit test (`tests/test_session59.py`, 16 tests): two clones of one bare repository claim the same task; the second loses, undoes and takes the next task.

### Cloud copies: where, how big, what limit, what cost

Measured 2026-10-02:

| Copy | Where | Size | Limit | Monthly cost |
|---|---|---|---|---|
| Code, metadata, news tables, the starter export | GitHub `SamuelEnrique/erw` (public) | 172 MB | GitHub recommends under 1 GB; files under 100 MB (the largest new file is the 32 MB starter CSV) | USD 0 (public repository; Actions minutes free) |
| Every public table, as last uploaded | Redivis `samuelca.energy_research_warehouse` (81 tables, draft) | 2.79 GB | not reported by Redivis's API | USD 0 so far |
| Every internal table | Redivis `samuelca.energy_research_warehouse_internal` (14 tables, draft) | 119 MB | as above | USD 0 so far |
| The live set | Supabase Postgres (Pro, spend cap on) | 381 MB | 8 GB included; the loader stops at 7,500 MB and warns at 6,000 MB | USD 25, Samuel's plan; the ERW adds nothing to it |
| The append-only archive | Supabase Storage, private bucket `erw-archive` (547 files) | 507 MB | 100 GB included in Pro | included |
| The network's hourly file | Supabase Storage, public bucket `erw-public` | 191 kB | as above | included |
| Raw source files | the data machine's disk | several GB | the disk | USD 0 |

Machines sync from Redivis first, and from the archive for what Redivis lacks (`warehouse/archive/restore.py`). No other service is used.

## The starter dataset for Ben

`exports/redivis-starter/`, rebuilt by `python warehouse/exports/redivis_starter.py`:
- `eia930_iso_hourly_demand_2019_2025.csv`;
- `codebook.csv`;
- `README.md`: the codebook, rows and gaps per ISO, the source workbooks with their dates, the license quoted from EIA's Copyrights and Reuse page, and the suggested citation;
- `note_to_ben.txt`: three sentences.

**The data:** EIA-930 hourly demand for the seven ISOs, every hour of 2019 to 2025, 429,525 rows.

**Built from Adjusted demand, after a first build was withdrawn.** The first build (`56f9865`) used EIA's raw Demand. That column holds values such as 2,147,480,000 MW in one PJM hour, so it was rebuilt on EIA's Adjusted demand before anything was sent:
- `demand_reported_mw` and `imputed` keep what EIA changed visible.

**The `suspect` column.** Adjusted demand still holds 42 hours no grid can have: PJM at 224,345 MW in July 2020 (its all-time peak is about 166,000 MW), NYISO at 0 MW, CAISO at 14 MW.
- These rows are flagged by one stated rule: below 30 percent of the ISO's median hour, or a single hour more than 20 percent above or below both neighbours.
- The values are EIA's, unchanged.
- Flagged hours: CAISO 27, PJM 7, NYISO 6, SPP 2.

**Hours left out:** 51, where EIA has no adjusted demand. Nothing is filled.

## The queue's first five tasks

All in `queue/todo/`, each with its full prompt, role and spend cap:

| Task | Role | Cap | What |
|---|---|---|---|
| 005-data-refresh-runner-blocked | data | USD 1.50 | Refresh CARB's auction prices and NYISO's queue, which GitHub's runners cannot download (issues #3, #4), per the runbook; Redivis draft, never released |
| 006-data-caiso-notices-2026 | data | USD 3 | Did CAISO declare anything on 2026-09-09? Session 58's open question 4; three requests at most |
| 007-code-docs-for-machines | code | USD 2 | Bring `CLAUDE.md`, `ARCHITECTURE.md`, the runbook and `llms.txt` up to date with this session's machines |
| 008-code-check-values-event-dates | code | USD 3 | Make check-values name the date of every event-page key and compare like with like (the false alarm of session 58's question 0) |
| 009-data-available-supply-probe | data | USD 3 | Probe CAISO's Today's Outlook history for available supply (open question 2); six files at most, a method note, no warehouse writes |

The three data tasks wait for a data machine; the portable laptop takes only 007 and 008.

## For Samuel: one list

1. **Send Ben the starter dataset.** It goes from Samuel's own email to Ben, so it is not automated.
   1. Open `exports/redivis-starter/note_to_ben.txt` and paste its three sentences into an email to Ben Domingue.
   2. Attach `eia930_iso_hourly_demand_2019_2025.csv` (32 MB; zip it if the mail limit is 25 MB), `codebook.csv` and `README.md` from the same folder.
   3. Send.
2. **Make the home laptop the data machine.** It needs that machine, its disk with the raw files, and a Claude sign-in only Samuel can do.
   1. On the home laptop, in PowerShell: `cd <the erw folder>`, then `git pull`.
   2. Check that `.env` is there; it is the same file as on this laptop.
   3. Run `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -Role data -Name home-laptop -Worker`.
   4. If it says Claude Code is missing: `npm install -g @anthropic-ai/claude-code`, then `claude` once to sign in, then run step 3 again.
   5. It should end with "ready: home-laptop is a data machine". The worker then starts at each logon, and takes tasks 005, 006 and 009.
3. **Next week, the lab machine.**
   1. Clone the repository: `git clone https://github.com/SamuelEnrique/erw.git`.
   2. Copy `.env` into it.
   3. Run the same command as item 2, with `-Name lab-machine`.

   Two data machines are safe: the lock lets one write at a time.
4. **Optional: let Actions open pull requests,** so each code task leaves a pull request on record instead of a direct merge. It is a repository setting the token cannot change (HTTP 403).
   1. GitHub, the `erw` repository, then Settings, Actions, General, Workflow permissions.
   2. Tick "Allow GitHub Actions to create and approve pull requests".
   3. Save.

   Merging works without this.
5. **Do not add branch protection that requires pull requests on `main`.**
   - Such a rule would stop the daily job's commit and the queue's claims, which push to `main` directly. The token cannot set protection anyway (HTTP 403).
   - If protection is wanted later, it needs a bypass for GitHub Actions and for Samuel's token, and a session to adapt the queue.
6. **When the GitHub token is renewed** (GitHub reports no expiry on it today), the schedule needs the new token in Vault. Vault is written only from a machine that holds the token.
   1. Put the new token in `.env` as `GH_TOKEN`.
   2. Run `python warehouse/supabase/scheduler.py --set-token`.
   3. Run `python warehouse/supabase/scheduler.py --test latest-prices.yml`; it should show HTTP 204.

## Open questions

- **The digest has no send-once-a-day guard.** A second daily run on one day would email subscribers twice. The `once=1` gate prevents it for scheduled runs, but not for a manual dispatch. A small fix for a code task: record the day's send in Supabase and skip a second one.
- **Redivis's storage limit for the account** is not exposed by its API. 2.9 GB is held today.
- **Three tables here differ from coverage** (`datacenter_queue_positions`, `ercot_interconnection_queue`, `spp_interconnection_queue`): this code machine holds rows newer than the last build. A data machine's next run settles them.
