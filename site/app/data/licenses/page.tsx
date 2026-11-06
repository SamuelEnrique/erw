import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Num } from "@/components/Num";
import { Section } from "@/components/Section";
import { DOCS, render } from "@/lib/markdown";
import { LETTERS, holds, permissive } from "@/lib/licensesPage";
import status from "@/data/license_status.json";
import site from "@/data/site.json";

// Session 471 (chain 019): the licensing record as a page, in review (site/lib/release.ts has no line for it, so it
// takes the in-review page like every page). A short reading from the two files the record writes, then
// docs/licenses.md itself, rendered as the methods pages render their notes: every table's verdict, each publisher's
// own sentence with the address read and the day. No publisher is read for this page and no table is read.

export const metadata: Metadata = { title: "Licenses" };

const repo = (p: string) => `${site.repository}/blob/main/${p}`;
const day = (d: string) => new Date(`${d}T00:00:00Z`).toLocaleDateString("en-US", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });

export default function Licenses() {
  const h = holds(status);
  const { both, todayOnly } = permissive(DOCS.license_verdicts ?? []);
  const grids = h.byPublisher.filter((p) => ["NYISO", "ISO-NE", "MISO", "PJM", "SPP", "CAISO", "ERCOT"].includes(p.publisher));
  const others = h.byPublisher.filter((p) => !grids.includes(p));
  return (
    <Brand>
      <p className="mb-4 text-sm">
        <Link href="/data#methods">Data</Link> / <code className="font-mono">docs/licenses.md</code>
      </p>
      <h1 className="mb-2 text-2xl">Licenses</h1>
      <p className="mb-8 max-w-3xl text-sm">
        What each publisher&apos;s own page allows, table by table: the sentence that allows or forbids redistribution, cut from the page as it was
        saved, with the address read and the day. A verdict is a session&apos;s reading of that sentence. It is not legal advice, and no lawyer has
        read it.
      </p>

      <Section title="Held: license needed" id="held">
        <p className="max-w-3xl text-sm">
          <strong className="font-normal tabular-nums">
            <Num check="lic|held|count" raw={h.count}>{h.count}</Num>
          </strong>{" "}
          tables are held from {day(h.from)}: each is flagged public, and a publisher whose sentence decides it asks for written permission or a paid
          license, and no permission is recorded for it.
        </p>
        <ul className="mt-3 max-w-3xl list-disc pl-5 text-sm">
          <li>A number read from a held table is not shown. In its place the site writes &ldquo;license needed&rdquo;, with the publishers in the hover.</li>
          <li>
            A table decided only by grid operators is held row by row: the rows of the grids that ask for permission are held, and the others are shown,
            as the price board holds PJM&apos;s prices. A table decided by anyone else (a news outlet, an operator&apos;s own site) is held whole.
          </li>
          <li>A held table is not offered as a download on the site, and the chat over the warehouse states no figure from a held table or a held row.</li>
          <li>
            The hold ends for a table when a permission is recorded in its row of{" "}
            <a href={repo("warehouse/metadata/license_status.csv")}>license_status.csv</a>, by a person.
          </li>
        </ul>
        <div className="mt-4 overflow-x-auto">
          <table className="border-collapse text-sm">
            <thead>
              <tr className="border-b border-rule text-left text-xs text-muted">
                <th className="py-1 pr-6 font-normal">Publisher whose sentence decides</th>
                <th className="py-1 pr-3 text-right font-normal">Held tables</th>
              </tr>
            </thead>
            <tbody>
              {[...grids, ...others].map((p) => (
                <tr key={p.publisher} className="border-b border-rule/60">
                  <td className="py-1 pr-6">{p.publisher}</td>
                  <td className="py-1 pr-3 text-right tabular-nums">
                    <Num check={`lic|held|pub|${p.publisher}`} raw={p.tables}>{p.tables}</Num>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-2 max-w-3xl text-xs text-muted">
          A table decided by several publishers counts under each. Source: <a href={repo("warehouse/metadata/license_status.csv")}>license_status.csv</a>,
          written by <code className="font-mono">scripts/licenses.py status</code> from the verdicts below.
        </p>
      </Section>

      <Section title="Permission asked" id="permission">
        <p className="max-w-3xl text-sm">
          Four letters were drafted on 20 October 2026, for Samuel Enrique to send. None had been sent when this page was written; a
          permission granted is recorded in <a href={repo("warehouse/metadata/license_status.csv")}>license_status.csv</a> and ends the hold it covers.
        </p>
        <ul className="mt-3 max-w-3xl list-disc pl-5 text-sm">
          {LETTERS.map((l) => (
            <li key={l.publisher}>
              <strong className="font-normal">{l.publisher}</strong>: {l.asks} (<a href={repo(l.file)}>the draft</a>).
            </li>
          ))}
        </ul>
        <p className="mt-2 max-w-3xl text-xs text-muted">
          ISO-NE&apos;s page names info@iso-ne.com for permission; a draft to it, of 12 October 2026, is{" "}
          <a href={repo("docs/reviews/isone-permission-email.md")}>here</a>, also not sent.
        </p>
      </Section>

      <Section title="Sources whose own page allows the ERW" id="permissive">
        <p className="max-w-3xl text-sm">
          <Num check="lic|verdict|both|count" raw={both.length}>{both.length}</Num> publishers&apos; sentences allow the ERW as it is (an open research
          project that sells nothing) and would allow it if it sold anything. The ERW publishes their tables, names the publisher and the report in every
          table&apos;s header and on the <Link href="/terms">terms page</Link>, and gives the credit each one asks for.
        </p>
        <ul className="mt-3 max-w-3xl list-disc pl-5 text-sm">
          {both.map((v) => (
            <li key={v.key}>
              <strong className="font-normal">{v.key}</strong>
              {v.note ? <span className="text-muted">: {v.note}</span> : null}
            </li>
          ))}
        </ul>
        <p className="mt-4 max-w-3xl text-sm">
          <Num check="lic|verdict|today_only|count" raw={todayOnly.length}>{todayOnly.length}</Num> more allow the ERW as it is today and would need
          written permission if it sold anything; their tables are public while the ERW sells nothing.
        </p>
        <ul className="mt-3 max-w-3xl list-disc pl-5 text-sm">
          {todayOnly.map((v) => (
            <li key={v.key}>
              <strong className="font-normal">{v.key}</strong>
              {v.note ? <span className="text-muted">: {v.note}</span> : null}
            </li>
          ))}
        </ul>
        <p className="mt-2 max-w-3xl text-xs text-muted">
          Source: <a href={repo("warehouse/metadata/license_verdicts.csv")}>license_verdicts.csv</a>, the columns verdict and if_commercial.
        </p>
      </Section>

      <Section title="The record" id="record">
        {DOCS.licenses ? (
          <article className="prose-erw max-w-none overflow-x-auto" dangerouslySetInnerHTML={{ __html: render(DOCS.licenses, "docs/licenses.md") }} />
        ) : (
          <p className="text-sm text-muted">The record is not in this build&apos;s content.</p>
        )}
      </Section>
    </Brand>
  );
}
