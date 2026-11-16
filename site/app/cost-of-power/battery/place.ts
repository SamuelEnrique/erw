// Session 7519 (chain 304, part B: the page read as a merchant battery developer choosing between two ERCOT nodes;
// docs/reviews/battery-read-2026-11-16.md, rows 1 and 2). The tool prices energy at one place a grid (ERCOT's hub
// average, CAISO's SP15: lib/batterystack.ts, GRIDS). An address that named a hub, a zone or a node was shown the
// grid's one place with no word of it: session 263's rule (nothing the address asks for is replaced in silence) did
// not reach a name of a place, because the page reads no such parameter. This file says it, in the page's one status
// line, and holds the address of the site's list of ERCOT's settlement points by name. Pure: no React, no imports.

/** The address parameters a reader (or a link from a page that holds hubs and nodes) may name a place with. */
export const PLACE_PARAMS = ["hub", "node", "region", "zone", "point"] as const;
/** The All grids tab's list of ERCOT's settlement points, each by ERCOT's own name, two of them side by side as A and
 * B: day-ahead prices against the hub average, not a battery's income. */
export const NODE_LIST = "/cost-of-power?view=allgrids&rows=nodes";

type Grid = { id: string; name: string; hub?: string; at?: string; entity?: string };

/** One sentence when the address names a place the page does not show as asked; empty when it names none, or names
 * the grid's own place. The text the reader typed is never repeated. */
export function placeNotes(q: Record<string, string | undefined>, g: Grid): string[] {
  const named = PLACE_PARAMS.map((k) => q[k]).filter((v): v is string => typeof v === "string" && v.trim() !== "");
  if (!named.length) return [];
  const own = [g.hub, g.entity, g.entity?.split(":")[1]].filter((v): v is string => !!v).map((v) => v.toLowerCase());
  if (named.every((v) => own.includes(v.trim().toLowerCase()))) return [];
  const place = g.at ?? `${g.hub} hub`;
  const nodes = g.id === "ercot" ? " ERCOT's settlement points by name, two of them side by side, are on the All grids tab's node list: day-ahead prices against the hub average, not a battery's income." : "";
  return [`This tool prices energy at one place in ${g.name}, its ${place}: the hub, zone or node the address names is not held here, so the ${place} is shown.${nodes}`];
}
