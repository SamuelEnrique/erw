import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { notFound } from "next/navigation";
import { DOCS, digestDates, isoWeek, renderDigest, weeklyWeeks } from "@/lib/markdown";
import { dayKind, dayWords } from "@/lib/digest";
import { digestRevisions } from "@/lib/digestLive";
import { utcDay } from "@/lib/license";

export const revalidate = 3600;
// session 23: a Saturday or Sunday without a digest is answered with "no weekend issue", so any date is accepted;
// session 402: so is a weekday of the archive without one ("no Digest"), and today before it is written
export const dynamicParams = true;

export function generateStaticParams() {
  return digestDates().map((date) => ({ date }));
}

const TITLE = { digest: "ERW's Energy Digest", weekend: "No weekend issue", pending: "No Digest yet", missed: "No Digest" } as const;

export async function generateMetadata({ params }: PageProps<"/digest/[date]">): Promise<Metadata> {
  const { date } = await params;
  const kind = dayKind(date, digestDates(), utcDay());
  return { title: `${TITLE[kind ?? "digest"]}, ${date}` };
}

export default async function DigestDay({ params }: PageProps<"/digest/[date]">) {
  const { date } = await params;
  const dates = digestDates();
  const kind = dayKind(date, dates, utcDay());
  if (kind === null) notFound();
  // the archive's neighbours: the Digests just before and after the day (a day without one has them too)
  const earlier = dates.find((d) => d < date), later = [...dates].reverse().find((d) => d > date);
  const nav = (
    <p className="mb-4 flex flex-wrap gap-x-4 text-sm">
      <Link href="/digest">Archive</Link>
      {earlier ? <Link href={`/digest/${earlier}`}>Earlier: {earlier}</Link> : null}
      {later ? <Link href={`/digest/${later}`}>Later: {later}</Link> : null}
    </p>
  );
  if (kind !== "digest") {
    // session 23: the digest is written Monday to Friday; the weekend's stories open Sunday's Energy Roundup.
    // session 402: a weekday without a Digest says so in one line too, and shows no other day's
    const week = isoWeek(date);
    return (
      <Brand>
        {nav}
        <h1 className="mb-2 text-3xl">{TITLE[kind]}</h1>
        <p className="max-w-prose" data-digest-none={kind}>
          {kind === "weekend" ? (
            <>
              {dayWords(date)}: ERW&apos;s Energy Digest is written Monday to Friday. The weekend&apos;s top stories open ERW&apos;s Roundup for {week},
              written and sent on Sunday at 23:00 UTC (4 PM Pacific){" "}
              {weeklyWeeks().includes(week) ? <Link href={`/roundup/${week}`}>(read it)</Link> : <>(not written yet; <Link href="/roundup">all Roundups</Link>)</>}.
            </>
          ) : kind === "pending"
            ? <>No Digest yet for {dayWords(date)}: the weekday brief is written by the daily run, which starts at 14:00 UTC.</>
            : <>No Digest was published for {dayWords(date)}.</>}
        </p>
      </Brand>
    );
  }
  // session 2207: a figure the warehouse revised after the issue was written is said in one line under the numbers
  const revisions = await digestRevisions(DOCS.digests[date], date);
  return (
    <Brand>
      {nav}
      <article className="prose-erw" data-digest-day={date} dangerouslySetInnerHTML={{ __html: renderDigest(DOCS.digests[date], date, new Date(), revisions) }} />
    </Brand>
  );
}
