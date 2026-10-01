// Session 58: California reliability v1, the data of /grid/caiso's Reliability section and /events/caiso-heat-2022.
// caiso_grid_emergencies (events: every CAISO notice since 1998, from its Grid Emergencies History Report) and
// caiso_reliability_daily (derived series: peak demand, the evening ramp, batteries at the evening peak, the day's notices),
// both in the Supabase live set. docs/methods/california_reliability.md.
import type { SeriesRow } from "@/lib/data";
import { HOURLY, rest } from "@/lib/supabase";

export const EMERGENCIES = "caiso_grid_emergencies";
export const DAILY = "caiso_reliability_daily";
export const GEHR = "https://www.caiso.com/documents/grid-emergencies-history-report-1998-to-present.pdf";

export type Notice = { event_id: string; event_date: string; event_type: string; extra: Record<string, string> };

/** CAISO's notices, oldest first; between two local days when given. */
export async function gridNotices(from?: string, to?: string): Promise<Notice[]> {
  const q: Record<string, string> = { select: "event_id,event_date,event_type,extra", table_name: `eq.${EMERGENCIES}`, order: "event_date,event_id" };
  if (from && to) q.and = `(event_date.gte.${from},event_date.lte.${to}T23:59:59Z)`;
  return rest<Notice>("events", q, HOURLY, 20_000);
}

/** The notice types, in the order of severity the page lists them, with their names. */
export const TYPES: { id: string; name: string; group: "conserve" | "maintenance" | "emergency" | "transmission" }[] = [
  { id: "flex_alert", name: "Flex Alert (before 2007, Power Watch)", group: "conserve" },
  { id: "rmo", name: "Restricted Maintenance Operations (before 2002, No Touch)", group: "maintenance" },
  { id: "alert", name: "Alert", group: "emergency" }, { id: "warning", name: "Warning", group: "emergency" },
  { id: "stage1", name: "Stage 1 emergency", group: "emergency" }, { id: "stage2", name: "Stage 2 emergency", group: "emergency" },
  { id: "stage3", name: "Stage 3 emergency", group: "emergency" },
  { id: "eea_watch", name: "EEA Watch", group: "emergency" }, { id: "eea1", name: "Energy Emergency Alert 1", group: "emergency" },
  { id: "eea2", name: "Energy Emergency Alert 2", group: "emergency" }, { id: "eea3", name: "Energy Emergency Alert 3", group: "emergency" },
  { id: "transmission_emergency", name: "Transmission emergency", group: "transmission" },
  { id: "vlrp", name: "Voluntary Load Reduction Program", group: "emergency" }, { id: "load_interruption", name: "1-hour probable load interruptions", group: "emergency" },
];
export const typeName = (t: string) => TYPES.find((x) => x.id === t)?.name ?? t;

/** Days with a notice of a type, per year: the distinct local days (CAISO's own counts are days). */
export function daysByYear(ns: Notice[]): Map<number, Map<string, number>> {
  const sets = new Map<string, Set<string>>();
  for (const n of ns) {
    const k = `${n.event_date.slice(0, 4)}|${n.event_type}`;
    (sets.get(k) ?? sets.set(k, new Set()).get(k)!).add(n.event_date.slice(0, 10));
  }
  const out = new Map<number, Map<string, number>>();
  for (const [k, s] of sets) {
    const [y, t] = k.split("|");
    (out.get(+y) ?? out.set(+y, new Map()).get(+y)!).set(t, s.size);
  }
  return out;
}

/** One variable of the daily table, every day held. */
export async function dailyVar(variable: string): Promise<SeriesRow[]> {
  return rest<SeriesRow>("series", { select: "entity,variable,ts_utc,value,unit", table_name: `eq.${DAILY}`, variable: `eq.${variable}`, order: "ts_utc" }, HOURLY, 20_000);
}

/** The daily table's notice counts (variables notices_<type>), every day with one. */
export async function dailyNotices(): Promise<SeriesRow[]> {
  return rest<SeriesRow>("series", { select: "entity,variable,ts_utc,value,unit", table_name: `eq.${DAILY}`, variable: "like.notices_*", order: "ts_utc" }, HOURLY, 20_000);
}
