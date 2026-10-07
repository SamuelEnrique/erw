// Energy Research Warehouse (ERW) site, session 144: the curtailment page (/curtailment), the pure part: what the page
// chooses from its address, the address of each choice, and the little arithmetic the face does over the site's files
// (a year's share from its months, the order of the schematic's tiles). No imports: node runs this file as it is
// (scripts/check-curtailment.mjs). One tool, one page, one address: /curtailment/v2 redirects here (next.config.ts).
// Nothing here fills, scales or invents a figure: what a file does not hold comes back null.

export type GridId = "caiso" | "spp" | "ercot" | "isone" | "nyiso";
export type GridRow = {
  id: string; name: string; open: boolean; words?: string;
  /** the grid's entity and daily table in the curtailment tables, where the ERW holds one */
  entity?: string; daily?: string;
  /** [variable, label, CSS color] stacked in the daily and monthly charts */
  parts?: [string, string, string][];
};
const SOLAR = "var(--color-fuel-solar)", WIND = "var(--color-fuel-wind)";
export const MONTHLY = "iso_curtailment_monthly";
/** Every grid the page names, in the order of the chooser. A grid that is not open is named with its words, never a number. */
export const GRIDS: GridRow[] = [
  { id: "caiso", name: "CAISO", open: true, entity: "caiso:ISO", daily: "caiso_curtailment_daily", parts: [["curtailed_solar_mwh", "Solar curtailed", SOLAR], ["curtailed_wind_mwh", "Wind curtailed", WIND]] },
  { id: "spp", name: "SPP", open: true, entity: "spp:SPP", daily: "spp_curtailment_daily", parts: [["curtailed_wind_mwh", "Wind curtailed", WIND], ["curtailed_solar_mwh", "Solar curtailed", SOLAR]] },
  { id: "ercot", name: "ERCOT", open: true, entity: "ercot:system", daily: "ercot_wind_solar_hsl_daily", parts: [["solar_below_hsl_mwh", "Solar below the limit", SOLAR], ["wind_below_hsl_mwh", "Wind below the limit", WIND]] },
  { id: "isone", name: "ISO-NE", open: true },
  { id: "nyiso", name: "NYISO", open: true },
  { id: "miso", name: "MISO", open: false, words: "paused while terms are reviewed" },
  { id: "pjm", name: "PJM", open: false, words: "licensed source needed" },
];
export const DURATIONS = [2, 4, 8] as const;
export const DEFAULT_GRID = "caiso";
export const gridOf = (id: string): GridRow => GRIDS.find((g) => g.id === id) ?? GRIDS[0];

export type Choice = { grid: string; period: string | null; place: string | null; win: "month" | "year" | null; dur: 2 | 4 | 8 };
/** What the address asks for, as far as it can be read without the files: a grid that is open (else the default), a
 * battery of 2, 4 or 8 hours (else 4), and the period, place and window as typed (the page checks them against its files). */
export function choiceOf(q: Record<string, string | undefined>): Choice {
  const g = GRIDS.find((x) => x.id === q.grid && x.open)?.id ?? DEFAULT_GRID;
  const d = Number(q.dur);
  return { grid: g, period: q.period ?? null, place: q.place ?? null, win: q.win === "month" || q.win === "year" ? q.win : null, dur: d === 2 || d === 8 ? d : 4 };
}
/** The address of a choice: the page's one address with what differs from the default, and a section's anchor. */
export function link(c: Partial<Choice>, hash?: string): string {
  const p: string[] = [];
  if (c.grid && c.grid !== DEFAULT_GRID) p.push(`grid=${c.grid}`);
  if (c.period) p.push(`period=${c.period}`);
  if (c.place) p.push(`place=${encodeURIComponent(c.place)}`);
  if (c.win) p.push(`win=${c.win}`);
  if (c.dur && c.dur !== 4) p.push(`dur=${c.dur}`);
  return `/curtailment${p.length ? `?${p.join("&")}` : ""}${hash ? `#${hash}` : ""}`;
}

// ---- shares (data/curtailment/shares.json) -----------------------------------------------------------------------

export type ShareMonth = { share_pct: number; curtailed_mwh: number; output_mwh: number; hours_held: number; hours_in_month: number; days_held: number; days_in_month: number; basis: string };
export type ShareGrid = { entity: string; months_with_share: number; months: Record<string, ShareMonth>; missing: Record<string, string>; by_basis: Record<string, number>; not_covered?: Record<string, string> };
export type SharesFile = { built: string; near_hours: number; table: string; definition: string; definitions: Record<string, string>; basis_words: Record<string, string>; grids: Record<string, ShareGrid> };

/** A year's share from its months' own figures: curtailed over curtailed plus output, over the months of the year that
 * hold a share (the same definition as a month, never another denominator). Null when the year holds no such month. */
export function yearShare(g: ShareGrid, year: string): { share: number; curtailed: number; output: number; months: number } | null {
  const ms = Object.entries(g.months).filter(([m]) => m.startsWith(`${year}-`)).map(([, r]) => r);
  const c = ms.reduce((a, r) => a + r.curtailed_mwh, 0), o = ms.reduce((a, r) => a + r.output_mwh, 0);
  return ms.length && c + o > 0 ? { share: (100 * c) / (c + o), curtailed: c, output: o, months: ms.length } : null;
}
/** The share of a period, a month ("2026-04") or a year ("2026"), with how many months it rests on. */
export function periodShare(g: ShareGrid, period: string): { share: number; curtailed: number; months: number } | null {
  if (period.length === 7) { const r = g.months[period]; return r ? { share: r.share_pct, curtailed: r.curtailed_mwh, months: 1 } : null; }
  const y = yearShare(g, period);
  return y ? { share: y.share, curtailed: y.curtailed, months: y.months } : null;
}
/** The newest month with a share, and the month with the highest. */
export function shareMarks(g: ShareGrid): { last: string; highest: string } | null {
  const ms = Object.keys(g.months).sort();
  if (!ms.length) return null;
  return { last: ms[ms.length - 1], highest: ms.reduce((a, m) => (g.months[m].share_pct > g.months[a].share_pct ? m : a), ms[0]) };
}
/** Why a month has no share: the file's own reason, or that the month is not in the file at all. */
export const shareReason = (g: ShareGrid, month: string): string => g.missing[month] ?? "the month is not in the file of shares yet: it is written when curtailment and output are both held for 95 percent of its hours";

// ---- names and numbers as the page writes them -------------------------------------------------------------------

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
export const monthName = (m: string): string => `${MONTHS[Number(m.slice(5, 7)) - 1]} ${m.slice(0, 4)}`;
export const dayName = (d: string): string => `${Number(d.slice(8, 10))} ${MONTHS[Number(d.slice(5, 7)) - 1]} ${d.slice(0, 4)}`;
export const whole = (v: number): string => Math.round(v).toLocaleString("en-US");
export const two = (v: number): string => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
/** US dollars in words of scale, with the sign written: "-41.2 million", "24.9 million", "812,400". */
export function usd(v: number): string {
  const a = Math.abs(v), s = v < 0 ? "-" : "";
  if (a >= 1e9) return `${s}${(a / 1e9).toFixed(2)} billion`;
  if (a >= 1e6) return `${s}${(a / 1e6).toFixed(1)} million`;
  return `${s}${Math.round(a).toLocaleString("en-US")}`;
}
/** A place's name as a reader says it: the operator's own id without its wrapping (".Z.MAINE" is "MAINE", "TH_SP15_GEN-APND" is "SP15"). */
export function placeName(id: string): string {
  return id.replace(/^TH_/, "").replace(/_GEN-APND$/, "").replace(/^\.[ZH]\./, "").replace(/^HB_/, "HB ").replace(/^LZ_/, "LZ ").replace(/_HUB$/, "").replace(/_/g, " ");
}
/** The market a count rests on, in words. */
export const basisName = (b: string): string => (b === "rt" ? "real time" : "day-ahead");
