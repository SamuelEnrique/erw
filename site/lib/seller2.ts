// Energy Research Warehouse (ERW) site, session 107: the seller's tab, version 2 (/cost-of-power/seller/v2, in review).
//
// The live seller tab's solar, wind and gas peaker, in the battery page's layout and in its framing: the last twelve
// months first, the long-run averages beside them and labeled as such. Every figure comes from the live tab's own
// model (lib/merchant.ts on data/merchant_snapshot.json), month by month; this file only adds the months up over a
// span. Nothing is filled: a span that is not whole is "not held".
// Session 145: version 2 is folded into the one page, /cost-of-power/seller, and its address redirects there. The spans
// are that page's now, for the battery (energy only, the model's 4-hour battery unless the reader sizes it) as well.

import { HEAT_RATE, VOM, months as merchantMonths, type Asset, type Inputs, type Month, type Snapshot } from "@/lib/merchant";

export type SellerAsset = Asset;
export const ASSETS: { id: SellerAsset; name: string; noun: string }[] = [
  { id: "solar", name: "Solar", noun: "a merchant solar plant" },
  { id: "wind", name: "Wind", noun: "a merchant wind plant" },
  { id: "battery", name: "Battery", noun: "a merchant battery selling energy alone" },
  { id: "peaker", name: "Gas peaker", noun: "a merchant gas peaker" },
];
/** The grids of the page, with the hub each is priced at, in words. MISO is not here: its pulls are paused since
 *  4 October 2026 and its terms forbid derivative works, so the page shows no figure of its prices (session 96's
 *  reading, as on /prices/compare and the price board). */
export const GRIDS: { id: string; name: string; at: string }[] = [
  { id: "ercot", name: "ERCOT", at: "the hub average" },
  { id: "caiso", name: "CAISO", at: "SP15" },
  { id: "nyiso", name: "NYISO", at: "the New York City zone" },
  { id: "spp", name: "SPP", at: "the North hub" },
  { id: "isone", name: "ISO-NE", at: "the Internal hub" },
];
export const PAUSED = { name: "MISO", words: "MISO is not shown: its pulls are paused since 4 October 2026 while a person reviews its terms, which forbid automated access and derivative works." };

export type Choice = { grid: string; asset: SellerAsset };
export function choiceOf(q: Record<string, string | undefined>): Choice {
  return { grid: GRIDS.some((g) => g.id === q.iso) ? (q.iso as string) : "ercot", asset: ASSETS.some((a) => a.id === q.asset) ? (q.asset as SellerAsset) : "solar" };
}
export const href = (c: Choice) => `/cost-of-power/seller?iso=${c.grid}&asset=${c.asset}`;

/** The months of one grid and asset from the live tab's model, per MW of nameplate, at the model's defaults. */
export function monthsOf(snap: Snapshot, c: Choice): Month[] {
  const x: Inputs = { iso: c.grid, asset: c.asset, mw: 1, mwh: c.asset === "battery" ? 4 : 0, ds: 0, hr: HEAT_RATE, vom: VOM, fom: 0 };
  return merchantMonths(snap, x);
}

const prevMonth = (m: string, k: number) => new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1 - k, 1)).toISOString().slice(0, 7);
/** The last twelve months: the newest held month whose eleven months before it are all held (the battery page's rule). */
export function lastTwelve(ms: Month[]): Month[] | null {
  const by = new Map(ms.map((r) => [r.m, r]));
  for (const r of [...ms].reverse()) {
    if (!r.held) continue;
    const twelve = Array.from({ length: 12 }, (_, k) => by.get(prevMonth(r.m, k)));
    if (twelve.every((t) => t && t.held)) return (twelve as Month[]).reverse();
  }
  return null;
}

export type Year = { y: string; months: number; complete: boolean; revenue: number };
/** Revenue by calendar year per MW, the held months only; a year is complete when all twelve of its months are held. */
export function years(ms: Month[]): Year[] {
  const out = new Map<string, Year>();
  for (const r of ms) {
    if (!r.held) continue;
    const y = r.m.slice(0, 4);
    if (!out.has(y)) out.set(y, { y, months: 0, complete: false, revenue: 0 });
    const t = out.get(y)!;
    t.months += 1; t.revenue += r.revenue;
  }
  return [...out.values()].map((t) => ({ ...t, complete: t.months === 12 })).sort((a, b) => a.y.localeCompare(b.y));
}
export const fullYears = (ms: Month[]) => years(ms).filter((y) => y.complete).map((y) => y.y);
/** The last three full calendar years, when all three are held. */
export function lastThreeYears(ms: Month[]): string[] | null {
  const full = fullYears(ms);
  const newest = full.at(-1);
  if (!newest) return null;
  const want = [0, 1, 2].map((k) => String(Number(newest) - k)).reverse();
  return want.every((y) => full.includes(y)) ? want : null;
}

export type Span = {
  months: number; years: number;       // months in the span; the years it is averaged over (1 for the last twelve months)
  revenue_kw: number;                   // USD per kW of nameplate, a year (the peaker's is its margin over fuel and variable cost)
  energy: number;                       // MWh per MW, a year
  capture: number | null;               // USD per MWh sold: sales over energy, over the span
  flat: number;                         // USD per MWh: the mean of the months' all-hours prices
  rate: number | null;                  // capture over flat, percent
  from: string; to: string;
};
/** One span's figures from its months, a year: sums over the number of years the span covers. */
export function spanOf(ms: Month[], yearsCovered: number): Span | null {
  if (!ms.length) return null;
  const revenue = ms.reduce((a, r) => a + r.revenue, 0), energy = ms.reduce((a, r) => a + r.energy, 0);
  const sales = ms.reduce((a, r) => a + (r.capture !== null ? r.capture * r.energy : 0), 0);
  const flat = ms.reduce((a, r) => a + r.flat, 0) / ms.length;
  const capture = energy > 0 ? sales / energy : null;
  return { months: ms.length, years: yearsCovered, revenue_kw: revenue / yearsCovered / 1000, energy: energy / yearsCovered, capture, flat,
    rate: capture !== null && flat ? (100 * capture) / flat : null, from: ms[0].m, to: ms[ms.length - 1].m };
}
/** The three spans of the page: the last twelve months, the last three full years (a long-run average), every full year held (a long-run average). */
export function spans(ms: Month[]): { twelve: Span | null; three: Span | null; threeYears: string[] | null; every: Span | null; everyYears: string[] } {
  const t = lastTwelve(ms);
  const ys = lastThreeYears(ms);
  const full = fullYears(ms);
  const held = (yy: string[]) => ms.filter((r) => r.held && yy.includes(r.m.slice(0, 4)));
  return { twelve: t ? spanOf(t, 1) : null, three: ys ? spanOf(held(ys), 3) : null, threeYears: ys, every: full.length ? spanOf(held(full), full.length) : null, everyYears: full };
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
export const monthName = (m: string) => `${MONTHS[Number(m.slice(5, 7)) - 1]} ${m.slice(0, 4)}`;
export const usd = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
export const whole = (v: number) => Math.round(v).toLocaleString("en-US");

/** The summary sentence. Null when the last twelve months are not held. */
export function sentence(c: Choice, s: ReturnType<typeof spans>): string | null {
  if (!s.twelve) return null;
  const g = GRIDS.find((x) => x.id === c.grid)!, a = ASSETS.find((x) => x.id === c.asset)!;
  const what = c.asset === "peaker" ? "a margin over fuel of" : "";
  const long = s.three
    ? ` The long-run average of ${s.threeYears![0]} to ${s.threeYears![2]} was USD ${usd(s.three.revenue_kw)} a year${s.every && s.everyYears.length > 3 ? `, and of the ${s.everyYears.length} full years held (${s.everyYears[0]} to ${s.everyYears.at(-1)}) USD ${usd(s.every.revenue_kw)}` : ""}.`
    : s.every
      ? s.everyYears.length === 1
        ? ` ${g.name} holds one full year, ${s.everyYears[0]}: USD ${usd(s.every.revenue_kw)}. There is no long-run average yet.`
        : ` ${g.name} holds ${s.everyYears.length} full years (${s.everyYears[0]} to ${s.everyYears.at(-1)}); their average was USD ${usd(s.every.revenue_kw)} a year. Three are needed for the three-year average.`
      : ` ${g.name} holds no full calendar year yet, so there is no long-run average.`;
  return `Over the last twelve months, ${monthName(s.twelve.from)} to ${monthName(s.twelve.to)}, ${a.noun} in ${g.name} priced at ${g.at} earned ${what ? `${what} ` : ""}USD ${usd(s.twelve.revenue_kw)} per kW.${long}`;
}
