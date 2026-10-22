import { SiteLink as Link } from "@/components/SiteLink";
import { Num } from "@/components/Num";
import { InputPanel } from "@/components/tool/ToolPage";
import { COLUMNS, GRID_NAMES, PROFILES, hubRows, nodeRows, sitingHref, sitingInputs, type Row, type SitingInputs } from "@/lib/siting";
import { NODES, SITING_FILES } from "@/lib/sitingdata";
import { AllGridsForm } from "./AllGridsForm";

// Session 700 (chain 050, docs/methods/siting.md): the All grids tab of "What a datacenter pays". The questions "Your
// load" answers for one region (what a load pays, when it connects, how clean the power is) for every grid, hub and
// zone the page's price files hold, and behind a toggle every ERCOT node of node_basis_daily, in one table, with the
// same model: the rows are "Your load"'s own index (lib/sitingdata.ts), and each column is computed by the library
// function that computes it for "Your load" (lib/siting.ts). The left box holds every input, the right side only
// results. The tab ranks nothing by a score and expresses no view: it sorts by the column the reader chooses and says
// what the sort is. Every figure is a check key, allgrids|<column>|<row>, recomputed by scripts/check-values.mjs from the
// same files. Session 700 draws the rows, the toggle, the column heads with their tips, and one number: the row count.

const tipCls = "cursor-help border-b border-dotted border-white/70";

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
                  {COLUMNS.map((c) => <td key={c.id} className="px-3 py-1.5 text-right" data-cell={c.id} />)}
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
