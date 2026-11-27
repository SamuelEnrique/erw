// Session 10402 (chain 720, part D): what /equities' download routes share: the series an address names, and what the
// Python and Stata readers need to know of each CSV's columns (lib/csvreader.ts).
import type { ReaderSpec } from "@/lib/csvreader";
import { LIST_FILED_FIGURES, LIST_HEAD, picksOf, type EqSeries } from "@/lib/equities";
import { equitiesList, equitiesSeries } from "@/lib/equitiesfiles";

const plain = { "Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex" };
export const notHere = (words: string) => new Response(`${words}\n`, { status: 404, headers: plain });

/** The series an address's `id` names, read through the list (so only a series the list offers is ever read). */
export function seriesOf(req: Request): EqSeries | null {
  const id = new URL(req.url).searchParams.get("id");
  const pick = picksOf(equitiesList()).find((p) => p.id === id);
  return pick ? equitiesSeries(pick.file) : null;
}

/** The daily rows' reader: the file's own columns, every one but the day a figure. */
export function rowsSpec(s: EqSeries): ReaderSpec {
  const figures = s.daily_columns.filter((c) => c !== "day");
  return { what: `${s.kind === "company" ? s.ticker ?? s.id : s.name ?? s.id}, day by day, as /equities draws it`, by: "site/lib/equities.ts seriesCsv", text: ["day"], figures, show: s.daily_columns.slice(0, 6), name: "series" };
}
/** The filed periods' reader. */
export function filedSpec(s: EqSeries): ReaderSpec {
  const cols = s.quarterly_columns ?? [];
  const figures = ["months", "revenue", "net_income", "capex", "debt", "shares_outstanding"].filter((c) => cols.includes(c));
  return { what: `the figures ${s.ticker ?? s.id} filed, period by period, as /equities draws them`, by: "site/lib/equities.ts filedCsv", text: cols.filter((c) => !figures.includes(c)), figures,
    show: ["period_end", "months", "form", "filed", "revenue", "net_income"].filter((c) => cols.includes(c)), count: cols.includes("form") ? "form" : undefined, name: "filed" };
}
export const LIST_SPEC: ReaderSpec = {
  what: "the listed energy companies by segment, as /equities lists them", by: "site/lib/equities.ts listCsv",
  // session 10414: the newest filed period's sums, months, debt and shares are figures; every other column is text
  text: LIST_HEAD.filter((c) => !LIST_FILED_FIGURES.includes(c)), figures: LIST_FILED_FIGURES,
  show: ["ticker", "name", "exchange", "segments", "price_status", "fundamentals_status"], count: "price_status", name: "companies",
};

export const attach = (name: string, type = "text/plain") => ({ "Content-Type": `${type}; charset=utf-8`, "Content-Disposition": `attachment; filename="${name}"`, "X-Robots-Tag": "noindex" });
