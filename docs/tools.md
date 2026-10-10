# The ERW's live tools

Energy Research Warehouse (ERW), session 53. Every tool live on the public site (https://erw-flame.vercel.app), with:
- its route;
- the question it answers;
- its audience: students and teachers, investors and lenders, researchers, or everyone;
- its data sources.

The plan of record is `docs/platform-tools.md` (31 tools, some planned). This list is what a visitor can open today. The home page's three audience sections and the nav draw on it; `site/lib/pages.ts` holds the nav's copy of each line.

**Count:** 34 public tools, plus 3 internal pages behind a token. Each row is one tool: routes that are parts of one tool (the seven grid pages, the five event pages, the three problem sets, a page and its detail pages) share a row.

## Prices and markets

| Tool | Route | The question it answers | Audience | Data |
|---|---|---|---|---|
| Price board | `/board` | What is power selling for at each ISO's main hub right now, and how did it move? | investors and lenders; everyone | `price_board_latest`, `price_board_peak_offpeak`, `price_board_spreads`, `price_board_carbon`, `latest_prices` |
| Markets (trader view) | `/markets` | How do day-ahead and real-time prices compare by hub, on- and off-peak? | investors and lenders | `iso_trader_daily`, `iso_rt_top_intervals` |
| Cost of power: what a datacenter pays (session 138; until then "what power costs to buy", now its view "Grid by grid") | `/cost-of-power` | For a load the reader describes (grid, region, size, how it runs, how it buys): what will the power cost, will it be there, how clean is it, how soon can it be had? The view `?view=grids`: what does a MWh cost to buy at each hub, weighted by when the grid uses it? | AI companies and large loads; investors and lenders; researchers | the site's files of hourly hub and zone prices (`site/data/datacenter`, from the public price tables: `docs/methods/datacenter_cost.md`); headline figures of `clean_energy_summary`, `grid_stress_yearly`, `eia930_demand_growth`, `interconnection_queue_summary`, `ercot_large_load_status`; the view: `cost_of_power_monthly`, `cost_of_power_hourly_profile`, `cost_of_power_carbon` |
| Cost of power: what a generator earns | `/cost-of-power/seller` | What does a merchant solar, wind, battery or peaker asset earn month by month, and does it cover its debt? | investors and lenders | `merchant_revenue_monthly` (snapshot `site/data/merchant_snapshot.json`) |
| The shoulder hours (in review, session 75) | `/shoulder` | How long is the evening stretch between the solar midday and the demand peak in ERCOT and CAISO, how much of it do today's batteries cover, and how many hours would they need? | investors and lenders; researchers | `shoulder_hours_monthly` |
| Cost of power: what a battery earns | `/cost-of-power/battery` | What does a grid battery of this size and duration earn from energy and ancillary services together, and does it cover its debt, with and without a contract? | investors and lenders | `battery_stack_monthly`, `battery_stack_stress_daily`; NYISO and SPP in review, in the internal view only (session 86): `battery_stack_review_monthly` |
| Prices | `/prices`, `/prices/<entity>` | Every public ISO hub and zone price, with Henry Hub, WTI and Brent | everyone | the ISO price tables, `eia_fuel_spot_prices`, `latest_prices` |
| ERCOT peak premium | `/explorer/ercot-peak-premium` | How do ERCOT's real-time prices spread across the day, by hub and year since 2015? | researchers | `ercot_peak_premium_annual`, `ercot_peak_premium_monthly` |
| Supply and trade (in review, session 134) | `/supply` | Is the market tighter or looser than last week, last year and normal for the season: gas storage, crude and product stocks, production, refining, trade, fuel burned for power and managed money positioning, each against the three, with the week's surprise marked? | investors and lenders (traders in oil, gas and power) | `eia_gas_storage_weekly`, `eia_petroleum_supply_weekly`, `eia_gas_trade_monthly`, `eia_basin_production_monthly`, `cftc_cot_positions` (the page reads `site/data/supply.json`); method `docs/methods/supply_and_trade.md` |

## The grid

| Tool | Route | The question it answers | Audience | Data |
|---|---|---|---|---|
| The network | `/network` (version 3 since session 168; `/network/v3` redirects to it) | Which balancing authorities trade power, and how much, hour by hour and on any day since 2019? | students and teachers | `eia930_all_interchange`, `grid_network_nodes`, `grid_network_links` (snapshot `site/data/grid_network.json`), `eia930_daily_interchange`, `eia930_daily_demand` (the replay, `site/public/network/`) |
| Grid conditions | `/grid` | What were yesterday's peak demand, forecast error and generation mix in each ISO? | everyone | `eia930_all_demand`, `eia930_all_generation` |
| Your grid (seven pages) | `/grid/ercot`, `/grid/caiso`, `/grid/pjm`, `/grid/nyiso`, `/grid/isone`, `/grid/miso`, `/grid/spp` | What is this grid, and what is it doing today? | students and teachers | `eia930_all_*`, ISO prices, `storage_capacity`, queues, news |
| Energy mix | `/mix` | What generates the power, by grid operator hourly and by state monthly? | everyone | `eia930_all_generation`, `eia930_generation_latest`, `state_generation_mix_monthly` |
| Curtailment | `/curtailment` | How much wind and solar output is curtailed, by ISO? | everyone | `caiso_curtailment_daily`, `spp_curtailment_daily`, `ercot_wind_solar_hsl_daily`, `iso_curtailment_monthly` |
| Emissions | `/emissions` | How much CO2 does each ISO's power carry, per MWh made and used? | everyone | `carbon_intensity_hourly`, `eia930_all_emissions` |
| Storage | `/storage` | Where is the US battery fleet, and how do batteries charge and discharge? | everyone | `storage_capacity`, `storage_daily_cycle`, `eia930_all_storage` |
| Who owns the batteries (in review, session 87) | `/storage/owners` | Which companies report the operating and planned battery storage of each US grid, how much, of what duration, and how much do the largest hold? | investors and lenders; researchers | `storage_owners_monthly` |
| Storage build-out (in review, session 72) | `/storage/buildout` | How much battery storage has each US grid built, of what duration, how does it compare with solar, and what is planned? | investors and lenders; everyone | `storage_buildout_monthly` |
| Consumption | `/consumption` | Who uses the power, and where is load growing fastest? | everyone | `eia_retail_sales_monthly`, `eia_sector_energy_consumption_monthly` |

## Projects, companies, deals and policy

| Tool | Route | The question it answers | Audience | Data |
|---|---|---|---|---|
| Project map | `/map` | Where are the generators, queue positions and datacenters? | investors and lenders | `energy_projects`, `datacenter_facilities` |
| Where the resources are (in review, session 146) | `/resources` | Where is the natural resource itself: wind, sun, geothermal heat, oil and gas basins and plays, hydropower, biomass and offshore wind areas, and how does what is built or planned sit on it? | investors and lenders; researchers | the resource layers of `docs/methods/resources.md` (files of the page, listed in `site/data/resources/manifest.json`); `eia860m_operating_generators`, `eia860m_planned_generators`, `energy_projects`, `datacenter_facilities` |
| Demand growth (in review, sessions 97 and 152) | `/demand` | How much more power does each grid use than in 2019, by year, month and hour of the day, and how much of that growth is left once the weather is taken out? | investors and lenders; researchers | `eia930_demand_growth` and `eia930_demand_weather` (the site's own copy for the weather view); methods in `docs/methods/demand_growth.md` and `docs/methods/demand_weather.md` |
| Datacenters | `/datacenters` | Which datacenters are being built, by whom, where and how large? | investors and lenders | `datacenter_facilities` |
| Thesis Builder (in review and internal, session 135) | `/thesis` | What does one niche look like to an investor: its scope, five trends, the companies those trends select, the deal funnel, the pipeline, capital, incumbents, risks and policy, every figure with its source? | the owner and invited investors | the internal table `thesis_runs` (never public); reads `energy_companies`, `energy_deals`, `policy_actions` |
| Companies (the Thesis Builder's output) | `/companies` | Which energy companies has the ERW mapped, at what stage and with what funding? | investors and lenders | `energy_companies` |
| Deals | `/deals` | Which PPAs, acquisitions and financings happened, with sources? | investors and lenders | `energy_deals` |
| Power contracts (in review, session 83; internal view only) | `/contracts` | Where are bilateral power contracts being signed: which seller, which buyer, what product, for how long, at what price as filed, delivered where? | investors and lenders | `ferc_eqr_contracts` (internal) |
| Policy | `/policy` | Which rules and notices matter, and what do they do? | investors and lenders; researchers | `policy_actions`, `policy_reads` |

## Events and studies

| Tool | Route | The question it answers | Audience | Data |
|---|---|---|---|---|
| Events (five pages) | `/events`, `/events/uri-2021`, `/events/covid-2020`, `/events/caiso-heat-2020`, `/events/elliott-2022`, `/events/ercot-heat-2023` | What happened to a grid in a major event, against the same days of earlier years, and how large was the effect, with and without the weather? | students and teachers; researchers | `event_window_daily`; the estimates of `event_study_estimates` computed on the page |

## Learning and play

| Tool | Route | The question it answers | Audience | Data |
|---|---|---|---|---|
| The tour | `/tour` | Where should a first-time visitor start? Five stops, about three minutes | everyone | links only |
| What is on a bill | `/learn/bill` | What does a home's electricity bill pay for, line by line, and how much of it is wholesale energy? Five utilities | students and teachers | `site/data/bill_rules.json` (tariffs), `cost_of_power_monthly` |
| Problem sets (five) | `/learn/problems`, `/learn/problems/know-your-grid`, `/learn/problems/prices-and-your-bill`, `/learn/problems/when-the-grid-broke`, `/learn/problems/storage-and-taxes`, `/learn/problems/networks-and-money` (session 55) | Five questions each, answered from the latest data | students and teachers | `eia930_all_*`, `storage_daily_cycle`, `carbon_intensity_daily`, `cost_of_power_*`, `event_window_daily`, `eia_fuel_spot_prices`, the network snapshot, `merchant_revenue_monthly` |
| Home battery game | `/play/battery` | Can you run a home battery through a real day of ERCOT prices better than perfect foresight would? | students and teachers; everyone | `iso_rtm_hub_prices`, `ercot_all_hub_prices_history`, `storage_capacity` |

## Practitioner tools

| Tool | Route | The question it answers | Audience | Data |
|---|---|---|---|---|
| Severance tax calculator | `/severance` | What state production tax is due on a month of oil, gas or condensate in Texas, Louisiana or New Mexico, and what reduced rates could apply? | investors and lenders | `site/data/severance_rules.json`, `eia_fuel_spot_prices` |
| Lease tool | `/severance/lease` | The same, for every well and month of a lease file, computed in the browser | investors and lenders | the same |
| What a battery saves a customer (in review, session 88) | `/battery/customer` | With my peak demand, my demand charge, my energy rates and a battery of this size, how much of the bill does shaving the peak and shifting energy save? | businesses with a demand charge; everyone | none: the reader's own numbers, worked out in the browser; nothing typed is sent or stored |

## News and analysis

| Tool | Route | The question it answers | Audience | Data |
|---|---|---|---|---|
| ERW's Energy Digest | `/digest`, `/digest/<date>` | What happened in energy today? | everyone | `news_index`, `docs/digest/` |
| ERW's Roundup | `/roundup`, `/roundup/<week>` | What happened this week, and what was the chart of the week? | everyone | `news_index`, `energy_deals`, `datacenter_projects`, `docs/roundup/` |
| Automated Analysis | `/analysis`, `/analysis/<week>` | What do the house chart templates show this week? | researchers | the price, EIA-930, curtailment, battery, trader view, deal and datacenter tables |
| Email | `/subscribe` | How do I get the digest and the Roundup by email? | everyone | Supabase subscribers (insert only) |

## Data and research

| Tool | Route | The question it answers | Audience | Data |
|---|---|---|---|---|
| Data and methods | `/data`, `/data/methods/<slug>`, `/data/standard` | What tables does the ERW hold, how is each built, and how do I read them in Python or on Redivis? | researchers | `catalogue`; `docs/methods/`; `docs/datastandard.md` |
| The event study notebook | `notebooks/event_study.ipynb` (GitHub), linked from `/data/methods/event_study` | Reproduce every event-study estimate from the `erw` package | researchers | `event_window_daily` |
| Ask the ERW | `/ask` | Ask the warehouse a question; every number in the answer comes from a table it read | researchers; everyone | the live set, four read-only tools |
| About, Terms | `/about`, `/terms` | What the ERW is, and what each source's license allows | everyone | `sources.csv` |
| Privacy | `/privacy` (session 177; in the footer, not in the menu) | What does the site record about a visit, and what does it not? | everyone | none (`docs/methods/usage_counts.md`) |

## Internal (behind a token, not in the nav)

| Page | Route | What it is |
|---|---|---|
| API costs | `/internal/costs` | the model spend ledger |
| Usage | `/internal/usage` (session 177) | how the tools are used, as counts by day, page and tool: no cookie, no address (`docs/methods/usage_counts.md`) |
| The internal view's door | `/internal/open` (session 177) | a form that opens the internal view with the token in the request's body, not in an address (`docs/release-gate.md`) |
| The shape premium report (draft) | `/reports/draft/shape-premium` | deep-dive report 1, a draft |
| Load a real lease | `/severance/lease/real` | the lease tool on the RRC's internal production data |
