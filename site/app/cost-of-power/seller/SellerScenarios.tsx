"use client";
// Session 186: the decisions block of /cost-of-power/seller, as session 179 built it for the battery. An assumptions
// panel (eight assumptions, each with its default, the default's source and a Reset), two scenarios A and B set side by
// side on the same eight rows, and a sensitivity chart for the scenario in view. Everything is computed in the browser
// (lib/seller/finance.ts) from figures the page already shows: the last twelve months at the hub chosen, the capture
// price, the months and the pair with a battery. A change sends no request: the address is rewritten in place
// (history.replaceState) so that a comparison can be shared as a link. No sentence here judges: each states a number.
// The formulas are in docs/methods/generator_earns_algorithm.md, section 11.
//
// Session 195: the panel, the two columns, the row in words and the chart are the component the three decision pages
// share (components/decisions/ScenarioBlock.tsx); this file hands it the generator's fields, rows and figures. The two
// scenarios are held above the page's sections (SellerDecisions), and scenario A sets the headline: the headline's
// coverage, the line of one month of debt payments, the section "Debt coverage" and each month's coverage are computed
// here from A's fixed O&M and A's debt payments (CoverHeadline, MonthsOfA, CoverageOfA, DscrOfA). "Your plant" no
// longer holds those two fields; their names in an older link are read as scenario A's (lib/seller/finance.ts,
// parseScenarios). No usage count is sent from here: the owner's ruling of 11 October 2026.
//
// Session 212 (the owner's chain prompt of 12 October 2026, the battery page's layout): the page asks three questions.
// The block answers the second, "Is it worth building?", with ten assumptions now: the contract's share and price are
// scenario assumptions, 0 by default, so the default is fully merchant and every figure at a share of 0 is what it
// was (for solar and wind a share of the energy at a price per MWh; for a battery and a peaker a toll on a share of
// the capacity, USD per kW-month). The standalone contract panel and "With your contract" are gone; the headline's
// coverage reads A's contract. The sensitivity chart answers the third question, "What matters most", in a section of
// its own (SellerSensitivity), so the block is handed no chart. MonthsOfA, CoverageOfA and DscrOfA stay for a page
// that draws the months; this page's months are its CSV (months.csv/route.ts).
//
// Session 235 (the owner's task of 12 October 2026): scenario B can be a PPA. One button under the assumptions, "Make B
// a PPA" (for a battery and a peaker, a toll), sets B's contract share to 100 percent and its contract price to B's own
// breakeven PPA price, rounded up to the cent, and puts B in view; both scenarios still open as merchant and no
// default moves. The results table has one more row, "Breakeven PPA price": the contract price at which NPV at the
// hurdle rate is zero, on the scenario's contract share, or on the whole plant when the scenario holds no contract
// (lib/seller/finance.ts, breakevenPpa). The row that was there, the price at which coverage reaches 1.25 times, stays.
import { useCallback, useMemo, type ReactNode } from "react";
import { ScenarioBlock, ScenarioState, Sensitivity, useScenarios, type Bar as ChartBar, type Cell, type Chart, type Field, type Row, type Side, type Values, type View } from "@/components/decisions/ScenarioBlock";
import { HeadlineNumber } from "@/components/tool/ToolPage";
import { usdShort } from "@/lib/batterystack";
import { ttm, type Month } from "@/lib/merchant";
import {
  KEYS, SPECS, TARGET, asPpa, bound, breakevenPpa, breakevenToll, contractPrice, contractUnits, coverage as coverageOf, debtUsd, debtYears, defaultsOf, ppaShare, differenceWords, differing, isOldParam, isScenarioParam, monthCoverage, parseScenarios, resultOf, scenarioQuery, sensitivity,
  type Assumptions, type Contract, type Key, type Scenarios as Both,
} from "@/lib/seller/finance";
import { CoverageLine, MonthlyRevenue } from "./SellerCharts";
import { Hint, Missing, U, V, count, longMonth } from "./nums";

const num = (v: number, d = 2) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
const plain = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const usd = (v: number) => `USD ${usdShort(Math.round(v))}`;

/** What the page hands the block: figures it already shows, for the grid, hub, asset and size chosen. A figure that is
 * not held is null and its reason is beside it. */
export type Facts = {
  /** `size` is the asset in words, with its size: "100 MW of solar", "a 100 MW gas peaker" */
  mw: number; size: string;
  /** `deg` and `degSource`: the cited degradation default of a battery (session 196); absent for the other assets */
  costs: { capex: number; fom: number; life: number; capexNote: string; fomNote: string; lifeNote: string; deg?: number; degSource?: string };
  /** the last twelve months at the hub chosen: revenue in USD per kW (a peaker: its margin over fuel), energy in MWh per kW */
  twelve: { revenueKw: number; energyKw: number; span: string; at: string } | null; twelveWhy: string;
  money: string;
  /** the headline's price beside it: the capture price (solar, wind), the price while selling or running (battery, peaker) */
  capture: { price: number; flat: number; ratio: number; words: string } | null; captureLabel: string; captureWhy: string;
  /** the lowest month of every month held, USD for the reader's size */
  lowest: { month: string; usd: number; months: number } | null;
  /** the contract's form: a price for a share of the energy (solar, wind), or a toll on a share of the capacity */
  contract: "energy" | "toll";
  /** the co-optimized pair and the plant alone at day-ahead prices, USD for the reader's sizes */
  battery: { withIt: number; without: number; words: string } | null; batteryWhy: string;
};
/** The contract the arithmetic reads: the page's form of it and the last twelve months' energy (session 212). */
const contractOf = (f: Pick<Facts, "contract" | "twelve">): Contract => ({ kind: f.contract, energyKw: f.twelve?.energyKw ?? 0 });

/** The parameters of the address the scenarios replace: their own, and the two old names read as scenario A's. */
const drop = (name: string) => isScenarioParam(name) || isOldParam(name);

/** The two scenarios of the page, held above its sections: the block edits them, the headline reads scenario A. */
export function SellerDecisions({ costs, mw, initial, children }: { costs: { capex: number; fom: number; life: number; deg?: number }; mw: number; initial: Record<string, string | undefined>; children: ReactNode }) {
  const d = useMemo(() => defaultsOf(costs), [costs]);
  const query = useCallback((s: { a: Values; b: Values; view: View }) => scenarioQuery(s as unknown as Both, d), [d]);
  return <ScenarioState start={parseScenarios(initial, d, mw)} query={query} drop={drop}>{children}</ScenarioState>;
}

/** One month as the page's coverage figures read it: its revenue in USD for the reader's size, and whether it is held. */
export type MonthRevenue = { m: string; revenue: number; held: boolean; share: number };
/** What the page's coverage figures read of scenario A: its fixed O&M and its debt payments, written into the check
 * key the page's library is recomputed from, and the months with the coverage those two give (lib/merchant.ts, months
 * and ttm, to the letter). */
function useA(mw: number, keyAsOpened: string, rows: MonthRevenue[] = []) {
  const { s } = useScenarios<Assumptions>();
  const fom = s.a.fom, ds = debtUsd(s.a, mw);
  const key = keyAsOpened.replace(/(^|&)ds=[^&]*/, `$1ds=${ds}`).replace(/(^|&)fom=[^&]*/, `$1fom=${fom}`);
  const dsMonth = ds / 12;
  const ms = rows.map((r) => { const cfads = r.revenue - (fom * 1000 * mw) / 12; return { ...r, cfads, dscr: dsMonth > 0 ? cfads / dsMonth : null }; });
  return { a: s.a, fom, ds, key, dsMonth, ms, t: ttm(ms as unknown as Month[], ds) };
}

/** The third headline number: debt coverage over the last twelve months, at scenario A's fixed O&M and debt payments.
 * Session 212: with a contract in A the coverage is A's own, the contract plus the uncontracted share of the market,
 * and carries no check key (the table holds no contract); at a share of 0 it is the page's trailing-twelve-month
 * figure with its key, as before. */
export function CoverHeadline({ rows, mw, pre, facts }: { rows: MonthRevenue[]; mw: number; pre: string; facts?: Pick<Facts, "contract" | "twelve"> }) {
  const { a, ds, key, t } = useA(mw, pre, rows);
  const last = t.at(-1);
  const contracted = (a.cshare ?? 0) > 0 && !!facts?.twelve;
  const u = facts ? contractUnits(facts.contract) : null;
  const own = contracted ? coverageOf(a, facts!.twelve!.revenueKw, contractOf(facts!)) : null;
  return (
    <HeadlineNumber label="Debt coverage, last twelve months"
      value={!last ? <Missing why="No twelve consecutive months are held, so there is no twelve-month coverage." /> : ds > 0
        ? contracted ? <span data-stat="cover" data-headline-contract="1">{own === null ? "no debt" : num(own)}</span> : <span data-stat="cover"><V pre={key} stat="ttm_last" v={last.dscr} /></span>
        : <span data-stat="cover">no debt</span>}
      unit={last && ds > 0 ? "times" : undefined}
      note={last ? <>The twelve months to {longMonth(last.m)}: {contracted ? <span data-headline-contract="2">scenario A&apos;s contract ({plain(a.cshare)} {u!.shareUnit} at {u!.priceUnit.replace("USD", `USD ${plain(a.cprice)}`)}) plus the market on the rest, </span> : "revenue "}less fixed O&amp;M, over debt payments of USD <U pre={key} stat="ds" v={ds} /> a year.</> : null} />
  );
}

/** "Month by month": the chart with its line at one month of scenario A's debt payments, and the chart's legend. */
export function MonthsOfA({ rows, mw, pre }: { rows: MonthRevenue[]; mw: number; pre: string }) {
  const { ds, key, dsMonth } = useA(mw, pre);
  return (
    <>
      <MonthlyRevenue key={dsMonth} rows={rows} dsMonth={dsMonth} label="Revenue per month, USD; a dashed line marks one month of debt payments" />
      <p className="mb-2 flex flex-wrap gap-x-4 text-xs text-muted">
        <span><span aria-hidden="true" className="mr-1 inline-block h-2.5 w-2.5 bg-ink" />A month held</span>
        <span><span aria-hidden="true" className="mr-1 inline-block h-2.5 w-2.5 bg-accent" />Below a month of debt payments (USD <U pre={key} stat="ds" v={ds} /> a year over twelve)</span>
        <span><span aria-hidden="true" className="mr-1 inline-block h-2.5 w-2.5 bg-rule" /><Hint why="A month with less than 90 percent of its hours (a battery: days) priced is shown and not counted.">Under 90 percent held</Hint></span>
      </p>
    </>
  );
}

/** The section "Debt coverage", at scenario A's fixed O&M and debt payments. */
export function CoverageOfA({ rows, mw, pre }: { rows: MonthRevenue[]; mw: number; pre: string }) {
  const { fom, ds, key, ms, t } = useA(mw, pre, rows);
  const held = ms.filter((r) => r.held);
  const under1 = held.filter((r) => r.dscr !== null && r.dscr < 1), under125 = held.filter((r) => r.dscr !== null && r.dscr < 1.25);
  return (
    <>
      <p className="mb-2 max-w-3xl text-sm">
        <Hint why="Cash flow available for debt payments is the month's revenue less fixed O&M; coverage is that over one month of the annual debt payments.">Coverage</Hint> with fixed O&amp;M of {fom} USD/kW a year and debt payments of{" "}
        <U pre={key} stat="ds" v={ds} /> USD a year: of the <V pre={key} stat="n" v={held.length} d={count} /> months held,{" "}
        <strong><V pre={key} stat="under1" v={under1.length} d={count} /></strong> covered less than 1.0x and{" "}
        <strong><V pre={key} stat="under125" v={under125.length} d={count} /></strong> less than 1.25x.
        {t.length ? (
          <> Over trailing twelve months, coverage was <V pre={key} stat="ttm_last" v={t.at(-1)!.dscr} />x at {longMonth(t.at(-1)!.m)}, at its lowest{" "}
            <V pre={key} stat="ttm_min" v={Math.min(...t.map((r) => r.dscr))} />x; <V pre={key} stat="ttm_under1" v={t.filter((r) => r.dscr < 1).length} d={count} /> of {t.length} twelve-month
            windows fell under 1.0x and <V pre={key} stat="ttm_under125" v={t.filter((r) => r.dscr < 1.25).length} d={count} /> under 1.25x.</>
        ) : <> Twelve-month coverage: <Missing why="No twelve consecutive months are held here, so there is no trailing-twelve-month figure." />.</>}
      </p>
      {t.length >= 2 ? <CoverageLine key={`${fom}|${ds}`} rows={t.map((r) => ({ m: r.m, dscr: r.dscr }))} label="Trailing-twelve-month debt coverage; lines at 1.0 and 1.25 times" /> : null}
      {under1.length ? <p className="mt-1 text-xs text-muted">Months under 1.0x: {under1.map((r) => r.m).join(", ")}.</p> : null}
    </>
  );
}

/** One month's coverage in the fold "Every month", at scenario A's fixed O&M and debt payments. */
export function DscrOfA({ m, revenue, mw, pre }: { m: string; revenue: number; mw: number; pre: string }) {
  const { fom, key, dsMonth } = useA(mw, pre);
  return dsMonth > 0 ? <V pre={key} stat={`dscr:${m}`} v={(revenue - (fom * 1000 * mw) / 12) / dsMonth} /> : null;
}

/** What the block and the chart both read: the scenarios, the defaults, the two columns and the bars of the scenario
 * in view (session 212, as the battery's Scenarios.tsx holds them). */
function useBlock(f: Facts) {
  const { s } = useScenarios<Assumptions>();
  const d = useMemo(() => defaultsOf(f.costs), [f.costs]);
  const a = s[s.view];
  const scale = 1000 * f.mw;
  const c = contractOf(f);
  const col = (p: View) => ({ p, y: s[p], r: f.twelve ? resultOf(s[p], f.twelve.revenueKw, c) : null });
  const cols = { a: col("a"), b: col("b") };
  const bars = f.twelve ? sensitivity(a, f.twelve.revenueKw, c) : [];
  const side = (t: Side | null) => (t ? `${usd(t.v)} at ${plain(t.value)}` : "no step inside its bounds");
  const chartBars: ChartBar[] = bars.map((b) => ({ key: b.key, label: b.label, step: b.key === "cprice" ? contractUnits(f.contract).priceStep : b.step, base: b.base * scale, size: b.size * scale,
    down: b.down ? { value: b.down.value, v: b.down.npv * scale } : null, up: b.up ? { value: b.up.value, v: b.up.npv * scale } : null }));
  const chart: Chart | null = chartBars.length ? { bars: chartBars, moves: "NPV", axis: "NPV", fmt: usd, pad: 1,
    says: (b) => `${b.label}, moved by ${b.step}: NPV is ${side(b.down)} and ${side(b.up)}; ${usd(b.base)} at ${plain(a[b.key as Key])}.`,
    sizeWords: (b) => usd(b.size), stepWords: (b) => `by ${b.step}`,
    heads: ["NPV, lowered", "NPV, raised"], side: (_, t) => side(t) } : null;
  return { s, d, a, scale, c, cols, chart };
}

export function SellerScenarios({ facts: f }: { facts: Facts }) {
  const { s, d, scale, cols } = useBlock(f);
  const { update } = useScenarios<Assumptions>();
  // session 235: scenario B as a PPA (a toll for a battery and a peaker): the whole plant at B's own breakeven price
  const ppa = f.twelve ? asPpa(s.b, f.twelve.revenueKw, contractOf(f)) : null;
  type Col = (typeof cols)["a"];
  const u = contractUnits(f.contract);
  const sourceOf = (k: Key) => (k === "capex" ? `${SPECS[k].source}, ${f.costs.capexNote}` : k === "fom" ? `${SPECS[k].source}, ${f.costs.fomNote}` : k === "life" || k === "term" ? `${SPECS[k].source}, ${f.costs.lifeNote}` : k === "deg" && f.costs.degSource ? f.costs.degSource : SPECS[k].source);

  const fields: Field[] = KEYS.map((k) => {
    const sp = SPECS[k];
    // session 212: the contract's units are the asset's (a share of the energy at a price per MWh; a toll on the capacity)
    const unit = k === "cshare" ? u.shareUnit : k === "cprice" ? u.priceUnit : sp.unit;
    return { key: k, label: sp.label, unit, min: sp.min, max: sp.max, whole: sp.whole, note: <>Default {plain(d[k])}. {sourceOf(k)}.</> };
  });
  const none = (why: string, v = "not held"): Cell => ({ v, raw: null, why });
  const noDebt: Cell = { v: "no debt", raw: null };
  const row = (key: string, label: string, note: string, cell: (c: Col) => Cell): Row => ({ key, label, note, cell: (p) => cell(cols[p]) });
  const contractNote = (c: Col) => (c.y.cshare > 0 ? `contract ${plain(c.y.cshare)} percent at USD ${plain(c.y.cprice)} ${u.priceUnit.replace("USD ", "")}; ` : "");
  const rows: Row[] = [
    row("revenue", `${f.money}, last twelve months`, "USD per kW, the market's",
      () => (f.twelve ? { v: `USD ${num(f.twelve.revenueKw)}`, raw: f.twelve.revenueKw, note: `${f.twelve.span}, priced at ${f.twelve.at}` } : none(f.twelveWhy))),
    row("capture", f.captureLabel, "USD per MWh, and its ratio to the flat average of every hour",
      () => (f.capture ? { v: `USD ${num(f.capture.price)}`, raw: f.capture.price, note: `${num(f.capture.ratio, 1)} percent of USD ${num(f.capture.flat)}; ${f.capture.words}` } : none(f.captureWhy))),
    row("month", "The worst month", `the lowest of the months held, for ${f.size}`,
      (c) => {
        if (!f.lowest) return none(f.twelveWhy);
        const cover = monthCoverage(c.y, f.lowest.usd / scale);
        return { v: usd(f.lowest.usd), raw: f.lowest.usd, note: `${f.lowest.month}, of ${f.lowest.months} months; ${cover === null ? "no debt" : `coverage that month ${num(cover)} times, in the market`}` };
      }),
    row("coverage", "Debt coverage", "last twelve months: the contract plus the market on the rest, less fixed O&M, over debt payments",
      (c) => (c.r ? (c.r.coverage === null ? noDebt : { v: `${num(c.r.coverage)} times`, raw: c.r.coverage, note: `${contractNote(c)}debt payments ${usd(c.r.debt * scale)} a year` }) : none(f.twelveWhy))),
    row("npv", "NPV at the hurdle rate", `to equity, for ${f.size}`,
      (c) => (c.r ? { v: usd(c.r.npv * scale), raw: c.r.npv, note: `USD ${num(c.r.npv)} per kW at ${plain(c.y.hurdle)} percent` } : none(f.twelveWhy))),
    row("irr", "IRR", "to equity, percent a year",
      (c) => (c.r ? (c.r.irr === null ? { v: "none", raw: null, note: "no rate from -99 to 1,000 percent sets NPV to zero" } : { v: `${num(c.r.irr, 1)} percent`, raw: c.r.irr }) : none(f.twelveWhy))),
    row("contract", `Contract price at which coverage reaches ${TARGET} times`,
      f.contract === "energy" ? "a contract for the whole of the energy, USD per MWh" : "a toll on the whole of the capacity, USD per kW-month",
      (c) => {
        if (f.contract === "toll") { const t = breakevenToll(c.y); return t === null ? noDebt : { v: `USD ${num(t)}`, raw: t }; }
        if (!f.twelve) return none(f.twelveWhy);
        const p = contractPrice(c.y, f.twelve.energyKw);
        return p === null ? noDebt : { v: `USD ${num(p)}`, raw: p, note: `on ${Math.round(f.twelve.energyKw * 1000).toLocaleString("en-US")} MWh a year per MW, ${f.twelve.span}` };
      }),
    // session 235: the breakeven PPA price, the contract price at which NPV is zero (lib/seller/finance.ts, breakevenPpa)
    row("ppa", f.contract === "energy" ? "Breakeven PPA price" : "Breakeven toll, NPV at zero",
      `the contract price at which NPV at the hurdle rate is zero, ${u.priceUnit}`,
      (c) => {
        if (!f.twelve) return none(f.twelveWhy);
        const share = ppaShare(c.y), p = breakevenPpa(c.y, f.twelve.revenueKw, contractOf(f));
        if (p === null) return none("The last twelve months hold no energy to price a contract on.", "none");
        const on = `on ${plain(share)} ${u.shareUnit} for the debt's ${plain(debtYears(c.y))} years${c.y.cshare > 0 ? "" : ", the scenario holding no contract"}`;
        if (p <= 0) return { v: "none needed", raw: p, note: `NPV is at or above zero with the contracted share paid nothing; ${on}` };
        return { v: `USD ${num(p)}`, raw: p, note: `${on}${c.y.cshare > 0 ? `; the scenario's own price is USD ${plain(c.y.cprice)}` : ""}` };
      }),
    row("battery", "Revenue with and without the battery beside it", "the co-optimized pair and the plant alone, energy at day-ahead prices",
      () => (f.battery ? { v: `${usd(f.battery.withIt)} with`, raw: f.battery.withIt, note: `${usd(f.battery.without)} without; ${f.battery.words}` } : none(f.batteryWhy, "not modeled"))),
  ];

  return (
    <ScenarioBlock
      fields={fields} defaults={d} bound={(k, v) => bound(k as Key, v, d)} head={`For ${f.size}`} rows={rows}
      differing={differing(s.a, s.b)} short={(k, v) => SPECS[k as Key].short(v)} differs={differenceWords(s.a, s.b)}
      sentence={cols.a.r ? (
        <p className="mt-3 max-w-3xl text-sm" data-npv-sentence="a">
          Scenario A, {f.size}: at a hurdle rate of {plain(s.a.hurdle)} percent, NPV is {usd(cols.a.r.npv * scale)}.
        </p>
      ) : null}
      chart={null}
      foot={(
        <p className="mt-4 border-t border-rule pt-3 text-xs text-muted" data-ppa="1">
          <button type="button" data-make-ppa="1" disabled={!ppa} className="mr-2 border border-accent bg-white px-3 py-1 text-accent disabled:text-muted"
            onClick={() => { if (ppa) update({ ...s, b: ppa, view: "b" }); }}>Make B a {f.contract === "energy" ? "PPA" : "toll"}</button>
          {ppa
            ? <>Sets scenario B&apos;s contract share to 100 {u.shareUnit} and its contract price to <span data-ppa-price={ppa.cprice}>USD {num(ppa.cprice)}</span> {u.priceUnit.replace("USD ", "")}: B&apos;s breakeven {f.contract === "energy" ? "PPA price" : "toll"}, the price at which its NPV is zero with its other assumptions as they are, rounded up to the cent. A starting point to move to an offer in hand; no published price is held. A and every default stay as they are.</>
            : <>Scenario B cannot be made a contract here: {f.twelve ? "the last twelve months hold no energy to price one on" : f.twelveWhy}</>}
        </p>
      )}
    />
  );
}

/** Session 212: the sensitivity chart of the scenario in view, in the page's third section, with one line on how to
 * read it (the battery page's BatterySensitivity). Drawn only when the scenario has a result. */
export function SellerSensitivity({ facts: f }: { facts: Facts }) {
  const { s, chart } = useBlock(f);
  if (!chart) return <p className="max-w-3xl text-sm text-muted" data-sensitivity-none="1">No twelve consecutive months are held, so there is no NPV to move.</p>;
  return (
    <>
      <p className="mb-2 max-w-3xl text-sm" data-how-to-read="1">
        Each row moves one assumption of scenario {s.view.toUpperCase()} down and up by the step named, holds the other nine, and draws where NPV lands from the
        scenario&apos;s own NPV (the line); the longest bars are the assumptions that matter most.
      </p>
      <Sensitivity c={chart} view={s.view} />
    </>
  );
}
