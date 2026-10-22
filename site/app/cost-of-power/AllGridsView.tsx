import { SiteLink as Link } from "@/components/SiteLink";
import { Num } from "@/components/Num";
import { InlineSpark } from "@/components/InlineSpark";
import { InputPanel } from "@/components/tool/ToolPage";
import type { ReactNode } from "react";
import { COLUMNS, GRID_NAMES, NODE_HUB, PROFILES, energyCell, hubRows, nodeRows, sitingHref, sitingInputs, type EnergyCell, type Row, type SitingInputs, type Twelve } from "@/lib/siting";
import { NODES, SITING_DC, SITING_FILES } from "@/lib/sitingdata";
import { AllGridsForm } from "./AllGridsForm";

// Session 700 (chain 050, docs/methods/siting.md): the All grids tab of "What a datacenter pays". The questions "Your
// load" answers for one region (what a load pays, when it connects, how clean the power is) for every grid, hub and
// zone the page's price files hold, and behind a toggle every ERCOT node of node_basis_daily, in one table, with the
// same model: the rows are "Your load"'s own index (lib/sitingdata.ts), and each column is computed by the library
// function that computes it for "Your load" (lib/siting.ts). The left box holds every input, the right side only
// results. The tab ranks nothing by a score and expresses no view: it sorts by the column the reader chooses and says
// what the sort is. Every figure is a check key, allgrids|<column>|<row>, recomputed by scripts/check-values.mjs from the
// same files. Session 700 draws the rows, the toggle, the column heads with their tips, and one number: the row count.

const tipCls = "cursor-help border-b border-dotted border-muted";
const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const monthWords = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });

/** A cell the warehouse cannot fill: short words in ink, the reason on hover and on focus (no visible grey text). */
function Words({ words, why }: { words: string; why: string }) {
  return <span className={tipCls} title={why} tabIndex={0} data-cell-words="1">{words}</span>;
}
/** One figure with its hover: the reason, the window and its source. */
function Fig({ check, v, tip, children }: { check: string; v: number; tip: string; children?: ReactNode }) {
  return (
    <span className={`group relative inline-block ${tipCls}`} title={tip} tabIndex={0}>
      <Num check={check} raw={v}>{two(v)}</Num>
      {children}
    </span>
  );
}
/** Session 701: the twelve months of a figure, drawn on hover and on focus (the shared inline chart, components/InlineSpark). */
function Spark({ t, label }: { t: Twelve; label: string }) {
  return (
    <span className="pointer-events-none absolute right-0 top-full z-10 hidden border border-rule bg-white p-1 group-hover:block group-focus:block" data-spark="1">
      <InlineSpark values={t.months.map((r) => ({ t: `${r.m}-01`, v: r.per }))} label={label} width={140} height={32} />
    </span>
  );
}
function twelveTip(t: Twelve, market: string): string {
  const last = t.months.at(-1)!;
  return `${market}, a flat load, ${monthWords(t.from)} to ${monthWords(t.to)}, ${t.hours.toLocaleString("en-US")} hours held: USD ${two(t.per)} per MWh. The last whole month, ${monthWords(last.m)}: USD ${two(last.per)}.${t.year ? ` The last whole year, ${t.year.y}: USD ${two(t.year.per)}.` : ""} From the page's hourly files, as "Your load" computes it (lib/datacenter.ts).`;
}
/** Session 701: the energy cell: the day-ahead figure, real time beside it where held; a node's hub plus its basis. */
function EnergyTd({ r, e }: { r: Row; e: EnergyCell }) {
  if (e.node) {
    const n = e.node;
    return (
      <Fig check={`allgrids|energy|${r.id}|da`} v={n.per}
        tip={`${NODE_HUB}'s day-ahead price over ${monthWords(n.hub.from)} to ${monthWords(n.hub.to)}, USD ${two(n.hub.per)} per MWh, plus this node's mean daily day-ahead basis to it, USD ${two(n.basis)}, over ${n.days} of the ${n.due} days (node_basis_daily, daily, not hourly). Real time is not held at the nodes for twelve months.`}>
        <Spark t={n.hub} label={`${NODE_HUB} day-ahead by month`} />
      </Fig>
    );
  }
  if (!e.da && !e.rt) return <Words words={e.words ?? "not held"} why={e.why ?? ""} />;
  return (
    <span className="whitespace-nowrap">
      {e.da ? <Fig check={`allgrids|energy|${r.id}|da`} v={e.da.per} tip={twelveTip(e.da, "Day-ahead")}><Spark t={e.da} label={`${r.region} day-ahead by month`} /></Fig> : <Words words="no day-ahead" why={`Twelve whole months of day-ahead prices are not held for ${r.region}.`} />}
      {e.rt ? <span className="ml-2 text-xs" data-rt="1">rt <Fig check={`allgrids|energy|${r.id}|rt`} v={e.rt.per} tip={twelveTip(e.rt, "Real time")} /></span> : null}
    </span>
  );
}

function RowToggle({ x, hubs, nodes }: { x: SitingInputs; hubs: number; nodes: number }) {
  const item = (rows: SitingInputs["rows"], label: string, n: number) => {
    const on = x.rows === rows;
    return (
      <Link href={sitingHref(x, { rows })} scroll={false} aria-current={on ? "page" : undefined} data-allgrids-rows={rows}
        style={{ color: on ? "var(--color-surface)" : "var(--color-ink)" }}
        className={`border px-2 py-1 no-underline ${on ? "border-accent bg-accent" : "border-rule bg-white hover:border-accent"}`}>
        <span style={{ color: on ? "var(--color-surface)" : "var(--color-ink)" }}>{label} ({n.toLocaleString("en-US")})</span>
      </Link>
    );
  };
  return <nav aria-label="Rows" className="mb-3 flex flex-wrap gap-1 text-xs" data-allgrids-toggle="1">{item("hubs", "Hubs and zones", hubs)}{item("nodes", "ERCOT nodes", nodes)}</nav>;
}

function RowHead({ r }: { r: Row }) {
  return (
    <th scope="row" className="px-3 py-1.5 text-left font-normal" data-row={r.id}>
      <span className="text-xs text-muted">{GRID_NAMES[r.grid]}</span>{" "}
      {r.blank ? <span className="cursor-help border-b border-dotted border-muted" title={r.blank.why} tabIndex={0}>{r.label}</span> : r.label}
    </th>
  );
}

export function AllGridsView({ q }: { q: Record<string, string | undefined> }) {
  const x = sitingInputs(q);
  const hubs = hubRows(SITING_FILES.index), nodes = nodeRows(NODES);
  const rows = x.rows === "nodes" ? nodes : hubs;
  const p = PROFILES[x.profile];
  return (
    <div className="grid gap-8 lg:grid-cols-[290px_minmax(0,1fr)]" data-no-usage="1" data-allgrids="1">
      <aside>
        <InputPanel title="Your load">
          <AllGridsForm x={x} />
        </InputPanel>
      </aside>
      <div className="min-w-0">
        <p className="mb-3 max-w-3xl text-sm" data-allgrids-count={x.rows}>
          {x.rows === "nodes"
            ? <>Every ERCOT node of node_basis_daily that is neither a hub nor a load zone: <Num check="allgrids|rows|nodes" raw={nodes.length}>{nodes.length.toLocaleString("en-US")}</Num> nodes, from {NODES.first} to {NODES.last}.</>
            : <>Every hub and load zone the page&apos;s price files hold, and the grids they do not price: <Num check="allgrids|rows|hubs" raw={hubs.length}>{hubs.length.toLocaleString("en-US")}</Num> rows.</>}
          {" "}A {p.label.toLowerCase()} load of {x.mw.toLocaleString("en-US")} MW at a load factor of {x.lf.toFixed(2)}. Sorted by grid, then by name.
        </p>
        <RowToggle x={x} hubs={hubs.length} nodes={nodes.length} />
        <div className="overflow-x-auto" role="region" aria-label="All grids" tabIndex={0} data-allgrids-table="1">
          <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: 960 }}>
            <caption className="sr-only">What a {p.label.toLowerCase()} load pays, when it connects and how clean the power is, {x.rows === "nodes" ? "at every ERCOT node" : "at every hub and zone"}</caption>
            <thead>
              <tr className="bg-accent text-white">
                <th scope="col" className="px-3 py-1.5 font-normal">{x.rows === "nodes" ? "Node" : "Grid and region"}</th>
                {COLUMNS.map((c) => (
                  <th key={c.id} scope="col" className="px-3 py-1.5 text-right font-normal" data-col={c.id}>
                    <span className={tipCls} title={`${c.tip} ${c.unit}.`} tabIndex={0}>{c.head}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-b border-rule" data-allgrids-row={r.id}>
                  <RowHead r={r} />
                  {COLUMNS.map((c) => <td key={c.id} className="px-3 py-1.5 text-right" data-cell={c.id}>{c.id === "energy" ? <EnergyTd r={r} e={energyCell(SITING_DC, SITING_FILES, r)} /> : null}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-2 max-w-3xl text-xs" data-allgrids-method="1">
          One row a hub, zone or node; one column a question. The columns are filled one session at a time from the warehouse&apos;s own tables, each by the function that computes it for &quot;Your load&quot;.
          {" "}<Link href="/data/methods/siting">Method note</Link>.
        </p>
      </div>
    </div>
  );
}
