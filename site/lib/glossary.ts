// Energy Research Warehouse (ERW) site: the acronyms the pages use (session 21). /about renders
// this list as its glossary; components/Term.tsx gives each use a hover title and links a page's
// first use to its entry.
export const GLOSSARY: Record<string, string> = {
  ISO: "Independent system operator: the organization that runs a region's power grid and wholesale electricity market.",
  ERCOT: "Electric Reliability Council of Texas: the ISO for most of Texas.",
  CAISO: "California Independent System Operator: the ISO for most of California.",
  NYISO: "New York Independent System Operator: the ISO for New York State.",
  MISO: "Midcontinent Independent System Operator: the ISO for 15 states from Minnesota to Louisiana.",
  SPP: "Southwest Power Pool: the ISO for the central plains, from North Dakota to Oklahoma and the Texas Panhandle.",
  "ISO-NE": "ISO New England: the ISO for the six New England states.",
  PJM: "PJM Interconnection: the ISO for 13 mid-Atlantic and Midwest states and DC. The ERW has no licensed PJM price data.",
  EIA: "U.S. Energy Information Administration: the federal statistics agency for energy; most ERW tables come from it.",
  DAM: "Day-ahead market: the auction, held the day before, that sets an hourly price for each hour of the next day.",
  RTM: "Real-time market: the market that balances the grid as it runs, with a price every 5 or 15 minutes.",
  LMP: "Locational marginal price: the price of one more MWh of power at one place on the grid, in USD/MWh.",
  HSL: "High Sustained Limit: the output a wind or solar resource reports it could sustain, given the weather, in ERCOT's data.",
  PADD: "Petroleum Administration for Defense District: one of the five regions EIA uses for oil statistics.",
  RPM: "Reliability Pricing Model: PJM's capacity market, which pays for power plants to be available years ahead.",
};

export const glossaryId = (term: string) => `glossary-${term.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
