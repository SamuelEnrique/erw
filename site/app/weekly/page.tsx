import type { Metadata } from "next";
import Link from "next/link";
import { DOCS, render, weeklyWeeks } from "@/lib/markdown";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Energy Week" };

// Session 17: the weekly brief (platform tool 14), written by warehouse/news/weekly.py on Mondays.
export default function WeeklyIndex() {
  const weeks = weeklyWeeks();
  if (weeks.length === 0) {
    return (
      <>
        <h1 className="mb-2 text-3xl">Energy Week</h1>
        <p className="text-sm text-muted">no data: no weekly brief is committed in docs/weekly/ yet.</p>
      </>
    );
  }
  const newest = weeks[0];
  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_14rem]">
      <article className="prose-erw min-w-0" dangerouslySetInnerHTML={{ __html: render(DOCS.weeklies[newest], `docs/weekly/${newest}.md`) }} />
      <aside className="text-sm lg:border-l lg:border-rule lg:pl-4">
        <h2 className="mb-2 text-lg">Archive</h2>
        <ul>
          {weeks.map((w) => (
            <li key={w}>
              <Link href={`/weekly/${w}`}>{w}</Link>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs text-muted">
          {weeks.length} weekly {weeks.length === 1 ? "brief" : "briefs"}, written on Mondays at 13:00 UTC and committed to{" "}
          <code className="font-mono">docs/weekly/</code>. The daily digest is at <Link href="/digest">/digest</Link>.
        </p>
      </aside>
    </div>
  );
}
