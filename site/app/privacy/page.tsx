import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";
import { Section } from "@/components/Section";

export const metadata: Metadata = { title: "Privacy" };

// Session 177: what the site records about a visit and what it does not. Every sentence here is checked against the
// code by tests/test_session177.py (the cookie names, the storage keys, the four events); the derivation of the daily
// hash is the method note docs/methods/usage_counts.md.
export default function Privacy() {
  return (
    <article className="max-w-3xl" data-privacy="1">
      <h1 className="mb-2 text-3xl">Privacy</h1>
      <p className="mb-6 text-sm">
        This site sets no tracking cookies, runs no advertising or analytics service, and keeps no profile of anyone. It counts how its
        tools are used, in a way that cannot follow a person. This page says exactly what is recorded.
      </p>

      <Section title="Usage counts" id="usage">
        <p className="mb-3 text-sm">When a page of this site is used, the site records one line with five things and nothing else:</p>
        <ul className="mb-3 list-disc space-y-1 pl-5 text-sm">
          <li>the page&apos;s path (for example <code className="font-mono">/storage</code>), without anything after a question mark;</li>
          <li>the name of the tool on that page;</li>
          <li>one of four events: a tool was opened, an input was changed, a scenario was compared, a file was downloaded;</li>
          <li>the day (UTC);</li>
          <li>a code that stands for one browser for that one day.</li>
        </ul>
        <p className="mb-3 text-sm">
          The code is made from the visitor&apos;s IP address and the browser&apos;s user agent, scrambled twice: once by this site&apos;s server under a secret
          it alone holds, and again by the database under a random value drawn new each day. Neither the address nor the user agent is
          stored or logged by the site. When the day is over the site keeps only the day&apos;s totals (how many events, from how many browsers)
          and deletes that day&apos;s codes and its random value, so the code of one day cannot be matched with the code of another, and nobody
          can be followed from day to day. The database&apos;s provider keeps its own backups for a few days, which hold a copy of what the
          tables held when a backup ran.
        </p>
        <p className="mb-3 text-sm">
          Never recorded: the IP address, the user agent, the page you came from, anything after a question mark in an address, what you
          type or choose in a tool, and any identifier kept in your browser. An input counts as changed; its name and its value are not sent.
        </p>
        <p className="mb-3 text-sm">
          If your browser sends Do Not Track or Global Privacy Control, nothing is counted at all. On the pages that say nothing you type
          is sent, only the opening of the page is counted: nothing is sent after it, whatever you do there.
        </p>
        <p className="text-sm text-muted">How the daily code is made, step by step: <Link href="/data/methods/usage_counts" gate="quiet">the usage counts method note</Link>.</p>
      </Section>

      <Section title="Cookies and browser storage" id="cookies">
        <p className="mb-3 text-sm">
          A visitor gets no cookie from this site. Two cookies exist, <code className="font-mono">erw_internal</code> and{" "}
          <code className="font-mono">erw_view</code>, and they are set only in the browser of a person reviewing the site, after that person
          opens the internal view with a token. They last 90 days, show the pages still in review, and are not used to count or follow anyone.
        </p>
        <p className="text-sm">
          The battery game keeps two things in your browser&apos;s own storage, on your device: that you have seen the tutorial, and the battery
          settings you last chose. They are never sent to the site. No other page stores anything in your browser.
        </p>
      </Section>

      <Section title="Limits on requests" id="limits">
        <p className="text-sm">
          To keep one address from flooding the question tools, the sign-up form, the game and the downloads, the site counts requests per
          address. The address itself is held only in the server&apos;s memory for the hour of the limit. What the database holds is a keyed
          code of the address for the current day, with a count: it cannot be turned back into an address, it is another value the next day,
          and it is deleted once it is a day old, the next time the site counts a request.
        </p>
      </Section>

      <Section title="What else the site stores" id="else">
        <ul className="list-disc space-y-1 pl-5 text-sm">
          <li><strong>Email sign-up.</strong> The address you give, what you chose to receive, and the times it was added, confirmed or unsubscribed. See <Link href="/terms">Terms</Link>.</li>
          <li><strong>Questions asked on Ask.</strong> The time, the question and whether it was answered, with nothing that identifies who asked. The question is sent to a Claude model from Anthropic to be answered.</li>
          <li><strong>The battery game.</strong> Each finished play (the day played, the moves, the score) under a random number made for that one play, and, if you choose to post a score, the nickname you type. No address and no account.</li>
        </ul>
      </Section>

      <Section title="Other parties" id="others">
        <p className="text-sm">
          The site is served by Vercel and its database is at Supabase; like any host they handle each request, IP address included, and
          keep their own operational logs under their own terms. The charts load one script file, the ECharts library, from the public
          library host cdnjs (Cloudflare), which therefore receives a request from your browser. Fonts are served by this site itself.
          There is no advertising network, no social media widget and no third-party analytics on any page.
        </p>
      </Section>
    </article>
  );
}
