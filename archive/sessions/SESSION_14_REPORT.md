# Session 14 report

Energy Research Warehouse (ERW), session 14, run 2026-09-26 to 2026-09-27 (UTC). Every task in SESSION_14_PROMPT.md was carried out, and the three human rulings applied:
1. CAISO stays `lmp_rtm_5min`.
2. ISO-NE hourly real-time gets per-day completeness.
3. The two datacenter digest scores stand, with no rubric change.

Nothing was pushed. No key was printed or committed.

**Read this first: none of the fixes below is on GitHub until a human pushes.** GitHub's `main` is still `6c4b3ea`. Any daily run before a push, a re-trigger or the 14:00 UTC schedule, runs the old workflow. With the secrets now set, that old workflow would get past the restore. It would then commit a `coverage.csv` that has lost 32 tables, and delete those tables' catalogue rows and headers from the live site's Supabase. That second defect is Task 1's main finding. As of 00:15 UTC, no re-triggered run had started.

## What was built

| Task | Result | Commit |
|---|---|---|
| 1 | Cause of the CI failure found; secret checks as the first step of both workflows; a second defect found by the fresh-clone test and fixed; `latest-prices` checked and its command run from the clone | `363dc72` |
| 2 | Per-day completeness for `isone_rtm_zone_prices_hourly`; 30-day rerun (29 of 30 days); validator, coverage, Supabase load; Redivis draft brought current | `1af3a6b` |
| 3 | Evaluation on `questions_s13.yaml` with the timezone fix: **30 of 30** | `20a3f40` |
| 4 | Root `README.md` rewritten; `STATUS.md` and its generator, built by the daily run | `b43ba74` |
| 5 | This report | final commit |

## Task 1: the CI failure

### The exact cause

Run `36277995065` (manual dispatch, 22:59 UTC, commit `6c4b3ea`) failed at the step "Pull, validate, rebuild coverage", 50 seconds after starting.
- **What passed first:** the job's steps, read from the GitHub API, show that checkout, Python 3.12, the dependency install and the merge tests all passed.
- **The empty secrets:** the step's environment in the log shows `REDIVIS_OWNER`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` and `PJM_API_KEY` empty, while `EIA_API_KEY`, `ANTHROPIC_API_KEY` and `REDIVIS_API_TOKEN` were set.
- **Where it stopped:** `run_daily.sh` begins with the Redivis restore (`RESTORE_FROM_REDIVIS=1`). `upload.py --restore` printed "REDIVIS_OWNER is not set (.env or environment); nothing uploaded" and exited 1, and `run_daily.sh` stopped: "restore from Redivis failed: stopping, so a partial window is never uploaded over a full one".
- **Missing secrets were the only cause of that failure.** Run from a fresh clone with the secrets present, the same restore succeeded, downloading 23 rolling-window tables. Every later step the run had not reached also passed there, up to coverage (below).
- **`PJM_API_KEY`** is empty too, but no step uses it yet, so it is not required.

### The secret checks

Both workflows now begin, before checkout, with a step that checks every required secret:

| Workflow | Secrets checked |
|---|---|
| `daily-prices.yml` | `EIA_API_KEY`, `ANTHROPIC_API_KEY`, `REDIVIS_API_TOKEN`, `REDIVIS_OWNER`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` |
| `latest-prices.yml` | `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` |

- **On failure:** an `::error` annotation for each missing secret naming it and where to set it, then "Missing repository secrets: ... Nothing was run.", then exit 1.
- **Tested** under `bash -e` (how the runner executes a step), with all secrets empty, one missing, and all set. Each case gave the right exit code and message. Both files parse, with `schedule` and `workflow_dispatch` in `on:`.

### The fresh-clone test, and the defect it found

**How it ran.**
- **The clone:** a `git clone` of this repository at `6c4b3ea`, with the Task 1 changes applied, so no table was present, as on the runner.
- **The commands:** the workflow's own, in order: the secret check, `python -m unittest discover -s tests -v`, then `bash warehouse/run_daily.sh 2>&1 | tee daily.log`.
- **The environment:** `DAYS=3`, `RESTORE_FROM_REDIVIS=1` and `GITHUB_ACTIONS=true`, with the secrets from `.env` passed as environment variables.
- **`GITHUB_ACTIONS=true`, not `=1`:** the prompt said `=1`, but GitHub sets `true` and the code tests for exactly `"true"`. With `1`, the peak-premium script would fail instead of skipping, and the runs would be recorded as local.
- **Two differences from the runner:** the local Python 3.14 venv instead of 3.12, and `DRY_STORES=1` (new), so the test wrote to neither Supabase nor the Redivis draft.

**What passed, in order:**
- the secret check and 11 of 11 tests;
- the restore, 23 tables;
- every ISO connector except the two expected failures: SPP real-time (its known file gap) and ISO-NE hourly (the clone did not yet have Task 2);
- the peak-premium script, skipped with its CI warning;
- every other connector, including EIA-860M;
- news ingest, scoring and index;
- **the validator: every table passed.**

**Where it stopped.** Claude Code stopped the run during coverage because the machine was low on memory, not because of the run. As instructed, the full run was not restarted. The steps it had not reached were then run one at a time in the same clone: coverage, `load.py --dry-run` and `upload.py --changed --dry-run`.

**The defect.** Coverage was built from whatever CSVs the machine holds. The runner restores only the rolling-window tables, so the old `build_coverage.py`, run on the clone, wrote **49 tables instead of 81**. It dropped:
- the 24 ERCOT yearly history tables;
- the 2 peak-premium tables;
- the 6 queues, which are pulled on Mondays only.

The workflow commits that `coverage.csv`. Next, `load.py` deleted Supabase catalogue rows for tables not in coverage. It also deleted every table's provenance headers but reinserted only those of the tables present. Then the shrunken coverage went to Redivis as `erw_coverage`. **The first successful CI run would have removed 32 tables from the committed coverage, from the site's `/data` page and catalogue, and from their citations.**

**The fixes:**
- **`build_coverage.py`** carries over, unchanged, any table in the previous coverage whose CSV is not on the machine: its CSV row and its line in `docs/coverage.md`. It names those tables in a note under the table, and never drops one; retiring a table is a human edit.
  - On the clone: **81 tables, 49 built there and 32 carried over.**
  - On this machine: 81 built, 0 carried, output identical to before.
- **`load.py`** replaces only the headers of the tables it loaded. For a table not on the machine, it updates only the coverage fields in the catalogue and keeps `in_live_set`, `columns` and `rows_sha256`.
  - The clone's dry run selected 34 live-set tables and left the other 32 alone.
- **`DRY_STORES=1`** in `run_daily.sh`, and `upload.py --dry-run`, make this test repeatable without writing to shared stores. CI never sets it.

**A related risk, removed in Task 2.** The Redivis draft still held session 10's windows: 3 days of MISO real-time, 144 rows of ERCO demand. The clone's restore got exactly those. A CI run would then have loaded those thin windows into Supabase and overwritten session 13's 30-day backfills. Task 2 uploaded the 11 changed tables to the draft.

### Why `latest-prices.yml` has not run

**Nothing in the file prevents it:**
- the cron `*/15 * * * *` is valid;
- `on:` has `schedule` and `workflow_dispatch`;
- the install is the daily job's, and it succeeded on GitHub;
- `requirements.txt` holds every import of `latest_prices.py`;
- its secrets are the Supabase pair, and now it checks them first.

**What GitHub reports.** The GitHub API reports the workflow `active`, registered at 22:42:31 UTC when `main` was pushed, with **0 runs as of 00:15 UTC**: 93 minutes, or six missed 15-minute slots. GitHub runs schedules on a best-effort basis, and this repository's daily cron (14:00 UTC) started at 17:27 UTC, 3.5 hours late. So the delay is GitHub's scheduler, not the file.

**Its command works from a fresh clone:** `python warehouse/connectors/latest_prices.py`, with only the two Supabase secrets set, fetched all 39 hubs and zones from six ISOs and "upserted 39 rows into Supabase latest_prices" (newest interval 23:55 UTC).

**To prove it on GitHub,** run it once by hand: Actions, latest prices, Run workflow. The workflow allows `workflow_dispatch`.

## Task 2: ISO-NE hourly real-time, per day

`isone_rtm_zone_prices_hourly` now uses the session 13 per-day mode. The 30-day run of ISO-NE:

| Table | Days written | Gaps |
|---|---|---|
| `isone_rtm_zone_prices_hourly` | 29 of 30 | 2026-09-25: ISO-NE served an empty final-report file (`EmptyDataError`) four times; now a gap row, not a failed table |
| `isone_rtm_zone_prices` (15-minute) | 24 of 30 | the same 6 days as session 13 (real holes in ISO-NE's 5-minute data) |
| `isone_dam_zone_prices` | complete | none |

**The steps after the rerun:**
- **Run status:** the rerun was recorded in `run_status.csv`: 12 rows, 7 of them gaps. New gap rows read "day incomplete" (session 13's fix).
- **Validator:** exit 0, every table. Coverage: 81 tables.
- **Supabase:** all 66 tables and the catalogue and sources match; 61 tables unchanged and skipped by their hash; 256.2 MB, under the 300 MB guard.
- **Redivis:** the 11 tables changed since session 10 (the session 13 and 14 backfills and the news tables) uploaded to the draft with `upload.py --changed`: **14 of 14 counts match, nothing released**. CI's restore now starts from the full windows. `warehouse/metadata/redivis_uploads.csv` is committed with them.

## Task 3: the evaluation with the timezone fix

Same 30 questions, `questions_s13.yaml`, not edited. Its expected answers were first recomputed from today's tables into a scratch file: no difference, so the set still holds. No code in the loop or the check changed. The run is `20260927T001104Z`.

| Measure | Session 12 | Session 13 | **Session 14** |
|---|---|---|---|
| Correct | 27 of 30 | 28 of 30 | **30 of 30** |
| number | 25 of 28 | 26 of 28 | 28 of 28 |
| citation | 25 of 28 | 28 of 28 | 28 of 28 |
| refusal right | 27 of 30 | 30 of 30 | 30 of 30 |
| Retried after the number check | 7 | 5 | 7 (all passed on the retry) |
| Mean tool calls | 2.93 | 1.73 | 1.57 |
| Cost per question: mean / median | USD 0.0433 / 0.0269 | USD 0.0195 / 0.0119 | USD 0.0185 / 0.0124 |
| Cost, total | USD 1.2996 | USD 0.5844 | USD 0.5536 |
| Time per question: median / max | 11.4 / 43.4 s | 6.8 / 25.6 s | 6.5 / 36.1 s |

- **The fix worked:** q01 and q09, the two local-operating-day questions the timezone bug failed in session 13, now pass. The model called `query` with `tz` and got the right local day: 33.39 (ERCOT HB_NORTH, 2026-09-25, America/Chicago) and 33.65 (ISO-NE hub, 2026-09-24, America/New_York).
- **The seven retries** were all descriptive numbers the unchanged check caught: "15" (q02, q03, q08, q12), "21" (q13), "930" (q29), and "5" and "4" from UTC offsets the model wrote in q01's first draft. All passed on the second draft.

## Task 4: the public face

**`README.md`, for a first-time visitor:**
- the positioning paragraph and the site link;
- three screenshots: the price board, the explorer, and an answer on `/ask`;
- what is in the warehouse, by family, with counts read from `coverage.csv` by a script, not typed: **81 tables and 3,751,828 rows as of 2026-09-26, 75 of them public** (3,629,472 rows);
- what is not in it yet;
- a way to fetch a table that works from a fresh clone with no API key. It clones, installs, runs ERCOT's connector for 3 days, then fetches and cites. The fetch was checked against the fresh clone's ERCOT table;
- how the daily and 15-minute refreshes work;
- the license rule;
- the IRW lineage, with credit to Ben Domingue and colleagues and to the Stanford independent study;
- a documents table, and the session log (sessions 1 to 14, each linked to its report).

**The honest state of access, stated in the README:** the tables are not in git; Redivis opens when a human releases the first version; the Supabase and Redivis backends need credentials.

**`STATUS.md`** is written by `warehouse/metadata/build_status.py`, which `run_daily.sh` runs after the digest, and which the daily workflow commits. Every number is read, not typed:
- **Tables and rows:** from `coverage.csv`, public and internal.
- **Last runs:**
  - the newest daily run on GitHub and the newest local one, from `run_status.csv`, with their ok, failed, gap and skipped counts;
  - for the 15-minute job, the newest `retrieved_at` in Supabase's `latest_prices`, because that job keeps no run record.
- **Tables whose last run failed.**
- **Open gaps:** every gap day in `run_status.csv`, re-checked against its table with the connector's own completeness rule (`missing_report` for ISO tables, the core-variable rule for EIA-930). A gap closes only when the table proves it filled. A table not on the machine is listed as not verifiable there.
- **Today it shows:**
  - no daily run from GitHub in this tree;
  - the last local run;
  - latest prices at 23:59 UTC, from the fresh-clone test;
  - 1 table whose last run failed: SPP real-time (its known file gap). ISO-NE hourly left this list once its per-day run was recorded;
  - 11 open gaps.

## Decisions

1. **`GITHUB_ACTIONS=true` in the clone test,** because that is the value the runner sets and the code tests.
2. **Carry over, never drop.** A table missing from one machine is not a table missing from the warehouse. Removing a table from coverage is a human edit.
3. **The full clone run was not restarted** after Claude Code stopped it for low memory. Its remaining steps were checked one at a time.
4. **The Redivis draft was brought current before any successful CI run could restore from it.** It is the pipeline's own draft-only step; nothing was released.
5. **`PJM_API_KEY` is not a required secret.** No step uses it.
6. **The README's example uses ERCOT,** the one source that needs no key, so it runs for a stranger today.

## Errors hit

1. **The simulated CI run was stopped for low memory** during coverage (Decision 3).
2. **The first `run_status` gap detail** ("incomplete data, no file written") was fixed in session 13; this session's gap rows use the new wording.

## Rerun

```bash
# the workflow logic in a fresh clone, writing to no shared store
git clone . /tmp/ci && cd /tmp/ci
GITHUB_ACTIONS=true RESTORE_FROM_REDIVIS=1 DRY_STORES=1 DAYS=3 bash warehouse/run_daily.sh
python warehouse/connectors/iso_prices.py isone --days 30
python warehouse/chat/eval/eval.py --questions warehouse/chat/eval/questions_s13.yaml
python warehouse/metadata/build_status.py
```

## Open questions for the human

1. **Push `main` before the next daily run.** Until then, a run with the secrets set would shrink the committed coverage and remove 32 tables from the live site's catalogue (Task 1).
2. **Run `latest prices` once by hand** (Actions, latest prices, Run workflow) to confirm it on GitHub, since its schedule has not fired yet.
3. **After the push, trigger `daily prices` by hand.**
   - Its first step now names any missing secret.
   - Its commit should then show `STATUS.md`, and `coverage.csv` with 81 tables (32 carried over).
   - Watch its "Report a failure" step: it opens an issue whenever the job fails.
4. **Large files in history** (GitHub's `GH001` warning on the last push) remain; removing them means rewriting published history.
