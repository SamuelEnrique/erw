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

// ---------------------------------------------------------------------------------------------------------------------
// Session 8601 (chain 504, 19 November 2026): the map made whole. Everything below is new; nothing above moved.
// - the boundary file of the whole country's page files (data/regions/ba_boundaries.json, the contract
//   docs/state/page_files_regions.md, section 1: a GeoJSON FeatureCollection, one feature a balancing authority), read
//   into the same Boundaries the map has always drawn, so the map draws either file with the same code;
// - a point inside a shape, where its ties begin and end (the contract's file gives none);
// - the words of a tie's hover, the batteries' ring, and the arithmetic of moving and zooming the map.

type Ring = [number, number][];

/** Twice the signed area of a ring (the shoelace sum), in the ring's own units. */
function ring2Area(ring: Ring): number {
  let s = 0;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i, i += 1) s += ring[j][0] * ring[i][1] - ring[i][0] * ring[j][1];
  return s;
}

/** Is the point inside the shape, its rings read even-odd (an outer ring holds it, a hole does not)? */
export function insideRings(p: [number, number], rings: Ring[]): boolean {
  let inside = false;
  for (const ring of rings) {
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i, i += 1) {
      const [xi, yi] = ring[i], [xj, yj] = ring[j];
      if ((yi > p[1]) !== (yj > p[1]) && p[0] < ((xj - xi) * (p[1] - yi)) / (yj - yi) + xi) inside = !inside;
    }
  }
  return inside;
}

/** A point inside a shape, for its ties and its ring: the centroid of its largest ring when that lies inside the
 * shape; else the middle of the longest stretch inside it on one of three level lines across that ring (a quarter,
 * a half and three quarters of its height). Null for a shape with no ring of three points. */
export function insidePoint(rings: Ring[]): [number, number] | null {
  let best: Ring | null = null, bestA = 0;
  for (const r of rings) { const a = Math.abs(ring2Area(r)); if (r.length >= 3 && a > bestA) { best = r; bestA = a; } }
  if (!best) return null;
  const a2 = ring2Area(best);
  let cx = 0, cy = 0;
  for (let i = 0, j = best.length - 1; i < best.length; j = i, i += 1) {
    const f = best[j][0] * best[i][1] - best[i][0] * best[j][1];
    cx += (best[j][0] + best[i][0]) * f; cy += (best[j][1] + best[i][1]) * f;
  }
  const c: [number, number] = [cx / (3 * a2), cy / (3 * a2)];
  const round = (p: [number, number]): [number, number] => [Math.round(p[0] * 1000) / 1000, Math.round(p[1] * 1000) / 1000];
  if (insideRings(c, rings)) return round(c);
  const ys = best.map((p) => p[1]), lo = Math.min(...ys), hi = Math.max(...ys);
  let pick: [number, number] | null = null, width = 0;
  for (const share of [0.5, 0.25, 0.75]) {
    const y = lo + (hi - lo) * share;
    const xs: number[] = [];
    for (const ring of rings) for (let i = 0, j = ring.length - 1; i < ring.length; j = i, i += 1) {
      const [xi, yi] = ring[i], [xj, yj] = ring[j];
      if ((yi > y) !== (yj > y)) xs.push(((xj - xi) * (y - yi)) / (yj - yi) + xi);
    }
    xs.sort((p, q) => p - q);
    // a stretch counts only when its middle is inside the shape a little above and a little below the line too (a line
    // that runs along an edge of a hole would otherwise give a point on that edge)
    const eps = (hi - lo) * 0.01;
    for (let k = 0; k + 1 < xs.length; k += 2) {
      const mid = (xs[k] + xs[k + 1]) / 2;
      if (xs[k + 1] - xs[k] > width && insideRings([mid, y + eps], rings) && insideRings([mid, y - eps], rings)) { width = xs[k + 1] - xs[k]; pick = [mid, y]; }
    }
  }
  return pick ? round(pick) : round(c);
}

/** The contract's boundary file (docs/state/page_files_regions.md, section 1) as the map draws a boundary file: one
 * region a balancing authority, largest first, each with a point inside it. Anything that is not that file whole (no
 * source, no retrieval time, a feature with no code or no polygon) is an error, never a partial drawing. The file is a
 * publisher's own layer, so it carries no derived label. */
export function readGeoBoundaries(v: unknown): Held {
  type Feature = { properties?: { code?: unknown; name?: unknown; area_km2?: unknown }; geometry?: { type?: unknown; coordinates?: unknown } };
  const f = v as { type?: unknown; features?: Feature[]; source?: unknown; source_url?: unknown; retrieved_at?: unknown; license?: unknown; simplify_tolerance_deg?: unknown;
    bas_without_polygon?: unknown; polygons_without_ba?: unknown; built?: unknown } | null;
  if (!f || typeof f !== "object" || f.type !== "FeatureCollection" || !Array.isArray(f.features)) return { state: "error", why: "the file is not a boundary file (a GeoJSON FeatureCollection)" };
  if (typeof f.source !== "string" || !f.source || typeof f.retrieved_at !== "string" || !f.retrieved_at) return { state: "error", why: "the boundary file does not say its source and when it was retrieved" };
  const regions: Region[] = [];
  for (const ft of f.features) {
    const code = ft?.properties?.code, g = ft?.geometry;
    if (typeof code !== "string" || !code || !g || (g.type !== "Polygon" && g.type !== "MultiPolygon") || !Array.isArray(g.coordinates)) return { state: "error", why: "a feature of the boundary file has no code or no polygon" };
    const rings = (g.type === "Polygon" ? [g.coordinates] : g.coordinates).flat() as Ring[];
    const point = insidePoint(rings);
    if (!point) return { state: "error", why: `the boundary of ${code} has no ring of three points` };
    regions.push({ id: code, source_name: typeof ft.properties?.name === "string" ? ft.properties.name : code, area_km2: typeof ft.properties?.area_km2 === "number" ? ft.properties.area_km2 : 0, point, rings });
  }
  // largest first (by the publisher's own area; the ring's own where none is given), so a smaller one is drawn on top
  const size = (r: Region) => r.area_km2 || Math.max(...r.rings.map((x) => Math.abs(ring2Area(x))));
  regions.sort((a, b) => size(b) - size(a));
  const without = Array.isArray(f.bas_without_polygon) ? (f.bas_without_polygon as unknown[]).filter((x): x is string => typeof x === "string") : [];
  const strays = Array.isArray(f.polygons_without_ba) ? (f.polygons_without_ba as { id?: unknown; name?: unknown }[]).map((x) => ({ code: String(x?.id ?? ""), name: String(x?.name ?? "") })) : [];
  return { state: "held", file: {
    provenance: { source: f.source, publisher: f.source, title: f.source, vintage: "", url: typeof f.source_url === "string" ? f.source_url : "", retrieved_utc: f.retrieved_at, raw_sha256: "",
      license_quoted: typeof f.license === "string" ? f.license : "", simplification: { tolerance_degrees: typeof f.simplify_tolerance_deg === "number" ? f.simplify_tolerance_deg : 0 } },
    nodes: regions.length + without.length, matched: regions.length, nodes_without_shape: without.map((id) => ({ id, name: id })), shapes_without_node: strays, regions } };
}

/** A grid's net imports in one frame, over the ties that reported in it: the panel's own sum (app/network/Network.tsx,
 * `ties` and `netImport`; lib/network.ts netValue's net|import), positive when the grid imports. `net` is null when no
 * tie reported. The map's hover reads this, so the hover, the panel and the figures under the network are one number. */
export function netOf(links: { a: string; b: string; mw: (number | null)[] }[], id: string, frame: number): { net: number | null; ties: number } {
  let net = 0, ties = 0;
  for (const l of links) {
    if (l.a !== id && l.b !== id) continue;
    const v = l.mw[frame];
    if (v === null || v === undefined) continue;
    net += l.a === id ? -v : v; ties += 1;
  }
  return { net: ties ? net || 0 : null, ties };
}

/** Which side's report a tie's flow is, in one frame. The snapshot's rule (data/grid_network.json, `rule`): a pair's
 * flow is read from the balancing authority whose code sorts first; in a frame it did not report, from the other's
 * with the sign turned. `other` is the list of frames read from the second side, when the file carries one; without
 * it the file does not mark which, and the answer is null. */
export function reportedBy(other: number[] | undefined, frame: number): "first" | "second" | null {
  if (!Array.isArray(other)) return null;
  return other.includes(frame) ? "second" : "first";
}

/** A figure in whole units, as the panel writes it (never "-0"). */
export const whole = (v: number) => (Math.round(v) === 0 ? 0 : Math.round(v)).toLocaleString("en-US");

/** The words of a tie's hover: both names, the megawatts, the frame shown, and which side reported it. */
export function flowTip(f: { from: string; to: string; fromName: string; toName: string; mw: number; when: string; unit: "hour" | "day";
  /** the pair as the file holds it: `a` sorts first */ a: string; b: string; aName: string; bName: string; side: "first" | "second" | null }): { head: string; lines: string[] } {
  const said = f.side === "first" ? `Reported by ${f.aName} (${f.a}).`
    : f.side === "second" ? `Reported by ${f.bName} (${f.b}): ${f.aName} (${f.a}) filed nothing for this ${f.unit}.`
      : `Reported by ${f.aName} (${f.a}), the first of the two by code; where it filed nothing for this ${f.unit}, by ${f.bName} (${f.b}). The file does not mark which.`;
  return { head: `${f.fromName} (${f.from}) to ${f.toName} (${f.to})`, lines: [`${whole(f.mw)} MW${f.unit === "day" ? " on average over the day" : ""}`, f.when, said] };
}

/** The tie whose line is nearest a point, and how far it is, in the drawing's own units; null with no tie. The hover
 * takes the nearest line, not the one drawn last, so of two ties that run close together each is reached on its own
 * side, and a short tie is never hidden under a long one. */
export function nearestLine(p: [number, number], lines: { from: [number, number]; to: [number, number] }[]): { index: number; distance: number; /** how far along the line its nearest point is, 0 to 1 */ along: number; length: number } | null {
  let index = -1, distance = Infinity, along = 0, length = 0;
  lines.forEach((l, i) => {
    const dx = l.to[0] - l.from[0], dy = l.to[1] - l.from[1], len2 = dx * dx + dy * dy;
    const u = len2 ? Math.max(0, Math.min(1, ((p[0] - l.from[0]) * dx + (p[1] - l.from[1]) * dy) / len2)) : 0;
    const d = Math.hypot(p[0] - (l.from[0] + u * dx), p[1] - (l.from[1] + u * dy));
    if (d < distance) { distance = d; index = i; along = u; length = Math.sqrt(len2); }
  });
  return index < 0 ? null : { index, distance, along, length };
}

/** Does a tie take the hover at its nearest point? Not at its two ends: there the pointer is on a grid's own point,
 * where all its ties meet, and the grid answers. An end is the last `end` units of the line, and never more than a
 * quarter of it, so a short tie still has a middle. */
export const onTheLine = (near: { along: number; length: number }, end: number) => {
  const cut = Math.min(end, near.length / 4), at = near.along * near.length;
  return at >= cut && at <= near.length - cut;
};

/** How full the batteries' ring is: the network's own rule (app/network/Network.tsx, nodeObject): half full at rest,
 * full when discharging at the period's most, nearly empty when charging at its most. */
export const batteryFill = (mw: number, max: number) => Math.max(0.02, Math.min(1, 0.5 + 0.5 * (mw / (max || 1))));

/** An arc of a circle as an SVG path: from the top, clockwise, `share` of the way round (the network's ring starts at
 * the top and runs the same way). */
export function arcPath(cx: number, cy: number, r: number, share: number): string {
  const f = Math.max(0, Math.min(1, share)), t = 2 * Math.PI * f;
  const n = (v: number) => Math.round(v * 100) / 100;
  // the whole circle is two halves: an arc that ends where it starts is not drawn
  if (f >= 0.999) return `M${n(cx)},${n(cy - r)}A${n(r)},${n(r)} 0 1 1 ${n(cx)},${n(cy + r)}A${n(r)},${n(r)} 0 1 1 ${n(cx)},${n(cy - r)}`;
  return `M${n(cx)},${n(cy - r)}A${n(r)},${n(r)} 0 ${f > 0.5 ? 1 : 0} 1 ${n(cx + r * Math.sin(t))},${n(cy - r * Math.cos(t))}`;
}

/** The map moved and zoomed: a point of the drawing stands at (point times k) plus (x, y), in the drawing's own units. */
export type MapView = { k: number; x: number; y: number };
export const MAP_ZOOM: readonly [number, number] = [1, 12];
export const MAP_HOME: MapView = { k: 1, x: 0, y: 0 };

/** A view the frame can show: the zoom inside its limits, and the drawing never pulled off the frame's edge. */
export function clampMapView(v: MapView, w: number, h: number): MapView {
  const k = Math.max(MAP_ZOOM[0], Math.min(MAP_ZOOM[1], v.k));
  const fit = (p: number, size: number) => Math.min(0, Math.max(size - size * k, p)) || 0;
  return { k, x: fit(v.x, w), y: fit(v.y, h) };
}

/** Zoom by a factor about a point of the frame, which stays where it is. */
export function zoomMapAt(v: MapView, factor: number, px: number, py: number, w: number, h: number): MapView {
  const k = Math.max(MAP_ZOOM[0], Math.min(MAP_ZOOM[1], v.k * factor));
  const r = k / v.k;
  return clampMapView({ k, x: px - (px - v.x) * r, y: py - (py - v.y) * r }, w, h);
}
