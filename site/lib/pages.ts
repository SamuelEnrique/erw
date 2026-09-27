// Energy Research Warehouse (ERW) site: every page, once (session 20). The top nav (six groups),
// the home page's Explore grid, /about and /data all read this list, so a page added here is
// reachable and described everywhere, and a page missing here is missing everywhere.

export type Page = { href: string; label: string; line: string; tables: string };
export type Group = { label: string; pages: Page[] };

export const GROUPS: Group[] = [
  {
    label: "Prices",
    pages: [
      { href: "/markets", label: "Markets", line: "Day-ahead against real-time by hub: spreads, on-peak prices, heat rates, volatility and the week's top intervals.", tables: "<iso>_trader_daily, iso_rt_top_intervals" },
      { href: "/prices", label: "Prices", line: "Every public ISO hub and zone, real-time and day-ahead, with Henry Hub, WTI and Brent.", tables: "ISO price tables, eia_fuel_spot_prices, latest_prices" },
      { href: "/explorer/ercot-peak-premium", label: "ERCOT peak premium", line: "How ERCOT real-time prices spread across the day, by hub and year since 2015.", tables: "ercot_peak_premium_annual, ercot_peak_premium_monthly" },
    ],
  },
  {
    label: "Grid",
    pages: [
      { href: "/grid", label: "Grid conditions", line: "Yesterday's peak demand, forecast error and generation mix for each ISO and the Lower 48.", tables: "eia930_<ba>_demand, eia930_<ba>_generation" },
      { href: "/mix", label: "Energy mix", line: "What generates the power: hourly by grid operator, and monthly by state since 2001.", tables: "eia930_<ba>_generation, eia930_generation_latest, state_generation_mix_monthly" },
      { href: "/curtailment", label: "Curtailment", line: "Wind and solar output curtailed, by ISO, daily and monthly, and what each ISO's figure means.", tables: "caiso_curtailment_daily, spp_curtailment_daily, ercot_wind_solar_hsl_daily, iso_curtailment_monthly" },
      { href: "/consumption", label: "Consumption", line: "Electricity sold by state and sector, and where industrial and commercial load grows fastest.", tables: "eia_retail_sales_monthly, eia_sector_energy_consumption_monthly" },
    ],
  },
  {
    label: "Projects",
    pages: [
      { href: "/map", label: "Project map", line: "Every EIA generator and ISO queue position on one US map, with filters.", tables: "energy_projects, datacenter_projects" },
      { href: "/datacenters", label: "Datacenters", line: "Datacenter facilities named in the news: operator, place, MW, status and power.", tables: "datacenter_projects" },
      { href: "/deals", label: "Deals", line: "PPAs, acquisitions, financings and supply deals from the news, with sources.", tables: "energy_deals" },
    ],
  },
  {
    label: "News",
    pages: [
      { href: "/digest", label: "Energy Digest", line: "The day's energy news, scored and ranked, with the day's numbers from the warehouse.", tables: "news_index; docs/digest/" },
      { href: "/weekly", label: "Energy Week", line: "Monday's brief: the five stories of the week, its deals and datacenters, and the week's numbers.", tables: "news_index, energy_deals, datacenter_projects; docs/weekly/" },
      { href: "/subscribe", label: "Email", line: "The digest and Energy Week by email: what it is and how to sign up.", tables: "Supabase subscribers (insert only)" },
    ],
  },
  {
    label: "Data",
    pages: [
      { href: "/data", label: "Data and methods", line: "Every public table with its dates, rows, source and license; the data standard and the methods.", tables: "catalogue" },
      { href: "/ask", label: "Ask", line: "Ask the warehouse a question; every number in the answer comes from a table it read.", tables: "the live set, through four read-only tools" },
    ],
  },
  {
    label: "About",
    pages: [{ href: "/about", label: "About", line: "What the ERW is, how it is built, and where the code and session logs are.", tables: "" }],
  },
];

export const PAGES: Page[] = GROUPS.flatMap((g) => g.pages);
