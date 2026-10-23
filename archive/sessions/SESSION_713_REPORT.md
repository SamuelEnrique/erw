# Session 713 report: the gaps, complete

22 October 2026, from 10:20 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-713` on `wip/713-allgrids` (cut from `wip/712-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 713. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **`docs/reviews/siting-gaps.md` is complete**: 28 rows, one a kind of cell the tab cannot fill, by grid. Each row gives what is not held, the source that would fill it, its license and the connector it resembles.
  - The licenses are as the source registry and `docs/licenses.md` record them, with no web request: EIA public domain (#1), ERCOT public (#2), CAISO with credit (#3), ISO-NE permission (#4), NYISO no license conferred (#5), SPP not within a commercial publication (#6), MISO written permission (#7), Berkeley Lab may be public (#14, not read: HTTP 403), PJM non-members may not republish (#15). The PUCT asks permission to copy its text (`rules.json`). The utilities' tariffs are not read.
  - Every connector named exists (the test checks).
- **`/internal/siting-gaps`** (internal view, a 404 for a visitor, as `/internal/holds`) draws the table.
  - It reads `site/data/siting/gaps.json`, which `siting_page.py` writes from the markdown, so it is read when the site is built.
  - Words only; no figure.

## What to review

1. After the landing, open `https://erw-flame.vercel.app/internal/open`, then `https://erw-flame.vercel.app/internal/siting-gaps`.
2. The table: 28 rows, each with its source, license and connector.
3. Screenshots: `docs/brand/review-713/` (taken on 715's build, which holds this session).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session713` (the site's copy is the table; every row whole; every connector real; the page internal), `703` | 0 | OK |
| built and checked on 715's branch: check-values on every `/cost-of-power` address, check-links on the new page | 0 | see 714's and 715's reports |

## The landing

Sessions 713 to 718 landed in one push at 13:01 UTC: see `SESSION_718_REPORT.md`, "The landing".

## Decisions made without you

1. **The page reads a JSON copy the builder writes**, not the markdown at run time: a deployed function holds no `docs/` file, and `scripts/build-content.mjs` is not this chain's.
2. **"Held" means held under terms**, said once above the table.

## For Samuel's ruling: the five gaps that would change the tab most

1. **The large-load tariffs outside ERCOT** (transmission, six grids). They would give CAISO and SPP an all-in figure, and every grid a delivery charge.
2. **The capacity prices, shown**: a permission from PJM, ISO-NE and NYISO, or MISO's terms reviewed. They would draw capacity and the all-in figure for four grids.
3. **ERCOT's settlement point mapping and resource registration**: each node's zone, hub, wires utility and county, so the node panel can name its place and its utility.
4. **Utility service territories**: now held by the data machine (`utility_service_territories`, chain 043), and wired in by session 718.
5. **A large load's own wait outside NYISO**: the utilities' and ISOs' large-load queues. Time to connect is a generator's today.

## Files

- New: `site/app/internal/siting-gaps/page.tsx`, `site/data/siting/gaps.json`, `tests/test_session713.py`, this report.
- Changed: `docs/reviews/siting-gaps.md` (complete), `warehouse/derived/siting_page.py` (`gaps.json`).
