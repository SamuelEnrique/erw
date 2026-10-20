"use client";
// Session 179: the decisions block of /cost-of-power/battery. An assumptions panel (ten assumptions, each with its
// default, the default's source and a Reset), two scenarios A and B set side by side on the same seven rows, and a
// sensitivity chart for the scenario in view. Everything is computed in the browser from the months already on the
// page (lib/battery/finance.ts; the two assumptions inside the model, efficiency and cycles a day, take only the steps
// the model itself was run at, data/battery_scenario_steps.json). A change sends no request: the address is rewritten
// in place (history.replaceState) so that a comparison can be shared as a link. No sentence here judges: each states a
// number. The formulas are in docs/methods/battery_earns_algorithm.md, section 11.1.
//
// Session 195: the panel, the two columns, the row in words and the chart are the component the three decision pages
// share (components/decisions/ScenarioBlock.tsx); this file hands it the battery's fields, rows and figures. The two
// scenarios are held above the page's sections (BatteryDecisions), and scenario A sets the headline: the summary
// sentence, the three headline numbers and the coverage of each month are computed here from A's fixed O&M and A's
// debt payments (BatteryHeadline, CoverOfA). "Your battery" no longer holds those two fields; their names in an older
// link are read as scenario A's (lib/battery/finance.ts, parseScenarios). No usage count is sent from here: the
// owner's ruling of 11 October 2026 closes the question sessions 179, 186 and 194 left.
//
// Session 208 (the owner's rulings of 12 October 2026): the page asks three questions. The block answers the second,
// "Is it worth building?", with twelve assumptions now: the contract's share and price are scenario assumptions,
// 0 by default, so the default is fully merchant and every figure at a share of 0 is what it was. The standalone
// contract panel and "With your contract" are gone (ContractOfA with them); the headline's coverage reads A's contract.
// The sensitivity chart answers the third question, "What matters most", in a section of its own (BatterySensitivity),
// so the block is handed no chart. CoverOfA stays for the CSV of every month, which the page no longer draws.
//
// Session 296 (the owner's rulings of 15 October 2026, the page's pass 1): the twelve assumptions are drawn in the
// left box, under "Financing" (Settings.tsx, BatteryFinancing: the same panel, the contract as a sub-group), and the
// block in the second question draws the table alone. The reader's view (lib/battery/view.ts) is held here with the
// scenarios and written into the address with them: which headline figures (up to six of eight: the three of before,
// NPV, IRR, the breakeven toll, the payback year and NPV per dollar of equity, each scenario A's), which charts (up to
// three of four: revenue by stream, and scenario A's years as cash after costs, cash after debt and the debt), at what
// scale, the units, and the sensitivity's mode (a sourced range, or a percent step) and measure (NPV or IRR). At the
// defaults (the three figures, the one chart, adjusted scale, this battery, the sourced range in NPV) every figure of
// before is what it was; the sensitivity chart is the one thing that reads differently at the default, as item 7 asks.
import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { ScenarioBlock, ScenarioPanel, ScenarioState, Sensitivity, useScenarios, type Bar as ChartBar, type Cell, type Chart, type Field, type Row, type Side, type Values, type View } from "@/components/decisions/ScenarioBlock";
import { SeriesChart } from "@/components/tool/SeriesChart";
import { HeadlineNumber, HeadlineRow, Tip } from "@/components/tool/ToolPage";
import { badMonth, coverage, inputsKey, last36, lastTwelve, monthName, sumOf, usdShort, type Inputs, type Month, type Year } from "@/lib/batterystack";
import {
  KEYS, MODEL, OPTIONS, SPECS, bound, cellTotals, clampWords, coverage as coverageOf, debtUsd, defaultsOf, differenceWords, differing, equityIn, flows, isOldParam, isScenarioParam, npvPerEquity, parseScenarios, paybackYear,
  noRangeOf, projection, rangesOf, resultOf, scenarioQuery, sensitivityIn, sensitivityKeys, stepState, stepsOffered, type Assumptions, type Ctx, type Key, type Mode, type Scenarios as Both, type StepCase, type StepState, type Steps,
} from "@/lib/battery/finance";
import { CHARTS, HEADS, isViewParam, viewQuery, type View as PageView } from "@/lib/battery/view";
import { U, V } from "./nums";
import { ViewCtx } from "./ViewState";
import { Num } from "@/components/Num";
import { highLow, chosen, windowWords, type PriceYear } from "@/lib/priceyears";

const num = (v: number, d = 2) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
const plain = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const usd = (v: number) => `USD ${usdShort(Math.round(v))}`;
const day = (iso: string) => new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });

type Revenue = { l12: number | null; first: string | null; last: string | null; bad: Month | null; n36: number; months: Month[] };
export type StepMeta = { built: string; rte_steps: number[]; cycle_steps: number[] };
type Costs = { capex: number; fom: number; note: string; source?: string };
/** Session 297: the grid's peak stress event (its window revenue, USD per kW, and its name), for the stress repeats. */
export type Peak = { kw: number; label: string } | null;
// session 352: `ws` the price years held for the battery shown (price_years_by_window), `win` the one the view chose (null: the
// page's own last twelve months, the default)
type Held = { d: Assumptions; steps: Steps; state: StepState; revenue: (rte: number, cycles: number) => Revenue | null; ctx: Ctx; peak: Peak; ws: PriceYear[]; win: PriceYear | null };
const Battery = createContext<Held | null>(null);
const useBattery = () => useContext(Battery)!;
/** The parameters of the address the scenarios replace: their own, the two old names read as scenario A's, and
 * (session 296) the view's. */
const drop = (name: string) => isScenarioParam(name) || isOldParam(name) || isViewParam(name);

/** The revenue the rows read at an efficiency and a cycle limit: the page's own months at the model's values, the
 * model's run at that step otherwise; null when the step is not held. Session 268: made here, outside the component,
 * with its own cache (the rules of React's hooks forbid a function made in render that changes a local value). */
function revenueAt(ms: Month[], need: string[], state: StepState, stepCase: StepCase | null, win: PriceYear | null) {
  const memo = new Map<string, Revenue | null>();
  return (rte: number, cycles: number): Revenue | null => {
    const k = `${rte}|${cycles}`;
    if (memo.has(k)) return memo.get(k)!;
    let months: Month[] | null = ms;
    // session 352: a window of price years is the table's, at the model's own efficiency and cycles; at another step the
    // table holds no figure, so the row says "not held"
    if (win) {
      const w = last36(ms);
      const out: Revenue | null = rte === MODEL.rte && cycles === MODEL.cycles
        ? { l12: win.value, first: win.from, last: win.to, bad: badMonth(w?.months ?? []), n36: w?.months.length ?? 0, months: ms } : null;
      memo.set(k, out);
      return out;
    }
    if (rte !== MODEL.rte || cycles !== MODEL.cycles) {
      const t = state.ok ? cellTotals(stepCase, rte, cycles) : null;
      months = t ? ms.map((r) => (need.includes(r.m) && t.has(r.m) ? { ...r, total: t.get(r.m)! } : r)) : null;
    }
    let out: Revenue | null = null;
    if (months) {
      const l12 = lastTwelve(months), w = last36(months);
      out = { l12: l12 ? sumOf(l12, "total") / 1000 : null, first: l12 ? l12[0].m : null, last: l12 ? l12[11].m : null, bad: badMonth(w?.months ?? []), n36: w?.months.length ?? 0, months };
    }
    memo.set(k, out);
    return out;
  };
}

/** The two scenarios of the page and (session 296) the reader's view, held above its sections: the box edits them,
 * the headline reads scenario A and the view. */
export function BatteryDecisions({ ms, mw, costs, stepCase, stepMeta, initial, view, peak, hours, years = [], children }: {
  ms: Month[]; mw: number; costs: { capex: number; fom: number }; stepCase: StepCase | null; stepMeta: StepMeta; initial: Record<string, string | undefined>; view: PageView;
  /** session 297: the grid's peak stress event, and the battery's hours (the augmentation cost is per kWh) */
  peak: Peak; hours: number; children: ReactNode;
  /** session 352: the price years held for the battery shown */
  years?: PriceYear[];
}) {
  const d = useMemo(() => defaultsOf(costs), [costs]);
  // the months the page's own windows read: a step is offered only while the file of steps still describes them
  const need = useMemo(() => (last36(ms)?.months ?? []).map((r) => r.m), [ms]);
  const state = useMemo(() => stepState(stepCase, ms, need), [stepCase, ms, need]);
  const steps = useMemo(() => stepsOffered(stepMeta, state), [stepMeta, state]);
  const [v, setV] = useState<PageView>(view);
  const win = useMemo(() => chosen(years, v.py), [years, v.py]);
  const revenue = useMemo(() => revenueAt(ms, need, state, stepCase, win), [ms, need, state, stepCase, win]);
  const set = useCallback((p: Partial<PageView>) => setV((cur) => ({ ...cur, ...p })), []);
  const query = useCallback((s: { a: Values; b: Values; view: View }) => [...scenarioQuery(s as unknown as Both, d), ...viewQuery(v)], [d, v]);
  const ctx = useMemo<Ctx>(() => ({ peak: peak?.kw ?? 0, hours }), [peak, hours]);
  const held = useMemo(() => ({ d, steps, state, revenue, ctx, peak, ws: years, win }), [d, steps, state, revenue, ctx, peak, years, win]);
  const heldView = useMemo(() => ({ v, set }), [v, set]);
  return (
    <Battery.Provider value={held}>
      <ViewCtx.Provider value={heldView}>
        <ScenarioState start={parseScenarios(initial, d, steps, mw)} query={query} drop={drop}>{children}</ScenarioState>
      </ViewCtx.Provider>
    </Battery.Provider>
  );
}

/** What the page's own figures read of scenario A: its fixed O&M and its debt payments, as the inputs the page's
 * library and its check keys take, the months at A's efficiency and cycle limit, and (session 208) whether A holds a
 * contract. */
function useA(x: Inputs, ms: Month[]) {
  const { s } = useScenarios<Assumptions>();
  const { revenue, ctx, win } = useBattery();
  const a = s.a;
  const model = a.rte === MODEL.rte && a.cycles === MODEL.cycles;
  const contracted = a.cshare > 0;
  const y: Inputs = { ...x, fom: a.fom, ds: debtUsd(a, x.mw) };
  return { a, model, contracted, y, ctx, months: model ? ms : revenue(a.rte, a.cycles)?.months ?? ms, win };
}

/** The summary sentence and the headline numbers, computed from scenario A. At the model's own efficiency and
 * cycle limit, with no contract, every figure carries the check key the page always wrote (bs|<inputs>|<stat>, the
 * inputs with A's fixed O&M and debt payments), so scripts/check-values.mjs recomputes it from the table. With a
 * contract in A (session 208) the coverage is A's own, contract plus the uncontracted share of the market, and carries
 * no key: the table holds no contract. Session 296: the reader picks which figures (up to six of eight); the five new
 * ones are scenario A's finance (lib/battery/finance.ts) and carry no key, as the results table's cells carry none. */
export function BatteryHeadline({ ms, x, gridName, gridFrom }: { ms: Month[]; x: Inputs; gridName: string; gridFrom?: string }) {
  const { a, model, contracted, y, ctx, months, win } = useA(x, ms);
  const { v } = useContext(ViewCtx)!;
  const key = inputsKey(y);
  const size = `${x.mw.toLocaleString("en-US")} MW, ${x.dur}-hour`;
  if (win) return <WindowHeadline x={x} gridName={gridName} />;
  const scale = 1000 * x.mw;
  const l12 = lastTwelve(months), w36 = last36(months), bad = badMonth(w36?.months ?? []);
  const total = l12 ? sumOf(l12, "total") : null;
  const share = l12 && total ? Math.round((sumOf(l12, "ancillary") / total) * 100) : null;
  const cover = total === null ? null : contracted ? coverageOf(a, total / 1000) : coverage(total, y);
  const kw = total === null ? null : total / 1000;
  const r = kw === null ? null : resultOf(a, kw, ctx);
  const fl = kw === null ? null : flows(a, kw, ctx);
  const cycles = `${plain(a.cycles)} ${a.cycles === 1 ? "cycle" : "cycles"} a day`;
  const keyed = model && !contracted;
  // session 263: a capital cost or a debt share of 0 leaves no debt; the sentence and the number say so, where they read
  // "not held times" until then
  const noDebt = total !== null && cover === null;
  const contractWords = contracted ? <span data-headline-contract="1"> with {plain(a.cshare)} percent of its power contracted at USD {plain(a.cprice)} per kW-month,</span> : null;
  const money = (perKw: number) => (v.units === "kw" ? <>USD {num(perKw)}<span className="ml-1 font-sans text-sm text-muted">per kW</span></> : <>{usd(perKw * scale)}</>);
  const none = <span className="text-muted">not held</span>;
  const payback = fl ? paybackYear(fl) : null;
  const perEquity = r ? npvPerEquity(a, r.npv) : null;
  const figures: Record<string, ReactNode> = {
    l12: <HeadlineNumber key="l12" label="Last twelve months, all streams" value={<>USD <V pre={key} s="l12_kw:total" v={kw} keyed={model} /><span className="ml-1 font-sans text-sm text-muted">per kW</span></>}
      note={l12 ? <>USD <U pre={key} s="l12:total" v={Math.round(total! * x.mw)} keyed={model} /> for {size}, {monthName(l12[0].m)} to {monthName(l12[11].m)}.
        {model ? null : <span data-scenario-a-steps="1"> Scenario A: round-trip efficiency {plain(a.rte)} percent, at most {cycles}. The sections below are the model&apos;s own run, at {MODEL.rte} percent and one cycle a day.</span>}</> : <>No twelve consecutive months are held.</>} />,
    bad: <HeadlineNumber key="bad" label="A bad month: the 10th percentile, last 36 months"
      value={v.units === "kw" ? <>USD <V pre={key} s="p10_36_kw" v={bad ? bad.total! / 1000 : null} keyed={false} /><span className="ml-1 font-sans text-sm text-muted">per kW</span></> : <>USD <U pre={key} s="p10_36" v={bad ? Math.round(bad.total! * x.mw) : null} keyed={model} /></>}
      note={bad && w36 ? <>{monthName(bad.m)}. One month in ten of the <V pre={key} s="n36" v={w36.months.length} keyed={model} /> months held from {monthName(w36.months[0].m)} to {monthName(w36.to)} earned this or less{w36.months.length < 36 ? `: ${gridName} is held from ${gridFrom}` : ""}.</> : null} />,
    cover: <HeadlineNumber key="cover" label="Debt coverage, last twelve months" value={noDebt ? <span data-no-debt="2">No debt</span> : <><V pre={key} s="cover" v={cover} keyed={keyed} /><span className="ml-1 font-sans text-sm text-muted">times</span></>}
      note={l12 ? <>{monthName(l12[0].m)} to {monthName(l12[11].m)}: {contracted ? <span data-headline-contract="2">scenario A&apos;s contract ({plain(a.cshare)} percent at USD {plain(a.cprice)} per kW-month) plus the market on the rest, </span> : "revenue "}less fixed O&amp;M, over debt payments of USD <U pre={key} s="ds" v={y.ds} /> a year.</> : <>No twelve consecutive months are held.</>} />,
    npv: <HeadlineNumber key="npv" label="NPV at the hurdle rate" value={r ? <span data-headline-raw={r.npv}>{money(r.npv)}</span> : none}
      note={r ? <>To equity, scenario A, at {plain(a.hurdle)} percent: USD {num(r.npv)} per kW for {size}.</> : <>No twelve consecutive months are held.</>} />,
    irr: <HeadlineNumber key="irr" label="IRR" value={r ? (r.irr === null ? <span className="text-muted" data-headline-raw="">none</span> : <span data-headline-raw={r.irr}>{num(r.irr, 1)}<span className="ml-1 font-sans text-sm text-muted">percent</span></span>) : none}
      note={r ? (r.irr === null ? <>To equity, scenario A: no rate from -99 to 1,000 percent sets NPV to zero.</> : <>To equity, scenario A, a year.</>) : <>No twelve consecutive months are held.</>} />,
    toll: <HeadlineNumber key="toll" label="Breakeven toll" value={r ? (r.toll === null ? <span className="text-muted" data-headline-raw="">no debt</span> : <span data-headline-raw={r.toll}>USD {num(r.toll)}<span className="ml-1 font-sans text-sm text-muted">per kW-month</span></span>) : none}
      note={<>A toll on the whole battery at which coverage is 1.25 times, scenario A.</>} />,
    payback: <HeadlineNumber key="payback" label="Payback year" value={fl ? (payback === null ? <span className="text-muted" data-headline-raw="">none</span> : <span data-headline-raw={payback}>{payback === 0 ? "none needed" : `year ${payback}`}</span>) : none}
      note={fl ? (payback === null ? <>Scenario A&apos;s cash flows to equity, added up without discounting, stay negative through year {plain(a.life)}.</> : payback === 0 ? <>No equity is paid in at year 0.</> : <>The first year scenario A&apos;s cash flows to equity, added up from year 0 without discounting, are no longer negative.</>) : <>No twelve consecutive months are held.</>} />,
    npveq: <HeadlineNumber key="npveq" label="NPV per dollar of equity" value={r ? (perEquity === null ? <span className="text-muted" data-headline-raw="">no equity</span> : <span data-headline-raw={perEquity}>{num(perEquity)}</span>) : none}
      note={r ? (perEquity === null ? <>Scenario A pays no equity in at year 0.</> : <>Scenario A&apos;s NPV over the equity paid in at year 0, USD {num(equityIn(a))} per kW.</>) : <>No twelve consecutive months are held.</>} />,
  };
  return (
    <>
      <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
        {!l12 ? (
          <>A {size} battery in {gridName}: no twelve consecutive months are held, so there is no last-twelve-months figure.</>
        ) : model ? (
          <>Over the last twelve months a {size} battery in {gridName} earned USD <V pre={key} s="l12_kw:total" v={kw} /> per kW, <V pre={key} s="l12_share:ancillary" v={share} /> percent
            of it from ancillary services, and{contractWords} {noDebt ? <span data-no-debt="1">has no debt to cover.</span> : <>covered its debt <V pre={key} s="cover" v={cover} keyed={keyed} /> times.</>}</>
        ) : (
          <>Over the last twelve months a {size} battery in {gridName} earned USD <V pre={key} s="l12_kw:total" v={kw} keyed={false} /> per kW at a round-trip efficiency
            of {plain(a.rte)} percent and at most {cycles}, and{contractWords} {noDebt ? <span data-no-debt="1">has no debt to cover.</span> : <>covered its debt <V pre={key} s="cover" v={cover} keyed={false} /> times.</>}</>
        )}
      </p>

      <HeadlineRow>
        {HEADS.filter((h) => v.heads.includes(h.key)).map((h) => figures[h.key])}
      </HeadlineRow>
    </>
  );
}

/** Session 296 (items 4, 5, 9): the charts the reader picked, side by side on a wide screen: revenue by stream (the
 * year chart the page always drew, from the table) and scenario A's years from the finance (cash after costs, cash
 * after debt, the debt), at the scale chosen, each with a Chart | Table toggle. At the default one chart is drawn,
 * the first, as before. */
export function BatteryCharts({ ms, x, ys, upper, brokenNote, strategyLine }: {
  ms: Month[]; x: Inputs; ys: Year[]; upper: string; brokenNote: ReactNode; strategyLine: string;
}) {
  const { a, ctx, months, win, model } = useA(x, ms);
  const { v } = useContext(ViewCtx)!;
  const l12 = lastTwelve(months);
  // session 352: the years of scenario A's life are priced on the window chosen, the table's figure at the model's step
  const kw = win ? (model ? win.value : null) : l12 ? sumOf(l12, "total") / 1000 : null;
  const rows = kw === null ? [] : projection(a, kw, ctx);
  const yearsOf = rows.map((r) => ({ label: String(r.t) }));
  const money = (n: number) => n.toLocaleString("en-US", { maximumFractionDigits: 0 });
  const charts: Record<string, ReactNode> = {
    revenue: (
      <SeriesChart key="revenue" id="years" title="Revenue by year, USD per kW" unit="USD per kW" kind="stacked" scale={v.scale} partialWords="Incomplete year"
        categories={ys.map((y) => ({ label: y.y, sub: y.complete ? undefined : `${y.months} months`, partial: !y.complete }))}
        series={[{ name: "Energy", color: "var(--color-accent)", values: ys.map((y) => y.energy / 1000) }, { name: "Ancillary services", color: "var(--color-ink)", values: ys.map((y) => y.ancillary / 1000) }]}
        says={(i) => `${ys[i].y}: energy ${money(ys[i].energy / 1000)}, ancillary ${money(ys[i].ancillary / 1000)} USD per kW${ys[i].complete ? "" : ` (${ys[i].months} months held)`}`}
        tip={<Tip id="years" label="the year chart"><span className="block" data-upper-bound="1">{upper}</span> {strategyLine} Per kW of rated power. A hatched year holds fewer than twelve months and is not a full year&apos;s revenue.{brokenNote}</Tip>} />
    ),
    after_costs: (
      <SeriesChart key="after_costs" id="after-costs" title="Cash after costs, USD per kW" unit="USD per kW" kind="line" scale={v.scale} categories={yearsOf}
        series={[{ name: "Income less fixed O&M", color: "var(--color-accent)", values: rows.map((r) => r.afterCosts) }]} fmt={money}
        tip={<Tip id="after-costs" label="cash after costs">Scenario A, each year of its {plain(a.life)}-year life: the income (the last twelve months&apos; revenue, falling by the degradation rate each year after the first, and the contract&apos;s income while the debt lasts) less fixed O&amp;M, USD per kW. The years run along the bottom.</Tip>} />
    ),
    after_debt: (
      <SeriesChart key="after_debt" id="after-debt" title="Cash after debt, USD per kW" unit="USD per kW" kind="line" scale={v.scale} categories={yearsOf}
        series={[{ name: "Cash to equity", color: "var(--color-accent)", values: rows.map((r) => r.afterDebt) }]} fmt={money}
        tip={<Tip id="after-debt" label="cash after debt">Scenario A, each year of its life: the income less fixed O&amp;M less the debt payment while the debt lasts, USD per kW: the cash flow to equity that NPV and IRR discount (the equity paid in at year 0 is not drawn).</Tip>} />
    ),
    debt: (
      <SeriesChart key="debt" id="debt" title="Debt, USD per kW" unit="USD per kW" kind="line" scale={v.scale} categories={yearsOf}
        series={[{ name: "Payment", color: "var(--color-accent)", values: rows.map((r) => r.debt) }, { name: "Still owed", color: "var(--color-ink)", values: rows.map((r) => r.balance) }]} fmt={money}
        tip={<Tip id="debt" label="the debt">Scenario A: the level debt payment each year of the debt&apos;s term, and the debt still owed at the end of each year (each payment covers the year&apos;s interest and the rest repays), USD per kW.</Tip>} />
    ),
  };
  const chosen = CHARTS.filter((c) => v.charts.includes(c.key)).map((c) => charts[c.key]);
  if (!chosen.length) return null;
  const cols = chosen.length === 3 ? "lg:grid-cols-3" : chosen.length === 2 ? "lg:grid-cols-2" : "";
  return <div className={`grid gap-x-6 ${cols}`} data-charts={v.charts.join("+")}>{chosen}</div>;
}

/** One month's coverage at scenario A's fixed O&M and debt payments (the CSV of every month reads it from the server
 * with the same arithmetic; this stays for a page that draws it). */
export function CoverOfA({ total, x }: { total: number; x: Inputs }) {
  const { y } = useA(x, []);
  return <>{(coverage(total * 12, y) ?? 0).toFixed(2)}</>;
}

/** What the block and the chart both read: the fields, the two columns and the bars of the scenario in view. */
function useBlock(x: Inputs) {
  const { s } = useScenarios<Assumptions>();
  const { d, steps, state, revenue, ctx, peak } = useBattery();
  const { v } = useContext(ViewCtx)!;
  const a = s[s.view];
  const size = `${x.mw.toLocaleString("en-US")} MW, ${x.dur}-hour`;
  const scale = 1000 * x.mw;
  const col = (p: View) => {
    const y = s[p], rev = revenue(y.rte, y.cycles);
    return { p, y, rev, r: rev && rev.l12 !== null ? resultOf(y, rev.l12, ctx) : null };
  };
  const cols = { a: col("a"), b: col("b") };
  const inView = cols[s.view];
  // session 296: the sensitivity in the mode and the measure the reader chose (the sourced range in NPV by default)
  const ranges = rangesOf(x.dur);
  const mode: Mode = v.mode === "range" ? { kind: "range", ranges } : { kind: "pct", pct: v.pct };
  const irr = v.measure === "irr";
  const bars = inView.r ? sensitivityIn(a, (rte, cycles) => revenue(rte, cycles)?.l12 ?? null, steps, mode, v.measure, ctx) : [];
  const fmt = irr ? (t: number) => `${num(t, 1)} percent` : usd;
  const side = (t: Side | null) => (t ? `${fmt(t.v)} at ${plain(t.value)}` : v.mode === "range" ? "no published case" : "no step held");
  const chartBars: ChartBar[] = bars.map((b) => ({ key: b.key, label: b.label, step: b.step, base: irr ? b.base : b.base * scale, size: irr ? b.size : b.size * scale,
    down: b.down ? { value: b.down.value, v: irr ? b.down.npv : b.down.npv * scale } : null, up: b.up ? { value: b.up.value, v: irr ? b.up.npv : b.up.npv * scale } : null }));
  const what = irr ? "IRR" : "NPV";
  const low = v.mode === "range" ? "at its published low case" : `lowered by ${plain(v.pct)} percent`, high = v.mode === "range" ? "at its published high case" : `raised by ${plain(v.pct)} percent`;
  const chart: Chart | null = chartBars.length ? { bars: chartBars, moves: what, axis: irr ? "IRR, percent" : "NPV", fmt, pad: irr ? 0.1 : 1,
    says: (b) => `${b.label}, ${low}: ${what} is ${side(b.down)}; ${high}: ${side(b.up)}; ${fmt(b.base)} at ${plain(a[b.key as Key])}.${v.mode === "range" ? ` ${ranges[b.key as Key]?.source ?? ""}.` : ""}`,
    sizeWords: (b) => (b.down || b.up ? fmt(b.size) : "no case held"), stepWords: () => (v.mode === "range" ? "low and high case" : `by ${plain(v.pct)} percent`),
    heads: v.mode === "range" ? [`${what}, low case`, `${what}, high case`] : [`${what}, lowered`, `${what}, raised`], side: (_, t) => side(t),
    legend: v.mode === "range" ? ["Low case", "High case"] : [`Lowered by ${plain(v.pct)} percent`, `Raised by ${plain(v.pct)} percent`] } : null;
  return { s, d, steps, state, a, size, scale, cols, chart, v, peak };
}

/** Session 296: the twelve assumptions of the scenario in view, in the left box under "Financing": the panel the
 * block drew in the second question until this session, the contract's share and price as a sub-group. */
export function BatteryFinancing({ x, costs, gridName, stepMeta }: { x: Inputs; costs: Costs; gridName: string; stepMeta: StepMeta }) {
  const { d, steps, state } = useBlock(x);
  const sourceOf = (k: Key) => (k === "capex" || k === "fom" ? `${costs.source ?? SPECS[k].source}: ${costs.note}` : SPECS[k].source);
  // session 263: a value typed outside a field's bounds is brought inside them by `bound`, and the field says so under
  // it while that value is in force (session 296: the field draws the line itself, from the value typed and the one used)
  // session 297: the stress repeats are set in the second question (Scenarios), beside the results they move; the
  // degradation method and the augmentation period are choices, each a list
  const fields: Field[] = KEYS.filter((k) => k !== "stress").map((k) => {
    const sp = SPECS[k];
    const options = k === "rte" || k === "cycles" ? steps[k].map((v) => ({ value: v, label: plain(v) })) : OPTIONS[k] ? OPTIONS[k]!.map((v) => ({ value: v, label: sp.plain(v) })) : undefined;
    return { key: k, label: sp.label, unit: sp.unit, min: sp.min, max: sp.max, whole: sp.whole, options,
      note: <>Default {sp.plain(d[k])}. {sourceOf(k)}.</>, clamp: (t: number, u: number) => clampWords(k, t, u) };
  });
  return (
    <ScenarioPanel fields={fields} defaults={d} bound={(k, v) => bound(k as Key, v, d, steps)} columns={1}
      groups={[{ key: "degradation", title: "Degradation and augmentation", keys: ["method", "fade", "aug", "augcost"] }, { key: "contract", title: "The contract", keys: ["cshare", "cprice"] }]}
      foot={(
        <p className="mt-3 text-xs leading-snug text-muted" data-steps={state.ok ? "held" : state.why}>
          {state.ok
            ? `Round-trip efficiency and cycles a day take the steps the model was run at on ${day(stepMeta.built)}.`
            : state.why === "none"
              ? `Round-trip efficiency and cycles a day: only the model's own step is held for ${gridName}.`
              : state.why === "months"
                ? `Round-trip efficiency and cycles a day: only the model's own step is offered. The other steps are held for months to ${monthName(state.fileLast!)}; the table now reaches ${monthName(state.liveLast!)}.`
                : `Round-trip efficiency and cycles a day: only the model's own step is offered. The other steps were run on ${day(stepMeta.built)}, and a month of the table has changed since.`}
        </p>
      )} />
  );
}

/** Session 297 (the roadmap's "what if Uri happened again"): the stress repeats of the scenario in view, set beside the
 * results they move. Each repeat adds the grid's peak stress event's window revenue once, spread evenly over the
 * life's years; 0 by default, so nothing moves. Drawn only when the grid holds a stress event. */
function StressRepeats({ peak }: { peak: Peak }) {
  const { s, update } = useScenarios<Assumptions>();
  const { d, steps } = useBattery();
  if (!peak) return null;
  const a = s[s.view];
  const set = (v: number) => update({ ...s, [s.view]: { ...a, stress: bound("stress", v, d, steps) } });
  return (
    <div className="mb-4 flex flex-wrap items-center gap-x-3 gap-y-2 border border-rule bg-paper px-3 py-2 text-sm" data-stress-repeats={s.view}>
      <span className="font-semibold">Stress test<Tip id="stress" label="the stress test">{SPECS.stress.source}. The peak event of this grid is {peak.label}: USD {num(peak.kw)} per kW in its window, from the stress table. A repeat is added to the market revenue of every year, {num(peak.kw / a.life)} per kW a year each at a life of {plain(a.life)} years, before the contract&apos;s share and after the degradation; coverage, which reads the last twelve months, does not move.</Tip></span>
      <label className="inline-flex items-center gap-2">scenario {s.view.toUpperCase()} repeats {peak.label}
        <input type="number" inputMode="numeric" min={0} max={SPECS.stress.max} step={1} value={a.stress} data-assumption="stress" aria-label="Repeats of the peak stress event over the life" className="w-16 border border-muted bg-white px-2 py-1 text-sm"
          onChange={(e) => { const v = Number(e.target.value); if (e.target.value !== "" && Number.isFinite(v)) set(v); }} />
        {a.stress === 1 ? "time" : "times"} over its life
      </label>
      <button type="button" data-reset="stress" aria-label="Reset repeats of the peak stress event" disabled={a.stress === d.stress} className="border border-rule bg-white px-2 py-1 text-xs text-accent disabled:text-muted" onClick={() => set(d.stress)}>Reset</button>
      <span className="text-xs text-muted">Default 0. USD {num(peak.kw)} per kW a repeat, {peak.label}.</span>
    </div>
  );
}

export function Scenarios({ x }: { x: Inputs }) {
  const { s, d, steps, size, scale, cols, peak } = useBlock(x);
  const { win, ws, ctx } = useBattery();
  type Col = (typeof cols)["a"];
  const none: Cell = { v: "not held", raw: null };
  const row = (key: string, label: string, note: string, cell: (c: Col) => Cell): Row => ({ key, label, note, cell: (p) => cell(cols[p]) });
  const contractNote = (c: Col) => (c.y.cshare > 0 ? `contract ${plain(c.y.cshare)} percent at USD ${plain(c.y.cprice)} per kW-month; ` : "");
  const rows: Row[] = [
    row("revenue", win ? `Revenue, ${windowWords(win).label.toLowerCase()}` : "Revenue, last twelve months", win ? "USD per kW a year, the market's, price_years_by_window" : "USD per kW, the market's",
      (c) => (c.rev && c.rev.l12 !== null ? { v: `USD ${num(c.rev.l12)}`, raw: c.rev.l12, note: `${monthName(c.rev.first!)} to ${monthName(c.rev.last!)}` } : none)),
    row("p10", "The 10th-percentile month", `for ${size}, last 36 months`,
      (c) => (c.rev?.bad ? { v: usd(c.rev.bad.total! * x.mw), raw: Math.round(c.rev.bad.total! * x.mw), note: `${monthName(c.rev.bad.m)}, of ${c.rev.n36} months` } : none)),
    row("coverage", "Debt coverage", "last twelve months: the contract plus the market on the rest, less fixed O&M, over debt payments",
      (c) => (c.r ? (c.r.coverage === null ? { v: "no debt", raw: null } : { v: `${num(c.r.coverage)} times`, raw: c.r.coverage, note: `${contractNote(c)}debt payments ${usd(c.r.debt * scale)} a year` }) : none)),
    row("npv", "NPV at the hurdle rate", `to equity, for ${size}`,
      (c) => (c.r ? { v: usd(c.r.npv * scale), raw: c.r.npv, note: `USD ${num(c.r.npv)} per kW at ${plain(c.y.hurdle)} percent` } : none)),
    row("irr", "IRR", "to equity, percent a year",
      (c) => (c.r ? (c.r.irr === null ? { v: "none", raw: null, note: "no rate from -99 to 1,000 percent sets NPV to zero" } : { v: `${num(c.r.irr, 1)} percent`, raw: c.r.irr }) : none)),
    row("toll", "Breakeven toll", "a toll on the whole battery: the price at which coverage reaches 1.25 times, USD per kW-month",
      (c) => (c.r ? (c.r.toll === null ? { v: "no debt", raw: null } : { v: `USD ${num(c.r.toll)}`, raw: c.r.toll }) : none)),
    row("tail", "Merchant tail after the contract", `the years after the debt's term, for ${size}, at the hurdle rate`,
      (c) => (c.r ? { v: usd(c.r.tail.pv * scale), raw: c.r.tail.pv, note: c.r.tail.years > 0 ? `years ${c.r.tail.from} to ${c.r.tail.to}` : c.y.term > c.y.life ? `0 years: the term of ${plain(c.y.term)} years is cut to the life, ${plain(c.y.life)} years` : `0 years: the term and the life are both ${plain(c.y.life)} years` } : none)),
  ];

  return (
    <>
      <p className="mb-3 max-w-3xl text-sm text-muted" data-financing-where="1">The assumptions of each scenario are set in the box on the left, under <a href="#financing">Financing</a>; scenario A gives the headline.</p>
      <StressRepeats peak={peak} />
      <ScenarioBlock
        panel={false} fields={[]} defaults={d} bound={(k, v) => bound(k as Key, v, d, steps)} head={`For ${size}`} rows={rows}
        differing={differing(s.a, s.b)} short={(k, v) => SPECS[k as Key].short(v)} differs={differenceWords(s.a, s.b)}
        sentence={cols.a.r ? (
          <p className="mt-3 max-w-3xl text-sm" data-npv-sentence="a">
            Scenario A, {size}: at a hurdle rate of {plain(s.a.hurdle)} percent, NPV is {usd(cols.a.r.npv * scale)}.
          </p>
        ) : null}
        chart={null}
      />
      <YearsLine ws={ws} a={s.a} ctx={ctx} size={size} scale={scale} />
    </>
  );
}

/** Session 352: what the same project earns in the highest and the lowest whole year held, at the model's own step, with
 * scenario A's NPV in each; said only when two whole years are held. */
function YearsLine({ ws, a, ctx, size, scale }: { ws: PriceYear[]; a: Assumptions; ctx: Ctx; size: string; scale: number }) {
  const bw = highLow(ws);
  if (!bw) return null;
  const one = (w: PriceYear) => {
    const r = resultOf(a, w.value, ctx);
    return <>USD <Num check={`series|price_years_by_window|${w.entity}|${w.variable}|${w.ts}`} raw={w.value}>{num(w.value)}</Num> per kW in {w.id.slice(5)} (scenario A&apos;s NPV {usd(r.npv * scale)})</>;
  };
  return (
    <p className="mt-3 max-w-3xl text-sm" data-years-line="1">
      The same {size} battery, at the model&apos;s efficiency and one cycle a day, earned {one(bw.high)} in its highest whole year held and {one(bw.low)} in its
      lowest. The &quot;Price years&quot; choice in the box prices the page on any of them.
    </p>
  );
}

/** Session 352: the summary and the first figures when the page is priced on a window of price years other than the
 * last twelve months: the table's figure, at the model's own step, scenario A's coverage and NPV on it. */
function WindowHeadline({ x, gridName }: { x: Inputs; gridName: string }) {
  const { s } = useScenarios<Assumptions>();
  const { win, revenue, ctx } = useBattery();
  const a = s.a, w = win!;
  const size = `${x.mw.toLocaleString("en-US")} MW, ${x.dur}-hour`;
  const rev = revenue(a.rte, a.cycles);
  const kw = rev?.l12 ?? null;
  const r = kw === null ? null : resultOf(a, kw, ctx);
  const words = windowWords(w);
  const value = <Num check={`series|price_years_by_window|${w.entity}|${w.variable}|${w.ts}`} raw={w.value}>{num(w.value)}</Num>;
  return (
    <>
      <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1" data-price-years={w.id}>
        {kw === null
          ? <>A {size} battery in {gridName}: the price years hold no figure at a round-trip efficiency of {plain(a.rte)} percent and at most {plain(a.cycles)} cycles a day, only at the model&apos;s own; choose the last twelve months for this step.</>
          : <>Priced {words.sentence}, a {size} battery in {gridName} earns USD {value} per kW a year{r && r.coverage !== null ? <>, and covers its debt {num(r.coverage)} times</> : null}.</>}
      </p>
      <HeadlineRow>
        <HeadlineNumber label={`Price years: ${words.label}`} value={kw === null ? <span className="text-muted">not held</span> : <>USD {value}<span className="ml-1 font-sans text-sm text-muted">per kW a year</span></>}
          note={<>{w.months} months, {monthName(w.from)} to {monthName(w.to)}, the model&apos;s own run (price_years_by_window).</>} />
        <HeadlineNumber label="Debt coverage" value={r ? (r.coverage === null ? <span>No debt</span> : <>{num(r.coverage)}<span className="ml-1 font-sans text-sm text-muted">times</span></>) : <span className="text-muted">not held</span>}
          note={<>Scenario A on these price years.</>} />
        <HeadlineNumber label="NPV at the hurdle rate" value={r ? <>{usd(r.npv * 1000 * x.mw)}</> : <span className="text-muted">not held</span>}
          note={<>To equity, scenario A, at {plain(a.hurdle)} percent, on these price years.</>} />
      </HeadlineRow>
    </>
  );
}

/** Session 208: the sensitivity chart of the scenario in view, in the page's third section, with one line on how to
 * read it. Drawn only when the scenario has a result. Session 296: in the mode and measure the reader chose. */
export function BatterySensitivity({ x }: { x: Inputs }) {
  const { s, chart, v } = useBlock(x);
  if (!chart) return <p className="max-w-3xl text-sm text-muted" data-sensitivity-none="1">No twelve consecutive months are held, so there is no NPV to move.</p>;
  const measure = v.measure === "irr" ? "IRR" : "NPV";
  const drawn = new Set(chart.bars.map((b) => b.key));
  // the rows the chart would draw for this scenario (session 297: sensitivityKeys) that have no published range
  // session 314: for 8 hours the capital cost and fixed O&M have no range either (the ATB's figure alone)
  const noRange = noRangeOf(x.dur);
  const missing = sensitivityKeys(s[s.view]).filter((k) => !drawn.has(k) && noRange[k]);
  return (
    <>
      <p className="mb-2 max-w-3xl text-sm" data-how-to-read="1" data-mode={v.mode} data-measure={v.measure}>
        {v.mode === "range"
          ? <>Each row moves one assumption of scenario {s.view.toUpperCase()} to its published low case and its published high case (Lazard, Levelized Cost of Energy+, June 2025, and NREL&apos;s Annual Technology Baseline 2025; the source is in the row&apos;s hover), holds the others, and draws where {measure} lands from the scenario&apos;s own {measure} (the line); the longest bars are the assumptions that matter most.</>
          : <>Each row moves one assumption of scenario {s.view.toUpperCase()} down and up by {plain(v.pct)} percent of its value, holds the others, and draws where {measure} lands from the scenario&apos;s own {measure} (the line); the longest bars are the assumptions that matter most. Round-trip efficiency and cycles a day move to the nearest step the model was run at, within their limits.</>}
      </p>
      <Sensitivity c={chart} view={s.view} />
      {v.mode === "range" && missing.length ? (
        <p className="mt-2 max-w-3xl text-xs text-muted" data-no-range={missing.join("+")}>
          No published range, so no row: {missing.map((k) => `${SPECS[k].label.toLowerCase()} (${noRange[k]})`).join("; ")}.
        </p>
      ) : null}
    </>
  );
}
