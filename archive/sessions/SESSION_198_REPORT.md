# Session 198 report: the battery tool's data side, on lab-desktop

lab-desktop (data role), Sunday 11 October 2026, 19:40 to about 20:45 UTC. Unattended. Branch `task/198-battery-data`; one data commit on `main`. Model spend USD 0, no model call. Nothing deleted.

## Read these first

- **The quantities step is in the data machine's daily run from tomorrow, and ran once today.** `ercot_as_quantities`: 3,840 rows before, 4,800 after (960 new: delivery days 5 to 12 October 2026, Central). Validator exit 0; archive 960 rows new; Redivis draft 4,800; `sync.py --check`: current.
- **Durations: ERCOT's documents state one hour where the model takes one hour, for two of the three assumed cases. No number on the page would move.** Stated: Non-Spin before 9 December 2022 (the Protocols as NPRR 1096 found them); Regulation and Responsive Reserve from 27 June 2024 to 4 December 2025 (NPRR 1186). Not stated in the three documents read: Regulation and Responsive Reserve from 2018 to 26 June 2024. That label stays.
- **The first precheck failed (exit 1) and the session stopped, as rule 1 says; it started on the owner's second message.** Cause: the bare `python` on this machine is the global interpreter, which holds no package; the repository's environment is `.venv`, which holds all of them. Nothing was installed. Every command of this session used `.venv/Scripts/python.exe`. Second precheck: exit 0, 6 of 6.
- **One failed row in `erw_health` is mine and is not a failure of the step**: `session198_ercot_as_quantities`, "ModuleNotFoundError: No module named 'pandas'", 20:01 to 20:02 UTC. My first start of the step named `python` and `warehouse/health.py` started the global one. No request was made and nothing was written. The second start, with the venv's interpreter named in full, is the run reported here.
- **One test fails on this machine and has nothing to do with this session**: `tests/test_session116.py::Records::test_the_tables_on_this_machine_add_up` (`limit_mwh` of August 2026: 5,362,152.4 in the monthly offers table, 4,873,801.6 summed from the daily one). The two storage offers tables here are a day apart (`ercot_storage_dam_offers_daily.csv` of 11 October 10:13, `ercot_storage_dam_offers_monthly.csv` of 10 October 14:06, both local time). This session wrote neither. GitHub skips the test (the tables are not on the runner).

## What to review

- The step: https://github.com/SamuelEnrique/erw/blob/main/warehouse/scheduled.py (`ercot_as_quantities` in `JOBS`) and https://github.com/SamuelEnrique/erw/blob/main/warehouse/run_data_machine.sh (block "2b").
- The connector: https://github.com/SamuelEnrique/erw/blob/main/warehouse/connectors/ercot_as_quantities.py
- The Method note, section 3.3 and the new 3.3.1: https://github.com/SamuelEnrique/erw/blob/main/docs/methods/battery_earns_algorithm.md (the page, in review: https://erw-flame.vercel.app/data/methods/battery_earns_algorithm).
- The tests: https://github.com/SamuelEnrique/erw/blob/main/tests/test_session198.py
- The data commit: https://github.com/SamuelEnrique/erw/commit/27a10ea0

## What was built

- `warehouse/scheduled.py`: `ercot_as_quantities`, daily. Its input is the table itself, rebuilt from the archive when absent, so the connector always merges into the table held. `--list` names it; `--check`: "every input is here", exit 0.
- `warehouse/run_data_machine.sh`, block 2b, after ERCOT's load zone prices and their stores, before the page files: `soft_step dm_ercot_as_quantities` (under `warehouse/health.py`, tried once more, recorded, never stops the run). When a delivery day was added: the validator, the table's coverage row, then the archive and the Redivis draft as soft steps. A validator or coverage failure is recorded and gates this table's stores only.
- `warehouse/connectors/ercot_as_quantities.py`, four changes for daily use: ERCOT's pause is asked before any request; a run that would download more than 60 files stops before the first; the 400,000 row ceiling is held against the table after the merge, and the count is printed; a row's `retrieved_at` is the time its file was really downloaded (a file read again from `warehouse/raw` no longer restamps its rows).
- `docs/methods/battery_earns_algorithm.md`: the durations table, a new section 3.3.1 (four rows, each quotation with its document, section, page and address) and the assumptions table.
- `tests/test_session198.py` (19 tests). Two earlier tests extended, none removed: `tests/test_session114_part2.py` (the new step set aside by name, as session 116's was) and `tests/test_session149.py` (two validator gates in the script, each unpiped).
- The model (`warehouse/derived/battery_stack.py`) and every page: untouched.

## Pulls against their ceilings

| Pull | Address | Time (UTC) | Size | Ceiling |
|---|---|---|---|---|
| NP4-33-CD, the file list | `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=12316` | 20:02:35 | 28,267 bytes, 32 files listed | 1 request a run |
| NP4-33-CD, every file the site holds | `https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<id>`, 32 addresses (in `warehouse/raw/ercot_as_quantities/20261011T200229Z/manifest.csv`) | 20:02:39 to 20:04:22 | 32 files, 88,261 bytes; 3,840 rows read, 960 new | 60 files: 32 used |
| Rows held, against ERCOT's ceiling for this table | | | 4,800 rows, each (service, hour) once | 400,000 (session 74): 1.2 percent |
| Document 1: NPRR 1096, PUCT Report | `https://www.ercot.com/files/docs/2022/05/17/1096NPRR-28%20PUCT%20Report%20051222.docx` | 20:09:43 | 60,007 bytes, 20 pages | 3 documents: 1 |
| Document 2: NPRR 1282, PUCT Report | `https://www.ercot.com/files/docs/2025/08/04/1282NPRR-20-PUCT-Report-073125.docx` | 20:09:46 | 97,761 bytes, 40 pages | 2 |
| Document 3: NPRR 1186, PUCT Report | `https://www.ercot.com/files/docs/2024/04/12/1186NPRR-36%20PUCT%20Report%20041124.docx` | 20:11:16 | 402,663 bytes, 93 pages | 3 of 3 |
| ERCOT's three pages that list a revision's documents (to find the addresses above; not documents) | `https://www.ercot.com/mktrules/issues/NPRR1096`, `.../NPRR1282`, `.../NPRR1186` | 20:09:24, 20:09:28, 20:11:05 | 83,567, 76,146 and 93,989 bytes | see "Decisions" |

- No request to a paused publisher (`paused_sources.csv`: MISO, the Virginia commission). No NYISO, SPP, PJM or MISO request.
- The three documents are in the session's scratch directory, outside the repository, and are not in git.

## Checks, with exit codes

- `python scripts/precheck.py --what "session 198"`: first exit 1 (`daily_cap`, "No module named 'requests'"), then exit 0 from the venv.
- `python warehouse/scheduled.py --list`: names `ercot_as_quantities`, exit 0. `python warehouse/scheduled.py ercot_as_quantities --check`: "every input is here", exit 0.
- The step under the lock and `warehouse/health.py`: exit 0 (`runs/s198_step.out`).
- `erw_validate.py warehouse/output/ercot_as_quantities.csv`: exit 0 (`runs/s198_validate.out`); never piped.
- `build_coverage.py --only '^ercot_as_quantities$'`: exit 0. `archive.py write --tables '^ercot_as_quantities$'`: exit 0, run `20261011T200437Z-local`, 960 rows new or changed, 0 keys deleted. The 2,880 rows read again were unchanged.
- `redivis/upload.py --tables ercot_as_quantities`: exit 0, "CSV 4,800 rows, Redivis count(*) 4,800", nothing released.
- `scripts/sync.py --check --tables '^ercot_as_quantities$'`: before the upload "ahead: 1"; after it "current: 1", exit 0.
- `bash -n warehouse/run_data_machine.sh`: exit 0.
- The whole suite: see "The landing".
- The data lock: taken 20:01 to 20:05 UTC for the write and its stores, and again for the data commit and push (20:06); released each time; never held through a wait.

## Ruling 4: today's daily run, read

`runs\data_machine_daily.out`, the run of 17:00 UTC. Everything as expected; nothing re-run.

- ERCOT against the ceiling: 2,477,352 load zone rows, each once, of 3,000,000 (2,524,608 while the two new copies were counted as full years, before they were read). 4,032 new rows.
- The scanner: `dm_scanner ok`. Its own line (`runs/daily_dm_scanner.out`): "scan of 2026-10-11: 117 tables, 6813 series, 15 flags, 23 suppressed by known faults, 7 drafts, 0 added, 112.9 s".
- The commit: `483c412d`, "Page files 2026-10-11". `commit exit=0`, `pull exit=0`, `push exit=0`.
- Seen in passing, not looked into (it is the runner's run, not this file): the runner's commit of the day (`ceafacf8`) lists `supabase_load: connector exit 1` and `redivis_upload: connector exit 1` among its failures.

## The landing

- No freeze (`python scripts/freeze.py status`, exit 0). No force push. Both pushes before the Roundup cutoff (22:30 to 23:45 UTC).
- **The data commit**, as a data task makes it: `27a10ea0` on `main`, five metadata files (coverage, `docs/coverage.md`, the source registry, the archive manifest, the Redivis record), committed and pushed under the data lock.
  - `before198a` at 20:05:52 UTC, its own command, exit 0, 25 pages, 0 failed.
  - `git push origin main` at 20:06:31 UTC, exit 0. `main` had not moved. Vercel production: "Deployment has completed", 20:07:56 UTC.
  - `after198a` at 20:08:34 UTC, exit 0. `compare before198a after198a`: **0 differences on the 25 pages**, exit 0 (`runs/s198_compare_a.out`). Expected: no page changed, and every page is in review.
- **The branch** `task/198-battery-data`: see the lines added below by the second push.

- (The push, GitHub's run, the merge, the deployment and the comparison are added here by the second push, `task/198-report`.)

## Decisions made without you

- **Nothing was installed.** The owner's second message said to install the requirements. `requirements.txt` says of itself that it does not install on Python 3.14, and the repository's `.venv` already held every package (`pip install --dry-run --no-deps -r requirements-py314.txt`: nothing to do). Using the venv is the reversible choice and is how the daily run itself starts Python.
- **The step is in the data machine's run only**, not in the runner's `run_daily.sh`: the ruling names the one script, and the runner does not hold this table.
- **The step's stores in the daily run** (validator, coverage, archive, Redivis draft, when a day was added) are mine: the ruling names the step. Without them a day's rows would sit on this machine alone. `META_PATHS` already carries the five files into the run's commit.
- **The Redivis draft was written today** (draft only, nothing released), because "sync.py --check current" cannot hold while the table is ahead of the draft.
- **Four changes to the connector** (listed above). The retrieval time: before, every run stamped every row it read with the day's time, including rows of files it never downloaded again.
- **"ERCOT's ceiling" for this pull is read as this table's own 400,000 rows** (session 74's approval), not the load zones' 3,000,000, which counts load zone rows only.
- **The third document is NPRR 1186**, which the prompt does not name. NPRR 1282's "15 minutes" turned out to be boxed text that never took effect, so the rule in force before 5 December 2025 had to come from elsewhere; NPRR 1186 is where ERCOT wrote it.
- **Three listing pages were requested to find the documents' addresses.** I did not count them among the three documents. If they count, the ceiling was passed by three small pages.
- **Pages of a Word file** are counted from the page breaks Word saved in it; the note says so and gives the section and paragraph beside each page.
- **The note is also a page in review** (`/data/methods/battery_earns_algorithm`). Ruling 3 names the file, so it was amended; rule 9 is read as not covering it. It is not one of the 25 snapshot pages.
- **Two earlier tests were extended** so that they hold the new step instead of forbidding it.
- **The by-hand run's health step is named** `session198_ercot_as_quantities`, so the daily step's own name (`dm_ercot_as_quantities`) first appears with tomorrow's run.

## For Samuel's ruling

- **Fleet-limited as a strategy, the case for building it.** Whole Central months of quantities held today: **0 for each of the five services** (Regulation Up, Regulation Down, Responsive Reserve, ECRS, Non-Spin). September 2026: 28 of 30 days (1 and 2 September are not held and are no longer on ERCOT's site). October 2026: 12 of 31 so far, every day from the 1st.
- At the daily pace the first whole month is October 2026 (complete with the run of 30 October), and **twelve whole months, October 2026 to September 2027, are held on 29 September 2027**. A gap of more than about a month in the daily run loses a month. Session 178's 5.66 (the model against the awards) is the reason to want it; an ERCOT API key would give the history sooner. Build now on the months held, or wait for twelve?
- **Durations, what the early years would become if the model used the documents: the same numbers.** The documents state one hour where the model takes one hour. What would change is two labels on the page's list of durations (printed from `REQUIREMENTS`): Non-Spin before 9 December 2022 from "assumed" to the Protocols before NPRR 1096; Regulation and Responsive Reserve from 27 June 2024 to 4 December 2025 to NPRR 1186. Change the labels (a change to the model's constants and the page)?
- Regulation and Responsive Reserve from 2018 to 26 June 2024 stay assumed. One more approved read (the Protocols' Section 8 of a date before June 2024) would settle them or show that no duration was written. Approve it?
- Responsive Reserve from fast frequency response needs 15 minutes of energy, not an hour (NPRR 1186 and NPRR 1282, quoted in the note). The model backs all Responsive Reserve for an hour. The effect was not computed (it needs a model run): the price per MW is the same, the energy held is less, so revenue could only rise. Model it, or leave the conservative hour?
- From 27 June 2024 to 4 December 2025 ERCOT set aside one hour's energy for ECRS and Non-Spin in real time, while NPRR 1096's two and four hours stayed the limit on what may be offered. The model uses two and four. Leave?
- 1 November 2026 has 25 hours. The connector's rule accepts a 25-hour day and reads ERCOT's flag for the repeated hour; it has not met a real file of that day. Have a session read the run of 31 October?
- The bare `python` on lab-desktop holds no package, so rule 1's command fails as written. Change the prompt template to `.venv/Scripts/python.exe scripts/precheck.py`, or have the machine's setup put the venv first on the path?
- `tests/test_session116.py::Records::test_the_tables_on_this_machine_add_up` fails here (see "Read these first"). Rebuild the monthly offers table on this machine, or wait for tomorrow's sync?
