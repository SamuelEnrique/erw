"use client";
// Session 194: the decisions block of /cost-of-power, as session 179 built it for the battery and session 186 for the
// generator. An assumptions panel (eight assumptions, each with its default, the default's source and a Reset), two
// scenarios A and B set side by side on the same eight rows, a row that sets B against A, and a sensitivity chart for
// the scenario in view. Everything is computed in the browser (lib/datacenter/finance.ts) from figures the server
// already computed for this page: the last twelve months of the load run flat and run flexible, and the bad month of
// each. A change sends no request: the address is rewritten in place (history.replaceState) so that a comparison can be
// shared as a link. No sentence here judges: each states a number. The formulas are in
// docs/methods/datacenter_pays_algorithm.md, section 4.14.
import { useEffect, useMemo, useState } from "react";
import { monthName, two, usdShort, whole } from "@/lib/datacenter";
import {
  FLAT, FLEX, KEYS, SPECS, against, bound, defaultsOf, differenceWords, differing, held, isScenarioParam, parseScenarios, resultOf, scenarioQuery, sensitivity, wayOf,
  type Assumptions, type Bar, type Key, type Scenarios as Both, type View, type Ways,
} from "@/lib/datacenter/finance";

const DOWN = "#2a78d6", UP = "#eb6834";  // app/tokens.css: the categorical slots 1 and 2 (fuel-gas, fuel-coal); neither is a verdict
const field = "w-full border border-rule bg-white px-2 py-1 text-sm";
const plain = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const usd = (v: number) => `USD ${usdShort(Math.round(v))}`;
const four = (v: number) => `USD ${v.toFixed(4)}`;

/** What the page hands the block: figures it already computed, for the grid, region, market and size chosen. A way of
 * running that is not held is null in `ways` and its reason is beside it. */
export type Facts = {
  /** `size` is the load's size in words ("100 MW"), `place` where it is and how it buys ("LZ_NORTH in ERCOT, real time") */
  mw: number; size: string; place: string; span: string | null;
  /** "Your load": how it runs (0 flat, 1 flexible), its power per GPU and overhead ratio, and the source of each default */
  load: { run: number; gpu: number; pue: number }; gpuSource: string; pueSource: string;
  ways: Ways;
  /** each way in words, and why a way is not held */
  words: [string, string]; why: [string, string];
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

/** The sensitivity chart: one row an assumption, two thin bars from the scenario's own figure, sorted by size. */
function Sensitivity({ bars, view, own, words }: { bars: Bar[]; view: View; own: Assumptions; words: [string, string] }) {
  const [on, setOn] = useState<Key | null>(null);
  const all = bars.flatMap((b) => [b.base, b.down?.v, b.up?.v]).filter((v): v is number => v !== undefined && v !== null);
  const lo0 = Math.min(...all), hi0 = Math.max(...all);
  const pad = (hi0 - lo0) * 0.04 || 0.0001;
  const lo = lo0 - pad, hi = hi0 + pad;
  const x = (v: number) => ((v - lo) / (hi - lo)) * 100;
  const base = bars[0].base;
  const hit = bars.find((b) => b.key === on) ?? null;
  const says = (b: Bar) => {
    if (b.key === "run") {
      const s = b.down ?? b.up;
      return s ? `How the load runs, the other way (${words[s.value]}): ${four(s.v)} per GPU-hour; ${four(b.base)} as it is (${words[own.run]}).` : "How the load runs: the other way is not held here, so it has no step.";
    }
    const side = (s: Bar["down"]) => (s ? `${four(s.v)} at ${plain(s.value)}` : "no step inside its bounds");
    return `${b.label}, moved by ${b.step}: all-in power per GPU-hour is ${side(b.down)} and ${side(b.up)}; ${four(b.base)} at ${plain(own[b.key])}.`;
  };
  return (
    <figure className="mt-8" data-sensitivity={view}>
      <figcaption className="mb-2 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-1">
        <span className="font-serif text-lg text-accent">How far each assumption moves all-in power per GPU-hour, scenario {view.toUpperCase()}</span>
        <span className="flex flex-wrap gap-x-4 text-xs text-ink">
          <span className="inline-flex items-center gap-1.5"><span aria-hidden="true" className="inline-block h-2.5 w-2.5" style={{ background: DOWN }} />Lowered by the step</span>
          <span className="inline-flex items-center gap-1.5"><span aria-hidden="true" className="inline-block h-2.5 w-2.5" style={{ background: UP }} />Raised by the step</span>
        </span>
      </figcaption>
      <ul className="space-y-1" onMouseLeave={() => setOn(null)}>
        {bars.map((b) => {
          const bar = (s: Bar["down"], color: string, top: boolean) => {
            if (!s) return null;
            const a = x(Math.min(s.v, b.base)), w = Math.abs(x(s.v) - x(b.base));
            const right = s.v >= b.base;
            return <span aria-hidden="true" className="absolute h-[6px]" style={{ left: `${a}%`, width: `${Math.max(w, 0.4)}%`, top: top ? 3 : 11, background: color, borderRadius: right ? "0 4px 4px 0" : "4px 0 0 4px" }} />;
          };
          return (
            <li key={b.key}>
              <button type="button" data-bar={b.key} data-size={b.size} data-down={b.down ? b.down.v : ""} data-up={b.up ? b.up.v : ""}
                title={says(b)} onMouseEnter={() => setOn(b.key)} onFocus={() => setOn(b.key)} onClick={() => setOn(b.key)}
                className={`grid w-full items-center gap-x-3 gap-y-0.5 px-1 py-1 text-left text-xs sm:grid-cols-[300px_minmax(0,1fr)] ${on === b.key ? "bg-paper" : ""}`}>
                <span className="flex items-baseline justify-between gap-2">
                  <span><span className="text-sm text-ink">{b.label}</span> <span className="text-muted">{b.key === "run" ? b.step : `by ${b.step}`}</span></span>
                  <span className="whitespace-nowrap tabular-nums text-muted">{four(b.size)}</span>
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
      <div className="mt-1 grid text-xs tabular-nums text-muted sm:grid-cols-[300px_minmax(0,1fr)] sm:gap-x-3">
        <span />
        <span className="flex justify-between px-1"><span>{four(lo0)}</span><span>per GPU-hour, {four(base)} at the line</span><span>{four(hi0)}</span></span>
      </div>
      <p className="mt-2 min-h-[2.5em] max-w-3xl text-sm" role="status" data-sensitivity-readout="1">
        {hit ? says(hit) : "Point at a row, or tab to it, for the two values."}
      </p>
      <details className="mt-1 text-xs">
        <summary className="cursor-pointer text-accent">The chart as a table</summary>
        <div className="overflow-x-auto">
          <table className="mt-2 w-full border-collapse text-left tabular-nums" style={{ minWidth: 480 }}>
            <thead><tr className="border-b border-rule"><th scope="col" className="py-1 pr-3 font-normal">Assumption</th><th scope="col" className="py-1 pr-3 font-normal">Step</th><th scope="col" className="py-1 pr-3 text-right font-normal">Per GPU-hour, lowered</th><th scope="col" className="py-1 text-right font-normal">Per GPU-hour, raised</th></tr></thead>
            <tbody>
              {bars.map((b) => {
                const side = (s: Bar["down"]) => (s ? `${four(s.v)} at ${b.key === "run" ? words[s.value] : plain(s.value)}` : b.key === "run" ? "" : "no step inside its bounds");
                return (
                  <tr key={b.key} className="border-b border-rule">
                    <th scope="row" className="py-1 pr-3 font-normal">{b.label}</th><td className="py-1 pr-3">{b.step}</td>
                    <td className="py-1 pr-3 text-right">{side(b.down)}</td>
                    <td className="py-1 text-right">{side(b.up)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </details>
    </figure>
  );
}

export function LoadScenarios({ facts: f, initial }: { facts: Facts; initial: Record<string, string | undefined> }) {
  const d = useMemo(() => defaultsOf(f.load), [f.load]);
  const open = useMemo(() => held(f.ways), [f.ways]);
  const [s, setS] = useState<Both>(() => parseScenarios(initial, d, open));

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
  // typed there is sent, and sessions 179 and 186 left the same call off their pages for the owner's ruling.
  const update = (next: Both) => setS(next);
  const set = (k: Key, v: number) => update({ ...s, [s.view]: { ...s[s.view], [k]: bound(k, v, d) } });
  const a = s[s.view];
  const diff = differing(s.a, s.b);
  const col = (p: View) => { const w = wayOf(s[p], f.ways); return { p, y: s[p], w, r: w ? resultOf(s[p], w) : null }; };
  const cols = [col("a"), col("b")];
  const inView = cols.find((c) => c.p === s.view)!;
  const bars = sensitivity(a, f.ways);
  const sourceOf = (k: Key) => {
    if (k === "gpu" || k === "pue") {
      const cited = k === "gpu" ? f.gpuSource : f.pueSource;
      return cited.replace(/\.$/, "");
    }
    return SPECS[k].source;
  };
  const rising = (g: number) => `${g > 0 ? "rising" : "falling"} ${plain(Math.abs(g))} percent a year`;

  type Cell = { v: string; raw: number | null; note?: string; why?: string };
  type Col = (typeof cols)[number];
  const none = (c: Col): Cell => ({ v: "not held", raw: null, why: f.why[c.y.run === FLEX ? FLEX : FLAT] });
  const rows: { key: string; label: string; note: string; cell: (c: Col) => Cell }[] = [
    { key: "price", label: "Market energy, last twelve months", note: "USD per MWh consumed",
      cell: (c) => (c.w ? { v: `USD ${two(c.w.per)}`, raw: c.w.per, note: `${f.span ? `${f.span}; ` : ""}${f.words[c.y.run]}` } : none(c)) },
    { key: "bill", label: "A year's energy", note: `for ${f.size}, the last twelve months`,
      cell: (c) => (c.r && c.w ? { v: usd(c.r.bill * f.mw), raw: c.r.bill, note: `${whole(c.w.energy * f.mw)} MWh${c.y.adder > 0 ? `, with USD ${plain(c.y.adder)} per MWh of other charges` : ""}` } : none(c)) },
    { key: "gpu", label: "Power per GPU-hour", note: "USD, for power alone",
      cell: (c) => (c.r ? { v: four(c.r.gpuHour), raw: c.r.gpuHour, note: `${whole(c.r.gpus * f.mw)} GPUs at ${plain(c.y.gpu)} kW and an overhead ratio of ${plain(c.y.pue)}` } : none(c)) },
    { key: "bad", label: "A bad month", note: "market energy, USD per MWh: one month in ten of the last 36 cost this or more",
      cell: (c) => (c.w ? (c.w.bad ? { v: `USD ${two(c.w.bad.per)}`, raw: c.w.bad.per, note: `${monthName(c.w.bad.m)}, of ${c.w.of} months; ${usd(c.w.bad.cost * f.mw)} that month` } : { v: "not held", raw: null, why: "No complete month is held to rank." }) : none(c)) },
    { key: "off", label: "Hours off, and the breakeven value of a GPU-hour", note: "what the power not bought would have cost, per GPU-hour not run",
      cell: (c) => {
        if (!c.r || !c.w) return none(c);
        if (!c.r.off) return { v: "none", raw: null, note: c.y.run === FLEX ? "the energy is moved within each day; no hour is off" : "a flat load runs in every hour" };
        return { v: four(c.r.off.perGpuHour), raw: c.r.off.perGpuHour, note: `off in ${whole(c.r.off.hours)} hours; USD ${two(c.r.off.perMwh)} per MWh not bought; an hour off saves more than it gives up when a GPU-hour earns less than this` };
      } },
    { key: "pv", label: "Present value of the cost, at the hurdle rate", note: `the upfront cost and every year counted, for ${f.size}`,
      cell: (c) => (c.r ? { v: usd(c.r.pv * f.mw), raw: c.r.pv, note: `${plain(c.y.life)} years at ${plain(c.y.hurdle)} percent${c.y.upfront > 0 ? `; USD ${plain(c.y.upfront)} per kW upfront` : ""}${c.y.growth !== 0 ? `; prices ${rising(c.y.growth)}` : ""}` } : none(c)) },
    { key: "level", label: "Fixed price with the same present value", note: "a contract for the whole of the energy, USD per MWh: its breakeven against the market",
      cell: (c) => (c.r && c.w ? { v: `USD ${two(c.r.level)}`, raw: c.r.level, note: c.y.growth === 0 ? "the last twelve months' price, repeated every year" : `the market's USD ${two(c.w.per)}, ${rising(c.y.growth)} for ${plain(c.y.life)} years` } : none(c)) },
    { key: "allin", label: "All-in power per GPU-hour, over the years counted", note: "the upfront cost and the energy, over the GPU-hours run, both at the hurdle rate",
      cell: (c) => (c.r ? { v: four(c.r.allIn), raw: c.r.allIn, note: `${whole(c.r.gpuHours * f.mw)} GPU-hours a year` } : none(c)) },
  ];

  // B set against A, in sentences that state numbers
  const [ca, cb] = cols;
  const versus = (() => {
    if (!ca.w || !cb.w || !ca.r || !cb.r) return "Not held for both scenarios.";
    if (!diff.length) return "No difference.";
    const g = against(ca.y, ca.w, cb.y, cb.w);
    const side = (v: number, lower: string, higher: string) => (v < 0 ? lower : higher);
    const out: string[] = [];
    out.push(g.bill === 0 ? `A year's energy is ${usd(ca.r.bill * f.mw)} in both.` : `A year's energy: ${usd(ca.r.bill * f.mw)} in A, ${usd(cb.r.bill * f.mw)} in B, so B is ${usd(Math.abs(g.bill) * f.mw)} ${side(g.bill, "lower", "higher")}.`);
    if (Math.round(g.gpuHours * f.mw) !== 0) out.push(`B runs ${whole(Math.abs(g.gpuHours) * f.mw)} ${side(g.gpuHours, "fewer", "more")} GPU-hours a year (${whole(cb.r.gpuHours * f.mw)} against ${whole(ca.r.gpuHours * f.mw)}).`);
    const own = ca.y.life !== cb.y.life || ca.y.hurdle !== cb.y.hurdle ? ", each over its own years and at its own hurdle rate" : ` over ${plain(ca.y.life)} years at ${plain(ca.y.hurdle)} percent`;
    out.push(g.pv === 0 ? `The present value of the cost is the same${own}.` : `Present value of the cost: B is ${usd(Math.abs(g.pv) * f.mw)} ${side(g.pv, "lower", "higher")}${own}.`);
    out.push(g.evenUpfront >= 0
      ? `The two have the same present value when B's upfront cost is USD ${plain(Math.round(g.evenUpfront * 100) / 100)} per kW (it is ${plain(cb.y.upfront)}).`
      : "No upfront cost of B gives the two the same present value: B's is the higher with none.");
    if (g.more) {
      const m = g.more.toUpperCase(), hurdle = plain(g.more === "b" ? cb.y.hurdle : ca.y.hurdle);
      out.push(!g.sameYears ? `${m} costs USD ${plain(g.extra)} per kW more upfront; no rate of return is stated, because the two count different years.`
        : g.rate === null ? `${m} costs USD ${plain(g.extra)} per kW more upfront; no rate from -99 to 1,000 percent sets that against its yearly cost.`
        : `${m} costs USD ${plain(g.extra)} per kW more upfront, which returns ${g.rate.toFixed(1)} percent a year in lower yearly cost; ${m}'s hurdle rate is ${hurdle} percent.`);
    }
    return out.join(" ");
  })();
  const versusRate = (() => { if (!ca.w || !cb.w || !diff.length) return ""; const g = against(ca.y, ca.w, cb.y, cb.w); return g.rate === null ? "" : String(g.rate); })();
  const versusEven = (() => { if (!ca.w || !cb.w || !diff.length) return ""; return String(against(ca.y, ca.w, cb.y, cb.w).evenUpfront); })();

  const tab = (p: View) => (
    <button key={p} type="button" aria-pressed={s.view === p} data-view={p} onClick={() => update({ ...s, view: p })}
      style={s.view === p ? { color: "#fff" } : undefined}
      className={`px-4 py-1.5 text-sm ${p === "b" ? "border-l border-accent" : ""} ${s.view === p ? "bg-accent font-semibold" : "bg-white text-accent"}`}>
      Scenario {p.toUpperCase()}
    </button>
  );
  const wayLabel = (v: number) => (v === FLEX ? `Flexible: ${f.words[FLEX]}` : "Flat: the same in every hour");

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
                  {k === "run" ? (
                    <select value={a.run} className={field} data-assumption="run" aria-label={sp.label} onChange={(e) => set("run", Number(e.target.value))}>
                      {[FLAT, FLEX].map((v) => <option key={v} value={v} disabled={!open[v]}>{wayLabel(v)}{open[v] ? "" : " (not held here)"}</option>)}
                    </select>
                  ) : <NumberField k={k} value={a[k]} onValue={(v) => set(k, v)} read={(v) => bound(k, v, d)} />}
                  <button type="button" data-reset={k} disabled={a[k] === d[k]} className="whitespace-nowrap border border-rule bg-white px-2 py-1 text-xs text-accent disabled:text-muted" onClick={() => set(k, d[k])}>Reset</button>
                </div>
                <p className="mt-1 text-xs leading-snug text-muted" data-default={d[k]}>
                  {k === "run" ? <>Default {d.run === FLEX ? "flexible" : "flat"}. {sourceOf(k)}.{open[FLAT] && open[FLEX] ? "" : ` ${f.why[open[FLAT] ? FLEX : FLAT]}`}</> : <>Default {plain(d[k])}. {sourceOf(k)}.</>}
                </p>
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
              <th scope="col" className="col-span-2 px-3 py-1.5 font-normal sm:table-cell">For {f.size} at {f.place}</th>
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
            <tr className="grid grid-cols-2 border-b border-rule bg-paper sm:table-row" data-row="against">
              <th scope="row" className="col-span-2 px-3 pb-0 pt-1.5 font-normal sm:table-cell sm:pb-1.5">B against A</th>
              <td colSpan={2} className="col-span-2 px-3 py-1.5 text-left sm:table-cell" data-against-words="1" data-rate={versusRate} data-even={versusEven}>{versus}</td>
            </tr>
          </tbody>
        </table>
      </div>
      {inView.r ? (
        <p className="mt-3 max-w-3xl text-sm" data-pv-sentence={s.view}>
          Scenario {s.view.toUpperCase()}, {f.size} at {f.place}: at a hurdle rate of {plain(a.hurdle)} percent, {plain(a.life)} years of power cost {usd(inView.r.pv * f.mw)} today, {four(inView.r.allIn)} per GPU-hour.
        </p>
      ) : null}
      {bars.length ? <Sensitivity bars={bars} view={s.view} own={a} words={f.words} /> : null}
    </div>
  );
}
