// Energy Research Warehouse (ERW) site, session 403: the frame every signature explorer shares (/explore/<name>,
// platform tool 5; lib/explore). One explorer is one page: the title, the figure's definition in one line, how old
// its tables are (read from the catalogue, never written by hand), the filters as a plain GET form (its state is the
// address, so every figure is drawn on the server and carries a check key), the charts (the site's shared charts
// only), the method note, the downloads line and the source line. Sessions 404 and 405 build the next two on it.
import type { ReactNode } from "react";
import { AutoSubmitSelect } from "@/components/AutoSubmit";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";
import { TableDownloads } from "@/components/tool/TableDownloads";
import { InputPanel, SourceLine, ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import { longDay, periodOf, type Option } from "@/lib/explore";
import { freshness } from "@/lib/explore/fresh";

/** The explorer's frame, in the brand (components/Brand.tsx). `definition` is the figure's definition in one line; `method` the method note's address. */
export function ExploreFrame({ id, title, definition, fresh, filters, method, tables, sourceNote, children }: {
  id: string; title: string; definition: ReactNode; fresh: ReactNode; filters?: ReactNode;
  method: { href: string; label: string }; tables: string[]; sourceNote?: ReactNode; children: ReactNode;
}) {
  return (
    <Brand>
      <ToolPage>
        <div data-explore={id}>
          <ToolHeader crumb="Explorer" title={title} lead={<span data-definition="1">{definition}</span>} />
          {fresh}
          {filters}
          {children}
          <p className="mt-8 text-sm" data-method-link="1">
            Method: <Link href={method.href}>{method.label}</Link>, every figure on this page step by step.
          </p>
          <TableDownloads tables={tables} />
          <SourceLine tables={tables} note={sourceNote} />
        </div>
      </ToolPage>
    </Brand>
  );
}

/** How old the explorer's tables are: each table's last computation and the newest period it holds, from the
 *  catalogue. A table not computed for more than `staleAfterDays` days is said to be stale, with its date, in the
 *  first words of the line. `detail` is the page's own line under it (the last interval a table used, say). */
export async function Freshness({ tables, staleAfterDays = 3, detail }: { tables: string[]; staleAfterDays?: number; detail?: ReactNode }) {
  const f = await freshness(tables);
  if (!f.ok) {
    return <p className="mb-6 text-sm text-muted" data-fresh="unread">How old these tables are could not be read: the catalogue did not answer.</p>;
  }
  const stale = f.rows.filter((r) => r.days !== null && r.days > staleAfterDays);
  return (
    <div className={`mb-6 border-l-2 px-3 py-2 text-sm ${stale.length ? "border-accent bg-paper" : "border-rule"}`} data-fresh={stale.length ? "stale" : "fresh"}>
      {f.rows.map((r) => (
        <p key={r.table} data-fresh-table={r.table} data-last-run={r.lastRun ?? ""} data-ts-max={r.tsMax ?? ""}>
          {r.lastRun === null ? (
            <><code className="font-mono">{r.table}</code>: not in the site&apos;s catalogue.</>
          ) : (
            <>
              {r.days !== null && r.days > staleAfterDays ? <strong>Stale since {longDay(r.lastRun)}. </strong> : null}
              <code className="font-mono">{r.table}</code> was last computed on {longDay(r.lastRun)}
              {r.days !== null ? <> ({r.days === 0 ? "today" : r.days === 1 ? "a day ago" : `${r.days} days ago`})</> : null}
              {r.tsMax ? <>; the newest period it holds is {periodOf(r.tsMax, r.interval)}</> : null}.
            </>
          )}
        </p>
      ))}
      {detail ? <p className="mt-1 text-xs text-muted">{detail}</p> : null}
    </div>
  );
}

export type Field = { name: string; label: string; value: string; options: Option[] };

/** The filters: one select a field, each sending the form when it changes; the button sends it without script. */
export function FilterForm({ action, fields, reset, note }: { action: string; fields: Field[]; reset: { href: string; defaults: string }; note?: ReactNode }) {
  return (
    <InputPanel title="Filters" reset={reset} note={note}>
      <form method="get" action={action} className="flex flex-wrap items-end gap-4" data-filters="1">
        {fields.map((f) => <AutoSubmitSelect key={f.name} name={f.name} label={f.label} value={f.value} options={f.options} />)}
        <button type="submit" className="border border-accent bg-accent px-4 py-1.5 text-sm text-white">Show</button>
      </form>
    </InputPanel>
  );
}
