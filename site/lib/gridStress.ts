// Energy Research Warehouse (ERW) site, session 1168 (chain 078): "How hard the system works" on the Grid tool's Mix tab
// (/grid?view=mix&mix=stress, components/mix/views.tsx StressView), drawn year by year. Four measures of
// docs/methods/grid_stress.md, each a chart with a point a year and, on hover, the year, the value and its unit, a note
// of the year's figures behind it (MW, the hour it began) and the line of what the figure is not:
//   ramp      the largest evening ramp, in one hour and over three, as a share of the year's peak demand (the chart
//             that stood since session 133; its series are as they were, the notes and the line are new)
//   netload   the lowest net load of the year, as a share of the year's peak demand
//   tight     each fuel's output in the year's tightest hours, as a share of its installed capacity
//   calm      the longest dark, calm stretch of the year, in hours
// Every value is a figure of the site's copy of grid_stress_yearly (site/data/stress/<grid>.json, through lib/stress.ts),
// picked, never computed: a year or a figure the file does not hold is a gap (null), never a zero. The table is public
// (EIA-930, EIA-860M, storage_buildout_monthly: site/data/license_status.json), so every grid is drawn. Pure: a node
// test runs it on the committed files (scripts/test-grid-stress.mjs).
import { caisoJoinDay } from "@/lib/caisoJoin";
import { n0, n1 } from "@/lib/mixpage";
import * as stress from "@/lib/stress";
import type { GridFile } from "@/lib/stress";

/** The method note's lines, each chart's own (docs/methods/grid_stress.md, "What each chart is not (session 1168)"). */
export const STRESS_METHOD = "/data/methods/grid_stress#what-each-chart-is-not-session-1168";
export type Measure = "ramp" | "netload" | "tight" | "calm";
export const MEASURES: readonly Measure[] = ["ramp", "netload", "tight", "calm"];

/** What each figure is not, in short (the note's "What the figures are not" and the two lines session 1168 added). */
export const NOT: Record<Measure, string> = {
  ramp: "Not a reliability study: the largest rise of net load from one hour to the next between 14:00 and 22:00 local, a spike the next hour takes back by more than half left out. Outages, transmission limits and reserves are not in the file.",
  netload: `One hour, not a level held: the year's single lowest hour of demand less wind less solar, set against the same year's peak demand. California across the join of ${caisoJoinDay()} is two series.`,
  tight: "Not what a plant could do: a plant below its capacity in a tight hour may have been in reserve, on outage, out of fuel or not needed; the share is what the fleet did. Not a reliability study: the hours are tight by net load.",
  calm: "Not a sizing of storage: the energy missing is set against today's battery fleet to show its scale. Dark and calm is one line, wind and solar below a tenth of their capacity, so a grid with much solar and little wind is below it most nights.",
};

/** A year as the tables write it: "2026 to date" when the file's year is not whole. */
export const yearName = (f: GridFile, y: string): string => `${y}${stress.wholeYear(f, y) ? "" : " to date"}`;

/** The years of several grids' files, in order, each once (the chart's categories). */
export const yearsOfAll = (fs: GridFile[]): string[] => [...new Set(fs.flatMap((f) => stress.yearsOf(f)))].sort();

/** One figure of a year, null when the year or the figure is not in the file. */
export const fig = (f: GridFile, y: string, k: string): number | null => (f.years[y] ? stress.get(f, y, k) : null);

/** The values of one variable over the years, a gap where the file holds none. */
export const valuesOf = (f: GridFile, years: string[], k: string): (number | null)[] => years.map((y) => fig(f, y, k));

const when = (f: GridFile, y: string, k: string): string | null => { const t = stress.at(f, y, k); return t ? stress.when(t, f.tz) : null; };
const join = (parts: (string | null | false)[]): string => parts.filter(Boolean).join("; ");
const partial = (f: GridFile, y: string): string | null => (f.years[y] && !stress.wholeYear(f, y) ? "the year to date" : null);

/** The hover note of a year's evening ramp: its MW in one hour and the hour it began, over three hours, the peak. */
export function rampNote(f: GridFile, y: string): string | null {
  const one = fig(f, y, "evening_ramp_max_mw_per_h"), three = fig(f, y, "evening_ramp_3h_max_mw"), peak = fig(f, y, "peak_demand_mw");
  if (one === null && three === null) return null;
  const at = when(f, y, "evening_ramp_max_mw_per_h");
  return join([one !== null && `in one hour ${n0(one)} MW${at ? `, starting ${at}` : ""}`, three !== null && `over three hours ${n0(three)} MW`, peak !== null && `peak demand ${n0(peak)} MW`, partial(f, y)]);
}

/** The hover note of a year's lowest net load: its MW, its hour and the peak it is set against. */
export function netLoadNote(f: GridFile, y: string): string | null {
  const mw = fig(f, y, "net_load_min_mw"), peak = fig(f, y, "peak_demand_mw");
  if (mw === null) return null;
  const at = when(f, y, "net_load_min_mw");
  return join([`${n0(mw)} MW${at ? `, ${at}` : ""}`, peak !== null && `peak demand ${n0(peak)} MW`, partial(f, y)]);
}

/** A note for each year: one grid's own, or each grid's prefixed with its name. */
export function notesOf(fs: GridFile[], years: string[], note: (f: GridFile, y: string) => string | null): (string | null)[] {
  return years.map((y) => {
    if (fs.length === 1) return note(fs[0], y);
    const ls = fs.map((f) => { const s = note(f, y); return s ? `${f.name}: ${s}` : null; }).filter((s): s is string => s !== null);
    return ls.length ? ls.join(". ") : null;
  });
}

/** Each fuel's output in the tightest hours as a share of its installed capacity, by year: the fuels with a share in
 *  any year, in the file's order (hydro and storage apart have none: they are set against capacity together). */
export function tightLines(f: GridFile, years: string[]): { fuel: string; name: string; values: (number | null)[] }[] {
  return f.fuels.map((fuel) => ({
    fuel, name: stress.FUEL_NAME[fuel] ?? fuel,
    values: years.map((y) => (f.years[y] ? stress.fuelRows(f, y).find((r) => r.fuel === fuel)?.share ?? null : null)),
  })).filter((l) => l.values.some((v) => v !== null));
}

/** The hover note of a year's tightest hours: how many, and their mean net load. */
export function tightNote(f: GridFile, y: string): string | null {
  const nl = fig(f, y, "tight_net_load_mw");
  if (nl === null) return null;
  return join([`mean net load in the ${f.tight} tightest hours ${n0(nl)} MW`, partial(f, y)]);
}

/** The hover note of a year's longest dark, calm stretch: when it began, the energy missing, the battery fleet's
 *  hours at full power, the dark, calm hours of the year. */
export function calmNote(f: GridFile, y: string): string | null {
  const h = fig(f, y, "calm_longest_hours");
  if (h === null) return null;
  const at = when(f, y, "calm_longest_hours"), miss = fig(f, y, "calm_longest_missing_mwh"), full = fig(f, y, "calm_longest_fleet_full_power_hours"), all = fig(f, y, "calm_hours");
  return join([`${stress.span(h)}${at ? `, beginning ${at}` : ""}`, miss !== null && `${n0(miss)} MWh missing`, full !== null && `${n1(full)} hours of the battery fleet at full power`,
    all !== null && `${n0(all)} dark, calm hours in the year`, partial(f, y)]);
}
