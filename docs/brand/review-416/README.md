# Session 416: the four faults of 015's landing, before and after

Before: production (https://erw-flame.vercel.app, the internal view), 21 October 2026 at about 14:15 UTC. After: the
local build of `wip/416-417-charts` (21 October at about 14:45 UTC, the database gate open at 2.69 s). 1280 x 900 and 390 x 844 (the second with mobile emulation), each
the part named scrolled to the top of the window, the viewport as it is (no clip). Taken with
`runs/chain_021/s416/shots.mjs` (not in git) from `runs/chain_021/s416/list.json`.

| Shot | Address | What to look at |
|---|---|---|
| `explorer-box_*` | `/explore/ercot-peak-premium` | the box chart's price axis: a tick at zero reads "0" (the "-0" the finisher saw comes from bounds whose lower end rounds to minus zero; the default view's bounds do not show it, the test runs the case) |
| `emissions-monthly_*` | `/grid?view=clean` (`/emissions` redirects there) | "Monthly since 2018": before, the axis read 08-01 to 09-01 over eight years; after, months (2018-07 ...) |
| `data-coverage_*` | `/data` | the coverage table scrolled to the top: before at 390, session 410's band came from its script's clip, not the page; this script shows no band either way |
| `data-refreshed_*` | `/data` | at 390 the table scrolled sideways to "Refreshed (UTC)": before, the head's first cell ("Table") stayed while the body's first column moved; after, the table's name is the row's header and stays beside it |

`runs/chain_021/s416/probe-data-390.mjs` (not in git) settled the /data fault on production: the head's "Table" cell
at 16 px while its column's first cell was at -599 px after the sideways scroll; the clipped capture showed a band of
the scroll's height (351 px), the plain one none.
