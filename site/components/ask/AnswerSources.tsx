// Energy Research Warehouse (ERW) site, session 1194: an answer's sources and reads, in the brand's source line
// (components/tool/ToolPage.tsx SourceLine: 12 px, grey, a rule above, "Source: ERW table ..."), drawn the same under
// every chat's answer: Ask ERCOT's and the grids' panel (components/ask/AskPanel.tsx) and the general chat's form
// (app/ask/AskForm.tsx), which until now drew them in two ways. Each source names its table with a link to it, its
// tier, its source report and, on hover, the data's version; each read is what one query read (sessions 1115, 1132).
import { SiteLink as Link } from "@/components/SiteLink";
import { TIER_LABEL, TIER_TITLE } from "@/lib/tiers";
import { PAGE_FILE_HREF } from "@/lib/chat/pagelinks";

export type AnswerCitation = { table: string; source_report: string; data_version: string; tier?: string };
export type AnswerRead = { table: string; entity?: string; variable?: string; start?: string; end?: string; aggregation?: string; group_by?: string; tz?: string };

/** Where a cited table is described: a grid's written page, a page's own file (session 153), or the catalogue's row.
 *  Moved here from AskPanel.tsx (session 1194), which imports it again. */
export function sourceHref(table: string): { href: string; what: string } {
  if (table.startsWith("docs/grids/")) return { href: `/grid?grid=${table.slice(11, -3)}`, what: "Written page" };
  if (table === "site/data/board.json") return { href: "/board", what: "Price board" };
  if (table === "site/data/supply.json") return { href: "/supply", what: "Supply and trade" };
  if (PAGE_FILE_HREF[table]) return PAGE_FILE_HREF[table];   // session 153: a page's own file, read by the tool page_file
  return { href: `/data#${table}`, what: "ERW table" };
}

/** One read, in words: the table, the entity and variable, the span (the end not included), the aggregation. */
export function readWords(r: AnswerRead): string {
  const span = r.start || r.end
    ? `, ${r.start ?? "the first row"} to ${r.end ?? "the newest row"}${r.end ? " (the end not included)" : ""}${r.tz && r.tz !== "UTC" ? `, ${r.tz} time` : ""}`
    : ", every row held";
  return `${span}${r.aggregation ? `, ${r.aggregation}${r.group_by ? ` by ${r.group_by}` : ""}` : ""}`;
}

export function AnswerSources({ citations, reads }: { citations: AnswerCitation[]; reads?: AnswerRead[] }) {
  const rs = reads ?? [];
  if (!citations.length && !rs.length) return null;
  return (
    <div className="mt-4 border-t border-rule pt-3 text-xs leading-relaxed text-muted" data-answer-sources="1">
      {citations.length ? (
        <ul data-sources={citations.length}>
          {citations.map((c) => {
            const src = sourceHref(c.table);
            return (
              <li key={c.table} className="py-0.5">
                Source: {src.what} <Link href={src.href} className="font-mono" gate="plain">{c.table}</Link>
                {c.tier === "model_extracted"
                  ? <> <span className="border border-rule px-1" title={TIER_TITLE.model_extracted}>{TIER_LABEL.model_extracted}</span></>
                  : c.tier ? ` (${c.tier})` : ""}
                {c.source_report ? <>, source report <span className="font-mono" title={c.data_version || undefined}>{c.source_report}</span></> : null}.
              </li>
            );
          })}
        </ul>
      ) : null}
      {rs.length ? (
        <ul className={citations.length ? "mt-1" : undefined} data-reads={rs.length}>
          {rs.map((r, i) => (
            <li key={i} className="py-0.5">
              Read: <span className="font-mono">{r.table}</span>{r.entity ? <>, <span className="font-mono">{r.entity}</span></> : null}{r.variable ? <>, <span className="font-mono">{r.variable}</span></> : null}
              {readWords(r)}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
