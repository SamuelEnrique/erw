import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { DOCS, digestDates, render } from "@/lib/markdown";

export const revalidate = 3600;
export const dynamicParams = false;

export function generateStaticParams() {
  return digestDates().map((date) => ({ date }));
}

export async function generateMetadata({ params }: PageProps<"/digest/[date]">): Promise<Metadata> {
  return { title: `Energy Digest, ${(await params).date}` };
}

export default async function DigestDay({ params }: PageProps<"/digest/[date]">) {
  const { date } = await params;
  const md = DOCS.digests[date];
  if (!md) notFound();
  const dates = digestDates();
  const i = dates.indexOf(date);
  return (
    <>
      <p className="mb-4 flex gap-4 text-sm">
        <Link href="/digest">Archive</Link>
        {dates[i + 1] ? <Link href={`/digest/${dates[i + 1]}`}>Earlier: {dates[i + 1]}</Link> : null}
        {i > 0 ? <Link href={`/digest/${dates[i - 1]}`}>Later: {dates[i - 1]}</Link> : null}
      </p>
      <article className="prose-erw" dangerouslySetInnerHTML={{ __html: render(md, `docs/digest/${date}.md`) }} />
    </>
  );
}
