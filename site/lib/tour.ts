// Session 53: the guided tour's stops (/tour), also linked from the home page. No numbers: each stop's page carries
// its own, checked.
// Session 292 (Samuel's ruling 11a of 14 October 2026): a guided path. Seven stops at today's addresses: the three tools
// (what a battery earns, what a generator earns, what a datacenter pays), the Grid, Research, the price board and the
// Digest, in that order. Each stop is a page of the tour (/tour/1 to /tour/7) with the progress bar (app/tour/TourBar.tsx),
// Back and Next, what to look at, and a link that opens the stop's page. `headings` are the headings `look` quotes, as the
// stop's page has them: site/scripts/check-tour.mjs opens each page and fails when one is gone.
// Until session 292: five stops (the network, ERCOT's grid page, the price board, Winter Storm Uri, what a generator
// earns), a list of links with no way back.
// Chain 507 (session 8902): `landed` is false for a stop whose page is not yet on main; such a stop is written here and
// held back from the path until its page lands (the flag is turned by the session that lands it, with check-tour run).
// Session 9601 (chain 620, the browser read of 20 November 2026): check-tour passed 89 of 96 on production. Three
// stops quoted words that were no longer on their page: "Your battery" (the box is "Assumptions" since the owner's
// ruling of 15 October, session 296); "Right now: demand" and "Who runs this grid" (on ERCOT's page; /grid opens on
// the Lower 48 since session 299, so the stop written "ERCOT first" now opens ERCOT); "How the map is drawn" (a
// heading inside the fold "Method note", closed until a reader opens it: `inFold` names the fold, and the stop's words
// say to open it). A heading that carries its year ("Who trades with whom, 2025") is read without the year.
export type Stop = { href: string; title: string; seconds: number; line: string; look: string; headings: string[]; landed?: boolean; inFold?: { fold: string; headings: string[] } };

/** The seven stops of Samuel's ruling 11a (14 October 2026), in the ruled order. */
export const RULED_STOPS: Stop[] = [
  {
    href: "/cost-of-power/battery", title: "What a battery earns", seconds: 45,
    line: "A grid battery of your size in ERCOT or CAISO: what it earned from selling power and from the grid's reserves, year by year, and whether that pays for building it.",
    look: "Read \"What did it earn?\", then \"Is it worth building?\". Change the battery's hours under \"Assumptions\" and watch both move.",
    headings: ["Assumptions", "What did it earn?", "Is it worth building?"],
  },
  {
    href: "/cost-of-power/seller", title: "What a generator earns", seconds: 45,
    line: "The other side of every price: what a solar farm, a wind farm, a battery or a gas peaker earns at a grid's main hub, month by month.",
    look: "Read \"What did it earn?\", then switch the plant under \"Your plant\" from solar to a gas peaker and compare.",
    headings: ["Your plant", "What did it earn?"],
  },
  {
    href: "/cost-of-power", title: "What a datacenter pays", seconds: 45,
    line: "A large load of your size on a grid: what its power will cost, whether the power will be there, how clean it is and how soon it can connect.",
    look: "Read \"What will it pay?\", then \"How soon?\".",
    headings: ["Your load", "What will it pay?", "How soon?"],
  },
  {
    href: "/grid?grid=ercot", title: "The grid", seconds: 40,
    line: "One grid at a time, ERCOT first: what it is doing now, where its power comes from, who runs it and what it costs.",
    look: "Read \"The mix in that hour\" and \"Right now: demand\", then pick another grid at the top.",
    headings: ["The mix in that hour", "Right now: demand", "Who runs this grid"],
  },
  {
    href: "/research", title: "Research", seconds: 40,
    line: "Ask for an analysis of the warehouse's data, and read today's chart, this week's and the library of findings, each with its data and its code.",
    look: "Read \"Today's chart\", then open the \"Findings library\".",
    headings: ["Ask for an analysis", "Today's chart", "Findings library"],
  },
  {
    href: "/board", title: "The price board", seconds: 30,
    line: "Every price the warehouse holds on one screen: power by hub and zone, gas, oil and refined products, with the day's moves.",
    look: "Read \"Power, by hub and zone\", then \"Natural gas\".",
    headings: ["Power, by hub and zone", "Natural gas"],
  },
  {
    href: "/digest", title: "The Energy Digest", seconds: 30,
    line: "The weekday brief: the day's energy news, scored and ranked, with the day's numbers from the warehouse and a chart.",
    look: "Read \"Top of the industry\", then \"ERW's Numbers Today\".",
    headings: ["Top of the industry", "ERW's Numbers Today"],
  },
];

/** Chain 507 (session 8902): what the site gained from 17 November 2026, after the ruled seven. No numbers: each page
 * carries its own. The headings each `look` quotes are read from the pages on main (19 November 2026); check-tour reads
 * them again on a build. */
export const NEW_STOPS: Stop[] = [
  {
    href: "/grid", title: "Every region of the grid", seconds: 40, landed: true,
    line: "The Grid tool beyond the seven grids: the thirteen regions EIA reports, six of them new to the site, each with its mix, its trade and the balancing authorities inside it, and the map of every balancing authority under the network view.",
    // session 9203 (chain 620, the desktop's second window): the Network tab opens on the 3D network (the standing
    // ruling), and the map is one press further, on Map; "Ask" stands beside the tool on a wide screen, under it on a phone
    look: "Pick Tennessee, or any of the thirteen regions, in the region list at the top; open its Network tab, then press Map for the map; then read \"Ask\", beside the tool on a wide screen and under it on a phone.",
    headings: ["Ask"],
  },
  {
    href: "/events/elliott-2022", title: "A storm across the country", seconds: 40, landed: true,
    line: "An event page now follows the storm beyond one grid: each region across the event, what ran against the baseline, and the power that moved between regions.",
    look: "Read \"The whole country\", then \"Power between regions, pair by pair\".",
    headings: ["The whole country", "Each region across the event", "Power between regions, pair by pair"],
  },
  {
    href: "/demand", title: "Demand in every region", seconds: 35, landed: true,
    line: "How much power each place uses, year by year since 2019, for the grids and the regions and balancing authorities of the whole country, two places side by side.",
    look: "Read \"Year by year\", then \"Where the growth is\".",
    headings: ["Year by year", "Where the growth is"],
  },
  {
    href: "/supply", title: "Who trades with whom", seconds: 35, landed: true,
    line: "Supply and trade for the whole country: each region's net imports by month and by neighbour, and the pairs that trade, with the gap where the two sides' reports differ.",
    look: "Read \"The whole country\", then \"Who trades with whom\".",
    headings: ["The whole country", "Who trades with whom"],
  },
  {
    // session 8905 (chain 590): the resource map is the Resources tab of /map; "/map" alone opened the Projects tab,
    // where none of this stop's words or headings are
    href: "/map?tab=resources", title: "What is under the ground and in the wind", seconds: 35, landed: true,
    line: "The resource map: where the coal, the gas, the sun and the wind are, each layer in its own unit, beside what is built or planned. A resource is not a power plant.",
    look: "Read \"What is built or planned\", then open \"Method note\" under the map and read \"How the map is drawn\".",
    headings: ["Where the resources are", "What is built or planned"],
    inFold: { fold: "Method note", headings: ["How the map is drawn"] },
  },
  {
    href: "/industry", title: "Where energy goes", seconds: 35, landed: true,
    line: "Energy by industry, by fuel and by state: who uses the country's energy, as the publishers count it.",
    look: "Read \"The industrial sector, month by month\", then \"States, year by year\".",
    headings: ["The industrial sector, month by month", "States, year by year"],
  },
  {
    href: "/ai-energy", title: "Energy per AI query", seconds: 30, landed: true,
    line: "Energy figures as each publisher printed them: an AI query, a training run, or a company's whole fleet with AI among the rest, with who measured it and how.",
    look: "Read \"Every figure, as printed\", then \"The publishers\".",
    headings: ["Every figure, as printed", "The publishers"],
  },
  {
    href: "/states", title: "Every state", seconds: 35, landed: true,
    line: "One state, or two side by side: what it runs on and how that changed since 2001, what its homes, businesses and industry pay, what is built and coming, and who operates its grid.",
    look: "Read \"What it runs on\", then \"What its homes, businesses and industry buy and pay\".",
    headings: ["What it runs on", "What its homes, businesses and industry buy and pay"],
  },
  {
    href: "/conditions", title: "Grid conditions", seconds: 35, landed: true,
    line: "Is a grid tight, and is it congested: demand against the forecast, the megawatts out of service, the constraints binding and the alerts in force, on one time axis, for any day or for one of the nine events.",
    look: "Read \"The strips\" for ERCOT, then choose Winter Storm Uri under Event; then read \"What is held for each grid\".",
    headings: ["The strips", "What is held for each grid"],
  },
];

/** The guided path: the ruled seven, then the new stops whose pages have landed. */
export const STOPS: Stop[] = [...RULED_STOPS, ...NEW_STOPS.filter((s) => s.landed)];

/** The stops written and held back until their pages land. */
export const HELD_STOPS: Stop[] = NEW_STOPS.filter((s) => !s.landed);

/** The tour's length: the stops' seconds, rounded to the nearest minute. */
export const MINUTES = Math.round(STOPS.reduce((a, s) => a + s.seconds, 0) / 60);
export const stopPath = (n: number) => `/tour/${n}`;
