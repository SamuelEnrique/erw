import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { DOCS, archiveDays, digestDates, renderDigest } from "@/lib/markdown";
import { dayKind, dayWords } from "@/lib/digest";
import { utcDay } from "@/lib/license";

// session 402: ten minutes, not an hour: the page names today (UTC), so that after midnight the day before's Digest is
// not shown in today's place for long
export const revalidate = 600;
export const metadata: Metadata = { title: "ERW's Energy Digest" };

const KIND_WORDS = { weekend: "no weekend issue", pending: "not written yet", missed: "no Digest" } as const;

export default function DigestIndex() {
  const dates = digestDates();
  const newest = dates[0];
  const today = utcDay();
  // session 402: the page is today's Digest, or one line saying today has none; until this session it showed the newest
  // Digest whatever its day, so on a day without one a visitor read the day before's as today's
  const kind = dayKind(today, dates, today);
  return (
    <Brand>
    <div className="grid gap-8 lg:grid-cols-[1fr_14rem]">
      {kind === "digest" ? (
        <article className="prose-erw min-w-0" data-digest-today={today} dangerouslySetInnerHTML={{ __html: renderDigest(DOCS.digests[today], today) }} />
      ) : (
        <article className="prose-erw min-w-0" data-digest-today="none">
          <h1>ERW&apos;s Energy Digest</h1>
          <p data-digest-none={kind ?? "none"}>
            {kind === "weekend"
              ? <>No Digest on {dayWords(today)}: it is written Monday to Friday, and the weekend&apos;s stories open Sunday&apos;s <Link href="/roundup">ERW&apos;s Roundup</Link>.</>
              : <>No Digest yet for {dayWords(today)}: the weekday brief is written by the daily run, which starts at 14:00 UTC.</>}
            {newest ? <> The newest is <Link href={`/digest/${newest}`}>the Digest of {dayWords(newest)}</Link>.</> : null}
          </p>
        </article>
      )}
      <aside className="text-sm lg:border-l lg:border-rule lg:pl-4">
        <h2 className="mb-2 text-lg">Archive</h2>
        <ul>
          {archiveDays(today).map(({ date, kind: k }) => (
            <li key={date} data-archive-day={k}>
              {k === "digest" ? <Link href={`/digest/${date}`}>{date}</Link> : <Link href={`/digest/${date}`} className="text-muted">{date}: {KIND_WORDS[k]}</Link>}
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs text-muted">
          {dates.length} digests, written Monday to Friday by the daily run that starts at 14:00 UTC and committed to{" "}
          <code className="font-mono">docs/digest/</code>; the weekend&apos;s stories open Sunday&apos;s <Link href="/roundup">ERW&apos;s Roundup</Link>.
          {kind === "digest" ? <> Today&apos;s, {dayWords(today)}, is shown here.</> : null} <Link href="/about#digest">How the Digest is made</Link>.
        </p>
      </aside>
    </div>
    </Brand>
  );
}
