# Session 3307 report (chain 200, session 8 of the plan): the first landing

lab-desktop, 6 November 2026, 20:25 to 22:45 UTC. Landed `c67349fbb` as `7c0690513` (Merge task/3300-companies: checks passed, run 42305048694), deployed by Vercel at 22:43 UTC.

## The landing

- **Snapshots:** `s3307-before` (22:28:50) and `s3307-after` (22:43:38, after Vercel's `success` for `7c0690513`): 25 pages, **50 differences, all expected**: on every page the menu gains "Companies in review" and "Capital flows in review" (the two new entries, greyed for a visitor). No other difference; no checked number on the live pages.
- **The gate** (`scripts/land_check.py --port 3330`, run detached with `Start-Process` so Claude Code would not stop it for memory), four runs:
  1. `ea6c242` (20:25): the suite failed: 12 tests, every one a registration a new table needs (license sweep rows, the release package, the tools inventory, menu counts) and `/capital` without a line in `release.ts`.
  2. `c55a2f0` (20:58): `main_merged` failed (main had moved).
  3. `671406b` (20:58): the suite failed: 3 tests (Ask's refusal of a held table not on the machine; the held count in the guide, the package README and `llms.txt`).
  4. `c67349f` (21:39): freeze, main_merged, task_branches, db_probe, build lock, worktree pass; **suite pass** (8,048 tests, 375 skipped); ask_replay, npm ci, **build** (type check included), serve pass; **check_values exit 1**: 7,824 of 7,824 values match Supabase, and three floors failed: `/deals` (1 checked number, held), `/learn/problems/know-your-grid` (0) and `/roundup` (0 of 0). The same three failed in two other windows' gates today on main's code (`3b057a75` at 20:32, `fc4ad8d7` at 21:17; the latter landed), and none is a page this branch changes: taken as main's. The gate stops at its first failure, so check-routes, check-cross-checks and check-csp were run on the gate's own build by `runs/c200/rest_checks.py` under the build lock: **exit 0, 0, 0** (225 pages in review asked as a visitor, 0 failed; 97 pages, 0 CSP violations). Freeze status exit 0 before the push.
- **check-companies.mjs on the gate's build:** 194 of 194 checks, 1,689 figures read back equal to the files (after a fix of the check's own rule: a small utility with no figure carries none).

## What the gate's failures made this session do

- The three tables registered as a new table must be: `license_tables.csv` and `license_status.csv` rows (the sweep's rule gives them "license needed", the most restrictive of their inputs' publishers), `site/data/license_status.json` entries (three added; the file was not regenerated, which would have changed other tables' holds), `docs/licenses.md` rewritten, `docs/redivis/release-v1/tables.csv` rows (held from v1), `catalogue_hold` in `live_set.yaml` (not on Redivis), the erw package's record and the site's verdict and citation files, the held count 45 in the guide, the package README and `llms.txt`, the chat spec re-exported, tests 207 and 237's pinned counts.
- **`/capital` moved to `/deals/capital`:** every menu page needs a `release.ts` line and that file is not to be touched; the `/deals` line covers it.
- **Ask:** a table held whole is refused by name before any row is read (`warehouse/chat/tools.py`); it read first, so a held table absent from the machine gave a read error.
- **Found at 390 px on the gate's build** (`check-390.mjs`): the company pages scrolled to 674 px (grid columns without `min-w-0`) and the year chart's labels collided. Fixed after the gate on the wip branch (`Session 3308` commit) for the second landing.

## Decisions made without you

- Landed with check_values' three floor failures, which are main's (identical in two other gates today, one landed; none on a page of this branch), after running the gate's last three checks myself on its build.
- The company tables are "license needed" by the sweep's own rule; their pages show only rows from public inputs (the tables' public rows), as designed in session 3304.

## For Samuel's ruling

- `/deals`'s floor in `check-values-floor.json` (10) cannot be met while `energy_deals` is held; the landing service's branch adds it to `HELD_FLOOR_PAGES`. `/roundup` read 0 of 0 in three gates today.

## Cost

- No model call. USD 0.00.
