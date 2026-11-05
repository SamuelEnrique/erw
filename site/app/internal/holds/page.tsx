import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { cookies } from "next/headers";
import { notFound } from "next/navigation";
import { HOLDS, REPO, isSitePath, tablesOf, type HoldRow, type HoldTable } from "@/lib/holds";
import { COOKIE } from "@/lib/release";
import { internalOk } from "@/lib/thesis/server";

// Session 587: the held figures that show. From 21 October 2026 a figure read from a table held for a license is drawn
// as "license needed" (lib/license.ts, components/Num.tsx); session 505's scripts/check-holds.mjs reads every page of
// check-values' list on a build and writes docs/licenses_holds.csv, one line a page that still draws such a figure
// without those words. This page is that file, read when the site is built (scripts/holds-content.mjs, lib/holds.ts):
// one row a line, each cell as written, with each table's record in warehouse/metadata/license_status.csv. It draws no
// figure of a held table: only the addresses, the tables, their verdicts, the grids and the check's count. How a held
// panel is drawn, and whether the check joins the landing gate, are Samuel's (session 505); this page decides neither.
// Internal: no nav link, not indexed, never cached (next.config.ts gives every /internal address those headers), and
// behind the internal view exactly as the waits page is: the page answers 404 unless the browser holds the internal
// cookie (set by the form at /internal/open). It takes no token in its address, reads no database and writes nothing.
export const dynamic = "force-dynamic";

/** The page's name is sent only to the internal view: a visitor's 404 carries none of this page's words. */
export async function generateMetadata(): Promise<Metadata> {
  const inside = (process.env.INTERNAL_COSTS_TOKEN ?? "").length >= 24 && (await internalOk((await cookies()).get(COOKIE)?.value));
  return { ...(inside ? { title: "Held figures that show (internal)" } : {}), robots: { index: false, follow: false } };
}

const plural = (n: number, one: string, many: string) => `${n.toLocaleString("en-US")} ${n === 1 ? one : many}`;
const fileLink = (p: string) => `${REPO}/blob/main/${p}`;

function TableRecord({ name, rec }: { name: string; rec: HoldTable | null | undefined }) {
  return (
    <li className="py-0.5" data-hold-table={name} data-hold-status={rec?.status ?? ""}>
      <span className="font-mono text-xs">{name}</span>
      {rec ? (
        <span className="text-xs text-muted">
          : {rec.status || "no status"}{rec.from ? ` from ${rec.from}` : ""}; verdict {rec.verdict ? <>&quot;{rec.verdict}&quot;</> : "not recorded"}
          {rec.publishers ? `; publishers ${rec.publishers}` : ""}
        </span>
      ) : (
        <span className="text-xs text-muted">: no row in license_status.csv</span>
      )}
    </li>
  );
}

function Row({ r, i }: { r: HoldRow; i: number }) {
  return (
    <tr className="border-b border-rule align-top" data-hold-row={i} data-hold-page={r.page}>
      <th scope="row" className="py-2 pr-3 text-left font-normal" style={{ overflowWrap: "anywhere" }}>
        {isSitePath(r.page) ? <a className="font-mono text-xs underline" href={r.page}>{r.page}</a> : <span className="font-mono text-xs">{r.page}</span>}
      </th>
      <td className="py-2 pr-3 text-right tabular-nums" data-hold-figures={r.figures}>{r.figures}</td>
      <td className="py-2 pr-3 text-xs">{r.kinds || "none named"}</td>
      <td className="py-2 pr-3">
        <ul>{tablesOf(r.tables).map((t) => <TableRecord key={t} name={t} rec={HOLDS.tables[t]} />)}</ul>
      </td>
      <td className="py-2 pr-3 text-xs">{r.grids || "none named"}</td>
      <td className="py-2 text-xs tabular-nums">{r.day}</td>
    </tr>
  );
}

export default async function HoldsPage() {
  const want = process.env.INTERNAL_COSTS_TOKEN ?? "";
  if (want.length < 24 || !(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();

  const h = HOLDS;
  const built = `${h.built_at.slice(0, 10)} ${h.built_at.slice(11, 16)} UTC`;
  const days = [...new Set(h.rows.map((r) => r.day))].sort();
  const tables = Object.keys(h.tables).sort();
  return (
    <Brand noUsage>
    <div className="max-w-5xl" data-holds={h.unread ? "unread" : String(h.rows.length)} data-no-usage>
      <h1 className="mb-1 text-3xl">Held figures that show (internal)</h1>
      <p className="mb-3 text-sm text-muted">
        A table held for a license is drawn as &quot;license needed&quot; in place of its numbers. The check{" "}
        <span className="font-mono">site/scripts/check-holds.mjs</span> reads every page of check-values&apos; list and writes{" "}
        <a className="underline" href={fileLink(h.source)} rel="noreferrer"><span className="font-mono">{h.source}</span></a>, one line a page that still draws a
        figure of a held table without those words. Below is that file, one row a line, each cell as the check wrote it, with each table&apos;s
        record in <a className="underline" href={fileLink(h.status_source)} rel="noreferrer"><span className="font-mono">{h.status_source}</span></a>. No figure of a
        held table is drawn here. Read when the site was built, {built}.
      </p>
      {h.unread ? (
        <p className="mb-6 border border-rule bg-panel p-2 text-sm" role="status" data-holds-unread="1">
          The list could not be read: {h.unread}. Nothing is listed, and nothing is known to show or not to show.
        </p>
      ) : (
        <>
          <div className="mb-4 grid grid-cols-3 gap-px border border-rule bg-rule">
            <div className="bg-panel p-3"><div className="text-xs text-muted">Pages listed</div><div className="text-2xl tabular-nums" data-hn="pages">{h.rows.length}</div></div>
            <div className="bg-panel p-3"><div className="text-xs text-muted">Held tables named</div><div className="text-2xl tabular-nums" data-hn="tables">{tables.length}</div></div>
            <div className="bg-panel p-3"><div className="text-xs text-muted">Checked on</div><div className="text-2xl tabular-nums" data-hn="day">{days.length ? days.join(", ") : "no line"}</div></div>
          </div>
          {h.status_unread ? (
            <p className="mb-4 border border-rule bg-panel p-2 text-sm" role="status" data-holds-status-unread="1">
              The tables&apos; records could not be read ({h.status_unread}), so no verdict is shown.
            </p>
          ) : null}
          {h.rows.length === 0 ? (
            <p className="mb-6 text-sm" data-holds-none="1">The file holds no line: on the day it was written, no page read drew a figure of a held table without the words.</p>
          ) : (
            <div className="mb-6 overflow-x-auto">
              <table className="w-full text-sm" style={{ minWidth: 860 }}>
                <caption className="sr-only">Pages that draw a figure of a table held for a license without the words license needed, as the check listed them</caption>
                <thead>
                  <tr className="border-b border-ink text-left text-xs text-muted">
                    <th scope="col" className="py-1 pr-3">Address</th>
                    <th scope="col" className="pr-3 text-right">Held figures shown (the check&apos;s count)</th>
                    <th scope="col" className="pr-3">Kinds</th>
                    <th scope="col" className="pr-3">Tables and their verdicts</th>
                    <th scope="col" className="pr-3">Grids held</th>
                    <th scope="col">Checked on</th>
                  </tr>
                </thead>
                <tbody>{h.rows.map((r, i) => <Row key={`${i}-${r.page}`} r={r} i={i} />)}</tbody>
              </table>
            </div>
          )}
        </>
      )}
      <p className="text-xs text-muted">
        The kinds are the check&apos;s: a <em>number</em> is a checked number drawn with its value, a <em>panel</em> a research card&apos;s small multiple of a
        held grid, a <em>view</em> a card&apos;s one-grid view. The list is as old as its last run: it is written by{" "}
        <span className="font-mono">node scripts/check-holds.mjs &lt;base&gt; --csv ../docs/licenses_holds.csv</span> on a build and committed, and this page is
        rebuilt with the site. {plural(h.rows.length, "line is", "lines are")} read. How a held figure is drawn, and whether the check joins the landing gate,
        wait for Samuel&apos;s ruling (session 505); this page changes no page.
      </p>
    </div>
    </Brand>
  );
}
