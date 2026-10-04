import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";
import spec from "@/lib/chat/spec_ercot.json";
import { contextOf } from "@/lib/askContext";
import { AskErcot } from "./AskErcot";

// Session 92: Ask ERCOT, the reference version. Ask developed fully for one grid before any other: it knows every ERCOT
// table (lib/chat/spec_ercot.json, exported from warehouse/chat/ercot.py), an answer that rests on a series comes with
// a chart and the rows it fetched, it proposes what to ask next, and a view of the site can open it with that view's
// period and settings (/ask/ercot?from=<view>&title=<its name>&s_<setting>=<value>&q=<question>). In review
// (lib/release.ts). The general chat (/ask) and the grid pages' chats (/ask?grid=<slug>) are as they were.
export const metadata: Metadata = { title: "Ask ERCOT", robots: { index: false, follow: false } };

export default async function AskErcotPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const context = contextOf(sp);
  const q = typeof sp.q === "string" ? sp.q.slice(0, 500) : "";
  return (
    <>
      <h1 className="mb-1 text-3xl">Ask ERCOT</h1>
      <p className="mb-2 max-w-3xl text-sm">
        A question about the Texas grid, answered only from the {spec.tables.length} ERCOT tables of the warehouse: prices at the hubs and for reserves, demand,
        generation, the batteries and what they could earn, the evening shoulder, the storms and heat waves, and the interconnection queue.
        This chat speaks for ERCOT only; <Link href="/ask">the general chat</Link> covers the whole warehouse.
      </p>
      <p className="mb-5 max-w-3xl text-sm text-muted">
        Every number in an answer comes from a query of a table, and the answer names the table; a number that cannot be traced to a query is not shown. An answer
        that rests on a series comes with a chart and the rows it was drawn from. If the tables do not hold the answer, it says so. On this site the tables are the
        live set&apos;s: the hub price history before the newest weeks, the reserve prices and Berkeley Lab&apos;s queue are in the warehouse and not yet in the
        site&apos;s database, and the chat says so when asked for them. At most 10 questions per hour.
      </p>
      <AskErcot initial={q} context={context} />
    </>
  );
}
