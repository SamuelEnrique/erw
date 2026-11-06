# Session 1467 report: fault 46, and the landing of sessions 1458 to 1467

Energy Research Warehouse (ERW), session 1467, chain 150, samueloldlaptop, 6 November 2026, 05:14 to 06:25 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; web requests to GitHub, the ERW's own database (the gate's reads) and production (the snapshots, the deploy mark) only. Branch `wip/1467-periodicals`, cut from `wip/1466-periodicals`, `origin/main` merged.

## First: the landing

**Sessions 1458 to 1467 merged into main at 06:18 UTC** (`2a56797cf`, "Merge task/1467-periodicals: checks passed (run 42172191531)"); production served it at 06:20 UTC (the mark: `/data/methods/periodicals` holds session 1458's `new_things`, read in the internal view); snapshot pair `s1467-before` (06:04:37 UTC) and `s1467-after` (06:20:48 UTC): **0 differences on the 25 live pages** (expected: every page is in review). Branches `wip/1458-periodicals` to `wip/1467-periodicals` deleted on origin once ancestors of main (`task/1467-periodicals` was gone already, the workflow's); their ten worktrees removed; `erw-land-5aa739c9`, the gate's kept worktree, unregistered with its folder left on disk ("Filename too long", in its `node_modules`).

## The fault

Row 46 of `docs/reviews/periodicals-faults-2026-11-05.md` (session 1463's dry run of 6 November):

- Faulted: "- APS expects peak demand to grow about 3.4% annually and plans coal use to 2038 (generation): [Utility Dive](...)"
- Written instead: "- APS expects peak demand to grow about 3.4% annually and plans coal use to 2038 (generation). [Utility Dive](...)"

## What it did, with commits

- `c6974d9f9`: `brief.sector_line(r, head)` writes the by-sector and AI and power lines, with a colon only before a why line; the email's `items()` and `scripts/periodicals_counts.py`'s `BULLET` read both forms. Tests: `Session1467SectorLine`.
- The gate's first run on the combined stack failed three tests that read `brief.main`'s source for the old line form (`test_session577`, `test_session801`, `test_session807`); they read `sector_line` now (the commit after `c6974d9f9`), and the second run is the one above.
- Sessions 1465 and 1466's reports' clock times corrected; row 46 fixed in the faults file.

## Checks

| Check | Exit | Result |
|---|---|---|
| `land_check.py --ref wip/1467-periodicals --port 3467 --keep-worktree`, run 1 (`61572f766`) | 1 | suite: 7,695 tests, 3 failures (the source-reading tests above) |
| run 2 (`5aa739c9c`): freeze, main merged, task branches, db probe, build lock, worktree | 0 | none in flight (task/198-battery-data left over) |
| suite (clean worktree) | 0 | Ran 7,695 tests in 632 s; OK (skipped=327) |
| ask replay, npm ci, build (82 s), serve | 0 | |
| check_values | 1 | 7,742 of 7,742 values match Supabase; 2 floors FAILED, `/deals` and know-your-grid (main's, as at sessions 1434, 1456, 1464) |
| `check-csp.mjs` (by hand, the gate's build on port 3467) | 0 | 97 pages, 0 violations |
| `check-cross-checks.mjs` (by hand) | 0 | 92 passed |
| `check-routes.mjs` (by hand) | 0 | 225 pages in review, 0 failed |
| push of `task/1467-periodicals`, only after `merge-base --is-ancestor origin/main` | 0 | GitHub's `code-branch.yml` run 42172191531 passed and merged |
| `snapshot-live.mjs take s1467-before`, `take s1467-after`, `compare` | 0, 0, 0 | 0 differences |

## Decisions made without you

- One landing for sessions 1464 and 1467 (session 1464's report).
- The gate's check-values failures on `/deals` and know-your-grid were read as main's (they fail on production too, as at sessions 1434 and 1456). The three checks the gate skips after them (check-routes, check-cross-checks, check-csp) were run by hand against the gate's own kept build before the push.

## For Samuel's ruling

- None beyond session 1464's (the two floors).
