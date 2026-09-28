import type { Metadata } from "next";
import Link from "next/link";
import { Section } from "@/components/Section";
import site from "@/data/site.json";
import { DOCS } from "@/lib/markdown";

export const metadata: Metadata = { title: "Terms" };

// Session 21, ruling 11: data licensing per source (warehouse/metadata/sources.csv), what the site stores
// about subscribers, that Ask questions are logged without identity, and what the site is and is not.
export default function Terms() {
  const news = DOCS.sources.filter((s) => s.report.startsWith("news stories"));
  const data = DOCS.sources.filter((s) => !s.report.startsWith("news stories")).sort((a, b) => a.publisher.localeCompare(b.publisher) || a.source.localeCompare(b.source));
  return (
    <article className="max-w-4xl">
      <h1 className="mb-2 text-3xl">Terms</h1>
      <p className="mb-6 text-sm">
        The ERW is a Stanford student research project. Nothing on this site is investment advice: the data are shown as their sources publish them,
        may contain errors or gaps, and come with no warranty.
      </p>

      <Section title="Data licensing, per source" id="licensing">
        <p className="mb-3 text-sm">
          Every table carries a license from its sources: <strong>public</strong> when all of its sources allow republication, <strong>internal</strong>{" "}
          when any source allows internal use only. Internal tables stay in the warehouse and never appear on this site; a table the ERW derives
          from others takes the most restrictive license among them. The {data.length} data sources in the registry
          (<code className="font-mono">warehouse/metadata/sources.csv</code>):
        </p>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-rule text-left text-xs text-muted">
                <th className="py-1 pr-3 font-normal">Publisher</th>
                <th className="py-1 pr-3 font-normal">Report</th>
                <th className="py-1 pr-3 font-normal">License</th>
              </tr>
            </thead>
            <tbody>
              {data.map((s) => (
                <tr key={s.source} className="border-b border-rule/60 align-top">
                  <td className="py-1 pr-3">{s.publisher}</td>
                  <td className="py-1 pr-3">{s.report_url ? <a href={s.report_url}>{s.report}</a> : s.report}</td>
                  <td className="py-1 pr-3">{s.license}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-sm">
          News: {news.length} outlets. Their titles and summaries are kept only for scoring and linking and are licensed internal: this site shows
          the ERW&apos;s own headlines and reasons, and links to each story at its outlet.
        </p>
      </Section>

      <Section title="Subscribers" id="subscribers">
        <p className="text-sm">
          The <Link href="/subscribe">email sign-up</Link> stores the address, which emails were chosen (the daily digest, the Energy Roundup,
          or both), the topics chosen for the top stories, the time it was added, and the times it was confirmed or unsubscribed, in the
          ERW&apos;s Supabase database. The public site can add an address but cannot read one back; only the warehouse&apos;s own service key can.
          Nothing is sent to an address until it confirms through the signed link in its confirmation email (double opt-in), and every email
          carries a signed one-click unsubscribe link; an address that unsubscribes is kept on a suppression list so that it is never emailed
          again, and is removed on request.
        </p>
      </Section>

      <Section title="Questions asked on Ask" id="ask">
        <p className="text-sm">
          Each question asked on <Link href="/ask">Ask</Link> is logged without identity: the time, the question and whether it was answered. The
          requester&apos;s IP address is held in the server&apos;s memory only to enforce the limit of questions per hour, and is never logged or stored.
          Questions are answered by a Claude model from Anthropic, which receives the question and the warehouse&apos;s data.
        </p>
      </Section>

      <p className="mt-6 text-sm text-muted">
        Code, data standard and session logs: <a href={site.repository}>{site.repository.replace("https://", "")}</a>.
      </p>
    </article>
  );
}
