import type { Metadata } from "next";
import Link from "next/link";
import { DOCS, archiveDays, digestDates, digestTitle, render } from "@/lib/markdown";

export const revalidate = 3600;
export const metadata: Metadata = { title: "ERW's Energy Digest" };

export default function DigestIndex() {
  const dates = digestDates();
  const newest = dates[0];
  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_14rem]">
      <article className="prose-erw min-w-0" dangerouslySetInnerHTML={{ __html: render(DOCS.digests[newest], `docs/digest/${newest}.md`) }} />
      <aside className="text-sm lg:border-l lg:border-rule lg:pl-4">
        <h2 className="mb-2 text-lg">Archive</h2>
        <ul>
          {archiveDays().map(({ date, has }) => (
            <li key={date}>
              {has ? <Link href={`/digest/${date}`}>{date}</Link> : <Link href={`/digest/${date}`} className="text-muted">{date}: no weekend issue</Link>}
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs text-muted">
          {dates.length} digests, written Monday to Friday at 14:00 UTC and committed to <code className="font-mono">docs/digest/</code>; the
          weekend&apos;s stories open Sunday&apos;s <Link href="/roundup">ERW&apos;s Roundup</Link>. {digestTitle(DOCS.digests[newest])} is shown here.
        </p>
      </aside>
    </div>
  );
}
