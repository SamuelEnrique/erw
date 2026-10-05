// Energy Research Warehouse (ERW) site, session 93: the network, version 3. The parts with no drawing in them, so a test
// can run them in Node: the address that holds a view (the grid, the moment and the switches), the replay's day frames,
// the weight of the price ring, and "trace the power" (a grid's suppliers and their suppliers, two steps).
// No imports beyond types: Node runs this file as it is.
import type { NetLink } from "../app/network/Network";

// ------------------------------------------------------------------ the replay: a day per frame

/** A year of the replay (public/network/daily_<year>.json, warehouse/derived/network_daily.py). */
export type Daily = { year: number; frame: "day"; tz: string; days: string[]; built: string; rule: string; links: NetLink[];
  /** session 124: for each day, how many pairs hold a flow; and the year's usual count (its median) */
  pairs_held?: number[]; pairs_usual?: number;
  intensity: Record<string, (number | null)[]>; hub_prices: Record<string, (number | null)[]>;
  /** session 109: each balancing authority's demand, the day's average MW (EIA's daily demand over the day's hours); null where not held or screened out */
  demand?: Record<string, (number | null)[]>;
  missing: { pair_days: number; pair_days_from_other_side: number; pair_days_screened: number; demand_days_held?: number } };
export type DailyIndex = { first: string; last: string; tz: string;
  /** session 124: the newest day that holds at least nine tenths of its year's usual pairs; what rule C left out and what was kept */
  last_complete?: string; pair_days_rule?: number; pair_days_confirmed_both_sides?: number; pair_days_confirmed_by_hours?: number; years: Record<string, { file: string; days: number; first: string; last: string; priced: string[]; pair_days_screened: number; pair_days: number }>;
  left_out_bas: string[]; built: string };

/** A day as a frame's time: noon UTC of the date, so that it reads as the same date in every US time zone. */
export const dayFrame = (day: string) => `${day}T12:00:00Z`;
export const isDay = (v: string) => /^\d{4}-\d{2}-\d{2}$/.test(v);
/** The day a date picker's value names, held to the replay's first and last day; null when it is not a date. */
export function clampDay(day: string, index: { first: string; last: string }): string | null {
  if (!isDay(day) || Number.isNaN(Date.parse(`${day}T00:00:00Z`))) return null;
  return day < index.first ? index.first : day > index.last ? index.last : day;
}
/** The hours of an Eastern day: 24, or 23 or 25 on the days the clocks change (a flow in MW times these is its MWh). */
export function easternHours(day: string): number {
  const at = (d: string) => {
    // the UTC instant of local midnight in New York: try the two offsets it can have
    for (const off of [4, 5]) {
      const t = Date.parse(`${d}T00:00:00Z`) + off * 3_600_000;
      const h = new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", hour: "2-digit", hourCycle: "h23" }).format(new Date(t));
      if (h === "00") return t;
    }
    return Date.parse(`${d}T05:00:00Z`);
  };
  const next = new Date(Date.parse(`${day}T00:00:00Z`) + 86_400_000).toISOString().slice(0, 10);
  return Math.round((at(next) - at(day)) / 3_600_000);
}

/** Session 124: the frames [from, to) of the month that holds frame i, when the frames are days ("2021-02-15T12:00:00Z"). */
export function monthSpan(frames: string[], i: number): [number, number] {
  const m = (frames[i] ?? "").slice(0, 7);
  let a = i, b = i + 1;
  while (a > 0 && frames[a - 1].slice(0, 7) === m) a -= 1;
  while (b < frames.length && frames[b].slice(0, 7) === m) b += 1;
  return [a, b];
}

// ------------------------------------------------------------------ the newest complete hour (session 124)

export type Complete = {
  /** the frame, and its time: the newest hour in which every reporting pair holds a flow; -1 and null when there is none */
  index: number; hour: string | null;
  /** the pairs of the week, and those that are reporting */
  pairs: number; reporting: number;
  /** the pairs that hold no flow in the last `quiet` hours of the week, each with the last hour it did hold */
  silent: { a: string; b: string; last: string | null }[];
  /** the week's newest hour, and how many of the reporting pairs hold it */
  newest: string; newestPairs: number;
};

/** The newest hour that is complete for every pair. A pair that has held nothing in the last `quiet` hours of the week
 * has stopped reporting: it is named, with its last hour, and is not waited for (one such pair would hold the page a week
 * behind). Among the others, the newest hour in which every one of them holds a flow. */
export function completeHour(hours: string[], links: { a: string; b: string; mw: (number | null)[] }[], quiet = 48): Complete {
  const n = hours.length;
  const lastOf = (l: { mw: (number | null)[] }) => { for (let h = n - 1; h >= 0; h -= 1) if (l.mw[h] !== null && l.mw[h] !== undefined) return h; return -1; };
  const last = links.map(lastOf);
  const silent = links.map((l, i) => ({ l, last: last[i] })).filter((x) => x.last < n - quiet)
    .map((x) => ({ a: x.l.a, b: x.l.b, last: x.last >= 0 ? hours[x.last] : null })).sort((x, y) => `${x.a}-${x.b}`.localeCompare(`${y.a}-${y.b}`));
  const reporting = links.filter((_, i) => last[i] >= n - quiet);
  const holds = (h: number) => reporting.filter((l) => l.mw[h] !== null && l.mw[h] !== undefined).length;
  let index = -1;
  if (reporting.length) for (let h = n - 1; h >= 0; h -= 1) if (holds(h) === reporting.length) { index = h; break; }
  return { index, hour: index >= 0 ? hours[index] : null, pairs: links.length, reporting: reporting.length, silent, newest: hours[n - 1] ?? "", newestPairs: n ? holds(n - 1) : 0 };
}

/** Session 124: a hub price a new page does not show, and the words it shows in its place. */
export const PAUSED_PRICE: Record<string, string> = {
  MISO: "Not shown: MISO's own files are paused since 4 October 2026 while a person reviews its terms. Its flows, demand and carbon here are EIA's, which are not paused.",
};

/** Session 124: a node that is not one network, so nothing is traced through it. CEN is Mexico's operator: its tie to
 * California (Baja California) and its ties to Texas belong to systems that do not connect inside Mexico. */
export const ISLANDS: Record<string, string> = {
  CEN: "Mexico's ties to Texas and to California are separate systems, so nothing is traced through it",
};

// ------------------------------------------------------------------ the address

export const VIEWS = ["live", "evening", "uri_2021", "east_heat_2025", "day"] as const;
export type ViewKey = (typeof VIEWS)[number];
/** What an address holds: the view, the moment (an hour's time, or a day for the replay), the grid and the switches. */
export type Shared = { view: ViewKey; t: string | null; grid: string | null; batteries: boolean; prices: boolean; trace: boolean };
export const DEFAULT: Shared = { view: "live", t: null, grid: null, batteries: false, prices: false, trace: false };

/** The view an address names. Anything it does not understand is left at its default, never an error. */
export function parseShared(search: string): Shared {
  const p = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
  const view = (VIEWS as readonly string[]).includes(p.get("view") ?? "") ? (p.get("view") as ViewKey) : "live";
  const t = p.get("t");
  const okT = t !== null && (view === "day" ? isDay(t) : /^\d{4}-\d{2}-\d{2}T\d{2}:00:00Z$/.test(t));
  const grid = p.get("grid");
  const on = (k: string) => p.get(k) === "1";
  return { view: view === "day" && !okT ? "live" : view, t: okT ? t : null, grid: grid && /^[A-Z0-9]{2,6}$/.test(grid) ? grid : null,
    batteries: on("batteries"), prices: on("prices"), trace: on("trace") };
}

/** The query that holds a view: only what differs from the page as it opens, in a fixed order. "" for the default. */
export function sharedQuery(s: Shared): string {
  const p: [string, string][] = [];
  if (s.view !== "live") p.push(["view", s.view]);
  if (s.t) p.push(["t", s.t]);
  if (s.grid) p.push(["grid", s.grid]);
  if (s.batteries) p.push(["batteries", "1"]);
  if (s.prices) p.push(["prices", "1"]);
  if (s.trace) p.push(["trace", "1"]);
  return p.length ? `?${p.map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join("&")}` : "";
}

// ------------------------------------------------------------------ the price ring

/** The ring's weight for a price, 0 to 1: the square root of its share of the highest price in the period shown, so a
 * scarcity hour does not make every other ring a hair. A price at or below zero is the thinnest ring (0). */
export function priceWeight(price: number | null, max: number): number | null {
  if (price === null) return null;
  if (!(max > 0) || price <= 0) return 0;
  return Math.sqrt(Math.min(1, price / max));
}

// ------------------------------------------------------------------ trace the power

export type TraceStep = { id: string; mwh: number; share: number };
export type TraceRow = TraceStep & { via: TraceStep[]; frames: number; /** session 124: not one network; nothing is traced through it */ island?: string };
export type Trace = { id: string; inMwh: number; outMwh: number; frames: number; rows: TraceRow[];
  /** session 124: the frames of the period in which at least one of the grid's ties holds a flow */
  held: number };

/** Each neighbour's net flow into `id` over the frames [from, to), MWh: positive, the neighbour supplied it. A frame a
 * tie did not report adds nothing; `frames` counts, per neighbour, the frames it did report. */
export function netInto(links: NetLink[], from: number, to: number, id: string, hoursOf: (h: number) => number): Map<string, { mwh: number; frames: number }> {
  const out = new Map<string, { mwh: number; frames: number }>();
  for (const l of links) {
    if (l.a !== id && l.b !== id) continue;
    const other = l.a === id ? l.b : l.a, sign = l.b === id ? 1 : -1;  // mw is positive when a exports to b
    const acc = out.get(other) ?? { mwh: 0, frames: 0 };
    for (let h = from; h < to; h += 1) {
      const v = l.mw[h];
      if (v === null || v === undefined) continue;
      acc.mwh += sign * v * hoursOf(h);
      acc.frames += 1;
    }
    out.set(other, acc);
  }
  return out;
}

/** Trace the power, two steps: the neighbours that supplied `id` over the period, largest first, each with its share of
 * what all of them supplied; and for each, the neighbours that supplied it over the same period (never `id` itself), with
 * their share of what its suppliers supplied. Physical flows over ties, as reported; not contracts, and not where the
 * power was generated. A neighbour that took power on net is not a supplier and is summed in outMwh. */
export function trace(links: NetLink[], from: number, to: number, id: string, hoursOf: (h: number) => number = () => 1, top = 4): Trace {
  const first = [...netInto(links, from, to, id, hoursOf)];
  const suppliers = first.filter(([, v]) => v.mwh > 0).sort((a, b) => b[1].mwh - a[1].mwh || a[0].localeCompare(b[0]));
  const inMwh = suppliers.reduce((a, [, v]) => a + v.mwh, 0);
  const outMwh = first.filter(([, v]) => v.mwh < 0).reduce((a, [, v]) => a - v.mwh, 0);
  const rows = suppliers.map(([n, v]) => {
    const base = { id: n, mwh: v.mwh, share: inMwh > 0 ? (100 * v.mwh) / inMwh : 0, frames: v.frames };
    if (ISLANDS[n]) return { ...base, via: [], island: ISLANDS[n] };
    const second = [...netInto(links, from, to, n, hoursOf)].filter(([m, x]) => m !== id && x.mwh > 0).sort((a, b) => b[1].mwh - a[1].mwh || a[0].localeCompare(b[0]));
    const total = second.reduce((a, [, x]) => a + x.mwh, 0);
    return { ...base, via: second.slice(0, top).map(([m, x]) => ({ id: m, mwh: x.mwh, share: total > 0 ? (100 * x.mwh) / total : 0 })) };
  });
  const mine = links.filter((l) => l.a === id || l.b === id);
  let held = 0;
  for (let h = from; h < to; h += 1) if (mine.some((l) => l.mw[h] !== null && l.mw[h] !== undefined)) held += 1;
  return { id, inMwh, outMwh, frames: Math.max(0, to - from), rows, held };
}
