# The desktop's second window, chain 228: the landing desk (13 November 2026)

Energy Research Warehouse (ERW), sessions 4000 onward, for Samuel. Chain 228 (`queue/done/228-day-13-november-desktop-window2-landings.md`), lab-desktop's second Claude Code window, unattended from 09:25 UTC. Opus 5.5. Model spend: USD 0.

(Kept current as the chain goes; session 4049 finishes it.)

## Read these first

- **An 8 GB laptop can run the landing gate again** once `wip/w2-4000` lands.
  - numpy's OpenBLAS committed about 610 MB in every Python process, a buffer for each of the desktop's 20 threads. The suite now runs its maths on one thread.
  - Below 12 GB, `land_check.py` runs the suite in batches of 40 modules (`scripts/suite_batches.py`).
  - Whole suite batched: 8,648 tests OK; the heaviest process 652 MB.
- **The curtain's hole is closed on production** (row 18, `b1ea7427a`): `check-curtain.mjs` exit 0 after the deploy.
- **Every morning gate failed `/digest`'s floor by the clock**, because the page has no issue before 14:00 UTC. check-values now notes the floor in that case instead of failing it.

## Every landing, with its commit

| Row | Branch | Commit on main | Snapshots |
|---|---|---|---|
| old laptop 9 | `wip/1905-revert` | `3a82aebe4` | 0 differences |
| portable 16 | `wip/3701-sellable` | already landed at `5a2193a1e` (12 November) | none needed |
| portable 18 (urgent) | `wip/5100-security` | `b1ea7427a` | 0 differences; curtain exit 0 |
| portable 17, 19 to 22 | `wip/5000-grid` (P1's stack) | `5fe21d6de` | 0 differences |
| old laptop 10, in part | `wip/1973-periodicals` to `5f5aea071` | `5fe21d6de` | 0 differences |
| this window's own | `wip/w2-4000` (the 8 GB gate, the root causes, the `/digest` floor) | `5fe21d6de` | 0 differences |

## Rows that wait, and why

## The fallback's results

- **(a) The 8 GB gate:** above.
- **(b) Root causes:** every failed scheduled run of 30 October to 12 November is written in `queue/summary/`. Two are open:
  - the board's spark spread (window A's session 3873);
  - in part, the 8 November ledger refusal.
- **(c) Main green:**
  - the gates' suites passed on main merged: 8,633 tests at 09:34 and 8,640 at 10:19;
  - the `/digest` floor fixed;
  - test 1116 passes on main.

## Decisions made without you

## For Samuel's ruling (each with the default taken)
