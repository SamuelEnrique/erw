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
