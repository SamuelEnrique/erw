import { SiteLink as Link } from "@/components/SiteLink";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { ChartFrame, SourceLine, ToolHeader, ToolSection } from "@/components/tool/ToolPage";
import duplicates from "@/data/deal_duplicates.json";
import { deals } from "@/lib/data";
import {
  DIMENSIONS, FEWER, MIN_DISCLOSED, NOT_STATED, comparables, compKey, fold, shown as shownOf, toDeal, whole,
  type Cell, type DealRow, type Pair,
} from "@/lib/deals2";
import { isLicenseReason } from "@/lib/license";
import { attempt } from "@/lib/supabase";
import { DealsHeld } from "../Held";

// Session 466: the comparables view of the deals tracker (/deals?view=comparables, in review, under the tracker's tab).
// The deals' disclosed figures side by side, one dimension at a time (?by=type, technology, grid or year; the type by
// default): the deals in each cell, those that state a price in US dollars per MWh and those that state a size in MW,
// and the median of each where at least three deals of the cell state it (lib/deals2.ts, comparables()). A cell with
// fewer says "fewer than three": nothing is computed from fewer than three disclosed deals. The chart shows, for the
// cells that have one, the price where any cell of the dimension has a median price, else the size. Every figure
// carries its key, deals|comp_<stat>|<dimension>|<value>, which scripts/check-values.mjs recomputes with the same
// functions. It reads energy_deals and nothing else; under the hold it shows the hold's words and nothing of a row.

const PAIRS = (duplicates as unknown as { pairs: Pair[] }).pairs;
const cell = "px-3 py-1.5 align-top";

function Bars({ cells, what }: { cells: Cell[]; what: "price" | "mw" }) {
  const rows = cells.filter((c) => (what === "price" ? c.medianPrice : c.medianMw) !== null);
  const W = 760, L = 210, R = 70, rowH = 26, top = 8, H = top + rows.length * rowH + 8;
  const hi = Math.max(1, ...rows.map((c) => (what === "price" ? c.medianPrice! : c.medianMw!)));
  const x = (v: number) => L + (v / hi) * (W - L - R);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img"
      aria-label={`The median ${what === "price" ? "price in US dollars per MWh" : "size in MW"} of each group with three or more deals that state it`}>
      {rows.map((c, i) => {
        const v = what === "price" ? c.medianPrice! : c.medianMw!;
        const y = top + i * rowH;
        return (
          <g key={c.value || "-"} data-comp-bar={c.value || "-"} data-comp-value={v}>
            <text x={L - 8} y={y + rowH / 2 + 4} textAnchor="end" fontSize="12" fill="var(--color-ink)">{c.label.length > 30 ? `${c.label.slice(0, 29)}.` : c.label}</text>
            <rect x={L} y={y + 4} width={Math.max(0.5, x(v) - L)} height={rowH - 8} fill="var(--color-accent)" />
            <text x={x(v) + 6} y={y + rowH / 2 + 4} fontSize="12" fill="var(--color-ink)">{whole(v)}{what === "price" ? "" : " MW"}</text>
            <title>{`${c.label}: median ${whole(v)} ${what === "price" ? "USD per MWh" : "MW"}, of ${what === "price" ? c.withPrice : c.withMw} deals that state it`}</title>
          </g>
        );
      })}
    </svg>
  );
}

function Figure({ v, k }: { v: number | null; k: string }) {
  return v === null ? <span className="text-muted">{FEWER}</span> : <Num check={k} raw={v}>{whole(v)}</Num>;
}

export async function ComparablesView({ sp }: { sp: Record<string, string | undefined> }) {
  const read = await attempt(deals);
  const by = DIMENSIONS.some((d) => d.id === sp.by) ? (sp.by as string) : "type";
  const dim = DIMENSIONS.find((d) => d.id === by)!;
  const all = read.ok ? fold((read.data as unknown as DealRow[]).map(toDeal), PAIRS) : [];
  const cells = comparables(all, by);
  const what: "price" | "mw" = cells.some((c) => c.medianPrice !== null) ? "price" : "mw";
  const charted = cells.filter((c) => (what === "price" ? c.medianPrice : c.medianMw) !== null).length;
  const withPrice = all.filter((d) => d.price !== null).length, withMw = all.filter((d) => d.mw !== null).length;

  return (
    <>
      <ToolHeader title="Deal comparables"
        crumb={<>Every deal, with its parties and sources: <Link href="/deals?tab=tracker" className="underline">Tracker</Link>. As a sortable table: <Link href="/deals" className="underline">Deals</Link></>}
        lead={<>What the deals the news reported disclose, side by side: how many state a price and a size, and the median of each, by deal type, technology, grid or year. <strong>Nothing is computed from fewer than {MIN_DISCLOSED} deals that state a figure</strong>; such a group says &quot;{FEWER}&quot;.</>} />

      <nav aria-label="Compare by" className="mb-6 flex flex-wrap items-baseline gap-x-4 gap-y-1 text-sm" data-comp-by={by}>
        <span className="font-semibold">Compare by</span>
        {DIMENSIONS.map((d) => (
          <Link key={d.id} href={d.id === "type" ? "/deals?view=comparables" : `/deals?view=comparables&by=${d.id}`} scroll={false}
            aria-current={d.id === by ? "true" : undefined} className={d.id === by ? "font-semibold no-underline" : "underline"}>
            {d.label}
          </Link>
        ))}
      </nav>

      {!read.ok && isLicenseReason(read.reason) ? (
        <>
          <p className="mb-3 text-sm"><NoData what="deals" reason={read.reason} /></p>
          <DealsHeld />
        </>
      ) : !read.ok ? (
        <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">The table could not be read, so no number is shown: {read.reason}</p>
      ) : !all.length ? (
        <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">No deal is held in the live set.</p>
      ) : (
        <>
          <p className="mb-8 max-w-3xl border-l-2 border-accent bg-paper px-4 py-3 text-sm" data-comp-stated="1">
            Of the {whole(all.length)} deals held, {whole(withPrice)} state a price in US dollars per MWh and {whole(withMw)} a size in MW.
            {what === "mw" ? <> No group of this view has {MIN_DISCLOSED} deals that state a price, so the chart shows the median size.</> : null}
          </p>

          <ChartFrame title={`The median ${what === "price" ? "price, USD per MWh" : "size, MW"}, by ${dim.label.toLowerCase()}`}
            note={<>Only the groups in which {MIN_DISCLOSED} or more deals state the figure ({whole(charted)} of {whole(cells.length)}); the others are in the table below. A median is of the figures the stories state; a deal that states none is left out, not counted as zero.</>}>
            {charted ? <Bars cells={cells} what={what} /> : <p className="text-sm text-muted" role="status">No group has {MIN_DISCLOSED} deals that state a {what === "price" ? "price" : "size"}.</p>}
          </ChartFrame>

          <ToolSection title={`By ${dim.label.toLowerCase()}`} id="comparables"
            note={<>{by === "grid" ? <>The grid is read from the state a story names, for the states one grid operator mostly serves; </> : null}A group &quot;{NOT_STATED}&quot; holds the deals whose stories do not state it. The deals of the register&apos;s folded pairs are counted once.</>}>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-left text-sm" style={{ minWidth: 720 }} data-comp-table={by}>
                <caption className="sr-only">The deals&apos; disclosed figures by {dim.label.toLowerCase()}</caption>
                <thead>
                  <tr className="bg-accent text-white">
                    {[dim.label, "Deals", "State a price", "Median price, USD/MWh", "State a size", "Median size, MW"].map((h) => <th key={h} scope="col" className="px-3 py-1.5 font-normal">{h}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {cells.map((c) => (
                    <tr key={c.value || "-"} className="border-b border-rule" data-comp-cell={c.value || "-"} data-comp-shows={shownOf(c).what}>
                      <th scope="row" className={`${cell} font-normal`}>{c.label}</th>
                      <td className={`${cell} tabular-nums`}><Num check={compKey("deals", by, c.value)} raw={c.deals}>{whole(c.deals)}</Num></td>
                      <td className={`${cell} tabular-nums`}><Num check={compKey("with_price", by, c.value)} raw={c.withPrice}>{whole(c.withPrice)}</Num></td>
                      <td className={`${cell} tabular-nums`}><Figure v={c.medianPrice} k={compKey("median_price", by, c.value)} /></td>
                      <td className={`${cell} tabular-nums`}><Num check={compKey("with_mw", by, c.value)} raw={c.withMw}>{whole(c.withMw)}</Num></td>
                      <td className={`${cell} tabular-nums`}><Figure v={c.medianMw} k={compKey("median_mw", by, c.value)} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ToolSection>
        </>
      )}
      <SourceLine tables={["energy_deals"]} note={<>The deals as <code className="font-mono">warehouse/deals/extract.py</code> extracted them from <code className="font-mono">news_stories</code>, with <code className="font-mono">warehouse/deals/duplicates.csv</code>&apos;s pairs shown once. <Link href="/data/methods/energy_deals">Method</Link>. This view is in review.</>} />
    </>
  );
}
