// Energy Research Warehouse (ERW) site, session 115: what Texas's storage resources were awarded day-ahead
// (/cost-of-power/battery/awards, in review).
//
// The arithmetic of the page, on the rows of ercot_storage_dam_awards_monthly (warehouse/derived, from ERCOT's 60-Day
// DAM Disclosure Reports, the file 60d_DAM_ESR_Data) and, beside them, the battery model's day-ahead schedule for a
// 2-hour battery from battery_stack_monthly. Pure functions, no imports (Node runs this file as it is, for
// tests/test_session115_page.py). Nothing is scaled, filled or estimated: a month whose days are not all held is
// partial and is never set beside the model, whose month is whole; a figure that is not held is null.

export const TABLE = "ercot_storage_dam_awards_monthly";
export const ENTITY = "ercot:esr_fleet";
export const MODEL_TABLE = "battery_stack_monthly";
export const MODEL_ENTITY = "ercot:HB_HUBAVG";
/** The model's rows the page reads: the day-ahead schedule, a 2-hour battery, USD per MW by month, and its days. */
export const MODEL_PREFIX = "dayahead_2h_";
export const MODEL_VARIABLES = ["revenue_total_usd_per_mw", "revenue_energy_usd_per_mw", "revenue_ancillary_usd_per_mw", "days_held", "days_in_month"].map((v) => MODEL_PREFIX + v);
/** The fleet's variables the page reads. */
export const VARIABLES = [
  "days_held", "days_missing", "days_in_month", "resources", "resources_with_award", "resource_hours", "resource_hours_energy_award", "mw",
  "revenue_energy_usd_per_mw", "revenue_ancillary_usd_per_mw", "revenue_total_usd_per_mw",
  "revenue_regup_usd_per_mw", "revenue_regdn_usd_per_mw", "revenue_rrs_usd_per_mw", "revenue_ecrs_usd_per_mw", "revenue_nspin_usd_per_mw",
];
export const PRODUCTS: { key: string; label: string }[] = [
  { key: "regup", label: "Regulation Up" }, { key: "regdn", label: "Regulation Down" }, { key: "rrs", label: "Responsive Reserve" },
  { key: "ecrs", label: "ECRS" }, { key: "nspin", label: "Non-Spin" },
];

/** A row of a series table as the live set serves it. */
export type Row = { variable: string; ts_utc: string; value: number | string };

/** The model's figure for one month, USD per MW, and whether the model holds every day of it. */
export type Model = { energy: number | null; ancillary: number | null; total: number; whole: boolean };

export type Month = {
  /** YYYY-MM, the local (Central) month */
  m: string;
  daysHeld: number; daysMissing: number | null; daysInMonth: number;
  /** every day of the month is held */
  complete: boolean;
  resources: number | null; resourcesWithAward: number | null; resourceHours: number | null; resourceHoursEnergy: number | null;
  mw: number | null;
  /** day-ahead awards, USD per MW of the fleet: energy net of charging, the ancillary services together, and their sum */
  energy: number; ancillary: number; total: number;
  products: Record<string, number | null>;
  model: Model | null;
};

export type Year = {
  y: string;
  /** every month held, partial ones with the days they hold */
  months: number; daysHeld: number; daysInMonths: number;
  energy: number; ancillary: number; total: number;
  /** the complete months, and over them the awards and the model's figure for the same months (USD per MW) */
  completeMonths: string[]; awardsComplete: number | null; modelComplete: number | null;
  /** why no model figure stands beside the year, when none does */
  noModel: string | null;
};

const num = (v: number | string | null | undefined): number | null => {
  if (v === null || v === undefined || v === "") return null;
  const n = typeof v === "number" ? v : Number(v);
  return Number.isFinite(n) ? n : null;
};

/** The months of the table, oldest first, each with the model's figure for the same month where the model holds one.
 * A month without its days or without its three per-MW sums is not a month the page can show, and is left out. */
export function monthsOf(rows: Row[], model: Row[] = []): Month[] {
  const by = new Map<string, Map<string, number>>();
  for (const r of rows) {
    const v = num(r.value);
    if (v === null) continue;
    const m = r.ts_utc.slice(0, 7);
    if (!by.has(m)) by.set(m, new Map());
    by.get(m)!.set(r.variable, v);
  }
  const mod = new Map<string, Map<string, number>>();
  for (const r of model) {
    const v = num(r.value);
    if (v === null || !r.variable.startsWith(MODEL_PREFIX)) continue;
    const m = r.ts_utc.slice(0, 7);
    if (!mod.has(m)) mod.set(m, new Map());
    mod.get(m)!.set(r.variable.slice(MODEL_PREFIX.length), v);
  }
  const out: Month[] = [];
  for (const m of [...by.keys()].sort()) {
    const g = by.get(m)!;
    const get = (k: string) => (g.has(k) ? g.get(k)! : null);
    const daysHeld = get("days_held"), daysInMonth = get("days_in_month");
    const energy = get("revenue_energy_usd_per_mw"), ancillary = get("revenue_ancillary_usd_per_mw"), total = get("revenue_total_usd_per_mw");
    if (daysHeld === null || daysInMonth === null || energy === null || ancillary === null || total === null) continue;
    const x = mod.get(m);
    const mt = x?.get("revenue_total_usd_per_mw");
    const model: Model | null = x && mt !== undefined
      ? { total: mt, energy: x.get("revenue_energy_usd_per_mw") ?? null, ancillary: x.get("revenue_ancillary_usd_per_mw") ?? null,
          whole: x.get("days_held") !== undefined && x.get("days_held") === x.get("days_in_month") }
      : null;
    out.push({
      m, daysHeld, daysMissing: get("days_missing"), daysInMonth, complete: daysHeld === daysInMonth,
      resources: get("resources"), resourcesWithAward: get("resources_with_award"), resourceHours: get("resource_hours"), resourceHoursEnergy: get("resource_hours_energy_award"),
      mw: get("mw"), energy, ancillary, total,
      products: Object.fromEntries(PRODUCTS.map((p) => [p.key, get(`revenue_${p.key}_usd_per_mw`)])),
      model,
    });
  }
  return out;
}

/** By calendar year: the sum of the months' per-MW figures over every day held; and, over the complete months only,
 * the awards beside the model's figure for the same months. A partial month is never scaled to a whole one. */
export function years(ms: Month[]): Year[] {
  const out: Year[] = [];
  for (const y of [...new Set(ms.map((r) => r.m.slice(0, 4)))].sort()) {
    const all = ms.filter((r) => r.m.startsWith(y));
    const full = all.filter((r) => r.complete);
    const sum = (rs: Month[], f: (r: Month) => number) => rs.reduce((a, r) => a + f(r), 0);
    const lacking = full.filter((r) => !r.model || !r.model.whole).map((r) => r.m);
    const noModel = !full.length ? "no month of the year is held whole"
      : lacking.length ? `the model does not hold every day of ${lacking.join(", ")}` : null;
    out.push({
      y, months: all.length, daysHeld: sum(all, (r) => r.daysHeld), daysInMonths: sum(all, (r) => r.daysInMonth),
      energy: sum(all, (r) => r.energy), ancillary: sum(all, (r) => r.ancillary), total: sum(all, (r) => r.total),
      completeMonths: full.map((r) => r.m),
      awardsComplete: full.length ? sum(full, (r) => r.total) : null,
      modelComplete: noModel ? null : sum(full, (r) => r.model!.total),
      noModel,
    });
  }
  return out;
}

/** The newest month held whole, or null. */
export function newestComplete(ms: Month[]): Month | null {
  const full = ms.filter((r) => r.complete);
  return full.length ? full[full.length - 1] : null;
}

/** The share of resource-hours that hold a day-ahead energy award, over every month that states both counts; null
 * when none does. */
export function energyAwardShare(ms: Month[]): { hours: number; withAward: number; share: number } | null {
  const rs = ms.filter((r) => r.resourceHours !== null && r.resourceHoursEnergy !== null && r.resourceHours > 0);
  if (!rs.length) return null;
  const hours = rs.reduce((a, r) => a + r.resourceHours!, 0), withAward = rs.reduce((a, r) => a + r.resourceHoursEnergy!, 0);
  return { hours, withAward, share: withAward / hours };
}

/** USD per MW as USD per kW. */
export const perKw = (usdPerMw: number): number => usdPerMw / 1000;
/** USD per kW as the page writes it: two decimals. */
export const kw = (usdPerMw: number): string => perKw(usdPerMw).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
export const whole = (v: number): string => Math.round(v).toLocaleString("en-US");
export const monthName = (m: string): string => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
export const shortMonth = (m: string): string => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "short", year: "numeric", timeZone: "UTC" });

/** The months of a list in words: "January to July 2026" for a run of one year, else each named. */
export function span(ms: string[]): string {
  if (!ms.length) return "";
  if (ms.length === 1) return monthName(ms[0]);
  const run = ms.every((m, i) => i === 0 || (Number(m.slice(0, 4)) * 12 + Number(m.slice(5, 7))) - (Number(ms[i - 1].slice(0, 4)) * 12 + Number(ms[i - 1].slice(5, 7))) === 1);
  if (!run) return ms.map(shortMonth).join(", ");
  const first = monthName(ms[0]), last = monthName(ms[ms.length - 1]);
  return ms[0].slice(0, 4) === ms[ms.length - 1].slice(0, 4) ? `${first.split(" ")[0]} to ${last}` : `${first} to ${last}`;
}

/** The page's one sentence, from the newest month held whole; null when no month is whole. */
export function summary(ms: Month[]): string | null {
  const r = newestComplete(ms);
  if (!r) return null;
  const fleet = r.resources !== null && r.mw !== null ? `${whole(r.resources)} storage resources with ${whole(r.mw)} MW between them` : "the storage fleet";
  return `In ${monthName(r.m)}, ERCOT's disclosure lists ${fleet}; their day-ahead awards came to USD ${kw(r.total)} per kW for the month, `
    + `${kw(r.energy)} from energy net of charging and ${kw(r.ancillary)} from ancillary services.`;
}
