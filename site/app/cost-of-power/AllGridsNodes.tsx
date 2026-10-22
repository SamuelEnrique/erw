"use client";
// Session 709 (chain 050): the ERCOT node set of the All grids tab, as a virtual list: every node of node_basis_daily
// that is neither a hub nor a load zone, one row each, with only the figures that differ from node to node (the energy,
// the basis to HB_HUBAVG, the all-in figure, the days held). The page computes every row on the server
// (lib/siting.ts, nodeTable) and hands them here; this draws the rows in view and a few around them, so the browser holds
// a few dozen rows of the 873 at a time. It sorts by any column, ascending or descending, and keeps the sort in the
// address (nsort, ndir), so a reader can send the screen. The first rows of the default sort are drawn on the server,
// each figure with its check key.
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { NODE_SORTS, sortNodes, type NodeSort, type NodeTableRow } from "@/lib/siting";

const ROW = 34, VIEW = 18, PAD = 12, FIRST = 40;
const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const HEADS: Record<NodeSort, string> = { node: "Node", cls: "Class", energy: "Energy", basis: "Basis to HB_HUBAVG", allin: "All-in", days: "Days held" };
const TIPS: Record<NodeSort, string> = {
  node: "The settlement point's name, as ERCOT gives it.",
  cls: "What ERCOT's disclosures say is settled at the node: storage, solar, wind, gas, other, mixed; unknown where no disclosure names it (node_basis_daily, x_class).",
  energy: "HB_HUBAVG's day-ahead price over its last twelve whole months, under the profile's rule, plus the node's mean daily day-ahead basis: USD per MWh.",
  basis: "The node's mean daily day-ahead price less HB_HUBAVG's, over the hub's twelve months, weighted by the days held (node_basis_daily): USD per MWh.",
  allin: "Energy plus the four-peak charge (paid on the hub's hours, the same at every node: above the table) plus capacity, none in ERCOT: USD per MWh.",
  days: "Days of day-ahead basis held over the hub's twelve months, of the days in them; under 90 percent, no twelve-month figure.",
};

// Session 711: a node's name opens its panel (the address's `node`, drawn by the server above the list).
export function AllGridsNodes({ rows, pkey, datacenter, sort, dir, open }: { rows: NodeTableRow[]; pkey: string; datacenter: boolean; sort: NodeSort; dir: "asc" | "desc"; open: string | null }) {
  const router = useRouter();
  const pick = (id: string) => {
    const q = new URLSearchParams(window.location.search);
    if (open === id) q.delete("node"); else q.set("node", id);
    router.push(`${window.location.pathname}?${q.toString()}`, { scroll: false });
  };
  const [by, setBy] = useState<NodeSort>(sort);
  const [d, setD] = useState<"asc" | "desc">(dir);
  const [top, setTop] = useState(0);
  const box = useRef<HTMLDivElement>(null);
  const sorted = useMemo(() => sortNodes(rows, by, d), [rows, by, d]);
  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    if (by === "node" && d === "asc") { q.delete("nsort"); q.delete("ndir"); } else { q.set("nsort", by); q.set("ndir", d); }
    const s = q.toString();
    window.history.replaceState(null, "", `${window.location.pathname}${s ? `?${s}` : ""}`);
  }, [by, d]);
  // the server and the first render draw the first FIRST rows; once mounted, the rows in view and PAD around them
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  const start = mounted ? Math.max(0, Math.floor(top / ROW) - PAD) : 0;
  const end = Math.min(sorted.length, mounted ? Math.floor(top / ROW) + VIEW + PAD : FIRST);
  const click = (k: NodeSort) => { if (k === by) setD(d === "asc" ? "desc" : "asc"); else { setBy(k); setD(k === "node" || k === "cls" ? "asc" : "desc"); } };
  const energyKey = (r: NodeTableRow) => (datacenter ? `allgrids|energy|${r.id}|da` : `allgrids|energy|${r.id}|da|${pkey}`);
  const cols = "grid grid-cols-[minmax(11rem,1.6fr)_6rem_6rem_7rem_6rem_6rem] items-center gap-x-3 px-3";
  return (
    <div data-allgrids-nodes="1">
      <p className="mb-2 text-sm" role="status" data-node-sort={`${by}|${d}`}>
        Sorted by {HEADS[by].toLowerCase()}, {d === "asc" ? "smallest first" : "largest first"}{by === "node" || by === "cls" ? " (alphabetical)" : ""}; a node with no figure last. Click a heading to sort by it, again to turn it round.
      </p>
      <div className="overflow-x-auto" role="region" aria-label="ERCOT nodes" tabIndex={0}>
        <div style={{ minWidth: 640 }}>
          <div className={`${cols} bg-accent py-1.5 text-sm text-white`} role="row">
            {NODE_SORTS.map((k) => (
              <button key={k} type="button" role="columnheader" aria-sort={by === k ? (d === "asc" ? "ascending" : "descending") : "none"} title={TIPS[k]}
                onClick={() => click(k)} className={`border-b border-dotted border-white/70 text-left ${k === "node" || k === "cls" ? "" : "text-right"}`} data-node-head={k}>
                <span className="text-white">{HEADS[k]}{by === k ? (d === "asc" ? " (up)" : " (down)") : ""}</span>
              </button>
            ))}
          </div>
          <div ref={box} className="relative overflow-y-auto border-b border-rule" style={{ height: Math.min(sorted.length, VIEW) * ROW }} onScroll={(e) => setTop(e.currentTarget.scrollTop)} data-node-list="1">
            <div style={{ height: sorted.length * ROW, position: "relative" }}>
              {sorted.slice(start, end).map((r, i) => (
                <div key={r.id} className={`${cols} absolute left-0 right-0 border-b border-rule text-sm tabular-nums`} style={{ top: (start + i) * ROW, height: ROW }} data-allgrids-row={r.id}>
                  <button type="button" onClick={() => pick(r.id)} aria-pressed={open === r.id} className={`truncate text-left underline decoration-dotted ${open === r.id ? "font-semibold" : ""}`} title={`${r.types ? `${r.node}: ERCOT's resource types ${r.types}. ` : ""}Open its panel`} data-node-open={r.id}>{r.node}</button>
                  <span className="text-xs">{r.cls}</span>
                  <span className="text-right">{r.per === null ? <span className="cursor-help border-b border-dotted border-muted" title={r.why}>not held</span> : <span data-check={energyKey(r)} data-raw={String(r.per)}>{two(r.per)}</span>}</span>
                  <span className="text-right">{r.basis === null ? "" : <span data-check={`allgrids|basis|${r.id}`} data-raw={String(r.basis)}>{two(r.basis)}</span>}</span>
                  <span className="text-right">{r.allin === null ? "" : <span data-check={`allgrids|allin|${r.id}|${pkey}`} data-raw={String(r.allin)}>{two(r.allin)}</span>}</span>
                  <span className="text-right text-xs">{r.days.toLocaleString("en-US")}{r.due ? ` of ${r.due}` : ""}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
