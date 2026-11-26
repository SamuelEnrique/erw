import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Section } from "@/components/Section";
import { TOPICS } from "@/lib/topics";

export const metadata: Metadata = { title: "Email" };

const STATES: Record<string, string> = {
  done: "Thank you: the address is on the list.",
  // session 23: double opt-in and the tokened unsubscribe
  check: "Almost done: a confirmation email is on its way. Nothing is sent to the address until the link in it is followed.",
  unsent: "The address is stored, but the confirmation email could not be sent just now, so nothing will be sent to it. Please try again later.",
  confirmed: "Confirmed: the emails you chose will come to this address. Every email has a link to stop them.",
  unsubscribed: "Unsubscribed: no more emails will come to this address.",
  badlink: "That link is not valid (it may be incomplete). Nothing was changed.",
  notopic: "Choose at least one topic. Nothing was stored.",
  invalid: "That does not look like an email address. Nothing was stored.",
  busy: "Too many sign-ups just now. Nothing was stored; please try again in an hour.",  // session 177: the limits of /api/subscribe
  error: "The address could not be stored just now. Nothing was stored; please try again later.",
  none: "Choose the daily digest, ERW's Roundup, or both. Nothing was stored.",
};

export default async function SubscribePage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const state = typeof sp.state === "string" ? STATES[sp.state] : undefined;
  // session 59: an email's unsubscribe link opens this page and asks; only the button below unsubscribes (a link scanner's
  // GET changes nothing). The address and token travel in hidden fields to /api/unsubscribe.
  const one = (k: string) => (typeof sp[k] === "string" ? (sp[k] as string) : "");
  const confirm = one("confirm") === "1" && one("e") && /^[0-9a-f]{64}$/.test(one("t"));
  return (
    <Brand>
      <h1 className="mb-1 text-3xl">Email</h1>
      <p className="mb-6 max-w-3xl text-sm text-muted">
        ERW&apos;s Energy Digest and ERW&apos;s Roundup by email, as short plain text with an HTML copy.
      </p>
      <Section title="What the email is">
        <ul className="max-w-3xl list-disc space-y-1 pl-5 text-sm">
          {/* session 10238 (docs/reviews/small-pages-audit-2026-11-26.md, finding 2): the email of the issues in the v2 form (session
              2703; warehouse/news/email_digest.py render: the opening number, the numbers block, three stories, the chart, the fun fact) */}
          <li>
            <strong>Weekdays (no weekend issue):</strong> the day&apos;s <Link href="/digest">Energy Digest</Link> in short: its opening number; its
            numbers (a market price, a physical figure such as demand, a project, and a policy, capital or reliability figure); the first three
            stories of what moved, each with why it matters and a link to its source; the chart of the day and a fun fact. The rest of the issue is
            one link away on the site.
          </li>
          <li>
            <strong>Sundays, 23:00 UTC (4 PM Pacific in summer time, 3 PM in winter):</strong> the <Link href="/roundup">ERW&apos;s Roundup</Link>: its
            opening number, the week in five numbers, the first three stories of what mattered, the chart of the week, the week ahead and a fun fact;
            the weekend&apos;s stories and the rest of the week are one link away on the site.
          </li>
          <li>
            Each figure says where it came from: a warehouse table, as on this site, or, for a figure a news story reported, its outlet. The email
            links back to the site for everything else.
          </li>
          <li>
            <strong>Your topics:</strong> with every topic chosen, the email&apos;s stories are the first three of the issue&apos;s own; with fewer,
            up to five of the day&apos;s (or week&apos;s) highest-ranked stories in the topics you choose. The numbers, the chart and the fun fact are
            always included. The <Link href="/digest">website digest</Link> stays complete.
          </li>
        </ul>
      </Section>
      {confirm ? (
        <Section title="Unsubscribe">
          <form method="post" action="/api/unsubscribe" className="flex max-w-xl flex-wrap items-center gap-3 border border-rule bg-panel p-3 text-sm">
            <input type="hidden" name="e" value={one("e")} />
            <input type="hidden" name="t" value={one("t")} />
            <input type="hidden" name="confirm" value="yes" />
            <span>Stop every ERW email to <strong>{one("e")}</strong>?</span>
            <button type="submit" className="border border-accent bg-accent px-4 py-1.5 text-white">Unsubscribe</button>
          </form>
          <p className="mt-2 max-w-xl text-xs text-muted">Nothing changes until you press the button.</p>
        </Section>
      ) : null}
      <Section title="Sign up">
        {state ? (
          <p className="mb-3 border border-dashed border-rule bg-panel px-3 py-2 text-sm" role="status">
            {state}
          </p>
        ) : null}
        <form method="post" action="/api/subscribe" className="flex max-w-xl flex-wrap items-end gap-3">
          <label className="flex flex-1 flex-col text-xs text-muted">
            Email address
            <input name="email" type="email" required maxLength={254} autoComplete="email" className="mt-1 border border-rule bg-panel px-2 py-1 text-sm text-ink" />
          </label>
          <fieldset className="flex w-full flex-wrap gap-4 text-sm">
            <legend className="mb-1 text-xs text-muted">Send me</legend>
            <label className="flex items-center gap-1">
              <input type="checkbox" name="daily" defaultChecked /> the daily Energy Digest
            </label>
            <label className="flex items-center gap-1">
              <input type="checkbox" name="weekly" /> ERW&apos;s Roundup, on Sundays
            </label>
          </fieldset>
          <fieldset className="grid w-full grid-cols-1 gap-x-4 gap-y-1 text-sm sm:grid-cols-2">
            <legend className="mb-1 text-xs text-muted">Topics for the top stories (all are checked; uncheck what you do not want)</legend>
            {TOPICS.map((t) => (
              <label key={t.id} className="flex items-center gap-1">
                <input type="checkbox" name="topic" value={t.id} defaultChecked /> {t.label}
              </label>
            ))}
          </fieldset>
          <label className="hidden" aria-hidden="true">
            Leave empty
            <input name="website" type="text" tabIndex={-1} autoComplete="off" />
          </label>
          <button type="submit" className="border border-accent bg-accent px-4 py-1.5 text-sm text-white">
            Sign up
          </button>
        </form>
        <p className="mt-3 max-w-3xl text-sm">Privacy: your address is used only to send the emails you chose, never shared or sold, and you can ask for it to be removed at any time.</p>
        <div className="mt-4 max-w-3xl space-y-2 text-xs text-muted">
          <p>
            {/* session 10238 (docs/reviews/small-pages-audit-2026-11-26.md, finding 1): since migration 034 the site's server writes the
                address with the service key, which can read the table; the suppression list is stored too (migration 007) */}
            What is stored: the address, which emails and topics you chose, the time it was added, and when it was confirmed or unsubscribed, in the
            ERW&apos;s Supabase database; an address that unsubscribes is also kept on a suppression list, so that it is never emailed again. The
            site&apos;s server writes the address with the warehouse&apos;s service key, which can read the table and which no browser is given; no page
            of the site reads an address back. The address is used for this email only, and never shared.
          </p>
          <p>
            Double opt-in: after you sign up, a confirmation email arrives with a signed link; nothing else is sent until you follow it. Every email
            then carries a signed unsubscribe link (<code className="font-mono">warehouse/news/email_digest.py</code>): it opens this page, and one
            press of its button stops every email (the link alone changes nothing, so a mail scanner that follows it cannot unsubscribe you); a mail
            program that shows its own unsubscribe button stops them in one click.{/* session 10238, small pages audit finding 6: app/api/unsubscribe/route.ts */}
          </p>
        </div>
      </Section>
    </Brand>
  );
}
