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
