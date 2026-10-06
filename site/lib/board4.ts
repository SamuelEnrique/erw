// Energy Research Warehouse (ERW) site, session 127: the price board, version 4 (/board/v4, in review).
//
// Every price the warehouse holds as a daily series, with its latest value, its move over a day, a week, a month and a
// year, and its place in its own one-year range; the spreads an analyst reads, each with its formula; and, greyed, what
// the master plan names and no free source gives. Pure functions over the site's own copy of price_board_stats
// (data/board_v4.json, written by warehouse/derived/price_board_v4.py --snapshot). Nothing is computed here that the
// table does not hold; a figure that is not held is null, and the page says "not held".

export type Move = { t: string; v: number; change: number; pct: number | null };
export type Line = {
  group: string; key: string; label: string; at: string; unit: string; formula: string | null;
  last: { t: string; v: number } | null;
  moves: Record<"1d" | "1w" | "1m" | "1y", Move | null> | null;
  range: { low: number; high: number; days: number; position: number | null } | null;
};
export type BoardFile = { built: string; table: string; heat_rate: number; slack_days: number; range_min_days: number; gas_back_days: number; lines: Line[] };

export const TABLE = "price_board_stats";
export const MOVES = [["1d", "Day"], ["1w", "Week"], ["1m", "Month"], ["1y", "Year"]] as const;

/** The board's sections, in order. `formula` sections are spreads: the page prints each line's formula under the table. */
export const GROUPS: { id: string; title: string; note: string; spread?: boolean }[] = [
  { id: "power_da", title: "Power, day-ahead", note: "The mean of a complete local operating day at each grid's main hub, day-ahead market." },
  { id: "power_rt", title: "Power, real time", note: "The mean of a complete local operating day at the same hubs, real-time market. Real time is published a day or two behind day-ahead." },
  { id: "gas", title: "Natural gas", note: "EIA's daily spot price." },
  { id: "crude", title: "Crude oil", note: "EIA's daily spot prices. EIA publishes two crude grades by the day, and no others." },
  { id: "products", title: "Refined products", note: "EIA's daily spot prices, at each place EIA publishes." },
  { id: "spark", title: "Spark spread, indicative", note: "What a megawatt-hour sells for day-ahead, less the gas a plant would burn to make it.", spread: true },
  { id: "da_rt", title: "Day-ahead less real time", note: "The day-ahead price less the real-time price of the same day and hub.", spread: true },
  { id: "crack", title: "3-2-1 crack spread", note: "What three barrels of crude earn as two of gasoline and one of diesel, per barrel, before any cost.", spread: true },
];

/** Named by the master plan and not on the board, each with the reason and the source that would supply it. */
export const NOT_HELD: { name: string; why: string; source: string }[] = [
  { name: "Regional natural gas hubs (Waha, SoCal Citygate, Algonquin, Transco Zone 6, Chicago and others)", why: "not held: licensed source needed", source: "S&P Global Commodity Insights (Platts) or Natural Gas Intelligence, daily indices" },
  { name: "TTF, the Dutch gas benchmark", why: "not held: licensed source needed", source: "ICE Endex or LSEG. A monthly average of European gas from the IMF is in fred_imf_commodity_prices; it is not a daily price" },
  { name: "JKM, the Japan-Korea LNG marker", why: "not held: licensed source needed", source: "S&P Global Commodity Insights (Platts). A monthly average of Japan's LNG import price from the IMF is in fred_imf_commodity_prices" },
  { name: "Uranium", why: "not held: licensed source needed", source: "UxC or TradeTech, weekly spot. A monthly average from the IMF is in fred_imf_commodity_prices" },
  { name: "Carbon allowances by the day (California, RGGI, the European Union)", why: "not held: licensed source needed", source: "ICE. The quarterly auction results of California and RGGI are held and not shown: their license is under review" },
  { name: "Lithium", why: "not held: licensed source needed", source: "Fastmarkets or Benchmark Mineral Intelligence" },
  { name: "NYMEX futures (crude oil, gasoline, heating oil, natural gas)", why: "not held after 5 April 2024: licensed source needed", source: "CME Group. EIA published contracts 1 to 4 until that day and then stopped; the history from 2019 is held and not shown" },
];

export const groupLines = (f: BoardFile, id: string) => f.lines.filter((l) => l.group === id);
const places = (unit: string) => (unit === "USD/gal" ? 3 : 2);
/** A value in its unit's precision: gallons to a tenth of a cent, everything else to the cent. */
export const value = (v: number, unit: string) => v.toLocaleString("en-US", { minimumFractionDigits: places(unit), maximumFractionDigits: places(unit) });
/** A move with its sign: "+0.28" or "-6.12". */
export const signed = (v: number, unit: string) => `${v > 0 ? "+" : ""}${value(v, unit)}`;
export const pct = (v: number) => `${v > 0 ? "+" : ""}${v.toFixed(1)}%`;
/** "29 September 2026" from a day. */
export const day = (t: string) => new Date(`${t}T00:00:00Z`).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
export const shortDay = (t: string) => new Date(`${t}T00:00:00Z`).toLocaleDateString("en-GB", { day: "numeric", month: "short", timeZone: "UTC" });
/** Where a value sits in its range, in words: the bottom tenth, the top tenth, or the share. */
export function placeWords(p: number): string {
  if (p <= 0.1) return "near its low";
  if (p >= 0.9) return "near its high";
  return `${Math.round(p * 100)}% of the way up`;
}
/** The lines that hold a latest value, and the newest and oldest of their days. */
export function held(f: BoardFile) {
  const ls = f.lines.filter((l) => l.last);
  const days = ls.map((l) => l.last!.t).sort();
  return { lines: ls, newest: days[days.length - 1], oldest: days[0], prices: ls.filter((l) => !l.formula).length, spreads: ls.filter((l) => l.formula).length };
}
/** The prices (not spreads) nearest the top and the bottom of their one-year range. */
export function extremes(f: BoardFile) {
  const ls = f.lines.filter((l) => !l.formula && l.range && l.range.position !== null).sort((a, b) => b.range!.position! - a.range!.position!);
  return ls.length ? { top: ls[0], bottom: ls[ls.length - 1] } : null;
}
