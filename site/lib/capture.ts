// Energy Research Warehouse (ERW) site, session 145: the capture price of a solar and a wind plant at every public
// hub and zone, for "What a generator earns" (/cost-of-power/seller). The file data/seller/capture.json
// (warehouse/derived/capture_price.py) holds months; every figure the page shows is added up here, by the page, by
// scripts/check-seller.mjs and by scripts/test-capture.mjs alike. No imports: Node runs this file as it is.
// docs/methods/cost_of_power.md, "The capture price".
//
//   generation-weighted price = sum(price x generation) / sum(generation)
//   flat average              = sum(price) / hours, over the same hours
//   premium or discount       = the first less the second, in USD per MWh and as a percent of the flat average
//
// A month counts when the hours that hold both a price and the fuel's generation are at least `near` (95 percent) of
// the month's hours. A month that does not count is in no figure: nothing is filled or scaled.

/** One month: hours used, hours in the month, sum of the prices, sum of the generation (MWh), sum of price x generation. */
export type Rec = [number, number, number, number, number];
export type Months = Record<string, Rec>;
export type Fuel = "solar" | "wind";
export type Market = "rt" | "da";
export type Side = { basis: string; tables: string[]; first: string; last: string; hours: number; solar?: Months; wind?: Months };
export type Hub = { id: string; entity: string; rt?: Side; da?: Side };
export type Grid = { name: string; tz: string; main: string; workbook: string; generation: string[]; mix_first: string; mix_last: string; hubs: Hub[] };
export type CaptureFile = { built: string; method: string; near: number; tables: string[]; grids: Record<string, Grid>; blank: Record<string, { name: string; words: string }> };
export type Figure = { price: number; flat: number; premium: number; pct: number | null; hours: number; mwh: number };

export const FUELS: Fuel[] = ["solar", "wind"];
export const MARKETS: Record<Market, string> = { rt: "Real time", da: "Day-ahead" };
/** The grids in the order the page lists them: the public five, then the two that are blank. */
export const ORDER = ["ercot", "caiso", "nyiso", "isone", "spp", "miso", "pjm"] as const;

/** The sums of one span of hours: the hours in which both the price and the generation are held. Generation below zero
 *  (a plant's own use at night) weighs nothing and the hour stays in the flat average. */
export function weighted(prices: (number | null | undefined)[], generation: (number | null | undefined)[]): { n: number; sp: number; g: number; pg: number } {
  let n = 0, sp = 0, g = 0, pg = 0;
  for (let i = 0; i < prices.length; i++) {
    const p = prices[i], q = generation[i];
    if (p === null || p === undefined || q === null || q === undefined || !Number.isFinite(p) || !Number.isFinite(q)) continue;
    const w = Math.max(0, q);
    n += 1; sp += p; g += w; pg += p * w;
  }
  return { n, sp, g, pg };
}

export const counted = (r: Rec, near: number) => r[0] >= near * r[1] - 1e-9;

/** The capture figures of a list of months, or null when they hold no hour or no generation. */
export function figure(recs: Rec[]): Figure | null {
  let n = 0, sp = 0, g = 0, pg = 0;
  for (const r of recs) { n += r[0]; sp += r[2]; g += r[3]; pg += r[4]; }
  if (!n || g <= 0) return null;
  const price = pg / g, flat = sp / n;
  return { price, flat, premium: price - flat, pct: flat > 0 ? (100 * (price - flat)) / flat : null, hours: n, mwh: g };
}

const prevMonth = (m: string, k: number) => new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1 - k, 1)).toISOString().slice(0, 7);

/** The last twelve months: the newest counted month whose eleven months before it all count (the battery page's rule).
 *  The twelve month keys, oldest first; null when there are none. */
export function lastTwelve(months: Months | undefined, near: number): string[] | null {
  if (!months) return null;
  for (const m of Object.keys(months).sort().reverse()) {
    const twelve = Array.from({ length: 12 }, (_, k) => prevMonth(m, 11 - k));
    if (twelve.every((t) => months[t] && counted(months[t], near))) return twelve;
  }
  return null;
}

export type Span = Figure & { from: string; to: string };
/** The last twelve months' figures, with the span's first and last month. */
export function twelve(months: Months | undefined, near: number): Span | null {
  const t = lastTwelve(months, near);
  if (!t || !months) return null;
  const f = figure(t.map((m) => months[m]));
  return f ? { ...f, from: t[0], to: t[11] } : null;
}

export type YearFigure = { y: string; months: number; whole: boolean; f: Figure | null };
/** Each calendar year from its counted months: whole with twelve of them, else partial (and it holds those months only). */
export function years(months: Months | undefined, near: number): YearFigure[] {
  if (!months) return [];
  const out: YearFigure[] = [];
  for (const y of [...new Set(Object.keys(months).map((m) => m.slice(0, 4)))].sort()) {
    const ms = Object.keys(months).filter((m) => m.slice(0, 4) === y && counted(months[m], near));
    if (ms.length) out.push({ y, months: ms.length, whole: ms.length === 12, f: figure(ms.map((m) => months[m])) });
  }
  return out;
}

/** Why a hub has no last twelve months, in words for a hover: how many of its months count, and since when it is held. */
export function whyNot(side: Side | undefined, fuel: Fuel, near: number): string {
  if (!side) return "No price of this market is held for this hub.";
  const months = side[fuel];
  const since = `The price is held from ${side.first.slice(0, 10)} to ${side.last.slice(0, 10)}.`;
  if (!months) return `${since} The grid's ${fuel} generation is not held in any of those hours.`;
  const n = Object.values(months).filter((r) => counted(r, near)).length;
  if (lastTwelve(months, near)) return `${since} The grid's ${fuel} generation, as its source reports it, is zero in every one of those hours, so there is no generation to weigh a price by.`;
  return `${since} ${n} of its months hold at least ${Math.round(near * 100)} percent of their hours with both a price and the grid's ${fuel} generation; twelve in a row are needed.`;
}

/** The hub the address names when the grid holds it, else the grid's main hub. */
export function hubOf(file: CaptureFile, grid: string, asked: string | undefined): Hub | null {
  const g = file.grids[grid];
  if (!g) return null;
  return g.hubs.find((h) => h.id === asked) ?? g.hubs.find((h) => h.id === g.main) ?? g.hubs[0] ?? null;
}

const SHORT: Record<string, string> = {
  HB_HUBAVG: "Hub average", HB_BUSAVG: "Bus average", "TH_SP15_GEN-APND": "SP15", "TH_NP15_GEN-APND": "NP15", "TH_ZP26_GEN-APND": "ZP26",
  ".H.INTERNAL_HUB": "Internal hub", SPPNORTH_HUB: "North hub", SPPSOUTH_HUB: "South hub", "N.Y.C.": "New York City zone",
  ".Z.NEMASSBOST": "Northeast Massachusetts and Boston zone", ".Z.SEMASS": "Southeast Massachusetts zone", ".Z.WCMASS": "West and Central Massachusetts zone",
  ".Z.NEWHAMPSHIRE": "New Hampshire zone", ".Z.RHODEISLAND": "Rhode Island zone",
};
const title = (s: string) => s.toLowerCase().replace(/(^|\s)\S/g, (c) => c.toUpperCase());
/** A hub or zone's name as the page writes it, from the operator's own identifier. */
export function hubName(id: string): string {
  if (SHORT[id]) return SHORT[id];
  if (id.startsWith("HB_")) return `${title(id.slice(3))} hub`;
  if (id.startsWith("LZ_")) return `${id.slice(3).length <= 5 && !["HOUSTON", "NORTH", "SOUTH", "WEST"].includes(id.slice(3)) ? id.slice(3) : title(id.slice(3))} load zone`;
  if (id.startsWith(".Z.")) return `${title(id.slice(3))} zone`;
  return `${id} zone`;
}

/** The same name inside a sentence: "the West hub", "the hub average", "SP15". */
export function hubAt(id: string): string {
  const name = hubName(id);
  if (/^[A-Z]{2}\d+$/.test(name)) return name;
  return `the ${/^(Hub|Bus) average$/.test(name) ? name.toLowerCase() : name}`;
}

/** (d) where the curtailment page shows free energy for this hub. */
export const freeEnergyHref = (grid: string, hub: string) => `/curtailment?grid=${grid}&place=${encodeURIComponent(hub)}#free-energy`;

/** (b) the plant's last twelve months as the contract arithmetic takes them (lib/datacenter.ts, contractResult, whose
 *  share is of the energy and whose price is in USD per MWh): energy in MWh per MW, and what the market paid for it,
 *  the energy at the hub's generation-weighted price. */
export const contractSpan = (energyPerMw: number, capturePrice: number) => ({ cost: energyPerMw * capturePrice, energy: energyPerMw });

/** (c) a solar plant and a battery at one hub: two revenues added, nothing else. Null when either is not held. */
export function combined(plant: number | null, battery: number | null): number | null {
  return plant === null || battery === null ? null : plant + battery;
}

/** The widest premium and the widest discount of one fuel and market over every hub of every grid, last twelve months. */
export function widest(file: CaptureFile, fuel: Fuel, market: Market): { premium: { grid: string; hub: string; s: Span } | null; discount: { grid: string; hub: string; s: Span } | null } {
  let hi: { grid: string; hub: string; s: Span } | null = null, lo: { grid: string; hub: string; s: Span } | null = null;
  for (const [grid, g] of Object.entries(file.grids)) {
    for (const h of g.hubs) {
      const s = twelve(h[market]?.[fuel], file.near);
      if (!s) continue;
      if (!hi || s.premium > hi.s.premium) hi = { grid, hub: h.id, s };
      if (!lo || s.premium < lo.s.premium) lo = { grid, hub: h.id, s };
    }
  }
  return { premium: hi && hi.s.premium > 0 ? hi : null, discount: lo && lo.s.premium < 0 ? lo : null };
}

export const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
/** A premium or discount with its sign: "+3.20" or "-12.45" (a plain hyphen). */
export const signed = (v: number, digits = 2) => `${v < 0 ? "-" : "+"}${Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits })}`;
export const premiumWord = (v: number) => (v < 0 ? "discount" : "premium");
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
export const monthName = (m: string) => `${MON[Number(m.slice(5, 7)) - 1]} ${m.slice(0, 4)}`;
