// Energy Research Warehouse (ERW) site, ruling alternative 1 of /grid (session 7725, 17 November 2026; branch
// wip/alt-grid-1, not a default on main): the Mix tab's three lead figures (demand, the exchange, carbon) at one hour, the
// newest hour all three hold: the oldest of their three newest hours, taken only when the network snapshot holds that hour
// (the exchange is read from it). On main each stands at its own newest hour, its hour printed. No imports.

/** The hour the three figures share, or null (each then keeps its own newest hour). Hours are ISO strings in UTC. */
export function alignHour(newest: (string | null | undefined)[], snapshotHours: string[]): string | null {
  const ts = newest.filter((h): h is string => !!h).map((h) => Date.parse(h));
  if (ts.length < 2) return null;
  const at = new Date(Math.min(...ts)).toISOString().replace(/\.\d{3}Z$/, "Z");
  return snapshotHours.some((h) => Date.parse(h) === Date.parse(at)) ? at : null;
}
