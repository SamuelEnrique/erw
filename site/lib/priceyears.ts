// Energy Research Warehouse (ERW) site, session 352 (the chain of 20 October 2026, night): the price years of the three
// economics pages. The data machine's table price_years_by_window (warehouse/derived/price_years.py, session 357;
// docs/methods/price_years.md) holds each page's figure under every window of years held: a calendar year, the page's
// own last twelve months, the averages of the last three and seven full years, everything held, and everything with a
// stress event taken out. A page offers its windows in a "Price years" choice; the last twelve months stay the default,
// so no number moves until a reader chooses another window.
//
// The live set holds the table's series columns only (entity, variable, ts_utc, value, unit, freq), so a window is read
// from them: its id from the variable (<tool>_<configuration>_<window>), its first month from ts_utc, its length from
// freq (P<n>M, the calendar months from the first to the last, both included). A calendar year is whole when it spans
// January to December. Pure: the server reads the rows (lib/priceyearsread.ts), the pages draw them.

export type Tool = "battery" | "generator" | "datacenter";
export const DEFAULT_WINDOW = "last_12";

/** One window of one configuration at one price point: the page's figure under it. */
export type PriceYear = {
  id: string;            // year_2024, last_12, avg_3y, avg_7y, all, all_less_uri_2021, all_less_events
  kind: "year" | "last_12" | "avg_3y" | "avg_7y" | "all" | "all_less";
  from: string;          // YYYY-MM
  to: string;            // YYYY-MM
  months: number;        // the calendar months from the first to the last, both included
  whole: boolean;        // a calendar year with all twelve months; every other window is written only when whole
  value: number;         // USD/kW-year (battery, generator) or USD/MWh (datacenter)
  unit: string;
  // the row's key, for the page's check (series|price_years_by_window|<entity>|<variable>|<ts_utc>)
  entity: string; variable: string; ts: string;
};

export type Row = { entity: string; variable: string; ts_utc: string; value: number; unit: string; freq: string | null };

const plusMonths = (ym: string, k: number) => {
  const [y, m] = ym.split("-").map(Number);
  const d = new Date(Date.UTC(y, m - 1 + k, 1));
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
};

/** The windows of one configuration, from its rows: `prefix` is "<tool>_<configuration>_". */
export function windowsOf(rows: Row[], prefix: string): PriceYear[] {
  const out: PriceYear[] = [];
  for (const r of rows) {
    if (!r.variable.startsWith(prefix) || !Number.isFinite(r.value)) continue;
    const id = r.variable.slice(prefix.length);
    const kind = id.startsWith("year_") ? "year" : id.startsWith("all_less") ? "all_less" : (["last_12", "avg_3y", "avg_7y", "all"] as const).find((k) => k === id);
    const n = Number((r.freq ?? "").match(/^P(\d+)M$/)?.[1] ?? NaN);
    if (!kind || !Number.isFinite(n) || n < 1) continue;
    const from = r.ts_utc.slice(0, 7), to = plusMonths(from, n - 1);
    out.push({ id, kind, from, to, months: n, whole: kind !== "year" || (n === 12 && from.endsWith("-01")), value: r.value, unit: r.unit, entity: r.entity, variable: r.variable, ts: r.ts_utc });
  }
  const order = (w: PriceYear) => (w.kind === "last_12" ? "0" : w.kind === "year" ? `1${9999 - Number(w.id.slice(5))}` : w.kind === "avg_3y" ? "2" : w.kind === "avg_7y" ? "3" : w.kind === "all" ? "4" : `5${w.id}`);
  return out.sort((a, b) => order(a).localeCompare(order(b)));
}

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const monthWords = (ym: string) => `${MONTHS[Number(ym.slice(5, 7)) - 1]} ${ym.slice(0, 4)}`;
const eventWords = (id: string) => id === "events" ? "every stress event" : id.replace(/_/g, " ");

/** A window's name in the choice and in a sentence. */
export function windowWords(w: PriceYear): { label: string; sentence: string } {
  const span = `${monthWords(w.from)} to ${monthWords(w.to)}`;
  if (w.kind === "last_12") return { label: "The last twelve months (default)", sentence: `over the last twelve months (${span})` };
  if (w.kind === "year") return w.whole
    ? { label: `${w.id.slice(5)}`, sentence: `in ${w.id.slice(5)}` }
    : { label: `${w.id.slice(5)}, ${w.months} months held (their sum, not a full year)`, sentence: `in the ${w.months} months held of ${w.id.slice(5)} (${span}), their sum and not a full year` };
  if (w.kind === "avg_3y") return { label: "The last three full years, averaged", sentence: `on the average year of ${w.from.slice(0, 4)} to ${w.to.slice(0, 4)}` };
  if (w.kind === "avg_7y") return { label: "The last seven full years, averaged", sentence: `on the average year of ${w.from.slice(0, 4)} to ${w.to.slice(0, 4)}` };
  if (w.kind === "all") return { label: "Every month held", sentence: `on the average year of every month held (${span})` };
  const ev = eventWords(w.id.replace(/^all_less_/, ""));
  return { label: `Every month held, less ${ev}`, sentence: `on the average year of every month held (${span}), with ${ev} taken out` };
}

/** The window the address asks for, if the rows hold it; null at the default or when it is not held. */
export function chosen(ws: PriceYear[], id: string | null | undefined): PriceYear | null {
  if (!id || id === DEFAULT_WINDOW) return null;
  return ws.find((w) => w.id === id) ?? null;
}

/** The highest and the lowest whole calendar year held: what the same project earns, or the same load pays, in each. */
export function highLow(ws: PriceYear[]): { high: PriceYear; low: PriceYear } | null {
  const ys = ws.filter((w) => w.kind === "year" && w.whole);
  if (ys.length < 2) return null;
  const s = [...ys].sort((a, b) => a.value - b.value);
  return { low: s[0], high: s[s.length - 1] };
}

export const WINDOW_RE = /^(year_\d{4}|last_12|avg_3y|avg_7y|all|all_less_[a-z0-9_]+)$/;
