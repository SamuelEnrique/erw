"use client";
// Session 2239 (chain 156): a reader's own deal placed against the disclosed prices, in one line. Nothing typed here
// is stored or sent: no request, no storage (the battery tool's rule for contract terms typed without an NDA). The
// line says where the price falls among the prices the stories state; it says nothing of whether the price is good.
import { useMemo, useState } from "react";
import { MIN_DISCLOSED, place, type Deal } from "@/lib/deals2";

const whole = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });

export function PlaceDeal({ deals, technologies, grids }: { deals: Deal[]; technologies: string[]; grids: string[] }) {
  const [tech, setTech] = useState("");
  const [grid, setGrid] = useState("");
  const [mw, setMw] = useState("");
  const [price, setPrice] = useState("");
  const p = Number(price);
  const line = useMemo(() => (price !== "" && Number.isFinite(p) && p >= 0 ? place(deals, { technology: tech, grid, price: p }) : null), [deals, tech, grid, price, p]);
  const box = "w-full min-w-0 border border-rule bg-panel px-2 py-1 text-sm text-ink";
  return (
    <div className="grid gap-4 lg:grid-cols-[15rem_minmax(0,1fr)]" data-place-deal="1">
      <form className="flex flex-col gap-2" aria-label="Your deal" onSubmit={(e) => e.preventDefault()} autoComplete="off">
        <label className="flex flex-col gap-1 text-xs text-muted" title="The technology as the stories state it">
          Technology
          <select value={tech} onChange={(e) => setTech(e.target.value)} className={box}>
            <option value="">Any</option>
            {technologies.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs text-muted" title="The grid operator">
          Grid
          <select value={grid} onChange={(e) => setGrid(e.target.value)} className={box}>
            <option value="">Any</option>
            {grids.map((g) => <option key={g} value={g}>{g}</option>)}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs text-muted" title="Shown beside the line; it narrows nothing">
          MW
          <input type="number" min="0" value={mw} onChange={(e) => setMw(e.target.value)} className={box} />
        </label>
        <label className="flex flex-col gap-1 text-xs text-muted" title="USD per MWh; never stored or sent">
          Price, USD per MWh
          <input type="number" min="0" step="0.01" value={price} onChange={(e) => setPrice(e.target.value)} className={box} />
        </label>
      </form>
      <p className="self-start border-l-2 border-accent bg-paper px-4 py-3 text-sm" role="status" aria-live="polite" data-place-line={line ? `${line.below}/${line.equal}/${line.above}` : ""}>
        {line === null ? (
          <span className="text-muted">Type a price to place it among the prices the stories state.</span>
        ) : line.count < MIN_DISCLOSED ? (
          <>Fewer than {MIN_DISCLOSED} PPAs or offtakes state a price ({line.count} in {line.scope}): there is nothing to place USD {whole(p)} per MWh against.</>
        ) : (
          <>
            USD {whole(p)} per MWh{mw ? ` (${whole(Number(mw))} MW)` : ""}: {line.below} of the {line.count} disclosed prices of {line.scope} are below it,{" "}
            {line.equal} equal and {line.above} above; their median is USD {whole(line.median!)}.
          </>
        )}
      </p>
    </div>
  );
}
