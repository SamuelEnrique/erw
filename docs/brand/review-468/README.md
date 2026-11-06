# Session 468: the datacenter tracker by grid

Before: production at 1280 and 390 px, 21 October 2026 at about 09:37 UTC (`before/`), at `/datacenters?view=grids`. Production has no such view yet, so these show the facilities page as a visitor to that address sees it today.

After: not taken. The database gate was closed (`scripts/db_probe.py`, 3.32 s against 3 s, at 09:27 and 09:38 UTC), so no local build ran. The commands are in `archive/sessions/SESSION_468_REPORT.md`, "To finish": the shots go to `after/`.

What to look at, after: the two tabs under the title ("Facilities", "By grid"); the table by grid and zone (ERCOT, zone not stated by the queue, 2 sites, 191.26 MW asked, beside ERCOT's active queue); the chart of each complete year at the cheapest zone, LZ_NORTH and the dearest zone, and its figures in the fold; the downloads line.

## After (session 461)

Taken by session 461 on 21 October 2026, about 12:30 UTC, from the local build of `wip/461-combined` (every branch of
chain 019 merged onto main, the internal view) at 1280 and 390 px, into `after/`. The build read the live set while it
was slow (the probe at 2.92 s against 3 s); the shots show these pages as the build drew them.
