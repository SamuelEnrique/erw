// Energy Research Warehouse (ERW) site, session 7539 (chain 304, part C, the read of /prices as a fund analyst would
// read it: docs/reviews/prices-read-2026-11-16.md): the pure part of a hub's page (app/prices/[entity]/page.tsx) and of
// the first tab's words (app/prices/page.tsx). Nothing here reads the database; scripts/test-prices-read.mjs holds it.
import type { SeriesRow } from "./data";
import { utc } from "./format";

/** Session 7539 (the read, row 4): the step of a table's rows in minutes (PT15M, PT5M, PT1H), for the count of the
 * intervals the span from the first row to the last holds, and the UTC days of that span with no row at all. */
export function stepMinutes(freq: string | undefined): number | null {
  const m = /^PT(\d+)([MH])$/.exec(freq ?? "");
  return m ? Number(m[1]) * (m[2] === "H" ? 60 : 1) : null;
}
export function heldOf(rows: SeriesRow[], freq: string | undefined): { due: number; missingDays: string[] } | null {
  const step = stepMinutes(freq);
  if (!step || rows.length === 0) return null;
  const t0 = Date.parse(rows[0].ts_utc), t1 = Date.parse(rows.at(-1)!.ts_utc);
  const due = Math.round((t1 - t0) / (step * 60_000)) + 1;
  const have = new Set(rows.map((r) => new Date(r.ts_utc).toISOString().slice(0, 10)));
  const missingDays: string[] = [];
  for (let d = Date.UTC(new Date(t0).getUTCFullYear(), new Date(t0).getUTCMonth(), new Date(t0).getUTCDate()); d <= t1; d += 86_400_000) {
    const day = new Date(d).toISOString().slice(0, 10);
    if (!have.has(day)) missingDays.push(day);
  }
  return { due, missingDays };
}

/** Session 7539 (the read, row 5): real time less day-ahead over the hours both hold. A real-time hour is the mean of
 * its intervals and is taken only when every interval of the hour is held (4 at 15 minutes, 12 at 5, 1 hourly), so the
 * two sides are the same hours; the two means of the table above are over different hours and their difference is not
 * this figure. */
export function realLessDayAhead(rt: SeriesRow[], da: SeriesRow[], rtFreq: string | undefined) {
  const step = stepMinutes(rtFreq);
  if (!step || !rt.length || !da.length) return null;
  const per = Math.max(1, Math.round(60 / step));
  const hours = new Map<number, number[]>();
  for (const r of rt) {
    const h = Math.floor(Date.parse(r.ts_utc) / 3_600_000);
    (hours.get(h) ?? hours.set(h, []).get(h)!).push(r.value);
  }
  const out: { t: string; v: number }[] = [];
  for (const d of da) {
    const vs = hours.get(Math.floor(Date.parse(d.ts_utc) / 3_600_000));
    if (vs && vs.length === per) out.push({ t: d.ts_utc, v: vs.reduce((a, b) => a + b, 0) / per - d.value });
  }
  if (!out.length) return null;
  let lo = out[0], hi = out[0];
  for (const o of out) { if (o.v < lo.v) lo = o; if (o.v > hi.v) hi = o; }
  return { n: out.length, mean: out.reduce((a, o) => a + o.v, 0) / out.length, min: lo.v, max: hi.v, minAt: lo.t, maxAt: hi.t, first: out[0].t, last: out.at(-1)!.t };
}

/** Session 7539 (the read, row 6): a variable as a reader names it, the code on hover. */
export const VARIABLE_WORDS: Record<string, string> = {
  spp_rtm: "15-minute settlement point price",
  spp_dam: "hourly settlement point price",
  lmp_dam: "hourly locational price",
  lmp_rtm: "hourly locational price",
  lmp_rtm_5min: "5-minute locational price",
  lmp_rtm_15m_mean: "15-minute mean of the 5-minute locational prices",
};
export const variableWords = (v: string) => VARIABLE_WORDS[v] ?? v;

/** Session 7539 (the read, rows 2 and 5): an interval's start in UTC and in the grid's own clock, for a hover. */
const ZONE: Record<string, string> = { ERCOT: "America/Chicago", SPP: "America/Chicago", MISO: "America/Chicago", CAISO: "America/Los_Angeles", NYISO: "America/New_York", "ISO-NE": "America/New_York" };
/** Ruling alternative 3 of /prices (session 7723, branch wip/alt-prices-3; not a default on main): hub A less hub B over the
 *  hours both hold whole (an hour's mean of its intervals, taken only when every interval of the hour is held, as
 *  realLessDayAhead takes real time). Null when no hour is held by both. On main a hub page has no second hub. */
export function hubLessHub(a: SeriesRow[], b: SeriesRow[], freq: string | undefined) {
  const step = stepMinutes(freq);
  if (!step || !a.length || !b.length) return null;
  const per = Math.max(1, Math.round(60 / step));
  const hourly = (rows: SeriesRow[]) => {
    const m = new Map<number, number[]>();
    for (const r of rows) { const h = Math.floor(Date.parse(r.ts_utc) / 3_600_000); (m.get(h) ?? m.set(h, []).get(h)!).push(r.value); }
    return m;
  };
  const A = hourly(a), B = hourly(b);
  const out: { t: number; v: number }[] = [];
  for (const [h, va] of A) {
    const vb = B.get(h);
    if (va.length === per && vb && vb.length === per) out.push({ t: h, v: va.reduce((x, y) => x + y, 0) / per - vb.reduce((x, y) => x + y, 0) / per });
  }
  if (!out.length) return null;
  out.sort((x, y) => x.t - y.t);
  const vs = out.map((o) => o.v).sort((x, y) => x - y), n = vs.length;
  let lo = out[0], hi = out[0];
  for (const o of out) { if (o.v < lo.v) lo = o; if (o.v > hi.v) hi = o; }
  const iso = (t: number) => new Date(t * 3_600_000).toISOString().replace(/\.\d{3}Z$/, "Z");
  return { n, mean: vs.reduce((x, y) => x + y, 0) / n, median: n % 2 ? vs[(n - 1) / 2] : (vs[n / 2 - 1] + vs[n / 2]) / 2, min: lo.v, max: hi.v,
    minAt: iso(lo.t), maxAt: iso(hi.t), below: out.filter((o) => o.v < 0).length, first: iso(out[0].t), last: iso(out[out.length - 1].t) };
}

export function whenWords(ts: string, iso: string): string {
  const z = ZONE[iso];
  const local = z ? new Date(ts).toLocaleString("en-US", { timeZone: z, year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hour12: false, timeZoneName: "short" }) : "";
  return `${utc(ts)}${local ? ` (${local})` : ""}`;
}
