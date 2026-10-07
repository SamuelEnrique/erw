import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Cite } from "@/components/Cite";
import { LineChart } from "@/components/LineChart";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { cells, cheapPrice, DEFAULTS, energy, flatPrice, type Cell } from "@/lib/cost";
import { series, type SeriesRow } from "@/lib/data";
import { shown } from "@/lib/format";
import { attempt } from "@/lib/supabase";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";
import { Calculator, CostCarbon, HeatGrid, RankBars } from "./charts";
import { CaisoBreakNote } from "@/components/CaisoBreakNote";  // session 73

// Session 37: the cost-of-power model v0 (platform tool 16), market-based. Every number is a row of the
// cost_of_power_* tables (derived: docs/methods/cost_of_power.md) or arithmetic on them with the calculator's
// labelled assumptions; the defaults are computed here and checked by scripts/check-values.mjs (keys cop|...).
// Session 138: this is what the tab showed until then, whole, as the view "Grid by grid" of the one page
// (/cost-of-power?view=grids); the page's first view is the reader's own load (page.tsx). Its charts and tables are
// as they were. What it said about method on its face (what is and is not in the figures, how load-weighted, simple
// mean and shape premium are defined, the calculator's assumptions) is in the Method note, with a short hover here.

const M = "cost_of_power_monthly", P = "cost_of_power_hourly_profile", C = "cost_of_power_carbon";
const METHOD = "/data/methods/cost_of_power";
const ISO: Record<string, { name: string; hub: string; grid: string }> = {
  ercot: { name: "ERCOT", hub: "HB_HUBAVG", grid: "/grid/ercot" },
  caiso: { name: "CAISO", hub: "SP15", grid: "/grid/caiso" },
  isone: { name: "ISO-NE", hub: "Internal Hub", grid: "/grid/isone" },
  miso: { name: "MISO", hub: "Indiana Hub", grid: "/grid/miso" },
  nyiso: { name: "NYISO", hub: "N.Y.C. (zone J)", grid: "/grid/nyiso" },
  spp: { name: "SPP", hub: "SPP North Hub", grid: "/grid/spp" },
};
const { mw: MW, loadFactor: LF, days: DAYS, share: SHARE } = DEFAULTS;

function Tier() {
  return (
    <Link href="/data/standard" title={TIER_TITLE.derived} className="ml-1 rounded border border-rule px-1 text-[10px] uppercase tracking-wide text-muted no-underline">
      {TIER_LABEL.derived}
    </Link>
  );
}

const N = ({ t, r }: { t: string; r?: SeriesRow }) =>
  r ? <Num check={`series|${t}|${r.entity}|${r.variable}|${r.ts_utc}`} raw={r.value}>{shown(r.value)}</Num> : <span className="text-muted">not held</span>;
const month = (ts: string) => ts.slice(0, 7);
const isoOf = (entity: string) => entity.split(":")[0];

/** US dollars, short, as scripts/check-values.mjs formats data-format usd. */
function usdShort(v: number) {
  const t = (x: number) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
  if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  return v.toLocaleString("en-US");
}
const Usd = ({ check, v }: { check: string; v: number }) => (
  <span data-format="usd"><Num check={check} raw={v}>{usdShort(v)}</Num></span>
);

export async function GridsView() {
  const got = await attempt(async () => {
    const [monthly, profile, carbon] = await Promise.all([series(M, {}), series(P, {}), series(C, {})]);
    return { monthly, profile, carbon };
  });
  const d = got.ok ? got.data : { monthly: [], profile: [], carbon: [] };
  const find = (rows: SeriesRow[], entity: string, variable: string, m: string) =>
    rows.find((r) => r.entity === entity && r.variable === variable && month(r.ts_utc) === m);
  // session 49: CAISO's NP15 is in the table for PG&E's bill (/learn/bill); the ISO comparison keeps each ISO's main hub
  const entities = [...new Set(d.monthly.map((r) => r.entity))].filter((e) => e !== "caiso:TH_NP15_GEN-APND")
    .sort((a, b) => Object.keys(ISO).indexOf(isoOf(a)) - Object.keys(ISO).indexOf(isoOf(b)));
  const monthsOf = (e: string) => new Set(d.monthly.filter((r) => r.entity === e && r.variable === "rt_load_weighted").map((r) => month(r.ts_utc)));
  // the ranked month (session 49, now that iso_hub_prices_history holds a year of every hub): the latest month complete
  // for every ISO (real-time hours equal to the month's); else, since the ISOs' own gap days leave few months complete at
  // every hub, the latest month in which every hub holds at least NEAR of its hours, labelled with the hours held; else,
  // as before, the latest month every ISO holds hours for
  const NEAR = 0.9;
  const shareOf = (e: string, m: string) => {
    const h = find(d.monthly, e, "rt_hours", m), hm = find(d.monthly, e, "hours_in_month", m);
    return h && hm ? h.value / hm.value : 0;
  };
  const held = entities.length ? [...monthsOf(entities[0])].filter((m) => entities.every((e) => monthsOf(e).has(m))).sort() : [];
  const back = [...held].reverse();
  const completeM = back.find((m) => entities.every((e) => shareOf(e, m) === 1));
  const nearM = back.find((m) => entities.every((e) => shareOf(e, m) >= NEAR));
  const common = completeM ?? nearM ?? held.at(-1);
  const rule = completeM ? "complete" : nearM ? "near" : "held";
  const rank = common ? entities.map((e) => ({
    e, lw: find(d.monthly, e, "rt_load_weighted", common), sm: find(d.monthly, e, "rt_simple_mean", common),
    sp: find(d.monthly, e, "rt_shape_premium", common), h: find(d.monthly, e, "rt_hours", common), hm: find(d.monthly, e, "hours_in_month", common),
  })).sort((a, b) => (b.lw?.value ?? 0) - (a.lw?.value ?? 0)) : [];
  const allComplete = rank.every((r) => r.h && r.hm && r.h.value === r.hm.value);

  // ERCOT since 2018
  const E = "ercot:HB_HUBAVG";
  const ercot = (v: string) => d.monthly.filter((r) => r.entity === E && r.variable === v).sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  const pts = (v: string) => ercot(v).map((r) => ({ t: Date.parse(`${month(r.ts_utc)}-01T00:00:00Z`) / 1000, v: r.value }));
  const ercotComplete = ercot("rt_hours").filter((h) => find(d.monthly, E, "hours_in_month", month(h.ts_utc))?.value === h.value).map((h) => month(h.ts_utc));
  const lastFull = ercotComplete.at(-1);
  const eLw = lastFull ? find(d.monthly, E, "rt_load_weighted", lastFull) : undefined;
  const eSp = lastFull ? find(d.monthly, E, "rt_shape_premium", lastFull) : undefined;
  const eTop = ercot("rt_load_weighted").reduce<SeriesRow | undefined>((a, r) => (!a || r.value > a.value ? r : a), undefined);

  // the hour-of-day profiles
  const profiles = entities.map((e) => {
    const cs = cells(d.profile, e);
    const last = [...new Set(cs.map((c) => c.month))].sort().pop();
    const lastCells = cs.filter((c) => c.month === last);
    const lo = lastCells.reduce<Cell | undefined>((a, c) => (!a || c.price < a.price ? c : a), undefined);
    const hi = lastCells.reduce<Cell | undefined>((a, c) => (!a || c.price > a.price ? c : a), undefined);
    const row = (c?: Cell) => (c ? find(d.profile, e, `rt_mean_h${String(c.hour).padStart(2, "0")}`, c.month) : undefined);
    return { e, cs, last, lo: row(lo), hi: row(hi), loHour: lo?.hour, hiHour: hi?.hour };
  });

  // cost against carbon: the latest month every ISO holds both
  const carbonMonths = (e: string) => new Set(d.carbon.filter((r) => r.entity === e && r.variable === "intensity_generation").map((r) => month(r.ts_utc)));
  const cm = entities.length ? [...carbonMonths(entities[0])].filter((m) => entities.every((e) => carbonMonths(e).has(m) && find(d.carbon, e, "rt_load_weighted", m))).sort().pop() : undefined;
  const cc = cm ? entities.map((e) => ({ e, price: find(d.carbon, e, "rt_load_weighted", cm), ci: find(d.carbon, e, "intensity_generation", cm) })) : [];

  // the calculator's defaults
  const calc = entities.map((e) => {
    // session 49: on the ranked month (the latest complete month every ISO holds)
    const f = flatPrice(d.monthly, e, common ? [common] : undefined);
    const c80 = cheapPrice(cells(d.profile, e).filter((c) => !common || c.month === common), SHARE);
    return { e, flat: f.price, months: f.months, c80 };
  });
  const eFlat = energy(MW, LF, DAYS), e80 = energy(MW, LF, DAYS, SHARE);
  const span = (ms: string[]) => (ms.length ? (ms.length === 1 ? ms[0] : `${ms.at(-1)} to ${ms[0]}`) : "");

  return (
    <>
      <CaisoBreakNote />
      {!got.ok || !d.monthly.length ? (
        <NoData what="the cost of power" reason={got.ok ? `${M} returned no rows` : got.reason} />
      ) : (
        <>
          <Section title={`Load-weighted real-time price by ISO, ${common ?? ""}`} aside={<Tier />}>
            <RankBars bars={rank.filter((r) => r.lw).map((r) => ({ name: ISO[isoOf(r.e)].name, value: r.lw!.value, partial: !(r.h && r.hm && r.h.value === r.hm.value) }))}
              label={`Load-weighted real-time price at each ISO's main hub in ${common}, USD/MWh`} />
            <p className="mb-2 text-sm text-muted">
              {allComplete ? `${common} is complete for every ISO.` : <span className="cursor-help border-b border-dotted border-muted" title={rule === "near"
                ? `No month is complete at every ISO's hub (each ISO's real-time files miss a few days or hours), so this is the latest month in which every hub holds at least ${NEAR * 100} percent of its hours. The hours held are in the table.`
                : `The latest month every ISO holds; no month has at least ${NEAR * 100} percent of its hours at every hub. The hours held are in the table.`}>{common}: grey bars are partial months</span>}
            </p>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[560px] text-sm">
                <thead className="text-left text-xs text-muted">
                  <tr><th className="py-1">ISO</th><th>Hub</th><th title="Each hour's price times the balancing authority's demand that hour, over the month's demand" className="cursor-help">Load-weighted, USD/MWh</th><th title="The plain mean of the same hours: what a flat load pays" className="cursor-help">Simple mean</th><th title="Load-weighted less simple mean: what the grid's own load shape paid above a flat load" className="cursor-help">Shape premium</th><th>Hours held</th></tr>
                </thead>
                <tbody>
                  {rank.map((r) => (
                    <tr key={r.e} className="border-t border-rule">
                      <td className="py-1"><Link href={ISO[isoOf(r.e)].grid}>{ISO[isoOf(r.e)].name}</Link></td>
                      <td className="font-mono text-xs">{r.e.split(":")[1]}</td>
                      <td><N t={M} r={r.lw} /></td>
                      <td><N t={M} r={r.sm} /></td>
                      <td><N t={M} r={r.sp} /></td>
                      <td><N t={M} r={r.h} /> of <N t={M} r={r.hm} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Cite tables={[M]} note="Hub prices from the ISO price tables; hourly demand from EIA-930 (the per-BA workbooks)" />
          </Section>

          <Section title="ERCOT since 2018: monthly load-weighted price" aside={<Tier />}>
            <LineChart
              lines={[
                { label: "Real-time, load-weighted", color: "accent", points: pts("rt_load_weighted") },
                { label: "Real-time, simple mean", color: "muted", points: pts("rt_simple_mean") },
                { label: "Day-ahead, load-weighted", color: "var(--color-fuel-gas)", points: pts("da_load_weighted") },
              ]}
              unit="USD/MWh" height={280} x="month" ariaLabel="ERCOT HB_HUBAVG monthly load-weighted and simple mean real-time price, and load-weighted day-ahead price, since July 2018"
            />
            <p className="mt-1 text-sm">
              Latest complete month, {lastFull}: <N t={M} r={eLw} /> USD/MWh load-weighted, a shape premium of <N t={M} r={eSp} /> USD/MWh. The dearest month
              since July 2018: <N t={M} r={eTop} /> USD/MWh in {eTop ? month(eTop.ts_utc) : ""}.
            </p>
            <Cite tables={[M]} note="ERCOT HB_HUBAVG from ercot_all_hub_prices_history and iso_rtm_hub_prices; ERCO demand from EIA-930" />
          </Section>

          <Section title="When is power cheap: real-time price by hour of day" aside={<Tier />}>
            <div className="grid gap-6 md:grid-cols-2">
              {profiles.map((p) => (
                <div key={p.e}>
                  <h3 className="mb-1 text-base"><Link href={ISO[isoOf(p.e)].grid}>{ISO[isoOf(p.e)].name}</Link> <span className="text-xs text-muted">{ISO[isoOf(p.e)].hub}</span></h3>
                  <HeatGrid cells={p.cs} label={`${ISO[isoOf(p.e)].name} mean real-time price by local hour of day and month`} />
                  <p className="text-sm">
                    In {p.last}: cheapest hour {p.loHour}:00, <N t={P} r={p.lo} /> USD/MWh; dearest {p.hiHour}:00, <N t={P} r={p.hi} /> USD/MWh (local time).
                  </p>
                </div>
              ))}
            </div>
            <Cite tables={[P]} note="The mean real-time price of each local hour of day, per month, the last 12 months each hub holds" />
          </Section>

          <Section title={`Cost against carbon, ${cm ?? ""}`} aside={<Tier />}>
            <CostCarbon points={cc.filter((c) => c.price && c.ci).map((c) => ({ name: ISO[isoOf(c.e)].name, x: c.ci!.value, y: c.price!.value }))}
              label={`Load-weighted real-time price against carbon intensity of generation, one point per ISO, ${cm}`} />
            <div className="overflow-x-auto">
              <table className="w-full min-w-[420px] text-sm">
                <thead className="text-left text-xs text-muted"><tr><th className="py-1">ISO</th><th>Load-weighted, USD/MWh</th><th title="CO2 generated over net generation, EIA's estimates, over the same hours as the price" className="cursor-help">kg CO2 per MWh generated</th></tr></thead>
                <tbody>
                  {cc.map((c) => (
                    <tr key={c.e} className="border-t border-rule"><td className="py-1">{ISO[isoOf(c.e)].name}</td><td><N t={C} r={c.price} /></td><td><N t={C} r={c.ci} /></td></tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Cite tables={[C]} />
          </Section>

          <Section title="The compute calculator: what a large load pays for energy" aside={<Tier />}>
            <p className="mb-2 max-w-3xl text-sm">
              Assumptions, each a default you can change below: a facility of <strong>{MW} MW</strong>, a load factor of <strong>{LF}</strong>, and a training run
              of <strong>{DAYS} days</strong>. Flat load: the facility draws {MW} MW x {LF} in every hour, <Num check={`cop|energy|${MW}|${LF}|${DAYS}|1`} raw={eFlat}>{shown(eFlat)}</Num> MWh,
              in {common}, the month the ranking above uses, at that month&apos;s mean real-time price. Cheapest 80 percent of hours: it draws the same
              only in the cheapest 80 percent of {common}&apos;s hours by hour of day, <Num check={`cop|energy|${MW}|${LF}|${DAYS}|${SHARE}`} raw={e80}>{shown(e80)}</Num> MWh.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[560px] text-sm">
                <thead className="text-left text-xs text-muted">
                  <tr><th className="py-1">ISO</th><th>Flat load, USD</th><th>USD/MWh</th><th>Cheapest 80% of hours, USD</th><th>USD/MWh</th><th>Month</th></tr>
                </thead>
                <tbody>
                  {calc.map((c) => (
                    <tr key={c.e} className="border-t border-rule">
                      <td className="py-1">{ISO[isoOf(c.e)].name}</td>
                      <td>{c.flat === null ? "not held" : <Usd check={`cop|flat_cost|${c.e}|${MW}|${LF}|${DAYS}|${common}`} v={eFlat * c.flat} />}</td>
                      <td>{c.flat === null ? "" : <Num check={`cop|flat_price|${c.e}|${common}`} raw={c.flat}>{shown(c.flat)}</Num>}</td>
                      <td>{c.c80 === null ? "not held" : <Usd check={`cop|cheap_cost|${c.e}|${MW}|${LF}|${DAYS}|${SHARE}|${common}`} v={e80 * c.c80} />}</td>
                      <td>{c.c80 === null ? "" : <Num check={`cop|cheap_price|${c.e}|${SHARE}|${common}`} raw={c.c80}>{shown(c.c80)}</Num>}</td>
                      <td className="text-xs text-muted">{span(c.months)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <h3 className="mb-2 text-base">Your own inputs</h3>
            <Calculator hubs={calc.map((c) => ({ iso: ISO[isoOf(c.e)].name, flat: c.flat, cells: cells(d.profile, c.e).filter((x) => !common || x.month === common), months: span(c.months) }))} />
            <Cite tables={[M, P]} note="Flat: the hub's real-time simple mean in the ranked month; cheapest 80 percent: the hourly profile's cheapest hour-of-day cells of that month" />
          </Section>
        </>
      )}
    </>
  );
}
