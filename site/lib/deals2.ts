// Energy Research Warehouse (ERW) site, session 113: the deals tracker, version 2 (/deals/v2, in review).
//
// The deals the ERW extracted from the news it reads (energy_deals, warehouse/deals/extract.py), as the page shows
// them: the choices of the panel, the selection, its counts, its disclosed megawatts, its months and its one
// sentence. Pure functions, no imports (Node runs this file as it is, for tests/test_session113.py). A figure a story
// does not state is null here and "not stated" on the page: nothing is estimated, and a sum is the sum of the deals
// that state the figure, said with their count.

/** A row of energy_deals as the live set serves it (lib/data.ts, deals()). */
export type DealRow = {
  event_id: string; event_date: string; status: string | null; mw: number | string | null; price: number | string | null;
  currency: string | null; parties: string | null; source: string; source_url: string; extra: Record<string, string> | null;
};

export type Deal = {
  id: string; date: string; month: string; year: string; type: string; group: string; status: string;
  buyer: string; seller: string; others: string[]; names: string[]; asset: string; technology: string;
  state: string; country: string; grid: string;
  mw: number | null; mwh: number | null; dollars: number | null;
  /** a price in USD per MWh, the only unit the table's price column holds */
  price: number | null;
  /** a price the story states in another unit, as extracted */
  priceOther: { value: number; unit: string } | null;
  termYears: number | null; ai: boolean; storage: boolean;
  source: string; links: string[];
  /** the ids of the rows folded into this one (warehouse/deals/duplicates.csv) */
  folded: string[];
};

export type Pair = { duplicate: string; kept: string; ruling: string; reason: string; found: string };

/** The six deal types of the panel, and the extraction's own types each one holds. Tolling is not a type the
 * extraction has (warehouse/deals/extract.py, DEAL_TYPES), so it holds none until a later extraction names one. */
export const GROUPS: { id: string; label: string; plural: string; types: string[] }[] = [
  { id: "ppa", label: "Power purchase", plural: "power purchase agreements", types: ["ppa"] },
  { id: "offtake", label: "Offtake", plural: "offtake agreements", types: ["offtake"] },
  { id: "project_finance", label: "Project finance", plural: "project financings", types: ["project_finance"] },
  { id: "acquisition", label: "Acquisition", plural: "acquisitions", types: ["m_and_a"] },
  { id: "tolling", label: "Tolling", plural: "tolling agreements", types: ["tolling"] },
  { id: "other", label: "Other", plural: "deals of another type", types: [] },
];
export const TYPE_LABEL: Record<string, string> = {
  ppa: "Power purchase", offtake: "Offtake", m_and_a: "Acquisition", project_finance: "Project finance", tolling: "Tolling",
  tax_equity: "Tax equity", debt: "Debt", equity_raise: "Equity raise", joint_venture: "Joint venture", lease: "Lease",
  behind_the_meter: "Behind the meter", nuclear_restart: "Nuclear restart", smr: "Small modular reactor", fuel_supply: "Fuel supply", other: "Other",
};
const NAMED = new Set(GROUPS.flatMap((g) => g.types));
export const groupOf = (type: string): string => GROUPS.find((g) => g.types.includes(type))?.id ?? "other";

/** The grid operator that serves most of a state, for the states where one does. A state split between grids, or
 * outside all seven, is not assigned: the table holds a deal's state, never its point of delivery. */
export const STATE_GRID: Record<string, string> = {
  TX: "ERCOT", CA: "CAISO", NY: "NYISO",
  CT: "ISO-NE", ME: "ISO-NE", MA: "ISO-NE", NH: "ISO-NE", RI: "ISO-NE", VT: "ISO-NE",
  PA: "PJM", NJ: "PJM", MD: "PJM", DE: "PJM", VA: "PJM", WV: "PJM", OH: "PJM", DC: "PJM",
  MN: "MISO", IA: "MISO", WI: "MISO", MI: "MISO", LA: "MISO",
  OK: "SPP", KS: "SPP", NE: "SPP",
};
export const GRIDS = ["ERCOT", "CAISO", "PJM", "MISO", "SPP", "NYISO", "ISO-NE"];

/** Storage: the story's technology names a battery or storage, or its asset names a battery, energy storage or a BESS. */
export const isStorage = (technology: string, asset: string): boolean =>
  /batter|storage|\bbess\b/i.test(technology) || /batter|energy storage|\bbess\b/i.test(asset);

const num = (v: unknown): number | null => {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};
const split = (s: string, by: RegExp) => s.split(by).map((x) => x.trim()).filter(Boolean);

export function toDeal(r: DealRow): Deal {
  const x = r.extra ?? {};
  const type = x.deal_type ?? "";
  const buyer = x.buyer ?? "", seller = x.seller ?? "";
  const others = split(x.other_parties ?? "", /;/);
  const state = (x.state ?? "").toUpperCase();
  const technology = x.technology ?? "", asset = x.asset ?? "";
  const other = num(x.price_value);
  const links = split(x.story_urls ?? "", /;/);
  return {
    id: r.event_id, date: r.event_date.slice(0, 10), month: r.event_date.slice(0, 7), year: r.event_date.slice(0, 4),
    type, group: groupOf(type), status: r.status ?? "",
    buyer, seller, others, names: [buyer, seller, ...others].filter(Boolean), asset, technology,
    state, country: x.country ?? "", grid: STATE_GRID[state] ?? "",
    mw: num(r.mw), mwh: num(x.mwh), dollars: num(x.dollars),
    price: num(r.price), priceOther: other !== null ? { value: other, unit: x.price_unit ?? "" } : null,
    termYears: num(x.term_years), ai: String(x.ai_power ?? "").toLowerCase() === "true", storage: isStorage(technology, asset),
    source: r.source, links: links.length ? links : [r.source_url].filter(Boolean), folded: [],
  };
}

/** The deals with each folded pair as one: the kept row as extracted, with the story links of both. A pair whose
 * rows are not both held is left alone. Newest first. */
export function fold(deals: Deal[], pairs: Pair[]): Deal[] {
  const by = new Map(deals.map((d) => [d.id, { ...d, links: [...d.links], folded: [...d.folded] }]));
  for (const p of pairs) {
    if (p.ruling !== "fold") continue;
    const kept = by.get(p.kept), dup = by.get(p.duplicate);
    if (!kept || !dup) continue;
    for (const u of dup.links) if (!kept.links.includes(u)) kept.links.push(u);
    kept.folded.push(dup.id);
    by.delete(dup.id);
  }
  return [...by.values()].sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : a.id.localeCompare(b.id)));
}

export type Inputs = { type: string; tech: string; grid: string; party: string; year: string; view: "" | "storage" | "ai" };
export const NOT_STATED = "not stated";

/** The panel's choices from the address. A value the page does not offer is dropped, so a mistyped address shows every deal. */
export function inputsOf(sp: Record<string, string | undefined>, deals: Deal[]): Inputs {
  const one = (k: string) => (sp[k] ?? "").trim();
  const type = GROUPS.some((g) => g.id === one("type")) ? one("type") : "";
  const tech = one("tech") === NOT_STATED || deals.some((d) => d.technology === one("tech")) ? one("tech") : "";
  const grid = GRIDS.includes(one("grid")) ? one("grid") : "";
  const year = /^\d{4}$/.test(one("year")) && deals.some((d) => d.year === one("year")) ? one("year") : "";
  const view = one("view") === "storage" || one("view") === "ai" ? (one("view") as "storage" | "ai") : "";
  return { type, tech, grid, party: one("party").slice(0, 80), year, view };
}

export function hrefOf(x: Inputs, patch: Partial<Inputs> = {}): string {
  const y = { ...x, ...patch };
  const q = new URLSearchParams();
  for (const k of ["view", "type", "tech", "grid", "party", "year"] as const) if (y[k]) q.set(k, y[k]);
  const s = q.toString();
  return s ? `/deals/v2?${s}` : "/deals/v2";
}

export function select(deals: Deal[], x: Inputs): Deal[] {
  const p = x.party.toLowerCase();
  return deals.filter((d) =>
    (!x.type || d.group === x.type)
    && (!x.tech || (x.tech === NOT_STATED ? d.technology === "" : d.technology === x.tech))
    && (!x.grid || d.grid === x.grid)
    && (!p || d.names.some((n) => n.toLowerCase().includes(p)))
    && (!x.year || d.year === x.year)
    && (x.view !== "storage" || d.storage)
    && (x.view !== "ai" || d.ai));
}

export type Counts = {
  deals: number; withMw: number; mw: number; withPrice: number; withOtherPrice: number; withDollars: number; dollars: number;
  byGroup: Record<string, number>;
};
/** The counts of a set of deals. mw and dollars are sums over the deals that state them, never over the others. */
export function counts(deals: Deal[]): Counts {
  const c: Counts = { deals: deals.length, withMw: 0, mw: 0, withPrice: 0, withOtherPrice: 0, withDollars: 0, dollars: 0, byGroup: {} };
  for (const g of GROUPS) c.byGroup[g.id] = 0;
  for (const d of deals) {
    c.byGroup[d.group]++;
    if (d.mw !== null) { c.withMw++; c.mw += d.mw; }
    if (d.price !== null) c.withPrice++;
    else if (d.priceOther !== null) c.withOtherPrice++;
    if (d.dollars !== null) { c.withDollars++; c.dollars += d.dollars; }
  }
  return c;
}

/** Every month from the first deal held to the last, with the selection's count: a month with none is a zero. */
export function months(all: Deal[], shown: Deal[]): { month: string; n: number }[] {
  if (!all.length) return [];
  const ms = all.map((d) => d.month).sort();
  const n = new Map<string, number>();
  for (const d of shown) n.set(d.month, (n.get(d.month) ?? 0) + 1);
  const out: { month: string; n: number }[] = [];
  let [y, m] = ms[0].split("-").map(Number);
  const last = ms[ms.length - 1];
  for (;;) {
    const k = `${y}-${String(m).padStart(2, "0")}`;
    out.push({ month: k, n: n.get(k) ?? 0 });
    if (k >= last) break;
    if (++m > 12) { m = 1; y++; }
  }
  return out;
}

/** The technologies as the stories state them, most frequent first, with "not stated" last. */
export function technologies(deals: Deal[]): { value: string; n: number }[] {
  const n = new Map<string, number>();
  for (const d of deals) n.set(d.technology, (n.get(d.technology) ?? 0) + 1);
  const stated = [...n.entries()].filter(([k]) => k !== "").sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).map(([value, k]) => ({ value, n: k }));
  return n.has("") ? [...stated, { value: NOT_STATED, n: n.get("")! }] : stated;
}

/** The parties named in two deals or more, most frequent first: the suggestions of the counterparty field. */
export function parties(deals: Deal[], min = 2): { name: string; n: number }[] {
  const n = new Map<string, number>();
  for (const d of deals) for (const p of new Set(d.names)) n.set(p, (n.get(p) ?? 0) + 1);
  return [...n.entries()].filter(([, k]) => k >= min).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).map(([name, k]) => ({ name, n: k }));
}

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
export const monthWords = (m: string) => `${MONTHS[Number(m.slice(5, 7)) - 1]} ${m.slice(0, 4)}`;
export const whole = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
/** US dollars, short: 6000000000 gives "6 billion". */
export function usd(v: number): string {
  const t = (x: number) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
  if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  return v.toLocaleString("en-US");
}

/** The choices in words, for the sentence and the headline labels: "" when nothing is chosen. */
export function selectionWords(x: Inputs): string {
  const w: string[] = [];
  if (x.view === "storage") w.push("storage");
  if (x.view === "ai") w.push("AI power");
  if (x.type) w.push(GROUPS.find((g) => g.id === x.type)!.label.toLowerCase());
  if (x.tech) w.push(x.tech === NOT_STATED ? "technology not stated" : `technology ${x.tech}`);
  if (x.grid) w.push(x.grid);
  if (x.party) w.push(`a party named "${x.party}"`);
  if (x.year) w.push(x.year);
  return w.join(", ");
}

/** The one sentence under the title, from the counts alone. */
export function summary(all: Deal[], shown: Deal[], x: Inputs): string {
  if (!all.length) return "No deal is held.";
  const c = counts(shown), words = selectionWords(x);
  const ms = all.map((d) => d.month).sort();
  const span = `${monthWords(ms[0])} to ${monthWords(ms[ms.length - 1])}`;
  if (!c.deals) return `No deal held matches this selection (${words}); ${whole(all.length)} are held, dated ${span}.`;
  const lead = words
    ? `${whole(c.deals)} of the ${whole(all.length)} deals held, dated ${span}, ${c.deals === 1 ? "matches" : "match"} this selection (${words}).`
    : `The ERW holds ${whole(all.length)} deals from the news it reads, dated ${span}.`;
  if (c.deals === 1) {
    return `${lead} It states ${c.withMw ? `a size, ${whole(c.mw)} MW` : "no size"}, and ${c.withPrice ? "a price in US dollars per MWh" : "no price"}.`;
  }
  const size = c.withMw ? `${whole(c.withMw)} of them ${c.withMw === 1 ? "states" : "state"} a size, ${whole(c.mw)} MW in all` : "None of them states a size";
  const price = c.withPrice ? `${whole(c.withPrice)} ${c.withPrice === 1 ? "states" : "state"} a price in US dollars per MWh` : "none states a price";
  return `${lead} ${size}, and ${price}.`;
}
