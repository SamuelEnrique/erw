# Session 8014 report (chain 581, lab-desktop, 20 November 2026, 02:04 UTC on)

Chain: `queue/done/581-evening-19-november-desktop-states-curtailment-map-layers.md`. Progress: `docs/state/progress_c581.md`. Model spend USD 0 (`ERW_SPEND_CAP_USD=0`; no script called a model).

## Unexpected differences

None. Every snapshot comparison: 0 differences on the 25 pages (all in review, read as a visitor).

## What a reader now sees

- `/states` (new, in review, in no menu): any state, the District of Columbia or the nation, or two side by side: net generation by source by year since 2001 and by month, each source's share of the last twelve months and of chosen years, sales, revenue and average price by sector with customers, capacity by source, the ten largest plants, what is planned to come and go, who operates the grid by share of people, EIA's state profile (net generation, sales, net interstate trade), CO2 from power since 1990, natural gas used and produced, SEDS total energy, the state's large-load law and severance tax where held. "Monthly, not hourly" said once with the Grid tool's link. A tour stop.
- `/curtailment/where-when` (new view; `/curtailment` unchanged): a month by hour grid for any place and year or every year held, coloured by CAISO's curtailed MWh or by a hub's share of hours below zero; the trend by year; the places ranked; two side by side. NYISO and ISO-NE prices named with "license needed", MISO paused, ERCOT's estimate not drawn.
- The old laptop's rows 57 (the tour's resource stop opens the Resources tab) and 58 (the fifth problem set of the whole country, the findings audit's last 29 drafts, request 561's tests).
- Waiting to land (gate 3): `/map`'s two line switches (transmission of 230 kV and above, EIA's HGL pipelines), four new board rows (aluminum, zinc, lead, tin), `/storage/places`, `/queues/places`. Waiting for gate 4: request 561's edition and row G1.

## Commits and landings

- `d33244fdf` resume file 582; `cd6bb28ba` progress file and the `/states` contract; `wip/c581-states` (`8213d16da` and on), `wip/c581-curtail`, `wip/c581-map`, `wip/c581-req561`.
- Gate 1 (`d41badf95`): failed test 5171 (`lib/states.ts` reads the disk and was not listed); fixed `df7320aae`.
- Gate 2 (`21d801d94`, B, C, rows 57, 58): every step passed; landed `4f7325f9f` (task/c581-curtail, GitHub run 44668262083), snapshots `c581-deskC-before` and `c581-deskC-after`, 0 differences.
- Docs push `ca57b20e2`: snapshots `c581-docs1-before`, `-after`, 0 differences.

## Tables

- `hifld_transmission_lines` (10,692 lines of 230 kV and above) and `eia_hgl_pipelines` (133): new, public, validated, archived (run 20261120T031518Z-local), registered (coverage, sources, license record, status, release v1 held out, live set not loaded, package, llms); Decision 82.

## Data requests

- 561 (the dated problem edition): built after row 58 landed; tests 293 and 7534 pass; replication 312 pass, 6 named, 0 differ; on `wip/c581-req561`.

## Decisions made without you

- `/states` reads revenue as EIA's sales times EIA's average price (the warehouse holds no state revenue column; the utilities' EIA-861M rows do not sum to the state totals).
- Connecticut's counties do not match between EIA-861 and the Census Bureau's estimates, so its shares by population are null with the reason.
- The curtailment view and the map layers write page files with no table of their own where their inputs are tables already held (as chain 505's price map did); the line layers are new sources, so they are tables.
- The map's line files are in columns (fields, rows, names, paths), not GeoJSON: GeoJSON's keys alone would fill the 2 MB limit for 10,692 lines.
- HIFLD's transmission lines take the HIFLD publisher's verdict already in the license record (read 2061, "None (Public Use)"); no new read was made for the layer.
- `/storage/places` and `/queues/places` are new addresses, not new tabs (test 239 pins the storage tabs).
- The stacked chart of generation misdraws where a source has no month (a shared component's limit); the page uses line charts instead and the shared chart is unchanged.
- A locked folder `C:\Users\Shared\Documents\erw-land-21d801d9` (gate 2's copy, unregistered from git) is left in place.

## For Samuel's ruling

- Where `/states`, `/curtailment/where-when`, `/storage/places` and `/queues/places` sit in the menu (default: in none).
- EIA's map layers of natural gas, crude oil and product pipelines, LNG terminals, refineries and gas storage: their host `services7.arcgis.com` answers 403 to its robots file; default not pulled. HIFLD's compressor stations and substations: in no public service the ERW reads; default not pulled.
- More Treasury maturities on the board (1-month to 20-year are in the Board's H.15 file already): test 207 pins the table's three; default not added.

## Needs the key

Nothing.
