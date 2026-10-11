"use client";
// Session 195: the decisions block the three decision pages share: /cost-of-power/battery (session 179),
// /cost-of-power/seller (session 186) and /cost-of-power (session 194). Until this session each page held its own copy
// of the assumptions panel, the two columns, the rows in words and the sensitivity chart. They are one component now:
// each page hands it its own fields, defaults, sources, rows and chart figures (battery/Scenarios.tsx,
// seller/SellerScenarios.tsx, LoadScenarios.tsx), and the arithmetic stays in each page's own library
// (lib/battery/finance.ts, lib/seller/finance.ts, lib/datacenter/finance.ts).
//
// The two scenarios are held above the page's sections (ScenarioState), so that the page's headline reads scenario A:
// the fields "Your battery", "Your plant" and "Your load" held twice are gone. A change sends no request and no usage
// count (the owner's ruling, 11 October 2026): the address is rewritten in place (history.replaceState) so that a
// comparison can be shared as a link. No sentence here judges: each states a number. The block is described once, in
// docs/methods/battery_earns_algorithm.md, section 11.1 ("The block the three pages share"); the generator's and the
// datacenter's notes point to it.
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

export type View = "a" | "b";
export type Values = Record<string, number>;
export type Both<V extends Values = Values> = { a: V; b: V; view: View };

type Held = { s: Both; update: (next: Both) => void };
const State = createContext<Held | null>(null);

/** The two scenarios of a page, and the address that keeps them. `query` gives the address parameters of a state (only
 * what differs from the defaults), `drop` says which parameters of the address are the scenarios' own or their old
 * names, so that they are replaced and every other parameter of the page is left as it is. Nothing is requested. */
export function ScenarioState({ start, query, drop, children }: { start: Both; query: (s: Both) => [string, string][]; drop: (name: string) => boolean; children: ReactNode }) {
  const [s, setS] = useState<Both>(start);
  useEffect(() => {
    const cur = new URLSearchParams(window.location.search);
    const next = new URLSearchParams();
    for (const [k, v] of cur) if (!drop(k)) next.append(k, v);
    for (const [k, v] of query(s)) next.set(k, v);
    const qs = next.toString();
    if (qs !== cur.toString()) window.history.replaceState(null, "", `${window.location.pathname}${qs ? `?${qs}` : ""}${window.location.hash}`);
  }, [s, query, drop]);
  return <State.Provider value={{ s, update: setS }}>{children}</State.Provider>;
}
/** The two scenarios and the way to change them, for the block and for the page's headline. */
export function useScenarios<V extends Values>(): { s: Both<V>; update: (next: Both<V>) => void } {
  const c = useContext(State);
  if (!c) throw new Error("the scenarios are read outside ScenarioState");
  return c as unknown as { s: Both<V>; update: (next: Both<V>) => void };
}

const DOWN = "#2a78d6", UP = "#eb6834";  // app/tokens.css: the categorical slots 1 and 2 (fuel-gas, fuel-coal); neither is a verdict
const field = "w-full border border-rule bg-white px-2 py-1 text-sm";

/** One assumption of the panel. A field with `options` is a list (the steps the model was run at, the two ways a load
 * runs); any other is a number. `note` is the line under it: the default and its source. */
export type Field = {
  key: string; label: string; unit: string; min: number; max: number; whole: boolean;
  options?: { value: number; label: string; disabled?: boolean }[]; aria?: string; note: ReactNode;
};
/** One cell of the table: what is shown, its value for the checks, the small line under it, and why it is not held. */
export type Cell = { v: string; raw: number | null; note?: string; why?: string };
export type Row = { key: string; label: string; note: string; cell: (p: View) => Cell };
export type Side = { value: number; v: number };
/** One row of the sensitivity chart, in the units the chart shows. */
export type Bar = { key: string; label: string; step: string; base: number; down: Side | null; up: Side | null; size: number };
export type Chart = {
  bars: Bar[];
  /** what the chart moves, in its title ("NPV") and under its axis ("NPV", "per GPU-hour") */
  moves: string; axis: string;
  fmt: (v: number) => string;
  /** the sentence a row gives when pointed at, the figure beside its label, and how its step reads there */
  says: (b: Bar) => string; sizeWords: (b: Bar) => string; stepWords: (b: Bar) => string;
  /** the table under the chart: its two value headings and one side of a row */
  heads: [string, string]; side: (b: Bar, s: Side | null) => string;
  /** the label column is wider where the labels are longer; the smallest padding of the scale */
  wide?: boolean; pad: number;
};

/** One number field. The text typed is shown while it still reads as the value in force; otherwise the value is. */
function NumberField({ f, value, onValue, read }: { f: Field; value: number; onValue: (v: number) => void; read: (v: number) => number }) {
  const [text, setText] = useState<string | null>(null);
  const shown = text !== null && (text === "" || read(Number(text)) === value) ? text : String(value);
  return (
    <input type="number" inputMode="decimal" autoComplete="off" min={f.min} max={f.max} step={f.whole ? 1 : "any"} value={shown} className={field}
      data-assumption={f.key} aria-label={`${f.label}, ${f.unit}`}
      onChange={(e) => { setText(e.target.value); const v = Number(e.target.value); if (e.target.value !== "" && Number.isFinite(v)) onValue(v); }}
      onBlur={() => setText(null)} />
  );
}

/** The sensitivity chart: one row an assumption, two thin bars from the scenario's own figure, sorted by size. */
function Sensitivity({ c, view }: { c: Chart; view: View }) {
  const [on, setOn] = useState<string | null>(null);
  const { bars } = c;
  const all = bars.flatMap((b) => [b.base, b.down?.v, b.up?.v]).filter((v): v is number => v !== undefined && v !== null);
  const lo0 = Math.min(...all), hi0 = Math.max(...all);
  const pad = (hi0 - lo0) * 0.04 || c.pad;
  const lo = lo0 - pad, hi = hi0 + pad;
  const x = (v: number) => ((v - lo) / (hi - lo)) * 100;
  const base = bars[0].base;
  const hit = bars.find((b) => b.key === on) ?? null;
  const cols = c.wide ? "sm:grid-cols-[300px_minmax(0,1fr)]" : "sm:grid-cols-[280px_minmax(0,1fr)]";
  return (
    <figure className="mt-8" data-sensitivity={view}>
      <figcaption className="mb-2 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-1">
        <span className="font-serif text-lg text-accent">How far each assumption moves {c.moves}, scenario {view.toUpperCase()}</span>
        <span className="flex flex-wrap gap-x-4 text-xs text-ink">
          <span className="inline-flex items-center gap-1.5"><span aria-hidden="true" className="inline-block h-2.5 w-2.5" style={{ background: DOWN }} />Lowered by the step</span>
          <span className="inline-flex items-center gap-1.5"><span aria-hidden="true" className="inline-block h-2.5 w-2.5" style={{ background: UP }} />Raised by the step</span>
        </span>
      </figcaption>
      <ul className="space-y-1" onMouseLeave={() => setOn(null)}>
        {bars.map((b) => {
          const bar = (s: Side | null, color: string, top: boolean) => {
            if (!s) return null;
            const a = x(Math.min(s.v, b.base)), w = Math.abs(x(s.v) - x(b.base));
            const right = s.v >= b.base;
            return <span aria-hidden="true" className="absolute h-[6px]" style={{ left: `${a}%`, width: `${Math.max(w, 0.4)}%`, top: top ? 3 : 11, background: color, borderRadius: right ? "0 4px 4px 0" : "4px 0 0 4px" }} />;
          };
          return (
            <li key={b.key}>
              <button type="button" data-bar={b.key} data-size={b.size} data-down={b.down ? b.down.v : ""} data-up={b.up ? b.up.v : ""}
                title={c.says(b)} onMouseEnter={() => setOn(b.key)} onFocus={() => setOn(b.key)} onClick={() => setOn(b.key)}
                className={`grid w-full items-center gap-x-3 gap-y-0.5 px-1 py-1 text-left text-xs ${cols} ${on === b.key ? "bg-paper" : ""}`}>
                <span className="flex items-baseline justify-between gap-2">
                  <span><span className="text-sm text-ink">{b.label}</span> <span className="text-muted">{c.stepWords(b)}</span></span>
                  <span className="whitespace-nowrap tabular-nums text-muted">{c.sizeWords(b)}</span>
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
      <div className={`mt-1 grid text-xs tabular-nums text-muted ${cols} sm:gap-x-3`}>
        <span />
        <span className="flex justify-between px-1"><span>{c.fmt(lo0)}</span><span>{c.axis}, {c.fmt(base)} at the line</span><span>{c.fmt(hi0)}</span></span>
      </div>
      <p className="mt-2 min-h-[2.5em] max-w-3xl text-sm" role="status" data-sensitivity-readout="1">
        {hit ? c.says(hit) : "Point at a row, or tab to it, for the two values."}
      </p>
      <details className="mt-1 text-xs">
        <summary className="cursor-pointer text-accent">The chart as a table</summary>
        <div className="overflow-x-auto">
          <table className="mt-2 w-full border-collapse text-left tabular-nums" style={{ minWidth: 480 }}>
            <thead><tr className="border-b border-rule"><th scope="col" className="py-1 pr-3 font-normal">Assumption</th><th scope="col" className="py-1 pr-3 font-normal">Step</th><th scope="col" className="py-1 pr-3 text-right font-normal">{c.heads[0]}</th><th scope="col" className="py-1 text-right font-normal">{c.heads[1]}</th></tr></thead>
            <tbody>
              {bars.map((b) => (
                <tr key={b.key} className="border-b border-rule">
                  <th scope="row" className="py-1 pr-3 font-normal">{b.label}</th><td className="py-1 pr-3">{b.step}</td>
                  <td className="py-1 pr-3 text-right">{c.side(b, b.down)}</td>
                  <td className="py-1 text-right">{c.side(b, b.up)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </figure>
  );
}

/** The block: the assumptions panel for the scenario in view, the two columns on the page's rows, the row that says in
 * words what differs, the page's own row that sets B against A in numbers (when it has one), the sentence under the
 * table, which states scenario A, the scenario the page's headline shows, and the chart for the scenario in view. */
export function ScenarioBlock({ fields, defaults: d, bound, head, rows, differing, short, differs, against, sentence, chart, foot }: {
  fields: Field[]; defaults: Values; bound: (key: string, v: number) => number;
  /** the table's first heading: what the two columns are for ("For 100 MW, 4-hour") */
  head: string; rows: Row[];
  /** the assumptions that differ between A and B, how each reads in a column's heading, and the row in words */
  differing: string[]; short: (key: string, v: number) => string; differs: string;
  against?: { words: string; rate: string; even: string };
  sentence: ReactNode; chart: Chart | null; foot?: ReactNode;
}) {
  const { s, update } = useScenarios();
  const a = s[s.view];
  const set = (k: string, v: number) => update({ ...s, [s.view]: { ...s[s.view], [k]: bound(k, v) } });
  const tab = (p: View) => (
    <button key={p} type="button" aria-pressed={s.view === p} data-view={p} onClick={() => update({ ...s, view: p })}
      style={s.view === p ? { color: "#fff" } : undefined}
      className={`px-4 py-1.5 text-sm ${p === "b" ? "border-l border-accent" : ""} ${s.view === p ? "bg-accent font-semibold" : "bg-white text-accent"}`}>
      Scenario {p.toUpperCase()}
    </button>
  );
  const views: View[] = ["a", "b"];

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
          {fields.map((f) => {
            const k = f.key;
            return (
              <div key={`${s.view}-${k}`} className="text-sm" data-field={k}>
                <div className="mb-1 font-semibold">{f.label}, <span className="font-normal">{f.unit}</span></div>
                <div className="flex items-center gap-2">
                  {f.options ? (
                    <select value={a[k]} className={field} data-assumption={k} aria-label={f.aria ?? `${f.label}, ${f.unit}`} onChange={(e) => set(k, Number(e.target.value))}>
                      {f.options.map((o) => <option key={o.value} value={o.value} disabled={o.disabled}>{o.label}</option>)}
                    </select>
                  ) : (
                    <NumberField f={f} value={a[k]} onValue={(v) => set(k, v)} read={(v) => bound(k, v)} />
                  )}
                  <button type="button" data-reset={k} disabled={a[k] === d[k]} className="whitespace-nowrap border border-rule bg-white px-2 py-1 text-xs text-accent disabled:text-muted" onClick={() => set(k, d[k])}>Reset</button>
                </div>
                <p className="mt-1 text-xs leading-snug text-muted" data-default={d[k]}>{f.note}</p>
              </div>
            );
          })}
        </div>
        {foot}
      </div>

      <div className="overflow-x-auto">
        <table className="block w-full border-collapse text-left text-sm tabular-nums sm:table" data-scenario-table="1">
          <caption className="sr-only">Scenarios A and B</caption>
          <thead className="block sm:table-header-group">
            <tr className="grid grid-cols-2 bg-accent align-top text-white sm:table-row">
              <th scope="col" className="col-span-2 px-3 py-1.5 font-normal sm:table-cell">{head}</th>
              {views.map((p) => (
                <th key={p} scope="col" className="px-3 py-1.5 text-right font-normal sm:table-cell" data-head={p}>
                  <span className="font-semibold">{p.toUpperCase()}</span>
                  {differing.map((k) => <span key={k} className="block text-xs opacity-90" data-differs={k}>{short(k, s[p][k])}</span>)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="block sm:table-row-group">
            {rows.map((r) => (
              <tr key={r.key} className="grid grid-cols-2 border-b border-rule align-top sm:table-row" data-row={r.key}>
                <th scope="row" className="col-span-2 px-3 pb-0 pt-1.5 font-normal sm:table-cell sm:pb-1.5">{r.label}<div className="text-xs font-normal text-muted">{r.note}</div></th>
                {views.map((p) => {
                  const cell = r.cell(p);
                  return (
                    <td key={p} className="px-3 py-1.5 text-right sm:table-cell" data-cell={`${p}|${r.key}`} data-raw={cell.raw === null ? "" : String(cell.raw)}>
                      {cell.why ? <span className="cursor-help border-b border-dotted border-muted italic text-muted" title={cell.why} data-missing="1">{cell.v}</span> : cell.v}
                      {cell.note ? <div className="text-xs text-muted">{cell.note}</div> : null}
                    </td>
                  );
                })}
              </tr>
            ))}
            <tr className="grid grid-cols-2 border-b border-rule bg-paper sm:table-row" data-row="differs">
              <th scope="row" className="col-span-2 px-3 pb-0 pt-1.5 font-normal sm:table-cell sm:pb-1.5">What differs</th>
              <td colSpan={2} className="col-span-2 px-3 py-1.5 text-left sm:table-cell" data-differs-words="1">{differs}</td>
            </tr>
            {against ? (
              <tr className="grid grid-cols-2 border-b border-rule bg-paper sm:table-row" data-row="against">
                <th scope="row" className="col-span-2 px-3 pb-0 pt-1.5 font-normal sm:table-cell sm:pb-1.5">B against A</th>
                <td colSpan={2} className="col-span-2 px-3 py-1.5 text-left sm:table-cell" data-against-words="1" data-rate={against.rate} data-even={against.even}>{against.words}</td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      {sentence}
      {chart && chart.bars.length ? <Sensitivity c={chart} view={s.view} /> : null}
    </div>
  );
}
