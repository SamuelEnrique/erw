import { SiteLink as Link } from "@/components/SiteLink";
import { NoData } from "@/components/NoData";
import { Num } from "@/components/Num";
import { SourceLine, ToolHeader, ToolSection } from "@/components/tool/ToolPage";
import { HeldRows } from "@/components/tool/HeldRows";
import duplicates from "@/data/deal_duplicates.json";
import { deals } from "@/lib/data";
import { fold, toDeal, whole, type Deal, type DealRow, type Pair } from "@/lib/deals2";
import { AI_DIMENSIONS, SUPPLY_LABEL, aiCells, aiKey, largest, supplyOf } from "@/lib/dealsai";
import { isLicenseReason } from "@/lib/license";
import { attempt } from "@/lib/supabase";
import { DealsHeld } from "../Held";

// Session 2240 (chain 156): the AI-power view of the deals (/deals?view=ai, in review, under the tracker's tab). The
// deals the AI-power rule tags, by buyer, by the kind of supply, by grid or by quarter (?aby=; the buyer by default):
// the deals of each group, and the MW and US dollars summed where stated, with the count that state each beside the
// sum; then the ten with the most MW and the ten with the most US dollars, each with its sources. Every figure carries
// its key, deals|ai_<stat>|<dimension>|<value>, which scripts/check-values.mjs recomputes with the same functions
// (lib/dealsai.ts). Under the hold it shows the hold's words and nothing of a row.

const PAIRS = (duplicates as unknown as { pairs: Pair[] }).pairs;
const cell = "px-3 py-1.5 align-top";
const usdWords = (v: number) => (v >= 1e9 ? `${whole(v / 1e9)} billion` : v >= 1e6 ? `${whole(v / 1e6)} million` : whole(v));

function Sum({ v, n, of, k, kn, unit }: { v: number | null; n: number; of: number; k: string; kn: string; unit: "MW" | "USD" }) {
  return (
    <>
      {v === null ? <span className="text-muted">none stated</span> : (
        <Num check={k} raw={v}>{unit === "USD" ? usdWords(v) : whole(v)}</Num>
      )}{" "}
      <span className="text-xs text-muted">(<Num check={kn} raw={n}>{whole(n)}</Num> of {whole(of)} state it)</span>
    </>
  );
}

function Largest({ rows, by }: { rows: Deal[]; by: "mw" | "usd" }) {
  if (!rows.length) return <p className="text-sm text-muted" role="status">No AI-tagged deal states {by === "mw" ? "MW" : "a sum in US dollars"}.</p>;
  return (
    <ol className="list-decimal space-y-1 pl-6 text-sm" data-ai-largest={by}>
      {rows.map((d) => (
        <li key={d.id} data-ai-deal={d.id}>
          <span className="tabular-nums">
            {by === "mw" ? <Num check={`event|energy_deals|${d.id}|mw`} raw={d.mw!}>{whole(d.mw!)}</Num> : <Num check={`event|energy_deals|${d.id}|dollars`} raw={d.dollars!}>{usdWords(d.dollars!)}</Num>}
            {by === "mw" ? " MW" : " USD"}
          </span>
          {": "}
          {[d.buyerName || d.buyer, d.sellerName || d.seller].filter(Boolean).join(" / ") || "parties not stated"}
          {d.asset ? `, ${d.asset}` : ""} <span className="text-muted">({d.date}; {SUPPLY_LABEL[supplyOf(d)]})</span>{" "}
          <span className="text-xs" title={d.aiBasis ? `Tagged AI by: ${d.aiBasis}` : "Tagged AI by the extraction (before session 2232)"}>
            {d.links.map((u, i) => (
              <span key={u}>{i ? ", " : ""}<a href={u} rel="noopener noreferrer" target="_blank">{i === 0 ? d.source : `story ${i + 1}`}</a></span>
            ))}
          </span>
        </li>
      ))}
    </ol>
  );
}

export async function AiView({ sp }: { sp: Record<string, string | undefined> }) {
  const read = await attempt(deals);
  const by = AI_DIMENSIONS.some((d) => d.id === sp.aby) ? (sp.aby as string) : "buyer";
  const dim = AI_DIMENSIONS.find((d) => d.id === by)!;
  const all = read.ok ? fold((read.data as unknown as DealRow[]).map(toDeal), PAIRS) : [];
  const ai = all.filter((d) => d.ai);
  const cells = aiCells(all, by);
  return (
    <>
      <ToolHeader title="Deals for AI power"
        crumb={<>Every deal: <Link href="/deals?tab=tracker" className="underline">Tracker</Link>. Side by side: <Link href="/deals?view=comparables" className="underline">Comparables</Link></>}
        lead={<>The deals the AI-power rule tags: a named AI lab, hyperscaler, datacenter operator or AI-load buyer is a party, or the load the deal serves is a datacenter. A sum is of the figures the stories state; the deals that state none are counted beside it, never added as zero.</>} />
      <nav aria-label="Group by" className="mb-6 flex flex-wrap items-baseline gap-x-4 gap-y-1 text-sm" data-ai-by={by}>
        <span className="font-semibold">Group by</span>
        {AI_DIMENSIONS.map((d) => (
          <Link key={d.id} href={d.id === "buyer" ? "/deals?view=ai" : `/deals?view=ai&aby=${d.id}`} scroll={false}
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
      ) : !ai.length ? (
        <p className="mb-6 border border-rule bg-paper px-3 py-2 text-sm" role="status">No deal held is tagged AI power.</p>
      ) : (
        <>
          <HeldRows shape="events" table="energy_deals" shown={all.length} method="/data/methods/energy_deals" />
          <p className="mb-6 max-w-3xl text-sm" data-ai-share="1">
            {whole(ai.length)} of the {whole(all.length)} deals held are tagged AI power (the register&apos;s folded pairs counted once).
          </p>
          <ToolSection title={`By ${dim.label.toLowerCase()}`} id="ai-groups"
            note={<>{by === "grid" ? <>A grid named in a story, else the grid that serves most of the state the story names; </> : null}{by === "supply" ? <>The kind of supply is read from the deal&apos;s kind and its stated technology; </> : null}{by === "buyer" ? <>The buyer as one name a company; for a raise or a loan with no buyer named, the party named first; </> : null}&quot;not stated&quot; holds the deals whose stories state none.</>}>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-left text-sm" data-ai-table={by}>
                <caption className="sr-only">The AI-power deals by {dim.label.toLowerCase()}</caption>
                <thead>
                  <tr className="bg-accent text-white">
                    {[dim.label, "Deals", "MW stated", "US dollars stated"].map((h) => <th key={h} scope="col" className="px-3 py-1.5 font-normal">{h}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {cells.map((c) => (
                    <tr key={c.value || "-"} className="border-b border-rule" data-ai-cell={c.value || "-"}>
                      <th scope="row" className={`${cell} font-normal`}>{c.label}</th>
                      <td className={`${cell} tabular-nums`}><Num check={aiKey("deals", by, c.value)} raw={c.deals}>{whole(c.deals)}</Num></td>
                      <td className={`${cell} tabular-nums`}><Sum v={c.mw} n={c.withMw} of={c.deals} k={aiKey("mw", by, c.value)} kn={aiKey("with_mw", by, c.value)} unit="MW" /></td>
                      <td className={`${cell} tabular-nums`}><Sum v={c.usd} n={c.withUsd} of={c.deals} k={aiKey("usd", by, c.value)} kn={aiKey("with_usd", by, c.value)} unit="USD" /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ToolSection>
          <div className="grid gap-6 lg:grid-cols-2">
            <ToolSection title="The ten with the most MW stated" id="ai-largest-mw" note={<>Hover a deal&apos;s sources for what tagged it AI.</>}>
              <Largest rows={largest(all, "mw")} by="mw" />
            </ToolSection>
            <ToolSection title="The ten with the most US dollars stated" id="ai-largest-usd" note={<>A sum as stated in US dollars; a valuation or a company-wide investment is not a deal&apos;s.</>}>
              <Largest rows={largest(all, "usd")} by="usd" />
            </ToolSection>
          </div>
        </>
      )}
      <SourceLine tables={["energy_deals"]} note={<>The deals as <code className="font-mono">warehouse/deals/extract.py</code> extracted them, with <code className="font-mono">warehouse/deals/duplicates.csv</code>&apos;s pairs shown once. <Link href="/data/methods/energy_deals">Method</Link>. This view is in review.</>} />
    </>
  );
}
