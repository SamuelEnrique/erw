// Session 60: the Flex Alert scorecard, the data of /grid/caiso/alerts. Two derived tables in the Supabase live set:
// flex_alert_effects (per alert day, P1D; per evening hour of an alert day, PT1H; per year, P1Y) and flex_alert_model
// (the pooled result, out-of-sample statistics, the variants, the held-out hot days). warehouse/derived/flex_alert_scorecard.py
// writes them; docs/methods/flex_alert_scorecard.md is the method. Every number on the page is a row of these tables,
// shown with its check key (series|<table>|<entity>|<variable>|<ts_utc>).
import type { SeriesRow } from "@/lib/data";
import { HOURLY, rest } from "@/lib/supabase";

export const EFFECTS = "flex_alert_effects";
export const MODEL = "flex_alert_model";
export const E = "eia930:CISO";
export const M = "erw:flex_alert_model";
export const T0 = "2018-07-01T00:00:00Z";
export const VARIANTS: { id: string; name: string }[] = [
  { id: "minimal", name: "Minimal: cooling degree hours, their square, the calendar" },
  { id: "base", name: "Plus the 24 hours before and the dew point" },
  { id: "base_prev24sq", name: "Plus the square of the 24 hours before" },
  { id: "base_cdh_dew", name: "Plus cooling degree hours times dew point" },
  { id: "chosen", name: "Both (the model used): lowest error on hot days" },
];

export const key = (r: SeriesRow, table = EFFECTS) => `series|${table}|${r.entity}|${r.variable}|${r.ts_utc}`;

/** Every row of flex_alert_effects, oldest first. */
export async function effects(): Promise<SeriesRow[]> {
  return rest<SeriesRow>("series", { select: "entity,variable,ts_utc,value,unit,freq", table_name: `eq.${EFFECTS}`, order: "ts_utc,variable" }, HOURLY, 20_000);
}

/** flex_alert_model without its coefficients (the page does not show them; the method and the CSV do). */
export async function model(): Promise<SeriesRow[]> {
  return rest<SeriesRow>("series", { select: "entity,variable,ts_utc,value,unit,freq", table_name: `eq.${MODEL}`, variable: "not.like.coef_*", order: "ts_utc,variable" }, HOURLY, 5_000);
}

export type Day = { day: string; ts: string; v: Map<string, SeriesRow> };

/** The per-day rows grouped by day; the per-hour rows by day (Pacific); the per-year rows by year; the model's rows by name. */
export function shape(eff: SeriesRow[], mod: SeriesRow[]) {
  const days = new Map<string, Day>(), hours = new Map<string, SeriesRow[]>(), years = new Map<string, Map<string, SeriesRow>>();
  for (const r of eff) {
    if (r.freq === "P1D") {
      const d = r.ts_utc.slice(0, 10);
      const x = days.get(d) ?? days.set(d, { day: d, ts: r.ts_utc, v: new Map() }).get(d)!;
      x.v.set(r.variable, r);
    } else if (r.freq === "PT1H") {
      const d = pacificDay(r.ts_utc);
      (hours.get(d) ?? hours.set(d, []).get(d)!).push(r);
    } else if (r.freq === "P1Y") {
      const y = r.ts_utc.slice(0, 4);
      (years.get(y) ?? years.set(y, new Map()).get(y)!).set(r.variable.replace(/^year_/, ""), r);
    }
  }
  const pooled = new Map<string, SeriesRow>(), heldout: { day: string; err?: SeriesRow; temp?: SeriesRow; price?: SeriesRow }[] = [];
  const ho = new Map<string, { day: string; err?: SeriesRow; temp?: SeriesRow; price?: SeriesRow }>();
  for (const r of mod) {
    if (Date.parse(r.ts_utc) === Date.parse(T0)) pooled.set(r.variable, r);  // Supabase writes +00:00, not Z
    else {
      const d = r.ts_utc.slice(0, 10);
      const x = ho.get(d) ?? ho.set(d, { day: d }).get(d)!;
      if (r.variable === "heldout_error_mw") x.err = r;
      if (r.variable === "heldout_temp_max_f") x.temp = r;
      if (r.variable === "heldout_price_usd_mwh") x.price = r;
    }
  }
  heldout.push(...[...ho.values()].sort((a, b) => a.day.localeCompare(b.day)));
  return { days: [...days.values()], hours, years, model: pooled, heldout };
}

/** The Pacific day of a UTC instant (the alert season is all daylight time, UTC-7). */
export function pacificDay(ts: string): string {
  return new Date(Date.parse(ts) - 7 * 3600_000).toISOString().slice(0, 10);
}
export function pacificHour(ts: string): number {
  return new Date(Date.parse(ts) - 7 * 3600_000).getUTCHours();
}
