import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { cookies } from "next/headers";
import { notFound } from "next/navigation";
import gapsJson from "@/data/siting/gaps.json";
import { REPO } from "@/lib/holds";
import { COOKIE } from "@/lib/release";
import { internalOk } from "@/lib/thesis/server";

// Session 713 (chain 050): the cells the All grids tab of /cost-of-power cannot fill. docs/reviews/siting-gaps.md holds
// one row a kind of cell, by grid, with the source that would fill it, its license as recorded and the connector it
// resembles; warehouse/derived/siting_page.py writes its table to site/data/siting/gaps.json, which this page imports, so
// it is read when the site is built. Words only: no figure. Internal, as /internal/holds is: no nav link, not indexed,
// never cached, and a 404 unless the browser holds the internal cookie. It takes no token in its address, reads no
// database and writes nothing.
export const dynamic = "force-dynamic";

type GapsFile = { source: string; columns: string[]; rows: Record<string, string>[] };
const GAPS = gapsJson as unknown as GapsFile;

export async function generateMetadata(): Promise<Metadata> {
  const inside = (process.env.INTERNAL_COSTS_TOKEN ?? "").length >= 24 && (await internalOk((await cookies()).get(COOKIE)?.value));
  return { ...(inside ? { title: "All grids: the cells not held (internal)" } : {}), robots: { index: false, follow: false } };
}

/** A cell as written, its `code` spans drawn as code. */
function Cell({ text }: { text: string }) {
  const parts = text.split("`");
  return <>{parts.map((p, i) => (i % 2 ? <span key={i} className="font-mono text-xs">{p}</span> : <span key={i}>{p}</span>))}</>;
}

export default async function SitingGapsPage() {
  const want = process.env.INTERNAL_COSTS_TOKEN ?? "";
  if (want.length < 24 || !(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();
  const grids = [...new Set(GAPS.rows.map((r) => r.Grid))];
  return (
    <Brand noUsage>
    <div className="max-w-6xl" data-siting-gaps={String(GAPS.rows.length)} data-no-usage>
      <h1 className="mb-1 text-3xl">All grids: the cells not held (internal)</h1>
      <p className="mb-4 max-w-3xl text-sm">
        Every kind of cell of <a className="underline" href="/cost-of-power?view=allgrids">the All grids tab</a> the warehouse cannot fill, by grid, with the source that would
        fill it, its license as the source registry and the licenses document record it (no web request was made to read them), and the connector it resembles.
        From <a className="underline" href={`${REPO}/blob/main/${GAPS.source}`} rel="noreferrer"><span className="font-mono">{GAPS.source}</span></a>, read when the site was built:
        {" "}{GAPS.rows.length} rows over {grids.length} grid groups.
      </p>
      <div className="overflow-x-auto" role="region" aria-label="The cells not held" tabIndex={0}>
        <table className="w-full text-sm" style={{ minWidth: 960 }}>
          <caption className="sr-only">The cells of the All grids tab the warehouse cannot fill, with the source that would fill each</caption>
          <thead>
            <tr className="border-b border-ink text-left text-xs">
              {GAPS.columns.map((c) => <th key={c} scope="col" className="py-1 pr-3 font-normal">{c}</th>)}
            </tr>
          </thead>
          <tbody>
            {GAPS.rows.map((r, i) => (
              <tr key={i} className="border-b border-rule align-top" data-gap-row={i}>
                {GAPS.columns.map((c, j) => j === 0
                  ? <th key={c} scope="row" className="py-2 pr-3 text-left font-normal"><Cell text={r[c] ?? ""} /></th>
                  : <td key={c} className="py-2 pr-3"><Cell text={r[c] ?? ""} /></td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
    </Brand>
  );
}
