// Energy Research Warehouse (ERW) site, session 1185 (chain 091): the Lower 48's monthly mix on the Grid tool's energy
// mix panel (grid_mix_us48, mixp=month). generation_mix_hourly_profile is built for the seven ISO grids only, and no
// table of the live set holds EIA-930's US48 by month (eia930_all_generation holds eia930:US48 for its recent window of
// hours; carbon_intensity_monthly holds the Lower 48's intensity, not its mix). So the Lower 48's month is the sum of the
// 48 contiguous states and the District of Columbia in state_generation_mix_monthly: EIA-923's net generation by state
// (docs/methods/generation_mix.md), not EIA-930's US48, which adds up balancing authorities hour by hour.
// - A month is drawn only when every one of the 49 holds it (a row of any group: the table writes a location's month only
//   when EIA publishes its total). A month that misses one is not drawn and not summed, and the panel names it.
// - A fuel group's figure is the sum of the 49 over the months held:
//   states_sum|state_generation_mix_monthly|<variables, comma separated>|<start>|<end>|lower48, a new key kind that
//   scripts/check-values.mjs recomputes with statesSum below on the rows it reads (the 49's rows from start to end): the
//   same rule, the same function. The month's total is the same key over the nine groups' variables; a share is
//   calc|pct|<the group's key>|<the total's key> ("~" for "|").
// Pure functions, no import, so a node test and check-values load this file (scripts/test-lower48.mjs).

export const STATE_MIX = "state_generation_mix_monthly";
/** The name of the group in a states_sum key. */
export const LOWER48 = "lower48";
/** The 48 contiguous states and the District of Columbia, as EIA writes them (eia:<code> in the table). */
export const LOWER48_STATES = ["AL", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
  "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"];
export const LOWER48_ENTITIES = LOWER48_STATES.map((s) => `eia:${s}`);
/** The entities a group of a states_sum key names; a group this file does not know throws. */
export function groupEntities(group: string): string[] {
  if (group === LOWER48) return LOWER48_ENTITIES;
  throw new Error(`states_sum: no group named ${group}`);
}

/** A fuel group of state_generation_mix_monthly (docs/methods/generation_mix.md), in components/mix/Now.tsx
 *  MONTHLY_FUELS' order, words and colors. */
export type L48Fuel = { key: string; label: string; color: string };
export const LOWER48_FUELS: L48Fuel[] = [
  { key: "natural_gas", label: "Natural gas", color: "var(--color-fuel-gas)" },
  { key: "coal", label: "Coal", color: "var(--color-fuel-coal)" },
  { key: "nuclear", label: "Nuclear", color: "var(--color-fuel-nuclear)" },
  { key: "wind", label: "Wind", color: "var(--color-fuel-wind)" },
  { key: "solar", label: "Solar (utility scale)", color: "var(--color-fuel-solar)" },
  { key: "hydro", label: "Hydro", color: "var(--color-fuel-hydro)" },
  { key: "other_renewables", label: "Geothermal and biomass", color: "var(--color-fuel-storage)" },
  { key: "oil_and_other", label: "Oil, other gases, pumped storage, other", color: "var(--color-fuel-other)" },
  { key: "not_itemized", label: "Not itemized by EIA", color: "var(--color-muted)" },
];
export const varOf = (k: string) => `net_generation_${k}_mwh`;
/** The nine groups' variables: their sum is a state's net generation, EIA's total (the method note). */
export const LOWER48_VARIABLES = LOWER48_FUELS.map((f) => varOf(f.key));

export type L48Row = { entity: string; variable: string; ts_utc: string; value: number };
export type L48Fig = { check: string; raw: number; tip: string };

/** -0 is written 0 */
const z = (v: number) => v || 0;
const inner = (k: string) => k.replaceAll("|", "~");
/** A month's first instant, YYYY-MM-01T00:00:00Z, from a row's ts_utc or a month (YYYY-MM). */
export const monthStart = (s: string) => `${s.slice(0, 7)}-01T00:00:00Z`;
/** The month after (YYYY-MM-01T00:00:00Z). */
export function nextMonth(s: string): string {
  const y = Number(s.slice(0, 4)), m = Number(s.slice(5, 7));
  return new Date(Date.UTC(y, m, 1)).toISOString().replace(/\.\d{3}Z$/, "Z");
}

/** Each month the rows touch (YYYY-MM), with the entities of the group that hold it and those that do not. */
export function monthsOf(rows: L48Row[], entities: string[]): Map<string, { held: boolean; missing: string[] }> {
  const want = new Set(entities);
  const by = new Map<string, Set<string>>();
  for (const r of rows) {
    if (!want.has(r.entity)) continue;
    const m = r.ts_utc.slice(0, 7);
    (by.get(m) ?? by.set(m, new Set()).get(m)!).add(r.entity);
  }
  return new Map([...by].sort(([a], [b]) => (a < b ? -1 : 1)).map(([m, s]) => [m, { held: s.size === want.size, missing: entities.filter((e) => !s.has(e)).map((e) => e.replace(/^eia:/, "")) }]));
}

/** The recomputation of a states_sum key: the sum of the variables' rows of the group's entities over the months from
 *  start (included) to end (excluded) that every entity holds; undefined when no such row is held. check-values reads
 *  the group's rows of every variable in the range (a month is held by a row of any group) and calls this. */
export function statesSum(rows: L48Row[], entities: string[], variables: string[], start: string, end: string): number | undefined {
  const s = Date.parse(start), e = Date.parse(end);
  const inside = rows.filter((r) => { const t = Date.parse(r.ts_utc); return t >= s && t < e; });
  const months = monthsOf(inside, entities);
  const want = new Set(entities), vars = new Set(variables);
  let sum = 0, n = 0;
  for (const r of inside) {
    if (!want.has(r.entity) || !vars.has(r.variable) || !months.get(r.ts_utc.slice(0, 7))?.held) continue;
    sum += r.value;
    n += 1;
  }
  return n ? z(sum) : undefined;
}

/** A states_sum key, and its parts back. */
export const statesSumKey = (variables: string[], start: string, end: string, group = LOWER48) => `states_sum|${STATE_MIX}|${variables.join(",")}|${start}|${end}|${group}`;
export function parseStatesSum(check: string): { table: string; variables: string[]; start: string; end: string; group: string } | null {
  const p = check.split("|");
  if (p[0] !== "states_sum" || p.length !== 6) return null;
  return { table: p[1], variables: p[2].split(",").filter(Boolean), start: p[3], end: p[4], group: p[5] };
}

export type L48FuelFig = L48Fuel & { values: (number | null)[]; mwh: L48Fig | null; share: L48Fig | null; year: L48Fig | null };
export type Lower48Monthly = {
  /** the months drawn, YYYY-MM-01 (the last `n` that every one of the 49 holds) */
  months: string[];
  newest: string;
  /** the twelve calendar months to the newest: [from, to) */
  from: string;
  to: string;
  /** of the twelve, those not drawn (YYYY-MM), each with the states (or DC) it misses ("all" when no row of it is read) */
  notHeld: { month: string; missing: string[] }[];
  fuels: L48FuelFig[];
  /** the newest month's net generation (the nine groups) and the twelve months' */
  total: L48Fig;
  totalYear: L48Fig;
};

/** The Lower 48's monthly mix from the 49's rows of state_generation_mix_monthly. */
export function lower48Monthly(rows: L48Row[], n = 24): Lower48Monthly | null {
  const ents = LOWER48_ENTITIES;
  const months = monthsOf(rows, ents);
  const held = [...months].filter(([, v]) => v.held).map(([m]) => `${m}-01`);
  if (!held.length) return null;
  const drawn = held.slice(-n);
  const newest = drawn[drawn.length - 1];
  const y = Number(newest.slice(0, 4)), mo = Number(newest.slice(5, 7));
  const iso = (t: number) => new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");
  const from = iso(Date.UTC(y, mo - 12, 1)), to = iso(Date.UTC(y, mo, 1));
  const twelve = Array.from({ length: 12 }, (_, i) => iso(Date.UTC(y, mo - 12 + i, 1)).slice(0, 7));
  const notHeld = twelve.filter((m) => !months.get(m)?.held).map((m) => ({ month: m, missing: months.get(m)?.missing ?? ["all"] }));
  const heldSet = new Set(held.map((m) => m.slice(0, 7))), entSet = new Set(ents);
  const at = new Map<string, number>();   // variable|YYYY-MM: the 49's sum, held months only
  for (const r of rows) {
    const m = r.ts_utc.slice(0, 7);
    if (!heldSet.has(m) || !entSet.has(r.entity)) continue;
    const k = `${r.variable}|${m}`;
    at.set(k, (at.get(k) ?? 0) + r.value);
  }
  const nm = newest.slice(0, 7), mStart = monthStart(nm), mEnd = nextMonth(mStart);
  const span = `the 48 contiguous states and DC, summed`;
  const totalRaw = LOWER48_VARIABLES.reduce((a, v) => a + (at.get(`${v}|${nm}`) ?? 0), 0);
  const total: L48Fig = { check: statesSumKey(LOWER48_VARIABLES, mStart, mEnd), raw: z(totalRaw), tip: `${STATE_MIX}, ${span}, the nine groups (net generation), ${nm}: MWh (EIA-923)` };
  const yearMonths = twelve.filter((m) => heldSet.has(m));
  const yearRaw = yearMonths.reduce((a, m) => a + LOWER48_VARIABLES.reduce((b, v) => b + (at.get(`${v}|${m}`) ?? 0), 0), 0);
  const gaps = notHeld.length ? ` (not drawn: ${notHeld.map((x) => x.month).join(", ")})` : "";
  const totalYear: L48Fig = { check: statesSumKey(LOWER48_VARIABLES, from, to), raw: z(yearRaw), tip: `${STATE_MIX}, ${span}, the nine groups (net generation), the months held from ${from.slice(0, 7)} to ${nm}${gaps}: MWh (EIA-923)` };
  const fuels: L48FuelFig[] = LOWER48_FUELS.filter((f) => drawn.some((m) => at.has(`${varOf(f.key)}|${m.slice(0, 7)}`))).map((f) => {
    const v = varOf(f.key);
    const x = at.get(`${v}|${nm}`);
    const mwh: L48Fig | null = x === undefined ? null : { check: statesSumKey([v], mStart, mEnd), raw: z(x), tip: `${STATE_MIX}, ${span}, ${v}, ${nm}: MWh (EIA-923)` };
    const share: L48Fig | null = mwh && totalRaw > 0 ? { check: `calc|pct|${inner(mwh.check)}|${inner(total.check)}`, raw: z((x! / totalRaw) * 100), tip: `${f.label}'s MWh as a percent of the nine groups' (net generation), ${nm}, ${STATE_MIX}, ${span}` } : null;
    const inYear = yearMonths.filter((m) => at.has(`${v}|${m}`));
    const year: L48Fig | null = inYear.length ? { check: statesSumKey([v], from, to), raw: z(inYear.reduce((a, m) => a + at.get(`${v}|${m}`)!, 0)), tip: `${STATE_MIX}, ${span}, ${v}, the months held from ${from.slice(0, 7)} to ${nm}${gaps}: MWh (EIA-923)` } : null;
    return { ...f, values: drawn.map((m) => at.get(`${v}|${m.slice(0, 7)}`) ?? null), mwh, share, year };
  });
  return { months: drawn, newest, from, to, notHeld, fuels, total, totalYear };
}
