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
// sentence, the three headline numbers, the coverage of each month and the contract's coverage are computed here from
// A's fixed O&M and A's debt payments (BatteryHeadline, CoverOfA, ContractOfA). "Your battery" no longer holds those
// two fields; their names in an older link are read as scenario A's (lib/battery/finance.ts, parseScenarios). No usage
// count is sent from here: the owner's ruling of 11 October 2026 closes the question sessions 179, 186 and 194 left.
import { createContext, useCallback, useContext, useMemo, type ReactNode } from "react";
import { ScenarioBlock, ScenarioState, useScenarios, type Bar as ChartBar, type Cell, type Field, type Row, type Side, type Values, type View } from "@/components/decisions/ScenarioBlock";
import { HeadlineNumber, HeadlineRow } from "@/components/tool/ToolPage";
import { badMonth, coverage, inputsKey, last36, lastTwelve, monthName, sumOf, usdShort, type Inputs, type Month } from "@/lib/batterystack";
import {
  KEYS, MODEL, SPECS, bound, cellTotals, debtUsd, defaultsOf, differenceWords, differing, isOldParam, isScenarioParam, parseScenarios, resultOf, scenarioQuery, sensitivity,
  stepState, stepsOffered, type Assumptions, type Key, type Scenarios as Both, type StepCase, type StepState, type Steps,
} from "@/lib/battery/finance";
import { ContractResult } from "./Contract";
import { U, V } from "./nums";

const num = (v: number, d = 2) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
const plain = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const usd = (v: number) => `USD ${usdShort(Math.round(v))}`;
const day = (iso: string) => new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });

type Revenue = { l12: number | null; first: string | null; last: string | null; bad: Month | null; n36: number; months: Month[] };
type StepMeta = { built: string; rte_steps: number[]; cycle_steps: number[] };
type Held = { d: Assumptions; steps: Steps; state: StepState; revenue: (rte: number, cycles: number) => Revenue | null };
const Battery = createContext<Held | null>(null);
const useBattery = () => useContext(Battery)!;
/** The parameters of the address the scenarios replace: their own, and the two old names read as scenario A's. */
const drop = (name: string) => isScenarioParam(name) || isOldParam(name);

/** The two scenarios of the page, held above its sections: the block edits them, the headline reads scenario A. */
export function BatteryDecisions({ ms, mw, costs, stepCase, stepMeta, initial, children }: {
  ms: Month[]; mw: number; costs: { capex: number; fom: number }; stepCase: StepCase | null; stepMeta: StepMeta; initial: Record<string, string | undefined>; children: ReactNode;
}) {
  const d = useMemo(() => defaultsOf(costs), [costs]);
  // the months the page's own windows read: a step is offered only while the file of steps still describes them
  const need = useMemo(() => (last36(ms)?.months ?? []).map((r) => r.m), [ms]);
  const state = useMemo(() => stepState(stepCase, ms, need), [stepCase, ms, need]);
  const steps = useMemo(() => stepsOffered(stepMeta, state), [stepMeta, state]);
  /** The revenue the rows read at an efficiency and a cycle limit: the page's own months at the model's values, the
   * model's run at that step otherwise; null when the step is not held. */
  const revenue = useMemo(() => {
    const memo = new Map<string, Revenue | null>();
    return (rte: number, cycles: number): Revenue | null => {
      const k = `${rte}|${cycles}`;
      if (memo.has(k)) return memo.get(k)!;
      let months: Month[] | null = ms;
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
  }, [ms, need, state, stepCase]);
  const query = useCallback((s: { a: Values; b: Values; view: View }) => scenarioQuery(s as unknown as Both, d), [d]);
  const held = useMemo(() => ({ d, steps, state, revenue }), [d, steps, state, revenue]);
  return (
    <Battery.Provider value={held}>
      <ScenarioState start={parseScenarios(initial, d, steps, mw)} query={query} drop={drop}>{children}</ScenarioState>
    </Battery.Provider>
  );
}

/** What the page's own figures read of scenario A: its fixed O&M and its debt payments, as the inputs the page's
 * library and its check keys take, and the months at A's efficiency and cycle limit. */
function useA(x: Inputs, ms: Month[]) {
  const { s } = useScenarios<Assumptions>();
  const { revenue } = useBattery();
  const a = s.a;
  const model = a.rte === MODEL.rte && a.cycles === MODEL.cycles;
  const y: Inputs = { ...x, fom: a.fom, ds: debtUsd(a, x.mw) };
  return { a, model, y, months: model ? ms : revenue(a.rte, a.cycles)?.months ?? ms };
}

/** The summary sentence and the three headline numbers, computed from scenario A. At the model's own efficiency and
 * cycle limit every figure carries the check key the page always wrote (bs|<inputs>|<stat>, the inputs with A's fixed
 * O&M and debt payments), so scripts/check-values.mjs recomputes it from the table. */
export function BatteryHeadline({ ms, x, gridName, gridFrom }: { ms: Month[]; x: Inputs; gridName: string; gridFrom?: string }) {
  const { a, model, y, months } = useA(x, ms);
  const key = inputsKey(y);
  const size = `${x.mw.toLocaleString("en-US")} MW, ${x.dur}-hour`;
  const l12 = lastTwelve(months), w36 = last36(months), bad = badMonth(w36?.months ?? []);
  const total = l12 ? sumOf(l12, "total") : null;
  const share = l12 && total ? Math.round((sumOf(l12, "ancillary") / total) * 100) : null;
  const cover = total === null ? null : coverage(total, y);
  const kw = total === null ? null : total / 1000;
  const cycles = `${plain(a.cycles)} ${a.cycles === 1 ? "cycle" : "cycles"} a day`;
  return (
    <>
      <p className="mb-6 max-w-3xl font-serif text-xl leading-snug" data-summary="1">
        {!l12 ? (
          <>A {size} battery in {gridName}: no twelve consecutive months are held, so there is no last-twelve-months figure.</>
        ) : model ? (
          <>Over the last twelve months a {size} battery in {gridName} earned USD <V pre={key} s="l12_kw:total" v={kw} /> per kW, <V pre={key} s="l12_share:ancillary" v={share} /> percent
            of it from ancillary services, and covered its debt <V pre={key} s="cover" v={cover} /> times.</>
        ) : (
          <>Over the last twelve months a {size} battery in {gridName} earned USD <V pre={key} s="l12_kw:total" v={kw} keyed={false} /> per kW at a round-trip efficiency
            of {plain(a.rte)} percent and at most {cycles}, and covered its debt <V pre={key} s="cover" v={cover} keyed={false} /> times.</>
        )}
      </p>

      <HeadlineRow>
        <HeadlineNumber label="Last twelve months, all streams" value={<>USD <V pre={key} s="l12_kw:total" v={kw} keyed={model} /><span className="ml-1 font-sans text-sm text-muted">per kW</span></>}
          note={l12 ? <>USD <U pre={key} s="l12:total" v={Math.round(total! * x.mw)} keyed={model} /> for {size}, {monthName(l12[0].m)} to {monthName(l12[11].m)}.
            {model ? null : <span data-scenario-a-steps="1"> Scenario A: round-trip efficiency {plain(a.rte)} percent, at most {cycles}. The sections below are the model&apos;s own run, at {MODEL.rte} percent and one cycle a day.</span>}</> : <>No twelve consecutive months are held.</>} />
        <HeadlineNumber label="A bad month: the 10th percentile, last 36 months" value={<>USD <U pre={key} s="p10_36" v={bad ? Math.round(bad.total! * x.mw) : null} keyed={model} /></>}
          note={bad && w36 ? <>{monthName(bad.m)}. One month in ten of the <V pre={key} s="n36" v={w36.months.length} keyed={model} /> months held from {monthName(w36.months[0].m)} to {monthName(w36.to)} earned this or less{w36.months.length < 36 ? `: ${gridName} is held from ${gridFrom}` : ""}.</> : null} />
        <HeadlineNumber label="Debt coverage, last twelve months" value={<><V pre={key} s="cover" v={cover} keyed={model} /><span className="ml-1 font-sans text-sm text-muted">times</span></>}
          note={l12 ? <>{monthName(l12[0].m)} to {monthName(l12[11].m)}: revenue less fixed O&amp;M, over debt payments of USD <U pre={key} s="ds" v={y.ds} /> a year.</> : <>No twelve consecutive months are held.</>} />
      </HeadlineRow>
    </>
  );
}

/** One month's coverage in the fold "Every month", at scenario A's fixed O&M and debt payments. */
export function CoverOfA({ total, x }: { total: number; x: Inputs }) {
  const { y } = useA(x, []);
  return <>{(coverage(total * 12, y) ?? 0).toFixed(2)}</>;
}
/** "With your contract", at scenario A's fixed O&M and debt payments. The contract's terms stay in Contract.tsx. */
export function ContractOfA({ ms, x }: { ms: Month[]; x: Inputs }) {
  const { y } = useA(x, []);
  return <ContractResult ms={ms} x={y} />;
}

export function Scenarios({ x, costs, gridName, stepMeta }: { x: Inputs; costs: { capex: number; fom: number; note: string }; gridName: string; stepMeta: StepMeta }) {
  const { s } = useScenarios<Assumptions>();
  const { d, steps, state, revenue } = useBattery();
  const a = s[s.view];
  const size = `${x.mw.toLocaleString("en-US")} MW, ${x.dur}-hour`;
  const scale = 1000 * x.mw;
  const col = (p: View) => {
    const y = s[p], rev = revenue(y.rte, y.cycles);
    return { p, y, rev, r: rev && rev.l12 !== null ? resultOf(y, rev.l12) : null };
  };
  const cols = { a: col("a"), b: col("b") };
  type Col = ReturnType<typeof col>;
  const inView = cols[s.view];
  const bars = inView.r ? sensitivity(a, (rte, cycles) => revenue(rte, cycles)?.l12 ?? null, steps) : [];
  const sourceOf = (k: Key) => (k === "capex" || k === "fom" ? `${SPECS[k].source}: ${costs.note}` : SPECS[k].source);

  const fields: Field[] = KEYS.map((k) => {
    const sp = SPECS[k];
    return { key: k, label: sp.label, unit: sp.unit, min: sp.min, max: sp.max, whole: sp.whole,
      options: k === "rte" || k === "cycles" ? steps[k].map((v) => ({ value: v, label: plain(v) })) : undefined,
      note: <>Default {plain(d[k])}. {sourceOf(k)}.</> };
  });
  const none: Cell = { v: "not held", raw: null };
  const row = (key: string, label: string, note: string, cell: (c: Col) => Cell): Row => ({ key, label, note, cell: (p) => cell(cols[p]) });
  const rows: Row[] = [
    row("revenue", "Revenue, last twelve months", "USD per kW",
      (c) => (c.rev && c.rev.l12 !== null ? { v: `USD ${num(c.rev.l12)}`, raw: c.rev.l12, note: `${monthName(c.rev.first!)} to ${monthName(c.rev.last!)}` } : none)),
    row("p10", "The 10th-percentile month", `for ${size}, last 36 months`,
      (c) => (c.rev?.bad ? { v: usd(c.rev.bad.total! * x.mw), raw: Math.round(c.rev.bad.total! * x.mw), note: `${monthName(c.rev.bad.m)}, of ${c.rev.n36} months` } : none)),
    row("coverage", "Debt coverage", "last twelve months: revenue less fixed O&M, over debt payments",
      (c) => (c.r ? (c.r.coverage === null ? { v: "no debt", raw: null } : { v: `${num(c.r.coverage)} times`, raw: c.r.coverage, note: `debt payments ${usd(c.r.debt * scale)} a year` }) : none)),
    row("npv", "NPV at the hurdle rate", `to equity, for ${size}`,
      (c) => (c.r ? { v: usd(c.r.npv * scale), raw: c.r.npv, note: `USD ${num(c.r.npv)} per kW at ${plain(c.y.hurdle)} percent` } : none)),
    row("irr", "IRR", "to equity, percent a year",
      (c) => (c.r ? (c.r.irr === null ? { v: "none", raw: null, note: "no rate from -99 to 1,000 percent sets NPV to zero" } : { v: `${num(c.r.irr, 1)} percent`, raw: c.r.irr }) : none)),
    row("toll", "Breakeven toll", "a toll on the whole battery: the price at which coverage reaches 1.25 times, USD per kW-month",
      (c) => (c.r ? (c.r.toll === null ? { v: "no debt", raw: null } : { v: `USD ${num(c.r.toll)}`, raw: c.r.toll }) : none)),
    row("tail", "Merchant tail after the contract", `the years after the debt's term, for ${size}, at the hurdle rate`,
      (c) => (c.r ? { v: usd(c.r.tail.pv * scale), raw: c.r.tail.pv, note: c.r.tail.years > 0 ? `years ${c.r.tail.from} to ${c.r.tail.to}` : `0 years: the term and the life are both ${plain(c.y.life)} years` } : none)),
  ];

  const side = (t: Side | null) => (t ? `${usd(t.v)} at ${plain(t.value)}` : "no step held");
  const chartBars: ChartBar[] = bars.map((b) => ({ key: b.key, label: b.label, step: b.step, base: b.base * scale, size: b.size * scale,
    down: b.down ? { value: b.down.value, v: b.down.npv * scale } : null, up: b.up ? { value: b.up.value, v: b.up.npv * scale } : null }));

  return (
    <ScenarioBlock
      fields={fields} defaults={d} bound={(k, v) => bound(k as Key, v, d, steps)} head={`For ${size}`} rows={rows}
      differing={differing(s.a, s.b)} short={(k, v) => SPECS[k as Key].short(v)} differs={differenceWords(s.a, s.b)}
      sentence={cols.a.r ? (
        <p className="mt-3 max-w-3xl text-sm" data-npv-sentence="a">
          Scenario A, {size}: at a hurdle rate of {plain(s.a.hurdle)} percent, NPV is {usd(cols.a.r.npv * scale)}.
        </p>
      ) : null}
      chart={chartBars.length ? { bars: chartBars, moves: "NPV", axis: "NPV", fmt: usd, pad: 1,
        says: (b) => `${b.label}, moved by ${b.step}: NPV is ${side(b.down)} and ${side(b.up)}; ${usd(b.base)} at ${plain(a[b.key as Key])}.`,
        sizeWords: (b) => (b.size > 0 ? usd(b.size) : "no step held"), stepWords: (b) => `by ${b.step}`,
        heads: ["NPV, lowered", "NPV, raised"], side: (_, t) => side(t) } : null}
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
      )}
    />
  );
}
