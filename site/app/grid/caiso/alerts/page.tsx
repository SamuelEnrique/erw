import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import type { SeriesRow } from "@/lib/data";
import { EFFECTS, MODEL, VARIANTS, effects, key, model, pacificHour, shape, type Day } from "@/lib/flexalerts";
import { shown } from "@/lib/format";
import { gridNotices } from "@/lib/reliability";
import { attempt } from "@/lib/supabase";

// Session 60: the Flex Alert scorecard (California grid-stress tool v1). How much did CAISO's demand fall in the hours of
// a Flex Alert or grid emergency, against what the weather and the calendar predicted, and what was that worth? Read from
// flex_alert_effects and flex_alert_model (warehouse/derived/flex_alert_scorecard.py, docs/methods/flex_alert_scorecard.md);
// notebooks/flex_alert_scorecard.ipynb reproduces every number. Charts are drawn here as plain SVG in the house palette:
// actual demand in cardinal, the model's prediction dashed, its 90 percent band shaded, the alert hours marked.
export const metadata: Metadata = { title: "The Flex Alert scorecard, CAISO" };
export const revalidate = 3600;

const GEHR = "https://www.caiso.com/documents/grid-emergencies-history-report-1998-to-present.pdf";
const SHORT: Record<string, string> = {
  flex_alert: "Flex Alert", eea_watch: "EEA Watch", eea1: "EEA 1", eea2: "EEA 2", eea3: "EEA 3", alert: "Alert", warning: "Warning",
  stage1: "Stage 1", stage2: "Stage 2", stage3: "Stage 3", load_interruption: "Load interruption", rmo: "RMO", transmission_emergency: "Transmission",
};

function V({ r, table = EFFECTS }: { r?: SeriesRow; table?: string }) {
  return r ? <Num check={key(r, table)} raw={r.value}>{shown(r.value)}</Num> : <span className="text-muted">not held</span>;
}
const usdShort = (v: number) => {
  const t = (x: number) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
  if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  return v.toLocaleString("en-US");
};
function Usd({ r, table = EFFECTS }: { r?: SeriesRow; table?: string }) {
  return r ? <span data-format="usd"><Num check={key(r, table)} raw={r.value}>{usdShort(r.value)}</Num></span> : <span className="text-muted">not held</span>;
}
const Interval = ({ lo, hi, table = EFFECTS, usd = false }: { lo?: SeriesRow; hi?: SeriesRow; table?: string; usd?: boolean }) =>
  usd ? <>(<Usd r={lo} table={table} /> to <Usd r={hi} table={table} />)</> : <>(<V r={lo} table={table} /> to <V r={hi} table={table} />)</>;

/** One alert day through the evening: actual (cardinal), predicted (dashed), its 90 percent band, the alert hours shaded. */
function DayChart({ rows }: { rows: SeriesRow[] }) {
  const by = new Map<number, Record<string, number>>();
  for (const r of rows) {
    const h = pacificHour(r.ts_utc);
    (by.get(h) ?? by.set(h, {}).get(h)!)[r.variable] = r.value;
  }
  const hs = [...by.keys()].sort((a, b) => a - b);
  if (!hs.length) return null;
  const vals = hs.flatMap((h) => ["actual_mw", "predicted_mw_lo", "predicted_mw_hi"].map((k) => by.get(h)![k]).filter((v) => v !== undefined));
  const lo = Math.min(...vals), hi = Math.max(...vals), pad = (hi - lo) * 0.08 || 500;
  const W = 260, Hh = 120, L = 34, B = 16, x = (h: number) => L + ((h - hs[0]) / Math.max(1, hs.at(-1)! - hs[0])) * (W - L - 6);
  const y = (v: number) => 4 + (1 - (v - (lo - pad)) / (hi - lo + 2 * pad)) * (Hh - B - 4);
  const path = (k: string) => hs.filter((h) => by.get(h)![k] !== undefined).map((h, i) => `${i ? "L" : "M"}${x(h).toFixed(1)},${y(by.get(h)![k]).toFixed(1)}`).join("");
  const band = hs.map((h) => `${x(h).toFixed(1)},${y(by.get(h)!.predicted_mw_hi).toFixed(1)}`).join(" ") + " " +
    [...hs].reverse().map((h) => `${x(h).toFixed(1)},${y(by.get(h)!.predicted_mw_lo).toFixed(1)}`).join(" ");
  const alertHs = hs.filter((h) => by.get(h)!.alert_hour === 1);
  const step = (W - L - 6) / Math.max(1, hs.at(-1)! - hs[0]);
  return (
    <svg viewBox={`0 0 ${W} ${Hh}`} className="h-auto w-full" role="img" aria-label="Actual and predicted demand through the evening">
      {alertHs.map((h) => <rect key={h} x={x(h) - step / 2} y={2} width={step} height={Hh - B - 2} fill="var(--color-panel)" stroke="var(--color-rule)" strokeWidth={0.4} />)}
      <polygon points={band} fill="var(--color-rule)" opacity={0.7} />
      <path d={path("predicted_mw")} fill="none" stroke="var(--color-muted)" strokeWidth={1.2} strokeDasharray="3 2" />
      <path d={path("actual_mw")} fill="none" stroke="var(--color-accent)" strokeWidth={1.6} />
      <text x={2} y={10} fontSize={8} fill="var(--color-muted)">{Math.round(hi / 1000)} GW</text>
      <text x={2} y={Hh - B} fontSize={8} fill="var(--color-muted)">{Math.round(lo / 1000)} GW</text>
      {hs.filter((h) => h % 3 === 0).map((h) => <text key={h} x={x(h)} y={Hh - 4} fontSize={8} textAnchor="middle" fill="var(--color-muted)">{h}:00</text>)}
    </svg>
  );
}

/** The year-by-year estimate: a bar per year with its 90 percent interval, zero marked. */
function YearChart({ years }: { years: [string, Map<string, SeriesRow>][] }) {
  const pts = years.map(([y, m]) => ({ y, v: m.get("reduction_mw")?.value, lo: m.get("reduction_mw_lo")?.value, hi: m.get("reduction_mw_hi")?.value }))
    .filter((p) => p.v !== undefined && p.lo !== undefined && p.hi !== undefined) as { y: string; v: number; lo: number; hi: number }[];
  if (!pts.length) return null;
  const mn = Math.min(0, ...pts.map((p) => p.lo)), mx = Math.max(0, ...pts.map((p) => p.hi));
  const W = 520, Hh = 200, L = 46, B = 20, bw = (W - L - 10) / pts.length;
  const y = (v: number) => 6 + (1 - (v - mn) / (mx - mn || 1)) * (Hh - B - 6);
  const ticks = [mn, mn / 2, 0, mx / 2, mx].filter((v, i, a) => a.indexOf(v) === i);
  return (
    <svg viewBox={`0 0 ${W} ${Hh}`} className="h-auto w-full max-w-2xl" role="img" aria-label="Estimated demand reduction by year, MW, with 90 percent intervals">
      {ticks.map((t) => <g key={t}><line x1={L} x2={W - 4} y1={y(t)} y2={y(t)} stroke="var(--color-rule)" strokeWidth={t === 0 ? 1.2 : 0.5} /><text x={L - 4} y={y(t) + 3} fontSize={9} textAnchor="end" fill="var(--color-muted)">{Math.round(t).toLocaleString("en-US")}</text></g>)}
      {pts.map((p, i) => {
        const cx = L + bw * i + bw / 2;
        return (
          <g key={p.y}>
            <rect x={cx - bw * 0.28} width={bw * 0.56} y={Math.min(y(p.v), y(0))} height={Math.abs(y(p.v) - y(0))} fill={p.v >= 0 ? "var(--color-down)" : "var(--color-accent)"} opacity={0.85} />
            <line x1={cx} x2={cx} y1={y(p.lo)} y2={y(p.hi)} stroke="var(--color-ink)" strokeWidth={1.2} />
            <line x1={cx - 5} x2={cx + 5} y1={y(p.lo)} y2={y(p.lo)} stroke="var(--color-ink)" />
            <line x1={cx - 5} x2={cx + 5} y1={y(p.hi)} y2={y(p.hi)} stroke="var(--color-ink)" />
            <text x={cx} y={Hh - 5} fontSize={10} textAnchor="middle" fill="var(--color-ink)">{p.y}</text>
          </g>
        );
      })}
    </svg>
  );
}

/** The model's check: each held-out hot day's error (actual less predicted, 16:00 to 21:00) against its temperature. */
function CheckChart({ pts }: { pts: { t: number; e: number }[] }) {
  if (!pts.length) return null;
  const tmin = Math.min(...pts.map((p) => p.t)), tmax = Math.max(...pts.map((p) => p.t));
  const emax = Math.max(...pts.map((p) => Math.abs(p.e)));
  const W = 520, Hh = 200, L = 46, B = 20;
  const x = (t: number) => L + ((t - tmin) / (tmax - tmin || 1)) * (W - L - 10);
  const y = (e: number) => 6 + (1 - (e + emax) / (2 * emax || 1)) * (Hh - B - 6);
  return (
    <svg viewBox={`0 0 ${W} ${Hh}`} className="h-auto w-full max-w-2xl" role="img" aria-label="Model error on the hottest non-alert days against temperature">
      {[-emax, 0, emax].map((e) => <g key={e}><line x1={L} x2={W - 4} y1={y(e)} y2={y(e)} stroke="var(--color-rule)" strokeWidth={e === 0 ? 1.2 : 0.5} /><text x={L - 4} y={y(e) + 3} fontSize={9} textAnchor="end" fill="var(--color-muted)">{Math.round(e).toLocaleString("en-US")}</text></g>)}
      {pts.map((p, i) => <circle key={i} cx={x(p.t)} cy={y(p.e)} r={2.6} fill="var(--color-muted)" opacity={0.75} />)}
      <text x={L} y={Hh - 4} fontSize={9} fill="var(--color-muted)">{tmin.toFixed(1)} F</text>
      <text x={W - 4} y={Hh - 4} fontSize={9} textAnchor="end" fill="var(--color-muted)">{tmax.toFixed(1)} F, the day&apos;s highest weighted temperature</text>
    </svg>
  );
}

export default async function FlexAlertScorecard() {
  const [eff, mod, ns] = await Promise.all([attempt(effects), attempt(model), attempt(() => gridNotices("2018-07-01", "2025-10-31"))]);
  if (!eff.ok || !mod.ok) {
    return (
      <div className="max-w-3xl">
        <h1 className="mb-3 text-3xl">The Flex Alert scorecard</h1>
        <p className="text-sm text-muted">The scorecard&apos;s tables could not be read: {!eff.ok ? eff.reason : !mod.ok ? mod.reason : ""}</p>
      </div>
    );
  }
  const { days, hours, years, model: g, heldout } = shape(eff.data, mod.data);
  const types = new Map<string, Set<string>>();
  for (const n of ns.ok ? ns.data : []) {
    const d = n.event_date.slice(0, 10);
    (types.get(d) ?? types.set(d, new Set()).get(d)!).add(n.event_type);
  }
  const P = (v: string) => g.get(v);
  const val = (d: Day, v: string) => d.v.get(v);
  const ranked = [...days].sort((a, b) => (val(b, "reduction_mw")?.value ?? 0) - (val(a, "reduction_mw")?.value ?? 0));
  const pooledMw = P("pooled_reduction_mw")?.value ?? 0;
  const bias = P("oos_bias_mw");
  const valued = days.filter((d) => val(d, "value_usd"));
  const yrs = [...years.entries()].sort((a, b) => a[0].localeCompare(b[0]));
  const checkPts = heldout.filter((h) => h.err && h.temp).map((h) => ({ t: h.temp!.value, e: h.err!.value }));
  const lastAlert = days.at(-1)?.day;

  return (
    <div>
      <p className="mb-1 text-xs text-muted"><Link href="/grid/caiso">CAISO</Link> / <Link href="/grid/caiso#reliability">Reliability</Link> / Flex Alert scorecard</p>
      <h1 className="mb-2 text-3xl">The Flex Alert scorecard: CAISO, 2018 to 2024</h1>
      <p className="mb-4 max-w-3xl">
        When California&apos;s grid runs short, CAISO asks people to use less power: a <strong>Flex Alert</strong>, and in worse hours an Energy Emergency
        Alert or stage emergency. Whether those calls cut demand, and by how much, is argued over, because the state pays for the alerts and for the
        programs dispatched with them. This page is an independent, replicable scorecard: for every alert day since July 2018 it compares the demand
        CAISO served in the alert hours with what a weather-and-calendar model predicted for those hours, and puts a wholesale price on the difference.
        Derived, tier <em>derived</em>; the <Link href="/data/methods/flex_alert_scorecard">method</Link> reads like a paper&apos;s, and a{" "}
        <a href="https://github.com/SamuelEnrique/erw/blob/main/notebooks/flex_alert_scorecard.ipynb">notebook</a> reproduces every number.
      </p>

      <Section title="The answer, pooled" aside="flex_alert_model">
        <div className="mb-3 max-w-3xl border-l-2 border-accent pl-3">
          <p className="mb-2 text-lg">
            Over <V r={P("pooled_days")} table={MODEL} /> alert days and <V r={P("pooled_hours")} table={MODEL} /> alert hours, the estimated cut in
            demand was <V r={P("pooled_reduction_mw")} table={MODEL} /> MW on average{" "}
            <span className="text-sm">(90 percent interval <Interval lo={P("pooled_reduction_mw_lo")} hi={P("pooled_reduction_mw_hi")} table={MODEL} /> MW;
            a positive number is a cut)</span>: demand served ran {pooledMw >= 0 ? "below" : "above"} what the weather and the calendar predicted.
          </p>
          <p className="text-sm">
            That is <V r={P("pooled_reduction_pct")} table={MODEL} /> percent of predicted demand in those hours, a total of{" "}
            <V r={P("pooled_reduction_mwh")} table={MODEL} /> MWh <Interval lo={P("pooled_reduction_mwh_lo")} hi={P("pooled_reduction_mwh_hi")} table={MODEL} />.
          </p>
        </div>
        <p className="mb-2 max-w-3xl text-sm">
          <strong>How to read it.</strong> The interval {(P("pooled_reduction_mw_lo")?.value ?? 0) < 0 && (P("pooled_reduction_mw_hi")?.value ?? 0) > 0 ? "includes zero" : "excludes zero"}.
          On the hottest non-alert days, which the model did not see, its error in the evening hours averaged <V r={bias} table={MODEL} /> MW (actual less
          predicted; root mean square error <V r={P("oos_rmse_mw")} table={MODEL} /> MW, mean absolute percentage error <V r={P("oos_mape_pct")} table={MODEL} /> percent,
          over <V r={P("oos_days")} table={MODEL} /> days). The alert days are hotter still: an effect of a few hundred megawatts, the size a statewide
          conservation call might plausibly have, is smaller than the model&apos;s own error on a hot evening. Read every number below against that.
        </p>
        <p className="mb-2 max-w-3xl text-sm">
          <strong>Does the model matter?</strong> Yes, and that is a finding. Five specifications named before fitting, each with its error on the hot days
          it did not see and its pooled estimate:
        </p>
        <div className="mb-2 overflow-x-auto">
          <table className="text-sm">
            <thead><tr className="border-b border-ink text-left text-xs text-muted"><th className="py-1 pr-3">Model</th><th className="py-1 pr-3 text-right">Hot-day error, MW (bias)</th><th className="py-1 pr-3 text-right">Hot-day RMSE, MW</th><th className="py-1 pr-3 text-right">Pooled estimate, MW (90 percent)</th></tr></thead>
            <tbody>
              {VARIANTS.map((v) => (
                <tr key={v.id} className="border-b border-rule">
                  <td className="py-1 pr-3">{v.name}</td>
                  <td className="py-1 pr-3 text-right tabular-nums"><V r={P(`variant_${v.id}_oos_bias_mw`)} table={MODEL} /></td>
                  <td className="py-1 pr-3 text-right tabular-nums"><V r={P(`variant_${v.id}_oos_rmse_mw`)} table={MODEL} /></td>
                  <td className="py-1 pr-3 text-right tabular-nums"><V r={P(`variant_${v.id}_pooled_reduction_mw`)} table={MODEL} />{" "}
                    <span className="text-xs text-muted"><Interval lo={P(`variant_${v.id}_pooled_reduction_mw_lo`)} hi={P(`variant_${v.id}_pooled_reduction_mw_hi`)} table={MODEL} /></span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="max-w-3xl text-xs text-muted">
          Each model is fitted hour by hour on the non-alert days of May to October; the hot-day error comes from five-fold cross-validation on the hottest
          tenth of those days (a daily high, population-weighted across Sacramento, Fresno and Los Angeles, of at least <V r={P("heldout_threshold_temp_f")} table={MODEL} /> F).
          Of the alert days, <V r={P("alert_days_hotter_than_threshold")} table={MODEL} /> were at least that hot. The robustness rows use 200 bootstrap
          replicates; the model used, 1,000.
        </p>
      </Section>

      <Section title="Every alert day, ranked" aside="flex_alert_effects">
        <p className="mb-2 max-w-3xl text-sm">
          Each day CAISO called a Flex Alert or a grid emergency for its whole area, from July 2018 to {lastAlert ?? "the last day held"}, ranked by the
          estimated cut in its alert hours (predicted less actual demand, MW, averaged over the hours). The hours are the Flex Alert&apos;s where there was one,
          else the emergency&apos;s; a day with none stated takes 16:00 to 21:00 and is marked. &ldquo;Days as hot&rdquo; counts the non-alert days in the
          model&apos;s training set at least as hot: where it is small, the model is extrapolating.
        </p>
        <div className="mb-2 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ink text-left text-xs text-muted">
                <th className="py-1 pr-2">Day (Pacific)</th><th className="py-1 pr-2">CAISO&apos;s notices</th><th className="py-1 pr-2">Alert hours</th>
                <th className="py-1 pr-2 text-right">High, F</th><th className="py-1 pr-2 text-right">Days as hot</th>
                <th className="py-1 pr-2 text-right">Cut, MW (90 percent)</th><th className="py-1 pr-2 text-right">Percent</th><th className="py-1 pr-2 text-right">Value, USD</th>
              </tr>
            </thead>
            <tbody>
              {ranked.map((d) => (
                <tr key={d.day} className="border-b border-rule">
                  <td className="py-1 pr-2 font-mono"><a href={`#d${d.day}`}>{d.day}</a></td>
                  <td className="py-1 pr-2 text-xs">{[...(types.get(d.day) ?? [])].filter((t) => SHORT[t] && t !== "rmo" && t !== "transmission_emergency").map((t) => SHORT[t]).join(", ")}</td>
                  <td className="py-1 pr-2 text-xs"><V r={val(d, "alert_first_hour")} />:00 to <V r={val(d, "alert_last_hour")} />:00{val(d, "hours_assumed")?.value === 1 ? " (assumed)" : ""}</td>
                  <td className="py-1 pr-2 text-right tabular-nums"><V r={val(d, "temp_max_f")} /></td>
                  <td className="py-1 pr-2 text-right tabular-nums"><V r={val(d, "train_days_as_hot")} /></td>
                  <td className="py-1 pr-2 text-right tabular-nums"><V r={val(d, "reduction_mw")} /> <span className="text-xs text-muted"><Interval lo={val(d, "reduction_mw_lo")} hi={val(d, "reduction_mw_hi")} /></span></td>
                  <td className="py-1 pr-2 text-right tabular-nums"><V r={val(d, "reduction_pct")} /></td>
                  <td className="py-1 pr-2 text-right tabular-nums">{val(d, "value_usd") ? <Usd r={val(d, "value_usd")} /> : <span className="text-xs text-muted">no price</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      <Section title="Year by year" aside="flex_alert_effects, P1Y">
        <YearChart years={yrs} />
        <div className="mt-2 overflow-x-auto">
          <table className="text-sm">
            <thead><tr className="border-b border-ink text-left text-xs text-muted"><th className="py-1 pr-3">Year</th><th className="py-1 pr-3 text-right">Alert days</th><th className="py-1 pr-3 text-right">Alert hours</th><th className="py-1 pr-3 text-right">Cut, MW (90 percent)</th><th className="py-1 pr-3 text-right">MWh</th></tr></thead>
            <tbody>
              {yrs.map(([y, m]) => (
                <tr key={y} className="border-b border-rule">
                  <td className="py-1 pr-3 font-mono">{y}</td><td className="py-1 pr-3 text-right tabular-nums"><V r={m.get("days")} /></td>
                  <td className="py-1 pr-3 text-right tabular-nums"><V r={m.get("hours")} /></td>
                  <td className="py-1 pr-3 text-right tabular-nums"><V r={m.get("reduction_mw")} /> <span className="text-xs text-muted"><Interval lo={m.get("reduction_mw_lo")} hi={m.get("reduction_mw_hi")} /></span></td>
                  <td className="py-1 pr-3 text-right tabular-nums"><V r={m.get("reduction_mwh")} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-1 max-w-3xl text-xs text-muted">Bars: the estimate, green where demand was below the model, cardinal where above; whiskers: the 90 percent interval.</p>
      </Section>

      <Section title="Each alert day through the evening" aside="flex_alert_effects, PT1H">
        <p className="mb-3 max-w-3xl text-sm">
          Demand served each hour from noon to midnight (cardinal) against the model&apos;s prediction (dashed) and its 90 percent band (shaded), the alert
          hours boxed. Where the cardinal line runs under the band through the boxed hours, the day shows a cut the model cannot explain.
        </p>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {days.map((d) => (
            <div key={d.day} id={`d${d.day}`} className="scroll-mt-2 border border-rule bg-panel p-2">
              <p className="mb-1 text-xs"><span className="font-mono">{d.day}</span>: cut <V r={val(d, "reduction_mw")} /> MW</p>
              <DayChart rows={hours.get(d.day) ?? []} />
            </div>
          ))}
        </div>
      </Section>

      <Section title="What it was worth, at the day-ahead price" aside="caiso_dam_alert_day_hub_prices">
        <p className="mb-2 max-w-3xl text-sm">
          Each alert hour&apos;s estimated cut, in MWh, times that hour&apos;s day-ahead price (the mean of CAISO&apos;s SP15 and NP15 hubs, OASIS), summed:
          a <strong>wholesale lower bound</strong>. The value of avoided scarcity, of reserves kept and of outages not taken is higher and is not estimated.
          A negative value means demand ran above the model, so the &ldquo;cut&rdquo; cost money at that price.
        </p>
        <p className="mb-2 max-w-3xl text-sm">
          Over the <V r={P("pooled_value_hours")} table={MODEL} /> alert hours with a price, the value is <Usd r={P("pooled_value_usd")} table={MODEL} /> USD{" "}
          <Interval lo={P("pooled_value_usd_lo")} hi={P("pooled_value_usd_hi")} table={MODEL} usd />. Prices are held for {valued.length} of the {days.length} alert
          days: CAISO&apos;s OASIS serves 39 months of history, so the 2018 to 2022 alert days, among them the heat waves of August 2020 and September 2022, have
          no price here and no value. On the hottest non-alert days with a price, the evening&apos;s day-ahead price averaged{" "}
          <V r={P("heldout_price_mean_usd_mwh")} table={MODEL} /> USD/MWh, against the alert days&apos; prices in the table above.
        </p>
      </Section>

      <Section title="The model's check: the hottest days it did not see" aside="flex_alert_model">
        <p className="mb-2 max-w-3xl text-sm">
          Alerts fall on the hottest days, so how the model does in extreme heat is the main risk. Each dot is one of the hottest non-alert days, predicted by
          the model fitted without it: its mean error from 16:00 to 21:00 (actual less predicted, MW) against the day&apos;s high. Dots below zero are days the
          model over-predicted; on an alert day, the same error would read as a cut.
        </p>
        <CheckChart pts={checkPts} />
      </Section>

      <Section title="What the estimate can and cannot say">
        <ul className="max-w-3xl list-disc pl-5 text-sm">
          <li><strong>It is the combined demand-side effect of an alert day, not the Flex Alert message alone.</strong> On the same days the state dispatches
            paid programs (the Demand Side Grid Support program, DSGS, and the Emergency Load Reduction Program, ELRP), utilities call their own demand
            response, and CAISO takes other actions; on 2020-08-14 and 2020-08-15 it ordered rotating outages, which also lower demand served.</li>
          <li><strong>The model&apos;s fit at extreme heat is the main risk.</strong> Alert days are hotter than nearly every day it learned from; the check above
            shows its error on the hottest days it did not see, and the table of models shows how much the answer moves with the specification.</li>
          <li><strong>Hourly data blurs short cuts.</strong> A conservation text can drop demand for twenty minutes; an hourly mean dilutes it.</li>
          <li><strong>Demand is demand served</strong> (EIA-930, CAISO&apos;s balancing authority), net of rooftop solar behind the meter; the year effects absorb
            its growth. Weather is three airports, weighted 0.5 Los Angeles, 0.3 Sacramento, 0.2 Fresno: it can miss a coastal fog or a storm&apos;s clouds.</li>
          <li><strong>The alert days end in 2024:</strong> CAISO&apos;s <a href={GEHR}>Grid Emergencies History Report</a> runs to 2025-04-30, so the 2025 season has none here.</li>
          <li><strong>The value is a lower bound</strong> at day-ahead prices, set before the day; real-time prices on alert evenings were often higher.</li>
        </ul>
        <p className="mt-3 max-w-3xl text-sm">
          The notices themselves, and how tight each evening was, are in <Link href="/grid/caiso#reliability">CAISO&apos;s Reliability section</Link>; the
          two heat waves have their own pages, <Link href="/events/caiso-heat-2020">August 2020</Link> and <Link href="/events/caiso-heat-2022">September 2022</Link>.
        </p>
      </Section>
      <Cite tables={[EFFECTS, MODEL, "caiso_grid_emergencies", "noaa_isd_hourly", "caiso_dam_alert_day_hub_prices"]} note="California ISO, Grid Emergencies History Report and OASIS PRC_LMP (credit the California ISO); EIA-930; NOAA NCEI Integrated Surface Database" />
    </div>
  );
}
