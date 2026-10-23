// Energy Research Warehouse (ERW) site, session 1152 (chain 077): the figures of the Grid tool's energy mix panel
// (`grid_mix_<grid>`, components/grid/MixFigures.tsx), on the Mix tab above the hourly chart. Pure functions, no
// import, so a node test can load this file (scripts/test-mix-hourly.mjs).
//
// The hourly view reads eia930_all_generation (EIA-930 by balancing authority, the live set's recent window) and
// eia930_all_demand. No EIA-930 sub-region generation table exists in the live set: EIA-930 publishes demand by
// sub-region (eia930_subba_demand_hourly, out of the live set) and generation only by balancing authority.
// - The headline is the 24 hours that end with the newest hour held (an hour is held when its net_generation_mw is):
//   each fuel group's MWh, series_sum|eia930_all_generation|<variables, comma separated>|<start>|<end>|<entity>, and its
//   share of the 24 hours' net generation, calc|pct|<the fuel's key>|<the net generation key> ("~" for "|").
// - The peak is the hour of highest demand (demand_mw) in those 24 hours: series_max|eia930_all_demand|demand_mw|...
//   recomputes its MW as the highest of the window.
// - The newest hour held: series|eia930_all_generation|<entity>|net_generation_mw|<hour>.
// The monthly view reads generation_mix_hourly_profile (warehouse/derived/mix_profile.py, by grid, iso:<grid>): each
// fuel's MWh and stored share in the newest month, series|generation_mix_hourly_profile|iso:<grid>|<fuel>_mwh|<month>,
// and its MWh over the last twelve months held, series_esum|generation_mix_hourly_profile|iso:<grid>|<fuel>_mwh|<from>|<to>.

export type MixRow = { entity: string; variable: string; ts_utc: string; value: number };
export type Fig = { check: string; raw: number; tip: string };
/** A fuel group of the hourly chart: EIA-930's energy sources (without "net_generation_" and "_mw") it adds up. */
export type HourGroup = { key: string; label: string; vars: string[] };
/** A fuel of the monthly build: its stem in generation_mix_hourly_profile (natural_gas, coal, ...). */
export type MonthFuel = { key: string; label: string; stem: string };

export const GEN = "eia930_all_generation";
export const DEMAND = "eia930_all_demand";
export const PROFILE = "generation_mix_hourly_profile";
const H = 3_600_000;
const NET = "net_generation_mw";

export const isoZ = (t: number) => new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");
const hourName = (t: number) => `${new Date(t).toISOString().slice(0, 13).replace("T", " ")}:00 UTC`;
/** -0 is written 0 */
const z = (v: number) => v || 0;
/** A key inside a calc key: its bars written as "~". */
const inner = (k: string) => k.replaceAll("|", "~");

/** The fuel group of one EIA-930 variable (net_generation_<source>_mw); a source no group names is "other". */
export function groupOf(variable: string, groups: HourGroup[]): string {
  const f = variable.replace(/^net_generation_/, "").replace(/_mw$/, "");
  return groups.find((g) => g.vars.includes(f))?.key ?? "other";
}

export type HourFuel = { key: string; label: string; variables: string[]; mwh: Fig; share: Fig | null };
export type MixHourly = {
  entity: string;
  /** the newest hour held (its start, ms) and its net generation */
  newest: { t: number; fig: Fig };
  /** the 24 hours of the headline: [start, end) */
  start: number;
  end: number;
  /** how many of the 24 hours hold a net generation */
  hours: number;
  total: Fig;
  fuels: HourFuel[];
  /** the hour of highest demand in the 24 hours, or null when demand is not held for them */
  peak: { t: number; fig: Fig } | null;
};

/** The headline figures of one balancing authority's hourly mix, from its eia930_all_generation and demand rows. */
export function mixHourly(gen: MixRow[], demand: MixRow[], groups: HourGroup[]): MixHourly | null {
  const net = gen.filter((r) => r.variable === NET);
  if (!net.length) return null;
  const entity = net[0].entity;
  const newestT = Math.max(...net.map((r) => Date.parse(r.ts_utc)));
  const end = newestT + H, start = end - 24 * H;
  const inside = (r: MixRow) => { const t = Date.parse(r.ts_utc); return t >= start && t < end; };
  const window = `${hourName(start)} to ${hourName(end)}`;
  const netIn = net.filter(inside);
  const totalKey = `series_sum|${GEN}|${NET}|${isoZ(start)}|${isoZ(end)}|${entity}`;
  const totalMwh = netIn.reduce((a, r) => a + r.value, 0);
  const total: Fig = { check: totalKey, raw: z(totalMwh), tip: `${GEN}, ${entity}, ${NET}, the sum of the hours from ${window}: MWh` };
  const newestRow = net.find((r) => Date.parse(r.ts_utc) === newestT)!;
  const newest = { t: newestT, fig: { check: `series|${GEN}|${entity}|${NET}|${isoZ(newestT)}`, raw: newestRow.value, tip: `${GEN}, ${entity}, ${NET}, the hour from ${hourName(newestT)}: the newest hour the table holds` } };
  const by = new Map<string, { variables: Set<string>; mwh: number }>();
  for (const r of gen) {
    if (r.variable === NET || !inside(r)) continue;
    const k = groupOf(r.variable, groups);
    const g = by.get(k) ?? { variables: new Set<string>(), mwh: 0 };
    g.variables.add(r.variable);
    g.mwh += r.value;
    by.set(k, g);
  }
  const fuels: HourFuel[] = groups.filter((g) => by.has(g.key)).map((g) => {
    const { variables, mwh } = by.get(g.key)!;
    const vars = [...variables].sort();
    const check = `series_sum|${GEN}|${vars.join(",")}|${isoZ(start)}|${isoZ(end)}|${entity}`;
    const fig: Fig = { check, raw: z(mwh), tip: `${GEN}, ${entity}, ${vars.join(" + ")}, the sum of the hours from ${window}: MWh` };
    const share: Fig | null = totalMwh > 0
      ? { check: `calc|pct|${inner(check)}|${inner(totalKey)}`, raw: z((mwh / totalMwh) * 100), tip: `${g.label}'s MWh as a percent of the net generation (${NET}) over the same 24 hours, ${GEN}, ${entity}` }
      : null;
    return { key: g.key, label: g.label, variables: vars, mwh: fig, share };
  });
  const dem = demand.filter((r) => r.variable === "demand_mw" && r.entity === entity && inside(r));
  let peak: MixHourly["peak"] = null;
  if (dem.length) {
    const top = dem.reduce((a, r) => (r.value > a.value || (r.value === a.value && Date.parse(r.ts_utc) < Date.parse(a.ts_utc)) ? r : a));
    const t = Date.parse(top.ts_utc);
    peak = { t, fig: { check: `series_max|${DEMAND}|demand_mw|${isoZ(start)}|${isoZ(end)}|${entity}`, raw: top.value, tip: `${DEMAND}, ${entity}, demand_mw, the highest hour from ${window}: the hour from ${hourName(t)}` } };
  }
  return { entity, newest, start, end, hours: new Set(netIn.map((r) => Date.parse(r.ts_utc))).size, total, fuels, peak };
}

/** The age of an hour, in whole hours from its end to `now` (never below 0). */
export function hourAge(hourStart: number, now: number): number {
  return Math.max(0, Math.floor((now - (hourStart + H)) / H));
}

export type MonthFig = { key: string; label: string; stem: string; values: (number | null)[]; mwh: Fig | null; share: Fig | null; year: Fig | null };
export type MixMonthly = { entity: string; months: string[]; fuels: MonthFig[]; newest: string; from: string; to: string;
  /** the months of the twelve to the newest that the build did not write (YYYY-MM) */
  notBuilt: string[];
  /** the newest month's complete days and days in the month, as the build counts them */
  days: Fig | null; daysInMonth: Fig | null };

/** The monthly mix of one grid from generation_mix_hourly_profile: the months held (the last `n`), each fuel's MWh by
 *  month for the chart, the newest month's MWh and share, and the MWh of the last twelve months held. */
export function mixMonthly(rows: MixRow[], fuels: MonthFuel[], n = 24): MixMonthly | null {
  const mwh = rows.filter((r) => r.variable.endsWith("_mwh"));
  if (!mwh.length) return null;
  const entity = mwh[0].entity;
  const day = (r: MixRow) => r.ts_utc.slice(0, 10);
  const months = [...new Set(mwh.map(day))].sort().slice(-n);
  const newest = months[months.length - 1];
  // the twelve calendar months to the newest (a month the build did not write is left out and named)
  const y = Number(newest.slice(0, 4)), mo = Number(newest.slice(5, 7));
  const from = isoZ(Date.UTC(y, mo - 12, 1)), to = isoZ(Date.UTC(y, mo, 1));
  const twelve = Array.from({ length: 12 }, (_, i) => isoZ(Date.UTC(y, mo - 12 + i, 1)).slice(0, 10));
  const last12 = twelve.filter((d) => months.includes(d));
  const notBuilt = twelve.filter((d) => !months.includes(d)).map((d) => d.slice(0, 7));
  const val = new Map(rows.map((r) => [`${r.variable}|${day(r)}`, r.value]));
  const out: MonthFig[] = fuels.filter((f) => mwh.some((r) => r.variable === `${f.stem}_mwh`)).map((f) => {
    const v = `${f.stem}_mwh`, s = `${f.stem}_share_pct`;
    const at = val.get(`${v}|${newest}`), sh = val.get(`${s}|${newest}`);
    const held12 = last12.filter((m) => val.has(`${v}|${m}`));
    const sum12 = held12.reduce((a, m) => a + val.get(`${v}|${m}`)!, 0);
    return {
      key: f.key, label: f.label, stem: f.stem,
      values: months.map((m) => val.get(`${v}|${m}`) ?? null),
      mwh: at === undefined ? null : { check: `series|${PROFILE}|${entity}|${v}|${newest}T00:00:00Z`, raw: at, tip: `${PROFILE}, ${entity}, ${v}, ${newest.slice(0, 7)}: MWh over the month's complete days` },
      share: sh === undefined ? null : { check: `series|${PROFILE}|${entity}|${s}|${newest}T00:00:00Z`, raw: sh, tip: `${PROFILE}, ${entity}, ${s}, ${newest.slice(0, 7)}: percent of the sum of the eight sources` },
      year: held12.length ? { check: `series_esum|${PROFILE}|${entity}|${v}|${from}|${to}`, raw: z(sum12), tip: `${PROFILE}, ${entity}, ${v}, the sum of the months held from ${from.slice(0, 7)} to ${newest.slice(0, 7)}${notBuilt.length ? ` (not built: ${notBuilt.join(", ")})` : ""}` } : null,
    };
  });
  const count = (v: string, what: string): Fig | null => {
    const x = val.get(`${v}|${newest}`);
    return x === undefined ? null : { check: `series|${PROFILE}|${entity}|${v}|${newest}T00:00:00Z`, raw: x, tip: `${PROFILE}, ${entity}, ${v}, ${newest.slice(0, 7)}: ${what}` };
  };
  return { entity, months, fuels: out, newest, from, to, notBuilt, days: count("days_held", "the complete days the month is built on"), daysInMonth: count("days_in_month", "the days of the month") };
}
