import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { DOCS } from "@/lib/markdown";
import { AskForm } from "./AskForm";

export const metadata: Metadata = { title: "Ask" };

// session 35: /ask?grid=<slug>&q=<question> is a grid page's scoped chat, opened by its "Ask" box
export default async function AskPage({ searchParams }: { searchParams: Promise<{ grid?: string; q?: string }> }) {
  const sp = await searchParams;
  const g = DOCS.grid_config.find((x) => x.slug === sp.grid) ?? null;
  return (
    <>
      <h1 className="mb-1 text-3xl">{g ? `Ask ${g.iso}` : "Ask the warehouse"}</h1>
      {g ? (
        <p className="mb-2 max-w-3xl text-sm">
          This chat speaks for {g.name} only: it reads the tables and rows that carry {g.iso}, and the text of its{" "}
          <Link href={`/grid/${g.slug}`}>grid page</Link> (cited as docs/grids/{g.slug}.md). <Link href="/ask">Ask about the whole warehouse</Link>.
        </p>
      ) : null}
      <p className="mb-5 max-w-3xl text-sm text-muted">
        A question about US energy prices, demand, generation, projects or news, answered only from the ERW tables this site reads. Every number in an
        answer comes from a query of a table, and the answer names the table and its source report; a number that cannot be traced to a query is not
        shown. If the warehouse does not hold the answer, it says so. Public tables only; power prices and demand cover the last 35 days. At most 10
        questions per hour.
      </p>
      <AskForm grid={g?.slug ?? null} initial={sp.q ?? ""} placeholder={g ? `For example: what was ${g.iso}'s highest demand this week?` : undefined} />
    </>
  );
}
