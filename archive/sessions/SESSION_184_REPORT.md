# Session 184 report: the lab desktop takes the data role

Run on 10 October 2026 (UTC), on `lab-desktop` (host `SU-4QC3QR3`), unattended. Waited for `scripts\setup.ps1` from
20:50 to 21:24:58 (checked every two minutes; nothing was written or run in the checkout before it was gone and
`.venv\Scripts\python.exe` and `.erw\machine.json` existed); worked from 21:25 to about 21:55. Model spend USD 0, no
model call. No deploy: nothing was pushed to `main` or to a `task/` branch. Docs and this report are on
`wip/184-lab-desktop`. Outputs under `runs/session184/` of the data checkout (`C:\Users\Shared\Documents\erw`).

## Read these first

- **Do not start `warehouse/run_data_machine.sh` for real on this machine yet.** `warehouse/raw/ercot_zone_prices/` is
  on the home laptop only, and it is the count against ERCOT's ceiling of 3,000,000 rows. With it empty the refresh
  asks ERCOT again for four workbooks, counts from zero and sends the whole table to the archive and the Redivis
  draft. Its `--check` is safe and was run.
- **The loader refuses to load on this machine as synced** (`load.py --dry-run` exit 1): five tables came from Redivis
  with header lines older than their rows. The archive holds the same rows with the right headers; I rebuilt and
  compared them, but replacing the five files in `warehouse/output` was refused by the session's permission layer, so
  they are as the sync left them. The commands are under "To finish", item 2.
- **The worker starts at log-on only.** The shell was not elevated, so no startup trigger. "Survives a restart" is
  shown by the task's trigger and settings, not by a restart: none was made.
- **`CHAIN_OCT8_PROMPT.md` is not on this machine** (it was never committed). I applied `CLAUDE.md` and the chain's
  rules as reports 166 to 183 state them: unattended, `wip/` branch, no force push, gates not piped, real data only.

## What works

- **Part 1, the warehouse.** All 198 tables of `coverage.csv` are here, 37,002,032 rows, 9.4 GB.
  - Against coverage: 198 of 198 hold coverage's row count and newest timestamp (`verify_tables.out`, exit 0; one
    line per table in `verify_tables.csv`). No table here is outside coverage.
  - Against Redivis: 198 current, 0 missing, behind, ahead, diverged or unread (`sync_check.out`, exit 0).
- **Part 2, raw files.** EIA's eight grid monitor workbooks and their extracts are in
  `warehouse/raw/eia930_emissions/20261010T212712Z/` (`eia930_workbooks.out`, exit 0). All ten scheduled steps find
  every input (`scheduled_checks.out`, each exit 0).
- **Part 3, the loop.**
  - Dry run: `run_data_machine.sh --check` under `lock.py run`, exit 0: "a data machine with the three price
    histories", branch `main` (`lock_dry_run.out`).
  - Data lock: free before; held by `lab-desktop/1aad416e` from 21:29:28 UTC with the token passed to the command;
    free after.
  - Direct connection: opened as `load.db_reader()` opens it, in 3.9 s (session pooler, port 5432, 10 minute
    statement timeout). `ercot_as_prices` counted (336,932 rows, 1.4 s) and read whole (13.9 s), the read that timed
    out through the API in session 166 (`db_direct.out`, exit 0). Reads only.
- **Part 4, the analysis worker.** Task `ERW findings worker` registered and running (pid 5988).
  - One request as `/analysis` sends it: `20261010T213043Z-8cdfa6`, `queue_divorce` from 2010, queued 21:30:43,
    started 21:30:52, done 21:30:53 UTC, by `SU-4QC3QR3` (`worker_request.out`, exit 0).
  - Restart on failure every minute, no time limit, one instance (`worker_task_query.out`).
- **Part 5.** `docs/machines.md`: the table of machines, and a new section "The lab desktop (session 184)".
- Tests on this machine's Python 3.14.7: `tests.test_session181_worker` and `tests.test_archive`, 38 tests, exit 0.

## What is missing

- **Raw files the archive does not hold.** The archive keeps table rows only (`archive.py status`: 1,098 run parts,
  1,618 MB in the bucket, 0 month files here). Not restored, so the home laptop's copy must be kept:
  - `warehouse/raw/ercot_zone_prices/` whole: the count against 3,000,000 rows. Not pulled again: the count would
    restart at zero.
  - `warehouse/raw/zone_price_history/` and `warehouse/raw/isone_zone_load/`: the count against 3,000,000 rows of the
    Saturday refresh. Same reason.
  - `warehouse/raw/ercot_wind_solar_history/`: the count against 2,000,000 rows. Same reason.
  - `warehouse/raw/ercot_60d_dam/`: not read by the data machine's run.
  - `warehouse/raw/policy_monitor_refresh/` and the saved Virginia filings: the commission is paused, never requested.
  - Every other `manifest.csv` under `warehouse/raw/`.
  - Untracked outputs outside coverage (`rrc_lease_production_statewide/`, `analysis_internal/`, `thesis_state/`,
    `shadow/`, `logs/`), `private/`, and `runs/` (snapshots, session outputs, chain prompts).
  - This list is from reading the code, not from the laptop: I could not see what it holds.
- **The loader's coverage check fails for five tables**: `caiso_`, `ercot_`, `isone_` and `spp_interconnection_queue`,
  and `energy_projects`. Rows of the run of 5 October, header lines of 26 and 29 September, from Redivis's
  `erw_headers` (`load_dry_run.out`).
  - Rebuilt from the archive as of 9 October 00:00 UTC into `runs/session184/archive_asof/`: all five carry the
    header of the run coverage describes. Four are row for row the synced files. The SPP queue differs in nine
    values of `poi`: the archive keeps a character that Redivis's export turned into a space (`archive_asof.out`).
  - Why the header lines are older: not found. My reading, unverified: a full upload from a machine holding older
    copies rewrote those lines (`upload.py`, the metadata step writes the header lines of every table on disk).
- **Two days of `iso_zone_prices_history` are in the archive only.** The home laptop archived 1,664,445 rows (to
  10 October 06:00 UTC) on 9 October and never uploaded them; Redivis, coverage and this machine hold 1,663,123 (to
  8 October). Rebuilt to `runs/session184/archive_latest/`, not put into `warehouse/output` (coverage would no longer
  describe it).
  - The archive's newest `energy_projects` and `ercot_interconnection_queue` are the laptop's older copies (the pull
    of 26 September), archived again on 9 October. They are not newer than Redivis.
- **No startup trigger for the worker, and no restart was made.**
- **`ERW data machine daily` is not registered**, on purpose (first bullet of this report).

## What Samuel must do by hand

1. **Copy the home laptop's raw folders here**, `ercot_zone_prices` first, into
   `C:\Users\Shared\Documents\erw\warehouse\raw\`. Keep the laptop's copy until `run_data_machine.sh` has run once
   here and its log shows the count against the ceiling carried over.
2. **On the home laptop:** `powershell -ExecutionPolicy Bypass -File scripts\unregister_findings_worker.ps1` (else
   two workers read one queue), `schtasks /Delete /TN "ERW data machine daily"` if it was registered, and
   `python warehouse/lock.py role` to confirm `code`.
3. **Here, from an elevated PowerShell,** to add the startup trigger:
   `powershell -ExecutionPolicy Bypass -File C:\Users\Shared\Documents\erw\scripts\register_findings_worker.ps1 -Root "C:\Users\Shared\Documents\erw"`.
   Then restart once and run `.venv\Scripts\python.exe warehouse\analysis\findings\worker.py --status`.
4. **Rule on the five tables and on `iso_zone_prices_history`** ("To finish", items 2 and 3).
5. **Register the daily task** after item 1 (`docs/machines.md`, "The data machine's daily run"; the path is
   `/c/Users/Shared/Documents/erw`).
6. **Land the branch** ("To finish", item 1).

## Requests to publishers

| Publisher | Requests | Bytes | Ceiling |
|---|---|---|---|
| EIA, `www.eia.gov/electricity/gridmonitor/knownissues/xls/` | 16 (8 HEAD, 8 GET) | 694,031,944 | the daily run's own step (`eia930_emissions.py --days 3`), which asks for the same eight files every day |

- Run with `--dry-run`: 2,856 rows counted in complete days, no table written.
- The MISO and PJM workbooks are EIA's files from eia.gov. No request to MISO, PJM, ERCOT or the Virginia SCC.

## Decisions made without asking (the reversible option each time)

- **"Dry run" read as `--check`,** which builds, asks and writes nothing. A full run with `COMMIT=0` was not made:
  its ERCOT step is the one this report warns about.
- **No load into the live set.** The direct connection was proven by reads; a load of a table a live page reads needs
  rule 8's snapshot, and the prompt says no deploy.
- **The three archive-only states were rebuilt beside the warehouse, not into it.**
- **Docs and report in a second working copy** (`C:\Users\Shared\Documents\erw-184`, branch `wip/184-lab-desktop`),
  so the data checkout never left `main`. Not merged: a merge to `main` deploys.
- **The worker was registered** because the prompt asks for it by name (session 181 held that an unattended session
  may not install persistence without being told to).

## What this session changed outside the repository

- Supabase: the data lock taken and released once; one row of `analysis_requests` (1 of the day's 24), done.
- This machine: the scheduled task; `warehouse/raw/eia930_emissions/20261010T212712Z/`; `runs/`; four untracked files
  the proof request wrote (`site/data/findings/queue_divorce__first_year-2010.json` and three downloads under
  `site/public/findings/`). `main` here was fast-forwarded by the sync from `1d224a7` to `a0c4f64`.
- Redivis, the archive bucket, the live set, GitHub `main`: nothing written.

## To finish

1. Land the docs (a push to `task/` deploys: rule 8). Docs only, so the comparison should list 0 differences.

   ```bash
   cd /c/Users/Shared/Documents/erw && git pull origin main
   .venv/Scripts/python.exe scripts/freeze.py status; echo "exit=$?"
   node site/scripts/snapshot-live.mjs take before184
   git push origin wip/184-lab-desktop:task/184-lab-desktop
   # after the workflow's merge and the deploy:
   node site/scripts/snapshot-live.mjs take after184
   node site/scripts/snapshot-live.mjs compare before184 after184
   ```

2. The five tables, under the data lock (the synced files are replaced: same rows, the right header; for the SPP
   queue nine `poi` values become the archive's):

   ```bash
   cd /c/Users/Shared/Documents/erw
   .venv/Scripts/python.exe warehouse/lock.py acquire --task "five tables from the archive" --minutes 30
   for t in caiso_interconnection_queue energy_projects ercot_interconnection_queue isone_interconnection_queue spp_interconnection_queue; do
     .venv/Scripts/python.exe warehouse/archive/restore.py $t --from-bucket --as-of 2026-10-09T00:00:00Z --out warehouse/output/$t.csv; echo "exit=$?"
   done
   .venv/Scripts/python.exe warehouse/supabase/load.py --dry-run > runs/load_dry_run.out 2>&1; echo "exit=$?"
   .venv/Scripts/python.exe warehouse/lock.py release
   ```

3. `iso_zone_prices_history`: either leave it (the Saturday refresh brings the days back once the raw folder of item 1
   of the list above is here), or take the archive's state with
   `restore.py iso_zone_prices_history --from-bucket --out warehouse/output/iso_zone_prices_history.csv` under the
   lock, then the validator, `build_coverage.py --only '^iso_zone_prices_history$'`, the archive and the Redivis draft.

## Open questions

- Why does Redivis's `erw_headers` hold older header lines than the rows for five tables? Any machine synced from the
  cloud will fail the loader's check on them until it is fixed at the source.
- Should `scripts\register_findings_worker.ps1` take its default root from its own location, not the home laptop's
  path? Not changed here.
- Should the worker write the machine's ERW name (`lab-desktop`) and not the host name in a request's `machine`?
