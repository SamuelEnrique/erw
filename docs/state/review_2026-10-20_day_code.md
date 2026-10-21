# The chain of 20 October 2026, day, on the code machine: the note for Samuel

Energy Research Warehouse (ERW), session 372, 20 October 2026. The chain `queue/done/012-day-20-october-code.md` (sessions 365 to 372) ran on samueloldlaptop, unattended, from 18:04 UTC: one orchestrating session landed and merged, and one agent a session built 365, 368, 369, 370 and 371 in their own worktrees. Every page is in review: open `https://erw-flame.vercel.app/internal/open` first. Each session's report is `archive/sessions/SESSION_<n>_REPORT.md`. Model spend USD 0. No pull from any publisher; no warehouse data written (three tables were read from the ERW's own archive into `runs/`, for the release package's rows).

## First: what stopped the chain

1. **Claude Code stopped the landing checks of 367 and 369 at 19:44 UTC for low memory** (the laptop's memory reaper; session 370's agent, waiting for the build mutex, was stopped with it). The whole suite had finished (two failures, both fixed since); the build was cut off at "Running TypeScript". The harness asks that a stopped job is not started again unattended, so **sessions 367 to 371 are built, tested and merged into one branch, `wip/367-372-day`, and not landed**. "To finish" below is every command, in order. You can let a chain restart such jobs by starting Claude Code with `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1` (your choice, never a session's).
2. **`iso_queue_statistics` (the third machine's session 348) is wrong in Supabase and in the archive.** It read the six queue tables with `comment="#"`, which cuts a row at a "#" inside a cell: on this machine's copies the read loses the queue date of 450 ERCOT rows (the method's "456 positions with no queue date" is mostly this), 169 CAISO, 104 NYISO, 30 MISO, 16 SPP and 94 ISO-NE. Session 367 fixed the code (`warehouse/derived/queue_statistics.py`, on the branch) and wrote the fault into the method note; **the table needs the data machine's rebuild** after the landing. The map's Queues tab draws it, in review.
3. **The queue step was not run** (it would start a new chain of builds right after the memory stop). `queue/next/014-night-20-october-code.md` waits for this machine (sessions 381 to 383; its first session lands this branch if it is not on main). Run `python scripts/chain_queue.py next` to continue.

## What each session did

| Session | State | Address to open |
|---|---|---|
| 365, the queue knows which machine a file is for | **landed** (`e468065a`, 19:10 UTC, with 366) | `queue/README.md`; `python scripts/chain_queue.py list` |
| 366, `wip/345-impact` (`/impact`) through the gate | **landed** (`e468065a`) | `https://erw-flame.vercel.app/impact` |
| 367, `wip/348-map` (the Queues tab) through the gate | on `wip/367-372-day`, not landed | `https://erw-flame.vercel.app/map?tab=queues` |
| 368, `/api/download` pages by key | on `wip/367-372-day`, not landed | `https://erw-flame.vercel.app/data` (any large table's CSV, e.g. `ercot_as_prices`) |
| 369, know-your-grid's day and check-values' event dates | on `wip/367-372-day`, not landed | `https://erw-flame.vercel.app/learn/problems/know-your-grid` |
| 370, the checks that fail on production | on `wip/367-372-day`, not landed; its local build cycle not run | `https://erw-flame.vercel.app/research/card/batteries_lunch` (the right-hand names) |
| 371, the documents and the security review | on `wip/367-372-day`, not landed | `docs/security.md`, `CLAUDE.md` |
| 372, this note | on `wip/367-372-day` | this file |

What each built, in a line:

- **365**: `machine: code` or `data` in a prompt file's first ten lines; `next` takes only this machine's files (or files with no line) and names the others; `next --file <name>`; `list` shows each file's machine; the planner marks its drafts. Without it this machine's queue step would have taken the data machine's chain.
- **366**: `/impact` (tool 17, phase one) on main in review under Economics, its two tables in coverage, sources and the release package; 340 of 340 checked numbers matched. The snapshot comparison: 25 differences, one a page, each the menu's new "Economic impact in review" (expected).
- **367**: the map's third tab, Queues, with its own table in the downloads line; positions placed by a place; the daily rebuild step `dm_project_map`; the comment-hash fault fixed in code (above).
- **368**: keyset paging on each shape's primary key, no count query: all ten large tables download whole on the local build (the old route: 3 of 10); the bytes identical on nine tables compared; the limit raised from 200,000 to 500,000 rows (`/data` says so); a count line only under 50,000 rows.
- **369**: know-your-grid uses the newest day both tables hold in full (18 October: ERCOT 40.48 percent from gas, CAISO 45.71) and names it; every event-page key names its date and is compared with that date's row only. check-values passed in full on its build, 6,639 of 6,639.
- **370**: `check-battery-scenarios`' CAISO case was the check's fault (the steps file is behind session 322's filled days; the page correctly offers only the model's step); `check-datacenter`'s 22 failures all described the page before sessions 190 to 317 (45 of 45 now on production); long chart names wrap inside the drawing (`site/lib/chartwrap.ts`).
- **371**: `docs/security.md` (28 items: 18 closed, eight open for you, three noted); the internal cookie compared in constant time; five internal addresses open with the cookie instead of `?token=` (a landing's check no longer puts the token in a production address); todo 007's documents, and its `CLAUDE.md` change (the owner's prompt named it; applied by the orchestrator).

## The screenshot folders

- `docs/brand/review-347/` and `review-349/` (the third machine's, for 366 and 367); `review-368/` (`/data`'s sentence); `review-369/` (know-your-grid); `review-370/before/` (the cards; the after shots come with "To finish" step 1); `review-371/` (16 shots).

## Decisions made without you

1. **The release package spliced here** for `impact_tax_rules`, `nlr_jedi_multipliers` (in v1) and `iso_queue_statistics` (held), from `release_v1.py`'s own `build()` on the tables as the archive holds them; the counts follow (137 tables, 42 held). The data machine's session 375 rewrites the package in full anyway.
2. **The floors of the new pages wait for a run that passes in full** (`FLOOR=1` in "To finish" step 2).
3. **The Queues tab offers its own table** in the downloads line; the method note keeps both merged sections.
4. **Menu pins follow `/impact`** (`test_session203`, `test_session237`); **`test_session330` follows the Queues tab's line**.
5. **368**: the 500,000-row limit, the count line under 50,000 rows, `maxDuration = 300`.
6. **369**: "in full" is the page's rule (24 hours) applied to both tables and each variable; a cached page is not failed when a newer day arrives.
7. **370**: the check follows the page where the page was right; retired assertions listed one a line in its report.
8. **371**: the cookie in constant time; the internal addresses by cookie, `?token=` still accepted.
9. **The queue step not run after the memory stop** (above); 014 written so that the machine has work.

## Waiting for you

1. **Run "To finish"** (or start Claude Code with the reaper off and ask a session to).
2. **The eight open security items** in `docs/security.md` (H1 with L5: the old link's retirement, then the token's rotation; M6 default privileges; M7 the Python packages; L4 the cookie's lifetime; L7 `search_path` on the lock and scheduler functions; L8 Supabase Auth sign-ups still on; L9 the linter's packages), each with its choice; S3 is noted (three internal checks send the real token in an address: run them on a local build only); and confirm `SUPABASE_SERVICE_KEY` is set on Vercel now that migration 034 is applied (H3, closed in code).
3. **368**: the empty `ba` and `event` columns of every download (a one-line patch waits, `runs/chain_oct20d/s368/route_ba_event.patch`: `event_window_daily`'s rows cannot tell their events apart without it); the 500,000-row limit.
4. **For the data machine**: rebuild `iso_queue_statistics` after the landing (above); rebuild `site/data/battery_scenario_steps.json` on tables holding session 322's filled CAISO days (session 370).
5. **The impact pack's ten questions** (`docs/reviews/packs/impact.md`) and the third machine's two (its note).

## To finish (in order, on this machine, outside 14:00 to 16:15 and 22:30 to 23:45 UTC)

```bash
cd C:/Users/lossa/Documents/erw
# 1. session 370's own cycle (its build, every check it names, the after shots), under the build mutex
mkdir runs/build.lock && echo "370 cycle $(date -u +%H:%M)" > runs/build.lock/owner.txt
bash runs/chain_oct20d/s370/cycle.sh; echo "exit=$?"          # read runs/chain_oct20d/s370/result.txt; stop port 3370
rm runs/build.lock/owner.txt && rmdir runs/build.lock
#    then in ../erw-370: git add docs/brand/review-370/after && git commit, and merge wip/370-check-faults into wip/367-372-day
# 2. the landing checks of the whole branch, with the floors
git fetch origin && git checkout --detach origin/wip/367-372-day
FLOOR=1 bash runs/chain_oct20d/land_checks.sh s372land 3372 check-queues.mjs check-map-v2.mjs check-table-downloads.mjs check-battery-scenarios.mjs check-datacenter.mjs check-datacenter-scenarios.mjs check-datacenter-face.mjs check-battery-face.mjs check-csp.mjs check-security.mjs
#    read runs/chain_oct20d/s372land/result.txt; commit site/scripts/check-values-floor.json onto the branch (in ../erw-372L) if written
git switch main
# 3. the landing
.venv/Scripts/python.exe scripts/freeze.py status
git ls-remote --heads origin "task/*"                         # trial-merge any branch in flight first
#    in ../erw-372L: git merge origin/main
node site/scripts/snapshot-live.mjs take s372-before           # its own command
#    in ../erw-372L: git push origin HEAD:refs/heads/task/367-372
bash runs/chain_oct20d/land_wait.sh s372wait <sha> task/367-372 s372-before s372-after
# 4. after the deploy: the download check against production (10 of 60 downloads an hour, about 5 minutes)
cd site && node scripts/check-download.mjs https://erw-flame.vercel.app; echo "exit=$?"
# 5. delete the merged remote branches: wip/348-map, wip/367-map-land, wip/368-download-keyset, wip/369-grid-day-event-dates,
#    wip/370-check-faults, wip/371-docs-security, wip/367-372-day
```

## The queue for this machine

`queue/next/014-night-20-october-code.md` (`machine: code`, sessions 381 to 383), committed and pushed to main with this note's push: 381 lands `wip/367-372-day` if it is not on main, then roadmap item 2's replication and cross-check tables for the five tools; 382 roadmap item 8's trader path written click by click; 383 its note and the queue step. The data machine's own chain (011, sessions 373 to 380) is running on lab-desktop.
