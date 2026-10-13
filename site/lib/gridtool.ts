// Energy Research Warehouse (ERW) site, session 237: the Grid tool, one page at /grid (the roadmap's item 2: the
// network, the energy mix and Ask merged into one tool). Its address and its small helpers. Pure functions and no
// imports, so the page, the network component (a client component) and a test in Node read this file as it is.
//
// The address: /grid?grid=<grid>&view=<view>. The grid is one of the eight of the picker; the view one of six. A view
// keeps its own state under its own words, so nothing collides with the page's two:
//   Mix       mix=<the mix page's view> and the mix page's own parameters (grids, period, cal, year, season, norm,
//             factor, src, states, state), as /mix wrote them
//   Network   net=<the network's view> (live, day, evening, uri_2021, east_heat_2025), node=<the balancing authority
//             whose panel is open>, and t, batteries, prices, trace, shape as /network wrote them
//   Ask       q=<a question to place in the box; it is never sent by the page>
// The addresses that redirect here (next.config.ts) carry their query over, so an old address is read too: a grid
// named by its EIA-930 code (grid=ERCO, the network's word), by the mix page's ba (ba=erco) or as the first of its
// grids (grids=pjm,miso) chooses that grid.

export const GRID_CHOICES = [
  { slug: "ercot", label: "ERCOT", ba: "ERCO", name: "Electric Reliability Council of Texas" },
  { slug: "caiso", label: "CAISO", ba: "CISO", name: "California Independent System Operator" },
  { slug: "pjm", label: "PJM", ba: "PJM", name: "PJM Interconnection" },
  { slug: "miso", label: "MISO", ba: "MISO", name: "Midcontinent Independent System Operator" },
  { slug: "nyiso", label: "NYISO", ba: "NYIS", name: "New York Independent System Operator" },
  { slug: "isone", label: "ISO-NE", ba: "ISNE", name: "ISO New England" },
  { slug: "spp", label: "SPP", ba: "SWPP", name: "Southwest Power Pool" },
  { slug: "us48", label: "US48", ba: "US48", name: "the Lower 48 states" },
] as const;
export type GridChoice = (typeof GRID_CHOICES)[number];
export type GridSlug8 = GridChoice["slug"];

export const GRID_VIEWS = [
  ["now", "Now"], ["network", "Network"], ["mix", "Mix"], ["clean", "Clean"], ["exchange", "Exchange"], ["ask", "Ask"],
] as const;
export type GridView = (typeof GRID_VIEWS)[number][0];

/** The grid the page opens with when the address names none. */
export const DEFAULT_GRID: GridSlug8 = "ercot";
export const GRID_PATH = "/grid";

type Query = Record<string, string | string[] | undefined>;
const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);

/** A grid by any of the words an address has used for it: the slug, the label, the EIA-930 code, in any case. */
export function gridBy(word: string | undefined | null): GridChoice | null {
  const w = (word ?? "").trim().toLowerCase().replace(/[^a-z0-9]/g, "");
  if (!w) return null;
  return GRID_CHOICES.find((g) => g.slug === w || g.ba.toLowerCase() === w || g.label.toLowerCase().replace(/[^a-z0-9]/g, "") === w) ?? null;
}

export type GridPick = {
  grid: GridChoice; view: GridView;
  /** the balancing authority whose panel the Network view opens: the address's node, else an old address's grid when
   *  it is a code that is none of the eight (BPAT), else the chosen grid's own (none for the Lower 48) */
  node: string | null;
  /** true when the address named the grid; false when the page chose its default */
  named: boolean;
};

/** What an address asks for. Anything unknown falls back to the page as it opens. */
export function gridPick(q: Query): GridPick {
  const asked = one(q.view);
  let view: GridView = GRID_VIEWS.some(([k]) => k === asked) ? (asked as GridView) : "now";
  // the mix page's view "How clean, and when" is the Clean view of this page
  if (view === "mix" && one(q.mix) === "clean") view = "clean";
  const raw = one(q.grid);
  const byGrid = gridBy(raw), byBa = gridBy(one(q.ba)), byGrids = gridBy((one(q.grids) ?? "").split(",")[0]);
  const byNode = gridBy(one(q.node));
  const code = (v: string | undefined) => (v && /^[A-Z0-9]{2,6}$/.test(v) ? v : null);
  // an old network address naming a balancing authority that is none of the eight (grid=BPAT): the Lower 48, that panel open
  const other = !byGrid ? code(raw) : null;
  const us48 = GRID_CHOICES.find((g) => g.slug === "us48")!;
  const grid = byGrid ?? (other ? us48 : null) ?? byBa ?? byGrids ?? byNode ?? GRID_CHOICES.find((g) => g.slug === DEFAULT_GRID)!;
  const node = code(one(q.node)) ?? other ?? (grid.slug === "us48" ? null : grid.ba);
  return { grid, view, node, named: !!(byGrid ?? other ?? byBa ?? byGrids ?? byNode) };
}

/** The address of a grid and a view; `more` adds a view's own state. The opening page writes nothing. */
export function gridHref(grid: string, view: GridView = "now", more: Record<string, string | undefined> = {}): string {
  const q = new URLSearchParams();
  q.set("grid", grid);
  if (view !== "now") q.set("view", view);
  for (const [k, v] of Object.entries(more)) if (v !== undefined && v !== "") q.set(k, v);
  return `${GRID_PATH}?${q.toString()}`;
}

// ------------------------------------------------------------------ the Network view's address
// The network component keeps its view in the address (lib/networkV3.ts sharedQuery: view, t, grid, batteries, prices,
// trace; lib/networkMap.ts: shape). On this page two of those words are the page's own, so the component reads and
// writes through these two: its "view" is the page's "net", its "grid" the page's "node".

/** The network's own query, read from the page's: "?net=day&t=2021-02-15&node=ERCO" gives "?view=day&t=2021-02-15&grid=ERCO". */
export function netFromPage(search: string, fallbackNode: string | null = null): string {
  const p = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
  const out: [string, string][] = [];
  const net = p.get("net");
  if (net) out.push(["view", net]);
  const t = p.get("t");
  if (t) out.push(["t", t]);
  const node = p.get("node") ?? fallbackNode;
  if (node) out.push(["grid", node]);
  for (const k of ["batteries", "prices", "trace", "shape"]) { const v = p.get(k); if (v) out.push([k, v]); }
  return out.length ? `?${out.map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join("&")}` : "";
}

/** The page's query for a network view: what the page keeps (its grid and view) and the network's own query after it. */
export function netToPage(keep: string, own: string): string {
  const p = new URLSearchParams(own.startsWith("?") ? own.slice(1) : own);
  const out: string[] = [];
  for (const [k, v] of p) out.push(`${k === "view" ? "net" : k === "grid" ? "node" : k}=${encodeURIComponent(v)}`);
  const head = keep.startsWith("?") ? keep : `?${keep}`;
  return out.length ? `${head}&${out.join("&")}` : head;
}
