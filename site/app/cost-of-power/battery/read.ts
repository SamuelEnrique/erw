// Session 208: what /cost-of-power/battery reads, shared by the page and by its CSV of every month (months.csv/route.ts).
// The rows of a ready grid come from Supabase (battery_stack_monthly); a grid in review is read from the committed
// snapshot, never from Supabase (session 86). The internal view's test is the proxy's own (lib/release.ts).
import { cookies } from "next/headers";
import reviewData from "@/data/battery_stack_review.json";
import { STRESS_TABLE, TABLE, type Inputs, type Row, type StressRow } from "@/lib/batterystack";
import { COOKIE, cookieOpens } from "@/lib/release";
import { HOURLY, rest } from "@/lib/supabase";

/** Whether this request carries the internal view's cookie. */
export async function internalView(): Promise<boolean> {
  const token = process.env.INTERNAL_COSTS_TOKEN;
  const have = (await cookies()).get(COOKIE)?.value;
  return cookieOpens(have, token);   // session 371: constant time (lib/release.ts); until then have === (await digest(token))
}
/** The rows of a grid in review, from the committed snapshot, for one strategy and duration. */
export function reviewRows(grid: string, x: Inputs): Row[] {
  const g = (reviewData as unknown as { grids: Record<string, { rows: [string, string, number][] }> }).grids[grid];
  const pre = `${x.strat}_${x.dur}h_`;
  return (g?.rows ?? []).filter((r) => r[0].startsWith(pre)).map(([variable, ts_utc, value]) => ({ variable, ts_utc, value }));
}
/** The monthly rows of a ready grid, from the live set. */
export async function rowsOf(entity: string, x: Pick<Inputs, "strat" | "dur">): Promise<Row[]> {
  return rest<Row>("series", { select: "variable,ts_utc,value", table_name: `eq.${TABLE}`, entity: `eq.${entity}`,
    variable: `like.${x.strat}_${x.dur}h_*`, order: "variable,ts_utc" }, HOURLY);
}
/** Session 257: the stress days of a ready grid for one strategy and duration, from the live set (the table is public).
 * The page reads them to name the events of the grid shown; a grid in review holds none and is never asked. */
export async function stressRowsOf(entity: string, x: Pick<Inputs, "strat" | "dur">): Promise<StressRow[]> {
  return rest<StressRow>("series", { select: "variable,ts_utc,value,event", table_name: `eq.${STRESS_TABLE}`, entity: `eq.${entity}`,
    variable: `like.${x.strat}_${x.dur}h_*`, order: "variable,ts_utc" }, HOURLY);
}
