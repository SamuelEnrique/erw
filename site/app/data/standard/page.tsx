import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { DOCS, render } from "@/lib/markdown";

export const metadata: Metadata = { title: "Data standard" };

export default function Standard() {
  return (
    <>
      <p className="mb-4 text-sm">
        <Link href="/data#methods">Data</Link> / <code className="font-mono">docs/datastandard.md</code>
      </p>
      <article className="prose-erw" dangerouslySetInnerHTML={{ __html: render(DOCS.datastandard, "docs/datastandard.md") }} />
    </>
  );
}
