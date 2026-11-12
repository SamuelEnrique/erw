# Session 1854: the datacenter tracker, read as a reader (chain 213, 12 November 2026)

Energy Research Warehouse (ERW). Chain 213, session 1854, samueloldlaptop, unattended, Fable 5.1. About 12:05 to 12:50 UTC. Long end 1:30. Precheck passed.

## What it did

- Served session 1850's build of origin/main (`37cbea47b`) on port 3854 (no new build: the harness stopped 1852's for memory and asks that it not be restarted unattended; the tracker's pages are on main unchanged) and read `/datacenters`, `/datacenters?view=grids` and the map's datacenter layer at 1280 and 390 with the internal cookie: screenshots, the HTML, every table, key, hover and status line (`runs/s1854/read-dc.mjs`, `findings.json`, 6 screenshots).
- The facilities table is held whole, so the facilities list, the rollups, the timeline and the charts are not drawn; the by-grid view draws placeholders. The rollups, timeline, grid loads and chart figures were recomputed with `lib/dcrollups.ts` in Node on the live set's 428 rows (`recompute-dc.mjs`, `recompute.json`), and ERCOT's rollup by hand in Python: 44 counted, 4 stating MW (50, 222, 73, 112), 457 MW, 40 stating none; the page's functions agree. The timeline has no row to recompute (the live rows lack the v2 field; nine hold the old `planned_year`).
- **The faults file written:** `docs/reviews/datacenter-faults-2026-11-11.md`, 14 rows: 5 open for session 1855 (the hold said as two bare words and a list of 25 publishers, "license needed% (summer 2027)" in ERCOT's reserve-margin cell, the by-year chart's figures drawn over each other, the map's sentence with the hold's words in its middle, the timeline reading only the new field name), 4 for the owner (the hold itself; the public peak and capacity columns hidden under the facilities' hold, item 28; the map serving a copy of the held table to every browser; the source hover missing from 309 of 316 `Num`s site-wide), 1 for the data machine (the live rows lack every v2 field), 4 not faults.
- Two rows of the deals faults file corrected: row 6 (the header band class is overridden by the brand's CSS on every page, so it was not a fault; the dead class was removed anyway) and row 19 (the comparables' cells carry their key, not a source hover).
- Server 3854 left running for 1855's check of the fixes against the same build (it is stopped by PID at the end of 1855).

## Decisions made without you

- The map layer was read at `/map?layer=datacenters` as "the map layer" of the tracker: the tracker's own words send the reader there, and what it showed (the held table's rows in every browser) is the read's largest finding after the hold itself; it is written as a ruling, not changed.
- The source hover is written as one site-wide ruling (row 11), not as a fault of this page: `Num` draws one only where a page passes it, and changing that touches every figure on the site.

## For Samuel's ruling

- Row 7: the map's copy of `datacenter_facilities` against the tracker's hold.
- Row 4: whether the public peak, capacity and reserve-margin columns show while the facility counts are held (item 28 of the state review; recommended yes).
- Row 11: the source hover on every figure, site-wide.
