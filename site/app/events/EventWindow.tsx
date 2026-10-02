import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import type { ReactNode } from "react";
import { Cite } from "@/components/Cite";
import { LineChart, type Line } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { series, type SeriesRow } from "@/lib/data";
import { shown } from "@/lib/format";
import { attempt } from "@/lib/supabase";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";

// Session 39: one event page on the COVID-19 pattern (session 36C), for the events of event_window_daily keyed by a
// weekday-aligned baseline (the same weekday 364 and 728 days earlier). Every number is a row of the table; the page
// picks rows (the highest, the lowest) and draws them, and computes no value.

export const T = "event_window_daily";
const COLORS = ["var(--color-fuel-gas)", "var(--color-fuel-coal)", "var(--color-fuel-nuclear)", "var(--color-fuel-wind)", "var(--color-fuel-solar)", "var(--color-fuel-hydro)", "var(--color-fuel-storage)"];

export type Grid = { entity: string; name: string; slug?: string; tz: string };

export function Tier() {
  return (
    <Link href="/data/standard" title={TIER_TITLE.derived} className="ml-1 rounded border border-rule px-1 text-[10px] uppercase tracking-wide text-muted no-underline">
      {TIER_LABEL.derived}
    </Link>
  );
}

export const N = ({ r, event }: { r?: SeriesRow; event: string }) =>
  r ? <Num check={`series|${T}|${r.entity}|${r.variable}|${r.ts_utc}|${event}`} raw={r.value}>{shown(r.value)}</Num> : <span className="text-muted">not held</span>;
export const day = (r?: SeriesRow) => (r ? r.ts_utc.slice(0, 10) : "");
const sec = (ts: string) => Date.parse(`${ts.slice(0, 10)}T00:00:00Z`) / 1000;

export function pickOf(rows: SeriesRow[], entity: string, variable: string, how: "max" | "min", inWindow: (d: string) => boolean): SeriesRow | undefined {
  const xs = rows.filter((r) => r.entity === entity && r.variable === variable && inWindow(r.ts_utc.slice(0, 10)));
  if (!xs.length) return undefined;
  return xs.reduce((a, b) => (how === "max" ? (b.value > a.value ? b : a) : b.value < a.value ? b : a));
}
export const find = (rows: SeriesRow[], entity: string, variable: string, d: string) =>
  rows.find((r) => r.entity === entity && r.variable === variable && r.ts_utc.slice(0, 10) === d);

// Session 64: the other ISOs' main hubs (iso_hub_prices_history, held from 2024-09-01, so no baseline days)
export type Hub = { entity: string; name: string; rtNote: string };

export async function EventWindow({ event, title, crumb, framing, caveat, grids, start, end, hub, hubs, peakWord = "highest", after }: {
  event: string; title: string; crumb: string; framing: ReactNode; caveat: ReactNode; grids: Grid[]; start: string; end: string;
  hub?: string; hubs?: Hub[]; peakWord?: string; after?: (rows: SeriesRow[]) => ReactNode;
}) {
  const got = await attempt(() => series(T, { event }));
  const rows = got.ok ? got.data : [];
  const inWin = (d: string) => d >= start && d <= end;
  const pts = (entity: string, variable: string, keep: (d: string) => boolean, shift = 0) =>
    rows.filter((r) => r.entity === entity && r.variable === variable && keep(r.ts_utc.slice(0, 10)))
      .sort((a, b) => a.ts_utc.localeCompare(b.ts_utc)).map((r) => ({ t: sec(r.ts_utc) + shift * 86_400, v: r.value }));
  const shifted = (o: number) => (d: string) => {
    const t = new Date(`${d}T00:00:00Z`);
    t.setUTCDate(t.getUTCDate() + o);
    return inWin(t.toISOString().slice(0, 10));
  };
  const multi = grids.length > 1;
  const color = (i: number, g: Grid) => (g.entity.endsWith("US48") ? "accent" : multi ? COLORS[i % COLORS.length] : "accent");
  const peakLines: Line[] = grids.map((g, i) => ({ label: g.name, color: color(i, g), points: pts(g.entity, "demand_max_pct_vs_baseline", inWin) }));
  const ciLines: Line[] = grids.map((g, i) => ({ label: g.name, color: color(i, g), points: pts(g.entity, "intensity_generation", inWin) }));
  const yr = start.slice(0, 4);
  return (
    <>
      <p className="mb-1 text-xs text-muted"><Link href="/events">Events</Link> / {crumb}</p>
      <h1 className="mb-1 text-3xl">{title}</h1>
      <div className="mb-5 max-w-3xl text-sm">
        <div className="mb-2">{framing}</div>
        <div className="text-muted">{caveat} <Link href="/data/methods/events">Method</Link>.</div>
      </div>
      {!got.ok || !rows.length ? (
        <NoData what="the event window" reason={got.ok ? `${T} returned no rows for ${event}` : got.reason} />
      ) : (
        <>
          <Section title={`Peak hour of demand against the same weekdays of earlier years${multi ? ", all grids" : ""}`} aside={<Tier />}>
            <LineChart lines={peakLines} unit="% vs baseline" height={280} ariaLabel={`Each day's peak hour of demand served against the mean of the same weekday 364 and 728 days earlier, in percent, ${start} to ${end}`} />
            <p className="mt-1 text-sm text-muted">
              Each point is a day: its highest hour of demand served over the mean of the highest hours of the same weekday 364 and 728 days earlier, minus one,
              in percent. A day with a missing hour, in any of the three years, has no point.
            </p>
            {after ? <div className="mt-2 max-w-3xl text-sm">{after(rows)}</div> : null}
            <Cite tables={[T]} note="EIA-930 hourly demand per balancing authority (the per-BA workbooks), each grid's local day; variable demand_max_pct_vs_baseline" />
          </Section>

          <Section title={multi ? "Each grid: the peak hour each day, the event and the same weekdays of earlier years" : "The peak hour each day, the event and the same weekdays of earlier years"} aside={<Tier />}>
            <div className={multi ? "grid gap-6 md:grid-cols-2" : ""}>
              {grids.map((g) => {
                const hi = pickOf(rows, g.entity, "demand_max_pct_vs_baseline", "max", inWin);
                const peak = hi ? find(rows, g.entity, "demand_max_mw", day(hi)) : undefined;
                const top = pickOf(rows, g.entity, "demand_max_mw", "max", inWin);
                const ci = pickOf(rows, g.entity, "intensity_generation", "max", inWin);
                return (
                  <div key={g.entity}>
                    {multi ? <h3 className="mb-1 text-base">{g.slug ? <Link href={`/grid/${g.slug}`}>{g.name}</Link> : g.name}</h3> : null}
                    <LineChart
                      lines={[
                        { label: yr, color: "accent", points: pts(g.entity, "demand_max_mw", inWin) },
                        { label: "364 days earlier", color: "muted", points: pts(g.entity, "demand_max_mw", shifted(364), 364) },
                        { label: "728 days earlier", color: "var(--color-fuel-gas)", points: pts(g.entity, "demand_max_mw", shifted(728), 728) },
                      ]}
                      unit="MW" height={multi ? 200 : 260}
                      ariaLabel={`${g.name} highest hour of demand served each day, ${start} to ${end}, and the same weekdays 364 and 728 days earlier`}
                    />
                    <p className="mt-1 text-sm">
                      The {peakWord} peak against the baseline: <N r={hi} event={event} />% on {day(hi)} (<N r={peak} event={event} /> MW). The highest hour of the
                      window: <N r={top} event={event} /> MW on {day(top)}. The highest carbon intensity: <N r={ci} event={event} /> kg CO2/MWh on {day(ci)}.
                    </p>
                    <p className="text-xs text-muted">Days: {g.tz}. Baseline days are drawn on the event day they are compared with.</p>
                  </div>
                );
              })}
            </div>
            <Cite tables={[T]} note="EIA-930 hourly demand; demand_max_mw, demand_max_pct_vs_baseline and intensity_generation (EIA's CO2 estimates over net generation, per local day)" />
          </Section>

          <Section title={`Carbon intensity of generation${multi ? ", all grids" : ""}`} aside={<Tier />}>
            <LineChart lines={ciLines} unit="kg CO2/MWh" height={240} ariaLabel={`Carbon intensity of generation per day, ${start} to ${end}`} />
            <Cite tables={[T]} note="EIA's CO2 emissions generated (eia930_all_emissions) over net generation, per local day" />
          </Section>

          {hub ? (
            <Section title="Price: ERCOT hub average" aside={<Tier />}>
              <LineChart
                lines={[
                  { label: "Real-time, daily mean", color: "accent", points: pts(hub, "rt_mean", inWin) },
                  { label: "Real-time, highest 15 minutes", color: "var(--color-fuel-coal)", points: pts(hub, "rt_max", inWin) },
                  { label: "Day-ahead, daily mean", color: "var(--color-fuel-gas)", points: pts(hub, "da_mean", inWin) },
                  { label: "Real-time mean, 364 days earlier", color: "muted", points: pts(hub, "rt_mean", shifted(364), 364) },
                ]}
                unit="USD/MWh" height={260} ariaLabel={`ERCOT hub average real-time and day-ahead prices per day, ${start} to ${end}`}
              />
              {(() => {
                const rt = pickOf(rows, hub, "rt_max", "max", inWin), da = pickOf(rows, hub, "da_max", "max", inWin), rm = pickOf(rows, hub, "rt_mean", "max", inWin);
                return (
                  <p className="mt-1 text-sm">
                    The highest 15-minute real-time price: <N r={rt} event={event} /> USD/MWh on {day(rt)}; the highest daily mean <N r={rm} event={event} /> on {day(rm)}; the
                    highest day-ahead hour <N r={da} event={event} /> on {day(da)}.
                  </p>
                );
              })()}
              <Cite tables={[T]} note="ERCOT's settlement point prices at the hub average (HB_HUBAVG), from ercot_all_hub_prices_history, per operating day" />
            </Section>
          ) : null}

          {hubs && hubs.length ? (
            <Section title={`Price: ${hubs.map((h) => h.name).join(", ")}`} aside={<Tier />}>
              <LineChart
                lines={hubs.map((h, i) => ({ label: h.name, color: COLORS[i % COLORS.length], points: pts(h.entity, "rt_mean", inWin) }))}
                unit="USD/MWh" height={260} ariaLabel={`Each hub's daily mean real-time price, ${start} to ${end}`}
              />
              <p className="mt-1 text-sm text-muted">
                Each point is a day&apos;s mean real-time price at the hub, on its grid&apos;s local day. The warehouse holds these hubs from 2024-09-01, so there are no
                baseline days to draw against: the price lines are the event days only.
              </p>
              <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm">
                {hubs.map((h) => {
                  const rt = pickOf(rows, h.entity, "rt_max", "max", inWin), rm = pickOf(rows, h.entity, "rt_mean", "max", inWin), da = pickOf(rows, h.entity, "da_max", "max", inWin);
                  return (
                    <li key={h.entity}>
                      <strong>{h.name}:</strong> the highest real-time price ({h.rtNote}) <N r={rt} event={event} /> USD/MWh on {day(rt)}; the highest daily mean{" "}
                      <N r={rm} event={event} /> on {day(rm)}; the highest day-ahead hour <N r={da} event={event} /> on {day(da)}.
                    </li>
                  );
                })}
              </ul>
              <Cite tables={[T, "iso_hub_prices_history"]} note="each ISO's own day-ahead and real-time prices at its main hub (the history table, session 49; its second year, session 64), per local day" />
            </Section>
          ) : null}
        </>
      )}
    </>
  );
}
