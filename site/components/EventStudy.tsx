// Session 47: "What the estimates say", the event study block of each /events page. The estimates are computed here, at
// build time, from event_window_daily (Supabase) by lib/eventstudy.ts, the twin of warehouse/derived/event_study.py,
// whose table event_study_estimates holds the same numbers (docs/methods/event_study.md). Every number carries a check
// key (es|<event>|<entity>|<variable>|<term>|<field>) that scripts/check-values.mjs recomputes.
import Link from "next/link";
import { Cite } from "@/components/Cite";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { series } from "@/lib/data";
import { studyOf, type Study } from "@/lib/eventstudy";
import { shown } from "@/lib/format";
import { attempt } from "@/lib/supabase";

const T = "event_window_daily";
export const GRID_LABEL: Record<string, string> = {
  "eia930:ERCO": "ERCOT", "eia930:CISO": "CAISO", "eia930:ISNE": "ISO-NE", "eia930:MISO": "MISO", "eia930:NYIS": "NYISO",
  "eia930:PJM": "PJM", "eia930:SWPP": "SPP", "eia930:US48": "the Lower 48", "ercot:HB_HUBAVG": "ERCOT's hub average",
};
const OUTCOME: Record<string, { what: string; unit: string }> = {
  demand_mwh: { what: "daily demand served", unit: "MWh a day" },
  rt_mean: { what: "daily mean real-time price", unit: "USD/MWh" },
};

type Row = { entity: string; variable: string; s: Study };

function E({ ev, r, term, field, v }: { ev: string; r: Row; term: string; field: string; v: number }) {
  return <Num check={`es|${ev}|${r.entity}|${r.variable}|${term}|${field}`} raw={v}>{shown(v)}</Num>;
}

/** The coefficient plot: each event day's effect and its 95 percent interval, a zero line. */
function Plot({ r, label }: { r: Row; label: string }) {
  const d = r.s.days;
  const lo = Math.min(0, ...d.map((x) => x.lo)), hi = Math.max(0, ...d.map((x) => x.hi));
  const W = 720, H = 240, L = 64, R = 12, top = 12, bot = 28;
  const x = (i: number) => L + ((i + 0.5) / d.length) * (W - L - R);
  const y = (v: number) => top + ((hi - v) / (hi - lo || 1)) * (H - top - bot);
  const ticks = [lo, (lo + hi) / 2, hi];
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img"
      aria-label={`${label}: the estimated effect of each event day, with its 95 percent interval; zero is no effect`}>
      {ticks.map((t, i) => (
        <g key={i}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={1} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize={11} fill="var(--color-muted)">{Math.round(t).toLocaleString("en-US")}</text>
        </g>
      ))}
      <line x1={L} x2={W - R} y1={y(0)} y2={y(0)} stroke="var(--color-ink)" strokeWidth={1} />
      {d.map((p, i) => (
        <g key={p.day}>
          <title>{`${p.day}: ${shown(p.estimate)} (${shown(p.lo)} to ${shown(p.hi)})`}</title>
          <line x1={x(i)} x2={x(i)} y1={y(p.lo)} y2={y(p.hi)} stroke="var(--color-muted)" strokeWidth={1.5} />
          <circle cx={x(i)} cy={y(p.estimate)} r={3.5} fill={p.lo > 0 || p.hi < 0 ? "var(--color-accent)" : "var(--color-panel)"} stroke="var(--color-accent)" strokeWidth={1.5} />
        </g>
      ))}
      {[0, Math.floor((d.length - 1) / 2), d.length - 1].map((i) => (
        <text key={i} x={x(i)} y={H - 8} textAnchor="middle" fontSize={11} fill="var(--color-muted)">{d[i].day}</text>
      ))}
    </svg>
  );
}

export async function EventStudy({ event, grids, primary, price }: { event: string; grids: string[]; primary: string; price?: boolean }) {
  const want = [...grids.map((g) => ({ entity: g, variable: "demand_mwh" })), ...(price ? [{ entity: "ercot:HB_HUBAVG", variable: "rt_mean" }] : [])];
  const got = await attempt(() => Promise.all(want.map(async (w) => {
    const rows = await series(T, { event, entity: w.entity, variable: w.variable });
    return { ...w, s: studyOf(event, rows) } as Row;
  })));
  if (!got.ok) return <Section title="What the estimates say"><NoData what="the event study" reason={got.reason} /></Section>;
  const rows = got.data;
  const lead = rows.find((r) => r.entity === primary && r.variable === "demand_mwh")!;
  const p = lead.s.pooled, pct = (p.estimate / lead.s.counterfactualMean) * 100;
  const clear = p.lo > 0 || p.hi < 0;
  const name = GRID_LABEL[primary];
  return (
    <Section title="What the estimates say">
      <p className="mb-2 max-w-3xl text-sm">
        Over the {lead.s.days.length} days of the event window, {name}&apos;s daily demand served was{" "}
        <strong><E ev={event} r={lead} term="pooled" field="est" v={p.estimate} /></strong> MWh a day {p.estimate >= 0 ? "above" : "below"} what
        its baseline days predict (95 percent interval <E ev={event} r={lead} term="pooled" field="lo" v={p.lo} /> to{" "}
        <E ev={event} r={lead} term="pooled" field="hi" v={p.hi} />), <E ev={event} r={lead} term="pooled" field="pct" v={pct} /> percent of the{" "}
        <E ev={event} r={lead} term="pooled" field="cf" v={lead.s.counterfactualMean} /> MWh a day expected.{" "}
        {clear ? "The interval excludes zero." : "The interval includes zero: the effect cannot be told apart from the baseline days' own variation."}
      </p>
      <p className="mb-3 max-w-3xl text-xs text-muted">
        A regression of each day&apos;s value on the event days, the day of the week and the year, fitted to the baseline days (the same days of earlier
        years); robust standard errors. It does not control for temperature, which the warehouse does not hold, nor for anything else that happened in
        the same days. <Link href="/data/methods/event_study">Method and replication</Link>.
      </p>
      <h3 className="mb-1 text-sm">{name}: the effect of each event day on daily demand served, MWh, with its 95 percent interval</h3>
      <Plot r={lead} label={name} />
      <p className="mb-3 text-xs text-muted">Filled: the day&apos;s interval excludes zero. Open: it includes zero.</p>
      <table className="mb-2 w-full text-left text-sm">
        <thead><tr className="border-b border-rule text-xs text-muted"><th className="py-1">Grid</th><th>Outcome</th><th className="text-right">Pooled effect</th><th className="text-right">95 percent interval</th><th className="text-right">Percent of expected</th><th className="text-right">Days</th></tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.entity + r.variable} className="border-b border-rule">
              <td className="py-1">{GRID_LABEL[r.entity]}</td>
              <td>{OUTCOME[r.variable].what}, {OUTCOME[r.variable].unit}</td>
              <td className="text-right tabular-nums"><E ev={event} r={r} term="pooled" field="est" v={r.s.pooled.estimate} /></td>
              <td className="text-right tabular-nums"><E ev={event} r={r} term="pooled" field="lo" v={r.s.pooled.lo} /> to <E ev={event} r={r} term="pooled" field="hi" v={r.s.pooled.hi} /></td>
              <td className="text-right tabular-nums"><E ev={event} r={r} term="pooled" field="pct" v={(r.s.pooled.estimate / r.s.counterfactualMean) * 100} /></td>
              <td className="text-right tabular-nums">{r.s.n}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <details className="text-sm">
        <summary className="cursor-pointer text-muted">Each event day&apos;s estimate, {name}, demand served (MWh)</summary>
        <table className="mt-1 text-left text-xs">
          <thead><tr className="text-muted"><th className="pr-4">Day</th><th className="pr-4 text-right">Effect</th><th className="text-right">95 percent interval</th></tr></thead>
          <tbody>
            {lead.s.days.map((d) => (
              <tr key={d.day}>
                <td className="pr-4">{d.day}</td>
                <td className="pr-4 text-right tabular-nums"><E ev={event} r={lead} term={`day|${d.day}`} field="est" v={d.estimate} /></td>
                <td className="text-right tabular-nums"><E ev={event} r={lead} term={`day|${d.day}`} field="lo" v={d.lo} /> to <E ev={event} r={lead} term={`day|${d.day}`} field="hi" v={d.hi} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
      <Cite tables={[T]} note="Estimated here with lib/eventstudy.ts, the twin of warehouse/derived/event_study.py, whose table event_study_estimates holds the same estimates" />
    </Section>
  );
}
