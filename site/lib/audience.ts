// Energy Research Warehouse (ERW) site, session 110: the home page and menu by audience, a draft (/home/v2, in review).
//
// Three ways in: investors and lenders, operators and developers, students and teachers. Each has its tools, each
// tool the one question it answers. Whether a tool is open to visitors is not written here: it is read from the
// release gate (lib/release.ts), so the draft cannot say "live" of a page the gate keeps in review. Within an
// audience the live tools come first, in the order written; then the tools in review, in the order written.
// The live home page (app/page.tsx) and the site's menu (components/Nav.tsx, lib/pages.ts) do not read this file.

import { statusOf, type Status } from "./release";

export const ONE_SENTENCE = "The Energy Research Warehouse is the live, citable record of the US energy system: prices, flows, projects, deals and policy, each number traced to the report it came from.";

export type Tool = { href: string; label: string; question: string };
export type Audience = { id: string; label: string; line: string; tools: Tool[] };

export const AUDIENCES: Audience[] = [
  {
    id: "investors", label: "Investors and lenders", line: "What an asset earns, what power costs and who is buying it.",
    tools: [
      { href: "/cost-of-power/battery", label: "What a battery earns", question: "What did a grid battery earn from energy and reserves, by year and over the last twelve months?" },
      // session 145: one tool, one page. Version 2 is folded into /cost-of-power/seller and its address redirects there
      { href: "/cost-of-power/seller", label: "What a generator earns", question: "What did solar, wind, a battery or a gas peaker earn at the hub, what price did it capture against the flat average, and how were its bad months?" },
      { href: "/board", label: "The price board", question: "Where do power, gas and oil prices stand, and how did they move on the day and the week?" },
      { href: "/prices/compare", label: "Where power is cheap", question: "Which hubs and zones were cheapest over the last twelve months?" },
      { href: "/shoulder", label: "The shoulder hours", question: "How long is the evening stretch batteries are built for, and how much of it does the fleet cover?" },
      { href: "/storage/buildout", label: "Storage build-out", question: "How much storage has each grid built, of what duration, and what is planned?" },
      { href: "/storage/owners", label: "Who owns the batteries", question: "Which companies report the battery fleet of each grid?" },
      { href: "/contracts", label: "Power contracts", question: "Where are power contracts being struck, and who are the largest buyers?" },
      { href: "/datacenters/v2", label: "The datacenter tracker", question: "How much large load has Texas approved, and how much is running?" },
      { href: "/deals", label: "Deals", question: "Which energy deals were announced, by whom and for how much?" },
    ],
  },
  {
    id: "operators", label: "Operators and developers", line: "What the grid is doing, what is being built and where the queue stands.",
    tools: [
      { href: "/network", label: "The network", question: "Which balancing authorities are trading power with which, hour by hour?" },
      { href: "/storage", label: "Storage", question: "How big is the battery fleet, and how does it charge and discharge?" },
      { href: "/network/v3", label: "The network, version 3", question: "What did the grid look like on any day since 2019, and who supplied whom?" },
      { href: "/map/v2", label: "The project map", question: "Where is every operating and planned generator and battery, by grid, technology and size?" },
      { href: "/queues", label: "The interconnection queue", question: "How much is waiting to connect, how much of the past got built, and how long did it take?" },
      { href: "/mix?view=day", label: "The energy mix", question: "What generates the power, hour by hour, in any month since 2019?" },
      { href: "/demand", label: "Demand growth", question: "How fast is each grid's demand and its peak growing?" },
      { href: "/curtailment/v2", label: "Curtailment", question: "When is solar and wind turned down in California, and how much do batteries soak up?" },
      { href: "/battery/customer", label: "What a battery saves a customer", question: "What would a battery take off my own demand charge and energy bill?" },
      { href: "/grid", label: "Grid conditions", question: "What were yesterday's peak, forecast error and mix on each grid?" },
      { href: "/ask/ercot", label: "Ask ERCOT", question: "A question about the Texas grid, answered from the tables with its sources." },
      { href: "/data/faults", label: "Known data faults", question: "What is wrong in the source data, and what does the ERW do about it?" },
      { href: "/data", label: "Data and methods", question: "Which tables does the ERW hold, and how is each number made?" },
    ],
  },
  {
    id: "students", label: "Students and teachers", line: "How the grid works, learned by using it.",
    tools: [
      { href: "/about", label: "About the ERW", question: "What is this, who makes it and how should it be cited?" },
      { href: "/play/battery", label: "The battery game", question: "Can you run a home battery through a real day better than a rule would?" },
      { href: "/tour", label: "The tour", question: "The energy system in a few screens, each with a real number." },
      { href: "/learn/problems", label: "Problem sets", question: "Exercises on prices, the grid and storage, with answers computed from today's data." },
      { href: "/learn/bill", label: "Your bill", question: "What is in an electricity bill, line by line?" },
      { href: "/events", label: "Events", question: "What happened to the grid in Winter Storm Uri and the other days that tested it?" },
      { href: "/emissions", label: "Emissions", question: "How much carbon does a MWh carry on each grid?" },
      { href: "/ask", label: "Ask the warehouse", question: "A question about US energy, answered from the tables with its sources." },
      { href: "/digest", label: "The Energy Digest", question: "What happened in energy today, scored for significance?" },
    ],
  },
];

export type Listed = Tool & { status: Status };
/** An audience's tools with each one's status from the release gate: the live ones first, then those in review. */
export function listed(a: Audience): Listed[] {
  const all = a.tools.map((t) => ({ ...t, status: statusOf(t.href) }));
  return [...all.filter((t) => t.status === "live"), ...all.filter((t) => t.status === "review")];
}
/** The counts the page states: tools in all (a tool listed under two audiences counted once), and how many are live. */
export function counts(): { tools: number; live: number; review: number } {
  const by = new Map<string, Status>();
  for (const a of AUDIENCES) for (const t of a.tools) by.set(t.href, statusOf(t.href));
  const live = [...by.values()].filter((s) => s === "live").length;
  return { tools: by.size, live, review: by.size - live };
}
