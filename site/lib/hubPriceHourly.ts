// Energy Research Warehouse (ERW) site, session 1402 (chain 100): the hub's real-time price beside the Grid tool's
// hourly mix (the Mix tab, under the 7-day chart of session 1152's panel grid_mix_<grid>), for the grids whose hub
// prices are public (site/lib/license.ts: ERCOT, CAISO and SPP; iso_rtm_hub_prices is held for MISO only). Pure
// functions, no import, so a node test and scripts/check-values.mjs load this file as it is (scripts/test-hub-price.mjs).
//
// The price: iso_rtm_hub_prices, the grid's hub as the site names it (docs/grids/grids.json `hub`), 15-minute rows.
// An hour's price is the mean of its four 15-minute prices, used only when all four are held: the rule of
// docs/methods/cost_of_power.md ("An hour's price is the mean of its intervals ... used only when every interval of
// the hour is present"), the hours floored in UTC. Nothing is filled: an hour with a missing interval has no price.
// The window: the 7 days the hourly chart draws (chartWindow, the rule of components/mix/Now.tsx Hourly: the last 7
// UTC days of the 9 read whose 24 hours hold net_generation_mw, to the newest hour held when that is later); where no
// chart is drawn (CAISO's hourly mix is withheld by the session 118 ruling; a failed generation read) the 7 UTC days
// that end with the price's newest day whose 24 hours are held whole (priceWindow).
// The figures written on the page, each a key scripts/check-values.mjs recomputes with hubHourStat on the table's rows:
//   series_hn|<table>|<variable>|<start>|<end>|<entity>     the hours of the window held whole
//   series_hmean|<table>|<variable>|<start>|<end>|<entity>  the mean of those hours' prices (the week's mean); over a
//                                                           one-hour window, that hour's price (the last hour held)
//   series_hmax|<table>|<variable>|<start>|<end>|<entity>   the highest of those hours' prices
// The hours' prices drawn in the strip and named on hover are not written figures.

export const RT_HUB_TABLE = "iso_rtm_hub_prices";
const H = 3_600_000;
const DAY = 24 * H;
const Q = 15 * 60_000;

/** A grid's hub in iso_rtm_hub_prices: its entity and variable, the hub's short name and the site's label for it. */
export type HubOf = { grid: string; entity: string; variable: string; hub: string; label: string };
export const HUB_PRICE: Record<string, HubOf> = {
  ercot: { grid: "ercot", entity: "ercot:HB_HUBAVG", variable: "spp_rtm", hub: "HB_HUBAVG", label: "ERCOT Hub Average (HB_HUBAVG)" },
  caiso: { grid: "caiso", entity: "caiso:TH_SP15_GEN-APND", variable: "lmp_rtm_15m_mean", hub: "SP15", label: "SP15, Southern California (TH_SP15_GEN-APND)" },
  spp: { grid: "spp", entity: "spp:SPPNORTH_HUB", variable: "lmp_rtm_15m_mean", hub: "SPPNORTH_HUB", label: "SPP North Hub (SPPNORTH_HUB)" },
};

export type PriceRow = { ts_utc: string; value: number; entity?: string; variable?: string };
export type Fig = { check: string; raw: number; tip: string };
export type HourPrice = { t: number; mean: number };

export const isoZ = (t: number) => new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");
export const hourName = (t: number) => `${new Date(t).toISOString().slice(0, 13).replace("T", " ")}:00 UTC`;
const dayOf = (t: number) => new Date(t).toISOString().slice(0, 10);

/** Each hour of [start, end) whose four 15-minute prices are all held, and its price, the mean of the four; in time
 *  order. An interval written twice is held once (its last row). */
export function hourMeans(rows: PriceRow[], start = -Infinity, end = Infinity): HourPrice[] {
  const by = new Map<number, Map<number, number>>();
  for (const r of rows) {
    const t = Date.parse(r.ts_utc);
    if (!Number.isFinite(t) || t < start || t >= end || typeof r.value !== "number" || !Number.isFinite(r.value)) continue;
    const h = Math.floor(t / H) * H;
    if ((t - h) % Q) continue;   // not a quarter hour's start
    const m = by.get(h) ?? new Map<number, number>();
    m.set(t, r.value);
    by.set(h, m);
  }
  const out: HourPrice[] = [];
  for (const [t, m] of by) if (m.size === 4) out.push({ t, mean: [...m.values()].reduce((a, v) => a + v, 0) / 4 });
  return out.sort((a, b) => a.t - b.t);
}

/** A key's value, as check-values recomputes it: over the hours of [start, end) held whole, "n" the count, "mean" the
 *  mean of their prices, "max" the highest; undefined for "mean" and "max" when no hour is held. */
export function hubHourStat(rows: PriceRow[], stat: string, start: string, end: string): number | undefined {
  const hs = hourMeans(rows, Date.parse(start), Date.parse(end));
  if (stat === "n") return hs.length;
  if (!hs.length) return undefined;
  if (stat === "mean") return hs.reduce((a, h) => a + h.mean, 0) / hs.length;
  if (stat === "max") return Math.max(...hs.map((h) => h.mean));
  throw new Error(`unknown statistic ${stat}`);
}

/** The window the hourly chart draws (components/mix/Now.tsx Hourly, the same rule): the last 7 UTC days whose 24
 *  hours hold net_generation_mw, to the end of the last of them or to the end of the newest hour held (`through`),
 *  whichever is later; null when no day is complete. */
export function chartWindow(gen: { variable: string; ts_utc: string }[], through?: number): { t0: number; t1: number } | null {
  const nh = new Map<string, number>();
  for (const r of gen) if (r.variable === "net_generation_mw") nh.set(r.ts_utc.slice(0, 10), (nh.get(r.ts_utc.slice(0, 10)) ?? 0) + 1);
  const days = Array.from(nh.entries()).filter(([, n]) => n === 24).map(([d]) => d).sort().slice(-7);
  if (!days.length) return null;
  const t0 = Date.parse(`${days[0]}T00:00:00Z`), t1 = Math.max(Date.parse(`${days[days.length - 1]}T00:00:00Z`) + DAY, through === undefined ? 0 : through + H);
  return { t0, t1 };
}

/** The price's own window, where no chart is drawn: the 7 UTC days that end with the newest day whose 24 hours are all
 *  held whole (an hour of them not held is a gap in the strip, never filled). */
export function priceWindow(rows: PriceRow[]): { t0: number; t1: number } | null {
  const n = new Map<string, number>();
  for (const h of hourMeans(rows)) n.set(dayOf(h.t), (n.get(dayOf(h.t)) ?? 0) + 1);
  const days = [...n.entries()].filter(([, k]) => k === 24).map(([d]) => d).sort();
  if (!days.length) return null;
  const t1 = Date.parse(`${days[days.length - 1]}T00:00:00Z`) + DAY;
  return { t0: t1 - 7 * DAY, t1 };
}

export type HubPrice = {
  hub: HubOf;
  t0: number;
  t1: number;
  /** the hours of the window (each hour's start), and the hour's price or null where it is not held whole */
  points: [number, number | null][];
  /** the hours of the window held whole, keyed */
  n: Fig;
  /** the hours in the window */
  of: number;
  mean: Fig | null;
  max: { t: number; fig: Fig } | null;
  latest: { t: number; fig: Fig } | null;
};

/** The strip's hours and the figures written under it, for one grid's hub over [t0, t1). */
export function hubPrice(rows: PriceRow[], hub: HubOf, w: { t0: number; t1: number }): HubPrice {
  const { t0, t1 } = w;
  const mine = rows.filter((r) => (r.entity === undefined || r.entity === hub.entity) && (r.variable === undefined || r.variable === hub.variable));
  const hs = hourMeans(mine, t0, t1);
  const at = new Map(hs.map((h) => [h.t, h.mean]));
  const points: [number, number | null][] = [];
  for (let t = t0; t < t1; t += H) points.push([t, at.get(t) ?? null]);
  const key = (kind: string, a: number, b: number) => `${kind}|${RT_HUB_TABLE}|${hub.variable}|${isoZ(a)}|${isoZ(b)}|${hub.entity}`;
  const span = `${hourName(t0)} to ${hourName(t1)}`;
  const src = `${RT_HUB_TABLE}, ${hub.entity}, ${hub.variable}`;
  const rule = "an hour's price is the mean of its four 15-minute prices, held only when all four are";
  const n: Fig = { check: key("series_hn", t0, t1), raw: hs.length, tip: `${src}: the hours from ${span} whose four 15-minute prices are all held` };
  const mean: Fig | null = hs.length ? { check: key("series_hmean", t0, t1), raw: hubHourStat(mine, "mean", isoZ(t0), isoZ(t1))!, tip: `${src}: the mean of the hours held from ${span} (${rule}): USD per MWh` } : null;
  let max: HubPrice["max"] = null, latest: HubPrice["latest"] = null;
  if (hs.length) {
    const top = hs.reduce((a, h) => (h.mean > a.mean ? h : a));   // the first on a tie
    max = { t: top.t, fig: { check: key("series_hmax", t0, t1), raw: top.mean, tip: `${src}: the highest hour of the hours held from ${span}, the hour from ${hourName(top.t)} (${rule}): USD per MWh` } };
    const last = hs[hs.length - 1];
    latest = { t: last.t, fig: { check: key("series_hmean", last.t, last.t + H), raw: hubHourStat(mine, "mean", isoZ(last.t), isoZ(last.t + H))!, tip: `${src}: the hour from ${hourName(last.t)}, the last hour of the window held (${rule}): USD per MWh` } };
  }
  return { hub, t0, t1, points, n, of: points.length, mean, max, latest };
}
