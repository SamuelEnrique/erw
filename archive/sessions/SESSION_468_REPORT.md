# Session 468 report: the datacenter tracker, by grid

21 October 2026, about 09:30 to 09:45 UTC, unattended, on portable-laptop (the code role; the chain was written for samueloldlaptop), in the worktree `C:\Users\samen\Documents\erw-467` on `wip/467-468-datacenters`, after session 467 on the same branch. The chain of 21 to 22 October, night (`queue/done/019-night-21-october-code.md`, session 468). Model spend USD 0; no warehouse data written; no web request (one read of the ERW's own live set to try the figures). Not landed: the database gate stayed closed (`scripts/db_probe.py`, 3.32 s at 09:38 UTC against 3 s), so there was no build, no after shot and no check-values run.

## Read these first

- **`/datacenters?view=grids`, a second tab of the tracker** ("Facilities", the page's own address, and "By grid"; `site/lib/tabs.ts`, the shared tabs). It is in review as the page is; `site/lib/release.ts` is not touched.
- **One table by grid and zone** (`site/app/datacenters/GridsView.tsx`, grouped by `site/lib/datacenter/bygrid.ts`): the sites a public source names (the queue positions of session 467), the count of them that state MW and the MW they ask to connect, the grid's or the zone's active queue beside them, and the cheapest and dearest load zone's price for a flat load over the calculator's last twelve months. Read from the live set at 09:37 UTC: **ERCOT, zone not stated by the queue: 2 sites, 2 stating MW, 191.26 MW asked to connect, beside ERCOT's 1,169 active positions and 298,606 MW active**. No other grid has a site; ISO-NE's, MISO's and NYISO's queues are held and named, not read.
- **The MW by zone the chain asks for does not exist yet in public form.** No public-source site states its own load: the queue's MW is generation or storage asked, and ERCOT's queue states no zone. The table says both in words; it counts, it does not sum a load.
- **One chart, the price years**: for each grid with a site, each complete calendar year (the last eight held) and the calculator's last twelve months, at the cheapest load zone, the calculator's default (LZ_NORTH in ERCOT) and the dearest load zone, with every figure in a fold beneath (`dcpow|<grid>|<region>|year|<YYYY>`). Every year equals the calculator's own months for that region, checked for every zone of every grid.
- **The downloads line** offers the queue tables of the grids shown and the price tables the calculator's regions read, as the shared line does.

## What to review

- The branch: `https://github.com/SamuelEnrique/erw/tree/wip/467-468-datacenters`, commit `3832c201`.
- After the landing: `https://erw-flame.vercel.app/datacenters?view=grids`.
- The method note's new section: `docs/methods/datacenter_facilities.md`, "The tracker by grid (session 468)".

## Checks

Every gate redirected to a file under `runs/chain_019/s468/` (git ignores `runs/`), never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 468"` | 0 | 6 checks passed |
| `tests.test_session468`, `test_session467`, `test_session239`, `test_session349` | 0 | 47 tests OK: the grouping on rows written in the test (a site without a zone beside the whole grid's queue, one with a zone beside its zone, a blank MW counted as a position only); every complete year equal to the calculator's own for every zone of every grid; the tab, the page's two views, the keys in check-values and the view in check-routes; every key named in the note as `check-methods.mjs` reads it; no dash. The tabs tests of sessions 239 and 349 still pass with the seventh tabbed page |
| `tests.test_session468.TheGroups` with the zone rule broken | 1 | 1 failure, as it should |
| `tsc --noEmit` | 2 | only Next's generated `PageProps` and `LayoutProps` errors; none in a changed file |
| Build, check-values, check-methods with a site, snapshot, after shots | not run | the database gate was closed |
| Impeccable | not run | not installed on this laptop |

Shots before, from production at 1280 and 390: `docs/brand/review-468/before/` (production has no such view yet: they show the facilities page at that address).

## Decisions made without you

1. **The view is a tab of `/datacenters`** (`?view=grids`, the parameter `/demand` uses), so the facilities page keeps its address and gains a row of two tabs above its first block.
2. **A site whose queue names no zone is set beside the grid's whole queue**, in a row that says so; a zone is used only where the queue names one.
3. **The queue totals are the active positions** (the queue connector's harmonized status), counted and summed from the queue table itself, not from `iso_queue_statistics`, whose yearly rows leave out the positions with no queue date (456 in ERCOT).
4. **The chart is the price years, not MW**: no public-source site states its load, so a MW chart would draw the queue's generation asked as if it were load.
5. **The builder's pattern and grids moved to `site/lib/datacenter/bygrid.ts`** (pure), so check-values recomputes the groups with the page's own constants; `lib/data.ts` re-exports them and session 467's test reads them there.
6. **No floor for the new address in `check-values-floor.json`**: session 408's practice gives a floor from a passing run (`CHECK_VALUES_WRITE_FLOOR=1`); the address is read and noted until then.

## For Samuel's ruling

- Whether the view should compare against the queue's large-load requests rather than its generation requests where a grid publishes them (ERCOT's large-load queue is a picture in its status report; NYISO's load queue is held).
- The same question as session 467's: a public county list of ERCOT's load zones, to place a Texas site in a zone.

## To finish

On a machine with this branch, when `python scripts/db_probe.py` exits 0, under the build lock:

```bash
cd site && npm run build > ../runs/chain_019/s468/build.out 2>&1; echo "exit=$?"
npm start -- -p 3468 &
CHECK_VALUES_PAGES=/datacenters node scripts/check-values.mjs http://localhost:3468 > ../runs/chain_019/s468/values.out 2>&1; echo "exit=$?"
node scripts/check-methods.mjs http://localhost:3468 > ../runs/chain_019/s468/methods.out 2>&1; echo "exit=$?"
node scripts/check-routes.mjs http://localhost:3468 > ../runs/chain_019/s468/routes.out 2>&1; echo "exit=$?"
node scripts/shot.mjs "http://localhost:3468/datacenters?view=grids" ../docs/brand/review-468/after/datacenters_grids_1280.png 1280 900 "[data-view-grids]"
node scripts/shot.mjs "http://localhost:3468/datacenters?view=grids" ../docs/brand/review-468/after/datacenters_grids_390.png 390 844 "[data-view-grids]"
```

A passing check-values run may write the new address's floor (`CHECK_VALUES_WRITE_FLOOR=1`). Then the chain's combined landing, with the snapshot before and after.

## Files

- `site/app/datacenters/GridsView.tsx` and `site/lib/datacenter/bygrid.ts` (new); `site/app/datacenters/page.tsx`, `site/lib/data.ts`, `site/lib/datacenter.ts` (each year), `site/lib/tabs.ts`, `site/scripts/check-values.mjs`, `site/scripts/check-routes.mjs`.
- `docs/methods/datacenter_facilities.md` (a section added).
- `tests/test_session468.py` (new); `tests/test_session467.py` (reads the pattern where it moved).
- `docs/brand/review-468/before/` (two shots) and its README.
- This report.
