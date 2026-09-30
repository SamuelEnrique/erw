// Energy Research Warehouse (ERW) site: every page, once (session 20). The top nav (six groups),
// the home page's Explore grid, /about and /data all read this list, so a page added here is
// reachable and described everywhere, and a page missing here is missing everywhere.

// related (session 21): the pages a data page's closing "Related" line links
export type Page = { href: string; label: string; line: string; tables: string; related?: string[] };
// session 35: sub, a line of short links under a group's pages (the Grid menu's "Your grid": the seven grid pages)
export type Group = { label: string; pages: Page[]; sub?: { label: string; links: { href: string; label: string }[] } };

// session 35: the seven grid pages (/grid/<slug>, docs/grids/grids.json), in the nav's Grid menu
export const YOUR_GRID = [
  { href: "/grid/ercot", label: "ERCOT" }, { href: "/grid/caiso", label: "CAISO" }, { href: "/grid/pjm", label: "PJM" },
  { href: "/grid/nyiso", label: "NYISO" }, { href: "/grid/isone", label: "ISO-NE" }, { href: "/grid/miso", label: "MISO" },
  { href: "/grid/spp", label: "SPP" },
];

export const GROUPS: Group[] = [
  {
    label: "Prices",
    pages: [
      // session 30: price board v2, the demo's page
      { href: "/board", label: "Price board", line: "The six ISOs' main hubs on one screen: day-ahead and real-time, moves, peak and off-peak, spark spreads, Henry Hub, Brent minus WTI, and ERCOT since 2015.", tables: "price_board_latest, price_board_peak_offpeak, price_board_spreads, price_board_carbon", related: ["/prices", "/markets"] },
      { href: "/markets", label: "Markets", line: "Day-ahead against real-time by hub: spreads, on-peak prices, heat rates, volatility and the week's top intervals.", tables: "iso_trader_daily, iso_rt_top_intervals", related: ["/prices", "/grid"] },
      // session 37: the cost-of-power model (platform tool 16), under Markets
      { href: "/cost-of-power", label: "Cost of power", line: "What a MWh costs to buy at each ISO's main hub, weighted by when the grid uses it; when power is cheap by hour of day; cost against carbon; and what a large load pays for energy.", tables: "cost_of_power_monthly, cost_of_power_hourly_profile, cost_of_power_carbon", related: ["/board", "/datacenters"] },
      { href: "/prices", label: "Prices", line: "Every public ISO hub and zone, real-time and day-ahead, with Henry Hub, WTI and Brent.", tables: "ISO price tables, eia_fuel_spot_prices, latest_prices", related: ["/markets", "/explorer/ercot-peak-premium"] },
      { href: "/explorer/ercot-peak-premium", label: "ERCOT peak premium", line: "How ERCOT real-time prices spread across the day, by hub and year since 2015.", tables: "ercot_peak_premium_annual, ercot_peak_premium_monthly", related: ["/prices", "/markets"] },
    ],
  },
  {
    label: "Grid",
    pages: [
      { href: "/grid", label: "Grid conditions", line: "Yesterday's peak demand, forecast error and generation mix for each ISO and the Lower 48.", tables: "eia930_all_demand, eia930_all_generation", related: ["/mix", "/curtailment"] },
      { href: "/mix", label: "Energy mix", line: "What generates the power: hourly by grid operator, and monthly by state since 2001.", tables: "eia930_all_generation, eia930_generation_latest, state_generation_mix_monthly", related: ["/grid", "/curtailment"] },
      { href: "/curtailment", label: "Curtailment", line: "Wind and solar output curtailed, by ISO, daily and monthly, and what each ISO's figure means.", tables: "caiso_curtailment_daily, spp_curtailment_daily, ercot_wind_solar_hsl_daily, iso_curtailment_monthly", related: ["/mix", "/grid"] },
      // session 32: emissions
      { href: "/emissions", label: "Emissions", line: "How much CO2 each ISO's power carries, per MWh made and per MWh used, from EIA's hourly estimates.", tables: "carbon_intensity_hourly, eia930_all_emissions", related: ["/grid", "/storage"] },
      // session 31: battery storage
      { href: "/storage", label: "Storage", line: "The US battery fleet by ISO, state and planned year, and how the batteries charge and discharge each hour and day.", tables: "storage_capacity, storage_daily_cycle, eia930_all_storage", related: ["/grid", "/mix"] },
      { href: "/consumption", label: "Consumption", line: "Electricity sold by state and sector, and where industrial and commercial load grows fastest.", tables: "eia_retail_sales_monthly, eia_sector_energy_consumption_monthly", related: ["/mix", "/datacenters"] },
    ],
    sub: { label: "Your grid", links: YOUR_GRID },
  },
  {
    label: "Projects",
    pages: [
      { href: "/map", label: "Project map", line: "Every EIA generator and ISO queue position on one US map, with filters.", tables: "energy_projects, datacenter_facilities", related: ["/datacenters", "/deals"] },
      { href: "/datacenters", label: "Datacenters", line: "Datacenter facilities from the news, nine operators' site lists and the ISO queues: operator, place, MW, status.", tables: "datacenter_facilities", related: ["/map", "/deals"] },
      { href: "/companies", label: "Companies", line: "Energy companies the ERW has found and sourced: stage, raised, location, founders and a confidence score, from Thesis Builder runs and the parties of the deal tracker.", tables: "energy_companies", related: ["/deals", "/datacenters"] },
      { href: "/policy", label: "Policy", line: "Energy rules, proposed rules and notices from the Federal Register and agency news, scored, with impact reads of the significant ones.", tables: "policy_actions, policy_reads", related: ["/digest", "/deals"] },
      { href: "/deals", label: "Deals", line: "PPAs, acquisitions, financings and supply deals from the news, with sources.", tables: "energy_deals", related: ["/companies", "/datacenters"] },
    ],
  },
  {
    // session 36B: the Historical Event Analyzer
    label: "Events",
    pages: [
      { href: "/events", label: "Events", line: "What happened to a grid during a major event, day by day, against the same days of earlier years: Winter Storm Uri, COVID-19 in the seven ISO grids, the August 2020 heat in CAISO, Winter Storm Elliott and the summer 2023 heat in ERCOT.", tables: "event_window_daily", related: ["/grid/ercot", "/emissions"] },
    ],
  },
  {
    // session 43: learning pages (the bill explainer), with the seven grid pages and the events
    label: "Learn",
    pages: [
      // session 44: the problem sets
      { href: "/learn/problems/know-your-grid", label: "Problems: know your grid", line: "Five questions on ERCOT and CAISO side by side: peak demand, generation mix, batteries and carbon intensity, answered from the latest data.", tables: "eia930_all_demand, eia930_all_generation, storage_daily_cycle, carbon_intensity_daily", related: ["/learn/problems", "/grid/ercot"] },
      { href: "/learn/problems/prices-and-your-bill", label: "Problems: prices and your bill", line: "Five questions on load-weighted prices, the shape premium, the wholesale share of two bills and the daily price swing.", tables: "cost_of_power_monthly, cost_of_power_hourly_profile; site/data/bill_rules.json", related: ["/learn/problems", "/cost-of-power"] },
      { href: "/learn/problems/when-the-grid-broke", label: "Problems: when the grid broke", line: "Five questions on Uri, CAISO's 2020 heat, Elliott and ERCOT's 2023 heat, answered from the event windows.", tables: "event_window_daily", related: ["/learn/problems", "/events"] },
      { href: "/learn/bill", label: "What is on a bill", line: "Two real electricity bills built line by line from the tariffs, PG&E in California and Oncor in Texas, and how much of each is the wholesale price of energy.", tables: "site/data/bill_rules.json; cost_of_power_monthly", related: ["/cost-of-power", "/grid/ercot"] },
    ],
    sub: { label: "Grids and events", links: [...YOUR_GRID, { href: "/events", label: "Events" }] },
  },
  {
    // session 40: tools for a practitioner
    label: "Tools",
    pages: [
      { href: "/severance", label: "Severance tax", line: "State production taxes on a month of oil, gas or condensate in Texas, Louisiana and New Mexico: the base rate, the reduced rates and exemptions, and the savings, each rule cited.", tables: "site/data/severance_rules.json; eia_fuel_spot_prices (default prices)", related: ["/prices", "/cost-of-power"] },
    ],
  },
  {
    // session 38: the home battery game
    label: "Play",
    pages: [
      { href: "/play/battery", label: "Home battery game", line: "Run a home battery through a real day of ERCOT prices: charge cheap, sell dear, answer the fleet call, and see what perfect foresight would have earned.", tables: "iso_rtm_hub_prices, ercot_all_hub_prices_history", related: ["/storage", "/grid/ercot"] },
    ],
  },
  {
    label: "News",
    pages: [
      { href: "/digest", label: "ERW's Energy Digest", line: "The weekday brief: the day's energy news, scored and ranked, the day's numbers from the warehouse, and a fun fact.", tables: "news_index; docs/digest/", related: ["/roundup", "/deals"] },
      { href: "/roundup", label: "ERW's Roundup", line: "Sunday's brief: the weekend's stories, the five stories of the week, its deals and datacenters, the week's numbers and the chart of the week.", tables: "news_index, energy_deals, datacenter_projects; docs/roundup/", related: ["/digest", "/analysis"] },
      { href: "/subscribe", label: "Email", line: "The digest and the Energy Roundup by email: what it is and how to sign up.", tables: "Supabase subscribers (insert only)" },
    ],
  },
  {
    label: "Data",
    pages: [
      { href: "/data", label: "Data and methods", line: "Every public table with its dates, rows, source and license; the data standard and the methods.", tables: "catalogue" },
      { href: "/analysis", label: "Automated Analysis", line: "Ten chart templates run on the warehouse every week, the chart of the week picked by rule, and a gallery to run each template with its parameters.", tables: "the ISO price, EIA-930, curtailment, battery, trader view, deal and datacenter tables; docs/analysis/", related: ["/roundup", "/markets"] },
      { href: "/ask", label: "Ask", line: "Ask the warehouse a question; every number in the answer comes from a table it read.", tables: "the live set, through four read-only tools" },
    ],
  },
  {
    label: "About",
    pages: [
      { href: "/about", label: "About", line: "What the ERW is, how the digest is made, the glossary, and where the code and session logs are.", tables: "" },
      { href: "/terms", label: "Terms", line: "Data licensing per source, what the site stores about subscribers and questions, and what it is not.", tables: "sources.csv" },
    ],
  },
];

export const PAGES: Page[] = GROUPS.flatMap((g) => g.pages);
