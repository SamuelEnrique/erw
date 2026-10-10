// Energy Research Warehouse (ERW) site, session 167: the project map, one page (/map).
//
// The page reads the site's own copy of four tables (data/map.json, written by warehouse/derived/project_map.py): EIA's
// operating and planned generating units with EIA's own status for each, the queue positions that are not withdrawn,
// and the datacenters the table places in a US state. Pure functions over that file: what a choice selects, its
// totals by kind, by status and by technology, the choice as an address and back, and the fields of a row's card.
// Nothing here asks a server for anything.

export type Named = { slug: string; name: string };
export type MapFile = {
  tables: string[]; vintage: string; vintages: Record<string, string>; retrieved: string; source_url: string; built: string;
  kinds: (Named & { start: number; rows: number })[]; grids: Named[]; techs: Named[]; statuses: (Named & { kind: number })[];
  states: string[]; names: string[]; held: { grid: string; name: string; words: string; rows: number }[]; counts: Record<string, number>;
  // one column a field, a row a position: a kind after another, the largest first inside a kind
  k: number[]; n: number[]; s: number[]; g: number[]; t: number[]; st: number[]; mw: (number | null)[]; la: (number | null)[]; lo: (number | null)[]; pr: number[];
  // what the card adds
  id: string[]; o: number[]; c: number[]; tx: number[]; d: number[]; operators: string[]; counties: string[]; technologies: string[];
  more: {
    operating: { codes: { code: string; label: string }[]; code: number[] };
    queue: { statuses: string[]; status: number[]; developer: number[] };
    datacenter: { city: string[]; developer: string[]; power: string[]; utility: string[]; from: string[]; urls: string[][] };
  };
};

/** What only the unit card reads. The page leaves it out and reads it once, at the first click on a unit, from
 *  /map/card (app/map/card/route.ts), the same file. */
export const CARD_KEYS = ["id", "o", "c", "tx", "operators", "counties", "technologies", "more"] as const;
export type CardKey = (typeof CARD_KEYS)[number];
export type MapFace = Omit<MapFile, CardKey>;
export type CardPart = Pick<MapFile, CardKey | "built">;
/** The page's columns without the card's. */
export function faceOf(f: MapFile): MapFace {
  const face: Record<string, unknown> = { ...f };
  for (const k of CARD_KEYS) delete face[k];
  return face as MapFace;
}

export const KIND = { operating: 0, planned: 1, queue: 2, datacenter: 3 } as const;
/** The five choices that are lists. `null`: every one (no choice made); a list: those positions only (an empty list: none). */
export const FILTERS = ["kind", "grid", "tech", "status", "state"] as const;
export type Filter = (typeof FILTERS)[number];
export type Choice = Record<Filter, number[] | null> & { min: string; max: string };
export const EVERYTHING: Choice = { kind: null, grid: null, tech: null, status: null, state: null, min: "", max: "" };

/** The slug a state has in the address: its postal code; "na" for a row whose source names no state. */
export const stateSlug = (code: string) => code || "na";
export function optionsOf(f: Pick<MapFile, "kinds" | "grids" | "techs" | "statuses" | "states">, which: Filter): string[] {
  if (which === "kind") return f.kinds.map((x) => x.slug);
  if (which === "grid") return f.grids.map((x) => x.slug);
  if (which === "tech") return f.techs.map((x) => x.slug);
  if (which === "status") return f.statuses.map((x) => x.slug);
  return f.states.map(stateSlug);
}

/** A size typed by the reader: a number at or above zero, or nothing (the bound is then open). */
export function sizeOf(text: string, open: number): number {
  const t = text.trim().replace(/,/g, "");
  if (!/^\d+(\.\d+)?$/.test(t)) return open;
  return Number(t);
}

/** A list of positions as the page keeps it: in order, once each; every option chosen is no choice at all. */
export function tidy(list: number[] | null, options: number): number[] | null {
  if (list === null) return null;
  const out = [...new Set(list)].filter((i) => Number.isInteger(i) && i >= 0 && i < options).sort((a, b) => a - b);
  return out.length === options ? null : out;
}

// The address keeps the choice: ?kind=operating,planned&grid=ercot&tech=solar,battery&status=u,v&state=TX,CA&min=100&max=500.
// A list is slugs with commas between them, in the page's own order. A parameter that is absent or empty means every
// one; "none" means none. A slug the page does not know is passed over. Slugs, never positions: an address written
// today reads the same after the file gains a grid, a status or a state.
export function parseChoice(search: string, f: Pick<MapFile, "kinds" | "grids" | "techs" | "statuses" | "states">): Choice {
  const q = new URLSearchParams(search);
  const c: Choice = { ...EVERYTHING };
  for (const which of FILTERS) {
    const v = (q.get(which) ?? "").trim();
    if (!v) continue;
    if (v === "none") { c[which] = []; continue; }
    const slugs = optionsOf(f, which);
    const found = v.split(",").map((s) => slugs.indexOf(s.trim())).filter((i) => i >= 0);
    c[which] = found.length ? tidy(found, slugs.length) : null;
  }
  const min = (q.get("min") ?? "").trim(), max = (q.get("max") ?? "").trim();
  if (sizeOf(min, -1) >= 0) c.min = min;
  if (sizeOf(max, -1) >= 0) c.max = max;
  return c;
}
export function queryOf(c: Choice, f: Pick<MapFile, "kinds" | "grids" | "techs" | "statuses" | "states">): string {
  const parts: string[] = [];
  for (const which of FILTERS) {
    const list = tidy(c[which], optionsOf(f, which).length);
    if (list === null) continue;
    const slugs = optionsOf(f, which);
    parts.push(`${which}=${list.length ? list.map((i) => encodeURIComponent(slugs[i])).join(",") : "none"}`);
  }
  if (sizeOf(c.min, -1) >= 0) parts.push(`min=${encodeURIComponent(c.min.trim().replace(/,/g, ""))}`);
  if (sizeOf(c.max, -1) >= 0) parts.push(`max=${encodeURIComponent(c.max.trim().replace(/,/g, ""))}`);
  return parts.length ? `?${parts.join("&")}` : "";
}

/** One option of a list turned on or off. */
export function toggle(list: number[] | null, i: number, options: number): number[] | null {
  const now = list === null ? Array.from({ length: options }, (_, j) => j) : list;
  return tidy(now.includes(i) ? now.filter((j) => j !== i) : [...now, i], options);
}
/** A click on a state of the drawing. With every state shown, the click chooses that state alone; after that a click
 *  adds a state or takes it away; taking the last one away shows every state again (the drawing has no dead end). */
export function clickState(list: number[] | null, i: number, options: number): number[] | null {
  if (list === null) return tidy([i], options);
  const next = list.includes(i) ? list.filter((j) => j !== i) : [...list, i];
  return next.length ? tidy(next, options) : null;
}

/** The positions of the rows a choice selects, in the file's order. A row whose source states no MW is selected only
 *  while no size is asked for: it cannot be said to fit one. */
export function select(f: Pick<MapFile, "k" | "g" | "t" | "st" | "s" | "mw">, c: Choice): number[] {
  const lo = sizeOf(c.min, -1), hi = sizeOf(c.max, -1), sized = lo >= 0 || hi >= 0;
  const has = (list: number[] | null) => (list === null ? null : new Set(list));
  const kind = has(c.kind), grid = has(c.grid), tech = has(c.tech), status = has(c.status), state = has(c.state);
  const out: number[] = [];
  for (let i = 0; i < f.k.length; i++) {
    if (kind && !kind.has(f.k[i])) continue;
    if (grid && !grid.has(f.g[i])) continue;
    if (tech && !tech.has(f.t[i])) continue;
    if (status && !status.has(f.st[i])) continue;
    if (state && !state.has(f.s[i])) continue;
    if (sized) {
      const mw = f.mw[i];
      if (mw === null || (lo >= 0 && mw < lo) || (hi >= 0 && mw > hi)) continue;
    }
    out.push(i);
  }
  return out;
}

export type Sum = { rows: number; mw: number; withMw: number };
export type Totals = { rows: number; byKind: Sum[]; byStatus: Sum[]; byTech: Sum[][] };   // byTech[technology][kind]
/** The totals of a selection. MW is never added across kinds: a unit's nameplate, a queue position's request and a
 *  datacenter's stated load are three different things. `withMw`: the rows whose source states a MW. */
export function totals(f: Pick<MapFile, "k" | "t" | "st" | "mw" | "kinds" | "statuses" | "techs">, picked: number[]): Totals {
  const zero = (): Sum => ({ rows: 0, mw: 0, withMw: 0 });
  const byKind = f.kinds.map(zero), byStatus = f.statuses.map(zero), byTech = f.techs.map(() => f.kinds.map(zero));
  for (const i of picked) {
    const mw = f.mw[i];
    for (const s of [byKind[f.k[i]], byStatus[f.st[i]], byTech[f.t[i]][f.k[i]]]) { s.rows += 1; if (mw !== null) { s.mw += mw; s.withMw += 1; } }
  }
  return { rows: picked.length, byKind, byStatus, byTech };
}

export const whole = (v: number) => Math.round(v).toLocaleString("en-US");
export const one = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
/** A date of the file as it is read: 202811 is 2028-11, 20230224 is 2023-02-24, 2027 is 2027, 0 is nothing. */
export function dateOf(d: number): string {
  const t = String(d);
  if (t.length === 8) return `${t.slice(0, 4)}-${t.slice(4, 6)}-${t.slice(6)}`;
  if (t.length === 6) return `${t.slice(0, 4)}-${t.slice(4)}`;
  return t.length === 4 ? t : "";
}
export const yearOf = (d: number) => (d ? String(d).slice(0, 4) : "");

/** The fuel color of a technology of the map: the site's eight, the rest share "other" (a ninth hue is never made). */
export const COLOR: Record<string, string> = {
  solar: "--color-fuel-solar", wind: "--color-fuel-wind", battery: "--color-fuel-storage", storage: "--color-fuel-storage", queue_storage: "--color-fuel-storage",
  natural_gas: "--color-fuel-gas", nuclear: "--color-fuel-nuclear", coal: "--color-fuel-coal", hydro: "--color-fuel-hydro", petroleum: "--color-fuel-other",
  biomass: "--color-fuel-other", geothermal: "--color-fuel-other", hybrid: "--color-fuel-other", transmission: "--color-fuel-other", other: "--color-fuel-other",
  datacenter: "--color-ink", unknown: "--color-fuel-other",
};
/** The key of the colors, one entry a hue. */
export const COLOR_KEY: { color: string; label: string }[] = [
  { color: "--color-fuel-gas", label: "Natural gas" }, { color: "--color-fuel-coal", label: "Coal" }, { color: "--color-fuel-nuclear", label: "Nuclear" },
  { color: "--color-fuel-wind", label: "Wind" }, { color: "--color-fuel-solar", label: "Solar" }, { color: "--color-fuel-hydro", label: "Hydro" },
  { color: "--color-fuel-storage", label: "Batteries and other storage" }, { color: "--color-fuel-other", label: "Everything else" },
];

// The unit card (version 1's card, session 16), from the page's own file: no request is made for it.
const ONE_OF: string[] = ["Operating unit (EIA-860M)", "Planned unit (EIA-860M)", "Queue position", "Datacenter"];
const DATE_IS: string[] = ["began operating", "planned operation date", "queue date", "planned year, as stated"];
const FROM: Record<string, string> = { news: "from the news", operator: "from its operator's site list", queue: "from a queue" };
export type CardRow = { key: string; label: string; value: string; table?: boolean };
export type Card = { i: number; name: string; id: string; rows: CardRow[]; stories: string[]; table: string; vintage: string; built: string };
export function cardOf(f: MapFile, i: number): Card {
  const kind = f.k[i], j = i - f.kinds[kind].start;
  const eia = kind === KIND.operating || kind === KIND.planned, dc = kind === KIND.datacenter, q = kind === KIND.queue;
  const tech = f.techs[f.t[i]], grid = f.grids[f.g[i]], status = f.statuses[f.st[i]], mw = f.mw[i];
  const text = f.tx[i] >= 0 ? f.technologies[f.tx[i]] : "";
  const operator = f.o[i] >= 0 ? f.operators[f.o[i]] : "";
  let said = status.name;
  if (kind === KIND.operating) {
    const code = f.more.operating.codes[f.more.operating.code[j]];
    if (code && code.code !== "OP" && code.label) said += ` (EIA: ${code.label})`;
  } else if (kind === KIND.planned) said += ` (EIA status ${status.slug.toUpperCase()})`;
  else if (q) {
    const own = f.more.queue.statuses[f.more.queue.status[j]];
    if (own) said += ` (as the queue states it: ${own})`;
  }
  const at = f.la[i] === null || f.lo[i] === null ? "" : `, ${f.la[i]}, ${f.lo[i]}`;
  const place = ["exact coordinates" + at, `county point (Census gazetteer)${at}; not the site itself`, `city point (Census gazetteer)${at}; not the site itself`,
    `the operator's coordinates${at}`, "not placed"][f.pr[i]] ?? "not placed";
  const m = f.more.datacenter;
  const developer = dc ? m.developer[j] : "";
  const sourceTable = eia ? f.tables[kind] : q ? `${grid.slug}_interconnection_queue` : "datacenter_facilities";
  const rows: CardRow[] = [
    { key: "kind", label: "Kind", value: ONE_OF[kind] + (dc && FROM[m.from[j]] ? `, ${FROM[m.from[j]]}` : "") },
    { key: "technology_group", label: "Technology group", value: dc ? "" : tech.name + (text ? ` (${text})` : "") },
    { key: "mw", label: "MW", value: mw === null ? "not stated" : `${mw.toLocaleString("en-US")} MW${q ? " requested" : ""}` },
    { key: "status", label: "Status", value: said },
    { key: "state", label: "State", value: f.states[f.s[i]] },
    { key: "county", label: "County", value: f.c[i] >= 0 ? f.counties[f.c[i]] : "" },
    { key: "city", label: "City", value: dc ? m.city[j] : "" },
    { key: "grid", label: "Grid", value: grid.slug === "none" ? "" : grid.name },
    { key: "operator", label: "Operator or developer", value: operator ? `${operator} (${q && f.more.queue.developer[j] ? "developer" : "operator"})` : "not stated" },
    { key: "developer", label: "Developer", value: developer && developer !== operator ? developer : "" },
    { key: "date", label: "Date", value: f.d[i] ? `${dateOf(f.d[i])} (${DATE_IS[kind]})` : "not stated" },
    { key: "power", label: "Power", value: dc ? [m.power[j], m.utility[j] ? `utility ${m.utility[j]}` : ""].filter(Boolean).join("; ") : "" },
    { key: "location", label: "Location", value: place },
    { key: "source_table", label: "Source table", value: sourceTable, table: true },
  ];
  return {
    i, name: f.names[f.n[i]] || "No name in the source", id: eia ? `eia860:${f.id[i]}` : f.id[i], rows: rows.filter((r) => r.value),
    stories: dc ? m.urls[j] : [], table: eia ? f.tables[kind] : q ? "energy_projects" : "datacenter_facilities", vintage: f.vintages[f.kinds[kind].slug] ?? "", built: f.built,
  };
}
