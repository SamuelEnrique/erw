// Energy Research Warehouse (ERW) site, session 130: the deals tracker, version 3 (/deals/v3, in review).
//
// Power deals read from the titles and summaries of the news the ERW holds (power_deals, warehouse/deals/extract_v3.py),
// as the page shows them: the choices of the panel, the selection, its counts and its one sentence. Pure functions, no
// imports (Node runs this file as it is, for tests/test_session130.py). A number is here only if the table holds it, and
// the table holds it only with the sentence it was read from; a figure a story does not state is null here and "not
// stated" on the page. Nothing is estimated, and a sum is the sum over the deals that state the figure, with their count.

/** A row of the site's copy of power_deals (data/deals_v3.json): every field a string, "" for not stated. */
export type Row = Record<string, string>;

/** A stated number: its value, the word before it that limits it ("up to"), and the story it was read from. */
export type Num = { value: number; qualifier: string; url: string };

export type Deal = {
  id: string; date: string; month: string; year: string; kind: string; status: string;
  buyer: string; seller: string; others: string[]; names: string[]; asset: string; technology: string[];
  storage: boolean; datacenter: boolean; place: string; state: string; country: string;
  mw: Num | null; mwh: Num | null; term: Num | null; dollars: Num | null;
  /** a price with its unit as the story states it; perMwh is true when the unit is US dollars per MWh */
  price: (Num & { unit: string; perMwh: boolean }) | null;
  source: string; links: string[]; readByV2: boolean; folded: number;
};

export const KINDS: { id: string; label: string; plural: string }[] = [
  { id: "power_purchase", label: "Power purchase", plural: "power purchase agreements" },
  { id: "tolling", label: "Tolling", plural: "tolling agreements" },
  { id: "offtake", label: "Offtake", plural: "offtake agreements" },
  { id: "project_finance", label: "Project finance", plural: "financings" },
  { id: "acquisition", label: "Acquisition", plural: "acquisitions" },
  { id: "other", label: "Other", plural: "power deals of another kind" },
];
export const KIND_LABEL: Record<string, string> = Object.fromEntries(KINDS.map((k) => [k.id, k.label]));
export const TECH_LABEL: Record<string, string> = {
  solar: "Solar", wind: "Wind", storage: "Storage", nuclear: "Nuclear", gas: "Gas", coal: "Coal", hydro: "Hydro",
  geothermal: "Geothermal", hydrogen: "Hydrogen", fuel_cell: "Fuel cell", transmission: "Transmission", other: "Other",
};
export const NOT_STATED = "not stated";
export const STATES: { id: string; label: string }[] = [
  { id: "size", label: "State a size (MW or MWh)" }, { id: "price", label: "State a price" },
  { id: "term", label: "State a term" }, { id: "dollars", label: "State a value in US dollars" },
];

const STATES_WORDS: Record<string, string> = { size: "stating a size", price: "stating a price", term: "stating a term", dollars: "stating a value in US dollars" };
const split = (s: string) => (s ?? "").split(";").map((x) => x.trim()).filter(Boolean);
const pairs = (s: string): Record<string, string> => Object.fromEntries(split(s).map((p) => { const i = p.indexOf("="); return [p.slice(0, i), p.slice(i + 1)]; }));

export function toDeal(r: Row): Deal {
  const ids = split(r.story_ids), urls = split(r.story_urls);
  const q = pairs(r.qualifiers), from = pairs(r.number_stories);
  const num = (field: string, raw: string): Num | null => {
    if (raw === "" || raw === undefined || !Number.isFinite(Number(raw))) return null;
    const i = ids.indexOf(from[field] ?? "");
    return { value: Number(raw), qualifier: q[field] ?? "", url: i >= 0 ? urls[i] ?? "" : "" };
  };
  const p = num("price_value", r.price_value);
  const others = split(r.other_parties);
  return {
    id: r.event_id, date: r.event_date.slice(0, 10), month: r.event_date.slice(0, 7), year: r.event_date.slice(0, 4),
    kind: r.kind, status: r.status, buyer: r.buyer, seller: r.seller, others, names: [r.buyer, r.seller, ...others].filter(Boolean),
    asset: r.asset, technology: split(r.technology), storage: r.storage === "true", datacenter: r.datacenter === "true",
    place: r.place, state: r.state, country: r.country,
    mw: num("mw", r.mw), mwh: num("mwh", r.mwh), term: num("term_years", r.term_years), dollars: num("dollars", r.dollars),
    price: p ? { ...p, unit: r.price_unit, perMwh: r.price !== "" } : null,
    source: r.source, links: urls.length ? urls : [r.source_url].filter(Boolean), readByV2: r.read_by_v2 === "true", folded: split(r.folded_ids).length,
  };
}

export type Inputs = { kind: string; tech: string; view: "" | "storage" | "datacenter"; states: string; party: string; year: string };

/** The panel's choices from the address. A value the page does not offer is dropped, so a mistyped address shows every deal. */
export function inputsOf(sp: Record<string, string | undefined>, deals: Deal[]): Inputs {
  const one = (k: string) => (sp[k] ?? "").trim();
  const view = one("view") === "storage" || one("view") === "datacenter" ? (one("view") as "storage" | "datacenter") : "";
  return {
    kind: KINDS.some((k) => k.id === one("kind")) ? one("kind") : "",
    tech: one("tech") === NOT_STATED || one("tech") in TECH_LABEL ? one("tech") : "",
    view, states: STATES.some((s) => s.id === one("states")) ? one("states") : "",
    party: one("party").slice(0, 80),
    year: /^\d{4}$/.test(one("year")) && deals.some((d) => d.year === one("year")) ? one("year") : "",
  };
}

export function hrefOf(x: Inputs, patch: Partial<Inputs> = {}): string {
  const y = { ...x, ...patch };
  const q = new URLSearchParams();
  for (const k of ["view", "kind", "tech", "states", "party", "year"] as const) if (y[k]) q.set(k, y[k]);
  const s = q.toString();
  return s ? `/deals/v3?${s}` : "/deals/v3";
}

export const states = (d: Deal, what: string): boolean =>
  what === "size" ? d.mw !== null || d.mwh !== null : what === "price" ? d.price !== null : what === "term" ? d.term !== null : what === "dollars" ? d.dollars !== null : true;

export function select(deals: Deal[], x: Inputs): Deal[] {
  const p = x.party.toLowerCase();
  return deals.filter((d) =>
    (!x.kind || d.kind === x.kind)
    && (!x.tech || (x.tech === NOT_STATED ? d.technology.length === 0 : d.technology.includes(x.tech)))
    && (x.view !== "storage" || d.storage)
    && (x.view !== "datacenter" || d.datacenter)
    && (!x.states || states(d, x.states))
    && (!p || d.names.some((n) => n.toLowerCase().includes(p)))
    && (!x.year || d.year === x.year));
}

export type Counts = {
  deals: number; size: number; withMw: number; mw: number; withMwh: number; mwh: number; price: number; pricePerMwh: number;
  term: number; withDollars: number; dollars: number; byKind: Record<string, number>;
};
/** The counts of a set of deals. mw, mwh and dollars are sums over the deals that state them, never over the others. */
export function counts(deals: Deal[]): Counts {
  const c: Counts = { deals: deals.length, size: 0, withMw: 0, mw: 0, withMwh: 0, mwh: 0, price: 0, pricePerMwh: 0, term: 0, withDollars: 0, dollars: 0, byKind: {} };
  for (const k of KINDS) c.byKind[k.id] = 0;
  for (const d of deals) {
    c.byKind[d.kind] = (c.byKind[d.kind] ?? 0) + 1;
    if (d.mw !== null || d.mwh !== null) c.size++;
    if (d.mw !== null) { c.withMw++; c.mw += d.mw.value; }
    if (d.mwh !== null) { c.withMwh++; c.mwh += d.mwh.value; }
    if (d.price !== null) { c.price++; if (d.price.perMwh) c.pricePerMwh++; }
    if (d.term !== null) c.term++;
    if (d.dollars !== null) { c.withDollars++; c.dollars += d.dollars.value; }
  }
  return c;
}

/** The technologies the deals name, most frequent first, with "not stated" last. A deal that names two counts in both. */
export function technologies(deals: Deal[]): { value: string; n: number }[] {
  const n = new Map<string, number>();
  let none = 0;
  for (const d of deals) { if (!d.technology.length) none++; for (const t of d.technology) n.set(t, (n.get(t) ?? 0) + 1); }
  const stated = [...n.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).map(([value, k]) => ({ value, n: k }));
  return none ? [...stated, { value: NOT_STATED, n: none }] : stated;
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
/** A stated number in words: its qualifier, then the figure and unit ("up to 250 MW"). */
export const stated = (n: Num, figure: string) => (n.qualifier ? `${n.qualifier} ${figure}` : figure);

/** The choices in words, for the sentence and the headline labels: "" when nothing is chosen. */
export function selectionWords(x: Inputs): string {
  const w: string[] = [];
  if (x.view === "storage") w.push("storage");
  if (x.view === "datacenter") w.push("datacenters");
  if (x.kind) w.push(KIND_LABEL[x.kind].toLowerCase());
  if (x.tech) w.push(x.tech === NOT_STATED ? "technology not stated" : `technology ${TECH_LABEL[x.tech].toLowerCase()}`);
  if (x.states) w.push(STATES_WORDS[x.states]);
  if (x.party) w.push(`a party named "${x.party}"`);
  if (x.year) w.push(x.year);
  return w.join(", ");
}

/** The one sentence under the title, from the counts alone. */
export function summary(all: Deal[], shown: Deal[], x: Inputs): string {
  if (!all.length) return "No power deal is held.";
  const c = counts(shown), words = selectionWords(x);
  const ms = all.map((d) => d.month).sort();
  const span = `${monthWords(ms[0])} to ${monthWords(ms[ms.length - 1])}`;
  if (!c.deals) return `No power deal held matches this selection (${words}); ${whole(all.length)} are held, dated ${span}.`;
  const lead = words
    ? `${whole(c.deals)} of the ${whole(all.length)} power deals held, dated ${span}, ${c.deals === 1 ? "matches" : "match"} this selection (${words}).`
    : `The ERW holds ${whole(all.length)} power deals read from the news, dated ${span}.`;
  const n = (k: number, what: string) => `${whole(k)} ${k === 1 ? "states" : "state"} ${what}`;
  return `${lead} ${n(c.size, "a size")}, ${n(c.price, "a price")} and ${n(c.term, "a term")}.`;
}
