// Energy Research Warehouse (ERW) site, session 1423 (chain 111): the words of the network component's side panel
// (app/network/Network.tsx, the panel a picked grid opens beside the network, the map or the gravity shape) that write a
// MW: the grid's ties in the frame shown, their net and its demand. Moved here from the component with their arithmetic
// unchanged, so a node test (scripts/test-network-words.mjs) can compute them on the committed snapshot and compare each
// with the server panels grid_network_<grid> and grid_gravity_<grid> (components/grid/NetworkFigures.tsx, lib/gridKeys.ts)
// for the same tie and hour, as each writes it. The opening hour and the demand's check key stay in the component, where
// older tests pin their lines (sessions 54 and 124); the test runs those two lines' own text. What changed in the words (session 1423): in the live week a MW is written as the server panel
// writes it (lib/format.ts shown, passed in), and a net of exactly zero reads as an export, as the panel and
// lib/network.ts netValue sign it. A story and a replayed day are written as before (whole MW).
// No imports but types, so Node runs this file as it is.
import type { LiveExtras, NetLink, Snapshot } from "../app/network/Network";

/** One tie of the picked grid in a frame: the neighbour and the net import over the tie, MW (positive: the neighbour
 * supplies the grid). */
export type SideTie = { other: string; imp: number };

/** The picked grid's ties with a figure in frame `h`, largest import first (the panel's "Who is supplying it"). */
export function sideTies(links: NetLink[], id: string, h: number): SideTie[] {
  return links.filter((l) => l.a === id || l.b === id).map((l) => {
    const v = l.mw[h];
    if (v === null || v === undefined) return null;
    return { other: l.a === id ? l.b : l.a, imp: l.a === id ? -v : v };  // positive: the neighbour supplies this grid
  }).filter((x): x is SideTie => !!x).sort((x, y) => y.imp - x.imp);
}

/** The net import over the ties (negative: a net export). */
export function sideNet(ties: SideTie[]): number {
  return ties.reduce((a, t) => a + t.imp, 0);
}

/** How the side panel writes a MW. In the live week (its hours, California's evening among them) the server panel's own
 * way (`panel`, lib/format.ts shown: a whole number with separators, else two decimals), so a tie, the net and the demand
 * read as grid_network_<grid> writes them; in a story or the replay, whole MW as before (`whole`). */
export function sideFormat(kind: "live" | "story", panel: (v: number) => string, whole: (v: number) => string): (v: number) => string {
  return kind === "live" ? panel : whole;
}

/** The net's label: "Net imports this hour" when the grid imports on net, else "Net exports this hour". A zero reads as
 * an export, as the server panel ("sent out, on net, 0") and netValue (net|export, zero or more) sign it. */
export function sideNetLabel(net: number, unit: "hour" | "day"): string {
  return `Net ${net > 0 ? "imports" : "exports"} this ${unit}`;
}

/** The net's size without its sign (the label says which way): "1,234 MW". */
export function sideNetMw(net: number, f: (v: number) => string): string {
  return `${f(Math.abs(net))} MW`;
}

/** One tie's words: "1,234 MW in" (the neighbour supplies the grid), "1,234 MW out", or "0 MW". `exact` (the live week):
 * only a zero figure is "0 MW", as the server panel writes it ("0", direction none); otherwise a figure that rounds to
 * zero, as before. */
export function sideTieWords(imp: number, f: (v: number) => string, exact: boolean): string {
  const zero = exact ? imp === 0 : Math.round(imp) === 0;
  return zero ? "0 MW" : imp > 0 ? `${f(imp)} MW in` : `${f(-imp)} MW out`;
}

/** The live week's demand of a balancing authority in frame `h`: the seven ISOs' hourly demand of the week
 * (eia930_all_demand, live.demand), else the hourly snapshot's demand_recent, else the node's own newest demand in its
 * hour; null when none holds it. The order lib/gridKeys.ts demandAt reads them in. */
export function liveDemand(snap: Snapshot, live: LiveExtras, id: string, h: number): number | null {
  const n = snap.nodes.find((x) => x.id === id);
  const ts = snap.hours[h];
  if (!n) return null;
  const d = live.demand[id]?.[h];
  if (d !== null && d !== undefined) return d;  // the seven ISOs' hourly demand of the week (eia930_all_demand)
  if (n.demand_recent && ts in n.demand_recent) return n.demand_recent[ts];
  return n.demand_ts === ts ? n.demand_mw : null;
}
