// Energy Research Warehouse (ERW) site, session 462 (chain 019 of 21 October 2026): the modelling choices each
// economics page makes, one line each, with the session that made it and the ruling where one exists. Drawn by
// components/tool/DecisionsBlock.tsx at the foot of the page, and listed in the page's step-by-step method note (the
// section "The decisions on the page"); tests/test_session462.py and test_session463.py hold the two to one list. Words
// only: nothing here is computed, and no figure of a page reads it. A choice is listed as the page makes it today; where
// a later session changed an earlier one, the later is named.
export type Decision = { key: string; text: string; session: string; ruling?: string };

/** /cost-of-power, "What a datacenter pays" (docs/methods/datacenter_pays_algorithm.md, section 12). */
export const DATACENTER_DECISIONS: Decision[] = [
  { key: "energy-only", session: "sessions 138 and 213",
    text: "The cost is wholesale energy alone at a hub or load zone, bought every hour at the hour's price with no hedge. No delivery, transmission, capacity, ancillary or retail charge is added to it; a reader adds one as a scenario's \"Delivery and other charges\"." },
  { key: "zone-not-site", session: "session 138",
    text: "A hub or load zone stands for the site: the price at one substation differs by congestion and losses, and no figure of the page is priced at a node." },
  { key: "months", session: "session 138",
    text: "A month counts when 95 percent of its hours are held; the last twelve months are the newest twelve counted months in a row, each grid and region on its own months." },
  { key: "bad-month", session: "sessions 138 and 190",
    text: "A bad month is the top tenth of the 36 months that end with the last twelve, by nearest rank: the mirror of the battery page's 10th percentile month." },
  { key: "standard-time", session: "session 138",
    text: "Months and years are counted in the grid's standard time, with no daylight saving shift." },
  { key: "flex-rule", session: "session 140", ruling: "the owner's ruling of 7 October 2026",
    text: "A flexible load follows a rule decided before each hour from the prior 30 days of day-ahead prices, within a budget of hours each calendar year; it turns off whole and at once, with no minimum run." },
  { key: "foreseen", session: "session 138",
    text: "\"If perfectly foreseen\" chooses the same budget of hours knowing the year's prices, pro-rated in a year held in part (section 10, item 15, waits for a ruling)." },
  { key: "gpu-pue", session: "sessions 138 and 195",
    text: "Power per GPU defaults to 1.3 kW (NVIDIA's DGX H100) and the overhead ratio to 1.56 (Uptime Institute, 2024); both are scenario A's assumptions since session 195." },
  { key: "questions", session: "sessions 213 and 228",
    text: "One page in the battery page's layout: what it will pay, whether the power is there, how clean it is and how soon it can be had, each computed for the load described, then the two scenarios and what matters most." },
  { key: "scenarios", session: "sessions 194, 195 and 213",
    text: "Scenarios A and B are the block the three economics pages share; scenario A sets the headline. The contract's share and price are two of each scenario's assumptions, 0 by default, so the default load is fully merchant." },
  { key: "hurdle", session: "sessions 196 and 265", ruling: "the owner's rulings of 11 October 2026, and 7a of 18 October 2026",
    text: "The cost of capital defaults to 9.6 percent, Lazard's weighted cost of a power plant's builder (60 percent debt at 8 percent, 40 percent equity at 12), labelled as a generator's, since no datacenter owner's rate is held." },
  { key: "years-and-zeros", session: "session 194",
    text: "Twenty years are counted, and the other charges, the change of prices and the upfront cost default to none: no cited figure is held for any of them." },
  { key: "scarcity", session: "session 236", ruling: "the owner's ruling of 12 October 2026",
    text: "The scarcity level is USD 1,000 per MWh on every grid, said beside the count, with a grid's own scarcity signal as a second count where a table of it is held." },
  { key: "delivery", session: "sessions 236 and 265", ruling: "ruling 1a of 18 October 2026",
    text: "Texas's delivery charges stand in their own table, one row a component, never added to the market cost; a line billed per kVA or per meter is marked conditional and left out of the first total." },
  { key: "bounds", session: "session 265", ruling: "ruling 8a of 18 October 2026",
    text: "A value typed outside its bounds is brought to the nearest bound, and a line says so." },
  { key: "runs-little", session: "session 298", ruling: "ruling 5c of 18 October 2026",
    text: "A load that runs in fewer than one in ten of the hours held is said so under the headline." },
  { key: "statements", session: "session 265", ruling: "the owner's ruling of 14 October 2026",
    text: "The public statements on large loads are facts with a link to the document, with no quoted text." },
  { key: "price-years", session: "session 352",
    text: "The scenarios are priced on the page's own last twelve months by default; another window is read from price_years_by_window, and a window a table does not hold is said, never computed." },
  { key: "four-peaks", session: "session 354",
    text: "ERCOT's four summer peaks are shown for the flexible way and not counted by default, at the Commission's newest approved transmission rate and the newest summer held." },
  { key: "node-band", session: "session 354",
    text: "A node's band (the resource nodes' day-ahead basis to the hub) is shown under the cost table and added to no figure: a load settles at its load zone." },
  { key: "capacity", session: "session 354",
    text: "Capacity charges: none in ERCOT, an energy-only market; elsewhere \"no public figure\", because the auction results are held only in an internal table." },
];
