// Session 53: the guided tour's five stops (/tour), also linked from the home page. No numbers: each stop's page carries
// its own, checked.
export const STOPS: { href: string; title: string; minutes: string; line: string; look: string }[] = [
  {
    href: "/network", title: "The network", minutes: "about 30 seconds",
    line: "The US grid is not one grid but dozens of balancing authorities that trade power every hour; here they are in 3D, with a week of their flows.",
    look: "Press play and watch the flows turn with the day; click ERCOT and see how little it trades with its neighbors.",
  },
  {
    href: "/grid/ercot", title: "One grid: ERCOT", minutes: "about 40 seconds",
    line: "Each of the seven ISO grids has a page with what it is and what it is doing today: demand, generation, prices, batteries and its queue.",
    // session 261: the three headings as the page a reader lands on has them, in its order ("Where the power comes
    // from" is on the grid's Mix view, not on this one)
    look: "Read \"The mix in that hour\", then \"Right now: demand\" and \"Who runs this grid\".",
  },
  {
    href: "/board", title: "The price board", minutes: "about 30 seconds",
    line: "What power is selling for at each grid's main hub right now, day-ahead and real-time, beside gas and oil.",
    // session 261: no count of hubs (the board holds a real-time price for five of its seven: MISO is paused and
    // PJM's needs a licensed source), and "the day before" for the board's own "Day" column
    look: "Compare the hubs' real-time prices with each other and with the day before.",
  },
  {
    href: "/events/uri-2021", title: "An event study: Winter Storm Uri", minutes: "about 45 seconds",
    line: "What a major event did to a grid, day by day against the same days of earlier years, with an estimate of its effect with and without the weather.",
    look: "Read the two estimates under \"What the estimates say\": how much of the jump in demand the cold explains.",
  },
  {
    href: "/cost-of-power/seller", title: "What a generator earns", minutes: "about 40 seconds",
    line: "The other side of every price: what a solar farm, a battery or a gas peaker earns month by month, and whether that covers its debt.",
    // session 261: the two headings as the page has them now ("The worst month", "Debt coverage")
    look: "Look at \"The worst month\" and \"Debt coverage\", then switch the asset to a battery.",
  },
];
