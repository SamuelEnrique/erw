import type { Metadata } from "next";
import Link from "next/link";
import { DOCS, digestDates, digestTitle, render } from "@/lib/markdown";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Energy Digest" };

export default function DigestIndex() {
  const dates = digestDates();
  const newest = dates[0];
  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_14rem]">
      <article className="prose-erw min-w-0" dangerouslySetInnerHTML={{ __html: render(DOCS.digests[newest], `docs/digest/${newest}.md`) }} />
      <aside className="text-sm lg:border-l lg:border-rule lg:pl-4">
        <h2 className="mb-2 text-lg">Archive</h2>
        <ul>
          {dates.map((d) => (
            <li key={d}>
              <Link href={`/digest/${d}`}>{d}</Link>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs text-muted">
          {dates.length} digests, committed daily to <code className="font-mono">docs/digest/</code>. {digestTitle(DOCS.digests[newest])} is shown here.
        </p>
      </aside>
    </div>
  );
}
