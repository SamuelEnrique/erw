import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { Num } from "@/components/Num";
import type { SeriesRow } from "@/lib/data";
import { count, shown } from "@/lib/format";
import { DAILY, EMERGENCIES, GEHR, daysByYear, dailyNotices, dailyVar, gridNotices, typeName } from "@/lib/reliability";
import { attempt } from "@/lib/supabase";
import { CAISO_HOLDS, wholeRead, wholeSeriesRead } from "@/lib/gridReads";  // session 1181; session 1411: wholeSeriesRead, the daily peaks' empty answer is a failed read
import { Missing } from "@/components/mix/Now";  // session 1181

// Session 58: California reliability v1, /grid/caiso's "Reliability" section. Every Flex Alert and emergency CAISO lists
// since 1998 (caiso_grid_emergencies), and how tight its evenings were day by day since 2018 (caiso_reliability_daily: peak
// demand, the evening ramp, batteries' share of the evening peak, the day's notices). Every number carries a check key:
// awe|days|<type>|<year> for the timeline's day counts, series keys for the daily figures. docs/methods/california_reliability.md.

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

function Row({ p, x, f = {} }: { p: SeriesRow; x: Days; f?: Unread }) {
  const d = dayOf(p), m = x.M.get(d) ?? [];
  if (f.R || f.S || f.B || f.M) return <RowUnread p={p} x={x} f={f} />;  // session 1411
  return (
    <tr className="border-b border-rule">
      <td className="py-1 pr-3 font-mono">{d}</td>
      <td className="py-1 pr-3 text-right tabular-nums"><V r={p} /></td>
      <td className="py-1 pr-3 text-right tabular-nums"><V r={x.R.get(d)} /></td>
      <td className="py-1 pr-3 text-right tabular-nums">{x.S.get(d) ? <><V r={x.S.get(d)} />% (<V r={x.B.get(d)} /> MW)</> : <span className="text-muted">not held</span>}</td>
      <td className="py-1 pr-3 text-xs">{m.length ? m.map((t) => SHORT[t] ?? typeName(t)).join(", ") : ""}</td>
    </tr>
  );
}

/** Session 1411: a day's row when a daily read other than the peak failed: each cell of a failed read says "could not be
 *  read" and draws no figure; the cells of the reads that succeeded are drawn as Row draws them. */
function RowUnread({ p, x, f }: { p: SeriesRow; x: Days; f: Unread }) {
  const d = dayOf(p), m = x.M.get(d) ?? [];
  const share = f.S ? unread("battery_share_pct", f.S)
    : x.S.get(d) ? <><V r={x.S.get(d)} />% ({f.B ? unread("battery_mw_evening_peak", f.B) : <><V r={x.B.get(d)} /> MW</>})</> : <span className="text-muted">not held</span>;
  return (
    <tr className="border-b border-rule" data-reliability-daily-unread="row">
      <td className="py-1 pr-3 font-mono">{d}</td>
      <td className="py-1 pr-3 text-right tabular-nums"><V r={p} /></td>
      <td className="py-1 pr-3 text-right tabular-nums">{f.R ? unread("evening_ramp_mw", f.R) : <V r={x.R.get(d)} />}</td>
      <td className="py-1 pr-3 text-right tabular-nums">{share}</td>
      <td className="py-1 pr-3 text-xs">{f.M ? unread("notices_*", f.M) : m.length ? m.map((t) => SHORT[t] ?? typeName(t)).join(", ") : ""}</td>
    </tr>
  );
}

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

  return (
    <div>
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

      <h3 className="mb-1 text-base">Every notice since 1998: days per year</h3>
      {ns.ok ? (
        <div className="mb-2 overflow-x-auto">
          <table className="text-sm">
            <thead><tr className="border-b border-ink text-xs text-muted"><th className="py-1 pr-3 text-left">Year</th>{COLS.map((c) => <th key={c} className="px-1 py-1 text-right">{SHORT[c]}</th>)}</tr></thead>
            <tbody>
              {years.map((y) => (
                <tr key={y} className="border-b border-rule">
                  <td className="py-0.5 pr-3 font-mono">{y}</td>
                  {COLS.map((c) => {
                    const n = byYear.get(y)?.get(c);
                    return <td key={c} className="px-1 py-0.5 text-right tabular-nums">{n ? <Num check={`awe|days|${c}|${y}`} raw={n}>{count(n)}</Num> : <span className="text-rule">.</span>}</td>;
                  })}
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
        differ, and why, are in <Link href="/data/methods/california_reliability">the method</Link>.
      </p>

      <h3 className="mb-1 text-base">The latest notices</h3>
      <ul className="mb-4 max-w-3xl text-sm">
        {recent.map((n) => (
          <li key={n.event_id}><span className="font-mono">{n.event_date.slice(0, 10)}</span>: {typeName(n.event_type)}{n.extra?.x_region ? `, ${n.extra.x_region}` : ""}{n.extra?.x_time_frame ? ` (${n.extra.x_time_frame})` : ""}</li>
        ))}
      </ul>

      <h3 className="mb-1 text-base">How tight was it: the twelve highest peaks since 2018</h3>
      <p className="mb-2 max-w-3xl text-sm">
        Each day&apos;s highest hour of demand served, the evening ramp (the rise from the 12:00 to 15:00 mean to the 17:00 to 21:00 peak), and, since
        2025-08-24, what CAISO&apos;s batteries delivered in the evening&apos;s peak hour and their share of that hour&apos;s demand.
      </p>
      {/* session 1411: the peak's read failed: the two tables say so, never an empty table */}
      {!peak.ok ? <p className="mb-4 text-sm text-muted" data-reliability-daily-unread="peaks">The daily peaks {unread("peak_demand_mw", peak.reason)}.</p> : null}
      {peak.ok ? <div className="mb-4 overflow-x-auto"><table className="w-full text-sm"><Head /><tbody>{tight.map((p) => <Row key={p.ts_utc} p={p} x={x} f={f} />)}</tbody></table></div> : null}
      <h3 className="mb-1 text-base">The latest fourteen days held</h3>
      {!peak.ok ? <p className="mb-2 text-sm text-muted" data-reliability-daily-unread="latest">The latest days {unread("peak_demand_mw", peak.reason)}.</p> : null}
      {peak.ok ? <div className="mb-2 overflow-x-auto"><table className="w-full text-sm"><Head /><tbody>{latest.map((p) => <Row key={p.ts_utc} p={p} x={x} f={f} />)}</tbody></table></div> : null}
      <p className="mb-2 max-w-3xl text-xs text-muted">
        Not here yet: the day&apos;s available supply (CAISO&apos;s Today&apos;s Outlook &quot;available resources&quot; is not in the warehouse), so peak demand is not set against it;
        and batteries before 2025-08-24. Demand is EIA-930&apos;s for CAISO&apos;s balancing authority, hourly, Pacific days. A September 2022 heat wave set the
        highest peak held: <Link href="/events/caiso-heat-2022">the event page</Link>.
      </p>
      <Cite tables={[EMERGENCIES, DAILY]} note={`California ISO, Grid Emergencies History Report (${GEHR}); EIA-930; CAISO Today's Outlook batteries`} />
    </div>
  );
}
