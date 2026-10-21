# The chain of 20 to 21 October 2026, night, on the code machine: the note for Samuel

Energy Research Warehouse (ERW), session 383, 21 October 2026. The chain `queue/done/014-night-20-october-code.md` (sessions 381 to 383) ran on samueloldlaptop, unattended, from 22:31 UTC on 20 October, after the owner's prompt of that evening (the "To finish" of `docs/state/review_2026-10-20_day_code.md` first, then 014, then 015). Every page is in review: open `https://erw-flame.vercel.app/internal/open` first. Model spend USD 0. No pull from any publisher; no warehouse data written.

## First: what holds the landing

1. **Supabase answers the heavier reads with statement timeouts since about 23:30 UTC on 20 October** (`canceling statement due to statement timeout`, code 57014). A probe of one ordered read of `series` failed every two minutes from 02:00 to past 03:00 UTC. Production prints "The live set could not be read" on `/cost-of-power?grid=spp` and `?grid=ercot` and answered 504 on `?grid=nyiso`. The scheduled jobs still pass (the latest prices, the hourly network, the chain watch). A build reads some tables as required (`site/lib/supabase.ts`), so every build since then has failed or cached an empty block: GitHub's check of `task/367-372` failed twice on it (runs 39525362021 and its re-run), and the local builds of 381 and 382 stopped on it three times each. The cause is not seen from the code machine (the data lock is free; nothing in `erw_health` explains it). Look at the project's database health in Supabase's dashboard (its disk input and output budget especially).
2. **The landing waits on that**, on one branch: `wip/381-382-land` holds `wip/367-372-day` (sessions 367 to 372, with origin/main merged and the floor written), session 381's second part and session 382, and main's commit that took 014 from the queue. "To finish" below is every command.
3. **From 00:00 UTC on 21 October the license holds of `license_status.csv` are in force on the site** (the public day). Two faults showed at once: `test_session166` counted the four missing ancillary tables while NYISO is now greyed first (fixed in the test, `b39bada3`); and the generator page held every model figure on every grid, not only ISO-NE's and NYISO's (session 382 found it and fixed it in `lib/license.ts`, `c5c3b806`, with its test). Both are on the landing branch, not on main: until it lands the generator page in review shows "license needed" on ERCOT, CAISO and SPP too.

## What each session did

| Session | State | Address to open |
|---|---|---|
| 381, first part: 367 to 371 through the gate | on `wip/381-382-land`, not landed (above) | `archive/sessions/SESSION_381_REPORT.md`, "The landing of 367 to 371" |
| 381, second part: the five tools against roadmap item 2 | on `wip/381-382-land` | `docs/reviews/packs/battery.md` (and `generator.md`, `datacenter.md`, `research.md`, `grid.md`), "Against roadmap item 2 (session 381)" |
| 382, the trader path click by click | on `wip/381-382-land` | `docs/reviews/trader-path.md`; `https://erw-flame.vercel.app/cost-of-power/seller` after the landing |
| 383, this note and the queue | on `wip/381-382-land` | this file |

- **381**: a table a tool against item 2's "done"; no method note is signed; a new replication of Research's nine cards from their CSVs alone (`site/public/findings/erw_2026_research_replication.py`: 304 of 304 figures equal); cross-check sections in `docs/methods/grid_network.md` (11 rows) and `docs/methods/automated_analysis_findings.md` (4 rows). The battery, datacenter, generator and Grid mirrors ran, exit 0. The checks that read a built site were not run (the timeouts).
- **382**: 16 steps through `/cost-of-power/seller`, `/cost-of-power/battery` and `/board`, each with its address, its click, its checked figure and key, and what a trader would ask that the page does not answer; 32 shots; the generator page's hold fixed (above). check-values on the seller page: 240 of 240.

## The screenshot folders

- `docs/brand/review-370/after/` (the cards at 1280 and 390, from session 370's cycle); `docs/brand/review-382/` (the trader path, 16 steps at 1280 and 390, and the walk's script and records).

## Decisions made without you

1. **origin/main merged into `wip/367-372-day` before the landing checks**, so that they ran on what would land; its five conflicts were records: `sources.csv` keeps the code machine's `iso_queue_statistics` row (public), as session 374's report said the merge should; the release package counts 42 held for a license and main's two held for storage; `docs/licenses.md` written again by its script (`licenses.py check` 0, `release_v1.py --check` 0).
2. **Landed with five browser checks failing**, had the database let the build pass: each failed on reads that timed out, the same reads fail on production, and the branch changes nothing those pages read (the list is in session 381's report).
3. **`check-findings-grids` left failing**: it waits for the small multiples as the card's first view, which they no longer are; it fails on production the same way.
4. **`test_session166` made independent of the day's holds** rather than rewritten for 21 October's.
5. **One landing for 367 to 372, 381 and 382**, as the chains of 20 October landed in combined pushes.
6. **015 taken before the landing** (the queue step below), so that the machine does not idle while the database is slow; its sessions run as the database allows.

## Waiting for you

1. **The database** (above): whether Supabase's plan or the day's loads need a change.
2. **Session 381's eight**: the five signatures; Research's `.py` downloads that do not run for a reader; links from `/research` and `/grid` to their replications; a decisions block on `/research`; "Checked against" lines on `/grid` and `/research`; whether a row against your thesis counts as a published figure; question 5's answer on the Grid page and `eia_annual_crosscheck_ba` in the live set; whether Research's form is "final".
3. **Session 382's**: the first figure two and a half screens down on a phone (seller and battery pages); one cent between the generator's headline and its spans table at a hub other than the main one; who walks the On.Energy and the traders' paths, and how a reader outside the project sees pages in review.
4. **For the data machine**: the board's ERCOT tiles stop on 15 October (day-ahead) while its week table holds 20 October; NYISO's and ISO-NE's prices leave the board at its next build (the hold); `iso_queue_statistics` rebuilt (the day note's item 2).
5. **The chain worker** (the owner's first job of 20 October's evening prompt): `scripts/chain_worker.ps1` was not written. Claude Code's auto mode refused the file as a script that starts unattended Claude Code sessions with no permission prompt; it is the owner's to write, or to allow.

## To finish (on this machine, outside 14:00 to 16:15 UTC)

```bash
cd C:/Users/lossa/Documents/erw
# 0. wait until Supabase answers the heavier reads again (an ordered read of series in a few seconds)
# 1. the landing checks of the combined branch (the suite in the clean copy, the build, check-values, check-routes)
git fetch origin && git checkout --detach origin/wip/381-382-land
bash runs/chain_oct20d/land_checks.sh s383land 3383 check-queues.mjs check-map-v2.mjs check-table-downloads.mjs check-battery-scenarios.mjs check-datacenter.mjs check-datacenter-scenarios.mjs check-datacenter-face.mjs check-battery-face.mjs check-csp.mjs check-security.mjs
git switch main
# 2. the landing
.venv/Scripts/python.exe scripts/freeze.py status
git ls-remote --heads origin "task/*"
#    in ../erw-land381: git merge origin/main
node site/scripts/snapshot-live.mjs take s383-before            # its own command
#    in ../erw-land381: git push origin HEAD:refs/heads/task/381-382
bash runs/chain_oct20d/land_wait.sh s383wait <sha> task/381-382 s383-before s383-after
# 3. after the deploy: the download check against production
cd site && node scripts/check-download.mjs https://erw-flame.vercel.app; echo "exit=$?"
# 4. delete the merged remote branches: wip/348-map, wip/367-map-land, wip/368-download-keyset, wip/369-grid-day-event-dates,
#    wip/370-check-faults, wip/371-docs-security, wip/367-372-day, wip/381-five-tools, wip/382-trader-path, wip/381-382-land, task/367-372
```

## The queue for this machine

`python scripts/chain_queue.py list` before the queue step: 1 waiting for samueloldlaptop, `015-day-20-october-code-pm.md` (`machine: code`, sessions 401 to 415). The queue step takes it; it runs next, and its own last session writes the file after it.
