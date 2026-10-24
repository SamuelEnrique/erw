// Energy Research Warehouse (ERW) site, session 1154 (chain 077): the Grid tool's scarcity hours, `grid_scarcity_<grid>`
// on the Mix tab. Pure functions over rows the caller reads (components/grid/ScarcityPanel.tsx), tested on a committed
// fixture of real rows (scripts/test-scarcity-strip.mjs, scripts/fixtures/scarcity_strip.json). No import: node runs
// this file with its types stripped, and scripts/check-values.mjs imports heldHours from it.
//
// The table is scarcity_hours_by_grid (docs/methods/scarcity_hours_by_grid.md, session 254): one row per grid, hour
// and variable, for ERCOT and CAISO only. An hour without a row is not held; it is not a zero. The level is USD 1,000
// per MWh (the method's LEVEL; lib/datacenter/answers.ts SBG_LEVEL, the same value, held equal by the test).
//
// The window (session 1150's decision): the latest 30 days the table holds, not the 30 days before today. The days are
// the grid's own standard-time days, as the method counts its hours: the last day is the standard-time day of the
// newest hour held, the first 29 days before it. The strip draws them across, the hour of day (standard time) down.
//
// The price on hover: the hour's highest 15-minute real-time price at the grid's hub from iso_rtm_hub_prices, where
// the live set holds it (about the last 35 days); for ERCOT, where it does not, the highest real-time price of ERCOT's
// local day from ercot_hub_prices_daily, said as the day's; else none, said so. Both reads are light (about 1,200
// rows a grid for the 15-minute prices, 30 for the days).

export const SCARCITY_TABLE = "scarcity_hours_by_grid";
export const SCARCITY_LEVEL = 1000;
export const SCARCITY_METHOD = "docs/methods/scarcity_hours_by_grid.md";
export const SCARCITY_DAYS = 30;
export const SCARCITY_VARIABLES = ["rt_intervals_ge_1000", "rt_hour_ge_1000", "da_hour_ge_1000", "own_signal"] as const;
export const RT_PRICE_TABLE = "iso_rtm_hub_prices";
export const DAILY_PRICE_TABLE = "ercot_hub_prices_daily";

export type ScarcityGrid = {
  slug: "ercot" | "caiso"; label: string; entity: string; hub: string;
  /** hours the grid's standard time is behind UTC */
  behind: number; zone: string; zoneName: string;
  /** the hub's 15-minute real-time price in iso_rtm_hub_prices */
  price: { entity: string; variable: string };
  /** ERCOT only: the local day's highest real-time price in ercot_hub_prices_daily */
  daily: { entity: string; variable: string; tz: string } | null;
  /** the grid's own signal, in words, and its hour not in force */
  own: string; ownOff: string;
  /** when no own_signal row is held in the window, why */
  ownMissing: string;
};

export const SCARCITY_GRIDS: Record<"ercot" | "caiso", ScarcityGrid> = {
  ercot: {
    slug: "ercot", label: "ERCOT", entity: "iso:ercot", hub: "HB_HUBAVG", behind: 6, zone: "CST", zoneName: "Central standard time",
    price: { entity: "ercot:HB_HUBAVG", variable: "spp_rtm" },
    daily: { entity: "ercot:HB_HUBAVG", variable: "rt_max", tz: "America/Chicago" },
    own: "its reserve adder above zero", ownOff: "the reserve adder was zero",
    ownMissing: "ERCOT published its reserve adder to 4 December 2025, so its own signal is not held for these days",
  },
  caiso: {
    slug: "caiso", label: "CAISO", entity: "iso:caiso", hub: "TH_SP15_GEN-APND", behind: 8, zone: "PST", zoneName: "Pacific standard time",
    price: { entity: "caiso:TH_SP15_GEN-APND", variable: "lmp_rtm_15m_mean" },
    daily: null,
    own: "an Energy Emergency Alert or a Flex Alert in force", ownOff: "no Energy Emergency Alert or Flex Alert in force",
    ownMissing: "CAISO's own signal is not held for these days",
  },
};

export const isScarcityGrid = (g: string): g is "ercot" | "caiso" => g === "ercot" || g === "caiso";

const H = 3_600_000, D = 86_400_000;
const iso = (ms: number) => new Date(ms).toISOString().replace(/\.\d{3}Z$/, "Z");
const hhmm = (ms: number) => new Date(ms).toISOString().slice(11, 16);
const usd = (v: number) => `USD ${v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const level = `USD ${SCARCITY_LEVEL.toLocaleString("en-US")} per MWh`;

/** The number of distinct hours the rows hold (an hour written twice is held once): the count a `series_n` key names
 *  (scripts/check-values.mjs runs this function on the rows it reads). */
export function heldHours(rows: { ts_utc: string }[]): number {
  return new Set(rows.map((r) => Date.parse(r.ts_utc))).size;
}

export type Window = { start: string; end: string; startMs: number; endMs: number; days: string[] };

/** The 30 standard-time days that end with the day of the newest hour held, and their bounds in UTC. */
export function windowOf(newest: string, behind: number, days = SCARCITY_DAYS): Window {
  const last = Date.parse(new Date(Date.parse(newest) - behind * H).toISOString().slice(0, 10) + "T00:00:00Z");
  const first = last - (days - 1) * D;
  const startMs = first + behind * H, endMs = last + D + behind * H;
  return { start: iso(startMs), end: iso(endMs), startMs, endMs, days: Array.from({ length: days }, (_, i) => new Date(first + i * D).toISOString().slice(0, 10)) };
}

export type Fig = { check: string; raw: number; tip: string };
export type Strip = {
  grid: ScarcityGrid; window: Window; newest: string;
  /** the chart: rows are the hours of the day 0 to 23 (standard time), columns the days */
  rows: string[]; cols: string[];
  /** 1 where the real-time or the day-ahead hour was at or above the level, 0 held and below, null not held */
  cells: (number | null)[][];
  /** [hour, day] where the grid's own signal was in force */
  marks: [number, number][];
  tips: string[][];
  rt: { hours: Fig; held: Fig; intervals: Fig } | null;
  da: { hours: Fig; held: Fig } | null;
  own: { hours: Fig; held: Fig } | null;
  /** the highest 15-minute real-time price held in the window, and the first interval held */
  rtMax: (Fig & { from: string }) | null;
  /** ERCOT: the highest real-time price of the window's local days */
  dayMax: Fig | null;
  /** the hours the strip marks at or above the level, and the hours of the own signal */
  high: number; signal: number;
};

type Row = { variable: string; ts_utc: string; value: number };
type Price = { ts_utc: string; value: number };

/** The local day (YYYY-MM-DD) of an instant in a time zone. */
function localDay(ms: number, tz: string): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(ms));
}

/** The strip and its figures, from the table's rows in the window, the hub's 15-minute prices and (ERCOT) its days. */
export function scarcityStrip(g: ScarcityGrid, input: { rows: Row[]; prices: Price[]; daily: Price[]; newest: string;
  /** session 1181: a price read that failed (its reason): an hour's hover then says the prices could not be read, not that none is held */
  unread?: { prices?: string | null; daily?: string | null } }, days = SCARCITY_DAYS): Strip {
  const w = windowOf(input.newest, g.behind, days);
  const inW = (ms: number) => ms >= w.startMs && ms < w.endMs;
  // each variable's value by hour, an hour written twice read once (its highest), as lib/datacenter/answers.ts reads it
  const byVar = new Map<string, Map<number, number>>();
  for (const v of SCARCITY_VARIABLES) byVar.set(v, new Map());
  for (const r of input.rows) {
    const ms = Date.parse(r.ts_utc), m = byVar.get(r.variable);
    if (!m || !inW(ms)) continue;
    m.set(ms, Math.max(m.get(ms) ?? -Infinity, Number(r.value)));
  }
  // the hour's highest 15-minute price, and ERCOT's local days
  const hourMax = new Map<number, { v: number; n: number }>();
  let rtMax: { v: number; t: number } | null = null, first: number | null = null;
  for (const p of input.prices) {
    const ms = Date.parse(p.ts_utc);
    if (!inW(ms) || !Number.isFinite(Number(p.value))) continue;
    const v = Number(p.value), h = Math.floor(ms / H) * H, o = hourMax.get(h);
    hourMax.set(h, { v: o ? Math.max(o.v, v) : v, n: (o?.n ?? 0) + 1 });
    if (!rtMax || v > rtMax.v) rtMax = { v, t: ms };
    if (first === null || ms < first) first = ms;
  }
  const dayFirst = w.days[0], dayLast = w.days[w.days.length - 1];
  const dayPrice = new Map<string, number>();
  for (const p of input.daily) {
    const d = p.ts_utc.slice(0, 10);
    if (d >= dayFirst && d <= dayLast && Number.isFinite(Number(p.value))) dayPrice.set(d, Number(p.value));
  }

  const rows = Array.from({ length: 24 }, (_, h) => `${String(h).padStart(2, "0")}:00`);
  const cols = w.days.map((d) => d.slice(5));
  const cells: (number | null)[][] = rows.map(() => w.days.map(() => null));
  const tips: string[][] = rows.map(() => w.days.map(() => ""));
  const marks: [number, number][] = [];
  const at = (v: string, ms: number) => byVar.get(v)!.get(ms);
  const tail = `Level: ${level}, ${SCARCITY_METHOD}; prices: ${g.label}.`;
  let high = 0, signal = 0;
  w.days.forEach((d, j) => {
    for (let h = 0; h < 24; h++) {
      const ms = Date.parse(`${d}T00:00:00Z`) + (h + g.behind) * H;
      const head = `${d} ${rows[h]} ${g.zone} (${new Date(ms).toISOString().slice(0, 10)} ${hhmm(ms)} UTC).`;
      const rtH = at("rt_hour_ge_1000", ms), daH = at("da_hour_ge_1000", ms), own = at("own_signal", ms), n = at("rt_intervals_ge_1000", ms);
      if (rtH === undefined && daH === undefined && own === undefined) {
        tips[h][j] = `${head} Not held in ${SCARCITY_TABLE}: an hour without a row is not counted, as a zero or otherwise. ${tail}`;
        continue;
      }
      // the cell is the price count's; an hour whose own signal alone is held (CAISO before its prices, from 1 September
      // 2024) keeps a blank cell, and its mark
      const on = rtH === 1 || daH === 1;
      if (rtH !== undefined || daH !== undefined) cells[h][j] = on ? 1 : 0;
      if (on) high += 1;
      if (own === 1) { marks.push([h, j]); signal += 1; }
      const ones = (["rt_hour_ge_1000", "da_hour_ge_1000", "own_signal"] as const).filter((v) => at(v, ms) === 1);
      const pm = hourMax.get(ms);
      const dp = g.daily ? dayPrice.get(localDay(ms, g.daily.tz)) : undefined;
      const lost = input.unread?.prices, lostDay = input.unread?.daily;
      const price = pm ? `Highest 15-minute real-time price at ${g.hub}: ${usd(pm.v)} per MWh (${pm.n} of 4 intervals held, ${RT_PRICE_TABLE}).`
        : dp !== undefined && g.daily ? `${lost ? `The hour's 15-minute prices could not be read just now (${RT_PRICE_TABLE})` : "The hour's 15-minute prices are not in the live set"}; the highest real-time price of ERCOT's local day ${localDay(ms, g.daily.tz)} at ${g.hub}: ${usd(dp)} per MWh (${DAILY_PRICE_TABLE}).`
        : lost ? `The hour's prices could not be read just now (${[RT_PRICE_TABLE, ...(lostDay ? [DAILY_PRICE_TABLE] : [])].join(", ")}).`
        : lostDay && g.daily ? `The hour's 15-minute prices are not in the live set; the highest real-time price of ERCOT's local day could not be read just now (${DAILY_PRICE_TABLE}).`
        : `No price of this hour is in the live set (it keeps about 35 days of 15-minute prices).`;
      tips[h][j] = [
        head,
        `Variables at 1: ${ones.length ? ones.join(", ") : "none"}.`,
        `Real-time intervals at or above ${level}: ${n === undefined ? "not held" : `${n} of 4`}.`,
        own === undefined ? `own_signal: not held (${g.ownMissing}).` : `own_signal ${own}: ${own === 1 ? g.own : g.ownOff}.`,
        price,
        tail,
      ].join(" ");
    }
  });

  const span = `${w.start.slice(0, 16).replace("T", " ")} to ${w.end.slice(0, 16).replace("T", " ")} UTC`;
  const sum = (v: string) => [...byVar.get(v)!.values()].reduce((a, x) => a + x, 0);
  const held = (v: string) => byVar.get(v)!.size;
  const key = (kind: string, v: string) => `${kind}|${SCARCITY_TABLE}|${v}|${w.start}|${w.end}|${g.entity}`;
  const sumFig = (v: string, what: string): Fig => ({ check: key("series_sum", v), raw: sum(v), tip: `${SCARCITY_TABLE}, ${g.entity}, ${v} summed over ${span}: ${what}. ${tail}` });
  const heldFig = (v: string): Fig => ({ check: key("series_n", v), raw: held(v), tip: `${SCARCITY_TABLE}, ${g.entity}: the hours of ${span} with a ${v} row (an hour without a row is not held).` });
  const rt = held("rt_hour_ge_1000") ? {
    hours: sumFig("rt_hour_ge_1000", `the hours whose real-time mean at ${g.hub} was at or above ${level}`),
    held: heldFig("rt_hour_ge_1000"),
    intervals: sumFig("rt_intervals_ge_1000", `the 15-minute real-time intervals at ${g.hub} at or above ${level}`),
  } : null;
  const da = held("da_hour_ge_1000") ? { hours: sumFig("da_hour_ge_1000", `the hours whose day-ahead price at ${g.hub} was at or above ${level}`), held: heldFig("da_hour_ge_1000") } : null;
  const own = held("own_signal") ? { hours: sumFig("own_signal", `the hours with ${g.own}`), held: heldFig("own_signal") } : null;
  const rtMaxFig = rtMax && first !== null ? {
    check: `series_max|${RT_PRICE_TABLE}|${g.price.variable}|${w.start}|${w.end}|${g.price.entity}`, raw: rtMax.v, from: iso(first),
    tip: `${RT_PRICE_TABLE}, ${g.price.entity}, ${g.price.variable}: the highest 15-minute price of ${span} the live set holds, at ${new Date(rtMax.t).toISOString().slice(0, 16).replace("T", " ")} UTC.`,
  } : null;
  const dayMax = g.daily && dayPrice.size ? {
    check: `series_max|${DAILY_PRICE_TABLE}|${g.daily.variable}|${dayFirst}T00:00:00Z|${iso(Date.parse(`${dayLast}T00:00:00Z`) + D)}|${g.daily.entity}`,
    raw: Math.max(...dayPrice.values()),
    tip: `${DAILY_PRICE_TABLE}, ${g.daily.entity}, ${g.daily.variable}: the highest real-time price of ERCOT's local days ${dayFirst} to ${dayLast} (${dayPrice.size} days held).`,
  } : null;
  return { grid: g, window: w, newest: iso(Date.parse(input.newest)), rows, cols, cells, marks, tips, rt, da, own, rtMax: rtMaxFig, dayMax, high, signal };
}
