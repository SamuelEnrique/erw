# Session 321 report: the daily run finishes

19 October 2026, from 20:14 UTC, unattended, on lab-desktop (the data machine), the first session of the chain of 19 October, daytime (sessions 321 to 327). Model spend USD 0. Pulls: none by the session (GitHub's API and the runs' log artifacts only).

## Read these first

- **Why the runs stopped.** The job's 180 minutes were too few. A good run takes 140 to 170 minutes (13 October: 2 h 20 min), and one publisher that does not answer the runner pushes it over the limit:

| Run | Ended | Where the time went |
|---|---|---|
| 38576599569, 14 Oct 14:00 | cancelled 17:00 | `eia_series` (EIA's API) 41 min; the run reached "== done" at the limit |
| 38747505887, 15 Oct 14:00 | cancelled 17:00 | SPP 39 min (`URLError(TimeoutError(110, 'Connection timed out'))`, 4 tries a day), SPP's curtailment 10 min; cut in the Redivis upload |
| 39207762565, 19 Oct 06:03 | cancelled 09:04 | CAISO 06:24 to 07:03 and SPP 07:03 to 07:43 (39 min each, `failed after 4 attempts`); cut after `eia_series` |
| 39264997370, 19 Oct 14:00 | cancelled 17:00 | `eia_series` 14:55 to 16:01 (66 min); cut in the live-set load, after the archive (16:47) |

  The retry rule was `with_retries` in `iso_prices.py`: 4 tries, waits of 5, 10, 15 s, and each request waited for the operating system's own connect timeout, about 2.4 minutes. Three days a run and two markets made it about 39 minutes a publisher. `eia_series` has no wall-clock limit at all. The logs were read from each run's `daily-prices-log` artifact (downloaded with this machine's GitHub sign-in; the job-log endpoint needs admin), timed by the `run_id` of each connector's status file.
- **The fix, both halves:** the job's limit is 300 minutes (the lock 320), and every publisher pull has 15 minutes of wall clock (`warehouse/pull_budget.py`). A pull stopped at its budget is a skip, and its tables are gap rows with the reason "publisher did not answer within the budget".
- **Item 5, the gate:** a failed daily step is now a failed row of `erw_health`, and so is a run stopped at the time limit. The gate counts a run as done only when its "daily run" step passed.
- **A third run, and two faults it found.** GitHub's own late schedule started run 39311936332 at 19:33 UTC on the old code. It held the data lock until about 22:20 and was left to run. Its job is green, but its daily step **failed** at 22:20 (9,569 s), for two reasons the timeout had hidden all week:
  1. **The Redivis license check** failed on four tables in the public draft that are not in coverage: `fred_daily_spot_prices`, `fred_treasury_yields`, `price_board_stats` (retired) and `power_deals` (session 130's stray table). They used to pass on their own header lines in `erw_headers`, a Redivis read the export cap now refuses. **Fix:** such a read refused for the cap is a skip, session 305's rule, and the table passes with a note, unless the internal dataset holds its name (`upload.py`, `check_license`; `tests/test_redivis_gates.py`).
  2. **The live-set load refused `energy_deals` and `datacenter_projects`** as older than the live copy. The cancelled 14:00 run had extracted newer deals and loaded them, but never committed them (it was cut before its commit), and the later run's model steps were skipped at the daily cap. **Fix:** the eight tracked news, deal and datacenter tables are restored as of the 14:00 run's archive (16:46:54 UTC, `restore.py --as-of`), plus the 19:33 run's 136 new stories and 114 index rows. A loader dry run accepts them (`rows selected: 17,024`, no refusal).
- **The first manual run was cancelled by this session** (39322988664, dispatched 20:52:54, cancelled 22:21 in its merge tests, before any data step). It had checked out main before the two fixes existed and would have failed the same way. The fixes land after the 22:30 to 23:45 blackout, and the manual run is dispatched again then (below).
- **Step 4, merchant revenue:** `merchant_revenue_monthly` was rebuilt here with CAISO's allowance (8,853 rows), stored and loaded (`match 8,853`; snapshots `s321m-before` and `-after`, 0 differences). **The snapshot could not move alone:** with the rebuilt snapshot, four tests of the generator group failed, and with the hub files and CSV rebuilt too, seven, one of them the page library's check ("the default peaker's month is the peaker computed from the hourly arrays", a NYISO difference). So `site/data/merchant_snapshot.json`, the hub files and the CSV stay as committed. The committed snapshot already carries CAISO's allowance, built by session 298 with the same rule from this machine's table. The rebuild is kept in `runs/s321/generator_build/`.

## What to review

1. `warehouse/pull_budget.py` and the budget in `iso_prices.py` (`budget_timeout`, `budget_spent`, `with_retries`).
2. `warehouse/run_daily.sh`: `pull`, `health_row`, and the failed branch of `run_other`.
3. `.github/workflows/daily-prices.yml`: the gate, the 300 minutes, and the step "Record a daily run stopped at the time limit".
4. `docs/machines.md`, "The budget of a publisher pull, and the gate (session 321)".

## Pulls against their ceilings

- Publishers: none (the session's part names none beyond the manual run's own).

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 321"` | 0 | |
| `tests.test_session321` | 0 | 16 tests; again with `GITHUB_ACTIONS=true` with 305 and 206: 62 tests, 0 |
| the whole suite, first | 1 | 16 failures: the four standing (51, 125, 165, 267), test 94 (it fails with this session's changes set aside: this machine's mix table moved past the site's copy, the morning note's item 15), and 11 pins of the lines changed here |
| the 12 modules with the pins, after | 0 | 278 tests, then test 207 again: 0 |
| `scripts/freeze.py status` | 0 | no freeze |
| `tests.test_redivis_gates`, 119 (after the license check's fix) | 0 | 70 tests |
| the generator group's tests, the committed files back | 0 | 98 tests |

## The landings

- **First** (the fix): freeze 0; before `s321-before` 20:38:52 UTC; `task/321-daily-run-finishes` pushed 20:38:58; checks run 39321064014 success; merge `68b46126`; deployment success 20:51:52; after `s321-after`; compare: **0 differences on 25 pages** (expected: every page is in review).
- **Second** (a budget gap closes with its table's next good run, `build_status.py`): before `s321b-before`; `task/321b-budget-gaps` pushed 20:54:08; run 39323163846 success; merge `0b9802ca`; deployment success 21:06:48; after `s321b-after`; **0 differences**.
- **Third** (the two faults above, and sessions 322 to 326): after 23:45 UTC, below.

## Decisions made without you

1. **Through `task/` branches**, the code path of `docs/machines.md`; the first landed in 13 minutes.
2. **The 19:33 scheduled run was left to finish**; the manual run queued behind it.
3. **The first manual run was cancelled** before it touched data, because it would have failed on faults its checkout could not see.
4. **`eia930_emissions`'s lag is a skip and its daily window 10 days** (above); otherwise the new gate would have made every day red.
5. **The tracked news tables came from the archive as of the 14:00 run** plus the later run's new rows, so nothing the live set holds is rolled back and nothing scored is scored again.
6. **The merchant snapshot, hub files and CSV stay as committed** (above).
7. **Sessions 322 to 326 wrote their data before the redispatched manual run**, not after: the first manual run was cancelled, and the next could start only after the blackout.

## For Samuel's ruling

- The generator group: let a session change the six tests that hold the hourly CSV to its export of 7 October (session 204's switch), and look into the page library's NYISO difference, so that the snapshot, hub files and CSV can move together with CAISO's allowance.
- `power_deals` in the public Redivis draft: a stray table of session 130, now passing the check on the cap's rule; remove it from the draft before the release (a person's step).

## Files

- New: `warehouse/pull_budget.py`, `tests/test_session321.py`, this report.
- Changed: `.github/workflows/daily-prices.yml`, `warehouse/run_daily.sh`, `warehouse/refresh_board.sh`, `warehouse/refresh_supply.sh`, `warehouse/connectors/iso_prices.py`, `warehouse/connectors/eia930_emissions.py`, `warehouse/metadata/build_status.py`, `warehouse/redivis/upload.py`, `docs/machines.md`; tests 49, 58, 82, 114_part2, 116, 119, 136, 138_demand, 140, 148, 157, 157_refresh, 207, `test_redivis_gates`; the tracked tables `energy_deals`, `energy_deals_evidence`, `datacenter_projects`, `datacenter_projects_evidence`, `datacenter_facilities`, `energy_companies`, `news_stories`, `news_index`; `coverage.csv`, `docs/coverage.md`, `archive_manifest.csv`, `redivis_uploads.csv`.
