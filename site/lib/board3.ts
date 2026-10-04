// Energy Research Warehouse (ERW) site, session 104: the price board, version 3 (/board/v3, in review).
//
// The prices that matter, grouped: power by grid (the day-ahead or the real-time daily mean at each grid's main hub,
// from price_board_latest), natural gas and oil (EIA's daily spot prices, eia_fuel_spot_prices). For each: its last
// value, its move on the day and on the week, and the last thirty values. Pure functions over the rows the page reads;
// nothing is filled: a move whose earlier day is not held is null, and the page says "not held".

export type Row = { entity: string; variable: string; ts_utc: string; value: number; unit: string };
export type Point = { t: string; v: number };

export type Line = {
  key: string;            // the entity
  label: string;          // "ERCOT", "Henry Hub natural gas"
  at: string;             // "Hub average", "" for a fuel
  unit: string;           // "USD/MWh"
  last: Point | null;     // the newest day held
  day: { from: Point; change: number; pct: number | null } | null;    // against the day held before it
  week: { from: Point; change: number; pct: number | null } | null;   // against the newest day held at least seven days before
  history: Point[];       // up to HISTORY days, oldest first
};

export const HISTORY = 30;
export const MARKETS = { da: "Day-ahead", rt: "Real-time" } as const;
export type MarketKey = keyof typeof MARKETS;
export const marketOf = (v: string | undefined): MarketKey => (v === "rt" ? "rt" : "da");

/** The grids of the board, in the site's order, each with its main hub and how the hub is named in words. */
export const GRIDS: { iso: string; entity: string; at: string }[] = [
  { iso: "ERCOT", entity: "ercot:HB_HUBAVG", at: "Hub average" },
  { iso: "CAISO", entity: "caiso:TH_SP15_GEN-APND", at: "SP15" },
  { iso: "NYISO", entity: "nyiso:N.Y.C.", at: "New York City zone" },
  { iso: "SPP", entity: "spp:SPPNORTH_HUB", at: "North hub" },
  { iso: "ISO-NE", entity: "isone:.H.INTERNAL_HUB", at: "Internal hub" },
];
/** Not shown, and why, in words. MISO: paused since 4 October 2026 (warehouse/metadata/paused_sources.csv,
 *  docs/methods/miso_pause.md); its terms forbid automated access and derivative works, so no figure of its prices is
 *  shown while the review is open (session 96's reading). PJM: its prices need a license the ERW does not hold. */
export const WITHHELD: { iso: string; status: string; words: string }[] = [
  { iso: "MISO", status: "Paused", words: " since 4 October 2026: MISO's terms forbid automated access to its site, so the ERW has stopped asking for its prices until a person has reviewed the terms. The prices already held stay in the warehouse and are not shown here." },
  { iso: "PJM", status: "Licensed", words: ": PJM's prices are published under a license and an account the ERW does not hold, so no PJM hub price is in the warehouse and none is shown." },
];
/** The whole sentence of a grid that carries no number: "Paused since ...", "Licensed: ...". */
export const withheldWords = (w: { status: string; words: string }) => `${w.status}${w.words}`;
export const FUELS: { entity: string; label: string; group: "gas" | "oil" }[] = [
  { entity: "eia:henry_hub", label: "Henry Hub natural gas", group: "gas" },
  { entity: "eia:wti_cushing", label: "WTI crude, Cushing", group: "oil" },
  { entity: "eia:brent", label: "Brent crude", group: "oil" },
];

const dayOf = (ts: string) => ts.slice(0, 10);
const daysBetween = (a: string, b: string) => Math.round((Date.parse(`${dayOf(b)}T00:00:00Z`) - Date.parse(`${dayOf(a)}T00:00:00Z`)) / 86_400_000);

/** One line of the board from the daily values of one entity (any order; one value a day). */
export function lineOf(key: string, label: string, at: string, rows: Row[]): Line {
  const pts = rows.filter((r) => Number.isFinite(r.value)).map((r) => ({ t: dayOf(r.ts_utc), v: r.value })).sort((a, b) => a.t.localeCompare(b.t));
  const unit = rows[0]?.unit ?? "";
  if (!pts.length) return { key, label, at, unit, last: null, day: null, week: null, history: [] };
  const last = pts[pts.length - 1];
  const move = (from: Point | undefined) => (from ? { from, change: last.v - from.v, pct: from.v !== 0 ? (100 * (last.v - from.v)) / Math.abs(from.v) : null } : null);
  // the day: the value held just before the last one, whatever the gap (a fuel has no weekend); the page names its date
  const prev = pts.length > 1 ? pts[pts.length - 2] : undefined;
  // the week: the newest value held at least seven days before the last one, and no more than ten (else it is not a week)
  const weekAgo = [...pts].reverse().find((p) => { const d = daysBetween(p.t, last.t); return d >= 7 && d <= 10; });
  return { key, label, at, unit, last, day: move(prev), week: move(weekAgo), history: pts.slice(-HISTORY) };
}

/** The board's lines of power for one market, from price_board_latest's rows. */
export function powerLines(rows: Row[], market: MarketKey): Line[] {
  const variable = `${market}_daily_mean`;
  return GRIDS.map((g) => lineOf(g.entity, g.iso, g.at, rows.filter((r) => r.entity === g.entity && r.variable === variable)));
}
/** The board's lines of gas and oil, from eia_fuel_spot_prices' rows. */
export function fuelLines(rows: Row[]): (Line & { group: "gas" | "oil" })[] {
  return FUELS.map((f) => ({ ...lineOf(f.entity, f.label, "", rows.filter((r) => r.entity === f.entity && r.variable === "spot_price")), group: f.group }));
}

export const money = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
export const signed = (v: number) => `${v > 0 ? "+" : v < 0 ? "-" : ""}${money(Math.abs(v))}`;
export const signedPct = (v: number) => `${v > 0 ? "+" : v < 0 ? "-" : ""}${Math.abs(v).toFixed(1)}`;
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
export const dayWords = (d: string) => `${Number(d.slice(8, 10))} ${MONTHS[Number(d.slice(5, 7)) - 1]} ${d.slice(0, 4)}`;

/** The day the grids are compared on: the newest day that every grid with a price holds (New York's day-ahead prices
 *  run a day ahead of the others'; a sentence about that day alone would speak for one grid). When no day is held by
 *  all of them, the newest day held by the most. Null when no grid holds a price. */
export function commonDay(power: Line[]): string | null {
  const held = power.filter((l) => l.last);
  if (!held.length) return null;
  const n = new Map<string, number>();
  for (const l of held) for (const p of l.history) n.set(p.t, (n.get(p.t) ?? 0) + 1);
  const most = Math.max(...n.values());
  return [...n.entries()].filter(([, k]) => k === most).map(([t]) => t).sort().at(-1) ?? null;
}
/** Each grid's value on one day: the grids that hold that day, lowest first. */
export function onDay(power: Line[], day: string): { line: Line; v: number }[] {
  return power.flatMap((l) => { const p = l.history.find((x) => x.t === day); return p ? [{ line: l, v: p.v }] : []; }).sort((a, b) => a.v - b.v);
}

/** The one summary sentence, on the common day. Null when no power line holds a price. */
export function summary(power: Line[], fuels: (Line & { group: string })[], market: MarketKey): string | null {
  const newest = commonDay(power);
  if (!newest) return null;
  const same = onDay(power, newest);
  const low = { label: same[0].line.label, last: { v: same[0].v } }, high = { label: same[same.length - 1].line.label, last: { v: same[same.length - 1].v } };
  const power1 = same.length === 1
    ? `${MARKETS[market]} power for ${dayWords(newest)} averaged USD ${money(low.last!.v)} per MWh in ${low.label}`
    : `${MARKETS[market]} power for ${dayWords(newest)} averaged from USD ${money(low.last!.v)} per MWh in ${low.label} to USD ${money(high.last!.v)} in ${high.label}, across the ${same.length} grids with that day held`;
  const gas = fuels.find((f) => f.group === "gas" && f.last);
  const oil = fuels.find((f) => f.key === "eia:wti_cushing" && f.last);
  const tail = [gas ? `Henry Hub gas was USD ${money(gas.last!.v)} per MMBtu on ${dayWords(gas.last!.t)}` : null,
    oil ? `WTI crude USD ${money(oil.last!.v)} a barrel${gas && gas.last!.t === oil.last!.t ? "" : ` on ${dayWords(oil.last!.t)}`}` : null].filter(Boolean);
  return `${power1}${tail.length ? `; ${tail.join(" and ")}` : ""}.`;
}
