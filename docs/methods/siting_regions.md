# Where the next gigawatts can go: every count side by side (method, internal)

Written by session 11200 (chain 760, part B) on 28 November 2026. Internal: this note is for the warehouse's own sessions and the replication; the page's hover gives each count's period and source in plain words. Builder: `warehouse/derived/siting_regions.py`. Files: `site/data/siting/regions/` (index, one file a place, a table of every place), shape fixed by the contract `docs/state/page_files_siting_regions.md`. Replication: `replication/siting_regions/replicate.py`. A daily step of the data machine (`dm_siting_regions`) writes the files again after the tables they read are refreshed.

Samuel agreed on 2 October 2026 that this is a flagship analysis, and ruled on 22 October 2026 that it lives on the datacenter page's All grids tab, not on a page of its own.

## What it is, and what it is not

For each place, each count the warehouse already holds that bears on where a large new load can connect: price, congestion, how tight the grid runs, what waits to connect, the large-load rules, the mix and its carbon, what the place leans on its neighbours for, what is spare, how well its demand is forecast, and the datacenters already there. Each count is what its publisher published, or a plain arithmetic of it (a share, a sum, a mean, a percentile, a count of hours), written below. There is no score, no rank, no weighting of one count against another and no "best region": how a reader sorts the places is the reader's choice on the page. No request is made; every figure comes from a table already held, and a count the warehouse cannot show is written null with its reason.

## The places

- **EIA's 13 regions**, as `regions[]` of `site/data/regions/index.json` (the Grid tool's list), each with its member authorities.
- **The seven market operators**, each through its own balancing authority (CAISO through CISO, ERCOT ERCO, SPP SWPP, MISO MISO, PJM PJM, NYISO NYIS, ISO-NE ISNE).
- **Every other balancing authority whose highest hourly demand in the last 12 whole months is at least 5,000 MW**, from `bas[]` of the same index (US, active, not generation-only), as `eia930_ba_demand_hourly` holds its demand. On 28 November 2026 these are 17: AECI, AZPS, BPAT, CPLE, DUK, FPC, FPL, LDWP, LGEE, NEVP, PACE, PSCO, SC, SCEG, SOCO, SRP, TVA (BANC's one hour at 6,091 MW on 29 September 2026 is an impossible hour; its highest real hour is under 5,000 MW). The list moves with the data: an authority that crosses the line appears or leaves at the next build, and the builder removes a place's file when the place leaves.

## The period

The last 12 whole calendar months before the build's month, in UTC (on 28 November 2026: 1 November 2025 to 31 October 2026), and for the growth of the peak the 12 months before them. A snapshot table (Berkeley Lab's queue, the large-load tables, the datacenter tables, the reserve reports) is read as it stands, and its own date is the period written beside the figure.

## Each count

**Price** (`ercot_all_hub_prices_history`; `iso_hub_prices_history`, with `iso_dam_hub_prices` and `iso_rtm_hub_prices` for the hubs they add). For each hub of the place's operator, each market (day-ahead, real-time): an hour's price is the mean of the intervals the tables hold for that hour, to 6 decimals; then over the period the mean, the 95th percentile, the hours above USD 100, the hours below zero and the hours held. A hub with fewer than 80 percent of the period's hours (SPP's South Hub and CAISO's ZP26, held only from 26 August 2026) is written with its figures held `too few:` and the span it does hold. PJM, NYISO and ISO-NE are held for their terms (`docs/licenses.md`), MISO for its pause; the words are those of `warehouse/derived/conditions_page.py`. A balancing authority outside the seven markets has no public hub price (`not a market:`); a region's hubs are those of the operators among its members. The reference hub of a place (`ref_hub`, the one the table shows) is the operator's first hub in the builder's list: ERCOT's Hub Average, CAISO's SP15, SPP's North Hub.

**Congestion** (`price_congestion_monthly`, `constraints_binding_monthly`, CAISO and SPP). A hub's share of its price that was congestion: the hour-weighted mean of the monthly congestion part over the hour-weighted mean of the monthly price, times 100, null when the mean price is not above zero. The constraints: hours bound and cost (the monthly mean absolute shadow price times the hours bound, summed over the period), the ten that bound most hours and the ten that cost most, each by the operator's own name and contingency, with no guess at where it is.

**How tight the grid runs.** Every hour of demand is first passed through the warehouse's rule for impossible hours (`warehouse/derived/impossible_hours.py`, `docs/methods/impossible_hours.md`: held, above zero, within 25 percent of the median of the four hours around it, within a third to three times the authority's median hour), which blanks hours that did not happen (TVA at 44,377 MW on 20 October 2026); every count that reads demand reads the screened hours. Peak demand: the highest hour of the period in `eia930_ba_demand_hourly`, and of the 12 months before; growth is the ratio less one, in percent. A region's demand is its members' sum: a member is counted when it reports in at least 90 percent of the two years' hours, and an hour is kept only when every counted member has a value in it. Notices (`grid_all_alerts`, CAISO and ERCOT only): the days in the period with at least one notice of each group, and the days with any. The groups, from each operator's own kinds: alerts (CAISO: restricted maintenance operations, alert, Flex Alert, voluntary load reduction; ERCOT: operating condition notice for weather, advisory, weather watch, conservation appeal, voluntary conservation), watches (CAISO: warning, EEA watch; ERCOT: watch, power watch), emergencies (CAISO: stage 1 to 3, EEA 1 to 3, transmission emergency, load interruption; ERCOT: EEA 1 to 3, rotating outages). Updates, statements and tests are not notices of a condition and are left out. Out of service at the peak hour (`generation_outages_hourly`, CAISO and SPP): the operator's total megawatts out in the peak hour. Reserves: CAISO's planning reserve margin achieved and required as its summer assessment prints them (`iso_reserve_margin_reports`); ERCOT's reserve margin at the summer peak load hour for the next summer, from its newest Capacity, Demand and Reserves report (`ercot_cdr_reserve_margins`; ERCOT prints no target beside it).

**What is waiting to connect** (`lbnl_interconnection_queue`, Berkeley Lab's Queued Up, 2026 edition, through 2025; `interconnection_durations`). Active requests summed in megawatts and counted, by fuel as Berkeley Lab cleans it. Withdrawn share: of the requests entered 2000 to 2020 that reached an end (withdrawn or operating), the withdrawn megawatts over all, in percent. Median years from request to operation of the projects operating 2021 to 2025, shown when at least five. An operator takes Berkeley Lab's region of the same name; an authority outside the markets takes Berkeley Lab's entity (the builder's `LBNL_ENTITY_BA`); Duke and PacifiCorp are split by the request's state (Duke: Florida to FPC, the Carolinas to DUK; PacifiCorp: Utah, Wyoming and Idaho to PACE, Oregon, Washington and California to PACW). A region sums its members.

**Large loads** (`utility_large_load_rules`, `utility_large_load_queue_totals`, `state_large_load_laws`). A rule or a queue total belongs to the authority its region words name (the builder's `LL_REGION_BA`), or, where they name none, to the authority a state is wholly in (below). The smallest load a rule applies to: the first figure written in MW, megawatts or kW within the first 80 characters of the rule's threshold as the table prints it; a text that begins by saying there is no threshold, "not published", and a figure in MVA or GW are not read. Each rule is listed with its printed threshold beside the figure read. The laws listed are those of the states the place reaches (below).

**The states a place reaches, and the authority a state is wholly in** (`eia861_utility_sales`, total retail sales, the newest year). A place reaches a state when its authorities sell at least 10 percent of the state's retail sales, or the state is at least 10 percent of the place's. A state is wholly in one authority when 85 percent of its retail sales are there (the rule of `site/data/siting/facilities.json`).

**What the power is made of and what it emits.** Each fuel's share of net generation over the period (`eia930_region_fuel_hourly`, EIA's net generation by source). The table holds EIA's 13 regions only, so an operator's and an authority's mix are held with that reason. Carbon intensity (`carbon_intensity_hourly`, the demand basis, `intensity_demand`): the mean of the hourly values over the period, and by hour of the day in the place's clock. The table covers the seven operators' authorities and the US 48 only; every other place is held `not held:` until it covers more. A region whose one member is an operator's own authority (Texas and ERCOT, New York and NYISO, New England and ISO-NE) is the same grid: the region takes the authority's carbon intensity (`intensity_from`) and the operator the region's mix (`mix_from`). A fuel is named in words, with its key beside it.

**What it leans on its neighbours for.** Net imports as a share of demand: minus the sum of total interchange (`eia930_ba_supply_hourly`, EIA's sign: positive is net export) over the sum of demand, in the hours both are held; the same over the 100 highest-demand hours of the period (two hours of equal demand: the earlier first). A region sums its members' demand and total interchange (flows between members cancel). The three neighbours a place took most from, net, over the period: an authority from `eia930_ba_interchange_hourly_<year>` (minus the sum of its interchange with each neighbour), a region from `eia930_region_pair_hourly` (Canada and Mexico among them).

**What is spare.** Curtailed wind and solar megawatt-hours over the period (`iso_curtailment_monthly`, CAISO and SPP), held `too few:` when a month is missing. Hours of negative price: the day-ahead hours below zero at the reference hub (the price count above).

**How well its demand is forecast** (`site/data/predict/scores.json`, the ERW forecast's own score file, built from `eia930_ba_demand_hourly`). The mean absolute percentage error of the operator's day-ahead demand forecast as filed on EIA-930, and of the ERW forecast, over the forecast's last 730 days (cut `last_2_years`), and the hours scored. An operator reads its authority's scores; a place the forecast does not cover is held.

**Datacenters already there** (`datacenter_facilities`, `datacenter_projects`). A facility or project is in an operator's authority by the `grid` the table gives it, else in the authority its state is wholly in; anything else is in no place. Counted, with the megawatts stated summed where a figure is stated, and the 25 largest listed with their source.

## `table.json`

One row a place, one value a column; every value is a count of the place's own file (the reference hub's for the prices), so the table computes nothing new. A held value is null with its reason in the row's `cell` map.

## Decisions (session 11200)

| Key | Choice | Default |
|---|---|---|
| `places` | The Grid tool's 13 regions, the seven operators, and the other authorities of at least 5,000 MW peak in the last 12 whole months; no new list | 37 places on 28 November 2026 |
| `screen` | Demand passes the warehouse's rule for impossible hours before any count reads it | the rule of `docs/methods/impossible_hours.md`, unchanged |
| `period` | The last 12 whole calendar months in UTC, the 12 before for growth | 2025-11-01 to 2026-10-31 |
| `hub-floor` | A hub's price figures need 80 percent of the period's hours | SPP South and CAISO ZP26 held `too few:` until August 2027 |
| `ref-hub` | The operator's first hub in the builder's list: ERCOT Hub Average, CAISO SP15, SPP North | as listed |
| `region-sum` | A region's demand and interchange are its members' sums (members reporting 90 percent of hours), not EIA's own region series, which the warehouse holds with gaps for five regions | members' sum |
| `notices` | Days with a notice of each group, the groups written above from each operator's own kinds | CAISO and ERCOT only |
| `threshold` | The first figure in MW or kW in the first 80 characters of the printed threshold, shown beside its text | as written above |
| `states` | 10 percent of either side's retail sales reaches a state; 85 percent puts a state wholly in one authority | EIA-861, newest year |
| `held` | A held count is null with a reason in six kinds: license needed, paused, not published, not held, not a market, too few | as the contract writes them |
| `no-rank` | No composite, no weighting, no order of merit; the page sorts as the reader chooses | the index's order: regions, operators, authorities A to Z |

## Limits

- Prices are public for ERCOT, CAISO and SPP only; the other four markets are held by their terms or their pause, and the places outside the markets have no hub price.
- Notices, outages and curtailment are held for the operators whose tables the warehouse holds; a blank says "not held", never that nothing happened.
- Carbon intensity covers the seven operators' authorities only.
- Berkeley Lab's file is a year-end snapshot (through 2025); it is not a live queue.
- The datacenter tables are the ERW's tracker, built from news and company sources; a place with none listed may have datacenters the tracker has not placed.

## Five years (part F, session 11200)

Beside its monthly trend, each of the six counts that carry one also carries `years`: its figure for each of the five whole calendar years before the build's year (2021 to 2025 on 28 November 2026), by the same arithmetic as the period's figure (the highest hour, the mean of the hourly prices, the mean intensity, net imports over demand, the sum of the monthly curtailment). A year holding under 80 percent of its hours (all twelve months for curtailment) is null. A region's year is its members' sum taken on that year alone. Demand passes the rule for impossible hours over the whole read (the five years and the period). Prices before July 2023 come from `iso_hub_prices_history_2018` (SPP's North Hub from July 2018); SPP's North Hub holds no hour from July 2023 to August 2024, so its 2023 and 2024 are null.
