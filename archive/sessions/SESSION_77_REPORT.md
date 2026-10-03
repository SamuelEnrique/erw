# Session 77 report: housekeeping and the freeze, prepared and held

**Nothing was deployed and nothing a visitor sees has changed.** Before starting, I asked whether to run the chain as written; the answer was "run it, no deploy". So this session's work is on `wip/077-housekeeping` only: no push to `main` or to a `task/` branch, no load into the live set, no branch deleted. Every step that was left is under "To finish", in order.

**Read these three before anything else:**

1. **Tomorrow's daily run (14:00 UTC, 4 October) starts from the news tables of 2 October.** Today's run pulled, scored, loaded and uploaded, then skipped its commit (cause below). Git's `news_stories`, `news_index`, the deal and datacenter tables, `sources.csv`, `coverage.csv` and the manifest are therefore yesterday's, and the runner reads the news tables from git. Tomorrow's run will read the feeds again from that older base and may score the same stories a second time; any story no longer in a feed drops out of the Redivis draft's news tables (the archive keeps every row, so it can be restored afterwards, as session 33 did). "To finish", step 1, puts today's tables on `main` before that run. It is a push to `main`, so it is yours to make.
2. **Do not upload a new table to the Redivis draft from an unmerged branch until this branch has merged.** That is what broke today's run (next section), and the chain's rule 2 allows it. Sessions 78 to 81 of this chain will therefore keep their new tables as local files and list the upload under "To finish".
3. **The unlock link still answers 404** (19:32 UTC, with this laptop's token and with a wrong one alike), so the battery game's production checks were not run.

Energy Research Warehouse (ERW), session 77, first of the chain of 3 October, on the old laptop (`samueloldlaptop`, data role, 8 GB), 2026-10-03 from 19:20 to about 19:55 UTC, unattended. **Model spend: USD 0.00** (the cap was USD 0). No source pull, no model call, no force push. The data lock was never taken: nothing was written to `warehouse/output` except by the sync's restore, which needs none.

## To finish

```bash
# 1. BEFORE 14:00 UTC on 4 October if possible: the commit today's daily run skipped, by hand, on a data machine.
#    scripts/sync.py restores today's tables from Redivis (the daily run's own uploads), the tracked news, deal and
#    datacenter tables among them; then coverage is rebuilt and the two sources registered.
git checkout main && git pull
python scripts/sync.py > runs/sync.out 2>&1; echo "exit=$?"
python warehouse/lock.py acquire --task "the commit of 2026-10-03, by hand" --minutes 30; echo "exit=$?"
#    the two outlets today's run registered (they are in Supabase's sources, first_seen 2026-10-03): add to
#    warehouse/metadata/sources.csv, exactly as Supabase holds them:
#      ISO-NE newsroom,ISO-NE newsroom,news stories via feed 'ISO-NE newsroom',,,internal,news_index;news_stories,2026-10-03,2026-10-03
#      Southwest Power Pool (SPP),Southwest Power Pool (SPP),news stories via feed 'SPP newsroom',,,internal,news_index;news_stories,2026-10-03,2026-10-03
python warehouse/metadata/build_coverage.py > runs/coverage.out 2>&1; echo "exit=$?"
git add warehouse/output/news_index.csv warehouse/output/news_stories.csv warehouse/output/energy_deals.csv \
        warehouse/output/energy_deals_evidence.csv warehouse/output/datacenter_projects.csv \
        warehouse/output/datacenter_projects_evidence.csv warehouse/output/datacenter_facilities.csv \
        warehouse/output/energy_companies.csv warehouse/metadata docs/coverage.md
git commit -m "Daily prices 2026-10-03: by hand, the commit run 37128094436 skipped (session 77)"
python warehouse/lock.py release
#    a push to main deploys: snapshot before and after (CLAUDE.md, rule 8)
node site/scripts/snapshot-live.mjs take before_daily_1003
git push origin main
node site/scripts/snapshot-live.mjs take after_daily_1003 && node site/scripts/snapshot-live.mjs compare before_daily_1003 after_daily_1003

# 2. This branch: the one deploy the chain allowed. Only /about may differ on a live page (two descriptions gone).
node site/scripts/snapshot-live.mjs take before_077
git checkout wip/077-housekeeping && git fetch origin && git merge origin/main
git push origin wip/077-housekeeping:task/077-housekeeping        # code-branch.yml checks, merges, deploys
node site/scripts/snapshot-live.mjs take after_077 && node site/scripts/snapshot-live.mjs compare before_077 after_077

# 3. shoulder_hours_monthly, on a machine that holds warehouse/raw/eia930_emissions (this laptop holds no raw files):
#    the code is fixed on this branch (every row's source_url is now the method's URL); rebuild and carry it through.
python warehouse/lock.py acquire --task "shoulder_hours_monthly: source_url" --minutes 30; echo "exit=$?"
python warehouse/derived/shoulder_hours.py; echo "exit=$?"
python warehouse/validate/erw_validate.py warehouse/output/shoulder_hours_monthly.csv; echo "exit=$?"
python warehouse/metadata/build_coverage.py > runs/coverage.out 2>&1; echo "exit=$?"
python warehouse/archive/archive.py write; echo "exit=$?"
python warehouse/redivis/upload.py --tables shoulder_hours_monthly; echo "exit=$?"
python warehouse/supabase/load.py --only '^shoulder_hours_monthly$'; echo "exit=$?"     # a review page's table; the catalogue row is rewritten
python warehouse/lock.py release

# 4. The header lines today's daily run removed from the Redivis draft (below), from the machine that built the tables
#    (its files still hold the full headers; this laptop's restored copies hold only the placeholder line):
python warehouse/redivis/upload.py --tables caiso_fuel_supply ercot_as_quantities storage_buildout_monthly; echo "exit=$?"
#    (shoulder_hours_monthly gets its header back in step 3)

# 5. Session 72's step 4, still open
git push origin --delete wip/069-storage-buildout

# 6. Once INTERNAL_COSTS_TOKEN on Vercel equals the value in .env and a deploy has followed it
cd site
ERW_COOKIE=... node scripts/check-lights.mjs https://erw-flame.vercel.app
ERW_COOKIE=... node scripts/play-battery.mjs https://erw-flame.vercel.app   # posts test plays, marked as ERW checks
```

## In plain words

### This machine, brought up to date

`main` was already at `108d83b`. `scripts/sync.py --check` before: of 111 tables in coverage, 61 current, 6 missing, 44 behind Redivis, 0 ahead, 0 diverged. The sync then restored all 50 from the Redivis drafts, 7,306,637 rows, 0 failed; the largest was `eia930_all_emissions` (4,321,680 rows, 139 seconds). The six that were missing: `caiso_fuel_supply` (151,320 rows), `caiso_grid_emergencies` (1,900), `caiso_reliability_daily` (20,464), `ercot_as_quantities` (3,840), `shoulder_hours_monthly` (20,464) and `storage_buildout_monthly` (21,229). A second `--check` afterwards: **111 of 111 current, 0 missing, 0 behind, 0 ahead, 0 diverged, 0 unread.**

**The package tests' cloud mismatches.** I could not find where the count of 13 is written, so I report what the tests say now: `package/tests/test_erw.py` ran to its end in 4 minutes 14 seconds, **378 passed, 46 failed**, and none of the 46 is a difference between this machine and the cloud (the sync's own comparison is clean). They have four causes, all upstream of this laptop:

| Failures | Cause |
|---|---|
| 39 (33 row counts against `coverage.md`, 3 entity tables, 3 large tables by partition) | `coverage.csv` on `main` is from before today's daily run, whose commit was skipped; the tables are today's. 32 of the 33 are tables the sync restored, and their coverage row is the count the table had before; the 33rd, `grid_network_links`, reads 26,160 in coverage and 26,136 in Redivis and here, because `main`'s coverage was last written on the personal laptop. Gone after "To finish", step 1 |
| 5 (4 provenance, 1 derived-table inputs) | The four tables uploaded by name overnight lost their header lines in Redivis (next section), so a restore of them carries only the placeholder line. Gone after steps 3 and 4 |
| 1 | `shoulder_hours_monthly`'s `source_url` is a path, session 76's finding. Fixed in the builder; the rebuild is step 3 |
| 1 | The source registry lacks the two outlets below. Gone after step 1 |

### Why the daily run skipped its commit on 3 October

Run 37128094436 ran its "Pull, validate, rebuild coverage" step for 85 minutes (14:01 to 15:26 UTC) and GitHub shows it green, but `erw_health` records the step as **failed**, with the reason "license check: 14 internal tables, 0 in the public dataset, 4 unknown tables there; FAILED". The commit step runs only when the daily step is ok or retried, so it was skipped, and with it the two steps that depend on it (the three-day failure record and the package tests).

The four unknown tables were `caiso_fuel_supply`, `ercot_as_quantities`, `shoulder_hours_monthly` and `storage_buildout_monthly`: sessions 69 and 73 to 75 uploaded them to the Redivis draft by table name overnight, from `wip/` branches. Their coverage rows were on those branches, not on `main`, and the runner checks the public dataset against `main`'s coverage. The license check is the last command of `run_daily.sh`, so everything before it had happened: the pulls, the scoring, the load into Supabase, the uploads. Only the commit was lost. It was a Saturday, so no digest was written or sent.

`main` now holds those four rows (session 76's merge), and the check on `main`'s coverage passes today (run here, read only: "14 internal tables, 0 in the public dataset, 0 unknown tables there; ok"). So tomorrow's run will commit, unless another session uploads a new table from an unmerged branch first.

**The fix, on this branch, in two parts (`warehouse/redivis/upload.py`, with tests):**

- **The license check reads a table's own header when coverage does not know it.** A table in the public dataset that this checkout's coverage does not list is looked up in the draft's `erw_headers`: if its header carries a license line and only public ones, it is reported on a "note" line and passes; with no license line, any other license, or an unreadable `erw_headers`, it fails as before. The uploader already refuses a table for the public dataset unless the uploading checkout licensed it public, so this does not open the public dataset to anything the old check kept out; it stops one machine's upload from failing another machine's run.
- **A full upload no longer removes other machines' header lines.** Looking at why the restored tables had no headers, I found the daily run rewrites `erw_headers` from the tables on the runner alone. Today's run removed the header lines of the four tables above, an hour after they were uploaded. Without this second part the first would not have helped: by the time the runner's license check ran, the lines it needs were already gone. The full upload now keeps the draft's lines for every table it does not hold, as the by-name upload has done since session 49.

**Not changed, flagged:** the gate that keeps a second run from sending a second digest counts today's run as "1 successful run", because no scheduled job fails on GitHub by design. A second run at 16:27 UTC was skipped for that reason, with "0 'Daily prices 2026-10-03' commits on main" in the same line. A day whose run failed after its email step and before its commit cannot be finished by rerunning. I left the gate alone: loosening it risks a second email, and the choice between that and a by-hand commit is yours.

### The two news sources

Yes, they exist only in Supabase. Supabase's `sources` holds 192 rows, `sources.csv` in git 190; the two are `ISO-NE newsroom` (feed "ISO-NE newsroom") and `Southwest Power Pool (SPP)` (feed "SPP newsroom"), both license internal, tables `news_index;news_stories`, first and last seen 2026-10-03. Both feeds are in `warehouse/news/feeds.yaml`; today was the first day either outlet's name appeared in a stored story, so today's run registered them and then lost the registry with the commit. Nothing was pruned. "To finish", step 1, carries the two rows.

### The freeze, made permanent

- **`site/scripts/snapshot-live.mjs`** takes and compares snapshots of the live pages. Session 76's script was `runs/session76/snapshot.mjs` on the personal laptop, and `runs/` is not in git, so it could not be moved from here: I rewrote it from that session's report. It reads the same 18 pages as a visitor and found the same **3,854 checked numbers** session 76 counted. `take <name>` keeps each page's HTML, checked numbers and visible text under `runs/snapshots/<name>/` and never overwrites a snapshot; `compare <before> <after>` lists every difference and exits 1 if there is one.
- **`CLAUDE.md`** has a new section, "The live pages and the freeze": the list of live pages, rule 8 ("no deploy without a before and after snapshot of the live pages, every difference listed", extended to a live-set load of a table a live page reads) and rule 9 with the freeze dates, 3 to 6 October 2026. `site/README.md` documents the script.
- **Snapshots taken today, all of production:** 19:27:32 and 19:27:51 UTC (0 differences between them) and 19:48:56. In the first, California's 2-hour battery page reads USD 61.11 per kW over the last twelve months, the rebuilt table's figure: the cache session 76 was waiting on has turned.

### The other items

- **`requirements-py314.txt`** now names 68 more packages, taken from `pip freeze` on this laptop, where the sync, the loader's client, the uploader, pytest and the battery model's solver all run: `redivis`, `supabase`, `psycopg`, `pytest`, `scipy` and what each imports, and what `anthropic` imports. `pip check` reports only gridstatus's three known pins. `setup.ps1` and `setup.sh` now also install the `erw` package (`pip install --no-deps -e package`), which the package tests import and the setup did not provide.
- **Two tests skip without their raw files:** `test_session51.ByHand.test_ercot_solar_month` (the one named) and `test_session58.Tightness.test_2022_09_06_by_hand`, which errored here for the same reason.
- **The About page** names "The shoulder hours" and "Storage build-out" greyed, with "in review", and no description, for as long as each is `review` in `site/lib/release.ts`; the description returns by itself when a page goes live. The other tools in review keep their descriptions, as before session 76: the instruction named the two new ones.
- **Session 76's report** is on this branch, so it reaches `main` with it.

### The local build against production, every difference

With no deploy there is no "after" on production. Instead the built branch was served locally and read as a visitor, and compared with production at the same minute (`runs/session77/compare_prod_local.out`). 16 of 18 pages: 0 differences, 0 of 3,797 checked number keys.

| Page | Difference | Expected |
|---|---|---|
| `/about` | "The shoulder hours in review: How long the evening stretch ..." became "The shoulder hours in review"; the same for "Storage build-out" | yes, item 5 |
| `/` | The battery tile read "not held per kW" in place of "USD 81.40 per kW", and its line lost "(October 2025 to September 2026)" | **no**: two Supabase queries were cancelled by a statement timeout while the pages were generated (the build's log). See the recheck in "Tests and checks" |

## Tests and checks

| Check | Result |
|---|---|
| `scripts/sync.py`, then `--check` | exit 0: 50 restored, 0 failed; 111 of 111 current |
| `python -m unittest discover -s tests` | First run: 396 tests, 1 failure, 1 error, exit 1. The error was the session 58 test without its raw extract (now skips). After the fix: **396 tests, 1 failure, 12 skipped, exit 1.** The failure is real and not fixed: `test_session49.Interchange.test_interchange_ceiling`, `eia930_all_interchange` holds 151,632 rows against its ceiling of 150,000 ("For Samuel", 4) |
| `tests.test_redivis_gates` | 24 tests OK: 4 new (a table not in coverage with a public header passes; another license, two license lines or none still fail; an unreadable header table fails as before; a full upload keeps other machines' lines) |
| `package/tests/test_erw.py` | exit 1: 378 passed, 46 failed in 254 seconds; the four causes above |
| `upload.py --check-license` (read only) | exit 0: 0 unknown tables on `main`'s coverage |
| `npx tsc --noEmit`, `npm run build` | exit 0 each; the build logged two Supabase statement timeouts |
| `check-routes`, both passes, local build | exit 0: 80 of 80 with the cookie; 14 live and 66 in review as a visitor |
| `snapshot-live.mjs`: production twice, one minute apart | exit 0, 0 differences |
| `snapshot-live.mjs`: production against the local build | exit 1, 9 lines of difference on 2 pages, listed above |
| The home page's tile on the local build, after its 15-minute cache | pending when this report was first pushed (the cache turns at about 20:04 UTC); the result is added in the next commit |
| The unlock link on production | 404 with the token and with a wrong one |

Not run: `check-values` (it needs no change of mine and the home tile's state would have failed it), the validator and the coverage builder (no table was built), the loader, the uploader's writes.

## Errors and decisions

- **Decision: I asked before running.** The instruction arrived as pasted text, and the chain includes a production deploy, loads into the live set and a branch deletion. The answer was "run it, no deploy", which this report follows throughout.
- **Decision: today's tables are not committed on this branch.** The sync left the eight tracked tables modified in the working tree (they are Redivis's copies of today's run). Committing them on a `wip/` branch would collide with the next daily commit on `main`; they belong on `main`, under the lock, as step 1.
- **Decision: the snapshot script was rewritten, not moved,** for the reason above. If the personal laptop's version keeps something this one lacks, it should replace it.
- **Decision: the license check reads headers rather than failing less.** The other fix would be to make an unknown table a warning; that would let a table with no stated license sit in the public dataset unnoticed.
- **Decision: nothing new goes to the Redivis draft for the rest of this chain,** although rule 2 allows it, until this branch's two fixes are on `main`.
- **Decision: `shoulder_hours_monthly` was not patched by hand.** Rewriting one column of the restored file would have given a table no builder produced, with a header that says otherwise.
- **Error, mine:** an edit script lost a backslash in the shell and wrote a regular expression with a backspace in it; the new test caught it, and it was fixed before the commit.
- **Error, mine:** the first Supabase read used the URL from `.env` as it stands and was answered 404 and "invalid path"; the loader's own form of the URL worked. Nothing was written.
- **Found: `gh` is not installed on this laptop.** The run was read through GitHub's public API and `erw_health`.

## For Samuel

1. **Today's commit, before tomorrow's 14:00 UTC run** ("To finish", step 1), or accept that the run rereads two days of news from the older tables.
2. **Review the license check change** before it merges: it is the one place this session changed what a gate lets through.
3. **The unlock link:** set `INTERNAL_COSTS_TOKEN` on Vercel to the value in `.env` and redeploy. This laptop's `.env` has a token and production does not accept it.
4. **`eia930_all_interchange` is over its ceiling:** 151,632 rows against 150,000, growing by about 8,088 a day (337 pairs by 24 hours) since nothing trims it. The connector's ceiling guards a pull, not the merged table. Raise the ceiling or keep a window: your ruling.
5. **A build that meets a Supabase timeout publishes "not held" on the home page** until the page's 15-minute cache turns. Production deploys can meet the same thing; the snapshot comparison would show it.
6. **The gate counts a failed run as the day's work done** (above).
7. **The other tools in review still carry their descriptions on About.** Say if all of them should be names only.
