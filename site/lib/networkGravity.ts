// Energy Research Warehouse (ERW) site, session 266 (the owner's task of 14 October 2026): the gravity shape of the
// Grid tool's Network view, beside "Map" and "Network". The parts with no drawing in them, so a test can run them in
// Node (no imports).
// The rule (docs/methods/grid_network.md, "The gravity shape (session 266)"): the Lower 48 (EIA-930's US48) is a circle
// at the center; each of the seven ISO grids is a circle around it, its AREA proportional to its net generation in the
// hour shown (eia930_all_generation, net_generation_mw; the Lower 48's own sets the scale), on a fixed bearing that
// follows the map (CAISO to the west, ISO-NE to the north-east). Its distance from the center follows its net imports
// over its reporting ties in that hour, as a share of its generation: a net importer is pulled in, a net exporter pushed
// out, a grid that neither imports nor exports on net sits on the middle ring. Nothing is drawn from a stand-in: a grid
// whose generation is not held for the hour is an empty outline on the middle ring, and the line under the frame says so.

/** The seven ISO grids, their EIA-930 codes, and the bearing each is drawn on (degrees clockwise from north). */
export const GRAVITY_GRIDS: { id: string; label: string; bearing: number }[] = [
  { id: "CISO", label: "CAISO", bearing: 262 },
  { id: "SWPP", label: "SPP", bearing: 318 },
  { id: "MISO", label: "MISO", bearing: 8 },
  { id: "ISNE", label: "ISO-NE", bearing: 40 },
  { id: "NYIS", label: "NYISO", bearing: 66 },
  { id: "PJM", label: "PJM", bearing: 104 },
  { id: "ERCO", label: "ERCOT", bearing: 196 },
];
export const GRAVITY_CENTER = "US48";

/** The frame (a square of SIZE units), the Lower 48's radius, the middle ring, how far a full pull moves a grid, and the
 * share of its generation at which the pull is full. */
export const GRAVITY = { SIZE: 640, R_CENTER: 80, D_MID: 205, D_SPAN: 90, S_FULL: 0.25, R_MIN: 6, GAP: 4 };

export type GravityState = "drawn" | "no-ties" | "zero-generation" | "no-generation";
export type GravityPlace = {
  id: string; label: string;
  /** net generation in the hour, MW; null when not held */
  gen: number | null;
  /** net imports over the reporting ties in the hour, MW (negative: a net export); null when no tie reported */
  net: number | null;
  /** net imports as a share of generation (0.1 is ten percent); null when either is missing or generation is zero */
  share: number | null;
  r: number; d: number; x: number; y: number; state: GravityState;
};
export type GravityLayout = { center: { gen: number | null; r: number; x: number; y: number }; places: GravityPlace[] };

const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));

/** Where each grid sits and how large it is, from the hour's generation (MW, by code, US48 included) and net imports
 * (MW, by code; null or missing: no tie reported in the hour). */
export function gravityLayout(gen: Record<string, number | null | undefined>, netImport: Record<string, number | null | undefined>): GravityLayout {
  const { SIZE, R_CENTER, D_MID, D_SPAN, S_FULL, R_MIN, GAP } = GRAVITY;
  const c = SIZE / 2;
  const g0 = gen[GRAVITY_CENTER] ?? null;
  // the scale: the Lower 48's generation; when it is not held, the largest of the seven (so the drawing still shows sizes relative to one another)
  const held = GRAVITY_GRIDS.map((g) => gen[g.id]).filter((v): v is number => typeof v === "number" && v > 0);
  const scale = g0 !== null && g0 > 0 ? g0 : held.length ? Math.max(...held) : 1;
  const places = GRAVITY_GRIDS.map((g): GravityPlace => {
    const gv = gen[g.id];
    const gi = typeof gv === "number" ? gv : null;
    const nv = netImport[g.id];
    const net = typeof nv === "number" ? nv : null;
    let state: GravityState = "drawn";
    let r = R_MIN, pull = 0, share: number | null = null;
    if (gi === null) state = "no-generation";
    else if (gi <= 0) state = "zero-generation";
    else r = Math.max(R_MIN, R_CENTER * Math.sqrt(gi / scale));
    if (net === null) { if (state === "drawn") state = "no-ties"; }
    else if (gi !== null && gi > 0) { share = net / gi; pull = clamp(share / S_FULL, -1, 1); }
    else if (gi !== null && net !== 0) pull = Math.sign(net);   // no generation and a net import: the full pull, either way
    // a net importer (pull > 0) is drawn nearer the center; never on top of the Lower 48, never outside the frame
    const d = clamp(D_MID - D_SPAN * pull, R_CENTER + r + GAP, c - r - GAP);
    const b = (g.bearing * Math.PI) / 180;
    return { id: g.id, label: g.label, gen: gi, net, share, r, d, x: c + d * Math.sin(b), y: c - d * Math.cos(b), state };
  });
  return { center: { gen: g0, r: R_CENTER, x: c, y: c }, places };
}

/** A grid's net imports in one frame of the view, summed over its ties as the panel sums them (positive: it imports). */
export function netImportAt(links: { a: string; b: string; mw: (number | null)[] }[], id: string, h: number): number | null {
  let sum = 0, n = 0;
  for (const l of links) {
    if (l.a !== id && l.b !== id) continue;
    const v = l.mw[h];
    if (v === null || v === undefined) continue;
    sum += l.a === id ? -v : v;
    n += 1;
  }
  return n ? sum : null;
}
