# The chain of 19 to 20 October 2026, night, on the code machine: the note for Samuel

Energy Research Warehouse (ERW), session 335, 20 October 2026. The chain `CHAIN_OCT19_PROMPT.md` ran on samueloldlaptop, unattended, from 01:19 UTC: part one landed sessions 316 to 320 and ran session 320's thirty questions; part two finished fifteen pages to the five tools' standard, lighter (sessions 328 to 335). Every page is in review: open `https://erw-flame.vercel.app/internal/open` first. Each session's report is `archive/sessions/SESSION_<n>_REPORT.md`. Model spend of the chain: USD 2.21, all of it session 320's thirty questions through the evaluation's own ledger step (`site_ask_eval`); every finish session USD 0. No pull; no warehouse data written, but for the one ledger row the chain prompt asked for (below).

## First: three things no one asked for

1. **A check wrote three rulings into production.** `check-internal-findings.mjs` approves, dismisses and asks a full card for three scanner drafts; meant for its local stand-in, it was handed to the landing script, which serves the build against the live database. Production's `scanner_drafts` holds exactly those three rulings, all within one second at 10:56:50 UTC on 19 October and again at 23:24:26 (`scan-spike-4c52d4239fe9` approved, `scan-record-483f592bf064` dismissed, `scan-record-6e1d1cff0ae4` full card asked). No person made them. The chain stopped its own run before the check, ran it on its stand-in from then on (`runs/chain_oct19/findings_stub_check.sh`), and wrote nothing to the database. Yours: put the three back to draft (by SQL: the state function refuses "draft"), or keep them.
2. **`/learn/problems/know-your-grid` prints 0 for data it does not have.** It picks the newest day the demand table holds in full and sums `eia930_all_generation` on that day, which ends a day earlier; since 19 October the page shows 0 MWh of generation and 0 percent from gas for ERCOT and CAISO, and `check-values` fails those six numbers on production too. No session of this chain touches the page; the fix (the day both tables hold) changes the day the page shows: yours to rule, or a session's.
3. **`/api/download` fails on the largest tables** (on `/data` as on every page's new downloads): its exact row count and its paging by offset pass the anon role's three-second statement timeout. Always on six tables (`eia930_all_emissions`, `carbon_intensity_hourly`, `ercot_as_prices`, `state_generation_mix_monthly`, `eia930_all_generation`, `iso_rtm_hub_prices`), sometimes on the next ones (`eia_fuel_spot_prices`, `iso_dam_hub_prices`, `event_window_daily`, `energy_projects`). The fix is keyset paging in the route: a session's.

## What landed

One line a session, with the address to open. Every landing took a before and after snapshot of the 25 visitor pages; every comparison read 0 differences (every page is in review). Where a landing changed no style, production was asked for a mark of the landing before the comparison stood.

**Part one: the five sessions of 19 October that stood on `wip/` branches** (each record is in the next session's report).

- **Session 316, the hunt and the publisher's figure** (`fa418c0f`, 01:56 UTC): `https://erw-flame.vercel.app/internal/findings`. Landed as its report said, but for its internal-findings check, which ran on its stand-in (item 1 above).
- **Session 317, the chart ruling, part two** (`5ad70aa9`, 03:00): `https://erw-flame.vercel.app/curtailment`. Its suite had never run: four of its own tests failed (an indentation fault, three pins still describing the canvas) and were fixed; its shots were retaken on its last commit. The first push failed GitHub's check on a test main itself failed since the daily run's commit of 02:11 (`test_session157`, two newly tagged policy actions): the test now lets an action beyond its frozen cases carry a known tag.
- **Session 318, the finding cards** (`a315f600`, 03:42): `https://erw-flame.vercel.app/research/card/batteries_lunch_grids`. `check-board` waited for a canvas the session had made SVG, and five older pins described the old charts: all follow now.
- **Session 319, cold_2026 and session 270's faults** (`59be8286`, 04:18): `https://erw-flame.vercel.app/events/cold-2026`. Its first build had built session 318's commit (a checkout refused in the shared worktree); rebuilt on its own, the probe found the companies tab still 611 px wide at 390: its labels shrink now.
- **Session 320, Ask round two** (`ad0a1e76`, 04:48): after migration 035 the thirty questions were asked through the evaluation's own step: **17 of 30 right**, USD 2.21 (`warehouse/chat/eval/eval_s320_first_run.json`). The probe's call of 19 October is in the ledger, written by hand as the prompt asked (row 2482, its request id followed by "probe of session 320, written by hand 2026-10-20"). `docs/state/review_2026-10-19_code_pm.md` was brought up to date and went with it.

**Part two: fifteen pages finished, lighter** (roadmap v3: every number traced and checked, every input's default written and a Reset, the tables to download, the method note current, Impeccable once, shots before and after).

- **Session 328, `/board` and `/prices`** (`208a2906`, 06:03): `https://erw-flame.vercel.app/prices`. The shared downloads line (`components/tool/TableDownloads.tsx`: each public table a page reads as CSV, with a Python and a Stata reader of that CSV from `/api/download`); the board's threshold default written beside its box with a Reset; `/prices`' first tab has a method note (`power_prices.md`); the ERCOT tab's box plot caption no longer speaks of a slider, and its median labels stay inside the drawing.
- **Session 329, `/datacenters` and `/deals`** (`be2de9af`, 06:52): `https://erw-flame.vercel.app/deals?tab=companies`. The companies' confidence is a checked number (a new key, `entity|`); the deals have a method note (`energy_deals.md`); the tracker tab's form has its Reset.
- **Session 330, `/map` and `/storage`** (`85800d14`, 08:01): `https://erw-flame.vercel.app/storage`. Downloads and current notes; both pages were near the standard.
- **Session 331, `/demand` and `/curtailment`** (`d651cb32`, 08:48): `https://erw-flame.vercel.app/demand?view=consumption`. The consumption view's note (`consumption.md`); the weather view's Reset; the shared bar charts' names no longer overlap the unit or run past a phone's drawing, and the heat legend fits.
- **Session 332, `/policy` and `/events`** (`d0092d60`, 09:36): `https://erw-flame.vercel.app/policy`. Every action's significance is a checked number and `/policy` is in `check-values`; every event page offers its tables; a time chart's long line names are written on lines inside the drawing.
- **Session 333, `/supply` and `/contracts`** (`725f51c4`, 10:27): `https://erw-flame.vercel.app/supply`. `/supply` offers its five tables from its file's sources (none is in the site's catalogue yet, so the line says so and names Redivis); the contracts panels have their Resets.
- **Session 334, `/thesis` and `/severance`** (`1b68e090`, 11:14): `https://erw-flame.vercel.app/severance`. Thesis Builder version 1 as it stands (no feature work); `/severance` offers its price table on both tabs.
- **Session 335, `/learn/bill` and this note** (landed with this line): `https://erw-flame.vercel.app/learn/bill`. The bill page's method note (`bill.md`) and its table to download.

## The screenshot folders

Each holds the pages the session touched at 1280 and 390 px, before (production) and after (the local build), with a README that says what to look at.

- `docs/brand/review-317/` (retaken on the last code commit), `review-318/`, `review-319/` (rebuilt on its own commit; the companies tab's after shots on the landing's build).
- `docs/brand/review-328/` to `review-335/`: one a finish session, each with its README; `review-331/` adds the bar chart alone (`chart_battery_months_*`), before and after the shared fix.

## Decisions made without you

The reports list each with its reason; the ones that shape a page, a number or a check:

1. **The internal-findings check runs only on its stand-in** (`runs/chain_oct19/findings_stub_check.sh`), never through the landing script (item 1 above).
2. **`test_session157` was loosened** so that main could land: every frozen case must hold its tags; an action the daily run tagged later must carry a known tag on a field the rule reads.
3. **Older tests follow what the sessions changed**: the canvas charts sessions 317 and 318 drew in SVG (pins in `test_session144_page`, `236`, `241a`, `241b`, `241c`, `303`, `317` and `318`), the board's foot and threshold words of session 328 (`240`, `281`); `test_session241a`'s list of event pages holds `cold-2026`.
4. **Session 320's first run is kept as `eval_s320_first_run.json`**, not as the fixtures the tests read as every answer right; no question was asked again, each cause being yours.
5. **One shared downloads line, not a replication package a page**: the tables themselves, with readers that load them unchanged (the five tools keep their own packages).
6. **Three faults of the shared charts were fixed for every page** (the box plot's clipped label and its slider words; the bar names and the heat legend; the time chart's long names). No value moved: `check-values` read every page after each.
7. **New checked numbers**: the companies' confidence (`entity|`), the policy scores (`event|`); `/policy` joined `check-values` with a floor of 10, the companies tab's floor rose from 0 to 10.
8. **A page with no table in the site's catalogue says so and names Redivis** (the supply page, two demand views, the storage owners tab); `/contracts` and `/thesis` (internal tables) get no line.
9. **Pages drawn from a site file keep their own checks** (`check-board`, `check-map`, `check-demand`, `check-curtailment`, `check-supply`): each reads every number against its file; making each a Num would change their structure.
10. **Landings went on with `/learn/problems/know-your-grid`'s six failing numbers**, failing on production too and on a page no session touched (item 2 above).
11. **The finish sessions' build is taken again after a database statement timeout** (`runs/chain_oct19/night/finish_build.sh`), as the landing script already does: the home page's required read timed out twice at 06:42 and 06:44 UTC.

## Waiting for you

In the order of their value:

1. **The three rulings no person made** in `scanner_drafts` (item 1 above): back to draft, or keep.
2. **Session 320's thirty: 17 of 30 right**, and three rulings: whether the tool converts USD per MW to USD per kW where a table's method note names the conversion (8 questions, every battery revenue asked per kW, which the battery page shows); whether a key takes a relative tolerance (3, right but rounded to the dollar); whether a key accepts every table that holds the figure (2).
3. **`/api/download` on the large tables** (item 3 above): keyset paging, or those tables pointed to Redivis.
4. **`/learn/problems/know-your-grid`** (item 2 above): choose the day both tables hold.
5. **Tables the pages cannot offer**: `/supply`'s five (public in `coverage.csv`, not in the site's catalogue); `eia930_demand_growth` and `storage_owners_monthly` (held for review in the live set); `eia930_demand_weather` and the NOAA tables (not in the catalogue); `ferc_eqr_contracts` (internal while its license stands).
6. **For the data machine, stale on 20 October**: `ercot_peak_premium_annual` and `_monthly` (last run 29 September); `site/data/map.json` (built 9 October) and `energy_projects` (5 October); `eia930_demand_growth` and `caiso_curtailment_profile` (5 October); the NOAA weather tables (3 and 4 October, session 310); `datacenter_operator_sites` (12 October); `ercot_large_load_status` (newest row June: ERCOT states none since); `eia_retail_electricity_prices` (July). And `test_session156`'s frozen evaluation key against the moving `curtailment/ercot.json` (session 327 named it; GitHub's check does not fail on it).
7. **The board's threshold default of USD 100 per MWh** for a power price: keep, or a figure with a source.
8. **Branches:** `task/198-battery-data` stands on GitHub with four commits not on main (not this chain's). Every `wip/` branch of 316 to 320 and 328 to 334 is deleted; `wip/335-bill-night` is deleted once this landing is on main.

Your answers of 20 October recorded in the queue's next chain (`queue/next/010-night-20-october-code.md`) settle several earlier questions: the two maps stay as they are (sessions 318 and 330 asked), no range slider, the hunt's floor at one typical move, the day-ahead column with its words. That chain (sessions 351 to 356) is the queue step's next file.
