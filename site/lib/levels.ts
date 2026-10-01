// Session 38: the home battery game's levels. Today's level is the latest complete ERCOT operating day of HB_HUBAVG
// real-time prices in the live set (iso_rtm_hub_prices, read with the anon key); the five famous days are frozen in
// data/battery_levels.json by warehouse/derived/battery_levels.py from ercot_all_hub_prices_history (the history is not
// in the live set). Every price is a warehouse row; nothing is filled.
import famous from "@/data/battery_levels.json";
import { rest } from "@/lib/supabase";

export type Level = {
  slug: string; date: string; title: string; why: string; table: string;
  grid?: "ERCOT" | "CAISO"; tz?: string; rule?: string;  // session 56: the California days (data/battery_levels.json)
  ts_utc: string[]; price: number[]; source: string[]; source_url: string[]; retrieved_at: string;
};

export const TZ = "America/Chicago";
const DAY = new Intl.DateTimeFormat("en-CA", { timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit" });
export const localDay = (ts: string) => DAY.format(new Date(ts));

/** The 15-minute intervals of an ERCOT operating day: 96, or 92 and 100 on the clock changes. */
export function intervalsIn(day: string): number {
  const start = localMidnight(day), end = localMidnight(nextDay(day));
  return Math.round((end - start) / 900_000);
}
function nextDay(day: string): string {
  const d = new Date(`${day}T12:00:00Z`);
  d.setUTCDate(d.getUTCDate() + 1);
  return d.toISOString().slice(0, 10);
}
/** The UTC instant of an operating day's midnight (Central time is UTC-5 or UTC-6). */
function localMidnight(day: string): number {
  for (const h of [5, 6]) {
    const t = Date.parse(`${day}T0${h}:00:00Z`);
    const t1 = new Date(t - 60_000).toISOString();
    if (localDay(new Date(t).toISOString()) === day && localDay(t1) !== day) return t;
  }
  throw new Error(`no local midnight for ${day}`);
}

export const FAMOUS: Level[] = (famous.levels as Level[]).map((l) => l);

type Row = { ts_utc: string; value: number; retrieved_at?: string; source?: string; source_url?: string };

/** The complete operating days of HB_HUBAVG real-time prices in the live set since `since`, newest first. */
async function recentDays(since: string, revalidate: number): Promise<Map<string, Row[]>> {
  const rows = await rest<Row>("series", {
    select: "ts_utc,value,retrieved_at,source,source_url",
    table_name: "eq.iso_rtm_hub_prices", entity: "eq.ercot:HB_HUBAVG", variable: "eq.spp_rtm", market: "eq.ercot_rtm",
    ts_utc: `gte.${since}`, order: "ts_utc",
  }, revalidate);
  const by = new Map<string, Row[]>();
  for (const r of rows) {
    const d = localDay(r.ts_utc);
    by.set(d, [...(by.get(d) ?? []), r]);
  }
  const full = new Map<string, Row[]>();
  for (const d of [...by.keys()].sort().reverse()) if (by.get(d)!.length === intervalsIn(d)) full.set(d, by.get(d)!);
  return full;
}

function toLevel(day: string, rows: Row[]): Level {
  return {
    slug: "today", date: day, title: "Today's level", why: `The latest complete ERCOT operating day the warehouse holds, ${day}.`,
    table: "iso_rtm_hub_prices", ts_utc: rows.map((r) => r.ts_utc), price: rows.map((r) => Number(r.value)),
    source: [...new Set(rows.map((r) => r.source ?? ""))].filter(Boolean), source_url: [...new Set(rows.map((r) => r.source_url ?? ""))].filter(Boolean),
    retrieved_at: rows.map((r) => r.retrieved_at ?? "").sort().pop() ?? "",
  };
}

/** Today's level: the latest complete operating day in the last four days of the live set. */
export async function todayLevel(revalidate = 3600): Promise<Level | null> {
  const since = new Date(Date.now() - 4 * 86_400_000).toISOString().slice(0, 13) + ":00:00Z";
  const days = await recentDays(since, revalidate);
  const [day] = days.keys();
  return day ? toLevel(day, days.get(day)!) : null;
}

/** The level of a posted play: a famous day, or a complete day of the live set's last ten days (a level that rolled
 * over while it was played still counts). */
export async function levelFor(date: string): Promise<Level | null> {
  const f = FAMOUS.find((l) => l.date === date);
  if (f) return f;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return null;
  const since = new Date(Date.parse(`${date}T00:00:00Z`) - 86_400_000).toISOString().slice(0, 13) + ":00:00Z";
  if (Date.now() - Date.parse(since) > 11 * 86_400_000) return null;
  const days = await recentDays(since, 300);
  const rows = days.get(date);
  return rows ? toLevel(date, rows) : null;
}
