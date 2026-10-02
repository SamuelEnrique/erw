import type { Metadata } from "next";
import { Num } from "@/components/Num";
import { SiteLink as Link } from "@/components/SiteLink";
import { ChartFrame, Fold, HeadlineNumber, HeadlineRow, InputPanel, SourceLine, ToolHeader, ToolPage, ToolSection, ToolTable } from "@/components/tool/ToolPage";
import {
  CAPACITY_WORDS, DEBT, EVENTS, PRODUCTS, REQUIREMENTS, RTE, STRATEGIES, STRESS_TABLE, TABLE, averageYear, badMonth, coverage, debtPerMw, gridOf, inputsKey,
  inputsOf, lastTwelve, monthName, monthsOf, stat, stress, sumOf, usdShort, years, type Inputs, type Month, type Row, type StressRow, type Year,
} from "@/lib/batterystack";
import { HOURLY, attempt, rest } from "@/lib/supabase";
import { CostTabs } from "../Tabs";
import { BatteryForm } from "./BatteryForm";
import { ContractInputs, ContractProvider, ContractResult } from "./Contract";

// Session 67: "What a battery earns". What a grid battery of the reader's size and duration earned from energy and
// from ancillary services together, split hour by hour so nothing is counted twice, and whether that covers its debt,
// with and without a contract. Every number is computed by lib/batterystack.ts from the rows of battery_stack_monthly
// and battery_stack_stress_daily (warehouse/derived/battery_stack.py), read from Supabase, and carries a check key
// (bs|<inputs>|<stat>) that scripts/check-values.mjs recomputes from its own read. The contract terms never leave the
// browser (Contract.tsx). No capacity price is read: the capacity table is internal and is named nowhere in this page.
export const metadata: Metadata = { title: "What a battery earns" };
export const dynamic = "force-dynamic";

const METHOD = "/data/methods/battery_stack";
const ENERGY = "#8C1515", ANCILLARY = "#2E2D29";  // cardinal and Stanford black (app/tokens.css: accent and ink)

async function rowsOf(entity: string, x: Inputs): Promise<Row[]> {
  return rest<Row>("series", { select: "variable,ts_utc,value", table_name: `eq.${TABLE}`, entity: `eq.${entity}`,
    variable: `like.${x.strat}_${x.dur}h_*`, order: "variable,ts_utc" }, HOURLY);
}
async function stressOf(entity: string, x: Inputs): Promise<StressRow[]> {
  return rest<StressRow>("series", { select: "variable,ts_utc,value,event", table_name: `eq.${STRESS_TABLE}`, entity: `eq.${entity}`,
    variable: `like.${x.strat}_${x.dur}h_*`, order: "variable,ts_utc" }, HOURLY);
}

/** A US dollar amount with its check key. */
function U({ pre, s, v }: { pre: string; s: string; v: number | null }) {
  return v === null ? <span className="text-muted">not held</span> : <span data-format="usd"><Num check={`bs|${pre}|${s}`} raw={v}>{usdShort(v)}</Num></span>;
}
/** A ratio, a count, a percent or USD per kW with its check key (a whole number, else two decimals). */
function V({ pre, s, v }: { pre: string; s: string; v: number | null }) {
  if (v === null) return <span className="text-muted">not held</span>;
  return <Num check={`bs|${pre}|${s}`} raw={v}>{Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</Num>;
}

/** Revenue by year, USD per kW, stacked by stream. A year far above the others (2021 in ERCOT) is drawn to the top of
 * the scale with a break mark and its value written, so the other years stay readable; an incomplete year is hatched. */
function YearBars({ ys }: { ys: Year[] }) {
  const W = 760, H = 300, L = 54, R = 10, top = 26, bot = 44;
  const tot = ys.map((y) => (Math.max(0, y.energy) + Math.max(0, y.ancillary)) / 1000);
  const neg = Math.min(0, ...ys.map((y) => (Math.min(0, y.energy) + Math.min(0, y.ancillary)) / 1000));
  const sorted = [...tot].sort((a, b) => b - a);
  const broken = sorted.length > 2 && sorted[0] > 2.5 * sorted[1];
  const hi = (broken ? sorted[1] : sorted[0] ?? 1) * 1.15 || 1;
  const step = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000].find((s) => hi / s <= 5) ?? 2000;
  const ticks: number[] = [];
  for (let t = Math.ceil(neg / step) * step; t <= hi; t += step) ticks.push(t);
  const y = (v: number) => top + ((hi - v) / (hi - neg)) * (H - top - bot);
  const bw = (W - L - R) / ys.length;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Revenue by year, USD per kW, stacked: energy and ancillary services">
      <defs>
        <pattern id="hatch-e" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#fff" /><rect width="2.2" height="5" fill={ENERGY} /></pattern>
        <pattern id="hatch-a" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#fff" /><rect width="2.2" height="5" fill={ANCILLARY} /></pattern>
      </defs>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke={t === 0 ? "#2E2D29" : "#D9D2C3"} strokeWidth={t === 0 ? 1 : 0.75} />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="#6B665E">{t}</text>
        </g>
      ))}
      <text x={L - 46} y={14} fontSize="11" fill="#6B665E">USD per kW</text>
      {ys.map((r, i) => {
        const e = r.energy / 1000, a = r.ancillary / 1000;
        const x0 = L + i * bw + bw * 0.18, w = bw * 0.64;
        const over = broken && tot[i] > hi;
        // positive parts stack upward from zero (energy first), negative parts downward
        const segs: { v0: number; v1: number; fill: string }[] = [];
        let up = 0, down = 0;
        for (const [v, solid, hatch] of [[e, ENERGY, "url(#hatch-e)"], [a, ANCILLARY, "url(#hatch-a)"]] as [number, string, string][]) {
          if (v >= 0) { segs.push({ v0: up, v1: up + v, fill: r.complete ? solid : hatch }); up += v; }
          else { segs.push({ v0: down + v, v1: down, fill: r.complete ? solid : hatch }); down += v; }
        }
        return (
          <g key={r.y}>
            {segs.map((s, k) => {
              const a1 = Math.min(s.v1, hi), a0 = Math.min(s.v0, hi);
              if (a1 === a0) return null;
              return <rect key={k} x={x0} width={w} y={y(a1)} height={Math.max(0.5, y(a0) - y(a1))} fill={s.fill} stroke={r.complete ? "none" : (k === 0 ? ENERGY : ANCILLARY)} strokeWidth={r.complete ? 0 : 0.75} />;
            })}
            {over ? <path d={`M${x0 - 3},${top + 14} l${w / 4 + 1.5},-5 l${w / 4},5 l${w / 4},-5 l${w / 4 + 1.5},5`} fill="none" stroke="#fff" strokeWidth="3" /> : null}
            <text x={x0 + w / 2} y={(over ? top : y(Math.min(up, hi))) - 6} textAnchor="middle" fontSize="11" fill="#2E2D29">{Math.round(e + a).toLocaleString("en-US")}</text>
            <text x={x0 + w / 2} y={H - bot + 16} textAnchor="middle" fontSize="11" fill="#2E2D29">{r.y}</text>
            {!r.complete ? <text x={x0 + w / 2} y={H - bot + 30} textAnchor="middle" fontSize="10" fill="#6B665E">{r.months} months</text> : null}
            <title>{`${r.y}: energy ${Math.round(e).toLocaleString("en-US")}, ancillary ${Math.round(a).toLocaleString("en-US")} USD per kW${r.complete ? "" : ` (${r.months} months held)`}`}</title>
          </g>
        );
      })}
    </svg>
  );
}

const OTHER: { grid: string; energy: string; ancillary: string; capacity: string }[] = [
  { grid: "PJM", energy: "not held, licensed", ancillary: "not yet in the warehouse", capacity: "Held, not shown: publishing requires a license from the market operator" },
  { grid: "NYISO", energy: "see the seller tab", ancillary: "not yet in the warehouse", capacity: "Held: license under review" },
  { grid: "ISO-NE", energy: "see the seller tab", ancillary: "not yet in the warehouse", capacity: "Held, not shown: publishing requires a license from the market operator" },
  { grid: "MISO", energy: "see the seller tab", ancillary: "not yet in the warehouse", capacity: "Held, not shown: publishing requires a license from the market operator" },
  { grid: "SPP", energy: "see the seller tab", ancillary: "not yet in the warehouse", capacity: "No capacity market" },
];

export default async function Battery({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const x = inputsOf(Object.fromEntries(Object.entries(sp).map(([k, v]) => [k, typeof v === "string" ? v : undefined])));
  const g = gridOf(x.grid);
  const key = inputsKey(x);
  const [read, readStress] = await Promise.all([attempt(() => rowsOf(g.entity!, x)), attempt(() => stressOf(g.entity!, x))]);
  const rows = read.ok ? read.data : [];
  const stressRows = readStress.ok ? readStress.data : [];
  const ms: Month[] = monthsOf(rows, x.strat, x.dur);
  const held = ms.filter((r) => r.held);
  const st = (s: string) => stat(rows, stressRows, x, s);
  const ys = years(ms);
  const l12 = lastTwelve(ms);
  const bad = badMonth(ms);
  const avgTotal = st("avg:total"), share = st("share:ancillary"), cover = st("cover");
  const size = `${x.mw.toLocaleString("en-US")} MW, ${x.dur}-hour`;
  const leftOut = ms.reduce((a, r) => a + r.daysOut, 0), leftAnc = ms.reduce((a, r) => a + r.daysOutAncillary, 0);
  const events = stress(stressRows, x.strat, x.dur);
  const defaultDs = Math.round(debtPerMw(x.dur) * x.mw);
  const products = PRODUCTS[x.grid];
  const broken = (() => { const t = ys.map((r) => r.energy + r.ancillary).sort((a, b) => b - a); return t.length > 2 && t[0] > 2.5 * t[1] ? ys.find((r) => r.energy + r.ancillary === t[0])! : null; })();
  const strategyLine = x.strat === "foresight"
    ? "Perfect foresight: energy at the hourly real-time price and ancillary services at day-ahead prices, all known in advance. An upper bound, not a forecast."
    : "Day-ahead schedule: the battery is scheduled against day-ahead energy and ancillary prices and paid those prices, with no real-time trading. It assumes its offers clear at the day-ahead price.";

  return (
    <ToolPage>
      <ToolHeader
        title="What a battery earns"
        crumb={<CostTabs active="battery" />}
        lead={<>What a grid battery earned from energy and from ancillary services together, by year and by stream, and whether that covers its debt, with and without a contract. The battery is split hour by hour between the two, so nothing is counted twice. <Link href={METHOD}>Method</Link>.</>}
      />
      <ContractProvider>
        <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]">
          <aside>
            <InputPanel title="Your battery" note={<>Debt payments default to {DEBT.share * 100} percent of the capital cost borrowed at {DEBT.rate * 100} percent over {DEBT.life} years: USD {usdShort(defaultDs)} a year for {size}. Costs are Lazard&apos;s Levelized Cost of Energy+ (June 2025), as on the seller tab, scaled to the duration.</>}>
              <BatteryForm key={key} x={x} />
            </InputPanel>
            <InputPanel title="Your contract (optional)">
              <ContractInputs />
            </InputPanel>
          </aside>

          <div className="min-w-0">
            {!read.ok ? (
              <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">The table could not be read, so no number is shown: {read.reason}</p>
            ) : !held.length ? (
              <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">No month is held for this battery in {g.name}.</p>
            ) : (
              <>
                <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
                  A {size} battery in {g.name} earned USD <U pre={key} s="avg:total" v={avgTotal} /> in an average year, <V pre={key} s="share:ancillary" v={share} /> percent
                  of it from ancillary services, and covered its debt <V pre={key} s="cover" v={cover} /> times over the last twelve months.
                </p>

                <HeadlineRow>
                  <HeadlineNumber label="An average year, all streams" value={<>USD <U pre={key} s="avg:total" v={avgTotal} /></>}
                    note={<><V pre={key} s="avg_kw:total" v={st("avg_kw:total")} /> USD per kW. The mean of each calendar month over {held.length} months, {monthName(held[0].m)} to {monthName(held.at(-1)!.m)}, summed.</>} />
                  <HeadlineNumber label="A bad month, the 10th percentile" value={<>USD <U pre={key} s="p10" v={st("p10")} /></>}
                    note={bad ? <>{monthName(bad.m)}. One month in ten earned this or less.</> : null} />
                  <HeadlineNumber label="Debt coverage, last twelve months" value={<><V pre={key} s="cover" v={cover} /><span className="ml-1 font-sans text-sm text-muted">times</span></>}
                    note={l12 ? <>{monthName(l12[0].m)} to {monthName(l12[11].m)}: revenue less fixed O&amp;M, over debt payments of USD <U pre={key} s="ds" v={x.ds} /> a year.</> : <>No twelve consecutive months are held.</>} />
                </HeadlineRow>

                <ChartFrame title="Revenue by year, USD per kW"
                  legend={[{ label: "Energy", color: ENERGY }, { label: "Ancillary services", color: ANCILLARY }, { label: "Incomplete year", color: ANCILLARY, hatch: true }]}
                  note={<>{strategyLine} Per kW of rated power. A hatched year holds fewer than twelve months and is not a full year&apos;s revenue.
                    {broken ? <> {broken.y} is off the scale at <V pre={key} s={`year:${broken.y}:total`} v={st(`year:${broken.y}:total`)} /> USD per kW: Winter Storm Uri, when reserve prices stood near the cap for days. It is in the average year.</> : null}</>}>
                  <YearBars ys={ys} />
                </ChartFrame>

                <ToolSection title="Income by stream" note={<>Average year and last twelve months for {size}. The total is split hour by hour by one optimization a day: in any hour the battery&apos;s power is sold as energy or held as a reserve, never both, so the rows add up with no double counting. Reserves are paid for being held and are assumed never called.</>}>
                  <ToolTable caption="Income by stream" head={["Stream", "Average year, USD", "Last twelve months, USD", "Share of the average year"]}
                    rows={[
                      { key: "energy", cells: ["Energy (charge low, sell high)", <U key="a" pre={key} s="avg:energy" v={st("avg:energy")} />, <U key="b" pre={key} s="l12:energy" v={st("l12:energy")} />, <><V pre={key} s="share:energy" v={st("share:energy")} /> percent</>] },
                      { key: "anc", cells: ["Ancillary services", <U key="a" pre={key} s="avg:ancillary" v={st("avg:ancillary")} />, <U key="b" pre={key} s="l12:ancillary" v={st("l12:ancillary")} />, <><V pre={key} s="share:ancillary" v={share} /> percent</>] },
                      ...products.map((p) => ({ key: p.key, muted: true, cells: [<span key="n" className="pl-4">{p.label}</span>, <U key="a" pre={key} s={`avg:${p.key}`} v={st(`avg:${p.key}`)} />, <U key="b" pre={key} s={`l12:${p.key}`} v={st(`l12:${p.key}`)} />, <><V pre={key} s={`share:${p.key}`} v={st(`share:${p.key}`)} /> percent</>] })),
                      { key: "cap", cells: ["Capacity", <span key="w" className="text-left text-muted">{CAPACITY_WORDS[x.grid]}</span>, "", ""] },
                      { key: "total", highlight: true, cells: ["Total, split hour by hour with no double counting", <U key="a" pre={key} s="avg:total" v={avgTotal} />, <U key="b" pre={key} s="l12:total" v={st("l12:total")} />, "100 percent"] },
                    ]} />
                </ToolSection>

                <ToolSection title="With your contract">
                  <ContractResult ms={ms} x={x} />
                </ToolSection>
              </>
            )}

            <ToolSection title="Other grids" note="In words only: no number from a licensed table is shown on this site.">
              <ToolTable caption="Other grids" head={["Grid", "Energy", "Ancillary services", "Capacity"]} minWidth={620}
                rows={OTHER.map((o) => ({ key: o.grid, cells: [o.grid, <span key="e" className="block text-left">{o.energy === "see the seller tab" ? <Link href="/cost-of-power/seller?asset=battery">see the seller tab</Link> : o.energy}</span>, <span key="a" className="block text-left">{o.ancillary}</span>, <span key="c" className="block text-left">{o.capacity}</span>] }))} />
            </ToolSection>

            <div className="mb-8 border-t border-rule">
              <Fold title="Every month">
                <ToolTable caption="Every month" minWidth={640} head={["Month", "Energy, USD", "Ancillary, USD", "Total, USD", "Coverage", "Days held", "Days left out"]}
                  rows={[...ms].reverse().map((r) => ({
                    key: r.m, muted: !r.held,
                    cells: [r.m,
                      r.total === null ? "" : <U key="e" pre={key} s={`month:${r.m}:energy`} v={st(`month:${r.m}:energy`)} />,
                      r.total === null ? "" : <U key="a" pre={key} s={`month:${r.m}:ancillary`} v={st(`month:${r.m}:ancillary`)} />,
                      r.total === null ? "no day held" : <U key="t" pre={key} s={`month:${r.m}:total`} v={st(`month:${r.m}:total`)} />,
                      r.total === null || !r.held ? "" : (coverage(r.total * 12, x) ?? 0).toFixed(2),
                      `${r.daysHeld} of ${r.daysInMonth}`, String(r.daysOut)],
                  }))} />
                <p className="mt-2 max-w-3xl text-xs text-muted">
                  For {size}. Coverage: the month&apos;s revenue less a month of fixed O&amp;M, over a month of debt payments. A grey month holds fewer than 90 percent of its
                  days and is shown but not counted; its revenue is the held days&apos; only. A day is left out, never estimated, when an hour of its energy price or of
                  an ancillary price is not held: <V pre={key} s="out" v={st("out")} /> days in all here{leftOut ? `, ${leftAnc} of them for a missing ancillary price` : ""}.
                </p>
              </Fold>
              <Fold title="Stress days: Uri, Elliott and the 2023 heat">
                {events.length ? (
                  <>
                    <ToolTable caption="Stress days" minWidth={620} head={["Event", "Days held", "Energy, USD", "Ancillary, USD", "Total, USD", "Best day, USD"]}
                      rows={events.map((e) => ({ key: e.event, cells: [<>{EVENTS[e.event]}<div className="text-xs text-muted">{e.first} to {e.last}</div></>, String(e.days),
                        <U key="e" pre={key} s={`stress:${e.event}:energy`} v={st(`stress:${e.event}:energy`)} />, <U key="a" pre={key} s={`stress:${e.event}:ancillary`} v={st(`stress:${e.event}:ancillary`)} />,
                        <U key="t" pre={key} s={`stress:${e.event}:total`} v={st(`stress:${e.event}:total`)} />, <><U pre={key} s={`stress:${e.event}:best`} v={st(`stress:${e.event}:best`)} /> <span className="text-xs text-muted">({e.best.day})</span></>] }))} />
                    <p className="mt-2 max-w-3xl text-xs text-muted">
                      For {size}, over each event&apos;s days. A battery&apos;s best days are the grid&apos;s worst, and what it earns in a storm depends on being available in it,
                      which this model assumes: no outage, no frozen equipment, and reserves that are paid and never called. In an event like Uri held
                      reserves are called: the battery sells energy and runs down. These figures are what the prices offered, not what a battery could have kept.
                    </p>
                  </>
                ) : (
                  <p className="max-w-3xl text-sm text-muted">{x.grid === "ercot" ? "No stress day is held for this battery." : `The stress days are ERCOT's. ${g.name}'s ancillary prices are held from ${g.from}, after these events.`}</p>
                )}
              </Fold>
              <Fold title="What this model cannot see">
                <ul className="max-w-3xl list-disc space-y-1.5 pl-5">
                  <li><strong>One battery does not move prices.</strong> The battery is a price taker. Ancillary markets are small next to the energy market. A large battery, or a fleet of them, pushes those prices down, so large sizes are overstated, ancillary income most of all.</li>
                  <li><strong>The hub, not your node.</strong> Energy is priced at {g.name}&apos;s {g.hub} hub. A battery is paid its own node&apos;s price, which can differ in either direction.</li>
                  <li><strong>Reserves are never called.</strong> An award pays its capacity price and moves no energy. A real battery that is called sells energy at the real-time price, and must recharge.</li>
                  <li><strong>No degradation beyond the round trip.</strong> Round-trip efficiency is {RTE * 100} percent, at most one full cycle a day, each day from empty. Capacity fade, augmentation, outages and station power are not modeled.</li>
                  <li><strong>{STRATEGIES[x.strat]}.</strong> {strategyLine}</li>
                  <li><strong>Hourly.</strong> Ancillary prices are hourly, so the whole model is. A battery trading the 5- and 15-minute real-time prices can earn more from energy than this shows.</li>
                  <li><strong>No capacity payment.</strong> {CAPACITY_WORDS[x.grid]}.</li>
                  <li><strong>How long a reserve must be backed.</strong> The battery must hold stored energy to deliver each upward reserve for the product&apos;s required duration:
                    <ul className="mt-1 list-disc space-y-0.5 pl-5">
                      {REQUIREMENTS[x.grid].map((r, i) => <li key={i}>{r.product}: {r.rule}{r.assumed ? ". Assumed: the operator's own requirement was not verified, so one hour is used" : ` (${r.source})`}.</li>)}
                    </ul>
                  </li>
                </ul>
              </Fold>
            </div>
          </div>
        </div>
      </ContractProvider>
      <SourceLine tables={[TABLE, STRESS_TABLE, ...(x.grid === "ercot" ? ["ercot_all_hub_prices_history", "iso_rtm_hub_prices", "iso_dam_hub_prices", "ercot_as_prices"] : ["iso_hub_prices_history", "iso_rtm_hub_prices", "iso_dam_hub_prices", "caiso_as_prices"])]}
        note={<>Derived by the ERW from {g.name}&apos;s public prices; the first two tables are what this page reads. Cost defaults: Lazard, Levelized Cost of Energy+, June 2025. Solar, wind and gas peakers are on <Link href="/cost-of-power/seller">the seller tab</Link>.</>} />
    </ToolPage>
  );
}
