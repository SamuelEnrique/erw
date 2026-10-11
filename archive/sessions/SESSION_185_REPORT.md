# Session 185 report: the data-machine handover, finished on lab-desktop

11 October 2026, 06:56 to about 08:20 UTC, unattended, on `lab-desktop` (host `SU-4QC3QR3`). Branch `wip/185-data-machine` in `C:\Users\Shared\Documents\erw-185` (it holds `wip/184-lab-desktop`), on this machine only. Model spend USD 0, no model call. No request to any publisher. Outputs: `runs/session185/` of the data checkout.

## Read these first

- **NOT LANDED. This machine still cannot push to GitHub**: no sign-in is stored for `Shared` (session 184, item 0, is still open). `wip/184-lab-desktop`, this session's branch and one data commit on `main` here wait for a person's push. I did not use the `GH_TOKEN` of `.env`: it is the scheduler's, and session 184 ruled it out for pushes. Commands under "To finish".
- **The raw files are here and every hash is verified.** `wip/187-raw-handover` arrived at 07:44 UTC, 45 minutes into the wait. 857 parts read, 33,630 files written (25.99 GB), 0 bad parts, 0 conflicts. `verify`: 33,630 the same as the manifest, 0 missing, 0 different.
- **ERCOT's count carried over: 2,473,320 of 3,000,000 rows**, counted by the connector from the restored folder with no request; it is the number of rows the table holds.
- **The daily run is registered** (`ERW data machine daily`, 10:00 Pacific). Its first run is today at 17:00 UTC. **I did not see a run**: none was started by hand, because a run asks ERCOT's lists and this session had no pull. A temporary task proved the scheduler's context with `--check`, and was removed.
- **The five tables are the archive's, and one differs from the synced file in more than its header.** `energy_projects`: 30,921 of 39,784 rows carry an older `retrieved_at` (26 September in place of 5 October). That is how the archive keeps the column; no other value differs. Session 184's "row for row" left that column out.
- **Migration 029 was already applied** (10 October, 18:01 UTC, session 181's landing). I did not apply it again. The review list on production shows the 8 drafts.
- **The findings worker had stopped** (an interrupt after 06:54 UTC, minutes before this session's first command; why is not known). Started again at 07:10 UTC.

## What was done, by the prompt's five parts

1. **The raw folders.**
   - Waited from 06:59 UTC, a check every five minutes; the branch was there at the tenth check (07:44:12 UTC).
   - Read `scripts/raw_handover.py` before running it, and ran the branch's own file (same git blob) from `runs/raw_handover_187.py`, with `--handover` and `--state` under `runs/session185/handover/`. Nothing was added at a path the branch tracks.
   - First `ercot_zone_prices` alone: 6 parts, 58 files, verify exit 0. Then everything: 851 more parts in 19 minutes.
   - Verify of the whole: 33,630 files hashed in 5.5 minutes, exit 0.
   - The folder this machine pulled in session 184 (`eia930_emissions/20261010T212712Z/`) is kept beside the laptop's.
2. **The five tables and `iso_zone_prices_history`**, under the data lock (held 06:59:49 to 07:04 UTC by `lab-desktop/83f0a5b4`).
   - The six synced files were copied first to `runs/session185/synced_before/`, with hashes.
   - Five tables rebuilt from the bucket as of 9 October 00:00 UTC, each exit 0, each the file session 184 had rebuilt. Validator exit 0. `load.py --dry-run` exit 0 (it was exit 1).
   - Against the synced files, cell by cell (`compare_values.out`): the SPP queue, 9 `poi` values (the archive keeps a character the export had turned into a space); `energy_projects`, 30,921 `retrieved_at` values, and 27,203 cells that differ only as text (`20` against `20.0`, a trailing zero).
   - `iso_zone_prices_history`: the archive's newest state, 1,664,445 rows to 10 October 06:00 UTC. Validator exit 0. Coverage row rebuilt (exit 0). Archive write: 0 rows new or changed. Redivis draft: `count(*)` 1,664,445; nothing released. `sync.py --check`: 198 of 198 current.
   - One commit on `main` here, as a data task makes it: `ac0bc90c` (coverage, the archive manifest, the Redivis manifest).
3. **The daily run.**
   - `scripts/register_data_machine_daily.ps1` and `scripts/unregister_data_machine_daily.ps1` (new). No elevation is needed: the task runs while `Shared` is logged on. A task that runs with nobody logged on needs an administrator, and would find no saved sign-in to push with.
   - The script refuses a machine without `warehouse\raw\ercot_zone_prices\manifest.csv` (the count would start at zero) and a machine that is not the data machine.
   - The task sets `GCM_INTERACTIVE=never` and `GIT_TERMINAL_PROMPT=0`: with no sign-in the run's push fails at once and is recorded, and never waits for a window while it holds the data lock.
   - Registered at 08:10 UTC: state Ready, next run 2026-10-11 17:00 UTC, one instance, stopped after six hours, a missed run is not started late.
   - Proof of the context: a temporary task with the same command and `--check` ran under the Task Scheduler at 08:05:31 UTC, exit 0, took and released the lock, found Git's bash. It was unregistered.
4. **Migration 029 and the review list.**
   - `public.scanner_drafts` holds 8 rows, all `draft`, raised 2026-10-10T18:01:40Z. The list function answers "not authorized" to the anon key alone and 8 drafts with the internal token.
   - Production, read only: `/internal/findings` is 404 without the cookie; with it, 200, `data-drafts="8"`, the 8 ids on the page, strongest first, the token nowhere in the page (`prove_review_list.out`, 07:10:14 UTC).
5. **Landing.** Not done: see the first bullet and "To finish".

## What to review

- `C:\Users\Shared\Documents\erw\runs\session185\handover\verify_all.out`: one line, the verification of every raw file.
- `runs\session185\compare_values.out`: what the restored tables changed against the synced files.
- `runs\session185\register.out` and, after 17:00 UTC today, `runs\data_machine_daily.out`: the first scheduled run. Expect in it "counted against the ceiling" at or just above 2,473,320 (ERCOT posts the year's workbooks again on Sundays), the five page files, the scanner's line, a commit, and "push exit" not 0.
- `https://erw-flame.vercel.app/internal/findings` (internal view): "Scanner drafts (internal)", 8 drafts.
- `docs/machines.md` on the branch: the section "The lab desktop, the handover finished (session 185)".

## Checks run

| Check | Exit | Result |
|---|---|---|
| `freeze.py status` | 0 | no freeze |
| `restore.py` of five tables, `--as-of 2026-10-09T00:00:00Z` | 0 each | the rows of session 184's rebuilds, hash for hash |
| Validator, five tables; then `iso_zone_prices_history` | 0, 0 | pass |
| `load.py --dry-run`, after the five; after the coverage row | 0, 0 | 1,832,363 and 1,832,362 rows selected (one row apart, minutes apart; not traced) |
| `build_coverage.py --only '^iso_zone_prices_history$'` | 0 | 1 row rebuilt, 197 carried over |
| `archive.py write`, `upload.py --tables iso_zone_prices_history` | 0, 0 | 0 rows archived; draft `count(*)` 1,664,445 |
| `sync.py --check` | 0 | 198 current |
| `raw_handover.py fetch`, then `verify` | 0, 0 | above |
| `ercot_zone_prices.py --pull --offline`; `ercot_ceiling_count.py` | 0, 1 then 0 | no request; 2,473,320. The first exit 1 was my script expecting the laptop's logged 2,524,608 |
| `drafts_state.py`; `prove_review_list.mjs` | 1 then 0; 0 | first try built a wrong address; then 8 drafts both ways |
| `tests.test_session185` | 0 | 14 tests |
| The task's command with `--check`, from a shell and from the Task Scheduler | 0, 0 | `task_command_check.out`, `task_context_check.out` |

- **Not run:** the whole test suite and the site build (the branch changes two scripts, one test file and two documents); the daily run itself.
- **Not verified:**
  - The counts against the other two ceilings (`zone_price_history`, `ercot_wind_solar_history`). Their files are the laptop's, hash for hash; their connectors were not asked to count.
  - That the daily run completes here. Only its `--check`, its inputs (session 184) and the scheduler's context were proven.
  - The laptop's log says 2,524,608 where this machine counts 2,473,320. A workbook just saved is counted as a full year until it is read; the two 2026 workbooks then held 51,288 fewer rows than a year, which is the whole difference.

## What this session changed outside the repository

- This machine: `warehouse/raw` (33,630 files); six table files in `warehouse/output`; two scheduled-task changes (the daily task registered; the worker started again); one temporary task, removed.
- Supabase: the data lock taken and released three times; nothing loaded into the live set.
- Redivis draft: `iso_zone_prices_history` replaced (1,664,445 rows) and its 18 header lines. Nothing released.
- Archive bucket: one run of 0 rows (`20261011T070321Z-local`). 22 GB read from `_handover/187/`.
- Production: read only.

## Decisions made without you (the reversible option each time)

- **No push with the scheduler's token.** A person signs in once; nothing is lost by waiting.
- **Migration 029 not applied a second time.** It is there and its list works; a second run would only replace three functions with themselves.
- **No hand-started daily run.** The schedule makes the first one today.
- **The task runs only while `Shared` is logged on.** The worker is the same. A restart with nobody logging on stops both.
- **The archive's `energy_projects` was taken as asked**, with its older `retrieved_at`. Reversible: the synced file is in `runs/session185/synced_before/`. The next run of `energy_projects.py` rewrites the table either way.
- **Redivis's header lines for the five tables were not corrected.** That needs an upload of the five tables from here, which was not asked.
- **The worker was started again.** It was registered by session 184 at your word.
- **`CHAIN_OCT8_PROMPT.md` is not on this machine** (it was never committed). I applied `CLAUDE.md` and the chain's rules as reports 166 to 186 state them.

## To finish

0. Sign in to GitHub on this machine (a terminal, any push, the sign-in window). Then, in this order (`wip/192-roundup-repeat` first: it is needed before 23:00 UTC today, see its report):

```bash
cd /c/Users/Shared/Documents/erw && git fetch origin
.venv/Scripts/python.exe scripts/freeze.py status; echo "exit=$?"
git -C ../erw-185 merge origin/main            # main has moved since (the daily run, session 187's landing)
node site/scripts/snapshot-live.mjs take before185
git -C ../erw-185 push origin wip/185-data-machine
git -C ../erw-185 push origin wip/185-data-machine:task/185-data-machine
# after the workflow's merge and the deploy:
node site/scripts/snapshot-live.mjs take after185
node site/scripts/snapshot-live.mjs compare before185 after185
git pull origin main                            # main here then holds its own data commit, merged
```

- The branch holds session 184's two commits, so it lands `wip/184-lab-desktop` too. No site file changes: the comparison should list 0 differences.
1. On the home laptop: `powershell -ExecutionPolicy Bypass -File scripts\unregister_findings_worker.ps1`, `schtasks /Delete /TN "ERW data machine daily"` if it was registered, `python warehouse/lock.py role` (session 184's item 2, still open; two workers would read one queue).
2. Here, from an elevated PowerShell, once: `powershell -ExecutionPolicy Bypass -File C:\Users\Shared\Documents\erw\scripts\register_findings_worker.ps1 -Root "C:\Users\Shared\Documents\erw"` (the worker's startup trigger; session 184's item 3).
3. After today's run at 17:00 UTC: read `runs\data_machine_daily.out`. The laptop's copy of `warehouse/raw` may go once it shows the count carried over.
4. The 22 GB under `_handover/187/` in the bucket: verified here, so it may be deleted (session 187's question).

## Open questions

- Session 184 listed files that are on the home laptop only and are not raw files: `runs/` (snapshots, session outputs, chain prompts), `private/`, and the untracked outputs outside coverage. Session 187 handed over `warehouse/raw` only. Are any of those wanted here?
- Redivis's `erw_headers` still holds the older header lines for the five tables. Upload the five from here (their rows would become the archive's), or correct the lines alone?
- Why did the worker stop at 06:54 UTC? Its task restarts it on a failure; an interrupt was not one.
- Should the daily task and the worker run with nobody logged on (an administrator registers that once)? Then the daily run's push needs a sign-in that works without a window.

## The prompt

"Session 185 (long end 2:30): finish the data-machine handover. (1) Wait for wip/187-raw-handover from the home laptop (check every five minutes, up to two hours), then restore the raw folders from the archive by its handover.json, verifying every hash; if it has not arrived in two hours, do everything else and say so. (2) Run the five-table restore under the data lock from session 184's "To finish", and rule on iso_zone_prices_history by keeping the archive's two days. (3) Register the daily data run here (ERW data machine daily), from an elevated context if the script needs it, else report the exact command for Samuel. (4) Apply migration 029 for the scanner's drafts and prove the review list at /internal/findings shows the 8 drafts. (5) Land wip/184-lab-desktop and this session's work. Report in short bullets and stop." Unattended; the rules of CHAIN_OCT8_PROMPT.md; model spend USD 0, no model call; deploys allowed; Samuel grants this session permission to install persistent things on this machine: scheduled tasks and the database migration.

## Night of Oct 11

11 October 2026, 09:22 to about 10:40 UTC (02:22 to 03:40 Pacific), unattended, on `lab-desktop`. Model spend USD 0. Pulls: none; the handover fetch read 0 parts from the bucket. Outputs: `runs/session185/night/` and `runs/session19x/landing_*.out`, `snapshot_*.out`.

### Read these first

- **Everything is landed.** Samuel's push of `wip/192-roundup-repeat` at 09:22 UTC stored the GitHub sign-in on this machine; the "NOT LANDED" lines above and in the reports of sessions 191, 192 and 193 are history.
- **The Roundup fix is on `main` since 09:37 UTC**, more than 13 hours before tonight's run at 23:00 UTC. On main's code the dry run of 2026-W41 exits 0 and carries "The peak hour moved".
- **0 differences on the 25 pages after each of the four deploys.**
- **One thing not as asked: the order.** The instruction (191, 193, 185) arrived after `wip/185-data-machine` had already merged. The order was 192, 185, 191, 193.
- **The daily run's push will now work.** A push with no window allowed exits 0 here (dry run). Today's run at 17:00 UTC commits to `main` and pushes, which deploys, as the data machine was designed to do (sessions 149 and 184).

### What landed

| Branch | Merge on `main` | Checks (run) | Suite here after merging `origin/main` | Snapshot |
|---|---|---|---|---|
| `wip/192-roundup-repeat` | `e5af1750`, 09:37 UTC | passed (38128573466) | 3,221 tests, exit 0 | `before192` to `after192`: 0 differences |
| `wip/185-data-machine` (holds `wip/184-lab-desktop`) | `13d1ba61`, 09:51 UTC | passed (38129372324) | 3,229 tests, exit 0 | `after192` to `after185`: 0 differences |
| `wip/191-scanner-review` | `330933e0`, 10:01 UTC | passed (38129984021) | 3,227 tests, exit 0 | `after185` to `after191`: 0 differences |
| `wip/193-ba-map` | `ad0307b1`, 10:13 UTC | passed (38130660203) | 3,273 tests, exit 0; site build exit 0; map check 31 of 31 on the local build | `after191` to `after193`: 0 differences |

- Each landing: freeze check exit 0, `origin/main` merged into the branch, pushed to `wip/` and to `task/`, the workflow's checks, its merge, the Vercel deploy reported finished, then the after snapshot.
- After the last deploy, on production: `check-network-map.mjs https://erw-flame.vercel.app` exit 0, 31 checks pass; `/network/ba_boundaries.json` and `/network/ba_counties.csv` answer 200.
- `main`'s `warehouse/config/scanner.yaml` reads version 1.1.0.
- The data commit `ac0bc90c` was already inside `wip/185-data-machine`, so it landed with it.

### What did not land

- Nothing failed its checks. No branch was left on `wip/` alone.

### The data checkout, the fetch and the verify

- `git pull origin main` at 10:15 UTC: a fast-forward to `ad0307b1`. The checkout now holds `warehouse/run_data_machine.sh`, which the daily task runs; before the pull it did not.
- Fetch, main's `scripts/raw_handover.py` with `runs/session187/handover.json` (both the same bytes as this morning's copies, by sha256), keeping this morning's place: exit 0, "0 parts read (857 already done, 0 bad); files written 0".
- **Verify: exit 0. "33,630 files the same as the manifest, 0 missing, 0 different"** (10:15:21 to 10:24:54 UTC, `runs/session185/night/verify.out`).
- Daily run: registered again from main's script after the verify, exit 0. State Ready, next run 2026-10-11 17:00 UTC (`runs/session185/night/register.out`). It was already registered since 08:10 UTC, after this morning's verify, which was also exit 0.
- `_handover/187/` was not deleted, in the bucket or anywhere.
- The findings worker is running.

### Review steps

1. The four merges. Open `https://github.com/SamuelEnrique/erw/commits/main`. The four lines "Merge task/192-roundup-repeat", "Merge task/185-data-machine", "Merge task/191-scanner-review", "Merge task/193-ba-map" each say "checks passed". A run's page: `https://github.com/SamuelEnrique/erw/actions/runs/38130660203` (the map), green.
2. The internal view. Open `https://erw-flame.vercel.app/internal/open`. Paste the token (`INTERNAL_COSTS_TOKEN` in `C:\Users\Shared\Documents\erw\.env`). Press "Open the internal view". The home page opens.
3. The map. Open `https://erw-flame.vercel.app/network`. At the top, click "Map" (beside "Network"). Expect the lower 48 states filled by county, and under the map the line that begins "Derived map: each county is given to one balancing authority". Click Texas near Houston: the panel is ERCOT's (a test holds that Harris County is not MISO's). Look at western Colorado and Wyoming: 37 counties are blank (`WACM`, for your ruling). The table behind it: `https://erw-flame.vercel.app/network/ba_counties.csv`.
4. The scanner's drafts. Open `https://erw-flame.vercel.app/internal/findings`. Expect "Scanner drafts (internal)" and 8 drafts. On the DC industrial retail price (one customer, the artifact), press "Dismiss". The other seven are yours to rule on.
5. The chart. Open `https://erw-flame.vercel.app/analysis/card/peak_hour_moved`. The button reads "Chosen for the Roundup".
6. The Roundup, after 23:00 UTC today. Open `https://github.com/SamuelEnrique/erw/actions/workflows/roundup.yml`. Click the newest run; expect green. Then open `https://github.com/SamuelEnrique/erw/blob/main/docs/roundup/2026-W41.md` (or `https://erw-flame.vercel.app/roundup/2026-W41` in the internal view). Under "ERW's Chart of the Week" expect "THE PEAK HOUR MOVED (chosen for this Roundup)". If the run is red: click "Run workflow", leave `once` at 0, press the green button.
7. What waits for you. Open `https://erw-flame.vercel.app/internal/waits`.
8. The first daily run, after 17:00 UTC today. Open `C:\Users\Shared\Documents\erw\runs\data_machine_daily.out` in Notepad. Expect "counted against the ceiling" at or just above 2,473,320, the scanner's line, a commit, and "push exit" 0. Then `https://github.com/SamuelEnrique/erw/commits/main` shows the run's commit.

### Open questions (choices made without you)

- **185 before 191 and 193.** It had merged when the order arrived. The branches touch different files; nothing depended on the order.
- **The fetch downloaded nothing.** I kept this morning's state file, so every part counted as done. Reading the 22 GB again would have proven nothing the verify does not prove. Say so if you want a fetch from an empty folder.
- **Registered twice.** The task existed since this morning; tonight's registration replaced it with the same definition from main's script.
- **One snapshot served twice**: the after snapshot of one landing was the before snapshot of the next. No deploy came between them.
- **The daily run's push to `main` now deploys from this machine every day.** If you want it held, run `powershell -ExecutionPolicy Bypass -File C:\Users\Shared\Documents\erw\scripts\unregister_data_machine_daily.ps1` before 17:00 UTC.
- **The sign-in is in the Windows credential store of `Shared`.** The task still runs only while `Shared` is logged on.
- **Left in place:** the worktrees `C:\Users\Shared\Documents\erw-184`, `-185`, `-191`, `-192`, `-193` and the `wip/` and `task/` branches on GitHub. All are merged; they can go when you like.
- **Still open from above:** the home laptop's worker and daily task (items 1 of "To finish"), the worker's startup trigger (item 2), Redivis's older header lines, `WACM` against `SWPW`, and whether a derived map is what you want on the page (reversible: delete `site/public/network/ba_boundaries.json`).
