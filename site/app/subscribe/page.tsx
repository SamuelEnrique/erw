import type { Metadata } from "next";
import Link from "next/link";
import { Section } from "@/components/Section";

export const metadata: Metadata = { title: "Email" };

const STATES: Record<string, string> = {
  done: "Thank you: the address is on the list.",
  invalid: "That does not look like an email address. Nothing was stored.",
  error: "The address could not be stored just now. Nothing was stored; please try again later.",
};

export default async function SubscribePage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = await searchParams;
  const state = typeof sp.state === "string" ? STATES[sp.state] : undefined;
  return (
    <>
      <h1 className="mb-1 text-3xl">Email</h1>
      <p className="mb-6 max-w-3xl text-sm text-muted">
        The Energy Digest and Energy Week by email, as short plain text with an HTML copy.
      </p>
      <Section title="What the email is">
        <ul className="max-w-3xl list-disc space-y-1 pl-5 text-sm">
          <li>
            <strong>Daily:</strong> the top 5 headlines of the day&apos;s <Link href="/digest">Energy Digest</Link>, each with why it matters and a link to
            its source, and the digest&apos;s numbers: yesterday&apos;s day-ahead average at each ISO&apos;s main hub, the highest real-time price, and
            the latest Henry Hub, WTI and Brent closes.
          </li>
          <li>
            <strong>Mondays:</strong> <Link href="/weekly">Energy Week</Link>, the five stories of the week and the week&apos;s numbers.
          </li>
          <li>
            Every number comes from the warehouse and names its table, as on this site. The email links back to the site for everything else.
          </li>
        </ul>
      </Section>
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
          <label className="hidden" aria-hidden="true">
            Leave empty
            <input name="website" type="text" tabIndex={-1} autoComplete="off" />
          </label>
          <button type="submit" className="border border-rule bg-panel px-3 py-1 text-sm">
            Sign up
          </button>
        </form>
        <div className="mt-4 max-w-3xl space-y-2 text-xs text-muted">
          <p>
            What is stored: the address and the time it was added, in the ERW&apos;s Supabase database. The public site can add an address but cannot
            read one back; only the warehouse&apos;s own service key can. The address is used for this email only, and never shared.
          </p>
          <p>
            Sending to this list is not switched on yet. The daily run sends the email to a fixed list of recipients
            (<code className="font-mono">warehouse/news/email_digest.py</code>); the first send to this list will say how to stop receiving it.
          </p>
        </div>
      </Section>
    </>
  );
}
