"use client";
// Chain 740 (lab-desktop window 3), session 10803: the datacenter on /impact, the parts of the page that differ from a
// plant's: its left-box groups (lib/dcui.ts's fields, defaults in grey with their sources in hover tips, edited in place),
// the announced projects to pick from, its year chart and table, and its taxes in other states. The arithmetic is
// lib/dcimpact.ts (docs/methods/forecast.md, the datacenter sections, internal).
import { useState, type ReactNode } from "react";
import { SeriesChart } from "@/components/tool/SeriesChart";
import { Tip } from "@/components/tool/ToolPage";
import { Num } from "@/components/Num";
import { stateName } from "@/lib/impact";
import { dcDefaults, dcDisplay, dcKey, dcRun, dcStat, type DcInputs, type DcParams, type DcResult } from "@/lib/dcimpact";
import { DC_FIELDS, DC_GROUPS, DC_UNREAD_EXEMPTION, dcClamp, dcResolve, type DcField, type DcProject } from "@/lib/dcui";
import { jobsText, usdText } from "@/lib/forecast";

export { dcDisplay };
type View = "a" | "b";
type Values = Record<string, number>;
const box = "w-full border border-rule bg-white px-2 py-1 text-sm";
const plain = (v: number, d = 2) => v.toLocaleString("en-US", { maximumFractionDigits: d });

// ---- the left box ----------------------------------------------------------------------------------------------------
export function DcGroups({ P2, v, state, set, update, dcList, techState }: { P2: DcParams; v: Values; state: string; set: (k: string, val: number) => void;
  update: (nv: Values) => void; dcList: DcProject[]; techState: ReactNode }) {
  // the defaults in grey: an investment not set follows the MW, construction workers the investment (set or not)
  const mwSet = Number.isFinite(v.dmw) ? { mw: v.dmw } : {};
  const dNone = dcDefaults(P2, state);  // the size's own default: the announced median, whatever is typed
  const dBase = dcDefaults(P2, state, mwSet);
  const d = dcDefaults(P2, state, { ...mwSet, ...(Number.isFinite(v.invest) ? { invest: v.invest } : {}) });
  const mine = dcList.map((p, i) => ({ p, i })).filter(({ p }) => p.state === state);
  const cur = Number.isFinite(v.dcproj) && dcList[v.dcproj]?.state === state ? v.dcproj : NaN;
  const pick = (i: number) => {
    const blank = Object.fromEntries(["dmw", "invest", "perm", "cons"].map((k) => [k, NaN]));
    if (!Number.isFinite(i)) { update({ ...v, dcproj: NaN }); return; }
    const p = dcList[i];
    update({ ...v, ...blank, dcproj: i, ...(p.mw !== null ? { dmw: p.mw } : {}), ...(p.invest !== null ? { invest: p.invest } : {}),
      ...(p.perm !== null ? { perm: p.perm } : {}), ...(p.cons !== null ? { cons: p.cons } : {}) });
  };
  return (
    <>
      {DC_GROUPS.map((g) => {
        const fs = DC_FIELDS.filter((f) => f.group === g.key);
        const changed = fs.filter((f) => Number.isFinite(v[f.name])).length;
        return (
          <details key={g.key} className="border-t border-rule" data-group={`dc-${g.key}`} open={g.open}>
            <summary className="cursor-pointer py-2 text-sm font-semibold">{g.title}{changed ? <span className="ml-2 text-xs font-normal text-muted">{changed} changed</span> : null}</summary>
            <div className="space-y-3 pb-3">
              {g.key === "project" ? techState : null}
              {g.key === "project" ? (
                <div className="text-sm" data-field="dcproj">
                  <div className="mb-1 font-semibold">Announced project</div>
                  <select className={box} value={Number.isFinite(cur) ? cur : ""} data-assumption="dcproj" aria-label="An announced datacenter in this state" disabled={!mine.length}
                    onChange={(e) => pick(e.target.value === "" ? NaN : Number(e.target.value))}>
                    <option value="">{mine.length ? "None: the inputs below" : "None read in this state"}</option>
                    {mine.map(({ p, i }) => <option key={p.id} value={i}>{p.name}{p.mw !== null ? `, ${plain(p.mw, 0)} MW` : ""}, {p.date.slice(0, 4)}</option>)}
                  </select>
                  <p className="mt-1 text-xs leading-snug text-muted" data-default="dcproj">
                    {Number.isFinite(cur) ? <>{dcList[cur].where ? `${dcList[cur].where}. ` : ""}As {dcList[cur].publisher} stated it, {dcList[cur].date}: <a href={dcList[cur].url} rel="noopener" className="underline">the document</a>.{dcList[cur].skipped ? <span className="block" data-skipped={dcList[cur].id}>{dcList[cur].skipped}</span> : null}</> : `${mine.length} announced in this state`}
                    <Tip id="f-dcproj" label="the announced project">Announced datacenters whose own documents (a state agency&apos;s or a company&apos;s release) state what they would bring, read by the ERW: each figure is the document&apos;s own. Picking one sets the MW, the investment (in 2025 dollars), the permanent jobs and the construction workers the document states; a figure it does not state keeps its default. A document&apos;s construction jobs are a headcount (at peak where it says so), held in every construction year here. A wage or a split of the spending that a document states is not taken (Pima County&apos;s bulletin on Beale&apos;s Project Blue gives average salaries of USD 64,000 and USD 2.4 billion of its USD 3.6 billion for equipment): the earnings stay Census County Business Patterns&apos; and the split JLARC&apos;s, unless typed under Jobs and wages or Spending.</Tip>
                  </p>
                  <p className="mt-2 text-xs leading-snug text-muted" data-defaults-note="dc">
                    The defaults below are medians over the announced projects the ERW has read ({dcList.length} in the list{P2.announced.computed ? `, as of ${P2.announced.computed}` : ""}): the size from the {P2.announced.defaults.mw_stated.n} that state it, the capital cost from {P2.announced.defaults.investment_per_mw.n}, the permanent jobs from {P2.announced.defaults.permanent_jobs_per_mw.n} and the construction workers from {P2.announced.defaults.construction_jobs_per_billion.n}.{dcList.some((p) => p.toDate) ? ` ${dcList.filter((p) => p.toDate).length} of the list are campuses' figures to date, which enter no median.` : ""} They move when another project is read.
                  </p>
                </div>
              ) : null}
              {fs.map((f) => <DcOne key={f.name} f={f} P2={P2} state={state} v={v} d={f.name === "dmw" ? dNone : f.name === "invest" ? dBase : d} set={set} />)}
            </div>
          </details>
        );
      })}
    </>
  );
}

function shownDc(f: DcField, d: DcInputs): string {
  const val = d[f.input];
  if (val === null) return "not given";
  if (typeof val === "boolean") return val ? "Applied where the project qualifies" : "Not applied";
  if (f.input === "start") return String(val);
  return plain(val as number, 2);
}

function DcOne({ f, P2, state, v, d, set }: { f: DcField; P2: DcParams; state: string; v: Values; d: DcInputs; set: (k: string, val: number) => void }) {
  const isSet = Number.isFinite(v[f.name]);
  const links = f.links ? f.links(state, P2) : [];
  const tip = <Tip id={`f-${f.name}`} label={f.label}>{f.source(state, P2)}{links.length ? <> Source: {links.map((l, i) => <span key={l.href}>{i ? "; " : ""}<a href={l.href} rel="noopener" className="underline" data-source-link={f.name}>{l.text}</a></span>)}.</> : null}</Tip>;
  let control: ReactNode;
  if (f.options) {
    const cur = isSet ? v[f.name] : (d[f.input] ? 1 : 0);
    control = (
      <select className={box} value={cur} data-assumption={f.name} aria-label={f.label} onChange={(e) => set(f.name, Number(e.target.value))}>
        {f.options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    );
  } else {
    const shown = isSet ? v[f.name] : (d[f.input] as number | null);
    control = <DcNumber f={f} value={shown} onValue={(val) => set(f.name, val)} />;
  }
  return (
    <div className="text-sm" data-field={f.name}>
      <div className="mb-1 font-semibold">{f.label}{f.unit ? <span className="font-normal">, {f.unit}</span> : null}</div>
      <div className="flex items-center gap-2">
        {control}
        <button type="button" data-reset={f.name} aria-label={`Reset ${f.label}`} disabled={!isSet}
          className="whitespace-nowrap border border-rule bg-white px-2 py-1 text-xs text-accent disabled:text-muted" onClick={() => set(f.name, NaN)}>Reset</button>
      </div>
      <p className="mt-1 text-xs leading-snug text-muted" data-default={f.name}>Default {shownDc(f, d)}{tip}</p>
    </div>
  );
}

function DcNumber({ f, value, onValue }: { f: DcField; value: number | null; onValue: (v: number) => void }) {
  const [text, setText] = useState<string | null>(null);
  const shown = text !== null ? text : value === null ? "" : String(Math.round(value * 10000) / 10000);
  return (
    <input type="number" inputMode="decimal" autoComplete="off" min={f.min} max={f.max} step={f.whole ? 1 : "any"} value={shown} className={box}
      data-assumption={f.name} aria-label={`${f.label}${f.unit ? `, ${f.unit}` : ""}`} placeholder={value === null ? "not given" : undefined}
      onChange={(e) => {
        setText(e.target.value);
        if (e.target.value === "") { onValue(NaN); return; }
        const n = Number(e.target.value);
        if (Number.isFinite(n)) onValue(dcClamp(f, n));
      }}
      onBlur={() => setText(null)} />
  );
}

// ---- the scenario in view, by year -----------------------------------------------------------------------------------
export function DcYears({ x, r, view }: { x: DcInputs; r: DcResult; view: View }) {
  const [open, setOpen] = useState(false);
  if (!r.ok) return <p className="text-sm text-muted">Scenario {view.toUpperCase()} has no figure: {r.why}.</p>;
  const cats = r.years.map((y) => ({ label: String(y.year), sub: y.phase === "construction" ? "build" : undefined }));
  const val = (f: (i: number) => number | null) => r.years.map((_, i) => f(i));
  const taxSeries = [
    ...(r.years.some((y) => y.property !== null) ? [{ name: "Property", color: "var(--color-year-1)", values: val((i) => r.years[i].property ?? 0) }] : []),
    { name: "Sales and use, paid", color: "var(--color-year-2)", values: val((i) => r.years[i].sales ?? 0) },
    { name: "Income", color: "var(--color-year-3)", values: val((i) => r.years[i].income) },
    ...(r.elec.held ? [{ name: "Electricity", color: "var(--color-year-4)", values: val((i) => r.years[i].elec ?? 0) }] : []),
  ];
  const short = (v: number) => usdText(v).replace(/^USD /, "");
  const say = (i: number) => {
    const y = r.years[i];
    return `${y.year} (${y.phase}): property ${y.property === null ? "not held" : usdText(y.property)}, sales paid ${usdText(y.sales ?? 0)} (forgone by the exemption ${usdText(y.forgone ?? 0)}), income ${usdText(y.income)}, electricity ${y.elec === null ? "not held" : usdText(y.elec)}`;
  };
  const jobsSays = (i: number) => { const y = r.years[i]; return `${y.year} (${y.phase}): ${jobsText(y.jobs.total)} jobs (on site ${jobsText(y.jobs.onsite)}${r.chain.held ? `, supply chain ${jobsText(y.jobs.supply_chain)}, induced ${jobsText(y.jobs.induced)}` : "; supply chain and induced not held"})`; };
  const key = dcKey(x);
  const cols: [string, string][] = [["jobs", "Jobs"], ["earnings", "Earnings"], ["equipment", "Equipment bought"], ["property", "Property tax"], ["salesbefore", "Sales tax before exemption"],
    ["forgone", "Forgone by exemption"], ["sales", "Sales tax paid"], ["income", "Income tax"], ["elec", "Electricity tax"]];
  return (
    <section data-years={view} data-dc="1">
      <h2 className="mb-2 text-lg font-semibold">Scenario {view.toUpperCase()} by year</h2>
      <div className="space-y-6">
        <SeriesChart id={`tax-${view}`} title="Taxes by year" unit="USD (2025)" kind="stacked" scale="linear" fmt={short} categories={cats} series={taxSeries} says={say}
          tip={<Tip id={`tax-${view}`} label="taxes by year">Each year&apos;s property tax (where the reader&apos;s rates are given), sales and use tax paid after any exemption, income tax and (where a statute and the MWh are held) the tax on the electricity bought, in 2025 dollars. The tax a datacenter exemption forgoes is not paid and is not drawn: it is in the hover and the table.</Tip>} />
        <SeriesChart id={`jobs-${view}`} title="Jobs by year" unit="jobs" kind="stacked" scale="linear" fmt={(v) => jobsText(v)} categories={cats}
          series={[
            { name: "On site", color: "var(--color-accent)", values: val((i) => r.years[i].jobs.onsite) },
            ...(r.chain.held ? [{ name: "Supply chain", color: "var(--color-ink)", values: val((i) => r.years[i].jobs.supply_chain) },
              { name: "Induced", color: "var(--color-muted)", values: val((i) => r.years[i].jobs.induced) }] : []),
          ]}
          says={jobsSays}
          tip={<Tip id={`jobs-${view}`} label="jobs by year">{r.chain.held ? "On site, and in the supply chain and induced by the ratios of the state's own published study (Virginia: JLARC, 2024; Georgia and Minnesota: the Carl Vinson Institute for the state auditor and the Legislative Budget Office, 2025)." : "On site only: no public multiplier for datacenters is held for this state, so the supply chain and induced jobs are not drawn (BEA sells them)."} Construction years hold the construction workers on site; operating years the permanent jobs.</Tip>} />
        <details className="border-t border-rule" open={open} onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)} data-year-table={view}>
          <summary className="cursor-pointer py-2 text-sm font-semibold">Every year</summary>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] border-collapse text-left text-xs tabular-nums">
              <caption className="sr-only">Scenario {view.toUpperCase()} by year</caption>
              <thead><tr className="border-b border-rule">{["Year", "Phase", ...cols.map((c) => c[1])].map((h) => <th key={h} scope="col" className="px-2 py-1 font-semibold">{h}</th>)}</tr></thead>
              <tbody>
                {r.years.map((y) => (
                  <tr key={y.year} className="border-b border-rule">
                    <td className="px-2 py-1">{y.year}</td><td className="px-2 py-1">{y.phase}</td>
                    {cols.map(([sname]) => {
                      const v = dcStat(r, `year:${y.year}:${sname}`);
                      return <td key={sname} className="px-2 py-1 text-right">{v === null ? <span className="text-muted">-</span> : <Num check={`${key}|year:${y.year}:${sname}`} raw={v}>{dcDisplay(`year:${y.year}:${sname}`, v)}</Num>}</td>;
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      </div>
    </section>
  );
}

// ---- the same datacenter in other states -------------------------------------------------------------------------------
export function DcOtherStates({ P2, v, x, view, states }: { P2: DcParams; v: Values; x: DcInputs; view: View; states: string[] }) {
  // the scenario's values as the reader set them, each state's own defaults for the rest (its wages, rates, exemption)
  const per = states.map((st) => {
    const res = dcRun(dcResolve(P2, { ...v, dcproj: NaN }, st), P2);
    // session 10808: property tax is left out of the comparison: its rates are each locality's, so the scenario's typed
    // rates would be laid on every state's cost (and Louisiana's 10 and 15 percent assessment lost elsewhere)
    const taxes = (res.pv.sales ?? 0) + res.pv.income + (res.pv.elec ?? 0);
    return { k: st, name: stateName(st), ok: res.ok, taxes, forgone: res.pv.forgone ?? 0, rule: !!P2.rules.states[st]?.sales_exemption && !P2.rules.states[st]?.sales_exemption?.discretionary };
  }).filter((p) => p.ok).sort((a, b) => b.taxes - a.taxes);
  if (per.length < 2) return null;
  const shown = per.filter((p, i) => i < 10 || i >= per.length - 5 || p.k === x.state);
  const rank = per.findIndex((p) => p.k === x.state) + 1;
  return (
    <section data-state-chart={view} data-dc="1">
      <h2 className="mb-2 text-lg font-semibold">Scenario {view.toUpperCase()} in other states<Tip id="dc-states" label="other states">The same datacenter in each state: every input the scenario sets, and each state&apos;s own wages, sales and income tax rates and datacenter rules for the rest. {rank > 0 ? `${stateName(x.state)} is ${rank} of ${per.length} by these taxes' present value.` : ""} Property tax is left out: its rates are each locality&apos;s. An exemption counts only where the ERW holds the state&apos;s rule, read from its statute or its agency&apos;s own description, so the bars are not like for like: the hover says which. Texas and Tennessee have datacenter exemptions in statute that the ERW could not read: their bars are before them.</Tip></h2>
      <SeriesChart id={`dc-state-taxes-${view}`} title="Sales, income and electricity taxes, present value, in other states" unit="USD (2025)" kind="stacked" scale="linear"
        fmt={(n) => usdText(n).replace(/^USD /, "")}
        categories={shown.map((p) => ({ label: p.name, sub: p.k === x.state ? "yours" : undefined }))}
        series={[{ name: "Sales, income and electricity taxes, present value", color: "var(--color-accent)", values: shown.map((p) => p.taxes) }]}
        saysOnCard
        says={(i) => `${shown[i].name}: ${usdText(shown[i].taxes)}${shown[i].rule ? `; a datacenter rule is applied (forgone by its exemption, present value ${usdText(shown[i].forgone)})` : DC_UNREAD_EXEMPTION[shown[i].k] ? "; the state's datacenter exemption exists in statute but could not be read: sales tax before it" : "; no datacenter rule applied (none read, or held as words): sales tax before exemptions"}`}
        tip={<Tip id={`dc-state-taxes-${view}`} label="taxes in other states">The ten states with the most, the scenario&apos;s own and the five with the fewest.</Tip>} />
    </section>
  );
}

/** One datacenter figure's cell value, for the A and B table */
export const dcCell = (r: DcResult, figure: string) => dcStat(r, figure);
export const dcCheck = (x: DcInputs, figure: string) => `${dcKey(x)}|${figure}`;
