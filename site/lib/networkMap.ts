// Energy Research Warehouse (ERW) site, session 180: the network as a map. The parts with no drawing in them, so a test
// can run them in Node: which of the page's two shapes an address names ("network", the page as it has always opened, or
// "map"), the query that keeps it, and the reading of the boundary file the map draws from
// (public/network/ba_boundaries.json, written by warehouse/connectors/eia_ba_boundaries.py from a publisher's file; the
// map draws nothing that is not in that file, and says so when the file is not held).
// No imports: Node runs this file as it is.

export type Shape = "network" | "map" | "gravity";  // session 266: the gravity shape (lib/networkGravity.ts)
/** The address's own word for the shape. "network" is never written: an address without it is the page as it always was. */
export const SHAPE_KEY = "shape";

/** The shape an address names. Anything but "map" or (session 266) "gravity" is the network. */
export function parseShape(search: string): Shape {
  const p = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
  if (p.get(SHAPE_KEY) === "gravity") return "gravity";
  return p.get(SHAPE_KEY) === "map" ? "map" : "network";
}

/** A view's query (lib/networkV3.ts sharedQuery, unchanged) with the shape after it. The network adds nothing. */
export function withShape(query: string, shape: Shape): string {
  if (shape === "gravity") return `${query ? `${query}&` : "?"}${SHAPE_KEY}=gravity`;
  if (shape !== "map") return query;
  return `${query ? `${query}&` : "?"}${SHAPE_KEY}=map`;
}

/** One balancing authority's shape: rings of [longitude, latitude], outer rings and holes alike (filled even-odd), and a
 * point inside its largest part, where its ties begin and end. */
export type Region = { id: string; source_name: string; area_km2: number; point: [number, number]; rings: [number, number][][] };
export type Boundaries = {
  provenance: { source: string; publisher: string; title: string; vintage: string; url: string; retrieved_utc: string; raw_sha256: string; license_quoted: string;
    simplification: { tolerance_degrees: number };
    /** session 193: true when the areas are the ERW's own derivation (counties given to a balancing authority), not a publisher's boundary; label says so in words */
    derived?: boolean; label?: string };
  nodes: number; matched: number; nodes_without_shape: { id: string; name: string }[]; shapes_without_node: { code: string; name: string }[];
  /** largest first: drawn in this order, a smaller balancing authority is on top of a larger one it sits inside */
  regions: Region[];
};

/** What the map holds: the file, or the plain fact that it is not held (the address answered 404), or why it could not be read. */
export type Held = { state: "loading" } | { state: "absent" } | { state: "error"; why: string } | { state: "held"; file: Boundaries };

/** A boundary file as it must be to be drawn; anything else is an error, never a partial drawing. */
export function readBoundaries(v: unknown): Held {
  const f = v as Partial<Boundaries> | null;
  if (!f || typeof f !== "object" || !Array.isArray(f.regions) || !f.provenance || typeof f.provenance.raw_sha256 !== "string" || !f.provenance.raw_sha256)
    return { state: "error", why: "the file is not a boundary file with a provenance record" };
  for (const r of f.regions) {
    if (!r || typeof r.id !== "string" || !Array.isArray(r.rings) || !Array.isArray(r.point) || r.point.length !== 2)
      return { state: "error", why: "a region of the file has no id, rings or point" };
  }
  return { state: "held", file: f as Boundaries };
}

/** Session 193: the words a derived file must be drawn with, or null for a publisher's own boundary. A derived file without its words still says it is derived. */
export function derivedLabel(f: Boundaries): string | null {
  if (!f.provenance.derived) return null;
  return f.provenance.label || "Derived map: these areas were put together by the ERW and are not a published boundary.";
}

/** A projected ring as an SVG path; a point the projection does not hold (outside the United States) is left out. */
export function ringPath(ring: [number, number][], project: (p: [number, number]) => [number, number] | null): string {
  let d = "";
  for (const p of ring) {
    const q = project(p);
    if (!q) continue;
    d += `${d ? "L" : "M"}${Math.round(q[0] * 10) / 10},${Math.round(q[1] * 10) / 10}`;
  }
  return d ? `${d}Z` : "";
}

/** A tie's width on the map: the vector view's own rule (0.4 + 3 times the square root of its share of the largest flow). */
export const flowWidth = (mw: number, maxMw: number) => 0.4 + 3 * Math.sqrt(mw / (maxMw || 1));

// ------------------------------------------------------------------ session 1156 (chain 077): the edges, their words, and a grid clicked
// The map's edges are the network's own ties in the frame shown (an hour of the live week or of a story, or a day of the
// replay), from EIA-930's interchange, which is public domain for every grid: no grid operator's own table is read for
// a line, so every grid's lines are drawn, the held grids' included. A tie with no figure in the frame is not drawn (a
// zero has no direction and is not drawn either, as the network has always done). A line answers a hover with its
// direction and its window; its MW only where the panel under the map (components/grid/NetworkFigures.tsx,
// grid_network_<grid>) holds that same figure, checked: a tie of the grid in view, in the hour that panel is of, in the
// live week. No other MW is written on the map. One of the seven ISO grids clicked opens its row on the Grid tool.

/** A tie of the network: its two ends and its flow by frame, positive from a to b (lib/network.ts, as the snapshot holds it). */
export type MapTie = { a: string; b: string; mw: (number | null | undefined)[] };
/** An edge drawn: from its exporter (source) to its importer (target), its flow in the frame without its sign, its tie's ends. */
export type MapEdge = { source: string; target: string; mw: number; a: string; b: string };

/** The edges of a frame: one for each tie with a figure in it, from the exporter to the importer; none for a tie with
 * no figure (null) or a zero. The network's own rule (Network.tsx linksAt). */
export function edgesAt(links: MapTie[], h: number): MapEdge[] {
  return links.filter((l) => l.mw[h] !== null && l.mw[h] !== undefined && l.mw[h] !== 0).map((l) => {
    const v = l.mw[h] as number;
    return { source: v > 0 ? l.a : l.b, target: v > 0 ? l.b : l.a, mw: Math.abs(v), a: l.a, b: l.b };
  });
}

/** The panel under the map: the grid in view's EIA-930 code (null for the Lower 48, whose panel holds no tie) and the hour its figures are of. */
export type MapPanel = { ba: string | null; hour: string };
/** The frame a line is drawn for: its start (an hour, UTC, or a day's), the snapshot's refresh for the live week (null
 * for a story or the replay), and whether the frame is a day of the replay. */
export type MapWindow = { at: string; refresh: string | null; day: boolean };

/** Whether an edge's MW is a figure the panel under the map holds: one of its ends is the grid in view, and the frame is
 * the live week's hour that panel is of. Only then is its MW written on the map. */
export function edgeHeld(e: MapEdge, panel: MapPanel | null, w: MapWindow): boolean {
  return !!panel && !!panel.ba && (e.a === panel.ba || e.b === panel.ba) && !w.day && w.refresh !== null && w.at === panel.hour;
}

const hourOf = (t: string) => `${t.slice(0, 10)} ${t.slice(11, 13)}:00 UTC`;
const minuteOf = (t: string) => `${t.slice(0, 16).replace("T", " ")} UTC`;

/** The window in words, as the gravity shape writes it for the live week: "In the hour from 2026-10-21 23:00 UTC, snapshot
 * refreshed 2026-10-23 14:36 UTC"; a day of the replay, "On 2021-02-15, EIA's Eastern day (the day's average MW)". */
export function mapWindowWords(w: MapWindow): string {
  if (w.day) return `On ${w.at.slice(0, 10)}, EIA's Eastern day (the day's average MW)`;
  return w.refresh ? `In the hour from ${hourOf(w.at)}, snapshot refreshed ${minuteOf(w.refresh)}` : `In the hour from ${hourOf(w.at)}, as the story's file holds it`;
}

/** The lines of a line's hover card: its direction, its MW where the panel holds it (else why not), its window and its source.
 * `fmt` writes a number as the panel writes it (lib/format.ts shown), so the two read alike. */
export function edgeTip(e: MapEdge, nameOf: (id: string) => string, panel: MapPanel | null, w: MapWindow, fmt: (v: number) => string): string[] {
  const dir = `From ${nameOf(e.source)} to ${nameOf(e.target)}`;
  const touches = !!panel && !!panel.ba && (e.a === panel.ba || e.b === panel.ba);
  const mw = edgeHeld(e, panel, w)
    ? `${fmt(e.mw)} MW, the figure checked in the panel under the map`
    : touches
      ? `Its MW is checked in the panel under the map for the hour from ${hourOf((panel as MapPanel).hour)}; here its width follows the flow`
      : "Its MW is not written on the map: the panel under it holds the ties of the grid in view only; the width follows the flow";
  return [dir, mw, mapWindowWords(w), "EIA-930's public interchange"];
}

/** A grid of the Grid tool's picker (lib/gridtool.ts GRID_CHOICES): its slug and its EIA-930 code. */
export type MapChoice = { slug: string; ba: string };

/** The Grid tool's slug a region clicked opens, or null: one of the picker's grids other than the grid in view opens
 * its row; the grid in view, and every other balancing authority, opens the panel as before. */
export function regionSlug(id: string, choices: readonly MapChoice[], inView: string | null): string | null {
  if (id === inView) return null;
  return choices.find((c) => c.ba === id)?.slug ?? null;
}

/** The moment the map shows, carried onto a grid's address: the network's own view word (as net, unless the live week)
 * and its t (the hour or the day the reader moved to), from the component's own query (lib/networkV3.ts sharedQuery). */
export function carryMoment(href: string, own: string): string {
  const from = new URLSearchParams(own.startsWith("?") ? own.slice(1) : own);
  const at = href.indexOf("?");
  const to = new URLSearchParams(at < 0 ? "" : href.slice(at + 1));
  const view = from.get("view"), t = from.get("t");
  if (view && view !== "live") to.set("net", view);
  if (t) to.set("t", t);
  const q = to.toString();
  return `${at < 0 ? href : href.slice(0, at)}${q ? `?${q}` : ""}`;
}

/** The panel under the map on the Grid tool, from the query the page keeps ("?grid=ercot&view=network", lib/gridtool.ts
 * gridHref) and the hour the component opens on (the newest hour every reporting pair holds, else the week's last): the
 * hour components/grid/NetworkFigures.tsx draws (lib/gridKeys.ts shownHour). The Lower 48's panel holds no tie (ba null). */
export function mapPanelOf(keep: string, choices: readonly MapChoice[], complete: string | null, hours: string[]): MapPanel | null {
  const slug = new URLSearchParams(keep.startsWith("?") ? keep.slice(1) : keep).get("grid");
  const g = choices.find((c) => c.slug === slug);
  const hour = complete ?? hours[hours.length - 1];
  if (!g || !hour) return null;
  return { ba: g.slug === "us48" ? null : g.ba, hour };
}
/** The part of a line that takes the pointer: its middle, from `trim` of its length after the exporter to `trim` before the
 * importer, so the ends, where a region's ties meet at its point, are left to the region (a click there opens it). */
export function hitSegment(s: [number, number], t: [number, number], trim = 0.2): [[number, number], [number, number]] {
  const at = (k: number): [number, number] => [Math.round((s[0] + (t[0] - s[0]) * k) * 10) / 10, Math.round((s[1] + (t[1] - s[1]) * k) * 10) / 10];
  return [at(trim), at(1 - trim)];
}

/** Session 1158 (chain 077, 390 pixels): the widest a hover card may be, drawn at `x` px from the left of the drawing and
 *  anchored on its left (`right` false: the card starts at x + 12) or on its right (`right` true: it ends at x - 12), so
 *  that it stays inside the frame, which clips it (overflow-hidden), on a phone as on a wide screen: at most 20rem (the
 *  max-w-xs the cards had), and never past the frame less 8 px. x below 0 (a card opened by the keyboard, drawn at the
 *  top left, 8 px in): the frame less 16 px. A CSS length, for the card's style. */
export function cardWidth(x: number, right: boolean): string {
  if (x < 0) return "min(20rem, calc(100% - 16px))";
  return right ? `min(20rem, ${Math.max(0, Math.round(x - 20))}px)` : `min(20rem, calc(100% - ${Math.round(x + 20)}px))`;
}
