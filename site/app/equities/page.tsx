import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { ToolPage } from "@/components/tool/ToolPage";
import { EquitiesView, tablesOf } from "./view";

// Session 10402 (chain 720, part D): "Energy equities", a new page: the analyzer of the price board's energy equities
// group. Every listed energy company by segment in one table that sorts and filters; a company, an index or a segment
// as a line over any window, with an energy price laid over it; a segment's two weightings named plainly; a company's
// filed revenue, income, capital spending, debt and shares by period, each with its filing's address; two side by
// side. Reads site/data/equities/*.json (the data machine's warehouse/derived/equity_pages.py; contract
// docs/state/page_files_equities.md; method docs/methods/equities.md) when a request names a series. What was
// published, and nothing else: no score, no signal, no view. In review (no line in lib/release.ts), in no menu.
export const metadata: Metadata = { title: "Energy equities", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

type Query = Record<string, string | string[] | undefined>;

export default async function EquitiesPage({ searchParams }: { searchParams: Promise<Query> }) {
  const q = await searchParams;
  const tables = tablesOf();
  return (
    <Brand>
      <ToolPage>
        <EquitiesView query={q} />
        {tables.length ? <TableDownloads tables={tables} /> : null}
      </ToolPage>
    </Brand>
  );
}
