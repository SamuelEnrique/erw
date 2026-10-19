import { redirect } from "next/navigation";
import { gridBy, gridHref } from "@/lib/gridtool";

// Session 299 (the owner's merge of 18 October 2026: "/mix and /ask become redirects to the tab and the panel"): /ask is
// the Ask panel of the Grid tool. /ask opens the panel beside the Lower 48 (the general chat, the whole warehouse);
// /ask?grid=<slug> opens it beside that grid (the grid's scoped chat, session 35, or Ask ERCOT's profile); a question
// carried in the address (q) is placed in the box, never sent. The page that stood here (sessions 35 to 298) is kept,
// unrouted, in app/_retired/ask-original. /ask/ercot (the reference version, session 92) is not this page and stays.
// The redirect is the page's own (a 307, reversible), not a rule of next.config.ts, so the query is carried whole.
export default async function AskPage({ searchParams }: { searchParams: Promise<{ grid?: string | string[]; q?: string | string[] }> }) {
  const sp = await searchParams;
  const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);
  const grid = one(sp.grid);
  const q = one(sp.q);
  // gridHref writes the grid (and the opening tab, Mix, writes no view); the panel's flag and the question follow (a grid by any of its words, else the Lower 48)
  const base = gridHref(gridBy(grid)?.slug ?? "us48");
  redirect(`${base}${base.includes("?") ? "&" : "?"}ask=1${q ? `&q=${encodeURIComponent(q.slice(0, 500))}` : ""}`);
}
