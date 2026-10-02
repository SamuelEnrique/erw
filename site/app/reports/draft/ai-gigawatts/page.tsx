import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { notFound } from "next/navigation";
import { Cite } from "@/components/Cite";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { series, type SeriesRow } from "@/lib/data";
import { shown } from "@/lib/format";

// Session 62: the flagship analysis, a draft, internal only. "Where the next gigawatts for AI can come from": one row of
// measures per ISO region (ai_power_regions, warehouse/derived/ai_power_regions.py; methods in
// docs/reports/ai_gigawatts_methods.md). Not in the nav, not indexed, gated by the internal token as
// /reports/draft/shape-premium: /reports/draft/ai-gigawatts?token=<INTERNAL_COSTS_TOKEN>, else 404. Every number is a row of
// ai_power_regions (series|...) or a ratio or difference of two (calc|...), and scripts/check-values.mjs recomputes each.
// The prose names regions from the data (the cheapest, the cleanest, the fastest), so it stays true when the table is
// rebuilt. Charts: plain SVG, Stanford palette (cardinal for the measure, Palo Alto green for the best region).
export const metadata: Metadata = { title: "Draft: where the next gigawatts for AI can come from", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

const T = "ai_power_regions";
const REGIONS: { id: string; name: string; hub?: string; ba: string }[] = [
  { id: "caiso", name: "CAISO", hub: "SP15", ba: "CISO" },
  { id: "ercot", name: "ERCOT", hub: "the hub average", ba: "ERCO" },
  { id: "isone", name: "ISO-NE", hub: "the internal hub", ba: "ISNE" },
  { id: "miso", name: "MISO", hub: "Indiana Hub", ba: "MISO" },
  { id: "nyiso", name: "NYISO", hub: "the New York City zone", ba: "NYIS" },
  { id: "pjm", name: "PJM", ba: "PJM" },
  { id: "spp", name: "SPP", hub: "SPP North", ba: "SWPP" },
];
const EVENTS: Record<string, string> = {
  uri_2021: "Winter Storm Uri, February 2021", elliott_2022: "Winter Storm Elliott, December 2022", caiso_heat_2020: "the August 2020 heat wave",
  caiso_heat_2022: "the September 2022 heat wave", ercot_heat_2023: "the summer 2023 heat",
};
type V = { v: number; k: string };
const tilde = (k: string) => k.replaceAll("|", "~");
const calc = (op: "ratio" | "diff" | "pct", a: V, b: V): V =>
  ({ v: op === "ratio" ? a.v / b.v : op === "diff" ? a.v - b.v : (a.v / b.v) * 100, k: `calc|${op}|${tilde(a.k)}|${tilde(b.k)}` });
const N = ({ x }: { x?: V }) => (x ? <Num check={x.k} raw={x.v}>{shown(x.v)}</Num> : <span className="text-muted">not held</span>);
const usdShort = (v: number) => {
  const t = (x: number) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
  if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  return v.toLocaleString("en-US");
};
const Usd = ({ x }: { x?: V }) => (x ? <span data-format="usd"><Num check={x.k} raw={x.v}>{usdShort(x.v)}</Num></span> : <span className="text-muted">not held</span>);

/** Horizontal bars, one measure per region; the best region in green, the rest cardinal. */
function Bars({ items, unit, best, fmt }: { items: { label: string; v: number }[]; unit: string; best: "low" | "high"; fmt?: (v: number) => string }) {
  const W = 640, row = 28, L = 80, R = 110, H = items.length * row + 24;
  const max = Math.max(...items.map((i) => Math.abs(i.v)), 1e-9);
  const x = (v: number) => L + (Math.max(0, v) / max) * (W - L - R);
  const bestV = best === "low" ? Math.min(...items.map((i) => i.v)) : Math.max(...items.map((i) => i.v));
  const f = fmt ?? shown;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-2xl" role="img" aria-label={`${unit} by region; the table holds the values`}>
      <line x1={L} x2={L} y1={4} y2={H - 20} stroke="var(--color-muted)" strokeWidth={1} />
      {items.map((it, i) => (
        <g key={it.label}>
          <title>{`${it.label}: ${f(it.v)} ${unit}`}</title>
          <text x={L - 8} y={i * row + 22} textAnchor="end" fontSize={12} fill="var(--color-ink)">{it.label}</text>
          <rect x={L} y={i * row + 10} width={Math.max(1, x(it.v) - L)} height={15} rx={2} fill={it.v === bestV ? "var(--color-down)" : "var(--color-accent)"} />
          <text x={x(it.v) + 6} y={i * row + 22} fontSize={12} fill="var(--color-muted)">{f(it.v)}</text>
        </g>
      ))}
      <text x={W - R} y={H - 4} textAnchor="end" fontSize={11} fill="var(--color-muted)">{unit}</text>
    </svg>
  );
}

export default async function AiGigawatts({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const token = typeof sp.token === "string" ? sp.token : "";
  const want = process.env.INTERNAL_COSTS_TOKEN ?? "";
  if (want.length < 24 || token !== want) notFound();

  const all = await series(T, {});
  const get = (r: string, v: string): V | undefined => {
    const row: SeriesRow | undefined = all.find((x) => x.entity === `iso:${r}` && x.variable === v);
    return row ? { v: row.value, k: `series|${T}|${row.entity}|${row.variable}|${row.ts_utc}` } : undefined;
  };
  const R = REGIONS.map((g) => ({
    ...g,
    rt: get(g.id, "flat_rt_price_usd_mwh"), da: get(g.id, "flat_da_price_usd_mwh"), cost: get(g.id, "flat_1gw_cost_usd"),
    ci: get(g.id, "carbon_intensity_kg_mwh"), co2: get(g.id, "flat_1gw_co2_t"), cdays: get(g.id, "carbon_days"),
    s200: get(g.id, "scarcity_hours_200"), s1000: get(g.id, "scarcity_hours_1000"), maxh: get(g.id, "max_rt_hour_usd_mwh"), seen: get(g.id, "rt_hours_seen"),
    emerg: get(g.id, "emergency_days"), ev: get(g.id, "event_largest_effect_pct"),
    lgw: get(g.id, "lbnl_active_mw"), lreq: get(g.id, "lbnl_active_requests"), yrs: get(g.id, "lbnl_median_years_to_cod"),
    ysample: get(g.id, "lbnl_cod_sample"), comp: get(g.id, "lbnl_completion_pct"), cohort: get(g.id, "lbnl_cohort_requests"),
    q: get(g.id, "queue_active_mw"), imp: get(g.id, "net_import_share_pct"), impd: get(g.id, "net_import_days_pct"),
    peak: get(g.id, "peak_import_share_pct"), pair: get(g.id, "pair_import_share_pct"), dem: get(g.id, "demand_mwh"),
    days: get(g.id, "interchange_days"), screened: get(g.id, "screened_pair_days"),
    evName: (() => { const f = all.find((x) => x.entity === `iso:${g.id}` && x.variable.startsWith("event_largest_is_")); return f ? EVENTS[f.variable.slice(17)] ?? f.variable.slice(17) : ""; })(),
  }));
  if (!R.some((r) => r.rt)) {
    return <div className="max-w-3xl"><h1 className="mb-3 text-3xl">Draft: where the next gigawatts for AI can come from</h1><p className="text-sm text-muted">The table {T} could not be read.</p></div>;
  }
  type Reg = (typeof R)[number];
  const by = (f: (r: Reg) => V | undefined, dir: "asc" | "desc") => R.filter((r) => f(r)).sort((a, b) => (dir === "asc" ? 1 : -1) * (f(a)!.v - f(b)!.v));
  const cheap = by((r) => r.cost, "asc"), clean = by((r) => r.ci, "asc"), calm = by((r) => r.s200, "asc"),
    fast = by((r) => r.yrs, "asc"), done = by((r) => r.comp, "desc"), self = by((r) => r.imp, "asc"), big = by((r) => r.lgw, "desc");
  const c0 = cheap[0], c1 = cheap.at(-1)!, ci0 = clean[0], ci1 = clean.at(-1)!, f0 = fast[0], f1 = fast.at(-1)!;
  const costRatio = calc("ratio", c1.cost!, c0.cost!), costDiff = calc("diff", c1.cost!, c0.cost!);
  const co2Ratio = calc("ratio", ci1.co2!, ci0.co2!), co2Diff = calc("diff", ci1.co2!, ci0.co2!);
  const yrsDiff = calc("diff", f1.yrs!, f0.yrs!);
  const imp0 = self[0], imp1 = self.at(-1)!;
  // regions in the better half on cost, carbon, calm, speed and self-sufficiency: how often each leads
  const half = (list: Reg[], r: Reg) => list.indexOf(r) >= 0 && list.indexOf(r) < Math.ceil(list.length / 2);
  const ORD = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh"];
  const rank = (list: Reg[], r: Reg) => (list.indexOf(r) >= 0 ? (list.indexOf(r) === list.length - 1 ? "last" : ORD[list.indexOf(r)]) : "not ranked");
  const tally = R.map((r) => ({ r, n: [cheap, clean, calm, fast, self].filter((l) => half(l, r)).length, of: [cheap, clean, calm, fast, self].filter((l) => l.includes(r)).length }))
    .sort((a, b) => b.n - a.n || a.r.name.localeCompare(b.r.name));

  return (
    <article className="max-w-4xl">
      <p className="mb-1 text-xs text-muted">Draft, internal. Not in the navigation, not published. <Link href="/data/methods/cost_of_power">Cost-of-power method</Link></p>
      <h1 className="mb-2 text-3xl">Where the next gigawatts for AI can come from</h1>
      <p className="mb-4 text-sm text-muted">
        Energy Research Warehouse (ERW), session 62. Seven U.S. ISO regions, September 2025 to August 2026, measured the same way: what a flat 1 GW
        load would pay for energy, how much carbon it would carry, how stressed the grid is, how long new supply takes to connect, and how much the
        region leans on its neighbors. Every number below is a row of the table {T}, read from Supabase with its check key.
      </p>

      <Section title="Five findings">
        <ol className="max-w-3xl list-decimal space-y-2 pl-5 text-sm">
          <li>
            <strong>Energy cost differs by a factor of <N x={costRatio} />.</strong> At real-time hub prices, a flat 1 GW would have paid <Usd x={c0.cost} /> USD a year
            in {c0.name}, the cheapest region, and <Usd x={c1.cost} /> USD in {c1.name}, the dearest: <Usd x={costDiff} /> USD more, for wholesale energy alone.
          </li>
          <li>
            <strong>Carbon differs {co2Ratio.v > costRatio.v ? "more" : "less"} than cost.</strong> The same gigawatt would carry <N x={ci0.co2} /> tonnes of CO2 a year in {ci0.name} and <N x={ci1.co2} /> in{" "}
            {ci1.name}, <N x={co2Ratio} /> times as much (<N x={co2Diff} /> tonnes more).{" "}
            {c0.id === ci0.id
              ? <>{c0.name} is both the cheapest and the cleanest; it is also the {rank(fast, c0)} of {fast.length} to connect new supply.</>
              : <>The cheapest region, {c0.name}, is the {rank(clean, c0)} of {clean.length} on carbon.</>}{" "}
            The three cheapest are {cheap.slice(0, 3).map((r) => r.name).join(", ")}; the three cleanest {clean.slice(0, 3).map((r) => r.name).join(", ")}.
          </li>
          <li>
            <strong>New supply connects fastest in {f0.name}.</strong> Requests that came online in 2018 to 2025 took a median <N x={f0.yrs} /> years from request
            to operation there, against <N x={f1.yrs} /> in {f1.name}, <N x={yrsDiff} /> years longer. {done[0].name} completed the largest share of its
            2000 to 2019 requests, <N x={done[0].comp} /> percent; {done.at(-1)!.name} the smallest, <N x={done.at(-1)!.comp} /> percent.
          </li>
          <li>
            <strong>The queues are not the bottleneck in size.</strong> {big[0].name} alone held <N x={big[0].lgw} /> MW of active requests at the end of 2025,
            and {big[1].name} <N x={big[1].lgw} /> MW. What matters is how little of it gets built, and how long it takes.
          </li>
          <li>
            <strong>Some regions lean on their neighbors.</strong> Over the year, {imp1.name} imported a net <N x={imp1.imp} /> percent of its demand (EIA&apos;s own
            balance) and was a net importer on <N x={imp1.impd} /> percent of its complete days. {imp0.name} is at the other end: <N x={imp0.imp} /> percent (a negative
            share is a net exporter). A new gigawatt in an importing region adds to that reliance unless new supply comes with it.
          </li>
        </ol>
      </Section>

      <Section title="1. The question, and the unit">
        <p className="mb-2 max-w-3xl text-sm">
          A large AI campus is, to the grid, a steady load: hundreds of megawatts to a gigawatt and more, nearly flat around the clock. Where it lands decides
          what it pays for energy, what it emits, whether its evenings are tight, and how soon new generation can be built to serve it. This draft measures the
          seven ISO regions that run U.S. wholesale markets the same way, over the same year (September 2025 to August 2026), for the same load: a flat 1 GW,
          8,760 GWh a year. It does not rank sites: a site sits inside a utility, behind substations, under local rules. It asks which regions start from
          a better place on five things the warehouse holds.
        </p>
        <p className="max-w-3xl text-sm">
          PJM, the largest region by load, is in the carbon, interconnection and import measures but not in cost or price stress: the warehouse licenses PJM&apos;s
          prices for internal use only and does not hold its hub prices. Nothing is estimated in its place.
        </p>
      </Section>

      <Section title="2. Cost: what a flat gigawatt pays for energy" aside={T}>
        <Bars items={cheap.map((r) => ({ label: r.name, v: r.cost!.v / 1e6 }))} unit="USD million a year" best="low" fmt={(v) => v.toFixed(1)} />
        <div className="mt-3 overflow-x-auto">
          <table className="text-sm">
            <thead><tr className="border-b border-ink text-left text-xs text-muted"><th className="py-1 pr-3">Region</th><th className="py-1 pr-3">Hub</th><th className="py-1 pr-3 text-right">Real time, USD/MWh</th><th className="py-1 pr-3 text-right">Day-ahead, USD/MWh</th><th className="py-1 pr-3 text-right">A flat 1 GW, USD a year</th></tr></thead>
            <tbody>
              {cheap.map((r) => (
                <tr key={r.id} className="border-b border-rule"><td className="py-1 pr-3">{r.name}</td><td className="py-1 pr-3 text-xs">{r.hub}</td>
                  <td className="py-1 pr-3 text-right tabular-nums"><N x={r.rt} /></td><td className="py-1 pr-3 text-right tabular-nums"><N x={r.da} /></td>
                  <td className="py-1 pr-3 text-right tabular-nums"><Usd x={r.cost} /></td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 max-w-3xl text-sm">
          A flat load pays the plain average of the hub&apos;s hourly prices, because it buys the same MW in every hour. Over the year that average ran from{" "}
          <N x={c0.rt} /> USD/MWh in {c0.name} to <N x={c1.rt} /> USD/MWh in {c1.name}. The {c1.name} figure is {c1.id === "nyiso" ? "the New York City zone, the dearest part of NYISO; upstate zones are cheaper" : `at ${c1.hub}`}.
          Day-ahead prices ran above real time in every region but {R.filter((r) => r.da && r.rt && r.da.v < r.rt.v).map((r) => r.name).join(", ") || "none"}: a buyer
          who fixes the day before pays a small premium for certainty.
        </p>
        <p className="mt-2 max-w-3xl text-sm">
          These are energy prices at a hub, not a delivered bill. Capacity charges (large in PJM, ISO-NE, NYISO and MISO), transmission, distribution,
          ancillary services, taxes and the hedges a real buyer signs all come on top, and they differ by region in ways this table does not hold.
        </p>
      </Section>

      <Section title="3. Carbon: what a flat gigawatt would emit" aside={T}>
        <Bars items={clean.map((r) => ({ label: r.name, v: r.ci!.v }))} unit="kg CO2 per MWh" best="low" fmt={(v) => v.toFixed(0)} />
        <div className="mt-3 overflow-x-auto">
          <table className="text-sm">
            <thead><tr className="border-b border-ink text-left text-xs text-muted"><th className="py-1 pr-3">Region</th><th className="py-1 pr-3 text-right">kg CO2/MWh</th><th className="py-1 pr-3 text-right">A flat 1 GW, t CO2 a year</th><th className="py-1 pr-3 text-right">Days held</th></tr></thead>
            <tbody>{clean.map((r) => <tr key={r.id} className="border-b border-rule"><td className="py-1 pr-3">{r.name}</td><td className="py-1 pr-3 text-right tabular-nums"><N x={r.ci} /></td><td className="py-1 pr-3 text-right tabular-nums"><N x={r.co2} /></td><td className="py-1 pr-3 text-right tabular-nums"><N x={r.cdays} /></td></tr>)}</tbody>
          </table>
        </div>
        <p className="mt-3 max-w-3xl text-sm">
          The intensity is consumption-based: the CO2 of the generation each region actually used, imports included, per MWh of its demand, averaged over the
          year&apos;s days, from <N x={ci0.ci} /> kg/MWh in {ci0.name} to <N x={ci1.ci} /> kg/MWh in {ci1.name}, which still burns more coal and gas in its mix.
          A new load is served at the margin, by whatever plant runs next, which is usually gas almost everywhere: the average is where a region starts,
          not the CO2 of the next MWh. The gap between regions is still the largest of the five measures.
        </p>
      </Section>

      <Section title="4. Stress: how often the grid runs short" aside={T}>
        <div className="mt-1 overflow-x-auto">
          <table className="text-sm">
            <thead><tr className="border-b border-ink text-left text-xs text-muted"><th className="py-1 pr-3">Region</th><th className="py-1 pr-3 text-right">Hours at or above USD 200/MWh</th><th className="py-1 pr-3 text-right">At or above 1,000</th><th className="py-1 pr-3 text-right">Highest hour, USD/MWh</th><th className="py-1 pr-3 text-right">Hours held</th><th className="py-1 pr-3 text-right">Largest studied event, percent of normal demand</th></tr></thead>
            <tbody>
              {R.map((r) => (
                <tr key={r.id} className="border-b border-rule"><td className="py-1 pr-3">{r.name}</td>
                  <td className="py-1 pr-3 text-right tabular-nums"><N x={r.s200} /></td><td className="py-1 pr-3 text-right tabular-nums"><N x={r.s1000} /></td>
                  <td className="py-1 pr-3 text-right tabular-nums"><N x={r.maxh} /></td><td className="py-1 pr-3 text-right tabular-nums"><N x={r.seen} /></td>
                  <td className="py-1 pr-3 text-right tabular-nums"><N x={r.ev} /> <span className="text-xs text-muted">{r.evName}</span></td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 max-w-3xl text-sm">
          Scarcity shows in the price. {calm[0].name} had the fewest hours at or above USD 200/MWh, <N x={calm[0].s200} />; {calm.at(-1)!.name} the most, <N x={calm.at(-1)!.s200} />.
          Hours above USD 1,000 were rare everywhere: {by((r) => r.s1000, "desc")[0].name} had the most, <N x={by((r) => r.s1000, "desc")[0].s1000} />. A steady load in a
          region with many dear hours either pays them or hedges them; it also adds to the demand in the hours that are already tight.
        </p>
        <p className="mt-2 max-w-3xl text-sm">
          For a flat load the dear hours are not optional. A factory or a campus that runs every hour buys the scarcity hours with the rest, and a region
          with hundreds of them a year asks either for a hedge (a fixed-price contract, which prices the risk in) or for flexibility: a campus that can
          shift or shed part of its load in those hours, or carry batteries, pays less and eases the grid at the same time. The count of hours above
          USD 200/MWh is therefore a rough guide to how much a buyer would gain from being able to step back when the grid is short.
        </p>
        <p className="mt-2 max-w-3xl text-sm">
          Grid emergencies are held for CAISO only: <N x={R.find((r) => r.id === "caiso")!.emerg} /> days with an ISO-wide Flex Alert or emergency from July 2018 to
          April 2025. The event studies add the scale of the worst weather the warehouse has measured: the largest effect on daily demand was{" "}
          <N x={by((r) => r.ev, "desc")[0].ev} /> percent above normal, in {by((r) => r.ev, "desc")[0].name} during {by((r) => r.ev, "desc")[0].evName}, after
          temperature is accounted for where the study holds it. A region that runs short in its extremes is where a new
          flat load matters most, and where it should bring its own flexibility or supply.
        </p>
      </Section>

      <Section title="5. Connection: how fast new supply gets built" aside={`${T}; lbnl_interconnection_queue`}>
        <Bars items={fast.map((r) => ({ label: r.name, v: r.yrs!.v }))} unit="median years, request to operation" best="low" fmt={(v) => v.toFixed(1)} />
        <div className="mt-3 overflow-x-auto">
          <table className="text-sm">
            <thead><tr className="border-b border-ink text-left text-xs text-muted"><th className="py-1 pr-3">Region</th><th className="py-1 pr-3 text-right">Active, MW (Berkeley Lab, end 2025)</th><th className="py-1 pr-3 text-right">Requests</th><th className="py-1 pr-3 text-right">Median years to operation</th><th className="py-1 pr-3 text-right">Sample</th><th className="py-1 pr-3 text-right">Completion, percent of 2000 to 2019 requests</th><th className="py-1 pr-3 text-right">Active, MW (ISO queue, Sept 2026)</th></tr></thead>
            <tbody>
              {big.map((r) => (
                <tr key={r.id} className="border-b border-rule"><td className="py-1 pr-3">{r.name}</td>
                  <td className="py-1 pr-3 text-right tabular-nums"><N x={r.lgw} /></td><td className="py-1 pr-3 text-right tabular-nums"><N x={r.lreq} /></td>
                  <td className="py-1 pr-3 text-right tabular-nums"><N x={r.yrs} /></td><td className="py-1 pr-3 text-right tabular-nums"><N x={r.ysample} /></td>
                  <td className="py-1 pr-3 text-right tabular-nums"><N x={r.comp} /></td><td className="py-1 pr-3 text-right tabular-nums"><N x={r.q} /></td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 max-w-3xl text-sm">
          Berkeley Lab&apos;s Queued Up data hold every generation and storage request in the seven regions through 2025. {f0.name} turned requests into operating
          plants fastest, a median <N x={f0.yrs} /> years; {f1.name} slowest, <N x={f1.yrs} /> years. Most requests never get built: of the requests made from 2000 to
          2019, {done[0].name} completed <N x={done[0].comp} /> percent and {done.at(-1)!.name} <N x={done.at(-1)!.comp} /> percent. ISO-NE has no median here: Berkeley Lab
          gives no online dates for its completed requests.
        </p>
        <p className="mt-2 max-w-3xl text-sm">
          The ISOs&apos; own queues, retrieved in September 2026, show the same order of size as Berkeley Lab&apos;s end-2025 counts, and differ where requests were added,
          withdrawn or counted differently since. A queue is a list of hopes. The completion rate and the time to connect are the better guides to how soon a
          region could add the supply a new gigawatt of load needs. These are times for generators; a load&apos;s own connection runs through its utility and is
          not in these data.
        </p>
        <p className="mt-2 max-w-3xl text-sm">
          The time to connect matters twice for a new campus. It sets how soon the generation the campus contracts for can be built, and in most regions it
          also sets how soon the transmission upgrades that new supply triggers get done. Where requests come online in a median <N x={f0.yrs} /> years
          ({f0.name}), a buyer can match new load with new supply within one planning cycle; where they take <N x={f1.yrs} /> ({f1.name}), the buyer relies on
          existing plants, and on the grid&apos;s margin, for most of that time.
        </p>
      </Section>

      <Section title="6. Imports: how much a region leans on its neighbors" aside={`${T}; eia930_daily_interchange`}>
        <Bars items={[...self].reverse().map((r) => ({ label: r.name, v: Math.max(0, r.imp!.v) }))} unit="percent of demand imported, net (exporters at 0)" best="low" fmt={(v) => v.toFixed(1)} />
        <div className="mt-3 overflow-x-auto">
          <table className="text-sm">
            <thead><tr className="border-b border-ink text-left text-xs text-muted"><th className="py-1 pr-3">Region</th><th className="py-1 pr-3 text-right">Net imports, percent of demand (EIA&apos;s balance)</th><th className="py-1 pr-3 text-right">Pair sums, percent</th><th className="py-1 pr-3 text-right">Days a net importer, percent</th><th className="py-1 pr-3 text-right">Ten peak days, percent imported</th><th className="py-1 pr-3 text-right">Complete days</th><th className="py-1 pr-3 text-right">Pair-days screened out</th><th className="py-1 pr-3 text-right">Demand, MWh</th></tr></thead>
            <tbody>
              {self.map((r) => (
                <tr key={r.id} className="border-b border-rule"><td className="py-1 pr-3">{r.name}</td>
                  <td className="py-1 pr-3 text-right tabular-nums"><N x={r.imp} /></td><td className="py-1 pr-3 text-right tabular-nums"><N x={r.pair} /></td>
                  <td className="py-1 pr-3 text-right tabular-nums"><N x={r.impd} /></td><td className="py-1 pr-3 text-right tabular-nums"><N x={r.peak} /></td>
                  <td className="py-1 pr-3 text-right tabular-nums"><N x={r.days} /></td><td className="py-1 pr-3 text-right tabular-nums"><N x={r.screened} /></td>
                  <td className="py-1 pr-3 text-right tabular-nums"><N x={r.dem} /></td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 max-w-3xl text-sm">
          The headline share is EIA&apos;s own balance for each region: demand less net generation, over demand, for the year&apos;s complete hours. {imp1.name} imported
          the most, a net <N x={imp1.imp} /> percent of its demand; {imp0.name} exported the most, <N x={imp0.imp} /> percent. The other columns come from the
          interchange EIA reports with each neighbor, summed per day, on complete days only: a day counts when every regular neighbor reported it.
          EIA&apos;s daily interchange is missing for some days of the year in every region (the complete-days column says how many remain), and a few pair-days
          are impossible (one day SPP and MISO reported more energy across their tie than SPP uses in a day); those are left out and counted.
        </p>
        <p className="mt-2 max-w-3xl text-sm">
          Where the pair sums and the balance agree, the data close. Where they do not, the region&apos;s reported interchange and its generation tell different
          stories: in {[...R].filter((r) => r.imp && r.pair).sort((a, b) => Math.abs(b.imp!.v - b.pair!.v) - Math.abs(a.imp!.v - a.pair!.v))[0].name} the balance says{" "}
          <N x={[...R].filter((r) => r.imp && r.pair).sort((a, b) => Math.abs(b.imp!.v - b.pair!.v) - Math.abs(a.imp!.v - a.pair!.v))[0].imp} /> percent and the pairs{" "}
          <N x={[...R].filter((r) => r.imp && r.pair).sort((a, b) => Math.abs(b.imp!.v - b.pair!.v) - Math.abs(a.imp!.v - a.pair!.v))[0].pair} /> percent, and the gap is EIA&apos;s
          data, not this report&apos;s. The peak-day share uses the pair sums: on a region&apos;s ten highest-demand complete days, how much of its demand came from
          neighbors.
        </p>
      </Section>

      <Section title="7. Putting it together">
        <p className="mb-2 max-w-3xl text-sm">
          No single number says where a gigawatt should go: a buyer who cares most about cost, carbon or speed would choose differently. The table counts, for
          each region, how many of the five measures (cost, carbon, scarcity hours, time to connect, imports) put it in the better half of the regions held.
          It is not a score: the measures are not weighted, and a region missing a measure (PJM&apos;s cost and stress, ISO-NE&apos;s time to connect) is counted only on
          what it has.
        </p>
        <div className="overflow-x-auto">
          <table className="text-sm">
            <thead><tr className="border-b border-ink text-left text-xs text-muted"><th className="py-1 pr-3">Region</th><th className="py-1 pr-3 text-right">Better half on</th><th className="py-1 pr-3 text-right">Of measures held</th></tr></thead>
            <tbody>{tally.map((t) => <tr key={t.r.id} className="border-b border-rule"><td className="py-1 pr-3">{t.r.name}</td><td className="py-1 pr-3 text-right tabular-nums">{t.n}</td><td className="py-1 pr-3 text-right tabular-nums">{t.of}</td></tr>)}</tbody>
          </table>
        </div>
        <p className="mt-3 max-w-3xl text-sm">
          {tally[0].r.name} is in the better half on {tally[0].n} of its {tally[0].of} measures, the most of any region. The tension is in the data: the cleanest
          region, {ci0.name}, is the {rank(fast, ci0)} of {fast.length} to connect new supply, and the fastest, {f0.name}, is the {rank(clean, f0)} of {clean.length} on
          carbon. A campus that wants all three brings its own: a contract for new clean supply where connection is fast, or flexibility that lets it avoid the tight
          hours where they are many.
        </p>
      </Section>

      <Section title="8. Reading the table three ways">
        <p className="mb-3 max-w-3xl text-sm">
          A developer, a utility planner and a policymaker would read the same table in different orders. Here is what each order picks, with the trade it
          brings along. Each line is the region&apos;s own row; nothing is weighted or combined.
        </p>
        {([
          ["If cost comes first", cheap, "cheapest"], ["If carbon comes first", clean, "cleanest"], ["If speed comes first", fast, "fastest to connect new supply"],
        ] as [string, Reg[], string][]).map(([title, list, what]) => (
          <div key={title} className="mb-3 max-w-3xl">
            <h3 className="mb-1 text-base">{title}</h3>
            <p className="mb-1 text-sm">The three {what}, and what each brings with it:</p>
            <ul className="list-disc space-y-1 pl-5 text-sm">
              {list.slice(0, 3).map((r) => (
                <li key={r.id}>
                  <strong>{r.name}</strong>: a flat 1 GW at <Usd x={r.cost} /> USD a year for energy{r.cost ? "" : " (its prices are not held)"}; <N x={r.ci} /> kg CO2/MWh;{" "}
                  {r.yrs ? <>new supply online in a median <N x={r.yrs} /> years</> : <>no median time to connect held</>}; <N x={r.s200} /> hours at or above USD 200/MWh;
                  net imports <N x={r.imp} /> percent of demand.
                </li>
              ))}
            </ul>
          </div>
        ))}
        <p className="max-w-3xl text-sm">
          {cheap[0].id === clean[0].id && clean[0].id === fast[0].id ? `${cheap[0].name} is first in all three orders.` : "No region is first in all three orders."} The
          picks differ by years of waiting or by millions of tonnes of CO2 a year. That is the case for a buyer bringing its own supply, storage or
          flexibility: it can choose the region for one measure and buy its way out of the others.
        </p>
      </Section>

      <Section title="9. What this cannot say">
        <ul className="max-w-3xl list-disc space-y-1 pl-5 text-sm">
          <li><strong>Permitting and local approval are out of scope.</strong> Land, zoning, water, community consent and the time a utility takes to connect a
            large load are what most often decide a site, and none of them is in these data.</li>
          <li><strong>Cost is wholesale energy at a hub.</strong> Capacity, transmission, distribution, ancillary services, taxes and hedges are left out; they can
            double a delivered price and differ more by region than energy does.</li>
          <li><strong>One year.</strong> 2025 to 2026&apos;s weather and gas prices shaped its prices and scarcity hours; another year would rank some regions differently.</li>
          <li><strong>Averages, not margins.</strong> The carbon of the next MWh, and the price of the hours a new load would add, are not the year&apos;s averages.</li>
          <li><strong>Queues and connection times are for generators.</strong> They say how fast a region adds supply, not how fast a data center gets its wires.</li>
          <li><strong>Regions are large.</strong> A region&apos;s hub, its average intensity and its net imports hide differences within it, across zones and utilities.</li>
          <li><strong>PJM&apos;s cost and price stress are not here,</strong> because its prices are licensed for internal use only and its hub prices are not held.</li>
        </ul>
      </Section>

      <Section title="Methods appendix">
        <p className="mb-2 max-w-3xl text-sm">
          The table is <code>{T}</code>, built by <code>warehouse/derived/ai_power_regions.py</code>; the measures, the hubs, the windows and the sources are in{" "}
          <code>docs/reports/ai_gigawatts_methods.md</code>. In short:
        </p>
        <ul className="max-w-3xl list-disc space-y-1 pl-5 text-sm">
          <li><strong>Cost</strong>: cost_of_power_monthly&apos;s real-time and day-ahead simple means, weighted by the hours priced, over the twelve months; a flat 1 GW is
            that price times 8,760,000 MWh.</li>
          <li><strong>Carbon</strong>: carbon_intensity_daily&apos;s consumption-based intensity, the mean over the days held; times 8,760,000 MWh for the tonnes.</li>
          <li><strong>Stress</strong>: hourly means of the hub&apos;s real-time prices (iso_hub_prices_history; ERCOT ercot_all_hub_prices_history), hours at or above USD
            200 and 1,000/MWh; CAISO&apos;s emergency days as the Flex Alert scorecard reads caiso_grid_emergencies; the largest pooled effect of a studied event
            (event_study_estimates, temperature-controlled where held).</li>
          <li><strong>Connection</strong>: Berkeley Lab and GridTracker&apos;s Queued Up 2026 data file (lbnl_interconnection_queue, CC BY 4.0): active requests at the
            end of 2025, the median years from request to operation for requests online in 2018 to 2025, the share of 2000 to 2019 requests completed; and
            each ISO&apos;s own queue (September 2026).</li>
          <li><strong>Imports</strong>: the headline is EIA&apos;s balance, demand less net generation over demand, from the region&apos;s EIA-930 workbook. The per-day
            measures sum EIA-930 daily interchange for every pair (eia930_daily_interchange, Eastern days, 2019 on) on complete days, with impossible pair-days
            (further than ten median absolute deviations from the pair&apos;s median) left out.</li>
        </ul>
      </Section>
      <Cite tables={[T, "cost_of_power_monthly", "carbon_intensity_daily", "lbnl_interconnection_queue", "eia930_daily_interchange", "event_study_estimates"]}
        note="Lawrence Berkeley National Laboratory and GridTracker, Queued Up (CC BY 4.0); U.S. EIA, Form EIA-930; the ISOs' public price and queue data" />
    </article>
  );
}
