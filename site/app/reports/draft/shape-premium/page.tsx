import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Cite } from "@/components/Cite";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { series, type SeriesRow } from "@/lib/data";
import { shown } from "@/lib/format";
import { monthsOf, stats, type Row } from "@/lib/shapepremium";

// Session 48 (fallback): the first deep-dive report, a draft, internal only. Not in the nav, not indexed, and gated by
// the internal token, as /internal/costs: /reports/draft/shape-premium?token=<INTERNAL_COSTS_TOKEN>; it answers 404
// otherwise. Every number is read from cost_of_power_monthly or cost_of_power_hourly_profile (Supabase) and carries a
// check key that scripts/check-values.mjs recomputes: a table row (series|...), a period statistic (shape|..., by
// lib/shapepremium.ts) or a ratio or difference of two (calc|...).
export const metadata: Metadata = { title: "Draft: what flat load pays", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const M = "cost_of_power_monthly", P = "cost_of_power_hourly_profile";
const HUBS: { e: string; iso: string; hub: string }[] = [
  { e: "caiso:TH_SP15_GEN-APND", iso: "CAISO", hub: "SP15" },
  { e: "ercot:HB_HUBAVG", iso: "ERCOT", hub: "the hub average" },
  { e: "isone:.H.INTERNAL_HUB", iso: "ISO-NE", hub: "the internal hub" },
  { e: "miso:INDIANA.HUB", iso: "MISO", hub: "Indiana Hub" },
  { e: "nyiso:N.Y.C.", iso: "NYISO", hub: "New York City" },
  { e: "spp:SPPNORTH_HUB", iso: "SPP", hub: "SPP North" },
];
const ERCOT = "ercot:HB_HUBAVG";
const tilde = (k: string) => k.replaceAll("|", "~");
type V = { v: number; k: string };
const rowV = (t: string, r: SeriesRow): V => ({ v: r.value, k: `series|${t}|${r.entity}|${r.variable}|${r.ts_utc}` });
const calc = (op: "ratio" | "diff" | "pct", a: V, b: V): V =>
  ({ v: op === "ratio" ? a.v / b.v : op === "diff" ? a.v - b.v : (a.v / b.v) * 100, k: `calc|${op}|${tilde(a.k)}|${tilde(b.k)}` });
const N = ({ x, d }: { x: V; d?: (v: number) => string }) => <Num check={x.k} raw={x.v}>{d ? d(x.v) : shown(x.v)}</Num>;
const month = (ts: string) => new Date(`${ts.slice(0, 10)}T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
const nextDay = (d: string) => new Date(Date.parse(`${d}T00:00:00Z`) + 32 * 86_400_000).toISOString().slice(0, 8) + "01";

/** Horizontal bars, one series: each hub's day-ahead shape premium, USD/MWh. */
function Bars({ items }: { items: { label: string; v: number }[] }) {
  const W = 640, row = 30, L = 120, R = 70, H = items.length * row + 24;
  const max = Math.max(...items.map((i) => i.v), 0.01);
  const x = (v: number) => L + (Math.max(0, v) / max) * (W - L - R);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-2xl" role="img" aria-label="Day-ahead shape premium by ISO hub, USD/MWh; the table below holds the values">
      <line x1={L} x2={L} y1={4} y2={H - 20} stroke="var(--color-muted)" strokeWidth={1} />
      {items.map((it, i) => (
        <g key={it.label}>
          <title>{`${it.label}: ${shown(it.v)} USD/MWh`}</title>
          <text x={L - 8} y={i * row + 22} textAnchor="end" fontSize={12} fill="var(--color-ink)">{it.label}</text>
          <rect x={L} y={i * row + 10} width={Math.max(1, x(it.v) - L)} height={16} rx={2} fill="var(--color-accent)" />
          <text x={x(it.v) + 6} y={i * row + 22} fontSize={12} fill="var(--color-muted)">{shown(it.v)}</text>
        </g>
      ))}
      <text x={L} y={H - 4} fontSize={11} fill="var(--color-muted)">0</text>
      <text x={W - R} y={H - 4} textAnchor="end" fontSize={11} fill="var(--color-muted)">USD/MWh</text>
    </svg>
  );
}

/** ERCOT's monthly real-time shape premium, every complete month: bars above zero in cardinal, below in green. The
 * axis is cut at the second-largest month so Uri's February 2021 does not flatten the rest; that bar is marked. */
function Months({ ms }: { ms: { ts: string; premium: number }[] }) {
  const W = 720, H = 220, L = 44, R = 8, top = 14, bot = 26;
  const sorted = [...ms].map((m) => m.premium).sort((a, b) => b - a);
  const cap = Math.ceil((sorted[1] ?? sorted[0]) / 5) * 5, lo = Math.min(0, ...ms.map((m) => m.premium));
  const y = (v: number) => top + ((cap - Math.min(v, cap)) / (cap - lo)) * (H - top - bot);
  const bw = (W - L - R) / ms.length;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="ERCOT hub average, real-time shape premium per complete month, USD/MWh">
      {[0, cap / 2, cap].map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke={t === 0 ? "var(--color-ink)" : "var(--color-rule)"} strokeWidth={1} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize={11} fill="var(--color-muted)">{t}</text>
        </g>
      ))}
      {ms.map((m, i) => (
        <g key={m.ts}>
          <title>{`${m.ts.slice(0, 7)}: ${shown(m.premium)} USD/MWh`}</title>
          <rect x={L + i * bw + 0.5} width={Math.max(1, bw - 1)} y={m.premium >= 0 ? y(m.premium) : y(0)}
            height={Math.max(1, Math.abs(y(m.premium) - y(0)))} fill={m.premium >= 0 ? "var(--color-up)" : "var(--color-down)"} />
          {m.premium > cap ? <text x={L + i * bw + bw / 2} y={top - 3} textAnchor="middle" fontSize={10} fill="var(--color-ink)">{`${m.ts.slice(0, 7)}: ${shown(m.premium)} (cut)`}</text> : null}
        </g>
      ))}
      {ms.filter((m) => m.ts.slice(5, 7) === "01").map((m) => {
        const i = ms.indexOf(m);
        return <text key={m.ts} x={L + i * bw} y={H - 8} fontSize={11} fill="var(--color-muted)">{m.ts.slice(0, 4)}</text>;
      })}
    </svg>
  );
}

/** One hub's hour-of-day real-time profile for a month: a 2px line, its own scale, the cheapest and dearest hours marked. */
function Profile({ label, cells }: { label: string; cells: { h: number; v: number }[] }) {
  const W = 220, H = 120, L = 34, R = 6, top = 18, bot = 18;
  const lo = Math.min(...cells.map((c) => c.v)), hi = Math.max(...cells.map((c) => c.v));
  const x = (h: number) => L + (h / 23) * (W - L - R), y = (v: number) => top + ((hi - v) / (hi - lo || 1)) * (H - top - bot);
  const a = cells.find((c) => c.v === lo)!, b = cells.find((c) => c.v === hi)!;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={`${label}: mean real-time price by hour of the day`}>
      <text x={L} y={11} fontSize={12} fill="var(--color-ink)">{label}</text>
      <line x1={L} x2={W - R} y1={H - bot} y2={H - bot} stroke="var(--color-rule)" />
      <text x={L - 4} y={y(hi) + 4} textAnchor="end" fontSize={10} fill="var(--color-muted)">{Math.round(hi)}</text>
      <text x={L - 4} y={y(lo) + 4} textAnchor="end" fontSize={10} fill="var(--color-muted)">{Math.round(lo)}</text>
      <polyline fill="none" stroke="var(--color-accent)" strokeWidth={2} points={cells.map((c) => `${x(c.h)},${y(c.v)}`).join(" ")} />
      {[a, b].map((c) => <circle key={c.h} cx={x(c.h)} cy={y(c.v)} r={4} fill="var(--color-accent)" stroke="var(--color-panel)" strokeWidth={2}><title>{`${String(c.h).padStart(2, "0")}:00, ${shown(c.v)} USD/MWh`}</title></circle>)}
      {[6, 12, 18].map((h) => <text key={h} x={x(h)} y={H - 4} textAnchor="middle" fontSize={10} fill="var(--color-muted)">{String(h).padStart(2, "0")}</text>)}
    </svg>
  );
}

export default async function ShapePremium({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const token = typeof sp.token === "string" ? sp.token : "";
  const want = process.env.INTERNAL_COSTS_TOKEN ?? "";
  if (want.length < 24 || token !== want) notFound();

  const all = await series(M, {});
  const rows: Row[] = all.map((r) => ({ entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: r.value }));
  const find = (e: string, v: string, ts: string) => all.find((r) => r.entity === e && r.variable === v && r.ts_utc.slice(0, 10) === ts.slice(0, 10))!;

  // 1. the six hubs, day-ahead, the latest month every hub holds with its day-ahead hours
  const latest = [...new Set(all.filter((r) => r.variable === "da_shape_premium").map((r) => r.ts_utc.slice(0, 10)))].sort()
    .reverse().find((ts) => HUBS.every((h) => all.some((r) => r.entity === h.e && r.variable === "da_shape_premium" && r.ts_utc.slice(0, 10) === ts)))!;
  const six = HUBS.map((h) => {
    const lw = rowV(M, find(h.e, "da_load_weighted", latest)), sm = rowV(M, find(h.e, "da_simple_mean", latest));
    const pr = rowV(M, find(h.e, "da_shape_premium", latest)), hrs = rowV(M, find(h.e, "da_hours", latest)), inMonth = rowV(M, find(h.e, "hours_in_month", latest));
    return { ...h, lw, sm, pr, hrs, inMonth, pct: calc("pct", pr, sm) };
  }).sort((a, b) => b.pr.v - a.pr.v);
  const top = six[0], low = six.at(-1)!, topPct = [...six].sort((a, b) => b.pct.v - a.pct.v)[0];

  // 2. ERCOT, every complete real-time month
  const ems = monthsOf(rows, ERCOT, "rt").filter((m) => m.complete);
  const first = ems[0].ts, endAll = nextDay(ems.at(-1)!.ts);
  const sAll = stats(rows, ERCOT, "rt", first, endAll);
  const sk = (stat: string, s: string, e: string, v: number): V => ({ v, k: `shape|${ERCOT}|rt|${stat}|${s}|${e}` });
  const nAll = sk("n", first, endAll, sAll.n), posAll = sk("npos", first, endAll, sAll.npos), meanAll = sk("mean", first, endAll, sAll.mean);
  const big = [...ems].sort((a, b) => b.premium - a.premium);
  const uri = rowV(M, find(ERCOT, "rt_shape_premium", big[0].ts)), second = rowV(M, find(ERCOT, "rt_shape_premium", big[1].ts));
  const uriLw = rowV(M, find(ERCOT, "rt_load_weighted", big[0].ts)), uriSm = rowV(M, find(ERCOT, "rt_simple_mean", big[0].ts));
  const neg = ems.filter((m) => m.premium <= 0);
  const years = [...new Set(ems.map((m) => m.ts.slice(0, 4)))].filter((y) => ems.filter((m) => m.ts.startsWith(y)).length === 12);
  const yearly = years.map((y) => {
    const s = stats(rows, ERCOT, "rt", `${y}-01-01`, `${Number(y) + 1}-01-01`);
    return { y, usd: sk("usdmw", `${y}-01-01`, `${Number(y) + 1}-01-01`, s.usdmw), mean: sk("mean", `${y}-01-01`, `${Number(y) + 1}-01-01`, s.mean) };
  });
  const y21 = yearly.find((x) => x.y === "2021"), lastY = yearly.at(-1)!;
  const last12Start = new Date(Date.parse(`${endAll}T00:00:00Z`) - 365 * 86_400_000).toISOString().slice(0, 8) + "01";
  const s12 = stats(rows, ERCOT, "rt", last12Start, endAll);
  const n12 = sk("n", last12Start, endAll, s12.n), usd12 = sk("usdmw", last12Start, endAll, s12.usdmw), mean12 = sk("mean", last12Start, endAll, s12.mean);

  // 1b. session 49: twelve months for every hub (iso_hub_prices_history holds a year of the five hubs other than ERCOT):
  // the twelve months ending with the latest month every hub holds in real time, each hub's complete months in it (the
  // ISOs' own gap days leave some months partial; only complete months count)
  const lastAll = [...new Set(all.filter((r) => r.variable === "rt_shape_premium").map((r) => r.ts_utc.slice(0, 10)))].sort().reverse()
    .find((ts) => HUBS.every((h) => monthsOf(rows, h.e, "rt").some((m) => m.ts === ts)));
  const yEnd = lastAll ? nextDay(lastAll) : "";
  const yStart = lastAll ? `${Number(lastAll.slice(0, 4)) - 1}-${String(Number(lastAll.slice(5, 7)) % 12 + 1).padStart(2, "0")}-01` : "";
  const fixStart = lastAll && Number(lastAll.slice(5, 7)) === 12 ? `${lastAll.slice(0, 4)}-01-01` : yStart;
  const year = lastAll ? HUBS.map((h) => {
    const st = stats(rows, h.e, "rt", fixStart, yEnd);
    const k = (stat: string, v: number): V => ({ v, k: `shape|${h.e}|rt|${stat}|${fixStart}|${yEnd}` });
    return { ...h, n: k("n", st.n), npos: k("npos", st.npos), mean: k("mean", st.mean), usd: k("usdmw", st.usdmw) };
  }).sort((a, b) => (b.n.v > 0 ? 1 : 0) - (a.n.v > 0 ? 1 : 0) || b.mean.v - a.mean.v) : [];
  const allTwelve = year.length > 0 && year.every((y) => y.n.v === 12);
  const ranked = year.filter((y) => y.n.v > 0);  // a hub with no complete month has no mean and is left out of the text
  const alwaysPos = ranked.filter((y) => y.npos.v === y.n.v);
  const noneComplete = year.filter((y) => y.n.v === 0);

  // 3. the hour of the day, each hub's latest profile month
  const prof = await series(P, {});
  const pm = [...new Set(prof.map((r) => r.ts_utc.slice(0, 10)))].sort().at(-1)!;
  const shapes = HUBS.map((h) => {
    const cells = prof.filter((r) => r.entity === h.e && r.ts_utc.slice(0, 10) === pm && r.variable.startsWith("rt_mean_h"));
    const days = prof.find((r) => r.entity === h.e && r.ts_utc.slice(0, 10) === pm && r.variable === "rt_days_h12");
    const lo = cells.reduce((a, b) => (b.value < a.value ? b : a)), hi = cells.reduce((a, b) => (b.value > a.value ? b : a));
    return { ...h, cells, lo: rowV(P, lo), hi: rowV(P, hi), loH: lo.variable.slice(-2), hiH: hi.variable.slice(-2), days: days ? rowV(P, days) : null };
  });
  const ercotShape = shapes.find((s) => s.e === ERCOT)!;
  const topShape = shapes.find((s) => s.e === top.e)!;
  const ercotDa = rowV(M, find(ERCOT, "da_shape_premium", latest)), ercotRt = rowV(M, find(ERCOT, "rt_shape_premium", latest));

  return (
    <article className="max-w-3xl">
      <p className="mb-2 text-xs uppercase tracking-wide text-accent">Draft, internal: not for circulation. Not in the nav, not indexed.</p>
      <h1 className="mb-1 text-3xl">What flat load pays: the shape premium across six ISOs</h1>
      <p className="mb-6 text-sm text-muted">Energy Research Warehouse (ERW), deep-dive report 1, draft of 2026-10-01. Every number is read from the warehouse&apos;s cost-of-power tables and checked against them.</p>

      <Section title="The question">
        <p className="mb-3">
          A load that draws the same power every hour pays the plain average of the hourly prices. A load shaped like the grid&apos;s own, heavy in the
          late afternoon and evening, light at night, buys more of its energy in the dear hours, and pays the load-weighted average. The difference
          between the two is the <strong>shape premium</strong>: what each megawatt-hour of grid-shaped load pays beyond a flat one. It is the price of
          being on the grid&apos;s schedule, and the saving a flat load (a datacenter, a factory on three shifts, an electrolyzer) collects without doing
          anything at all.
        </p>
        <p>
          The warehouse computes it every month for the main hub of six ISOs (<code className="font-mono">cost_of_power_monthly</code>, method:{" "}
          <Link href="/data/methods/cost_of_power">cost of power</Link>), weighting each hour&apos;s hub price by the ISO&apos;s demand that hour from EIA-930.
          This draft asks three things: how large the premium is across the six ISOs now, how it has moved in the one ISO where the warehouse holds
          eight years, and where in the day it comes from.
        </p>
      </Section>

      <Section title={`Six ISOs, ${month(latest)}`}>
        <p className="mb-3">
          Day-ahead, over the days of {month(latest)} the warehouse holds for every hub ({top.hrs.v === top.inMonth.v ? "the whole month" : <><N x={top.hrs} /> of <N x={top.inMonth} /> hours</>}),
          the premium runs from <N x={low.pr} /> USD/MWh at {low.iso}&apos;s {low.hub} to <N x={top.pr} /> USD/MWh at {top.iso}&apos;s {top.hub}. Against the
          flat price, the spread is wider still: {low.iso}&apos;s premium is <N x={low.pct} /> percent of its simple average, {topPct.iso}&apos;s{" "}
          <N x={topPct.pct} /> percent. Day-ahead is used here because it is the one market every hub holds for nearly every hour of the month.
          The twelve-month view below reads the real-time market over a year.
        </p>
        <Bars items={six.map((s) => ({ label: s.iso, v: s.pr.v }))} />
        <table className="mt-2 w-full text-left text-sm tabular-nums">
          <thead><tr className="border-b border-rule text-xs text-muted"><th className="py-1">ISO hub</th><th className="text-right">Load-weighted</th><th className="text-right">Simple</th><th className="text-right">Premium</th><th className="text-right">Percent</th><th className="text-right">Hours held</th></tr></thead>
          <tbody>
            {six.map((s) => (
              <tr key={s.e} className="border-b border-rule">
                <td className="py-1">{s.iso}, {s.hub}</td>
                <td className="text-right"><N x={s.lw} /></td><td className="text-right"><N x={s.sm} /></td>
                <td className="text-right"><N x={s.pr} /></td><td className="text-right"><N x={s.pct} /></td>
                <td className="text-right"><N x={s.hrs} /></td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-1 text-xs text-muted">USD/MWh, day-ahead, {month(latest)}. Percent: the premium over the simple average.</p>
        <p className="mt-3">
          One month is a thin basis for ranking grids. {topShape.iso}&apos;s lead comes from its evening: in real time its dearest hour of the day,{" "}
          {topShape.hiH}:00, averaged <N x={topShape.hi} /> USD/MWh over the days held, <N x={calc("ratio", topShape.hi, topShape.lo)} /> times its cheapest,{" "}
          {topShape.loH}:00 (<N x={topShape.lo} />). A few dear evenings are enough to lift a month&apos;s load-weighted price, and they need not recur. What
          the six agree on is the sign: in every hub, the grid&apos;s own load paid more per megawatt-hour than a flat load would have.
        </p>
      </Section>

      {ranked.length >= 2 ? (
        <Section title={`Twelve months, six hubs: ${month(fixStart)} to ${month(lastAll!)}`}>
          <p className="mb-3">
            {allTwelve ? "Every hub has all twelve months complete in real time." : "Not every hub has all twelve months complete; the table gives each hub's count, and its figures are over those months."}{" "}
            {noneComplete.length ? <>{noneComplete.map((y) => y.iso).join(" and ")} {noneComplete.length === 1 ? "has" : "have"} no complete month in it, so {noneComplete.length === 1 ? "it is" : "they are"} left out of what follows. </> : null}
            Over their complete months, the mean real-time premium runs from <N x={ranked.at(-1)!.mean} /> USD/MWh at {ranked.at(-1)!.iso}&apos;s {ranked.at(-1)!.hub} to{" "}
            <N x={ranked[0].mean} /> at {ranked[0].iso}&apos;s {ranked[0].hub}.{" "}
            {alwaysPos.length === ranked.length
              ? "The premium was positive in every complete month at each of them."
              : alwaysPos.length
                ? <>It was positive in every complete month at {alwaysPos.map((y) => y.iso).join(", ")}; at the others, some months had a negative premium (the table counts them).</>
                : "At every hub, some months had a negative premium (the table counts them)."}{" "}
            Summed over its complete months, a megawatt shaped like the grid&apos;s load paid <N x={ranked[0].usd} /> USD more than a flat megawatt at {ranked[0].iso}, and{" "}
            <N x={ranked.at(-1)!.usd} /> USD at {ranked.at(-1)!.iso}; the counts of months differ, so these sums are not a ranking.
          </p>
          <table className="w-full text-left text-sm tabular-nums">
            <thead><tr className="border-b border-rule text-xs text-muted"><th className="py-1">ISO hub</th><th className="text-right">Complete months</th><th className="text-right">Positive</th><th className="text-right">Mean premium, USD/MWh</th><th className="text-right">Grid-shaped over flat, USD per MW</th></tr></thead>
            <tbody>
              {year.map((y) => (
                <tr key={y.e} className="border-b border-rule">
                  <td className="py-1">{y.iso}, {y.hub}</td><td className="text-right"><N x={y.n} /></td><td className="text-right"><N x={y.npos} /></td>
                  {y.n.v > 0 ? <><td className="text-right"><N x={y.mean} /></td><td className="text-right"><N x={y.usd} /></td></> : <td colSpan={2} className="text-right text-muted">no complete month</td>}
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-1 text-xs text-muted">Real-time, each hub&apos;s complete months from {month(fixStart)} to {month(lastAll!)}. Mean: the months&apos; premiums averaged; USD per MW: each month&apos;s premium times its hours, summed.</p>
        </Section>
      ) : null}

      <Section title="Eight years of ERCOT">
        <p className="mb-3">
          ERCOT is the one hub with a long history in the warehouse. Over <N x={nAll} /> complete months, from {month(first)} to{" "}
          {month(ems.at(-1)!.ts)}, the real-time premium was positive in <N x={posAll} /> and averaged <N x={meanAll} /> USD/MWh.{" "}
          {neg.length ? <>The {neg.length === 1 ? "one exception was" : "exceptions were"} {neg.map((m) => month(m.ts)).join(", ")}.</> : null}
        </p>
        <Months ms={ems} />
        <p className="mt-1 mb-3 text-xs text-muted">USD/MWh, real-time, each complete month. Cardinal above zero, green below; the axis is cut, and the month above it labeled.</p>
        <p className="mb-3">
          One month dwarfs the rest. In {month(big[0].ts)}, the month of Winter Storm Uri, ERCOT&apos;s load-weighted real-time price was <N x={uriLw} /> USD/MWh against
          a simple average of <N x={uriSm} />: a premium of <N x={uri} />, <N x={calc("ratio", uri, second)} /> times the next largest month,{" "}
          {month(big[1].ts)}&apos;s <N x={second} />. In the storm the dearest hours were also the hours of greatest need, so a load shaped like
          the grid&apos;s bought far more of its energy at the storm&apos;s prices than a flat load did, which bought the same amount every hour.
        </p>
        <p className="mb-3">
          Away from Uri, the premium is a summer story: the largest months fall in July, August and September, when the evening peak of air
          conditioning meets the hour solar output falls away. And it has shrunk. Counting each complete year, a megawatt shaped like ERCOT&apos;s load paid{" "}
          {y21 ? <><N x={y21.usd} /> USD more than a flat megawatt in 2021, </> : null}and <N x={lastY.usd} /> USD more in {lastY.y}. Over the
          latest twelve months held (<N x={n12} /> of them complete), the difference was <N x={usd12} /> USD per megawatt, a mean premium of{" "}
          <N x={mean12} /> USD/MWh. The warehouse does not say why; the same years saw ERCOT&apos;s battery fleet grow, and batteries sell into exactly
          the hours that make the premium.
        </p>
        <table className="w-full text-left text-sm tabular-nums">
          <thead><tr className="border-b border-rule text-xs text-muted"><th className="py-1">Year</th><th className="text-right">Mean premium, USD/MWh</th><th className="text-right">Grid-shaped over flat, USD per MW</th></tr></thead>
          <tbody>{yearly.map((x) => <tr key={x.y} className="border-b border-rule"><td className="py-1">{x.y}</td><td className="text-right"><N x={x.mean} /></td><td className="text-right"><N x={x.usd} /></td></tr>)}</tbody>
        </table>
        <p className="mt-1 text-xs text-muted">Complete years only. USD per MW: each month&apos;s premium times its hours, summed over the year.</p>
      </Section>

      <Section title="Where in the day it comes from">
        <p className="mb-3">
          The premium exists because prices and load peak together. In {month(pm)} (the days held; the month is in progress), ERCOT&apos;s mean real-time
          price was lowest at {ercotShape.loH}:00, <N x={ercotShape.lo} /> USD/MWh, when solar floods the grid, and highest at {ercotShape.hiH}:00,{" "}
          <N x={ercotShape.hi} />, after the sun has set and before the evening load falls: <N x={calc("ratio", ercotShape.hi, ercotShape.lo)} /> times as much. Each hub
          has its own shape, and its own dear hours.
        </p>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {shapes.map((s) => <Profile key={s.e} label={s.iso} cells={s.cells.map((c) => ({ h: Number(c.variable.slice(-2)), v: c.value }))} />)}
        </div>
        <p className="mt-1 mb-3 text-xs text-muted">Mean real-time price by local hour of the day, USD/MWh, {month(pm)}; each panel on its own scale; the dots mark the cheapest and dearest hour.</p>
        <table className="w-full text-left text-sm tabular-nums">
          <thead><tr className="border-b border-rule text-xs text-muted"><th className="py-1">ISO</th><th className="text-right">Cheapest hour</th><th className="text-right">USD/MWh</th><th className="text-right">Dearest hour</th><th className="text-right">USD/MWh</th><th className="text-right">Days</th></tr></thead>
          <tbody>{shapes.map((s) => (
            <tr key={s.e} className="border-b border-rule">
              <td className="py-1">{s.iso}</td><td className="text-right">{s.loH}:00</td><td className="text-right"><N x={s.lo} /></td>
              <td className="text-right">{s.hiH}:00</td><td className="text-right"><N x={s.hi} /></td><td className="text-right">{s.days ? <N x={s.days} /> : "n/a"}</td>
            </tr>
          ))}</tbody>
        </table>
        <p className="mt-3">
          The dear hours are few. A load that can move a few hours a day out of the evening, or a battery that fills at midday and empties at night,
          captures much of the premium without being flat at all: the{" "}
          <Link href="/play/battery">battery game</Link> plays exactly this spread on one real ERCOT day.
        </p>
      </Section>

      <Section title="Day-ahead or real-time">
        <p>
          Most of this report reads the real-time market, where ERCOT&apos;s history is longest, and the six-ISO comparison reads the day-ahead
          market, which every hub holds. The two premiums are close but not the same. In {month(latest)}, ERCOT&apos;s day-ahead premium was{" "}
          <N x={ercotDa} /> USD/MWh and its real-time premium <N x={ercotRt} /> over the hours held. Day-ahead prices are set the day before, on
          forecasts of load and of wind and sun; real-time prices settle what actually happened, so they carry the surprises: a forecast that missed the
          evening ramp, a plant that tripped. A buyer who hedges day-ahead locks in the day-ahead shape; one who floats in real time takes the
          surprises with it, and in a month like Uri&apos;s, the surprises are the premium.
        </p>
      </Section>

      <Section title="What it means for a flat load">
        <p className="mb-3">
          For a buyer at the hub, a flat load pays the simple average. The premium is the discount it enjoys against the grid&apos;s own average cost, and
          it is not small where the evening is dear: over the latest twelve months in ERCOT, <N x={usd12} /> USD per megawatt of load. For a
          datacenter of a few hundred megawatts, that is a line item, and it is earned by the shape alone, before any contract. The same arithmetic
          serves any load: take its own hourly profile, weight the hub&apos;s hourly prices by it, and compare the result with the simple average; the
          closer the profile is to flat, the closer the load pays to the simple average, and the more of the evening it avoids, the less it pays.
        </p>
        <p>
          Two cautions. First, the premium measured here is at the hub and in the energy market only: a real load pays its own node, plus capacity,
          transmission and ancillary charges that this table leaves out, and a flat load may pay a demand charge that a shaped one avoids. Second, the
          premium is not a law: Uri shows how far it can jump in a single month, and its recent shrinking shows it can fade as storage and solar
          reshape the day. A flat load is a bet that the evening stays dear.
        </p>
      </Section>

      <Section title="Data and method">
        <ul className="list-disc space-y-1 pl-5 text-sm">
          <li><code className="font-mono">cost_of_power_monthly</code>: per ISO main hub and month, the load-weighted and simple averages of the real-time and day-ahead price, and their hours. A month counts as complete when its hours equal the month&apos;s.</li>
          <li><code className="font-mono">cost_of_power_hourly_profile</code>: per hub and month, the mean real-time price at each local hour of the day.</li>
          <li>Hubs: CAISO SP15, ERCOT HB_HUBAVG, ISO-NE .H.INTERNAL_HUB, MISO Indiana Hub, NYISO N.Y.C., SPP SPPNORTH_HUB. PJM is not here: its prices are internal.</li>
          <li>Only ERCOT has a long history in the warehouse. Since session 49 the other five hubs reach back to September 2025 (<code className="font-mono">iso_hub_prices_history</code>), which gives the twelve-month view.</li>
        </ul>
        <Cite tables={[M, P]} note="The cost-of-power model (docs/methods/cost_of_power.md); statistics by site/lib/shapepremium.ts" />
      </Section>
    </article>
  );
}
