// Energy Research Warehouse (ERW) site: every page, once (session 20). The top nav (six groups),
// the home page's Explore grid, /about and /data all read this list, so a page added here is
// reachable and described everywhere, and a page missing here is missing everywhere.
// Session 53: no menu holds more than eight entries (a test checks it): the seven grid pages are their own menu, "Your
// grid", instead of a sub-list under Grid and Learn; the battery game joins Learn, beside the tour; the seller's tab of
// the cost of power and the lease tool are listed. docs/tools.md is the inventory these lines follow.

// related (session 21): the pages a data page's closing "Related" line links
// session 203: menu, the name the top menu shows where it is shorter than the page's own ("Batteries" for "What a
// battery earns"); every other reader of this list (the About page, the Related lines, /data) keeps the page's own name
export type Page = { href: string; label: string; line: string; tables: string; related?: string[]; menu?: string };
// session 35: sub, a line of short links under a group's pages (the Grid menu's "Your grid": the seven grid pages).
// session 203: sub holds pages like any other (they are in PAGES below); a sub-group is a short list under its own
// name (Economics: "Infrastructure Economics"), or with inline a line of short links (Grid: "Your grid"). aside: the
// group is not a menu; its pages are plain links at the right of the header, in grey (News).
export type Group = { label: string; pages: Page[]; sub?: { label: string; pages: Page[]; inline?: boolean }; aside?: boolean };

// session 35: the seven grid pages (/grid/<slug>, docs/grids/grids.json), in the nav's Grid menu
export const YOUR_GRID = [
  { href: "/grid/ercot", label: "ERCOT" }, { href: "/grid/caiso", label: "CAISO" }, { href: "/grid/pjm", label: "PJM" },
  { href: "/grid/nyiso", label: "NYISO" }, { href: "/grid/isone", label: "ISO-NE" }, { href: "/grid/miso", label: "MISO" },
  { href: "/grid/spp", label: "SPP" },
];

// Session 203 (the roadmap's ruling of 12 October 2026, docs/roadmap.md): the menu is Economics (with the sub-group
// Infrastructure Economics), Grid, Infrastructure, Analysis, Games, About, and at the right in grey Energy Digest,
// Roundup, Email. Every page keeps its address, its line and its tables; only the groups and the menu's names changed.
// Where the ruling names no place for a page, the place is this session's choice and is listed in its report.
// The menus until session 203 were Prices, Grid, Your grid, Projects, Events, Learn, Tools, News, Data and About. Their own notes:
//   Your grid: session 53: the seven grid pages, their own menu (they were a sub-list under Grid and Learn)
//   Events: session 36B: the Historical Event Analyzer
//   Learn: session 43: learning pages (the bill explainer), with the seven grid pages and the events
//   Tools: session 40: tools for a practitioner
export const GROUPS: Group[] = [
  {
    // session 203: what energy costs and earns. Until then: Prices (the board, prices, supply, the cost of power and its tabs), with the two severance
    // tools from Tools, the bill from Learn and the power contracts from Projects. Its sub-group is the ruling's own list, in its order
    label: "Economics",
    pages: [
      // session 30: price board v2, the demo's page
      { href: "/board", label: "Price board", line: "Every price held on one dense screen: power by hub and zone, gas, crude, products, retail fuel and electricity, coal, metals, rates and credits, each with its moves, trend and one-year range, the spreads, and a workbench to compare any two series.", tables: "the ISO price tables, eia_fuel_spot_prices, eia_product_spot_prices and the tables of docs/methods/price_board.md", related: ["/prices", "/supply"] },
      // session 239: one page, two tabs (lib/tabs.ts): every hub and zone, and ERCOT (the peak premium explorer, until then its own entry "ERCOT peak premium" at /explorer/ercot-peak-premium, which redirects to the tab)
      { href: "/prices", label: "Prices", line: "Every public ISO hub and zone, real-time and day-ahead, with Henry Hub, WTI and Brent; and, on the ERCOT tab, how ERCOT real-time prices spread across the day, by hub and year since 2015.", tables: "ISO price tables, eia_fuel_spot_prices, latest_prices, ercot_peak_premium_annual, ercot_peak_premium_monthly", related: ["/board", "/supply"] },
      // session 37: the cost-of-power model (platform tool 16), under Markets
      // session 134: supply and trade, for a trader in oil, gas and power
      { href: "/supply", label: "Supply and trade", line: "Is the market tighter or looser than last week, last year and normal for the season: gas storage, crude and product stocks, production, refining, trade, fuel burned for power and positioning, each against its five-year range.", tables: "eia_gas_storage_weekly, eia_petroleum_supply_weekly, eia_gas_trade_monthly, eia_basin_production_monthly, cftc_cot_positions", related: ["/board", "/grid"] },
      // session 83: FERC's Electric Quarterly Report contracts, an internal table behind the internal view (in review)
      { href: "/contracts", label: "Power contracts", line: "Where bilateral power contracts are being signed: seller, buyer, product, term, price as filed and delivery point, by the quarter of signing, from the contracts sellers file with FERC.", tables: "ferc_eqr_contracts (internal)", related: ["/deals", "/cost-of-power/seller"] },
      // session 239: one page, two tabs (lib/tabs.ts): the calculator and the lease tool (until then its own entry "Lease tool" at /severance/lease, which redirects to the tab)
      { href: "/severance", label: "Severance tax", line: "State production taxes on a month of oil, gas or condensate in Texas, Louisiana and New Mexico: the base rate, the reduced rates and exemptions, and the savings, each rule cited; and, on the Lease tab, the same calculator for every well and month of a lease file, computed in the browser: nothing is sent.", tables: "site/data/severance_rules.json; eia_fuel_spot_prices (default prices)", related: ["/prices", "/cost-of-power"] },
    ],
    sub: {
      label: "Infrastructure Economics",
      pages: [
        { href: "/cost-of-power/battery", label: "What a battery earns", line: "What a grid battery of your size and duration earned in ERCOT and CAISO from energy and ancillary services together, by year and by stream, and whether it covers its debt, with and without a contract.", tables: "battery_stack_monthly, battery_stack_stress_daily", related: ["/cost-of-power/seller", "/storage"], menu: "Batteries" },
        // session 51: the seller's tab
        { href: "/cost-of-power/seller", label: "What a generator earns", line: "What a merchant solar, wind, battery or gas peaker asset earns month by month at an ISO's main hub, its bad months and stress days, and whether it covers its debt.", tables: "merchant_revenue_monthly", related: ["/cost-of-power", "/board"], menu: "Generators" },
        { href: "/cost-of-power", label: "Cost of power", line: "What a MWh costs to buy at each ISO's main hub, weighted by when the grid uses it; when power is cheap by hour of day; cost against carbon; and what a large load pays for energy.", tables: "cost_of_power_monthly, cost_of_power_hourly_profile, cost_of_power_carbon", related: ["/board", "/datacenters"], menu: "Datacenters" },
        // session 53: the lease tool, listed (session 45)
        // session 88: a calculator on the reader's own bill; no ERW table is read, and nothing typed leaves the browser (in review)
        { href: "/battery/customer", label: "What a battery saves a customer", line: "Type your peak demand, your demand charge, your energy rates and a battery's size: the bill saved by shaving the peak and shifting energy. Your own numbers, worked out in your browser; nothing is sent.", tables: "", related: ["/cost-of-power/battery", "/learn/bill"] },
        // session 67: the battery revenue stack, next to the seller's tab
        // session 75: in review
        { href: "/shoulder", label: "The shoulder hours", line: "How long the evening stretch between the solar midday and the demand peak lasts in ERCOT and CAISO, how much of it today's batteries cover, and how many hours they would need.", tables: "shoulder_hours_monthly", related: ["/cost-of-power/battery", "/storage"] },
      ],
    },
  },
  {
    // session 203: the grid as it runs. Storage moved to Infrastructure; Consumption came back from Data (session 159 had moved it there)
    label: "Grid",
    pages: [
      // session 237 (the roadmap's item 2): the Grid tool, one page. It stands in the menu in place of the pages that
      // redirect into it (next.config.ts): "The network" (/network, session 49), "Grid conditions" (what /grid was),
      // "Energy mix" (/mix), "Emissions" (/emissions, session 32) and the seven grid pages of "Your grid" (/grid/<iso>,
      // session 35). Their lines and tables are in this one entry.
      { href: "/grid", label: "The grid", line: "One grid at a time (ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, SPP or the Lower 48): what it is doing now, the network of balancing authorities and the power they trade, the energy mix now and since 2001, how much CO2 the power carries, its exchange with its neighbours, and a question box.", tables: "eia930_all_demand, eia930_all_generation, eia930_all_interchange, carbon_intensity_hourly, carbon_intensity_monthly, eia930_generation_latest, state_generation_mix_monthly, generation_mix_hourly_profile, clean_energy_summary, grid_stress_yearly, ba_supply_monthly, grid_network_nodes, grid_network_links and, for a grid's own blocks, the ISO price tables, storage_capacity, the interconnection queues and news_index", related: ["/demand", "/curtailment"] },
      // session 159 (the owner's instruction of 8 October 2026): demand growth, one page with two views (as metered, and with the weather taken out; sessions 97 and 152), in review. The Grid menu holds eight with it: Consumption moved to Data
      // session 239: a third view, Consumption (until then its own entry at /consumption, which redirects to the view)
      { href: "/demand", label: "Demand growth", line: "How much more power each grid uses than in 2019, by year, month and hour of the day, and the same growth with the weather taken out; and, on the Consumption tab, electricity sold by state and sector, and where industrial and commercial load grows fastest.", tables: "eia930_demand_growth, eia930_demand_weather, eia_retail_sales_monthly, eia_sector_energy_consumption_monthly", related: ["/grid"] },
      { href: "/curtailment", label: "Curtailment", line: "Wind and solar output curtailed, by grid, by day, month and hour, as a share of available output; where power is priced under USD 5 per MWh, by hub and zone; and what the curtailed energy was worth to a load or a battery.", tables: "caiso_curtailment_daily, spp_curtailment_daily, ercot_wind_solar_hsl_daily, iso_curtailment_monthly, caiso_curtailment_profile, ercot_wind_solar_hsl_hourly and the hub and zone price tables", related: ["/grid"] },
    ],
    // session 53 gave the seven grid pages a menu of their own, "Your grid"; session 203: they were the Grid menu's line
    // of short links again (session 35). Session 237: the seven are the Grid tool's picker, so the menu has no such line
  },
  {
    // session 203: what is built, where and by whom. Until then: Projects, and the three storage pages of Grid. The datacenter page is
    // renamed "Datacenter tracker" (the roadmap's ruling of 12 October 2026): "Datacenters" is the cost-of-power page's name in Economics now
    label: "Infrastructure",
    pages: [
      // session 239: one page, two tabs (lib/tabs.ts): the projects, and the resources (session 146: the natural resource itself; until then its own entry "Where the resources are" at /resources, which redirects to the tab)
      { href: "/map", label: "Project map", line: "Every EIA generator and ISO queue position on one US map, with filters; and, on the Resources tab, the natural resource itself: wind, sun, geothermal heat, oil and gas basins and plays, hydropower, biomass and offshore wind areas, each from its publisher at its own grain, with the plants, the queue and the datacenters laid over it.", tables: "energy_projects, datacenter_facilities; the resource layers of docs/methods/resources.md; eia860m_operating_generators, eia860m_planned_generators", related: ["/datacenters", "/deals"] },
      { href: "/datacenters", label: "Datacenter tracker", line: "Datacenter facilities from the news, nine operators' site lists and the ISO queues: operator, place, MW, status.", tables: "datacenter_facilities", related: ["/map", "/deals"] },
      // session 31: battery storage
      // session 239: one page, three tabs (lib/tabs.ts): the fleet, the build-out (session 72: until then its own entry "Storage build-out" at /storage/buildout) and the owners (session 87: "Who owns the batteries" at /storage/owners); both addresses redirect to their tabs
      { href: "/storage", label: "Storage", line: "The US battery fleet by ISO, state and planned year, and how the batteries charge and discharge each hour and day; on the build-out tab, how much battery storage each US grid has built, of what duration, how it compares with solar, and what is planned; on the owners tab, operating and planned storage by the company that reports each plant: MW, MWh, average duration, and the largest owners.", tables: "storage_capacity, storage_daily_cycle, eia930_all_storage, storage_buildout_monthly, storage_owners_monthly", related: ["/cost-of-power/battery", "/grid"] },
      // session 239: one page, three tabs (lib/tabs.ts): the deals, the tracker (session 113: /deals/v2) and the companies (session 26: until then its own entry "Companies" at /companies); both addresses redirect to their tabs, and a company is a filter of the tracker
      { href: "/deals", label: "Deals", line: "PPAs, acquisitions, financings and supply deals from the news, with sources: as a sortable table, and on the tracker by type, technology, grid, counterparty and year; and, on the Companies tab, the energy companies the ERW has found and sourced: stage, raised, location, founders and a confidence score, from Thesis Builder runs and the parties of the deals.", tables: "energy_deals, energy_companies", related: ["/datacenters", "/map"] },
    ],
  },
  {
    // session 203: Automated Analysis and Ask (from Data), the event studies (their own menu since session 36B), Policy (from Projects), Thesis
    // Builder (from Tools)
    label: "Analysis",
    pages: [
      { href: "/research", label: "Research", line: "Ask for an analysis, today's chart and this week's, and the findings library: one card a screen, by grid and topic, each with its data, its Stata do-file and its Python file.", tables: "the ISO price, EIA-930, curtailment, battery, trader view, deal and datacenter tables; docs/analysis/", related: ["/roundup", "/board"] },
      { href: "/ask", label: "Ask", line: "Ask the warehouse a question; every number in the answer comes from a table it read.", tables: "the live set, through four read-only tools" },
      { href: "/events", label: "Events", line: "What happened to a grid during a major event, day by day, against the same days of earlier years: Winter Storm Uri, COVID-19 in the seven ISO grids, the August 2020 heat in CAISO, Winter Storm Elliott and the summer 2023 heat in ERCOT.", tables: "event_window_daily", related: ["/grid"] },
      { href: "/policy", label: "Policy", line: "Energy rules, proposed rules and notices from the Federal Register and agency news, scored, with impact reads of the significant ones.", tables: "policy_actions, policy_reads", related: ["/digest", "/deals"] },
      // session 135: Thesis Builder as a tool of the site (in review, and internal: the page answers only the internal view). Session 146: moved here from Projects, which holds eight with "Where the resources are"
      { href: "/thesis", label: "Thesis Builder", line: "Type a niche and get a sourced investment map of it: scope and definitions, trends, the company landscape, the deal funnel, the pipeline, capital, incumbents, risks and policy, every figure with its source.", tables: "thesis_runs (internal)", related: ["/deals", "/policy"] },
    ],
  },
  {
    // session 203: the battery game, the tour and the problem sets. Until then: Learn (session 43)
    // Session 288 (Samuel's ruling 14 of 14 October 2026): the menu is the battery game, the tour, the bill explainer (from
    // Economics) and "Problem sets", the index of all five sets (until then four of the five were listed one by one and
    // the index not at all; each set is reached from the index). The EV game joins it on the games branch (session 294).
    label: "Games",
    pages: [
      // session 53: the battery game joins Learn (it was its own "Play" group)
      { href: "/play/battery", label: "Home battery game", line: "Run a home battery through a real day of ERCOT prices: charge cheap, sell dear, answer the fleet call, and see what perfect foresight would have earned.", tables: "iso_rtm_hub_prices, ercot_all_hub_prices_history", related: ["/storage", "/grid"] },
      // session 53: the guided tour, first
      // session 292 (ruling 11a): a guided path of seven stops
      { href: "/tour", label: "The tour", line: "Seven stops for a first visit, about five minutes, one page each with Back and Next: the three tools, the grid, research, the price board and the digest.", tables: "" },
      // session 43: the bill explainer (in Economics from session 203 to session 288)
      { href: "/learn/bill", label: "What is on a bill", line: "Five real electricity bills built line by line from the tariffs (PG&E, SCE and SDG&E in California; Oncor and CenterPoint in Texas), and how much of each is the wholesale price of energy.", tables: "site/data/bill_rules.json; cost_of_power_monthly", related: ["/learn/problems/prices-and-your-bill", "/cost-of-power"] },
      // session 44: the problem sets; session 288: one entry, the index of the five
      { href: "/learn/problems", label: "Problem sets", line: "Five sets of five questions for a class: know your grid; prices and your bill; when the grid broke; storage and taxes; networks and money. Each answer is worked from the warehouse's tables.", tables: "eia930_all_demand, eia930_all_generation, storage_daily_cycle, carbon_intensity_daily, cost_of_power_monthly, cost_of_power_hourly_profile, event_window_daily, eia_fuel_spot_prices, eia930_all_interchange, merchant_revenue_monthly; site/data/bill_rules.json, site/data/severance_rules.json", related: ["/learn/bill", "/grid"] },
      // session 294 (Samuel's rulings 14 and 17): the EV game, the menu's fifth entry
      { href: "/play/ev", label: "Should your family get an EV?", line: "For a middle-schooler and their parents: what driving costs in your state on gasoline and on electricity, payback and net present value, and every number with its source, ready to print.", tables: "eia_retail_electricity_prices, eia_regional_retail_fuel_prices (site/data/ev_prices.json)", related: ["/play/battery", "/learn/bill"], menu: "The EV game" },
    ],
  },
  {
    // session 203: Data and methods, About, Terms (the ruling's three, in its order)
    label: "About",
    pages: [
      { href: "/data", label: "Data and methods", line: "Every public table with its dates, rows, source and license; the data standard and the methods.", tables: "catalogue" },
      { href: "/about", label: "About", line: "What the ERW is, how the digest is made, the glossary, and where the code and session logs are.", tables: "" },
      { href: "/terms", label: "Terms", line: "Data licensing per source, what the site stores about subscribers and questions, and what it is not.", tables: "sources.csv" },
    ],
  },
  {
    // session 203: not a menu. The three are drawn at the right of the header, in grey (aside: components/Nav.tsx)
    label: "News",
    pages: [
      { href: "/digest", label: "ERW's Energy Digest", line: "The weekday brief: the day's energy news, scored and ranked, the day's numbers from the warehouse, and a fun fact.", tables: "news_index; docs/digest/", related: ["/roundup", "/deals"], menu: "Energy Digest" },
      { href: "/roundup", label: "ERW's Roundup", line: "Sunday's brief: the weekend's stories, the five stories of the week, its deals and datacenters, the week's numbers and the chart of the week.", tables: "news_index, energy_deals, datacenter_projects; docs/roundup/", related: ["/digest", "/research"], menu: "Roundup" },
      { href: "/subscribe", label: "Email", line: "The digest and the Energy Roundup by email: what it is and how to sign up.", tables: "Supabase subscribers (insert only)" },
    ],
    aside: true,
  },
];

// session 203: a sub-group's pages are pages too
export const PAGES: Page[] = GROUPS.flatMap((g) => [...g.pages, ...(g.sub?.pages ?? [])]);
