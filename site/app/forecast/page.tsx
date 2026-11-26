import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { ToolPage } from "@/components/tool/ToolPage";
import { ForecastView, tablesOf } from "./view";

// Session 10401 (chain 720, part C): "ERW forecast", a new page. The ERW's own day-ahead forecast of demand and price
// for a place, with its band and the operator's own forecast beside it; any past day beside what happened; and the
// report card of the ERW, the operator, the same hour yesterday and the same hour a week ago, by month, by hour of day
// and for all places at once. Two places side by side. Reads site/data/predict/*.json (the data machine's forecast
// build, warehouse/predict/; contract docs/state/page_files_predict.md; methods docs/methods/predict.md and
// predict_price.md) when a request names a place, so the files land with no change of code. The word "forecast" in the
// code is the Economic impact tool's: nothing of /impact is imported here. In review (no line in lib/release.ts), in no
// menu.
export const metadata: Metadata = { title: "ERW forecast", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

type Query = Record<string, string | string[] | undefined>;

export default async function ForecastPage({ searchParams }: { searchParams: Promise<Query> }) {
  const q = await searchParams;
  const tables = tablesOf(q);
  return (
    <Brand>
      <ToolPage>
        <ForecastView query={q} />
        {tables.length ? <TableDownloads tables={tables} /> : null}
      </ToolPage>
    </Brand>
  );
}
