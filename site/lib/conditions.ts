// Energy Research Warehouse (ERW) site, session 9000 (chain 601, part G): the grid conditions page (/conditions) reads
// data/conditions/<operator>.json and index.json, written by the data machine (warehouse/derived/conditions_page.py;
// contract docs/state/page_files_conditions.md, section 2; method docs/methods/grid_conditions.md). This module holds
// the files' shape and the choice of a window. Nothing is filled: a day or hour not held has no point.

import caiso from "@/data/conditions/caiso.json";
import ercot from "@/data/conditions/ercot.json";
import spp from "@/data/conditions/spp.json";
import miso from "@/data/conditions/miso.json";
import pjm from "@/data/conditions/pjm.json";
import nyiso from "@/data/conditions/nyiso.json";
import isone from "@/data/conditions/isone.json";
import index from "@/data/conditions/index.json";

export type Strip = { status: string; source?: string; why?: string; note?: string };
export type Window = { id: string; title: string; start: string; end: string };
/** daily: [day, demand_peak, demand_min, forecast_peak, out_mean, out_max, cons_hours, cons_max, adder_hours, adder_max, alerts] */
export type DailyRow = [string, ...(number | null)[]];
/** hourly: [ts_utc, demand, forecast, out_total, out_planned, out_forced, cons_n, cons_max, adder] */
export type HourlyRow = [string, ...(number | null)[]];
export type OperatorFile = {
  built: string; method: string; license: string; op: string; name: string; ba: string; time: string;
  strips: Record<string, Strip>; first_day: string | null; last_day: string | null;
  daily_columns: string[]; daily: DailyRow[]; hourly_columns: string[]; windows: Window[];
  hourly: Record<string, HourlyRow[]>; alert_columns: string[]; alerts: [string, string, string | null, string | null, string][];
};
export type Index = { built: string; method: string; contract: string; license: string; recent_days: number;
  events: { id: string; title: string; start: string; end: string }[];
  operators: { op: string; name: string; ba: string; strips: Record<string, string>; first_day: string | null; last_day: string | null }[] };

export const FILES: Record<string, OperatorFile> = Object.fromEntries(
  [caiso, ercot, spp, miso, pjm, nyiso, isone].map((f) => [(f as unknown as OperatorFile).op, f as unknown as OperatorFile]));
export const INDEX = index as unknown as Index;
export const OP_IDS = INDEX.operators.map((o) => o.op);
export const DAY = 86_400_000;
export const toMs = (day: string) => Date.parse(`${day}T00:00:00Z`);
export const dayOf = (ms: number) => new Date(ms).toISOString().slice(0, 10);

/** The column index of a name in a file's daily or hourly rows. */
export const col = (cols: string[], name: string) => cols.indexOf(name);

/** The window a reader asked for: an event, a day (fifteen days either side, daily), or the newest days. */
export function windowOf(f: OperatorFile, event: string | undefined, day: string | undefined): { start: string; end: string; title: string; hourly: string | null } {
  const ev = f.windows.find((w) => w.id === event && w.id !== "recent");
  if (ev) return { start: ev.start, end: ev.end, title: ev.title, hourly: f.hourly[ev.id] ? ev.id : null };
  if (day && /^\d{4}-\d{2}-\d{2}$/.test(day)) {
    const t = toMs(day);
    const hit = f.windows.find((w) => w.start <= day && day <= w.end && f.hourly[w.id]);
    return { start: dayOf(t - 15 * DAY), end: dayOf(t + 15 * DAY), title: `the fifteen days either side of ${day}`, hourly: hit ? hit.id : null };
  }
  const rec = f.windows.find((w) => w.id === "recent") as Window;
  return { start: rec.start, end: rec.end, title: rec.title, hourly: f.hourly.recent ? "recent" : null };
}
