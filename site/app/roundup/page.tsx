import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { DOCS, render, weeklyWeeks } from "@/lib/markdown";

export const revalidate = 3600;
export const metadata: Metadata = { title: "ERW's Roundup" };

// Session 17: the weekly brief (platform tool 14), "Energy Week" on Mondays. Session 23: ERW&apos;s Roundup,
// written and sent on Sundays at 23:00 UTC by warehouse/news/roundup.py; /weekly redirects here.
export default function RoundupIndex() {
  const weeks = weeklyWeeks();
  if (weeks.length === 0) {
    return (
      <>
        <h1 className="mb-2 text-3xl">ERW&apos;s Roundup</h1>
        <p className="text-sm text-muted">no data: no Roundup is committed in docs/roundup/ yet.</p>
      </>
    );
  }
  const newest = weeks[0];
  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_14rem]">
      <article className="prose-erw min-w-0" dangerouslySetInnerHTML={{ __html: render(DOCS.weeklies[newest], DOCS.weekly_source[newest]) }} />
      <aside className="text-sm lg:border-l lg:border-rule lg:pl-4">
        <h2 className="mb-2 text-lg">Archive</h2>
        <ul>
          {weeks.map((w) => (
            <li key={w}>
              <Link href={`/roundup/${w}`}>{w}</Link>
              {DOCS.weekly_source[w]?.startsWith("docs/weekly/") ? <span className="text-muted"> (Energy Week)</span> : null}
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs text-muted">
          ERW&apos;s Roundup is written and sent on Sundays at 23:00 UTC (4 PM Pacific) and covers Monday to Sunday, opening with the
          weekend&apos;s stories; it is committed to <code className="font-mono">docs/roundup/</code>. Until session 23 the weekly brief was
          Energy Week, on Mondays (<code className="font-mono">docs/weekly/</code>). The daily digest, Monday to Friday, is at{" "}
          <Link href="/digest">/digest</Link>; the chart of the week is on <Link href="/analysis">/analysis</Link>.
        </p>
      </aside>
    </div>
  );
}
