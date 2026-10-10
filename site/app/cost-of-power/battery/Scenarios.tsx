"use client";
// Session 179: the decisions block of /cost-of-power/battery. An assumptions panel (ten assumptions, each with its
// default, the default's source and a Reset), two scenarios A and B set side by side on the same seven rows, and a
// sensitivity chart for the scenario in view. Everything is computed in the browser from the months already on the
// page (lib/battery/finance.ts; the two assumptions inside the model, efficiency and cycles a day, take only the steps
// the model itself was run at, data/battery_scenario_steps.json). A change sends no request: the address is rewritten
// in place (history.replaceState) so that a comparison can be shared as a link. No sentence here judges: each states a
// number. The formulas are in docs/methods/battery_earns_algorithm.md, section 11.1.
import { useEffect, useMemo, useState } from "react";
import { badMonth, last36, lastTwelve, monthName, sumOf, usdShort, type Inputs, type Month } from "@/lib/batterystack";
import {
  KEYS, MODEL, SPECS, bound, cellTotals, defaultsOf, differenceWords, differing, isScenarioParam, parseScenarios, resultOf, scenarioQuery, sensitivity,
  stepState, stepsOffered, type Assumptions, type Bar, type Key, type Scenarios as Both, type StepCase, type View,
} from "@/lib/battery/finance";

const DOWN = "#2a78d6", UP = "#eb6834";  // app/tokens.css: the categorical slots 1 and 2 (fuel-gas, fuel-coal); neither is a verdict
const field = "w-full border border-rule bg-white px-2 py-1 text-sm";
const num = (v: number, d = 2) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
const plain = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const usd = (v: number) => `USD ${usdShort(Math.round(v))}`;
const day = (iso: string) => new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });

type Revenue = { l12: number | null; first: string | null; last: string | null; bad: Month | null; n36: number };

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
    const side = (s: Bar["down"]) => (s ? `${usd(s.npv * scale)} at ${plain(s.value)}` : "no step held");
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
                  <span className="whitespace-nowrap tabular-nums text-muted">{b.size > 0 ? usd(b.size * scale) : "no step held"}</span>
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
                  <td className="py-1 pr-3 text-right">{b.down ? `${usd(b.down.npv * scale)} at ${plain(b.down.value)}` : "no step held"}</td>
                  <td className="py-1 text-right">{b.up ? `${usd(b.up.npv * scale)} at ${plain(b.up.value)}` : "no step held"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </figure>
  );
}

export function Scenarios({ ms, x, costs, gridName, stepCase, stepMeta, initial }: {
  ms: Month[]; x: Inputs; costs: { capex: number; fom: number; note: string }; gridName: string;
  stepCase: StepCase | null; stepMeta: { built: string; rte_steps: number[]; cycle_steps: number[] }; initial: Record<string, string | undefined>;
}) {
  const d = useMemo(() => defaultsOf(costs), [costs]);
  // the months the page's own windows read: a step is offered only while the file of steps still describes them
  const need = useMemo(() => (last36(ms)?.months ?? []).map((r) => r.m), [ms]);
  const state = useMemo(() => stepState(stepCase, ms, need), [stepCase, ms, need]);
  const steps = useMemo(() => stepsOffered(stepMeta, state), [stepMeta, state]);
  const [s, setS] = useState<Both>(() => parseScenarios(initial, d, steps));

  // the address keeps both scenarios; nothing is requested (the page's other parameters are left as they are)
  useEffect(() => {
    const cur = new URLSearchParams(window.location.search);
    const next = new URLSearchParams();
    for (const [k, v] of cur) if (!isScenarioParam(k)) next.append(k, v);
    for (const [k, v] of scenarioQuery(s, d)) next.set(k, v);
    const qs = next.toString();
    if (qs !== cur.toString()) window.history.replaceState(null, "", `${window.location.pathname}${qs ? `?${qs}` : ""}${window.location.hash}`);
  }, [s, d]);

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
        out = { l12: l12 ? sumOf(l12, "total") / 1000 : null, first: l12 ? l12[0].m : null, last: l12 ? l12[11].m : null, bad: badMonth(w?.months ?? []), n36: w?.months.length ?? 0 };
      }
      memo.set(k, out);
      return out;
    };
  }, [ms, need, state, stepCase]);

  const update = (next: Both) => {
    // session 179: track("scenario compared") goes here once site/lib/usage.ts is on main
    // Once a page view, when a change first makes B differ from A:
    //   if (!compared.current && differing(next.a, next.b).length > 0) { compared.current = true; track("scenario compared"); }
    // with `const compared = useRef(differing(s.a, s.b).length > 0);` beside the state, so that a shared link which
    // already compares sends nothing when it is merely opened or edited. The count carries the event and the path only
    // (lib/usage.ts). It is the one request a reader's action on this page would cause: the automatic counts are
    // silent here because the contract box says nothing typed there is sent (components/Usage.tsx, PROMISE), and this
    // block sits outside that box. scripts/check-battery-scenarios.mjs allows that one count and nothing else.
    setS(next);
  };
  const set = (k: Key, v: number) => update({ ...s, [s.view]: { ...s[s.view], [k]: bound(k, v, d, steps) } });
  const a = s[s.view];
  const size = `${x.mw.toLocaleString("en-US")} MW, ${x.dur}-hour`;
  const scale = 1000 * x.mw;
  const diff = differing(s.a, s.b);
  const col = (p: View) => {
    const y = s[p], rev = revenue(y.rte, y.cycles);
    return { p, y, rev, r: rev && rev.l12 !== null ? resultOf(y, rev.l12) : null };
  };
  const cols = [col("a"), col("b")];
  const inView = cols.find((c) => c.p === s.view)!;
  const bars = inView.r ? sensitivity(a, (rte, cycles) => revenue(rte, cycles)?.l12 ?? null, steps) : [];
  const sourceOf = (k: Key) => (k === "capex" || k === "fom" ? `${SPECS[k].source}: ${costs.note}` : SPECS[k].source);

  type Cell = { v: string; raw: number | null; note?: string };
  const none: Cell = { v: "not held", raw: null };
  const rows: { key: string; label: string; note: string; cell: (c: (typeof cols)[number]) => Cell }[] = [
    { key: "revenue", label: "Revenue, last twelve months", note: "USD per kW",
      cell: (c) => (c.rev && c.rev.l12 !== null ? { v: `USD ${num(c.rev.l12)}`, raw: c.rev.l12, note: `${monthName(c.rev.first!)} to ${monthName(c.rev.last!)}` } : none) },
    { key: "p10", label: "The 10th-percentile month", note: `for ${size}, last 36 months`,
      cell: (c) => (c.rev?.bad ? { v: usd(c.rev.bad.total! * x.mw), raw: Math.round(c.rev.bad.total! * x.mw), note: `${monthName(c.rev.bad.m)}, of ${c.rev.n36} months` } : none) },
    { key: "coverage", label: "Debt coverage", note: "last twelve months: revenue less fixed O&M, over debt payments",
      cell: (c) => (c.r ? (c.r.coverage === null ? { v: "no debt", raw: null } : { v: `${num(c.r.coverage)} times`, raw: c.r.coverage, note: `debt payments ${usd(c.r.debt * scale)} a year` }) : none) },
    { key: "npv", label: "NPV at the hurdle rate", note: `to equity, for ${size}`,
      cell: (c) => (c.r ? { v: usd(c.r.npv * scale), raw: c.r.npv, note: `USD ${num(c.r.npv)} per kW at ${plain(c.y.hurdle)} percent` } : none) },
    { key: "irr", label: "IRR", note: "to equity, percent a year",
      cell: (c) => (c.r ? (c.r.irr === null ? { v: "none", raw: null, note: "no rate from -99 to 1,000 percent sets NPV to zero" } : { v: `${num(c.r.irr, 1)} percent`, raw: c.r.irr }) : none) },
    { key: "toll", label: "Breakeven toll", note: "a toll on the whole battery: the price at which coverage reaches 1.25 times, USD per kW-month",
      cell: (c) => (c.r ? (c.r.toll === null ? { v: "no debt", raw: null } : { v: `USD ${num(c.r.toll)}`, raw: c.r.toll }) : none) },
    { key: "tail", label: "Merchant tail after the contract", note: `the years after the debt's term, for ${size}, at the hurdle rate`,
      cell: (c) => (c.r ? { v: usd(c.r.tail.pv * scale), raw: c.r.tail.pv, note: c.r.tail.years > 0 ? `years ${c.r.tail.from} to ${c.r.tail.to}` : `0 years: the term and the life are both ${plain(c.y.life)} years` } : none) },
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
            const stepped = k === "rte" || k === "cycles";
            return (
              <div key={`${s.view}-${k}`} className="text-sm" data-field={k}>
                <div className="mb-1 font-semibold">{sp.label}, <span className="font-normal">{sp.unit}</span></div>
                <div className="flex items-center gap-2">
                  {stepped ? (
                    <select value={a[k]} className={field} data-assumption={k} aria-label={`${sp.label}, ${sp.unit}`} onChange={(e) => set(k, Number(e.target.value))}>
                      {steps[k].map((v) => <option key={v} value={v}>{plain(v)}</option>)}
                    </select>
                  ) : (
                    <NumberField k={k} value={a[k]} onValue={(v) => set(k, v)} read={(v) => bound(k, v, d, steps)} />
                  )}
                  <button type="button" data-reset={k} disabled={a[k] === d[k]} className="whitespace-nowrap border border-rule bg-white px-2 py-1 text-xs text-accent disabled:text-muted" onClick={() => set(k, d[k])}>Reset</button>
                </div>
                <p className="mt-1 text-xs leading-snug text-muted" data-default={d[k]}>Default {plain(d[k])}. {sourceOf(k)}.</p>
              </div>
            );
          })}
        </div>
        <p className="mt-3 text-xs leading-snug text-muted" data-steps={state.ok ? "held" : state.why}>
          {state.ok
            ? `Round-trip efficiency and cycles a day take the steps the model was run at on ${day(stepMeta.built)}.`
            : state.why === "none"
              ? `Round-trip efficiency and cycles a day: only the model's own step is held for ${gridName}.`
              : state.why === "months"
                ? `Round-trip efficiency and cycles a day: only the model's own step is offered. The other steps are held for months to ${monthName(state.fileLast!)}; the table now reaches ${monthName(state.liveLast!)}.`
                : `Round-trip efficiency and cycles a day: only the model's own step is offered. The other steps were run on ${day(stepMeta.built)}, and a month of the table has changed since.`}
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="block w-full border-collapse text-left text-sm tabular-nums sm:table" data-scenario-table="1">
          <caption className="sr-only">Scenarios A and B</caption>
          <thead className="block sm:table-header-group">
            <tr className="grid grid-cols-2 bg-accent align-top text-white sm:table-row">
              <th scope="col" className="col-span-2 px-3 py-1.5 font-normal sm:table-cell">For {size}</th>
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
                      {cell.v}{cell.note ? <div className="text-xs text-muted">{cell.note}</div> : null}
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
          Scenario {s.view.toUpperCase()}, {size}: at a hurdle rate of {plain(a.hurdle)} percent, NPV is {usd(inView.r.npv * scale)}.
        </p>
      ) : null}
      {bars.length ? <Sensitivity bars={bars} mw={x.mw} view={s.view} own={a} /> : null}
    </div>
  );
}
