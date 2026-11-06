# Session 1494 report: the explorers, live: what holds already, read on a build

Energy Research Warehouse (ERW), session 1494, chain 158, samueloldlaptop, 6 November 2026, 09:20 to 09:30 UTC (during session 1493's landing). Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; web requests to the ERW's own database (the gate's build's reads) only. Branch `wip/1494-explorers` (sessions 1494 to 1496), cut from session 1493's landing commit.

## What it found, explorer by explorer (read on session 1493's gate build of `d4a5fe42`, port 3493, the internal view)

| Asked of each explorer | ERCOT peak premium | Demand growth | Interconnection |
|---|---|---|---|
| reads the live set, not a frozen file | yes: `lib/supabase`'s `rest` on request, `ercot_peak_premium_annual` and `_monthly` | yes: `eia930_demand_growth` | yes: `iso_queue_statistics` |
| its refresh date shown | yes: `Freshness` (each table's last computation and newest period, from the catalogue) and the newest 15-minute interval from the tables' header | yes: the catalogue line and the partial year's last month | yes: the catalogue line and the table's build time and the queue's retrieval day from its header |
| figures keyed and traced by `check-values` | 64 keyed figures on the default view; four views on the floors | 63; five views on the floors | 218; on the floors |
| the thesis's figure as the default view | **yes, to the cent**: HB_HUBAVG 2015 against 2025, all-hours median 20.49 and 25.68, 99.9th percentile 583.96 and 311.80, peak interquartile range 7.64 and 34.12, midday minimum -3.98 and -18.25, each the page's keyed figure and the method note's thesis table (`docs/methods/ercot_peak_premium.md`) | no thesis chart is named in the ERW's documents (`docs/methods/demand_growth.md`, 21 October 2026): the default is the table's own headline figure for every grid | no thesis figure is held: the default is CAISO in positions |

- The gate's `check-values` on that build: 7,793 of 7,793 values match, the explorers' floors met.

## Decisions made without you

- Nothing to change: chain 086's sessions 2200 to 2202 and sessions 403 to 405 had already made the three explorers read the live set with their dates and keys; this session recorded it with the figures.

## For Samuel's ruling

- None.
