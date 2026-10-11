"use client";
// Session 186: the decisions block of /cost-of-power/seller, as session 179 built it for the battery. An assumptions
// panel (eight assumptions, each with its default, the default's source and a Reset), two scenarios A and B set side by
// side on the same eight rows, and a sensitivity chart for the scenario in view. Everything is computed in the browser
// (lib/seller/finance.ts) from figures the page already shows: the last twelve months at the hub chosen, the capture
// price, the months and the pair with a battery. A change sends no request: the address is rewritten in place
// (history.replaceState) so that a comparison can be shared as a link. No sentence here judges: each states a number.
// The formulas are in docs/methods/generator_earns_algorithm.md, section 11.
import { useEffect, useMemo, useState } from "react";
import { usdShort } from "@/lib/batterystack";
import {
  KEYS, SPECS, TARGET, bound, breakevenToll, contractPrice, defaultsOf, differenceWords, differing, isScenarioParam, monthCoverage, parseScenarios, resultOf, scenarioQuery, sensitivity,
  type Assumptions, type Bar, type Key, type Scenarios as Both, type View,
} from "@/lib/seller/finance";

const DOWN = "#2a78d6", UP = "#eb6834";  // app/tokens.css: the categorical slots 1 and 2 (fuel-gas, fuel-coal); neither is a verdict
const field = "w-full border border-rule bg-white px-2 py-1 text-sm";
const num = (v: number, d = 2) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
const plain = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const usd = (v: number) => `USD ${usdShort(Math.round(v))}`;

/** What the page hands the block: figures it already shows, for the grid, hub, asset and size chosen. A figure that is
 * not held is null and its reason is beside it. */
export type Facts = {
  /** `size` is the asset in words, with its size: "100 MW of solar", "a 100 MW gas peaker" */
  mw: number; size: string;
  costs: { capex: number; fom: number; life: number; capexNote: string; fomNote: string; lifeNote: string };
  /** the last twelve months at the hub chosen: revenue in USD per kW (a peaker: its margin over fuel), energy in MWh per kW */
  twelve: { revenueKw: number; energyKw: number; span: string; at: string } | null; twelveWhy: string;
  money: string;
  /** the headline's price beside it: the capture price (solar, wind), the price while selling or running (battery, peaker) */
  capture: { price: number; flat: number; ratio: number; words: string } | null; captureLabel: string; captureWhy: string;
  /** the lowest month of every month held, USD for the reader's size */
  lowest: { month: string; usd: number; months: number } | null;
  /** the contract row's unit: a price for the whole of the energy, or a toll on the whole asset */
  contract: "energy" | "toll";
  /** the co-optimized pair and the plant alone at day-ahead prices, USD for the reader's sizes */
  battery: { withIt: number; without: number; words: string } | null; batteryWhy: string;
};

/** One number field. The text typed is shown while it still reads as the value in force; otherwise the value is. */
function NumberField({ k, value, onValue, read }: { k: Key; value: number; onValue: (v: number) => void; read: (v: number) => number }) {
  const [text, setText] = useState<string | null>(null);
  const s = SPECS[k];
  const shown = text !== null && (text === "" || read(Number(text)) === value) ? text : String(value);
  return (
    <input type="number" inputMode="decimal" autoComplete="off" min={s.min} max={s.max} step={s.whole ? 1 : "any"} value={shown} className={field}
      data-assumption={k} aria-label={`${s.label}, ${s.unit}`}
      onChange={(e) => { setText(e.target.value); const v = Number(e.target.value); if (e.target.value !== "" && Number.isFinite(v)) onValue(v); }}
      onBlur={() => setText(null)} />
  );
}

/** The sensitivity chart: one row an assumption, two thin bars from the scenario's own NPV, sorted by size. */
function Sensitivity({ bars, mw, view, own }: { bars: Bar[]; mw: number; view: View; own: Assumptions }) {
  const [on, setOn] = useState<Key | null>(null);
  const scale = 1000 * mw;
  const all = bars.flatMap((b) => [b.base, b.down?.npv, b.up?.npv]).filter((v): v is number => v !== undefined && v !== null).map((v) => v * scale);
  const lo0 = Math.min(...all), hi0 = Math.max(...all);
  const pad = (hi0 - lo0) * 0.04 || 1;
  const lo = lo0 - pad, hi = hi0 + pad;
  const x = (v: number) => ((v * scale - lo) / (hi - lo)) * 100;
  const base = bars[0].base;
  const hit = bars.find((b) => b.key === on) ?? null;
  const says = (b: Bar) => {
    const side = (s: Bar["down"]) => (s ? `${usd(s.npv * scale)} at ${plain(s.value)}` : "no step inside its bounds");
    return `${b.label}, moved by ${b.step}: NPV is ${side(b.down)} and ${side(b.up)}; ${usd(b.base * scale)} at ${plain(own[b.key])}.`;
  };
  return (
    <figure className="mt-8" data-sensitivity={view}>
      <figcaption className="mb-2 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-1">
        <span className="font-serif text-lg text-accent">How far each assumption moves NPV, scenario {view.toUpperCase()}</span>
        <span className="flex flex-wrap gap-x-4 text-xs text-ink">
          <span className="inline-flex items-center gap-1.5"><span aria-hidden="true" className="inline-block h-2.5 w-2.5" style={{ background: DOWN }} />Lowered by the step</span>
          <span className="inline-flex items-center gap-1.5"><span aria-hidden="true" className="inline-block h-2.5 w-2.5" style={{ background: UP }} />Raised by the step</span>
        </span>
      </figcaption>
      <ul className="space-y-1" onMouseLeave={() => setOn(null)}>
        {bars.map((b) => {
          const bar = (s: Bar["down"], color: string, top: boolean) => {
            if (!s) return null;
            const a = x(Math.min(s.npv, b.base)), w = Math.abs(x(s.npv) - x(b.base));
            const right = s.npv >= b.base;
            return <span aria-hidden="true" className="absolute h-[6px]" style={{ left: `${a}%`, width: `${Math.max(w, 0.4)}%`, top: top ? 3 : 11, background: color, borderRadius: right ? "0 4px 4px 0" : "4px 0 0 4px" }} />;
          };
          return (
            <li key={b.key}>
              <button type="button" data-bar={b.key} data-size={b.size * scale} data-down={b.down ? b.down.npv * scale : ""} data-up={b.up ? b.up.npv * scale : ""}
                title={says(b)} onMouseEnter={() => setOn(b.key)} onFocus={() => setOn(b.key)} onClick={() => setOn(b.key)}
                className={`grid w-full items-center gap-x-3 gap-y-0.5 px-1 py-1 text-left text-xs sm:grid-cols-[280px_minmax(0,1fr)] ${on === b.key ? "bg-paper" : ""}`}>
                <span className="flex items-baseline justify-between gap-2">
                  <span><span className="text-sm text-ink">{b.label}</span> <span className="text-muted">by {b.step}</span></span>
                  <span className="whitespace-nowrap tabular-nums text-muted">{usd(b.size * scale)}</span>
                </span>
                <span className="relative block h-5 bg-panel">
                  {bar(b.down, DOWN, true)}
                  {bar(b.up, UP, false)}
                  <span aria-hidden="true" className="absolute top-0 h-5 border-l border-ink" style={{ left: `${x(base)}%` }} />
                </span>
              </button>
            </li>
          );
        })}
      </ul>
      <div className="mt-1 grid text-xs tabular-nums text-muted sm:grid-cols-[280px_minmax(0,1fr)] sm:gap-x-3">
        <span />
        <span className="flex justify-between px-1"><span>{usd(lo0)}</span><span>NPV, {usd(base * scale)} at the line</span><span>{usd(hi0)}</span></span>
      </div>
      <p className="mt-2 min-h-[2.5em] max-w-3xl text-sm" role="status" data-sensitivity-readout="1">
        {hit ? says(hit) : "Point at a row, or tab to it, for the two values."}
      </p>
      <details className="mt-1 text-xs">
        <summary className="cursor-pointer text-accent">The chart as a table</summary>
        <div className="overflow-x-auto">
          <table className="mt-2 w-full border-collapse text-left tabular-nums" style={{ minWidth: 480 }}>
            <thead><tr className="border-b border-rule"><th scope="col" className="py-1 pr-3 font-normal">Assumption</th><th scope="col" className="py-1 pr-3 font-normal">Step</th><th scope="col" className="py-1 pr-3 text-right font-normal">NPV, lowered</th><th scope="col" className="py-1 text-right font-normal">NPV, raised</th></tr></thead>
            <tbody>
              {bars.map((b) => (
                <tr key={b.key} className="border-b border-rule">
                  <th scope="row" className="py-1 pr-3 font-normal">{b.label}</th><td className="py-1 pr-3">{b.step}</td>
                  <td className="py-1 pr-3 text-right">{b.down ? `${usd(b.down.npv * scale)} at ${plain(b.down.value)}` : "no step inside its bounds"}</td>
                  <td className="py-1 text-right">{b.up ? `${usd(b.up.npv * scale)} at ${plain(b.up.value)}` : "no step inside its bounds"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </figure>
  );
}

export function SellerScenarios({ facts: f, initial }: { facts: Facts; initial: Record<string, string | undefined> }) {
  const d = useMemo(() => defaultsOf(f.costs), [f.costs]);
  const [s, setS] = useState<Both>(() => parseScenarios(initial, d));

  // the address keeps both scenarios; nothing is requested (the page's other parameters are left as they are)
  useEffect(() => {
    const cur = new URLSearchParams(window.location.search);
    const next = new URLSearchParams();
    for (const [k, v] of cur) if (!isScenarioParam(k)) next.append(k, v);
    for (const [k, v] of scenarioQuery(s, d)) next.set(k, v);
    const qs = next.toString();
    if (qs !== cur.toString()) window.history.replaceState(null, "", `${window.location.pathname}${qs ? `?${qs}` : ""}${window.location.hash}`);
  }, [s, d]);

  // No usage count is sent from here (lib/usage.ts, "scenario compared"): the contract box on this page says nothing
  // typed there is sent, and session 179 left the same call off the battery page for the owner's ruling.
  const update = (next: Both) => setS(next);
  const set = (k: Key, v: number) => update({ ...s, [s.view]: { ...s[s.view], [k]: bound(k, v, d) } });
  const a = s[s.view];
  const scale = 1000 * f.mw;
  const diff = differing(s.a, s.b);
  const col = (p: View) => ({ p, y: s[p], r: f.twelve ? resultOf(s[p], f.twelve.revenueKw) : null });
  const cols = [col("a"), col("b")];
  const inView = cols.find((c) => c.p === s.view)!;
  const bars = f.twelve ? sensitivity(a, f.twelve.revenueKw) : [];
  const sourceOf = (k: Key) => (k === "capex" ? `${SPECS[k].source}, ${f.costs.capexNote}` : k === "fom" ? `${SPECS[k].source}, ${f.costs.fomNote}` : k === "life" || k === "term" ? `${SPECS[k].source}, ${f.costs.lifeNote}` : SPECS[k].source);

  type Cell = { v: string; raw: number | null; note?: string; why?: string };
  const none = (why: string, v = "not held"): Cell => ({ v, raw: null, why });
  const noDebt: Cell = { v: "no debt", raw: null };
  const rows: { key: string; label: string; note: string; cell: (c: (typeof cols)[number]) => Cell }[] = [
    { key: "revenue", label: `${f.money}, last twelve months`, note: "USD per kW",
      cell: () => (f.twelve ? { v: `USD ${num(f.twelve.revenueKw)}`, raw: f.twelve.revenueKw, note: `${f.twelve.span}, priced at ${f.twelve.at}` } : none(f.twelveWhy)) },
    { key: "capture", label: f.captureLabel, note: "USD per MWh, and its ratio to the flat average of every hour",
      cell: () => (f.capture ? { v: `USD ${num(f.capture.price)}`, raw: f.capture.price, note: `${num(f.capture.ratio, 1)} percent of USD ${num(f.capture.flat)}; ${f.capture.words}` } : none(f.captureWhy)) },
    { key: "month", label: "The worst month", note: `the lowest of the months held, for ${f.size}`,
      cell: (c) => {
        if (!f.lowest) return none(f.twelveWhy);
        const cover = monthCoverage(c.y, f.lowest.usd / scale);
        return { v: usd(f.lowest.usd), raw: f.lowest.usd, note: `${f.lowest.month}, of ${f.lowest.months} months; ${cover === null ? "no debt" : `coverage that month ${num(cover)} times`}` };
      } },
    { key: "coverage", label: "Debt coverage", note: "last twelve months: revenue less fixed O&M, over debt payments",
      cell: (c) => (c.r ? (c.r.coverage === null ? noDebt : { v: `${num(c.r.coverage)} times`, raw: c.r.coverage, note: `debt payments ${usd(c.r.debt * scale)} a year` }) : none(f.twelveWhy)) },
    { key: "npv", label: "NPV at the hurdle rate", note: `to equity, for ${f.size}`,
      cell: (c) => (c.r ? { v: usd(c.r.npv * scale), raw: c.r.npv, note: `USD ${num(c.r.npv)} per kW at ${plain(c.y.hurdle)} percent` } : none(f.twelveWhy)) },
    { key: "irr", label: "IRR", note: "to equity, percent a year",
      cell: (c) => (c.r ? (c.r.irr === null ? { v: "none", raw: null, note: "no rate from -99 to 1,000 percent sets NPV to zero" } : { v: `${num(c.r.irr, 1)} percent`, raw: c.r.irr }) : none(f.twelveWhy)) },
    { key: "contract", label: `Contract price at which coverage reaches ${TARGET} times`,
      note: f.contract === "energy" ? "a contract for the whole of the energy, USD per MWh" : "a toll on the whole of the capacity, USD per kW-month",
      cell: (c) => {
        if (f.contract === "toll") { const t = breakevenToll(c.y); return t === null ? noDebt : { v: `USD ${num(t)}`, raw: t }; }
        if (!f.twelve) return none(f.twelveWhy);
        const p = contractPrice(c.y, f.twelve.energyKw);
        return p === null ? noDebt : { v: `USD ${num(p)}`, raw: p, note: `on ${Math.round(f.twelve.energyKw * 1000).toLocaleString("en-US")} MWh a year per MW, ${f.twelve.span}` };
      } },
    { key: "battery", label: "Revenue with and without the battery beside it", note: "the co-optimized pair and the plant alone, energy at day-ahead prices",
      cell: () => (f.battery ? { v: `${usd(f.battery.withIt)} with`, raw: f.battery.withIt, note: `${usd(f.battery.without)} without; ${f.battery.words}` } : none(f.batteryWhy, "not modeled")) },
  ];
  const tab = (p: View) => (
    <button key={p} type="button" aria-pressed={s.view === p} data-view={p} onClick={() => update({ ...s, view: p })}
      style={s.view === p ? { color: "#fff" } : undefined}
      className={`px-4 py-1.5 text-sm ${p === "b" ? "border-l border-accent" : ""} ${s.view === p ? "bg-accent font-semibold" : "bg-white text-accent"}`}>
      Scenario {p.toUpperCase()}
    </button>
  );

  return (
    <div data-scenarios="1">
      <div className="mb-4 bg-paper px-4 py-4" data-assumptions={s.view}>
        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
          <div className="inline-grid grid-cols-2 border border-accent" role="group" aria-label="The scenario in view">{tab("a")}{tab("b")}</div>
          <div className="flex flex-wrap gap-2 text-xs">
            <button type="button" data-copy="1" className="border border-accent bg-white px-3 py-1 text-accent" onClick={() => update({ ...s, b: { ...s.a } })}>Copy A to B</button>
            <button type="button" data-reset-all="1" className="border border-accent bg-white px-3 py-1 text-accent" onClick={() => update({ ...s, [s.view]: { ...d } })}>Reset all of {s.view.toUpperCase()}</button>
          </div>
        </div>
        <div className="grid gap-x-6 gap-y-3 sm:grid-cols-2">
          {KEYS.map((k) => {
            const sp = SPECS[k];
            return (
              <div key={`${s.view}-${k}`} className="text-sm" data-field={k}>
                <div className="mb-1 font-semibold">{sp.label}, <span className="font-normal">{sp.unit}</span></div>
                <div className="flex items-center gap-2">
                  <NumberField k={k} value={a[k]} onValue={(v) => set(k, v)} read={(v) => bound(k, v, d)} />
                  <button type="button" data-reset={k} disabled={a[k] === d[k]} className="whitespace-nowrap border border-rule bg-white px-2 py-1 text-xs text-accent disabled:text-muted" onClick={() => set(k, d[k])}>Reset</button>
                </div>
                <p className="mt-1 text-xs leading-snug text-muted" data-default={d[k]}>Default {plain(d[k])}. {sourceOf(k)}.</p>
              </div>
            );
          })}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="block w-full border-collapse text-left text-sm tabular-nums sm:table" data-scenario-table="1">
          <caption className="sr-only">Scenarios A and B</caption>
          <thead className="block sm:table-header-group">
            <tr className="grid grid-cols-2 bg-accent align-top text-white sm:table-row">
              <th scope="col" className="col-span-2 px-3 py-1.5 font-normal sm:table-cell">For {f.size}</th>
              {cols.map((c) => (
                <th key={c.p} scope="col" className="px-3 py-1.5 text-right font-normal sm:table-cell" data-head={c.p}>
                  <span className="font-semibold">{c.p.toUpperCase()}</span>
                  {diff.map((k) => <span key={k} className="block text-xs opacity-90" data-differs={k}>{SPECS[k].short(c.y[k])}</span>)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="block sm:table-row-group">
            {rows.map((r) => (
              <tr key={r.key} className="grid grid-cols-2 border-b border-rule align-top sm:table-row" data-row={r.key}>
                <th scope="row" className="col-span-2 px-3 pb-0 pt-1.5 font-normal sm:table-cell sm:pb-1.5">{r.label}<div className="text-xs font-normal text-muted">{r.note}</div></th>
                {cols.map((c) => {
                  const cell = r.cell(c);
                  return (
                    <td key={c.p} className="px-3 py-1.5 text-right sm:table-cell" data-cell={`${c.p}|${r.key}`} data-raw={cell.raw === null ? "" : String(cell.raw)}>
                      {cell.why ? <span className="cursor-help border-b border-dotted border-muted italic text-muted" title={cell.why} data-missing="1">{cell.v}</span> : cell.v}
                      {cell.note ? <div className="text-xs text-muted">{cell.note}</div> : null}
                    </td>
                  );
                })}
              </tr>
            ))}
            <tr className="grid grid-cols-2 border-b border-rule bg-paper sm:table-row" data-row="differs">
              <th scope="row" className="col-span-2 px-3 pb-0 pt-1.5 font-normal sm:table-cell sm:pb-1.5">What differs</th>
              <td colSpan={2} className="col-span-2 px-3 py-1.5 text-left sm:table-cell" data-differs-words="1">{differenceWords(s.a, s.b)}</td>
            </tr>
          </tbody>
        </table>
      </div>
      {inView.r ? (
        <p className="mt-3 max-w-3xl text-sm" data-npv-sentence={s.view}>
          Scenario {s.view.toUpperCase()}, {f.size}: at a hurdle rate of {plain(a.hurdle)} percent, NPV is {usd(inView.r.npv * scale)}.
        </p>
      ) : null}
      {bars.length ? <Sensitivity bars={bars} mw={f.mw} view={s.view} own={a} /> : null}
    </div>
  );
}
