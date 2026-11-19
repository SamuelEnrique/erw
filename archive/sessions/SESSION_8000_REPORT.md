# Sessions 8000 to 8008 report: chain 501, the whole country's page data, who trades with whom, the resource map and energy by industry, the landing desk

Energy Research Warehouse (ERW). Chain 501 of 19 November 2026, lab-desktop, data machine, first window. Model spend USD 0: no script called a model (`ERW_SPEND_CAP_USD=0`). Session numbers 8000 to 8008 checked free on origin/main and every branch. Progress, one line an item: `docs/state/progress_c501.md`.

## What a reader now sees

- Nothing changed on a page that existed: both landings' snapshots show 0 differences on the 25 pages the script reads (every page is in review).
- **After the first landing (`792dbb50d`)**: the method page `/data/methods/ba_boundaries` (read on production with the internal cookie at 1280 and 390 px: the title, the source table of hosts read and not read, the key to EIA-930, the lists of authorities without a polygon). No page reads `site/data/regions/ba_boundaries.json` yet.
- **After the desk's landing** (below): the old laptop's whole-country sections of `/events`, `/demand` and `/supply`, the portable laptop's Grid map and regions, and the second window's findings code, now reading the region files this chain wrote. The production reads are in the section "The landings".

## Part B: the whole country's page files

- **The contract** `docs/state/page_files_regions.md`, on main at 10:30 UTC (`733e7d3d5`), within the first hour; real samples and the industry and resource sections added (`cd40082b2`, `ce22c9265`, session 8006's commits), each change a dated line under "Changes".
- **B2 `ba_boundaries`**: HIFLD's Control Areas layer as Penn State's PASDA serves it (HIFLD's own catalog closed in 2025; NASA's mirror did not resolve; DataLumos disallows ClaudeBot), 71 polygons in nine batches, 67 keyed to an EIA-930 code through EIA-861's BA ID to BA Code pairs (nothing matched by name). Entities table (Decision 80, `balancing_authority`), 71 rows; web file 979,100 bytes. Landed `792dbb50d`.
- **B3 to B7** (`warehouse/derived/region_files.py`, renamed from `regions_pages.py` at the desk: test 147 keeps the word `pages.py` out of the method notes): 107 files under `site/data/regions/`, 28.7 MB: the index (13 regions, the lower 48's authorities and, on request 324, the Canadian and Mexican ones), 13 region and 58 authority demand files, 13 mix files, 13 trade files, 9 event files.
- **A region's demand** is the sum of its demand-filing authorities (generation-only authorities file none, which is why `eia930_region_hourly` holds no demand for four regions). Texas, the Mid-Atlantic, New York and New England equal ERCOT's, PJM's, NYISO's and ISO-NE's yearly averages in `demand_growth.json` to the tenth of a megawatt in every whole year 2019 to 2025.
- **New table `eia930_region_fuel_hourly`** (6,282,393 rows): the six-month files' energy source columns, which chain 401 did not keep; Texas's monthly shares equal `site/data/mix/ercot.json` to the hundredth of a percent.
- **B8**: the region tables, the fuel table, the pair tables and the page files join the data machine's daily run (`warehouse/run_data_machine.sh`, section 1f, with a test group), on `wip/c501-more`.

## Part C: who trades with whom

- `interchange_pair_daily` 552,751 rows, `interchange_pair_monthly` 18,284, `ba_trade_partners` 5,987, `interchange_event_pairs` 13,574: each side's report, their mean over the hours both reported, their gap, the direction; partners ranked by gross and net; the nine events beside the same calendar hours of the other years. Descriptive only.
- `trade_matrix.json` 452 KB, with `months_held` (request 325). For a region pair it agrees with the trade files to the MWh (the Carolinas and the Southeast, 2019, 2025 and 2026).

## Part D: the resource map, energy by industry, energy per AI query

- **D1**: `resource_layer_features` (1,371,628 rows, Decision 81, `resource`): every cell of the wind and two solar grids at 0.05 degrees and every site and area of the other resource layers, and the USGS coal fields (Open-File Report 2012-1205, 602 polygons, public domain) as a new web file `site/data/resources/coal_fields.json` (544,878 bytes). On `wip/c501-more`.
- **D2**: `eia_seds_industrial_annual` (30,940 rows, 17 SEDS series by state), `eia_aeo_industrial` (75,504 rows, the AEO2026's eleven industrial sub-sector tables, every case), and `site/data/industry.json` (1.1 MB: the Monthly Energy Review by source since 1973, MECS 2022 by industry and region, SEDS by state, EIA-861M sales by state, the AEO's sub-sectors). Landed with the desk's stack.
- **D3**: `ai_energy_published` (21 figures from 7 publications), each figure's printed words cut from its saved copy and checked at every build; nothing summed or averaged. On `wip/c501-more`.

## Part E: the filed large-load tariffs

- Avista, Schedule 25 (Washington, 3,000 kVa and up): read, a file written (energy 42.11 USD/MWh in the last block, the first-3,000-kVa charge $47,891.00 a month, contracts of five years or longer); on `wip/c501-more`, not yet in the table.
- Held by the host's terms, not read: PSEG (its Terms of Use forbid crawling and automated means for any purpose), Colorado Springs Utilities (its documents "solely for personal, noncommercial and informational purposes"), WEC's We Energies (no retransmission, republication or reuse without written consent).
- Still open: SDG&E and LADWP (their terms pages were not found at the addresses asked). Still pending: DTE (U-22061; michigan.gov refuses this reader), Tampa Electric (LLCS-1), Otter Tail (PU-26-215), Minnesota Power (agenda of 24 November).

## Part A: the desk and the requests

- Landed: chain 501's B2 (`792dbb50d`); then one stack, `wip/c501-desk-a` (`22cb29294`): chain 501's pages and tables, the old laptop's rows 51, 52 and 53, the portable laptop's rows 41 and 42, and the second window's rows 1 and 2. The first gate failed two tests, fixed at the desk (test 147, test 5171's list of readers of the disk); the second refused to start because main had moved; the third passed every step.
- Data requests 323 to 327: done (contract lines, the names across the border, months held). 320, 321, 322, 540 and 541: answered and left as they are, since each changes an existing page file or table, which chain 501's rule forbids (for Samuel's ruling). Standing rows (five_tools 2 and 5, forecast 5, licenses 11 and 12): not new.

## Decisions made without you

- **A new table for generation by source** where the chain named `eia930_ba_supply_hourly`, which holds no source columns.
- **A region's demand as the sum of its demand-filing authorities**, not `eia930_region_hourly`'s demand, which waits for generation-only authorities that never file demand.
- **The Midwest's days in Central time**, as the seven grids' files count MISO's, though EIA's reference gives MISO Eastern.
- **Weather degrees from the weighted temperature** (the region table holds no per-station degrees), and no dew point term; the 95 percent rule then leaves many regions' yearly energy figures blank.
- **The resource layers' table from the page's own reductions** (the manifest records each publisher's file and sha256), one entities table for all layers rather than fourteen tables; the offshore lease and planning areas left out as rights, not resources.
- **The AEO's entity ids carry six hex digits of the series name's sha1**, since EIA gives one series id to two series.
- **The region builder renamed `region_files.py`** at the desk, and the two new site readers of `data/regions/` listed in test 5171, so the other windows' code could land.

## For Samuel's ruling (the default taken)

- Uranium and critical-mineral deposits: `mrdata.usgs.gov` disallows every path, ScienceBase disallows Claude by name. Default: not pulled.
- Data requests 320, 321, 322, 540 and 541 (a range rule for the CAISO's study duration; SPP's October real-time month; two storage days; carbon intensity for every authority; which side reported a tie): each changes an existing page file or table. Default: left as they are.
- PSEG, Colorado Springs Utilities and We Energies: their terms forbid reuse or automated reading. Default: not read.
- The new tables in release v1: held out, as chain 401's were. Default: held.

## Needs the key

- None.

## The landings (production reads)

- **The desk's stack landed at `ce36c2541`** (task/c501-desk-a, run 44530420905: the checks, then the suite again because main moved). Snapshots `c501-deska-before` and `c501-deska-after`: 0 differences on the 25 pages.
- Read on production with the internal cookie at 1280 and 390 px: `/demand?view=country` shows "The whole country" tab, Tennessee beside the Carolinas, "From 2019 to 2025, average demand went from 18,190 MW to 19,490 MW, a change of +7.15 percent, and the highest hour from 29,568 MW to 35,086 MW (+18.66 percent)", the figures of `demand/ten.json`; `/grid?view=network&shape=map` shows the thirteen EIA regions as a second row of buttons under the seven grids; `/events/uri-2021` at 390 px draws without sideways scroll; `/supply?view=country` opened on the page's head (the whole-country section is lower and was not read in view).

## Later in session 8009

- **Data request 328** (the old laptop): a record's first and last local days, held only in part, were written as whole days; now a day is whole only with every hour of its calendar day. Fixed in `region_files.py`, demand files rebuilt.
- **Data request 329**: the seven grids' authority files carry `alike` (equal to `demand_growth.json` in every whole year, California's included); the method note says which demand and that no hour is moved.
- **Data request 542** (the portable laptop): the coal fields in the map's layer form and `site/data/resources/manifest_added.json`, a new file in the manifest's form; `manifest.json` unchanged.
- **Data request 543**: the live set stood at 15 and 16 November because the daily run's test step stopped on 18 November at test 7014 (under `health.py` its skip exits 75, and the test expected 0); the test now sets `ERW_SKIP_EXIT` aside. On `wip/c501-desk-b`.
- **The mix files' rule**: the first build tested each authority's sources against its net generation; one small authority a few megawatts off then left its whole region out, and the Mid-Atlantic's mix held 40 months, the Southwest's 36. `eia930_region_fuel_hourly` now applies `mix_profile`'s rule to the region (15 percent for the Mid-Atlantic, as PJM): 6,730,507 rows; the Mid-Atlantic holds 95 months, the Southwest 85, California 98. Texas still equals ERCOT.
- **D3**: Meta's 2025 data index and Microsoft's 2026 fact sheet added: 23 figures from 9 publications. Google's environmental reports sit in a folder `www.gstatic.com` disallows: not read.
- **A slip, put right**: a `git stash pop` in the stack's worktree took the data machine's stash of 18 November (its uncommitted news and deals tables) from the shared stash list; it was stashed again at once with the same files (`git stash list`, entry 0).

## Sessions 8010 and 8011

- **Data requests 544 to 551** (the old and portable laptops): 545 (each side's report beside an event pair's flow), 546 (the weather's coverage by year), 551 (a source never printed drawn blank, `sources_not_printed`) done on the stack; 544, 547, 548, 550 answered from EIA's files: Seminole's 2019 has 5,292 hours at or below zero, SRP's 9,283 MW at 14:00 on 22 July 2023 is EIA's value and passes the screen at 20 percent above its neighbours, the Mid-Atlantic's missing 1,637 hours of 2025 with the Carolinas are hours PJM did not file (1,632 on its tie with CPLW); 549 in part.
- **Stack d** (`wip/c501-desk-d` at `d40518884`): chain 501's D1, D3, B8, part E's Avista row, the region's mix rule, the daily run's test fix (request 543), requests 328, 329, 542, 545, 546 and 551, the portable laptop's rows 42 and 43 and window 2's row 2. The first gate of stack b failed one test (8603, the portable's check of layer files, which now counts `manifest_added.json`); stacks c and d then passed every step (the suite 10,299 and 10,324 tests OK). Gated in the hours with no landing; pushed after 16:15 UTC.
- **Stack d landed** at `d89580bd3` (16:44 UTC; snapshots `c501-deskd-before` and `c501-deskd-after`: 0 differences on the 25 pages). Read on production with the internal cookie at 1280 and 390 px: /resources (the coal fields still read "not held": the landed map reads manifest.json only; the portable's newer head reads manifest_added.json), /grid?view=regions, /demand?view=country, /events/uri-2021. Window 2's row 2 marked landed; the portable's rows 42 and 43 kept requested (their heads had moved).
- **Data request 552** (the portable): the coal fields' `value` in square miles, the unit of the map's other outlines, with `AREA_KM2` beside it; the entry's note without the file name (a new key, `method_note`); `resource_tables.py --map-only` rebuilds only the map's form. Run from the main checkout, where the saved GIS.zip is.
- **Stack e** (`b0a3bfb47`): stack d with the portable's rows 42 at `43863e85d` and 43 at `180880ef6` (the portable's versions of `replicate_regions.py` and test 8603 taken in the merges: they already read the null sources and accept the coal layer by its source). Its first gate failed test 8608 (it imports `topojson-client`, and land_check runs the suite before its `npm ci`); the test now skips where the site's packages are not installed. The second gate passed every step; pushed at 17:33 UTC.
- **Stack f** (`195b0f795`): stack e with the portable's newest heads (rows 42 at `c527a0bb7`, 43 at `4e2b2b54c`), gating from 17:34 UTC. Decision: this is the chain's last stack. The portable moves its heads about every half hour, and a head that moves after f is gated waits for the next desk.
- **Part E, the rest of the eighty**: chain 401 tried every one of them. The open ones are held by terms or access controls. JEA was asked again and still gives no connection. Nothing new written.
- **Slip**: a progress line gave 16:58 UTC for a request the clock put at 16:53; corrected in the next commit.
- **Stack e landed** at `93e657696` (18:08 UTC, after GitHub ran the suite again because main had moved; snapshots `c501-deske-before` and `c501-deske-after`: 0 differences). On production at 1280 and 390 px, /resources now lists the coal fields as a layer with its measure line.
- **Stack f landed** at `214f7cd9d` (18:28 UTC; snapshots `c501-deskf-before` and `c501-deskf-after`: 0 differences); /grid?view=regions on production draws the 13 regions' row.
- **Data request 553** (the portable): the wind supply curve's and the hydrothermal systems' hover fields. `manifest.json` is an existing page file, so the lists go in a new file, `site/data/resources/hover_fields_added.json`, built by `warehouse/derived/resource_hover_fields.py` from the laboratory's saved column lookup and USGS's saved metadata, each pair in the publisher's words; the wind layer's `name` is the supply curve's `sc_point_gid`. The page needs one line of its own code to read the file (the portable's).
- **Decision, revised**: stack f was meant to be the last; request 553 arrived while it landed, so stack g carries 553 and the portable's newest heads, and it is the last.
- **Slip**: the Write tool turned a typed `—` escape into a literal em dash in the new builder and test; caught by the dash count before the commit and replaced with `chr(0x2014)`.
