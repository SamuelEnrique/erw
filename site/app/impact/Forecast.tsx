"use client";
// Session 4213 (chain 239): the forecast tool on /impact, "Local impact" (tool 17). The inputs in a box on the left, in
// groups that open and close; every assumption shows its default in grey with its source in a hover tip and is edited
// in place; scenarios A and B side by side on the right, with a chart of the scenario in view by year (hover gives the
// values), its table by year, and the run's downloads. The arithmetic is lib/forecast.ts (docs/methods/forecast.md,
// internal); the fields, defaults' words and the address are lib/forecastui.ts. A change sends no request: the address
// is rewritten in place (ScenarioState), so a comparison can be shared as a link.
import { useState, type ReactNode } from "react";
import { ScenarioState, useScenarios } from "@/components/decisions/ScenarioBlock";
import { SeriesChart } from "@/components/tool/SeriesChart";
import { Tip } from "@/components/tool/ToolPage";
import { Num } from "@/components/Num";
import { TECHS, stateName } from "@/lib/impact";
import { compute, type Rules } from "@/lib/severance";
import { displayOf, inputsKey, jobsText, run, stat, unpack, usdText, type Inputs, type Packed, type Params, type Result, type TechKey } from "@/lib/forecast";
import { FIELDS, GROUPS, STATE_LIST, clampTo, dropParam, queryWithProjects, resolve, stateOfIx, techOfIx, type Both, type FieldDef, type Values } from "@/lib/forecastui";
import type { Planned } from "@/lib/forecast";
import { csvOf, pythonOf, stataOf } from "@/lib/forecastfiles";
import { StateChart } from "./StateChart";

type View = "a" | "b";
const box = "w-full border border-rule bg-white px-2 py-1 text-sm";

// ---- how figures are written ---------------------------------------------------------------------------------------
// the forms check-values reads too (lib/forecast.ts, displayOf)
const usd = usdText;
const jobs = jobsText;
const plain = (v: number, d = 2) => v.toLocaleString("en-US", { maximumFractionDigits: d });

/** The severance on a gas plant's in-state fuel: /severance's own rules and arithmetic (lib/severance.ts), its base
 *  rates and fees, for the three states it holds; null elsewhere. */
function severanceOf(rules: Rules) {
  return (state: string, volume: number, price: number): number | null => {
    const st = state.toUpperCase();
    if (!rules.states[st]?.products?.gas) return null;
    const r = compute(rules, { state: st, product: "gas", volume, price });
    return r.baseTotal + r.fees.reduce((a, f) => a + f.amount, 0);
  };
}

export function Forecast({ P, jedi, start, rules, planned }: { P: Params; jedi: Packed; start: Both; rules: unknown; planned: Planned[] }) {
  const ids = planned.map((p) => p.id);
  return (
    <ScenarioState start={start as never} query={((s: Both) => queryWithProjects(s, ids)) as never} drop={dropParam}>
      <Body P={P} jedi={jedi} rules={rules as Rules} planned={planned} />
    </ScenarioState>
  );
}

function Body({ P, jedi, rules, planned }: { P: Params; jedi: Packed; rules: Rules; planned: Planned[] }) {
  const { s, update } = useScenarios<Values>();
  const sev = severanceOf(rules);
  const x = { a: resolve(P, s.a), b: resolve(P, s.b) };
  const r = { a: run(x.a, unpack(jedi, x.a.tech, x.a.state), P, sev), b: run(x.b, unpack(jedi, x.b.tech, x.b.state), P, sev) };
  return (
    <div className="grid gap-8 lg:grid-cols-[320px_minmax(0,1fr)]" data-forecast="1">
      <aside><Panel P={P} s={s} update={update} planned={planned} /></aside>
      <div className="min-w-0 space-y-8">
        <Compare x={x} r={r} names={{ a: projectOf(planned, s.a, x.a), b: projectOf(planned, s.b, x.b) }} />
        <Years x={x[s.view]} r={r[s.view]} view={s.view} />
        <OtherStates P={P} jedi={jedi} x={x[s.view]} v={s[s.view]} view={s.view} sev={sev} />
        <Downloads P={P} x={x} r={r} jedi={jedi} />
      </div>
    </div>
  );
}

// ---- the left box ----------------------------------------------------------------------------------------------------
/** The scenario's planned project, when one is picked and it is still of the scenario's technology and state */
function projectOf(planned: Planned[], v: Values, x: Inputs): Planned | null {
  const p = Number.isFinite(v.proj) ? planned[v.proj] : undefined;
  return p && p.tech === x.tech && p.state === x.state ? p : null;
}

function Panel({ P, s, update, planned }: { P: Params; s: Both; update: (b: Both) => void; planned: Planned[] }) {
  const v = s[s.view];
  const tech = techOfIx(v.tech), state = stateOfIx(v.state);
  const d = resolve(P, { tech: v.tech, state: v.state } as Values);  // the defaults for the technology and state in view
  // a new technology or state leaves the planned project, which belongs to the old ones
  const set = (k: string, val: number) => update({ ...s, [s.view]: { ...v, [k]: val, ...(k === "tech" || k === "state" ? { proj: NaN } : {}) } });
  const mine = planned.map((p, i) => ({ p, i })).filter(({ p }) => p.tech === tech && p.state === state);
  const pick = (i: number) => {
    if (!Number.isFinite(i)) { update({ ...s, [s.view]: { ...v, proj: NaN } }); return; }
    const p = planned[i];
    const build = Number.isFinite(v.build) ? v.build : d.build;
    const start = p.year === null ? v.start : Math.max(2026, p.year - build);
    update({ ...s, [s.view]: { ...v, proj: i, mw: Math.round(p.mw * 1000) / 1000, start } });
  };
  const cur = Number.isFinite(v.proj) && planned[v.proj]?.tech === tech && planned[v.proj]?.state === state ? v.proj : NaN;
  const tab = (p: View) => (
    <button key={p} type="button" aria-pressed={s.view === p} data-view={p} onClick={() => update({ ...s, view: p })}
      style={s.view === p ? { color: "#fff" } : undefined}
      className={`px-4 py-1.5 text-sm ${p === "b" ? "border-l border-accent" : ""} ${s.view === p ? "bg-accent font-semibold" : "bg-white text-accent"}`}>
      Scenario {p.toUpperCase()}
    </button>
  );
  const blank: Values = Object.fromEntries(FIELDS.map((f) => [f.key, NaN]));
  return (
    <div className="bg-paper px-4 py-4" data-assumptions={s.view}>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <div className="inline-grid grid-cols-2 border border-accent" role="group" aria-label="The scenario in view">{tab("a")}{tab("b")}</div>
      </div>
      <div className="mb-3 flex flex-wrap gap-2 text-xs">
        <button type="button" data-copy="1" className="border border-accent bg-white px-3 py-1 text-accent" onClick={() => update({ ...s, b: { ...s.a } })}>Copy A to B</button>
        <button type="button" data-reset-all="1" className="border border-accent bg-white px-3 py-1 text-accent"
          onClick={() => update({ ...s, [s.view]: { ...blank, tech: v.tech, state: v.state } })}>Reset all of {s.view.toUpperCase()}</button>
      </div>
      {GROUPS.map((g) => {
        const fs = FIELDS.filter((f) => f.group === g.key && (!f.applies || f.applies(tech, state, P)));
        if (!fs.length) return null;
        const set_ = fs.filter((f) => f.key !== "tech" && f.key !== "state" && Number.isFinite(v[f.key])).length;
        return (
          <details key={g.key} className="border-t border-rule" data-group={g.key} open={g.open}>
            <summary className="cursor-pointer py-2 text-sm font-semibold">{g.title}{set_ ? <span className="ml-2 text-xs font-normal text-muted">{set_} changed</span> : null}</summary>
            <div className="space-y-3 pb-3">
              {fs.flatMap((f) => {
                const el = <One key={`${s.view}-${f.key}`} f={f} P={P} tech={tech} state={state} v={v} d={d} set={set} />;
                if (f.key !== "state") return [el];
                return [el, (
                  <div key={`${s.view}-proj`} className="text-sm" data-field="proj">
                    <div className="mb-1 font-semibold">Planned project</div>
                    <select className={box} value={Number.isFinite(cur) ? cur : ""} data-assumption="proj" aria-label="A planned project in this state" disabled={!mine.length}
                      onChange={(e) => pick(e.target.value === "" ? NaN : Number(e.target.value))}>
                      <option value="">{mine.length ? "None: the inputs below" : "None planned in EIA-860M"}</option>
                      {mine.map(({ p, i }) => <option key={p.id} value={i}>{p.name}, {plain(p.mw, 1)} MW{p.year ? `, ${p.year}` : ""}</option>)}
                    </select>
                    <p className="mt-1 text-xs leading-snug text-muted" data-default="proj">{Number.isFinite(cur) ? `${planned[cur].county} County. Sets the size and the first construction year.` : `${mine.length} planned in this state`}<Tip id="f-proj" label="the planned project">EIA-860M&apos;s planned generators of this technology in this state (the ERW&apos;s energy_projects, from eia860m_planned_generators), a plant&apos;s generators added; the year is its earliest planned operation date. Picking one sets the size and the first construction year; every other input stays the scenario&apos;s.</Tip></p>
                  </div>
                )];
              })}
            </div>
          </details>
        );
      })}
    </div>
  );
}

function shownDefault(f: FieldDef, d: Inputs): string {
  const val = d[f.key];
  if (val === null) return "not given";
  if (f.key === "tech") return TECHS.find((t) => t.key === val)?.label ?? String(val);
  if (f.key === "state") return stateName(String(val));
  if (f.key === "iaval") return val ? "Yes" : "No";
  if (f.key === "capex") return `${plain(val as number, 0)}`;
  if (f.key === "start") return String(val);  // fault 6: a year, never "2,027"
  return plain(val as number, f.key === "cf" || f.key === "ilr" ? 4 : 2);
}

function One({ f, P, tech, state, v, d, set }: { f: FieldDef; P: Params; tech: TechKey; state: string; v: Values; d: Inputs; set: (k: string, val: number) => void }) {
  const k = f.key;
  const isSet = Number.isFinite(v[k]) && k !== "tech" && k !== "state";
  const label = <>{f.label}{f.unit ? <span className="font-normal">, {f.unit}</span> : null}</>;
  const tip = <Tip id={`f-${k}`} label={f.label}>{f.source(tech, state, P)}</Tip>;
  let control: ReactNode;
  if (f.options) {
    const cur = k === "tech" || k === "state" ? v[k] : Number.isFinite(v[k]) ? v[k] : (d[k] ? 1 : 0);
    control = (
      <select className={box} value={cur} data-assumption={k} aria-label={f.label} onChange={(e) => set(k, Number(e.target.value))}>
        {f.options(P).map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    );
  } else {
    const shown = Number.isFinite(v[k]) ? v[k] : (d[k] as number | null);
    control = <NumberInput f={f} value={shown} onValue={(val) => set(k, val)} />;
  }
  return (
    <div className="text-sm" data-field={k}>
      <div className="mb-1 font-semibold">{label}</div>
      <div className="flex items-center gap-2">
        {control}
        {k !== "tech" && k !== "state" ? (
          <button type="button" data-reset={k} aria-label={`Reset ${f.label}`} disabled={!isSet}
            className="whitespace-nowrap border border-rule bg-white px-2 py-1 text-xs text-accent disabled:text-muted" onClick={() => set(k, NaN)}>Reset</button>
        ) : null}
      </div>
      {k !== "tech" && k !== "state" ? (
        <p className="mt-1 text-xs leading-snug text-muted" data-default={k}>Default {shownDefault(f, d)}{tip}</p>
      ) : <p className="mt-1 text-xs leading-snug text-muted" data-default={k}>{tip}</p>}
    </div>
  );
}

/** One number box: the text typed while it is typed; empty sets the field back to its default (NaN). */
function NumberInput({ f, value, onValue }: { f: FieldDef; value: number | null; onValue: (v: number) => void }) {
  const [text, setText] = useState<string | null>(null);
  const shown = text !== null ? text : value === null ? "" : String(Math.round(value * 10000) / 10000);
  return (
    <input type="number" inputMode="decimal" autoComplete="off" min={f.min} max={f.max} step={f.whole ? 1 : "any"} value={shown} className={box}
      data-assumption={f.key} aria-label={`${f.label}${f.unit ? `, ${f.unit}` : ""}`} placeholder={value === null ? "not given" : undefined}
      onChange={(e) => {
        setText(e.target.value);
        if (e.target.value === "") { onValue(NaN); return; }
        const n = Number(e.target.value);
        if (Number.isFinite(n)) onValue(clampTo(f, n));
      }}
      onBlur={() => setText(null)} />
  );
}

// ---- A and B side by side ------------------------------------------------------------------------------------------
type Line = { key: string; label: string; tip: string; figure: string; fmt: (v: number) => string; why?: (r: Result, x: Inputs) => string | null };
const LINES: Line[] = [
  { key: "cjobs", label: "Construction jobs", tip: "Job-years over the build (one is a full-time job for a year): on site, in the state's supply chain and induced by the wages' spending. JEDI's per-MW construction figures, scaled by the spending.", figure: "c:jobs:total", fmt: jobs },
  { key: "ojobs", label: "Operating jobs, each year", tip: "Full-time jobs in each year the plant runs, all three effects. JEDI's per-MW operating figures; for solar, JEDI's 2010 operating costs give an upper reading.", figure: "o:jobs:total", fmt: jobs },
  { key: "cearn", label: "Construction earnings", tip: "Wages, salaries and benefits of those jobs over the build, in 2025 dollars.", figure: "c:earnings:total", fmt: usd },
  { key: "oearn", label: "Operating earnings, each year", tip: "Wages, salaries and benefits of the operating jobs each year, in 2025 dollars.", figure: "o:earnings:total", fmt: usd },
  { key: "cout", label: "Construction output", tip: "The value of all the goods and services produced in the state because of the build: JEDI's widest measure, in 2025 dollars.", figure: "c:output:total", fmt: usd },
  { key: "oout", label: "Operating output, each year", tip: "The same measure for each year the plant runs.", figure: "o:output:total", fmt: usd },
  { key: "prop1", label: "Property tax, first operating year", tip: "From the state's statute where one is held (Minnesota, South Dakota, North Dakota, Nebraska, Iowa; Kansas exempts the first ten years and holds no rule after; Oregon solar by county agreement; Wyoming's wind generation excise of USD 1 a MWh from the fourth year, to which the reader's own property tax rate is added), or the reader's own rate. Land is not included.", figure: "y1:property", fmt: usd,
    why: (r) => (r.property.held ? null : r.property.note) },
  { key: "propl", label: "Property tax over the life", tip: "Every operating year added, in 2025 dollars.", figure: "sum:property", fmt: usd, why: (r) => (r.property.held ? null : r.property.note) },
  { key: "sales", label: "Sales and use tax", tip: "On the taxable share of the construction spending at the state and average local rate, spread over the build.", figure: "sum:sales", fmt: usd,
    why: (r) => (r.sales.held ? null : r.sales.note) },
  { key: "income", label: "State income tax over the life", tip: "Each job taxed as one single filer on the average earnings, by the state's 2026 brackets, every year of the build and the operation.", figure: "sum:income", fmt: usd },
  { key: "sev", label: "Severance, each year", tip: "On the gas a gas plant burns that is produced in the state, by /severance's rules (Texas, Louisiana, New Mexico).", figure: "y1:severance", fmt: usd,
    why: (r) => (r.severance.held ? null : r.severance.note) },
  { key: "pvtax", label: "Taxes, present value", tip: "Property, sales, income and severance taxes, each year discounted to the first construction year at the scenario's real rate.", figure: "pv:taxes", fmt: usd },
  { key: "pvearn", label: "Earnings, present value", tip: "Every year's earnings discounted the same way.", figure: "pv:earnings", fmt: usd },
];

function scenarioWords(x: Inputs): string {
  return `${TECHS.find((t) => t.key === x.tech)?.label}, ${stateName(x.state)}, ${plain(x.mw, 1)} MW`;
}

function Compare({ x, r, names }: { x: Record<View, Inputs>; r: Record<View, Result>; names: Record<View, Planned | null> }) {
  const views: View[] = ["a", "b"];
  return (
    <section data-compare="1">
      <h2 className="mb-2 text-lg font-semibold">A and B</h2>
      <div>
        <table className="block w-full border-collapse text-left text-sm tabular-nums sm:table sm:table-fixed" data-compare-table="1">
          <caption className="sr-only">Scenarios A and B</caption>
          <thead className="block sm:table-header-group">
            <tr className="grid grid-cols-2 bg-accent align-top text-white sm:table-row">
              <th scope="col" className="col-span-2 px-3 py-1.5 font-normal sm:table-cell sm:w-[34%]">Figure</th>
              {views.map((p) => (
                <th key={p} scope="col" className="px-3 py-1.5 text-right font-normal sm:table-cell" data-head={p}>
                  <span className="font-semibold">{p.toUpperCase()}</span>
                  <span className="block text-xs opacity-90">{scenarioWords(x[p])}</span>
                  {names[p] ? <span className="block text-xs opacity-90" data-project={names[p]!.id}>{names[p]!.name}, {names[p]!.county} County</span> : null}
                  <span className="block text-xs opacity-90">rate {plain(x[p].rate)}%, {x[p].start} to {x[p].start + x[p].build + x[p].life - 1}</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="block sm:table-row-group">
            {LINES.map((l) => (
              <tr key={l.key} className="grid grid-cols-2 border-b border-rule align-top sm:table-row" data-row={l.key}>
                <th scope="row" className="col-span-2 px-3 pb-0 pt-1.5 font-normal sm:table-cell sm:pb-1.5">{l.label}<Tip id={`l-${l.key}`} label={l.label}>{l.tip}</Tip></th>
                {views.map((p) => {
                  const res = r[p];
                  const cls = "px-3 py-1.5 text-right sm:table-cell";
                  if (!res.ok) return <td key={p} className={`${cls} italic text-muted`} data-cell={`${p}|${l.key}`}><span className="cursor-help border-b border-dotted border-muted" title={res.why}>no figure</span></td>;
                  const v = stat(res, l.figure);
                  const why = l.why?.(res, x[p]) ?? null;
                  // fault 11: a short word in the cell, the reason in its hover (a long reason widened the table past its column)
                  if (v === null) return <td key={p} className={`${cls} italic text-muted`} data-cell={`${p}|${l.key}`}><span className="cursor-help border-b border-dotted border-muted" title={why ?? "not held"}>{l.key === "sev" && x[p].tech !== "natural_gas" ? "none" : "not held"}</span></td>;
                  return <td key={p} className={cls} data-cell={`${p}|${l.key}`}><Num check={`${inputsKey(x[p])}|${l.figure}`} raw={v}>{displayOf(l.figure, v)}</Num></td>;
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

// ---- the scenario in view, by year -----------------------------------------------------------------------------------
function Years({ x, r, view }: { x: Inputs; r: Result; view: View }) {
  const [open, setOpen] = useState(false);  // fault 18: the fold's state only; its rows are always drawn, so check-values reads them
  if (!r.ok) return <p className="text-sm text-muted">Scenario {view.toUpperCase()} has no figure: {r.why}.</p>;
  const cats = r.years.map((y) => ({ label: String(y.year), sub: y.phase === "construction" ? "build" : undefined }));
  const val = (f: (i: number) => number | null) => r.years.map((_, i) => f(i));
  // fault 9: a tax held for the scenario is 0 in the years it does not fall (sales after the build, property during it);
  // a tax not held at all is left out of the chart, not drawn as "not held" in every year; fault 17: a property tax held
  // for some years (an agreement, an exemption) is drawn for them
  const prop = val((i) => (r.years[i].phase === "construction" ? 0 : r.years[i].property)), sales = val((i) => r.years[i].sales ?? 0), inc = val((i) => r.years[i].income), sev = val((i) => r.years[i].severance ?? 0);
  const taxSeries = [
    ...(r.years.some((y) => y.property !== null) ? [{ name: "Property", color: "var(--color-year-1)", values: prop }] : []),
    ...(r.sales.held ? [{ name: "Sales and use", color: "var(--color-year-2)", values: sales }] : []),
    { name: "Income", color: "var(--color-year-3)", values: inc },
    ...(r.severance.held ? [{ name: "Severance", color: "var(--color-year-4)", values: sev }] : []),
  ];
  const short = (v: number) => usd(v).replace(/^USD /, "");  // fault 10: the chart writes its unit itself
  const say = (i: number) => { const y = r.years[i]; return `${y.year} (${y.phase}): property ${y.property === null ? "not held" : usd(y.property)}, sales ${y.sales === null ? "none" : usd(y.sales)}, income ${usd(y.income)}${x.tech === "natural_gas" ? `, severance ${y.severance === null ? "not held" : usd(y.severance)}` : ""}`; };
  const jobsSays = (i: number) => { const y = r.years[i]; return `${y.year} (${y.phase}): ${jobs(y.jobs.total)} jobs (on site ${jobs(y.jobs.onsite)}, supply chain ${jobs(y.jobs.supply_chain)}, induced ${jobs(y.jobs.induced)})`; };
  const key = inputsKey(x);
  // session 4220 (the county assessor's read): the year's MWh where a production tax rests on it, the taxable value
  // where a valuation or the reader's own rate taxes one
  const hasMwh = r.years.some((y) => y.mwh !== null) && r.property.production;  // fault 20: by the rule's kind, not its id
  const hasValue = r.years.some((y) => y.value !== null);
  return (
    <section data-years={view}>
      <h2 className="mb-2 text-lg font-semibold">Scenario {view.toUpperCase()} by year</h2>
      <div className="space-y-6">
        <SeriesChart id={`tax-${view}`} title="Taxes by year" unit="USD (2025)" kind="stacked" scale="linear" fmt={short}
          categories={cats} series={taxSeries} says={say}
          tip={<Tip id={`tax-${view}`} label="taxes by year">Each year&apos;s property, sales and use, income and (for a gas plant) severance taxes of the scenario in view, in 2025 dollars. A tax not held for this state and technology is left out.</Tip>} />
        <SeriesChart id={`jobs-${view}`} title="Jobs by year" unit="jobs" kind="stacked" scale="linear" fmt={(v) => jobs(v)}
          categories={cats}
          series={[
            { name: "On site", color: "var(--color-accent)", values: val((i) => r.years[i].jobs.onsite) },
            { name: "Supply chain", color: "var(--color-ink)", values: val((i) => r.years[i].jobs.supply_chain) },
            { name: "Induced", color: "var(--color-muted)", values: val((i) => r.years[i].jobs.induced) },
          ]}
          says={jobsSays}
          tip={<Tip id={`jobs-${view}`} label="jobs by year">Full-time jobs each year: the build&apos;s job-years spread evenly over its years, then each operating year&apos;s.</Tip>} />
        <details className="border-t border-rule" open={open} onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)} data-year-table={view}>
          <summary className="cursor-pointer py-2 text-sm font-semibold">Every year</summary>
          {(
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] border-collapse text-left text-xs tabular-nums">
                <caption className="sr-only">Scenario {view.toUpperCase()} by year</caption>
                <thead><tr className="border-b border-rule">{["Year", "Phase", "Jobs", "Earnings", ...(hasMwh ? ["MWh"] : []), ...(hasValue ? ["Taxable value"] : []), "Property tax", "Sales tax", "Income tax", "Severance"].map((h) => <th key={h} scope="col" className="px-2 py-1 font-semibold">{h}</th>)}</tr></thead>
                <tbody>
                  {r.years.map((y) => (
                    <tr key={y.year} className="border-b border-rule">
                      <td className="px-2 py-1">{y.year}</td><td className="px-2 py-1">{y.phase}</td>
                      {(["jobs", "earnings", ...(hasMwh ? ["mwh"] : []), ...(hasValue ? ["value"] : []), "property", "sales", "income", "severance"] as const).map((sname) => {
                        const v = stat(r, `year:${y.year}:${sname}`);
                        return <td key={sname} className="px-2 py-1 text-right">{v === null ? <span className="text-muted">-</span> : <Num check={`${key}|year:${y.year}:${sname}`} raw={v}>{displayOf(`year:${y.year}:${sname}`, v)}</Num>}</td>;
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </details>
      </div>
    </section>
  );
}

// ---- the same project in other states (session 347's third question, kept) ---------------------------------------------
function OtherStates({ P, jedi, x, v, view, sev }: { P: Params; jedi: Packed; x: Inputs; v: Values; view: View; sev: (s: string, v: number, p: number) => number | null }) {
  // fault 14 (session 4222): the scenario in every state JEDI gives a figure for, from the scenario's values as the reader
  // set them and each state's own defaults for the rest (its capital cost, capacity factor, tax rates and exemptions); a
  // first version carried the scenario's own state's defaults everywhere (Minnesota's wind exemption gave every state none)
  const per = Object.keys(jedi).filter((k) => k.startsWith(`${x.tech}:`) && !k.endsWith(":us")).map((k) => {
    const st = k.split(":")[1];
    const ix = STATE_LIST.findIndex(([s]) => s === st);
    const res = run(resolve(P, { ...v, state: ix, proj: NaN }), unpack(jedi, x.tech, st), P, sev);
    return { k: st, name: stateName(st), ok: res.ok, c: res.construction.jobs, taxes: res.pv.taxes, prop: res.property.held };
  }).filter((v) => v.ok).sort((a, b) => b.c.total - a.c.total);
  if (per.length < 2) return null;
  const shown = per.filter((v, i) => i < 10 || i >= per.length - 5 || v.k === x.state);
  const rank = per.findIndex((v) => v.k === x.state) + 1;
  const taxSorted = [...per].sort((a, b) => b.taxes - a.taxes);
  const byTax = taxSorted.filter((v, i) => i < 10 || i >= taxSorted.length - 5 || v.k === x.state);
  return (
    <section data-state-chart={view}>
      <h2 className="mb-2 text-lg font-semibold">Scenario {view.toUpperCase()} in other states<Tip id="states" label="other states">The scenario in each state: every input the scenario sets, and each state&apos;s own default for the rest (its capital cost, capacity factor, tax rates and exemptions), with that state&apos;s JEDI multipliers and JEDI&apos;s default cost there: construction job-years. {rank > 0 ? `${stateName(x.state)} is ${rank} of ${per.length}.` : ""} The ten states with the most, the scenario&apos;s own and the five with the fewest; the chart&apos;s table holds them.</Tip></h2>
      <StateChart id={`states-${view}`} unit="job-years" highlight={x.state}
        categories={shown.map((v) => v.name)} keys={shown.map((v) => v.k)}
        onsite={shown.map((v) => v.c.onsite)} supply={shown.map((v) => v.c.supply_chain)} induced={shown.map((v) => v.c.induced)} />
      <div className="mt-6" data-state-taxes={view}>
        <SeriesChart id={`state-taxes-${view}`} title="Taxes, present value, in other states" unit="USD (2025)" kind="stacked" scale="linear"
          fmt={(v) => usd(v).replace(/^USD /, "")}
          categories={byTax.map((v) => ({ label: v.name, sub: v.k === x.state ? "yours" : undefined }))}
          series={[{ name: "Taxes, present value", color: "var(--color-accent)", values: byTax.map((v) => v.taxes) }]}
          saysOnCard
          says={(i) => `${byTax[i].name}: ${usd(byTax[i].taxes)}${byTax[i].prop ? " (a property tax statute is held)" : " (no property tax rule held: sales and income tax only)"}`}
          tip={<Tip id={`state-taxes-${view}`} label="taxes in other states">The scenario&apos;s property, sales and use, income and severance taxes in each state, discounted at its rate: every input the scenario sets, and each state&apos;s own rules, rates, exemptions and default cost for the rest. A state without a held property tax statute shows its sales and income taxes only, so the bars are not like for like there: the hover says which. The ten states with the most, the scenario&apos;s own and the five with the fewest.</Tip>} />
      </div>
    </section>
  );
}

// ---- the run's files -------------------------------------------------------------------------------------------------
function save(name: string, text: string, type: string) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement("a");
  a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function Downloads({ P, x, r, jedi }: { P: Params; x: Record<View, Inputs>; r: Record<View, Result>; jedi: Packed }) {
  const btn = "border border-accent bg-white px-3 py-1 text-sm text-accent";
  const rows = { a: unpack(jedi, x.a.tech, x.a.state), b: unpack(jedi, x.b.tech, x.b.state) };
  return (
    <section data-downloads="1">
      <h2 className="mb-2 text-lg font-semibold">This run<Tip id="downloads" label="the run's files">The CSV holds both scenarios year by year. The Python script and the Stata do-file recompute both from the inputs and parameters they carry, and check their totals against the CSV's.</Tip></h2>
      <div className="flex flex-wrap gap-2">
        <button type="button" className={btn} data-download="csv" onClick={() => save("erw_local_impact_run.csv", csvOf(x, r), "text/csv")}>CSV</button>
        <button type="button" className={btn} data-download="py" onClick={() => save("erw_local_impact_run.py", pythonOf(P, x, rows, r), "text/x-python")}>Python</button>
        <button type="button" className={btn} data-download="do" onClick={() => save("erw_local_impact_run.do", stataOf(P, x, rows, r), "text/plain")}>Stata</button>
      </div>
    </section>
  );
}

