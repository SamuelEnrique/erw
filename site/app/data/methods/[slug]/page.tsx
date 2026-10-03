import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { notFound } from "next/navigation";
import { DOCS, render } from "@/lib/markdown";

export const dynamicParams = false;

export function generateStaticParams() {
  return Object.keys(DOCS.methods).map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: PageProps<"/data/methods/[slug]">): Promise<Metadata> {
  return { title: `Method: ${(await params).slug}` };
}

export default async function Method({ params }: PageProps<"/data/methods/[slug]">) {
  const { slug } = await params;
  const md = DOCS.methods[slug];
  if (!md) notFound();
  return (
    <>
      <p className="mb-4 text-sm">
        <Link href="/data#methods">Data</Link> / <code className="font-mono">docs/methods/{slug}.md</code>
      </p>
      <article className="prose-erw" dangerouslySetInnerHTML={{ __html: render(md, `docs/methods/${slug}.md`) }} />
    </>
  );
}
