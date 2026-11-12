// Energy Research Warehouse (ERW) site, session 3306 (chain 200): capital flows (platform tool 11), its first view.
// The deal tracker's project finance, M&A, debt and equity raise rows (energy_deals) with the kind of the counterparty
// that brings the money (the company database: company_links, company_directory), from site/data/capital.json
// (warehouse/derived/capital_page.py). While energy_deals is held for a license the file holds the hold and the table's
// row count only, and the page says so: nothing of a held row is shown (the deals page's rule). The choice on the left,
// the figures on the right; what a figure means is a hover tip; thin where the rows are thin, and said so.
import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";
import { ChartFrame, InputPanel, SourceLine, Tip, ToolHeader, ToolPage, ToolSection } from "@/components/tool/ToolPage";
import { GroupedBars } from "@/components/tool/GroupedBars";
import { count } from "@/lib/format";
import { bn, named, quarterBars, toneOf, type Cell, type Quarter } from "@/lib/capitalview";
import file from "@/data/capital.json";

export const metadata: Metadata = { title: "Capital flows", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

type Deal = { event_id: string; date: string; quarter: string; type: string; buyer: string; seller: string; asset: string; technology: string; usd: number; mw: number | null; sources: string[]; buyer_kinds: string[] };
type Capital = {
  built: string; table: string; n_rows: number; method: string; held: boolean;
  types?: string[]; type_words?: Record<string, string>; quarters?: Quarter[];
  segments?: ({ segment: string } & Cell)[]; kinds?: ({ kind: string } & Cell)[]; total?: Cell; disclosed_share?: number | null; largest?: Deal[];
};
const CAP = file as unknown as Capital;

function K({ k, raw, children }: { k: string; raw: number; children: React.ReactNode }) {
  return <span data-n={`capital|${k}`} data-raw={String(raw)} title={`energy_deals (the deal tracker), summed by warehouse/derived/capital_page.py on ${CAP.built.slice(0, 10)}`}>{children}</span>;
}

function CellRow({ id, label, c }: { id: string; label: string; c: Cell }) {
  return (
    <tr className="border-b border-rule">
      <th scope="row" className="px-3 py-1.5 font-normal">{label}</th>
      <td className="px-3 py-1.5 text-right"><K k={`${id}|rows`} raw={c.rows}>{count(c.rows)}</K></td>
      <td className="px-3 py-1.5 text-right"><K k={`${id}|usd`} raw={c.usd}>{bn(c.usd)}</K></td>
      <td className="px-3 py-1.5 text-right"><K k={`${id}|no_usd`} raw={c.no_usd}>{count(c.no_usd)}</K></td>
      <td className="px-3 py-1.5 text-right"><K k={`${id}|mw`} raw={c.mw}>{Math.round(c.mw).toLocaleString("en-US")}</K></td>
    </tr>
  );
}

function CellTable({ caption, first, rows }: { caption: string; first: string; rows: { id: string; label: string; c: Cell }[] }) {
  return (
    <div className="overflow-x-auto" role="region" aria-label={caption} tabIndex={0}>
      <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: 520 }}>
        <caption className="sr-only">{caption}</caption>
        <thead><tr>
          <th scope="col" className="px-3 py-1.5 font-normal">{first}</th>
          <th scope="col" className="px-3 py-1.5 text-right font-normal">Deals</th>
          <th scope="col" className="px-3 py-1.5 text-right font-normal">USD billion disclosed</th>
          <th scope="col" className="px-3 py-1.5 text-right font-normal">Deals with no USD</th>
          <th scope="col" className="px-3 py-1.5 text-right font-normal">MW stated</th>
        </tr></thead>
        <tbody>{rows.map((r) => <CellRow key={r.id} id={r.id} label={r.label} c={r.c} />)}</tbody>
      </table>
    </div>
  );
}

export default async function Capital({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const want = typeof sp.type === "string" ? sp.type : "";
  const head = <ToolHeader title="Capital flows" lead={<>Project finance, acquisitions, debt and equity raises in the deal tracker, by quarter, segment and the kind of company that brings the money.<Tip id="capital-what" label="What this view is">The capital rows of energy_deals (deal types project_finance, m_and_a, debt and equity_raise), each deal&apos;s buyer (the acquirer, the lender or the investor) given its kind by the company database. USD is summed only where a story states it; a deal without one is counted apart, never estimated.</Tip></>} />;
  if (CAP.held || !CAP.total || !CAP.types) {
    return (
      <Brand>
      <ToolPage>
        {head}
        <p className="mb-6 max-w-3xl border-l-2 border-accent bg-paper px-4 py-3 text-sm" data-capital-held="1">
          <strong>The hold covers every row this view is built from.</strong> All <span data-n="capital|n_rows" data-raw={CAP.n_rows} title="energy_deals, its row count">{count(CAP.n_rows)}</span> rows
          of <code className="font-mono">energy_deals</code> are held for a license: each deal was extracted from news stories, and the outlets&apos; own pages ask for
          permission, which is not yet recorded. No figure of them is drawn here until it is.
          <Tip id="capital-held" label="When the view opens">When a permission is recorded (warehouse/metadata/license_status.csv), the next build of the view&apos;s file draws USD and MW by quarter and type, by segment and by the kind of counterparty, the share of deals that disclose USD, and the twenty largest with their sources.</Tip>
        </p>
        <SourceLine tables={["energy_deals", "company_links", "company_directory"]} note={<>Built {CAP.built.slice(0, 10)}; the method is <Link href="/data/methods/companies">docs/methods/companies.md</Link>; the deals&apos; own on <Link href="/data/methods/energy_deals">its note</Link>.</>} />
      </ToolPage>
      </Brand>
    );
  }
  const types = CAP.types;
  const words = CAP.type_words ?? {};
  const pick = types.includes(want) ? want : "";
  const shown = pick ? [pick] : types;
  const total = CAP.total;
  const largest = (CAP.largest ?? []).filter((d) => !pick || d.type === pick);
  const quarters = CAP.quarters ?? [];
  return (
    <Brand>
    <ToolPage>
      {head}
      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <aside className="min-w-0">
          <InputPanel title="Choose" reset={{ href: "/deals/capital", defaults: "every kind of capital deal." }}>
            <nav aria-label="Deal type" className="text-sm">
              <div><Link href="/deals/capital" aria-current={!pick ? "true" : undefined}>Every type</Link></div>
              {types.map((t) => <div key={t}><Link href={`/deals/capital?type=${t}`} aria-current={t === pick ? "true" : undefined}>{words[t] ?? t}</Link></div>)}
            </nav>
          </InputPanel>
        </aside>
        <div className="min-w-0">
          <p className="mb-6 text-sm" data-capital-total="1">
            <K k="total|rows" raw={total.rows}>{count(total.rows)}</K> capital deals; <K k="total|usd_rows" raw={total.usd_rows}>{count(total.usd_rows)}</K> state a USD amount
            ({CAP.disclosed_share !== null && CAP.disclosed_share !== undefined ? `${(CAP.disclosed_share * 100).toFixed(1)}%` : "none"});
            {" "}<K k="total|no_usd" raw={total.no_usd}>{count(total.no_usd)}</K> do not.
            <Tip id="capital-thin" label="How thin">A quarter with few deals in the tracker reads thin, and one large deal (an acquisition) can be most of a quarter: the counts are in each bar&apos;s hover.</Tip>
          </p>
          <ChartFrame title="USD disclosed by quarter" tip={<Tip id="capital-q" label="The quarters">USD billion stated by the stories, by the quarter of the deal&apos;s date and its type; deals with no USD are not in the bars and are counted in the hover.</Tip>}>
            <GroupedBars id="capital-quarters" unit="USD billion" label="USD disclosed by quarter and type"
              series={shown.map((t) => ({ name: words[t] ?? t, tone: toneOf(types.indexOf(t)) }))}
              groups={quarters.map((q) => ({ label: q.quarter, ...quarterBars(q, shown, words) }))}
              fmt={(v) => bn(v * 1e9)} />
          </ChartFrame>
          <ToolSection title="By segment">
            <CellTable caption="Capital deals by segment" first="Segment" rows={(CAP.segments ?? []).map((s) => ({ id: `segment|${s.segment}`, label: s.segment, c: s }))} />
          </ToolSection>
          <ToolSection title="By the kind of company that brings the money">
            <CellTable caption="Capital deals by the kind of their buyer" first="Kind" rows={(CAP.kinds ?? []).map((s) => ({ id: `kind|${s.kind}`, label: s.kind, c: s }))} />
          </ToolSection>
          <ToolSection title={`The ${largest.length} largest by USD`}>
            <div className="overflow-x-auto" role="region" aria-label="The largest deals" tabIndex={0}>
              <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: 760 }}>
                <caption className="sr-only">The largest capital deals by USD stated</caption>
                <thead><tr>
                  <th scope="col" className="px-3 py-1.5 font-normal">Date</th><th scope="col" className="px-3 py-1.5 font-normal">Type</th>
                  <th scope="col" className="px-3 py-1.5 font-normal">Buyer</th><th scope="col" className="px-3 py-1.5 font-normal">Seller</th>
                  <th scope="col" className="px-3 py-1.5 text-right font-normal">USD billion</th><th scope="col" className="px-3 py-1.5 font-normal">Sources</th>
                </tr></thead>
                <tbody>
                  {largest.map((d) => (
                    <tr key={d.event_id} className="border-b border-rule">
                      <th scope="row" className="px-3 py-1.5 font-normal">{d.date}</th>
                      <td className="px-3 py-1.5">{words[d.type] ?? d.type}</td>
                      <td className="px-3 py-1.5">{named(d.buyer)} <span className="text-xs text-muted">{d.buyer_kinds.join(", ")}</span></td>
                      <td className="px-3 py-1.5">{named(d.seller)}</td>
                      <td className="px-3 py-1.5 text-right"><K k={`deal|${d.event_id}|usd`} raw={d.usd}>{bn(d.usd)}</K></td>
                      <td className="px-3 py-1.5 text-xs">{d.sources.map((u, i) => <a key={u} href={u} className="mr-2" rel="noopener">{`story ${i + 1}`}</a>)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ToolSection>
          <SourceLine tables={["energy_deals", "company_links", "company_directory"]} note={<>Built {CAP.built.slice(0, 10)}; the method is <Link href="/data/methods/companies">docs/methods/companies.md</Link>.</>} />
        </div>
      </div>
    </ToolPage>
    </Brand>
  );
}
