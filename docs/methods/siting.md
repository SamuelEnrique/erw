# Where can a large load go: the All grids tab of "What a datacenter pays"

Version 1, session 712, 22 October 2026 (chain 050, `queue/done/050-night-23-october-code-allgrids.md`); version 0 was session 700's. Internal: the tab is in review, like every page.

`/cost-of-power` ("What a datacenter pays") answers, for one chosen region, what a load pays, when it connects and how clean the power is. Its tab **All grids** (`/cost-of-power?view=allgrids`) answers the same questions for every grid, hub and zone the warehouse holds a price for, and behind a toggle for every ERCOT node of `node_basis_daily`, in one sortable table.

It is the same page and the same model. The rows are "Your load"'s own index. Each column is computed by the library function that computes it for "Your load", or by a function of `site/lib/siting.ts` that takes "Your load"'s own functions as an argument, so the two views cannot disagree. The tab ranks nothing by a score and expresses no view: it sorts by the column the reader chooses and says what the sort is.

## Where the code and the files are

- **Code**:
  - `site/lib/siting.ts`: pure; the profiles, the columns, the rows, the inputs, every figure and its check key;
  - `site/lib/sitingdata.ts`: the files, server only;
  - `site/app/cost-of-power/AllGridsView.tsx` (the right side), `AllGridsForm.tsx` (the left box) and `AllGridsNodes.tsx` (the node list).
- **Files**:
  - `site/data/datacenter/`: the hub and zone prices, `warehouse/derived/datacenter_page.py`; "Your load"'s rules, waits and delivery files;
  - `site/data/siting/`: `warehouse/derived/siting_page.py`;
  - `site/data/demand_growth.json` and `site/data/large_load_status.json`: "Your load"'s own.
- **No read of the database** is made by the tab.
- **The check keys**: every figure carries `allgrids|<column>|<row>[|<inputs>]` (the site's form of the prompt's `allgrids_<column>_<row>`). `site/scripts/check-values.mjs` recomputes each from the same files with the same functions (`site/scripts/siting-files.mjs`).
- **Held figures**: a figure from an internal table is computed where the table is held and drawn as "license needed" in place, with no key, so the value checker passes it by (session 408's rule).

## The rows

- **Hubs and zones** (the default row set): every region of `site/data/datacenter/index.json`, the index "Your load" reads. `datacenter_page.py` builds it from the hub and zone price tables (`ercot_all_hub_prices_history`, `ercot_zone_prices_history`, `iso_dam_hub_prices`, `iso_rtm_hub_prices`, `iso_hub_prices_history`, `iso_zone_prices_history`, the ISO-NE and NYISO zone tables).
  - On 22 October 2026: ERCOT 14 (6 hubs, 8 load zones), CAISO 3, NYISO 11, ISO-NE 9, SPP 2.
  - Then MISO's 8 hubs, which the index names and does not price ("paused while terms are reviewed", `docs/methods/miso_pause.md`).
  - Then PJM as one row of its own, since no PJM hub or zone price is held: its columns held without a price (queues, carbon, capacity) have a row.
  - 48 rows. The default order is alphabetical by the grid's name, then by the row's name.
- **ERCOT nodes** (the toggle): every settlement point of `node_basis_daily` that is neither a hub nor a load zone, 873 of its 888 points.
  - Each node has its class and ERCOT's resource types at it.
  - The table holds no node's load zone, settlement hub or wires utility, and the tab says so once, above the list.

## The load's profiles

A profile sets three inputs (the load factor, the curtailment rule, whether the load is interruptible) and nothing else. Each default is shown in grey beside its field, with its source on hover, and is editable in place within the profile's range. The size is the reader's: default 100 MW, the size "Your load" opens on.

| Profile | Load factor | Curtailment rule | Interruptible | Source of the defaults |
|---|---|---|---|---|
| Datacenter (default) | 0.90: it draws 0.90 of its size in every hour | never curtails | no | the owner's chain prompt of 22 October 2026 |
| Flexible compute | 0.90 while running | off in the hours of ERCOT's four summer peak intervals, and in hours whose day-ahead price is at or above a strike, USD 1,000 per MWh by default | no | the prompt; the strike is the page's scarcity level (`SCARCITY_USD`) |
| Electrolyzer | 0.55, editable from 0.40 to 0.70: the share of the hours it runs, at its full size | runs only in hours below a strike. With no strike typed, it runs at or below each row's own k-th cheapest hour of the window, k the load factor's share of the hours | no | the prompt's range; 0.55 its middle |
| Heavy industry | 0.80 | off only when the grid interrupts it. No table holds those hours, so it runs every hour | yes | the prompt |

## The columns, each with its formula

| Column | Formula | Table, filter | Vintage (22 October 2026) | License | Where it cannot be filled, the words |
|---|---|---|---|---|---|
| **Energy**, USD per MWh | the flat load: `span(lastTwelve(months)).flat` over the day-ahead hours, real time beside it (`flatTwelve`, `lib/datacenter.ts`'s own `monthsRuled`, `lastTwelve`, `span`); a month counts when 95 percent of its hours are held. Under a profile: the load-weighted day-ahead price over the hours it runs inside the same twelve months (`profileTwelve`), and the hours off. A node: its hub's figure (HB_HUBAVG) plus its mean daily day-ahead basis over the same months, weighted by days, drawn when it holds 90 percent of the days | `data/datacenter/<grid>_<year>.json` (day-ahead `da`, real time `rt`); `node_basis_daily`, `variable = dam_basis` | October 2025 to September 2026 at most rows; nodes 1 October 2025 to 20 October 2026 | public (ISO-NE, MISO and NYISO prices held since 20 October; see the ruling) | MISO "paused"; PJM "license needed"; ISO-NE's zones "not held" (no twelve whole months in a row) |
| **Transmission and 4CP**, USD per MWh | ERCOT: rate x 1,000 x share / hours run a year. The share is the load's mean weight in the hours of the four intervals of the newest whole summer; the hours run a year are the profile's hours over its twelve months, scaled to 8,760; the rate is the Commission's newest approved postage stamp rate (matrix A). Drawn three ways: the profile's own, firm (share 1), off (the rule "off at the four peaks", computed) | `ercot_4cp_intervals` (`data/siting/ercot_4cp.json`); `texas_transmission_matrix` (`texas_delivery.json`, as "Your load") | summer 2025; the 2025 rate (USD 68.547301 per kW a year) | intervals public; matrix internal (see the ruling) | every other grid "not held": the utility's large-load tariff |
| **Capacity**, USD per MWh | the newest cleared delivery period's price for the row's zone, x 365 (USD per MW-day) or x 12,000 (USD per kW-month) to USD per MW a year, over the hours the load runs a year (it is taken to run at the grid's peak) | `iso_all_capacity_prices` (`capacity.json` holds the period, auction and zones, no price) | PJM BRA 2028/29, ISO-NE FCA 18, MISO PRA 2026/27 spring, NYISO spot October 2026 | internal | ERCOT, CAISO, SPP "no capacity market" (zero in the all-in); PJM, ISO-NE, MISO, NYISO "license needed"; an interruptible load "not held" (its utility's interruptible rate) |
| **Time to connect**, months | the median of the months from request to operation (on_date less q_date, / 30.4375 days, to one decimal) of the requests operational and online in the newest three whole years, by grid; none under five requests. Since session 718 from the data machine's `interconnection_durations` (chain 043), the same requests, its months to one decimal. Under it: the newest decided large-load rule of the grid, ERCOT's MW approved to energize, the measured waits | `interconnection_durations`, from `lbnl_interconnection_queue` (`connect.json`); `large_load_rules` (`rules.json`); `ercot_large_load_status`; `large_load_waits` (`how_soon.json`) | Berkeley Lab 2026 edition (through 2025); rules to 22 September 2026; ERCOT's report of 19 June 2026 | public; waits internal | ISO-NE "not held" (no request with both dates); "no rule held"; waits "license needed" |
| **Headroom**, percent; MW | demand growth: the mean demand of the last twelve months over the twelve before, the monthly means weighted by their hours (the grid's balancing authority); generation under construction (EIA status U, V, TS) due in the twelve months after the vintage; capacity above the peak: the grid's operating generators' net summer capacity over its peak hour, less 100 (since session 718, `grid_peak_vs_capacity`, every grid, by each generator's balancing authority; before it, the whole states' installed capacity, NYISO and ISO-NE only) | `eia930_demand_growth` (`demand_growth.json`); `eia860m_planned_generators` (`headroom.json`); `grid_peak_vs_capacity` | demand through September 2026; EIA-860M vintage August 2026; the 2025 peak against the August 2026 list | public | reserve margins by zone not held |
| **Carbon**, kg CO2 per MWh | the row's eGRID subregion's plants' CO2 over their net generation (a plant reporting no CO2 adds generation only, as eGRID sums them); for a profile that runs in some hours, the grid's hourly intensity weighted by the load over the hours it runs, where it covers 90 percent of them | `egrid_power_plants` (`carbon.json`); `carbon_intensity_hourly`, `intensity_demand` | eGRID2023 (data year 2023); hourly to 18 October 2026 | public | none today; MISO and PJM have no hourly figure (no price, so no hours run) |
| **Utility** | where the row's name is a place (18 rows: a city's zone, a hub the data machine placed in a county), the utilities EIA-861's service territories list for that county, and among those billing customers inside the row's grid the largest seller to industry: its industrial revenue over its industrial sales, and its growth (since session 718); else the state's largest seller inside the grid, said to be a stand-in | `utility_service_territories`, `eia861_utility_sales` (`utility.json`) | 2025 | public | ERCOT nodes "not held" (no county); a county's wires utility with no sales row is named and not priced |
| **All-in**, USD per MWh | energy + transmission + capacity, each held or zero by market design | as its parts | as its parts | as its parts | "not held", or "license needed" where the missing part is a held figure |

## The screen

- **Sort by any column**, largest or smallest first. A row with no figure, or one whose figure is held under a license, sorts last: a held figure is never sorted by its value, which the order would give away.
- **Filters**: by grid, by kind (load zones or hubs), by an energy band, and to rows whose every cost part is held.
- **A and B**: two rows side by side, every column's figure and B less A, the load's year all-in in USD and the MWh it uses. The MWh are its draw while running (its size times the load factor; its size for a load that runs below a strike) times the hours it runs a year. A sets one headline line.
- **Every input is in the address**: a reader can send the screen. The node list sorts in place and keeps its sort in the address (`nsort`, `ndir`), and a node's name opens its panel (`node`).

## The replication

`warehouse/replication/siting.py` (standard library only) computes, for three rows (ERCOT HB_HUBAVG, CAISO SP15, NYISO N.Y.C.) and three ERCOT nodes under each of the four profiles, every figure the tab draws for them, and sets each beside the page's `data-raw`.

- **What it reads**: the live set with the anon key only for the tables the live set holds (the four peaks, Berkeley Lab's queue, the hourly intensity), and the tab's own files for those it does not (the price history, the node basis, eGRID, EIA-861, the Commission's rate). It ports `lib/datacenter.ts`'s hours, months and twelve-month window to Python.
- **How to run it**: `python warehouse/replication/siting.py --repo . --page <a build>`. Exit 0 when every figure set beside the page equals it.

## Decisions (each dated, and reversible unless said)

1. 2026-10-22, session 700: a third view of the one page, between "Your load" and "Grid by grid". "Grid by grid" stays.
2. 2026-10-22, 700: the profile dropdown is in the tab's own box, so no default figure of "Your load" moves.
3. 2026-10-22, 700: PJM is one row; MISO's hubs are rows with the existing tab's words.
4. 2026-10-22, 700: the flexible strike is USD 1,000 (the scarcity level). The electrolyzer's load factor is 0.55, and its default strike is each row's own k-th cheapest hour.
5. 2026-10-22, 701: `lib/siting.ts` takes `lib/datacenter.ts`'s functions as an argument (one arithmetic, no import).
6. 2026-10-22, 701: ISO-NE's and NYISO's prices are drawn as "Your load" draws them (see the ruling).
7. 2026-10-22, 702: the load factor does not move the price per MWh; heavy industry runs every hour.
8. 2026-10-22, 703: the four-peak charge: the rate over the hours run; the draw cancels; a node is charged on its hub's hours.
9. 2026-10-22, 704: no internal price in the public repository (irreversible in effect once pushed, so kept out). Capacity is drawn as "license needed"; a load is taken to run at the grid's peak.
10. 2026-10-22, 705: the generators' median months to connect stand for the grid's wait. The rule is the newest decided row. ERCOT's approved MW stand where a wait is not held.
11. 2026-10-22, 706: demand growth is the grid's balancing authority's (not the sub-region's). "Coming" is under construction, not an interconnection agreement (EIA-860M records none). Capacity over peak only where the grid is whole states.
12. 2026-10-22, 707: each row's eGRID subregion by its geography (written in `subregionOf`); PJM by eGRID's ISO/RTO field; the hourly figure is the balancing authority's intensity, consumed.
13. 2026-10-22, 708: the state's largest seller to industry stands for the row's utility (territories not held); hubs take a state (ISO-NE's hub Massachusetts, SPP's North Kansas, South Oklahoma).
14. 2026-10-22, 709: what every node shares is drawn once, above the list; the list is virtual (the first 40 rows on the server).
15. 2026-10-22, 710: "load band" is read as an energy band, together with a filter by kind. A held figure never sorts by its value.
17. 2026-10-22, 718: the data machine's three tables of chain 043 wired in: `interconnection_durations` for the time to connect (the same requests, its months), `grid_peak_vs_capacity` for capacity above the peak (every grid; the figure is now "percent above the peak", where 706's was "percent of the peak"), `utility_service_territories` for the utility of a row whose name is a place (its county: the data machine's hub counties of session 681, and a zone's city's county). A county's utilities are kept inside the row's grid by the balancing authority their sales rows name.
16. 2026-10-22, 711: a node's basis spread is the 10th, 50th and 90th percentile of its days over the node file's twelve whole months. Its county, the planned generation near it and the transmission projects there are not held.
18. 2026-10-22, 719: the datacenter tracker links each facility it shows to the tab. A facility is placed by its county where the county's utilities (EIA-861's service territories) bill inside one grid only (the county's own row where the tab has one, else the grid's main region), else by its state where 85 percent or more of its retail sales are inside one grid, else not at all; it is never placed at a node. The link sets the facility's MW (bounded as the form bounds it) and its row as A; the facility is named on the tracker beside the link, never in the address or on the tab. `datacenter_facilities` is held whole (license needed since 21 October 2026), so `facilities.json` is built from the two public tables only (every county and state, 1,504 counties in one grid) and holds nothing of the tracker's rows; the tracker places the rows it shows when it draws them. While the hold stands the tracker shows no row, so no link shows.
19. 2026-10-22, 724 (chain 062): the node list's basis spread is the node's 90th percentile of daily basis less its 10th over the days it holds in the file's twelve months, the panel's own percentiles; the months node_basis_daily lacks are named from the file's days by month; a node can be set as A or B, and the download is the rows shown in the page's figures, made in the browser.
20. 2026-10-22, 726 (chain 062): the Utility column's revenue per MWh is of three kinds, from EIA-861's service type (bundled, delivery only, energy only); each cell names its kind, and the A and B panel's utility line subtracts only like from like ("not alike" otherwise). No figure changes; one difference key is no longer drawn where the kinds differ.

## The limits

- **Figures as of the build**: every figure is of the files the build read. The node basis and the eGRID and EIA-861 tables are rebuilt from the archive on a machine that holds them; the tab's files are only as new as their last build.
- **The energy is wholesale**: no delivery, distribution, ancillary or retail charge is in it, and no hedge.
- **The "Utility" column is a state's largest seller to industry**, not the row's own utility.
- **Demand growth is the whole grid's**, and weather is not removed.
- **Time to connect is a generator's wait**, not a load's: loads are not in Berkeley Lab's file.
- **Carbon differs between the two measures**: the annual figure is generation in the subregion; the hourly is consumption in the balancing authority. They differ, and each says which it is.
- **Gaps**: `docs/reviews/siting-gaps.md` lists every cell the warehouse cannot fill, with the source that would.
