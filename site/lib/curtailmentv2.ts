// Session 98: curtailment, version 2 (then /curtailment/v2; since session 144 part of /curtailment). The pure part: what the page chooses from its address
// and how it reads the site's own copy of caiso_curtailment_profile (data/curtailment_profile.json, written by
// warehouse/derived/curtailment_profile.py; docs/methods/caiso_curtailment_intervals.md). No arithmetic beyond adding
// wind to solar for a bar's height: every number shown is a row of the table, or a year's sum the builder wrote.
export const TABLE = "caiso_curtailment_profile";
export const INPUT = "caiso_curtailment_intervals";

export type Row = Record<string, number>;
export type CurtFile = {
  table: string; input: string; built: string; first: string; last: string; near: number; first_day: string; last_day: string; days_not_held: string[];
  months: Record<string, Row>; years: Record<string, Row>;
};
export const FUELS = [{ key: "solar", label: "Solar", color: "var(--color-fuel-solar)" }, { key: "wind", label: "Wind", color: "var(--color-fuel-wind)" }] as const;
export const REASONS = [
  { key: "local", label: "Local congestion", color: "var(--color-accent)" },
  { key: "system", label: "System-wide oversupply", color: "var(--color-fuel-storage)" },
  { key: "unspecified", label: "No reason published", color: "var(--color-not-reported)" },
] as const;
export const CATS = [
  { key: "econ", label: "Economic bids", what: "Market dispatch of generators with economic bids" },
  { key: "ss", label: "Self-schedule cuts", what: "Market dispatch of self-schedules" },
  { key: "oi", label: "Operator instructions", what: "Operator instructions" },
] as const;

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
export const periodName = (p: string) => (p.length === 7 ? `${MONTHS[Number(p.slice(5)) - 1]} ${p.slice(0, 4)}` : p);
export const hourName = (h: number) => `${String(h).padStart(2, "0")}:00`;
export const whole = (v: number) => Math.round(v).toLocaleString("en-US");
export const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const pad = (n: number) => String(n).padStart(2, "0");

export const periodOf = (f: CurtFile, p: string | undefined): Row | null => (!p ? null : (p.length === 7 ? f.months[p] : f.years[p]) ?? null);
/** The page's period from its address: a month or a year the copy holds, or the newest whole year. */
export function choice(q: Record<string, string | undefined>, f: CurtFile): string {
  if (q.period && periodOf(f, q.period)) return q.period;
  return Object.keys(f.years).sort().at(-1) ?? f.last;
}
// session 144: version 2 is part of the one page now (/curtailment); /curtailment/v2 redirects there (next.config.ts)
export const href = (period: string) => `/curtailment?period=${period}`;

/** A fuel's MWh by local hour of the day over a period. */
export const byHour = (r: Row, fuel: string): number[] => Array.from({ length: 24 }, (_, h) => r[`curtailed_${fuel}_mwh_h${pad(h)}`] ?? 0);
/** The hour of the day in which the most was curtailed (wind and solar), with its MWh by fuel. */
export function peakHour(r: Row): { hour: number; solar: number; wind: number } {
  const s = byHour(r, "solar"), w = byHour(r, "wind");
  let best = 0;
  for (let h = 1; h < 24; h++) if (s[h] + w[h] > s[best] + w[best]) best = h;
  return { hour: best, solar: s[best], wind: w[best] };
}
/** Whether CAISO published a reason for any of the period's curtailment, and whether for all of it. */
export function reasonCover(r: Row): "none" | "part" | "all" {
  const un = (r.curtailed_solar_unspecified_mwh ?? 0) + (r.curtailed_wind_unspecified_mwh ?? 0);
  const known = (r.curtailed_solar_local_mwh ?? 0) + (r.curtailed_wind_local_mwh ?? 0) + (r.curtailed_solar_system_mwh ?? 0) + (r.curtailed_wind_system_mwh ?? 0);
  return known === 0 ? "none" : un === 0 ? "all" : "part";
}
export const hasCats = (r: Row) => r.curtailed_solar_econ_mwh !== undefined;
export const hasBattery = (r: Row) => r.battery_days_held !== undefined;
/** The average day of a month with the batteries: curtailment and battery charging by local hour, MW. */
export const battDay = (r: Row) => Array.from({ length: 24 }, (_, h) => ({ hour: h, curtailed: r[`avg_curtailed_mw_h${pad(h)}`] ?? 0, charging: r[`avg_battery_charging_mw_h${pad(h)}`] ?? 0 }));
/** The months the copy holds with the batteries, in order. */
export const batteryMonths = (f: CurtFile) => Object.keys(f.months).sort().filter((m) => hasBattery(f.months[m]));
