import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";
import { contextOf } from "@/lib/askContext";
import { AskErcot } from "./AskErcot";

// Session 92: Ask ERCOT, the reference version. Ask developed fully for one grid before any other: it knows every ERCOT
// table (lib/chat/spec_ercot.json, exported from warehouse/chat/ercot.py), an answer that rests on a series comes with
// a chart and the rows it fetched, it proposes what to ask next, and a view of the site can open it with that view's
// period and settings (/ask/ercot?from=<view>&title=<its name>&s_<setting>=<value>&q=<question>). In review
// (lib/release.ts). The general chat (/ask) and the grid pages' chats (/ask?grid=<slug>) are as they were.
// Session 121: a conversation (the turns before go with the next question), a refusal that names the nearest tables, a
// premise the tables contradict said first, what is being read shown while the answer is prepared, and each chart
// checked against the rows fetched.
// Session 137: the box and the answer panel are one component (components/ask/AskPanel.tsx); what the page said about
// how answers are made is in docs/methods/ask_ercot.md, linked under the box.
// Session 156: the line under the title said that the panel spoke for one grid only. Since session 153 the tool answers
// for the other grids what four pages show, so the line now says that (as a refusal's closing words do, lib/chat/ready.ts).
export const metadata: Metadata = { title: "Ask ERCOT", robots: { index: false, follow: false } };

export default async function AskErcotPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const context = contextOf(sp);
  const q = typeof sp.q === "string" ? sp.q.slice(0, 500) : "";
  return (
    <>
      <h1 className="mb-1 text-3xl">Ask ERCOT</h1>
      <p className="mb-4 max-w-3xl text-sm">
        A question about the Texas grid, answered from the ERCOT tables of the warehouse and the ERCOT page&apos;s own text. For the other grids it answers
        only what four pages show: curtailment, what a datacenter pays, the capture price and the resource layers;
        {" "}<Link href="/ask">the general chat</Link> covers the whole warehouse.
      </p>
      <AskErcot initial={q} context={context} />
    </>
  );
}
