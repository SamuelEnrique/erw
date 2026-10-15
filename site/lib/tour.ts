// Session 53: the guided tour's stops (/tour), also linked from the home page. No numbers: each stop's page carries
// its own, checked.
// Session 292 (Samuel's ruling 11a of 14 October 2026): a guided path. Seven stops at today's addresses: the three tools
// (what a battery earns, what a generator earns, what a datacenter pays), the Grid, Research, the price board and the
// Digest, in that order. Each stop is a page of the tour (/tour/1 to /tour/7) with the progress bar (app/tour/TourBar.tsx),
// Back and Next, what to look at, and a link that opens the stop's page. `headings` are the headings `look` quotes, as the
// stop's page has them: site/scripts/check-tour.mjs opens each page and fails when one is gone.
// Until session 292: five stops (the network, ERCOT's grid page, the price board, Winter Storm Uri, what a generator
// earns), a list of links with no way back.
export type Stop = { href: string; title: string; seconds: number; line: string; look: string; headings: string[] };

export const STOPS: Stop[] = [
  {
    href: "/cost-of-power/battery", title: "What a battery earns", seconds: 45,
    line: "A grid battery of your size in ERCOT or CAISO: what it earned from selling power and from the grid's reserves, year by year, and whether that pays for building it.",
    look: "Read \"What did it earn?\", then \"Is it worth building?\". Change the battery's hours under \"Your battery\" and watch both move.",
    headings: ["Your battery", "What did it earn?", "Is it worth building?"],
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
    href: "/grid", title: "The grid", seconds: 40,
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

/** The tour's length: the stops' seconds, rounded to the nearest minute. */
export const MINUTES = Math.round(STOPS.reduce((a, s) => a + s.seconds, 0) / 60);
export const stopPath = (n: number) => `/tour/${n}`;
