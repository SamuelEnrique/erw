# Session 367 report: wip/348-map landed through the full gate

20 October 2026, from about 18:25 UTC, unattended, on samueloldlaptop (the code machine), the third session of the chain of 20 October, day (`queue/done/012-day-20-october-code.md`). Run by the chain's orchestrator itself, in the worktree `erw-367` on `wip/367-map-land`, made from the third machine's `wip/348-map` (sessions 348 to 350). Lands on main together with session 369 as `task/367-369`. Model spend USD 0. No pull from any publisher; no warehouse data written (the new table was read from the ERW's own archive into `runs/`, for the release package's row only).

## Read these first

- **The map's Queues tab is on main, in review**: `iso_queue_statistics` (the six ISO queues by entry year, 1,511 rows, loaded by the third machine with its `sources.csv` row `erw:iso_queue_statistics`), positions placed by a city or a town, the card's generator link, and the daily rebuild step `dm_project_map` for the data machine. The third machine's night note, `docs/state/review_2026-10-20_third.md`, comes to main with it.
- **Two conflicts with main, both resolved by keeping both sides**: `docs/methods/energy_projects.md` (session 330's "The page as it stands" and session 348's "Queue statistics"; the first now says the map has a third tab) and `site/app/map/page.tsx` (session 330's downloads line under the map, session 349's Queues tab): **the Queues tab's downloads line offers its own table**, `iso_queue_statistics`, where the other two tabs offer the map file's four tables. The table is held for review in the live set, so the line says it is not in the site's live set and names Redivis, as session 333's rule has it.
- **The release package**: `iso_queue_statistics` spliced in as held (`in_v1 = no`: license needed from 21 October for ISO-NE, MISO and NYISO; held whole), the counts 41 to 42 held; as session 366 did for its two tables.
- **The check-values floors** of the four `/impact` addresses and the three `/map?tab=queues` addresses are written at this landing, from a run that passed in full (session 369's fix of `/learn/problems/know-your-grid` lands with it): see "Landing".

## What to review

- `https://erw-flame.vercel.app/map?tab=queues` (open `https://erw-flame.vercel.app/internal/open` first), and the downloads line at its foot.
- `https://erw-flame.vercel.app/map` (positions placed by a place; a unit's card and its generator link).
- The third machine's shots, `docs/brand/review-349/` (the code is theirs; the one change here is the Queues tab's downloads line).

## Checks

| Check | Exit | Result |
|---|---|---|
| Impeccable `detect --json` on `site/app/map/page.tsx`, `QueuesView.tsx`, `QueueCharts.tsx`, `ProjectMap.tsx`, `site/lib/projectmap.ts` | 0 | `[]`, clean |
| `test_session203`, `237`, `239`, `275`, `345` to `349`, `369` after the merges | 1, then 0 | 107 tests; `test_session275` failed (the package did not list `iso_queue_statistics`) until the splice |
| The landing's checks (`runs/chain_oct20d/land_checks.sh s367land`) | see Landing | |

## Landing

(written at the landing)

## Decisions made without you

1. **The Queues tab offers its own table** in the downloads line (above).
2. **The method note keeps both sections**; "Two tabs" now names the third.
3. **The release package spliced here** for `iso_queue_statistics` (held), as in session 366; the data machine's next full `release_v1.py` run rewrites the package from its own tables.

## For Samuel's ruling

- Nothing new from this session. The third machine's two questions stand (its note, "What waits for Samuel", items 2 and 3: whether the resources tool should count a position placed by a place; ERCOT's withdrawn positions from its past GIS reports, a pull).

## Files

- `docs/methods/energy_projects.md`, `site/app/map/page.tsx` (the merge), `docs/redivis/release-v1/tables.csv`, `README.md`, `docs/redivis/release-v1.md`, `docs/redivis/release-v1-runbook.md`; this report. Everything else is the third machine's sessions 348 to 350 as they stood on `wip/348-map` (`61acb4f2`).
