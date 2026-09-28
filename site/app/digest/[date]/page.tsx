import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { DOCS, digestDates, isWeekend, isoWeek, render, weeklyWeeks } from "@/lib/markdown";

export const revalidate = 3600;
// session 23: a Saturday or Sunday without a digest is answered with "no weekend issue", so any date is accepted
export const dynamicParams = true;

export function generateStaticParams() {
  return digestDates().map((date) => ({ date }));
}

export async function generateMetadata({ params }: PageProps<"/digest/[date]">): Promise<Metadata> {
  const { date } = await params;
  return { title: DOCS.digests[date] || !isWeekend(date) ? `ERW's Energy Digest, ${date}` : `No weekend issue, ${date}` };
}

export default async function DigestDay({ params }: PageProps<"/digest/[date]">) {
  const { date } = await params;
  const md = DOCS.digests[date];
  if (!md) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !isWeekend(date)) notFound();
    // session 23: the digest is written Monday to Friday; the weekend's stories open Sunday's Energy Roundup
    const week = isoWeek(date);
    const day = new Date(`${date}T00:00:00Z`).toLocaleDateString("en-US", { weekday: "long", timeZone: "UTC" });
    return (
      <>
        <p className="mb-4 text-sm"><Link href="/digest">Archive</Link></p>
        <h1 className="mb-2 text-3xl">No weekend issue</h1>
        <p className="max-w-prose">
          {day} {date}: ERW&apos;s Energy Digest is written Monday to Friday. The weekend&apos;s top stories open ERW&apos;s Roundup for {week},
          written and sent on Sunday at 23:00 UTC (4 PM Pacific){" "}
          {weeklyWeeks().includes(week) ? <Link href={`/roundup/${week}`}>(read it)</Link> : <>(not written yet; <Link href="/roundup">all Roundups</Link>)</>}.
        </p>
      </>
    );
  }
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
