import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { Num } from "@/components/Num";
import type { SeriesRow } from "@/lib/data";
import { count, shown } from "@/lib/format";
import { DAILY, EMERGENCIES, GEHR, daysByYear, dailyNotices, dailyVar, gridNotices, typeName } from "@/lib/reliability";
import { attempt } from "@/lib/supabase";
import { CAISO_HOLDS, wholeRead, wholeSeriesRead } from "@/lib/gridReads";  // session 1181; session 1411: wholeSeriesRead, the daily peaks' empty answer is a failed read
import { Missing } from "@/components/mix/Now";  // session 1181
import type { ReactNode } from "react";
import { PanelFile, type FileCell } from "@/components/grid/PanelFile";  // session 1420: the three tables, to download
import { gridHref } from "@/lib/gridtool";
// session 1421: each table's anchor and the sections of the note that define them (lib/gridAnchors.ts, as session 1184)
import { METHOD_RELIABILITY_DAILY, METHOD_RELIABILITY_NOTICES, OLDER_ANCHOR } from "@/lib/gridAnchors";

// Session 58: California reliability v1, /grid/caiso's "Reliability" section. Every Flex Alert and emergency CAISO lists
// since 1998 (caiso_grid_emergencies), and how tight its evenings were day by day since 2018 (caiso_reliability_daily: peak
// demand, the evening ramp, batteries' share of the evening peak, the day's notices). Every number carries a check key:
// awe|days|<type>|<year> for the timeline's day counts, series keys for the daily figures. docs/methods/california_reliability.md.
// Session 1420 (chain 111): a named panel (grid_reliability_caiso) whose three tables (the days per year, the twelve highest
// peaks, the latest fourteen days) each offer their figures as a file (components/grid/PanelFile.tsx, session 1182): the
// same figure nodes the rows draw (dayParts), the batteries' share and MW, one cell on the page, two columns of the file.

const COLS = ["flex_alert", "rmo", "eea_watch", "eea1", "eea2", "eea3", "alert", "warning", "stage1", "stage2", "stage3", "transmission_emergency"] as const;
const SHORT: Record<string, string> = {
  flex_alert: "Flex Alert", rmo: "RMO", eea_watch: "EEA Watch", eea1: "EEA 1", eea2: "EEA 2", eea3: "EEA 3", alert: "Alert", warning: "Warning",
  stage1: "Stage 1", stage2: "Stage 2", stage3: "Stage 3", transmission_emergency: "Transmission",
};
const dayOf = (r: SeriesRow) => r.ts_utc.slice(0, 10);
const key = (r: SeriesRow) => `series|${DAILY}|${r.entity}|${r.variable}|${r.ts_utc}`;
type Days = { R: Map<string, SeriesRow>; S: Map<string, SeriesRow>; B: Map<string, SeriesRow>; M: Map<string, string[]> };
// session 1411: the daily reads that failed (R the ramp, S the share, B the batteries' MW, M the notices), each with its reason
type Unread = Partial<Record<"R" | "S" | "B" | "M", string>>;
/** Session 1411: a figure of caiso_reliability_daily whose read failed, in the tool's one look (session 1181). */
const unread = (what: string, reason: string) => <Missing words="could not be read" why={`${DAILY} (${what}) could not be read just now: ${reason}`} />;

/** Session 1420: a day's figures and words, as its row draws them (Row, RowUnread) and as its file writes them: a cell of
 *  a failed read says "could not be read" (session 1411); the batteries' MW is drawn only beside their share. */
function dayParts(p: SeriesRow, x: Days, f: Unread = {}) {
  const d = dayOf(p), m = x.M.get(d) ?? [], s = x.S.get(d);
  const share: ReactNode = f.S ? unread("battery_share_pct", f.S) : s ? <V r={s} /> : null;
  const mw: ReactNode = f.S || !s ? null : f.B ? unread("battery_mw_evening_peak", f.B) : <V r={x.B.get(d)} />;
  const notices: ReactNode = f.M ? unread("notices_*", f.M) : m.length ? m.map((t) => SHORT[t] ?? typeName(t)).join(", ") : "";
  return { d, peak: <V r={p} />, ramp: f.R ? unread("evening_ramp_mw", f.R) : <V r={x.R.get(d)} />, share, mw, notices };
}

function Row({ p, x, f = {} }: { p: SeriesRow; x: Days; f?: Unread }) {
  if (f.R || f.S || f.B || f.M) return <RowUnread p={p} x={x} f={f} />;  // session 1411
  const c = dayParts(p, x);
  return (
    <tr className="border-b border-rule">
      <td className="py-1 pr-3 font-mono">{c.d}</td>
      <td className="py-1 pr-3 text-right tabular-nums">{c.peak}</td>
      <td className="py-1 pr-3 text-right tabular-nums">{c.ramp}</td>
      <td className="py-1 pr-3 text-right tabular-nums">{c.share ? <>{c.share}% ({c.mw} MW)</> : <span className="text-muted">not held</span>}</td>
      <td className="py-1 pr-3 text-xs">{c.notices}</td>
    </tr>
  );
}

/** Session 1411: a day's row when a daily read other than the peak failed: each cell of a failed read says "could not be
 *  read" and draws no figure; the cells of the reads that succeeded are drawn as Row draws them. */
function RowUnread({ p, x, f }: { p: SeriesRow; x: Days; f: Unread }) {
  const c = dayParts(p, x, f);   // session 1420: the cells as dayParts gives them, drawn as session 1411 drew them
  const share = f.S ? c.share
    : c.share ? <>{c.share}% ({f.B ? c.mw : <>{c.mw} MW</>})</> : <span className="text-muted">not held</span>;
  return (
    <tr className="border-b border-rule" data-reliability-daily-unread="row">
      <td className="py-1 pr-3 font-mono">{c.d}</td>
      <td className="py-1 pr-3 text-right tabular-nums">{c.peak}</td>
      <td className="py-1 pr-3 text-right tabular-nums">{c.ramp}</td>
      <td className="py-1 pr-3 text-right tabular-nums">{share}</td>
      <td className="py-1 pr-3 text-xs">{c.notices}</td>
    </tr>
  );
}

/** Session 1420: the columns of the two daily tables' files (the page's five, the batteries' cell in two). */
const DAY_COLUMNS = ["Day (Pacific)", "Peak demand, MW", "Evening ramp, MW", "Batteries' share of the evening peak hour's demand, percent", "Batteries at the evening peak, MW", "CAISO's notices that day"];

function Head() {
  return (
    <thead>
      <tr className="border-b border-ink text-left text-xs text-muted">
        <th className="py-1 pr-3">Day (Pacific)</th><th className="py-1 pr-3 text-right">Peak demand, MW</th>
        <th className="py-1 pr-3 text-right">Evening ramp, MW</th><th className="py-1 pr-3 text-right">Batteries at the evening peak</th>
        <th className="py-1 pr-3">CAISO&apos;s notices that day</th>
      </tr>
    </thead>
  );
}

function V({ r, unit }: { r?: SeriesRow; unit?: string }) {
  return r ? <><Num check={key(r)} raw={r.value}>{shown(r.value)}</Num>{unit ? ` ${unit}` : ""}</> : <span className="text-muted">not held</span>;
}

export async function Reliability() {
  const [ns, peak, ramp, share, bat, marks] = await Promise.all([
    wholeRead(EMERGENCIES, CAISO_HOLDS, attempt(() => gridNotices())).then((r) => r!), wholeSeriesRead(DAILY, "every Pacific day since 2018", attempt(() => dailyVar("peak_demand_mw"))), attempt(() => dailyVar("evening_ramp_mw")),
    attempt(() => dailyVar("battery_share_pct")), attempt(() => dailyVar("battery_mw_evening_peak")), attempt(() => dailyNotices()),
  ]);
  const notices = ns.ok ? ns.data : [];
  const byYear = daysByYear(notices);
  const years = [...byYear.keys()].sort((a, b) => b - a);
  const idx = (x: { ok: boolean; data?: SeriesRow[] }) => new Map((x.ok ? x.data! : []).map((r) => [dayOf(r), r]));
  const x: Days = { R: idx(ramp as never), S: idx(share as never), B: idx(bat as never), M: new Map() };
  for (const r of marks.ok ? marks.data : []) x.M.set(dayOf(r), [...(x.M.get(dayOf(r)) ?? []), r.variable.replace(/^notices_/, "")]);
  // session 1411: the daily reads that failed, so a row says "could not be read" where it said "not held" or nothing
  const f: Unread = { ...(ramp.ok ? {} : { R: ramp.reason }), ...(share.ok ? {} : { S: share.reason }), ...(bat.ok ? {} : { B: bat.reason }), ...(marks.ok ? {} : { M: marks.reason }) };
  const peaks = peak.ok ? [...peak.data] : [];
  const tight = [...peaks].sort((a, b) => b.value - a.value || a.ts_utc.localeCompare(b.ts_utc)).slice(0, 12);
  const latest = peaks.slice(-14).reverse();
  const recent = notices.slice(-12).reverse();
  const lastNotice = notices.at(-1);
  // session 1420: the days per year, one row a year, drawn in the table and written in its file (a blank: no such day)
  const yearCells: (ReactNode | null)[][] = years.map((y) => COLS.map((c) => {
    const n = byYear.get(y)?.get(c);
    return n ? <Num check={`awe|days|${c}|${y}`} raw={n}>{count(n)}</Num> : null;
  }));
  const dayRow = (p: SeriesRow): FileCell[] => { const c = dayParts(p, x, f); return [c.d, c.peak, c.ramp, c.share ?? "not held", c.mw ?? (f.S ? "could not be read" : "not held"), c.notices]; };
  const page = gridHref("caiso", "mix");
  const dailyTables = [`${DAILY} (EIA-930's demand for CAISO's balancing authority, hourly, Pacific days; CAISO's Today's Outlook batteries since 2025-08-24; the day's notices from ${EMERGENCIES})`];
  const dailyFilter = "peak_demand_mw, evening_ramp_mw, battery_share_pct, battery_mw_evening_peak and notices_<type> (each figure's entity in its key)";

  return (
    <div data-grid-panel="grid_reliability_caiso">
      <p className="mb-3 max-w-3xl text-sm">
        When California&apos;s grid runs short, CAISO says so in public: a <strong>Flex Alert</strong> asks people to use less power in the evening; a{" "}
        <strong>Restricted Maintenance Operations</strong> notice tells plant and line owners to put off maintenance; an <strong>Energy Emergency Alert</strong>{" "}
        (EEA 1 to 3, called stage emergencies before May 2022) means supply may not cover demand plus reserves, and at EEA 3 rotating outages are near.
        The tightest hour is usually early evening: solar fades while air conditioners still run.
      </p>

      <p className="mb-3 max-w-3xl text-sm">
        <strong>Did the alerts cut demand?</strong> <Link href="/grid/caiso/alerts">The Flex Alert scorecard</Link> sets every alert day since 2018 against
        a weather-and-calendar model of demand, with intervals and a wholesale value.
      </p>

      <h3 id={OLDER_ANCHOR.reliabilityDays} className="mb-1 text-base">Every notice since 1998: days per year</h3>
      {ns.ok ? (
        <div className="mb-2 overflow-x-auto">
          <table className="text-sm">
            <thead><tr className="border-b border-ink text-xs text-muted"><th className="py-1 pr-3 text-left">Year</th>{COLS.map((c) => <th key={c} className="px-1 py-1 text-right">{SHORT[c]}</th>)}</tr></thead>
            <tbody>
              {years.map((y, i) => (
                <tr key={y} className="border-b border-rule">
                  <td className="py-0.5 pr-3 font-mono">{y}</td>
                  {COLS.map((c, j) => <td key={c} className="px-1 py-0.5 text-right tabular-nums">{yearCells[i][j] ?? <span className="text-rule">.</span>}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : <p className="text-sm text-muted">The notices could not be read: {ns.reason}</p>}
      <p className="mb-4 max-w-3xl text-xs text-muted">
        Days with at least one notice of each type, as CAISO counts them; a notice for one region counts as that day. Stage emergencies, Alerts and Warnings were
        CAISO&apos;s notices until April 2022; EEA Watch and EEA 1 to 3 since May 2022. {/* session 1181: a failed read is said, never "0 notices" */}{ns.ok ? <>The table holds{" "}
        {/* session 1166: the count and the newest day, keyed (awe|rows|any and awe|newest|any, lib/caisoAlerts.ts aweValue) */}
        {ns.ok ? <span title={`${EMERGENCIES}: every row (one a notice type, region and Pacific day)`} className="cursor-help border-b border-dotted border-muted"><Num check="awe|rows|any" raw={notices.length}>{count(notices.length)}</Num></span> : count(notices.length)} notices, the latest on{" "}
        {lastNotice ? <span title={`${EMERGENCIES}: the newest event_date of any notice`} className="cursor-help border-b border-dotted border-muted"><Num check="awe|newest|any" raw={lastNotice.event_date.slice(0, 10)}>{lastNotice.event_date.slice(0, 10)}</Num></span> : "no day"}.</>
        : <span data-reliability-unread="1">The table&apos;s notices <Missing words="could not be read" why={`${EMERGENCIES} could not be read just now: ${ns.reason}`} />.</span>} Our day counts match CAISO&apos;s own yearly summary in 214 of 232 year and type cells; the 18 that
        differ, and why, are in <Link href={METHOD_RELIABILITY_NOTICES}>the method</Link>.
      </p>
      {ns.ok && years.length ? (
        <PanelFile of={{ panel: "grid_reliability_caiso", part: "days_per_year", title: "the days per year with at least one notice of each type, as CAISO counts them, since 1998", page,
          tables: [`${EMERGENCIES} (California ISO, Grid Emergencies History Report, ${GEHR})`],
          filter: "every notice the table holds, by type; a notice for one region counts as that day",
          window: `Window: every Pacific day the table holds, 1998 to ${lastNotice ? lastNotice.event_date.slice(0, 10) : "its newest day"}`,
          notes: ["A blank cell: no day with a notice of that type that year (the page draws a dot)"],
          figures: [{ label: "Notices the table holds", value: { check: "awe|rows|any", raw: notices.length } },
            ...(lastNotice ? [{ label: "The latest notice's day", value: { check: "awe|newest|any", raw: lastNotice.event_date.slice(0, 10) } }] : [])] }}
          columns={["Year", ...COLS.map((c) => SHORT[c])]} rows={years.map((y, i) => [String(y), ...yearCells[i].map((c) => c ?? "")])} />
      ) : null}

      <h3 className="mb-1 text-base">The latest notices</h3>
      <ul className="mb-4 max-w-3xl text-sm">
        {recent.map((n) => (
          <li key={n.event_id}><span className="font-mono">{n.event_date.slice(0, 10)}</span>: {typeName(n.event_type)}{n.extra?.x_region ? `, ${n.extra.x_region}` : ""}{n.extra?.x_time_frame ? ` (${n.extra.x_time_frame})` : ""}</li>
        ))}
      </ul>

      <h3 id={OLDER_ANCHOR.reliabilityPeaks} className="mb-1 text-base">How tight was it: the twelve highest peaks since 2018</h3>
      <p className="mb-2 max-w-3xl text-sm">
        Each day&apos;s highest hour of demand served, the evening ramp (the rise from the 12:00 to 15:00 mean to the 17:00 to 21:00 peak), and, since
        2025-08-24, what CAISO&apos;s batteries delivered in the evening&apos;s peak hour and their share of that hour&apos;s demand.
      </p>
      {/* session 1411: the peak's read failed: the two tables say so, never an empty table */}
      {!peak.ok ? <p className="mb-4 text-sm text-muted" data-reliability-daily-unread="peaks">The daily peaks {unread("peak_demand_mw", peak.reason)}.</p> : null}
      {peak.ok ? <div className="mb-4 overflow-x-auto"><table className="w-full text-sm"><Head /><tbody>{tight.map((p) => <Row key={p.ts_utc} p={p} x={x} f={f} />)}</tbody></table></div> : null}
      {peak.ok && tight.length ? (
        <PanelFile of={{ panel: "grid_reliability_caiso", part: "highest_peaks", title: "the twelve highest daily peaks of demand since 2018, with the evening ramp, the batteries and the day's notices", page,
          tables: dailyTables, filter: dailyFilter, window: "Window: every Pacific day since 2018 the table holds: the twelve with the highest peak_demand_mw" }}
          columns={DAY_COLUMNS} rows={tight.map(dayRow)} />
      ) : null}
      <h3 id={OLDER_ANCHOR.reliabilityLatest} className="mb-1 text-base">The latest fourteen days held</h3>
      {!peak.ok ? <p className="mb-2 text-sm text-muted" data-reliability-daily-unread="latest">The latest days {unread("peak_demand_mw", peak.reason)}.</p> : null}
      {peak.ok ? <div className="mb-2 overflow-x-auto"><table className="w-full text-sm"><Head /><tbody>{latest.map((p) => <Row key={p.ts_utc} p={p} x={x} f={f} />)}</tbody></table></div> : null}
      {peak.ok && latest.length ? (
        <PanelFile of={{ panel: "grid_reliability_caiso", part: "latest_days", title: "the latest fourteen days held, with the evening ramp, the batteries and the day's notices", page,
          tables: dailyTables, filter: dailyFilter, window: `Window: the latest fourteen Pacific days the table holds, ${dayOf(latest.at(-1)!)} to ${dayOf(latest[0])}` }}
          columns={DAY_COLUMNS} rows={latest.map(dayRow)} />
      ) : null}
      {/* session 1421: the two daily tables' method, the section that defines their figures (drawn whether or not the read succeeded) */}
      <p className="mb-2 text-xs text-muted" data-grid-method="reliability-daily"><Link href={METHOD_RELIABILITY_DAILY}>Method: how tight was it, the daily figures</Link>.</p>
      <p className="mb-2 max-w-3xl text-xs text-muted">
        Not here yet: the day&apos;s available supply (CAISO&apos;s Today&apos;s Outlook &quot;available resources&quot; is not in the warehouse), so peak demand is not set against it;
        and batteries before 2025-08-24. Demand is EIA-930&apos;s for CAISO&apos;s balancing authority, hourly, Pacific days. A September 2022 heat wave set the
        highest peak held: <Link href="/events/caiso-heat-2022">the event page</Link>.
      </p>
      <Cite tables={[EMERGENCIES, DAILY]} note={`California ISO, Grid Emergencies History Report (${GEHR}); EIA-930; CAISO Today's Outlook batteries`} />
    </div>
  );
}
