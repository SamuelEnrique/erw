"use client";
// Session 709 (chain 050): the ERCOT node set of the All grids tab, as a virtual list: every node of node_basis_daily
// that is neither a hub nor a load zone, one row each, with only the figures that differ from node to node (the energy,
// the basis to HB_HUBAVG, the all-in figure, the days held). The page computes every row on the server
// (lib/siting.ts, nodeTable) and hands them here; this draws the rows in view and a few around them, so the browser holds
// a few dozen rows of the 873 at a time. It sorts by any column, ascending or descending, and keeps the sort in the
// address (nsort, ndir), so a reader can send the screen. The first rows of the default sort are drawn on the server,
// each figure with its check key.
// Session 724 (chain 062, the trader's walk): the basis's spread as a column; the months node_basis_daily lacks, named;
// a filter by name, kept in the address (nq); and the rows shown, downloaded as a CSV made here from the page's own
// figures (no new route, no read).
import { useRouter } from "next/navigation";
import { useEffect, useId, useMemo, useRef, useState } from "react";
import { NODE_SORTS, sortNodes, type NodeSort, type NodeTableRow } from "@/lib/siting";

const ROW = 34, VIEW = 18, PAD = 12, FIRST = 40;
const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const HEADS: Record<NodeSort, string> = { node: "Node", cls: "Class", energy: "Energy", basis: "Basis to HB_HUBAVG", spread: "Basis spread", swing: "Intraday swing", allin: "All-in", days: "Days held" };
const TIPS: Record<NodeSort, string> = {
  node: "The settlement point's name, as ERCOT gives it.",
  cls: "What ERCOT's disclosures say is settled at the node: storage, solar, wind, gas, other, mixed; unknown where no disclosure names it (node_basis_daily, x_class).",
  energy: "HB_HUBAVG's day-ahead price over its last twelve whole months, under the profile's rule, plus the node's mean daily day-ahead basis: USD per MWh.",
  basis: "The node's mean daily day-ahead price less HB_HUBAVG's, over the hub's twelve months, weighted by the days held (node_basis_daily): USD per MWh. Every node is set against the same hub, so this sorts the nodes as Energy does.",
  spread: "How far the node's daily basis moves: the day at nine in ten less the day at one in ten (its 90th percentile less its 10th) over the days the node holds in the file's twelve months (the panel says how many; a node under 90 percent of days has a spread but no energy figure), the panel's own percentiles: USD per MWh.",
  swing: "How far the node's day-ahead price moves within a day: each day's four dearest hours' mean less its four cheapest (node_basis_daily, dam_spread_4h), averaged over the days the node holds in the file's twelve months: USD per MWh. What a battery or a load that shifts its hours reads.",
  allin: "Energy plus the four-peak charge (paid on the hub's hours, the same at every node: above the table) plus capacity, none in ERCOT: USD per MWh.",
  days: "Days of day-ahead basis held over the hub's twelve months, of the days in them; under 90 percent, no twelve-month figure. The days the table lacks for every node are named above the list.",
};

// Session 711: a node's name opens its panel (the address's `node`, drawn by the server above the list).
export function AllGridsNodes({ rows, pkey, datacenter, sort, dir, open, short, find, csvHead }: { rows: NodeTableRow[]; pkey: string; datacenter: boolean; sort: NodeSort; dir: "asc" | "desc"; open: string | null;
  short: string; find: string; csvHead: string[] }) {
  const router = useRouter();
  const uid = useId();   // session 714: each heading's tip, reachable by the keyboard (app/tokens.css, ".tip")
  const pick = (id: string) => {
    const q = new URLSearchParams(window.location.search);
    if (open === id) q.delete("node"); else q.set("node", id);
    router.push(`${window.location.pathname}?${q.toString()}`, { scroll: false });
  };
  const [by, setBy] = useState<NodeSort>(sort);
  const [d, setD] = useState<"asc" | "desc">(dir);
  const [top, setTop] = useState(0);
  const [nq, setNq] = useState(find);
  const box = useRef<HTMLDivElement>(null);
  const sorted = useMemo(() => {
    const want = nq.trim().toUpperCase();
    return sortNodes(want ? rows.filter((r) => r.node.toUpperCase().includes(want)) : rows, by, d);
  }, [rows, by, d, nq]);
  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    if (by === "node" && d === "asc") { q.delete("nsort"); q.delete("ndir"); } else { q.set("nsort", by); q.set("ndir", d); }
    if (nq.trim()) q.set("nq", nq.trim()); else q.delete("nq");
    const s = q.toString();
    window.history.replaceState(null, "", `${window.location.pathname}${s ? `?${s}` : ""}`);
  }, [by, d, nq]);
  const download = () => {
    const cell = (v: number | null) => (v === null ? "" : String(v));
    const lines = [...csvHead.map((h) => `# ${h}`), `# ${short}`, "node,class,energy_usd_mwh,basis_usd_mwh,spread_usd_mwh,swing_usd_mwh,allin_usd_mwh,days_held,days_in_window",
      ...sorted.map((r) => [r.node, r.cls, cell(r.per), cell(r.basis), cell(r.spread), cell(r.swing), cell(r.allin), r.days, r.due].join(","))];
    const url = URL.createObjectURL(new Blob([lines.join("\n") + "\n"], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url; a.download = `erw_allgrids_ercot_nodes${nq.trim() ? `_${nq.trim().replace(/[^A-Za-z0-9_]+/g, "_")}` : ""}.csv`;
    document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
  };
  // the server and the first render draw the first FIRST rows; once mounted, the rows in view and PAD around them
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  const start = mounted ? Math.max(0, Math.floor(top / ROW) - PAD) : 0;
  const end = Math.min(sorted.length, mounted ? Math.floor(top / ROW) + VIEW + PAD : FIRST);
  const click = (k: NodeSort) => { if (k === by) setD(d === "asc" ? "desc" : "asc"); else { setBy(k); setD(k === "node" || k === "cls" ? "asc" : "desc"); } };
  const energyKey = (r: NodeTableRow) => (datacenter ? `allgrids|energy|${r.id}|da` : `allgrids|energy|${r.id}|da|${pkey}`);
  const cols = "grid grid-cols-[minmax(8rem,1.4fr)_4.5rem_5rem_5.5rem_5rem_5rem_5rem_5rem] items-center gap-x-2 px-3";
  return (
    <div data-allgrids-nodes="1">
      <div className="mb-2 flex flex-wrap items-end gap-3 text-sm">
        <label className="flex flex-col gap-1">Find a node by name
          <input type="search" value={nq} onChange={(e) => { setNq(e.target.value); setTop(0); box.current?.scrollTo({ top: 0 }); }} placeholder="for example RN or SOLAR"
            className="w-64 max-w-full border border-rule bg-panel px-2 py-1 font-mono text-sm text-ink" data-node-find="1" />
        </label>
        <button type="button" onClick={download} className="border border-rule px-2 py-1 text-sm" data-node-download="1">Download these {sorted.length.toLocaleString("en-US")} rows (CSV)</button>
      </div>
      <p className="mb-2 text-sm" role="status" data-node-sort={`${by}|${d}`}>
        Sorted by {HEADS[by].charAt(0).toLowerCase() + HEADS[by].slice(1)}, {d === "asc" ? "smallest first" : "largest first"}{by === "node" || by === "cls" ? " (alphabetical)" : ""}; a node with no figure last. {sorted.length.toLocaleString("en-US")} of {rows.length.toLocaleString("en-US")} nodes shown{nq.trim() ? ` (names holding "${nq.trim()}")` : ""}. Click a heading to sort by it, again to turn it round. Days held: {short}.
      </p>
      <div className="overflow-x-auto" role="region" aria-label="ERCOT nodes" tabIndex={0}>
        <div style={{ minWidth: 740 }} role="table" aria-label="ERCOT nodes" aria-rowcount={sorted.length + 1}>
          <div className={`${cols} bg-accent py-1.5 text-sm text-white`} role="row">
            {NODE_SORTS.map((k) => (
              <span key={k} className={`tip relative ${k === "node" || k === "cls" ? "text-left" : "text-right"}`} role="columnheader" aria-sort={by === k ? (d === "asc" ? "ascending" : "descending") : "none"}>
                <button type="button" aria-describedby={`${uid}-${k}`} onClick={() => click(k)} className="border-b border-dotted border-white/70" data-node-head={k}>
                  <span className="text-white">{HEADS[k]}{by === k ? (d === "asc" ? " (up)" : " (down)") : ""}</span>
                </button>
                <span role="tooltip" id={`${uid}-${k}`} className="absolute left-0 top-full z-20 hidden w-64 max-w-[80vw] whitespace-normal border border-rule bg-paper px-2 py-1.5 text-left text-xs font-normal leading-snug text-ink">{TIPS[k]} Press to sort by it; again to turn it round.</span>
              </span>
            ))}
          </div>
          <div ref={box} className="relative overflow-y-auto border-b border-rule" style={{ height: Math.min(sorted.length, VIEW) * ROW }} onScroll={(e) => setTop(e.currentTarget.scrollTop)} data-node-list="1" role="rowgroup">
            <div style={{ height: sorted.length * ROW, position: "relative" }}>
              {sorted.slice(start, end).map((r, i) => (
                <div key={r.id} className={`${cols} absolute left-0 right-0 border-b border-rule text-sm tabular-nums`} style={{ top: (start + i) * ROW, height: ROW }} data-allgrids-row={r.id} role="row" aria-rowindex={start + i + 2}>
                  <span role="cell" className="min-w-0"><button type="button" onClick={() => pick(r.id)} aria-pressed={open === r.id} className={`truncate text-left underline decoration-dotted ${open === r.id ? "font-semibold" : ""}`} aria-label={`${r.node}: open its panel${r.types ? `; ERCOT's resource types ${r.types}` : ""}`} data-node-open={r.id}>{r.node}</button></span>
                  <span role="cell" className="text-xs">{r.cls}</span>
                  <span role="cell" className="text-right">{r.per === null ? <span className="tip relative inline-block"><button type="button" aria-describedby={`${uid}-why-${r.id}`} className="cursor-help border-b border-dotted border-muted" data-tip-trigger="1">not held</button><span role="tooltip" id={`${uid}-why-${r.id}`} className="absolute right-0 top-full z-20 hidden w-64 max-w-[80vw] whitespace-normal border border-rule bg-paper px-2 py-1.5 text-left text-xs leading-snug text-ink">{r.why}</span></span> : <span data-check={energyKey(r)} data-raw={String(r.per)}>{two(r.per)}</span>}</span>
                  <span role="cell" className="text-right">{r.basis === null ? "" : <span data-check={`allgrids|basis|${r.id}`} data-raw={String(r.basis)}>{two(r.basis)}</span>}</span>
                  <span role="cell" className="text-right">{r.spread === null ? "" : <span data-check={`allgrids|nodespread|${r.id}`} data-raw={String(r.spread)}>{two(r.spread)}</span>}</span>
                  <span role="cell" className="text-right">{r.swing === null ? "" : <span data-check={`allgrids|nodeswing|${r.id}`} data-raw={String(r.swing)}>{two(r.swing)}</span>}</span>
                  <span role="cell" className="text-right">{r.allin === null ? "" : <span data-check={`allgrids|allin|${r.id}|${pkey}`} data-raw={String(r.allin)}>{two(r.allin)}</span>}</span>
                  <span role="cell" className="text-right text-xs">{r.days.toLocaleString("en-US")}{r.due ? ` of ${r.due}` : ""}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
