import type { Metadata } from "next";
import Link from "next/link";
import site from "@/data/site.json";
import { GLOSSARY, glossaryId } from "@/lib/glossary";
import { GROUPS } from "@/lib/pages";

export const metadata: Metadata = { title: "About" };

export default function About() {
  return (
    <article className="max-w-3xl">
      <h1 className="mb-4 text-3xl">About</h1>
      <p className="mb-4 leading-relaxed">
        The Energy Research Warehouse (ERW) is the live, citable record of the US energy system: prices, flows, projects, deals and policy across power,
        natural gas, oil, nuclear, renewables, storage and transmission, with the global prices and events that move US markets. AI&apos;s demand for
        power is the sharpest current lens on that system, not its boundary. It is built as a Stanford independent study. Its design follows the{" "}
        <a href="https://github.com/ben-domingue/irw">Item Response Warehouse</a> (IRW), whose owner allowed the ERW to copy its infrastructure and
        documents: one connector per source, a small number of standard table shapes so that sources can be joined and compared, a validator every table
        must pass, a provenance header on every table naming the source report and the time it was retrieved, and a versioned store of record on Redivis
        that only a human releases. Every table carries a license from its sources: a table is public only if all of its sources allow republication,
        and a table derived from other tables takes the most restrictive license among them. Tables licensed for internal use only, such as PJM market
        data, stay in the warehouse and are never shown on this site.
      </p>
      <h2 id="digest" className="mb-2 mt-6 text-xl">How the digest and the Energy Roundup are made</h2>
      <div className="mb-6 space-y-2 text-sm leading-relaxed">
        <p>
          <strong>Stories.</strong> The ERW reads energy news feeds (the outlets are listed in the source registry) and keeps each story&apos;s title,
          summary and link, never its body. Titles and summaries are the outlets&apos; text, kept for scoring and linking; they are not republished.
        </p>
        <p>
          <strong>Scoring.</strong> A model (the newest Sonnet-class Claude model the API lists) scores every story against a fixed rubric
          (<a href={`${site.repository}/blob/main/warehouse/news/rubric.md`}>warehouse/news/rubric.md</a>): significance from 0 to 10 across the whole
          energy industry, a sector, a region, and a one-line reason. Stories about the same event are grouped into one cluster, and clusters are ranked by
          their highest significance. The ranking decides the order; the score itself is not shown.
        </p>
        <p>
          <strong>Headlines.</strong> The model writes each cluster&apos;s headline, using only words and figures in the stories&apos; titles, summaries and
          scored fields; a headline&apos;s numbers are checked against them. The line under each headline is the story&apos;s own scored reason, with its
          sources linked.
        </p>
        <p>
          <strong>Numbers.</strong> Every number in the numbers section is read from the ERW&apos;s tables through its Python package, and each names its
          table in the section&apos;s footnotes. The short summary above them is written by the model under a literal check: every number in it must appear
          in the section, or the summary is regenerated once and otherwise left out.
        </p>
        <p>
          <strong>Schedule.</strong> The digest covers the 24 hours before it is written, Monday to Friday at 14:00 UTC; there is no weekend issue.
          The Energy Roundup covers an ISO week (Monday to Sunday, UTC), opens with the weekend&apos;s top stories, and is written and sent on Sundays at
          23:00 UTC (4 PM Pacific). It was called Energy Week, on Mondays, until session 23.
        </p>
        <p>
          <strong>Fun fact and chart of the week.</strong> Each digest ends with a fun fact: always an energy fact first (a number from the warehouse,
          a piece of energy history, or a quirk of how the system works), sometimes with a second half. A number must match the warehouse exactly, and
          a history or word-origin claim must be found, word for word, in a stored copy of its source (Wikipedia or EIA), in the source's own words; a fact that
          fails is dropped and the digest ships without one. The Roundup carries the chart of the week, picked by a fixed rule from the Automated
          Analysis templates (<a href="/analysis">/analysis</a>).
        </p>
      </div>

      <h2 className="mb-2 mt-6 text-xl">The site</h2>
      <dl className="mb-6 text-sm">
        {GROUPS.map((g) => (
          <div key={g.label} className="mb-3">
            <dt className="text-xs uppercase tracking-wide text-muted">{g.label}</dt>
            {g.pages.map((p) => (
              <dd key={p.href} className="ml-0">
                <Link href={p.href}>{p.label}</Link>: {p.line}
              </dd>
            ))}
          </div>
        ))}
      </dl>
      <h2 id="glossary" className="mb-2 mt-6 text-xl">Glossary</h2>
      <dl className="mb-6 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
        {Object.entries(GLOSSARY).map(([t, d]) => (
          <div key={t} id={glossaryId(t)} className="contents">
            <dt className="font-mono">{t}</dt>
            <dd>{d}</dd>
          </div>
        ))}
      </dl>
      <p className="text-sm text-muted">
        Code, data standard and session logs: <a href={site.repository}>{site.repository.replace("https://", "")}</a>.
      </p>
    </article>
  );
}
