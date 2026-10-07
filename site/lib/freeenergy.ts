// Energy Research Warehouse (ERW) site, session 144: the arithmetic of the curtailment page's two new sections, "Where
// free energy is" (data/curtailment/free_energy.json, warehouse/derived/free_energy.py) and "What it is worth"
// (data/curtailment/worth.json, warehouse/derived/curtailment_worth.py), and of the monthly shares
// (data/curtailment/shares.json, warehouse/derived/curtailment_shares.py). Pure functions, no imports: node runs this
// file as it is (scripts/test-freeenergy.mjs). Nothing here fills, scales or invents a figure: a figure the files do
// not hold comes back null, with the file's own reason where it gives one.

// ---- the files' shapes -------------------------------------------------------------------------------------------

/** A location's window when it is whole: its market ("rt" real time, "da" day-ahead), hours, and the two counts. */
export type Held = { basis: "rt" | "da"; hours_in_window: number; hours_held: number; negative: number; under5: number; mean: number };
/** A window that is not whole: the reason, and no count. */
export type NotHeld = { missing: string; hours_in_window: number; rt_hours_held?: number; da_hours_held?: number };
export type Win = Held | NotHeld;
export type Heat = { basis: "rt" | "da"; whole: boolean; hours_held: number; under5: number[][]; negative: number[][]; held: number[][] };
export type Loc = { id: string; entity: string; kind: "hub" | "zone" | "average"; geo: string; lat: number | null; lon: number | null; month: Win; year: Win; heat: Heat };
export type Side = { mean: number; negative: number; under5: number };
export type Gap = { basis: "rt" | "da"; hours_common: number; hours_in_window: number; places: string[]; cheapest: Side & { id: string }; dearest: Side & { id: string }; gap: number; by_place: Record<string, Side> }
  | { missing: string; hours_in_window: number };
export type Pair = { basis: "rt" | "da"; hours_common: number; hours_in_window: number; a: Side; b: Side; mean_b_less_a: number; hours_a_under5_b_not: number; hours_b_under5_a_not: number }
  | { missing: string; hours_in_window: number };
export type Grid = { name: string; std_hours_behind_utc: number; std_name: string; locations: Loc[]; gap: { month: Gap; year: Gap } };
export type Blank = { name: string; words: string; regions: string[] };
export type FreeFile = {
  built: string; end_month: string; year_months: string[]; threshold_usd_per_mwh: number; near_hours: number;
  grids: Record<string, Grid>; blank: Record<string, Blank>;
  compare: Record<string, { words: string; grid?: string; missing?: string; hub?: { a: string; b: string; month: Pair; year: Pair }; zone?: { a: string; b: string; month: Pair; year: Pair } }>;
};
export type WindowName = "month" | "year";

// ---- the face: one line per grid saying what its number is -------------------------------------------------------

/** Whose number each grid's figure is. The caveat paragraphs are in the Method note. */
export const FACE: Record<string, { whose: "operator" | "estimate" | "none"; line: string }> = {
  caiso: { whose: "operator", line: "CAISO's own figure: the wind and solar energy its market or its operators turned down." },
  spp: { whose: "operator", line: "SPP's own figure: the wind and solar energy curtailed in its balancing authority area. The share is the ERW's, on EIA's hourly output." },
  ercot: { whose: "estimate", line: "The ERW's estimate: output below the limit the plants reported they could sustain. ERCOT publishes no curtailment figure." },
  isone: { whose: "operator", line: "ISO-NE's own figure, by month only: the undelivered energy of its dispatchable wind and solar plants. Not yet in the ERW." },
  nyiso: { whose: "operator", line: "NYISO prints a monthly figure in a report, as a document and not as data. Not in the ERW." },
  miso: { whose: "none", line: "Paused while terms are reviewed." },
  pjm: { whose: "none", line: "Licensed source needed." },
};

// ---- shares ------------------------------------------------------------------------------------------------------

/** Curtailed over curtailed plus output, in percent: null unless both are held, neither is negative and the output is
 * more than nothing. It cannot pass 100. */
export function share(curtailed: number | null | undefined, output: number | null | undefined): number | null {
  if (curtailed === null || curtailed === undefined || output === null || output === undefined) return null;
  if (!Number.isFinite(curtailed) || !Number.isFinite(output) || curtailed < 0 || output <= 0) return null;
  return (100 * curtailed) / (curtailed + output);
}

/** A part of a whole in percent, or null when the whole is nothing. */
export const pct = (part: number, whole: number): number | null => (whole > 0 ? (100 * part) / whole : null);

// ---- where free energy is ----------------------------------------------------------------------------------------

export const isHeld = (w: Win): w is Held => (w as Held).basis !== undefined;
/** The hours priced from zero to under the threshold: the hours under it less the hours below zero (each hour once). */
export const zeroToFive = (w: Held): number => w.under5 - w.negative;
/** The share of the hours held that were under the threshold, percent. */
export const cheapShare = (w: Held): number | null => pct(w.under5, w.hours_held);

/** A grid's places with a count in the window, most hours under the threshold first; an average of hubs is not a place. */
export function ranked(g: Grid, w: WindowName): (Loc & { win: Held })[] {
  return g.locations.filter((l) => l.kind !== "average" && isHeld(l[w])).map((l) => ({ ...l, win: l[w] as Held }))
    .sort((a, b) => b.win.under5 - a.win.under5 || b.win.negative - a.win.negative || a.id.localeCompare(b.id));
}
/** The places of a grid with no count in the window, each with the file's reason. */
export function notHeld(g: Grid, w: WindowName): { id: string; reason: string }[] {
  return g.locations.filter((l) => !isHeld(l[w])).map((l) => ({ id: l.id, reason: (l[w] as NotHeld).missing }));
}
/** How dark a point is drawn, from 0 to 1: its count against the most of any place shown. 0 when none has an hour. */
export const shade = (count: number, most: number): number => (most > 0 ? Math.min(1, Math.max(0, count / most)) : 0);
/** The most hours under the threshold of any place in any grid, in the window: the scale of the map's shading. */
export function mostCheap(f: FreeFile, w: WindowName): number {
  return Math.max(0, ...Object.values(f.grids).flatMap((g) => ranked(g, w).map((l) => l.win.under5)));
}

/** The heatmap's largest cell, for its color scale. */
export const heatMost = (h: Heat, key: "under5" | "negative"): number => Math.max(0, ...h[key].flat());
/** A month's row of the heatmap added up: the month's hours under the threshold (or below zero, or held). */
export const heatMonth = (h: Heat, key: "under5" | "negative" | "held", month: number): number => h[key][month].reduce((a, v) => a + v, 0);
/** The whole heatmap added up. When the year is whole this is the year's count: an hour is in one cell and no other. */
export const heatTotal = (h: Heat, key: "under5" | "negative" | "held"): number => h[key].reduce((a, row) => a + row.reduce((b, v) => b + v, 0), 0);
/** An hour of the day summed over the twelve months. */
export const heatHour = (h: Heat, key: "under5" | "negative" | "held", hour: number): number => h[key].reduce((a, row) => a + row[hour], 0);
/** A cell's hover text: the count, of the hours held in that cell; "not held" when the cell holds no hour. */
export function cellText(h: Heat, months: string[], month: number, hour: number): string {
  const held = h.held[month][hour];
  if (!held) return `${months[month]}, ${hourName(hour)}: not held`;
  return `${months[month]}, ${hourName(hour)}: ${h.under5[month][hour]} of ${held} hours under USD 5, ${h.negative[month][hour]} below zero`;
}
/** The hour of the day as it is written: "00:00" to "23:00". */
export const hourName = (h: number): string => `${String(h).padStart(2, "0")}:00`;

export const hasGap = (g: Gap): g is Extract<Gap, { gap: number }> => (g as { gap?: number }).gap !== undefined;
export const hasPair = (p: Pair): p is Extract<Pair, { basis: string }> => (p as { basis?: string }).basis !== undefined;

/** The grid with the widest gap between its cheapest and dearest place in the window, or null when none has two. */
export function widestGap(f: FreeFile, w: WindowName): { grid: string; gap: number; cheapest: string; dearest: string } | null {
  let best: { grid: string; gap: number; cheapest: string; dearest: string } | null = null;
  for (const [id, g] of Object.entries(f.grids)) {
    const x = g.gap[w];
    if (hasGap(x) && (best === null || x.gap > best.gap)) best = { grid: id, gap: x.gap, cheapest: x.cheapest.id, dearest: x.dearest.id };
  }
  return best;
}

/** What the summary sentence needs: West Texas against Houston and California north against south, for a window.
 * Load zones when they are held, otherwise the hubs; a pair not held is null. */
export function summaryPairs(f: FreeFile, w: WindowName): { texas: { kind: "zone" | "hub"; west: Side; houston: Side; hours: number } | null; california: { north: Side; south: Side; hours: number } | null } {
  const t = f.compare.west_texas_houston, c = f.compare.california_north_south;
  let texas: { kind: "zone" | "hub"; west: Side; houston: Side; hours: number } | null = null;
  for (const kind of ["zone", "hub"] as const) {
    const p = t?.[kind]?.[w];
    if (p && hasPair(p)) { texas = { kind, west: p.a, houston: p.b, hours: p.hours_common }; break; }
  }
  const p = c?.hub?.[w];
  return { texas, california: p && hasPair(p) ? { north: p.a, south: p.b, hours: p.hours_common } : null };
}

/** A grid that is named and shown blank: its words, and never a number. */
export const blankWords = (f: FreeFile, id: string): string | null => f.blank[id]?.words ?? null;

// ---- what it is worth --------------------------------------------------------------------------------------------

export type WorthMonth = {
  hours_priced: number; hours_in_month?: number; curtailed_mwh: number; curtailed_mwh_priced: number; value_usd?: number; usd_per_mwh_curtailed?: number;
  share_mwh_negative_pct?: number; share_mwh_under5_pct?: number; price_all_hours_mean?: number; price_curtailed_hours_mean?: number;
};
/** What a flat 1 MW load running only in the curtailed hours pays against one running every hour: the two mean prices
 * and the difference, USD per MWh; null when the month has no curtailed hour with a price. */
export function flatLoad(m: WorthMonth): { curtailedHours: number; allHours: number; less: number } | null {
  if (m.price_curtailed_hours_mean === undefined || m.price_all_hours_mean === undefined) return null;
  return { curtailedHours: m.price_curtailed_hours_mean, allHours: m.price_all_hours_mean, less: m.price_all_hours_mean - m.price_curtailed_hours_mean };
}
/** The dollars again from the file's two figures, for a check: MWh priced times USD per MWh curtailed. */
export const valueAgain = (m: WorthMonth): number | null => (m.usd_per_mwh_curtailed === undefined ? null : m.curtailed_mwh_priced * m.usd_per_mwh_curtailed);
/** What a battery of `hours` hours per MW took in at most in `days` days: one cycle a day. */
export const batteryCeiling = (hours: number, days: number): number => hours * days;
/** The share of that ceiling the rule reached, percent. */
export const batteryFill = (absorbedPerMw: number, hours: number, days: number): number | null => pct(absorbedPerMw, batteryCeiling(hours, days));
/** A ratio of two energies in percent, not bounded by 100 (the fleet may charge more in those hours than was curtailed). */
export const ratio = (a: number | undefined, b: number | undefined): number | null => (a === undefined || b === undefined || b <= 0 ? null : (100 * a) / b);
