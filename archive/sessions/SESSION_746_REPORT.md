# Session 746 report: the node's intraday swing

22 October 2026, from 18:33 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-746` on `wip/746-allgrids` (cut from `wip/745-allgrids`). Chain `queue/done/063-evening-22-october-code-allgrids-3.md`, session 746. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: the archive's copy of `node_basis_daily` on this machine, the live set with the anon key, a local build.

## Read these first

- **Each node's day-ahead intraday swing**: `node_basis_daily`'s `dam_spread_4h`, each day's four dearest hours' mean less its four cheapest. It was held and unused (session 733). The window is the same twelve months as the basis.
  - **In the node list**: a column, "Intraday swing", its mean, keyed `allgrids|nodeswing|<node>`; sortable, in the download too.
  - **In a node's panel**: one line, the mean, the 10th and 90th percentile and the days.
- **The widest**: APPLE_RN USD 108.21 per MWh (over 68 days held, so no twelve-month energy figure), PALACIOS_RN 105.86, JUNCTION_RN 93.14. The narrowest are wind and solar nodes in the far west.
  - A node with few days held has a swing over those days alone. The panel says how many, and the column's tip says "over the days the node holds".
- **No figure moved**: 105 new keys; check-values 2,814 of 2,814; the existing tab 0 differences from production.
- **The replication computes it** from the table (`--tables`): 92 figures, 80 beside the page, 0 differ.
- **Eight columns fit at 1280**: the list's widths were narrowed once more; no sideways scroll.
- Decision 24 in the method note.

## What to review

1. After the landing, `https://erw-flame.vercel.app/cost-of-power?view=allgrids&mw=1000&rows=nodes&nsort=swing&ndir=desc` (internal view): the swing column, widest first.
2. Click APPLE_RN: its panel's swing line, with its 68 days.
3. Shots: `docs/brand/review-746/`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `warehouse/derived/siting_page.py --in-dir-first ...` | 0 | nodes.json rewritten (364 KB), 873 nodes with a swing |
| `tests.test_session746`, `724`, `711`, `709`, `716`, `712` | 0 | OK |
| `db_probe.py` (the build only on its 0) | 0 | |
| `npm ci`, `npm run build` (lock `s746`, beat) | 0 | |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 2,814 of 2,814 |
| `check-existing-tab.mjs`, production against the build | 0 | every figure the same |
| the replication, `--tables`, against the build | 0 | 92 / 80 / 0 differ |

## The landing

Sessions 744 to 756 landed in one push at 19:06 UTC: see `SESSION_756_REPORT.md`, "The landing".

## Decisions made without you

1. **The swing's mean in the list, its spread in the panel**: one figure a column, as the list's other columns.
2. **A node with few days keeps its swing**, said so, rather than hidden: the figure is the table's, over the days it holds.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `warehouse/derived/siting_page.py` (`nodes_file`), `site/data/siting/nodes.json`, `site/lib/siting.ts` (`NodeRow.swing`, `NodeTableRow.swing`, `NODE_SORTS`, the key), `site/app/cost-of-power/AllGridsNodes.tsx`, `site/app/cost-of-power/AllGridsView.tsx` (the panel's line), `warehouse/replication/siting.py`, `site/scripts/check-values.mjs` and `check-values-floor.json` (one address), `docs/methods/siting.md` (decision 24).
- New: `tests/test_session746.py`, `docs/brand/review-746/`, this report.
