# Session 7400 report: chain 303's ground, and the datacenter tracker's replication

Energy Research Warehouse (ERW). Chain 303 (`queue/done/303-night-16-november-portable-trackers-done-line.md`), portable-laptop (code role), 16 November 2026, about 09:10 to 09:30 UTC. Model spend: USD 0 (`ERW_SPEND_CAP_USD=0`; no script that calls a model was run).

## For Samuel's ruling (at the top because it is not this chain's to settle)

- **The repository is public, and it tracks the held tables' own files.** `warehouse/output/datacenter_facilities.csv`, `datacenter_projects.csv`, `datacenter_projects_evidence.csv`, `datacenter_operator_sites.csv`, `energy_deals.csv` and `energy_deals_evidence.csv` are in git (the `.gitignore` allowlist of sessions 15, 16 and 22, written before the hold of 21 October), and GitHub answers for the repository without a login. The site holds the same tables "license needed"; the evidence tables are outlet text the notes call internal. Found while deciding where the replication's rows may be kept. **Default taken: nothing changed.** No file was removed or rewritten (a removal from history is not a session's, and the daily run on the runner reads these files). The replication fetches its rows at run time into a folder git ignores and commits only figures (counts and sums).

## What was done

- **The ground.** Precheck passed; `git fetch`; 1.7 GB of memory free of 15.6 (so no build), 277 GB of disk; no freeze. Sessions 7400 to 7429 and queue numbers 330 to 339 checked free on origin/main, every branch and every queue file.
- **Worktrees.** Six landed worktrees removed (`erw-p2-row`, `erw-p3-5200`, `erw-p3-5250`, `erw-p3-5264`, `erw-p4`, `erw-p4-row`), their ignored `runs/` entries kept first in `runs/kept/<worktree>/` of the main checkout. The seventh landed one, `erw-p1-269`, was moved to `erw-c303` and reused (its `node_modules` saves an install). `erw-p2-5150` and `erw-p2-5157` are not landed and stay.
- **Resume files.** None of this machine's in `queue/next/` (310 is the data machine's, 321 the old laptop's). `queue/next/330-resume-chain-303.md` written, committed alone and pushed (`debaa965f`). The progress file `docs/state/progress_c303.md` started and pushed.
- **Rule 8.** The before snapshot of the live pages: `runs/snapshots/c303-before`, 25 pages, 0 failed, 09:15 UTC. The two pushes to main so far hold a queue file and a progress file, no site file.
- **The rows.** Read from the live set with the anon key, as session 1851 read them (`replication/datacenter_tracker/fetch_rows.py`): 458 rows of `datacenter_facilities` (vintage 15 November; 428 on 11 November), 38 of `ercot_large_load_status`, 2 queue sites (ERCOT's; the queues of NYISO, MISO and ISO-NE are held and not read), 1,159 active ERCOT positions. The rows now carry the v2 fields (`grid`, `grid_basis`, `mw_basis`, `power_kind`): faults row 8 is fixed in the data as far as those go; `energized_year` is still on no row.
- **The page's own functions on the rows.** The top block's arithmetic and the operator grouping moved, unchanged, from the components into `site/lib/dctop.ts`, so Node can run what the page runs (`site/scripts/datacenter-tracker-figures.mjs`). No figure and no word of the page changes.
- **The replication.** `replication/datacenter_tracker/replicate.py`, its own Python from the rules: the top block, the list's group lines, the sites beside ERCOT, ERCOT's 38 stated figures, the rollups by grid and by operator, the timeline, the three charts, the facilities against each grid, the queue sites, and what a flat load paid at ERCOT's eight load zones (last twelve months and by year). **454 of 454 inside the tolerance** (half the last shown digit). `page_figures.json` and `.csv` hold both sides.
- **One site fault found and fixed with a test (new faults row 15).** The rollups' list of US states left out Puerto Rico while the top block's list has it: a Puerto Rico facility would be counted at the top and missing from the rollups. No row is Puerto Rico's today, so no figure moves. `site/lib/dcrollups.ts` and `scripts/check_datacenters.py` take the 52.
- **Tests.** `tests/test_session7400_trackers.py`, 8 pass (made-up rows only). The nine test files that name a changed module: 60 pass. Type check of `app/datacenters/` and what it imports: 0 diagnostics. No full suite and no build (rule 6).

## Decisions made without you

- A landed worktree was reused, not removed: `erw-p1-269` is now `erw-c303`.
- The page's figure, for a held table, is what the page's own functions compute on the live set's rows; the replication compares with that. The built page draws none of the facility figures to anyone.
- `site/lib/dctop.ts` restates three small rules of `site/lib/largeload.ts` so Node runs it alone (as `dcrollups.ts` does); a test holds the two equal.
- `tests/test_session240.py` reads two of its asserted lines from the library file they moved to.

## Needs the key

- Nothing in this session.

## Commits

- main: `debaa965f` (the resume pointer), the progress file.
- `wip/7400-trackers`: `1e0eb26ba`.
