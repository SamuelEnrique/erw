// Energy Research Warehouse (ERW) site, session 404: the freshness line of an explorer whose table is held for review
// (lib/explore/heldfresh.ts says why the shared Freshness in ./Explore.tsx cannot read it). The same lines as Freshness,
// in its manner: each table's last computation and the newest period it holds, from the catalogue, never written by
// hand; a table not computed for more than `staleAfterDays` days is said to be stale, with its date, first. Kept in a
// file of its own so that the explorers built in parallel on ./Explore.tsx merge cleanly.
import type { ReactNode } from "react";
import { longDay, periodOf } from "@/lib/explore";
import { freshnessHeld } from "@/lib/explore/heldfresh";

export async function HeldFreshness({ tables, staleAfterDays = 3, detail }: { tables: string[]; staleAfterDays?: number; detail?: ReactNode }) {
  const f = await freshnessHeld(tables);
  if (!f.ok) {
    return <p className="mb-6 text-sm text-muted" data-fresh="unread">How old these tables are could not be read: the catalogue did not answer.</p>;
  }
  const stale = f.rows.filter((r) => r.days !== null && r.days > staleAfterDays);
  return (
    <div className={`mb-6 border-l-2 px-3 py-2 text-sm ${stale.length ? "border-accent bg-paper" : "border-rule"}`} data-fresh={stale.length ? "stale" : "fresh"}>
      {f.rows.map((r) => (
        <p key={r.table} data-fresh-table={r.table} data-last-run={r.lastRun ?? ""} data-ts-max={r.tsMax ?? ""} data-held={f.held.includes(r.table) ? "review" : ""}>
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
