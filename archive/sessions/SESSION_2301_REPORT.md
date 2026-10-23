# Session 2301 report: the hover on every mark and chart, both pages

23 October 2026, about 20:21 to 20:32 UTC, unattended, on portable-laptop (the code machine). Chain `queue/done/087-day-23-october-portable-map-tracker.md`, session 2301. Model Fable 5.1. Precheck 0. Model spend USD 0. No warehouse data written; no request but GitHub and the ERW's own database (the probe). Code in the worktree `C:\Users\samen\Documents\erw-2301` on `wip/2301-map-tracker`, stacked on `wip/2300-map-tracker` (session 2300 has not landed).

## Read these first

- **Every mark on the map has the brand's hover card.** The chart's tooltip (fog with a rule-colored edge, 12 px) now draws the name in sans, the figure in mono ("1,400.0 MW requested"), the grey line with the status, state, grid and date, and under it the source line: the table the row is read from (the operating or planned EIA table, `energy_projects` or `datacenter_facilities`), its vintage and the copy's build day. A state's hover says how many rows chosen it holds and what a click does. The words are a pure function (`hoverOf`, `stateHover` in `site/lib/projectmap.ts`) tested on one row of each kind without a browser.
- **The Queues tab's three charts** name, in each hover, the table and the entity (`iso_queue_statistics`, `ercot:queue_2019`) with the variable; their Table toggle held the same figures already.
- **The tracker's two bars** (MW by state, top operators) each have a hover card on the figure: the state or operator, the MW and the facilities counted in mono, then the rule and the source (`datacenter_facilities`, summed on the page, the check key). The figure is a button, so a keyboard reaches the card; a fold under the bars, "The bars' figures", holds the same figures as a table. Two source tips stand by the bars' headings.
- **The grids view's chart** (a flat load's price by year, per grid) has a hover per group naming the cheapest and dearest zones, the default zone and their figures, with the check keys; its fold held the table already. **The power side's** MW column has a source tip and each MW a hover naming its row's queue table, position and the day it was read. **ERCOT's large-load chart** is drawn by the shared chart now (one category a report), so each report has a hover with its three figures and the source, and the Chart | Table toggle holds them by keyboard; the plain line chart it replaced had no hover.
- **Not built, not landed.** The probe took 3.44 s at the end of the code (the gate needs under 3 s); free memory was 4.0 GB then. The gate's commands are under "To finish".

## What to review (on a build of `wip/2301-map-tracker`, in the internal view)

- `/map`: hover any mark (a dot, a ring, a triangle, a diamond) and a state; the card's last line is the source. `/map?tab=queues&iso=ercot`: hover a point of each chart.
- `/datacenters`: in the summary, hover or tab to a figure of "Stated MW by state" or "Top operators by MW"; open "The bars' figures" under them; in "ERCOT: large load approved and energized, over time", hover a report's column of "MW, by report" and press "Table"; on the power side, hover the "i" after "MW asked to connect" and a row's MW.
- `/datacenters?view=grids`: hover a year's group of the chart under each grid.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 2301"` | 0 | on duty |
| `node --import ./scripts/alias-register.mjs scripts/test-map-sources.mjs` | 0 | 43 of 43 (session 2300's 37, and the hover words of one row of each kind, a state's hover, the component's use of them) |
| `eslint app/map app/datacenters lib/projectmap.ts` | 0 | clean (one unused helper of the replaced line chart found and removed) |
| `tsc --noEmit`, this session's files | 0 errors | the 15 pre-existing errors of session 2300's report stand elsewhere |
| `scripts/db_probe.py` | 1 | 3.44 s for 1,000 rows: no build this session |
| free memory | | 4,015,672 KB at the end of the code |
| `scripts/db_probe.py`, again at the report | 0 | open 2.62 s 1000 rows of iso_dam_hub_prices (free memory then 3157788 KB) |
| `scripts/check-datacenters.mjs` (a served site) | not run | extended with four checks (each bar's hover card and its describedby id; the fold's table with as many rows as bars; the three source tips; the large-load chart framed with its source); runs under the gate |

## The landing

Not run: the probe said no build. The branch is pushed. Session 2302 stacks on `wip/2301-map-tracker` unless it has landed by then. `git ls-remote --heads origin 'task/*'` at 20:28 UTC: `task/198-battery-data` alone (the data machine's `task/2014-2027-data` merged at `32547dd5`).

## Files

- `site/lib/projectmap.ts`: `Hover`, `hoverOf`, `stateHover`.
- `site/app/map/ProjectMap.tsx` (the tooltip formatter, `perState`), `QueueCharts.tsx` (the `says` words).
- `site/app/datacenters/Body.tsx` (the bars' hover cards, the fold's tables, two tips), `PowerSide.tsx` (the MW column's tip and row hovers), `GridsView.tsx` (the groups' `title`), `LargeLoad.tsx` (`SeriesChart` in place of `LineChart`, framed with `data-source`).
- `site/scripts/check-datacenters.mjs` (four checks), `site/scripts/test-map-sources.mjs` (six checks).

## Decisions made without you

1. The map's marks are drawn on a canvas, so no mark is focusable: the keyboard's path to the same figures is the totals, "By technology" and the unit card (the card opens on a click), as the method note will say in session 2305. No shared component was changed for this.
2. The shared chart's hover (`SeriesChart`, the battery page's reference chart) is taken as the brand's hover card and not restyled; the Queues tab, the grids view and now the large-load chart use it. The tracker's bars are not a chart component but a list, so their card is the shared `Tip` pattern on the figure, with `font: inherit` inline so the figure keeps its mono face (the shared tip CSS sets sans on its trigger).
3. ERCOT's large-load chart moved from the plain `LineChart` (no hover) to the shared `SeriesChart`; the figures are the same rows of the site's copy of `ercot_large_load_status`, one category a report, the reports' days as labels. The legend of the old frame is the direct labels of the new chart.
4. The hover on the power side's MW is the browser's `title` and a tip on the column, not a card per cell: the cell already names its row's table in the hover and the Queue position cell links the report.
5. No build on a probe over 3 s, as the chain's rule says, although free memory had reached 4.0 GB by the end.

## For Samuel's ruling

- None from this session.

## To finish (the gate)

From the main checkout, each its own command, its exit read, on a probe under 3 s: `.venv\Scripts\python.exe scripts\land_check.py --ref wip/2301-map-tracker --lock-as s2301 --port 3301`, then the commands it prints (freeze status, the snapshot before, the push to `task/2301-map-tracker`, the snapshot after, `compare`). When 2302 to 2304 stack on this branch, the last branch's gate carries this work.
