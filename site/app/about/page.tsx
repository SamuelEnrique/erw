import type { Metadata } from "next";
import { Brand } from "@/components/Brand";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import site from "@/data/site.json";
import { GLOSSARY, glossaryId } from "@/lib/glossary";
import { DOCS } from "@/lib/markdown";
import { GROUPS } from "@/lib/pages";
import { gated } from "@/lib/release";

// Session 77: the two tools added in review by sessions 72 and 75 are named here, greyed, without their descriptions,
// for as long as they are in review. Once a page is live in lib/release.ts its description shows again by itself.
const NAME_ONLY_IN_REVIEW = ["/shoulder", "/storage/buildout", "/contracts", "/storage/owners", "/battery/customer"];  // session 83: and each tool added in review since
const nameOnly = (href: string) => NAME_ONLY_IN_REVIEW.includes(href) && gated(href);

export const metadata: Metadata = { title: "About" };

export default function About() {
  return (
    <Brand>
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
      <h2 id="digest" className="mb-2 mt-6 text-xl">How the digest and ERW&apos;s Roundup are made</h2>
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
        {/* Session 532: the four paragraphs below say what warehouse/news/brief.py does since session 470 (tests/test_session470.py);
            each claim names, in a comment beside it, the function that does it. */}
        <p>
          <strong>Sections.</strong> An issue has its top 10 stories, up to three more for each group of sectors, and AI and power; a story is shown
          in one section only, the first that takes it.{/* brief.py select */} AI and power takes up to five stories that the scorer rated 7 or more
          for AI&apos;s demand for power and 5 or more for significance, so commentary and minor items are not in it.{/* brief.py select, AI_MIN_SIG = 5 */}
        </p>
        <p>
          <strong>One event once.</strong> The scorer groups stories only within one batch, so one event can reach an issue as two clusters. Two
          clusters are one event when they name a party in common, are filed in the same sector, and either their lead titles share most of their
          words or they share an amount (a sum of USD 1 million or more, or a capacity of 10 MW or more).{/* brief.py same_event */} The
          lower-ranked of the two is left out before the sections are filled, so the top 10 still holds ten stories.{/* brief.py one_per_event */} A
          story is also dropped when its headline or any of its links is already in the issue, and the top stories are numbered again; the run log
          names each story dropped.{/* brief.py unique_items, without_repeats, drop_repeated_items */}
        </p>
        <p>
          <strong>Not the same story twice in a week.</strong> A story that a digest of the seven days before printed is left out: a link in common,
          or a party named again with either an amount that issue printed or most of its headline&apos;s words.{/* brief.py earlier_issues (days=7), repeat_of, not_shown_before */}{" "}
          It comes back only when it brings a sum of money none of those issues printed, such as a price disclosed after the deal.{/* brief.py not_shown_before */}{" "}
          The Roundup leaves out, in the same way, the stories the previous week&apos;s Roundup printed.{/* roundup.py main: brief.not_shown_before on the previous Roundup */}
        </p>
        <p>
          <strong>Links.</strong> A top story links up to three of its sources and a story in the other sections its first, each address
          once.{/* brief.py build_clusters (links[:3]), main (links[:1]) */} The ERW follows a Google News link once to reach the outlet; when it
          cannot, the link stays a Google News address and says so, &ldquo;(via Google News)&rdquo;, in the digest, the Roundup and the digest&apos;s
          email.{/* ingest.py resolves the address; brief.py link_text; email_digest.py story_list */}
        </p>
        <p>
          <strong>Numbers.</strong> Every number in the numbers section is read from the ERW&apos;s tables through its Python package, and each names its
          table in the section&apos;s footnotes. A day-ahead average is the mean of the 24 hourly prices of the grid&apos;s own operating day, rounded half
          up to cents. The short summary above them is written by the model under a literal check: every number in it must appear
          in the section, or the summary is regenerated once and otherwise left out. On this site each figure carries the table and key it came from:
          scripts/check-values.mjs compares it with the live set, and scripts/check_digest.py traces every Digest of the archive to the warehouse. Since
          21 October 2026 a figure from a table whose publisher asks for permission reads &ldquo;license needed&rdquo;, as it does on every page; so does the
          summary when it names one, and so do the stories, which come from the news index.
        </p>
        <p>
          <strong>Schedule.</strong> The digest covers the 24 hours before it is written, Monday to Friday, by the daily run that starts at 14:00 UTC;
          there is no weekend issue. A day without a digest, before it is written or when none was, says so on its page and shows no other day&apos;s.
          ERW&apos;s Roundup covers an ISO week (Monday to Sunday, UTC), opens with the weekend&apos;s top stories, and is written and sent on Sundays at
          23:00 UTC (4 PM Pacific). It was called Energy Week, on Mondays, until session 23.
        </p>
        <p>
          <strong>Chart of the day.</strong> Since 13 October 2026 each digest carries a chart drawn by code, with no model and no person choosing it: the
          strongest flag of the day&apos;s scan of the warehouse that no digest has shown (<Link href="/data/methods/automated_analysis_scanner">how the chart
          is chosen</Link>). Its figures are its table&apos;s, as its record holds them.
        </p>
        <p>
          <strong>Fun fact and chart of the week.</strong> Each digest ends with a fun fact: always an energy fact first (a number from the warehouse,
          a piece of energy history, or a quirk of how the system works), sometimes with a second half. A number must match the warehouse exactly, and
          a history or word-origin claim must be found, word for word, in a stored copy of its source (Wikipedia or EIA), in the source's own words; a fact that
          fails is dropped and the digest ships without one. The Roundup carries the chart of the week, picked by a fixed rule from the Automated
          Analysis templates (<a href="/research">/research</a>).
        </p>
      </div>

      <h2 className="mb-2 mt-6 text-xl">The platform</h2>
      <p className="mb-6 text-sm leading-relaxed">
        The ERW is the data layer of an energy intelligence platform of {DOCS.platform.total} tools for enthusiasts, investors, researchers, traders
        and educators. Today {DOCS.platform.yes + DOCS.platform.partial} of them have a working data layer ({DOCS.platform.yes} complete,{" "}
        {DOCS.platform.partial} partial), {DOCS.platform.no} are not built and {DOCS.platform.planned} are planned. The list, with each tool&apos;s tables and
        gaps, is <a href={`${site.repository}/blob/main/docs/platform-tools.md`}>docs/platform-tools.md</a>.
      </p>
      {/* session 1123: Ask's rule and its evaluation's score, with the date it was measured (docs/methods/ask.md) */}
      <p className="mb-6 text-sm leading-relaxed" data-about-ask="1">
        <strong>Ask the warehouse.</strong> The question-answering tool states no number a query of the warehouse did not return: every figure of an
        answer is checked against what its tools read, in its unit, and an answer that fails twice says the warehouse does not hold that figure (<Link href="/data/methods/ask">its
        method</Link>). Its evaluation: 17 of 30 hard questions right when last asked, on 20 October 2026, and 14 of 30 when those answers are graded
        under the license hold of 21 October; the wrong answers wait on three rulings on units and on how the questions are scored, not on the figures.
      </p>
      <h2 className="mb-2 mt-6 text-xl">The site</h2>
      <dl className="mb-6 text-sm">
        {GROUPS.map((g) => (
          <div key={g.label} className="mb-3">
            <dt className="text-xs uppercase tracking-wide text-muted">{g.label}</dt>
            {/* session 203: a menu's sub-group (Economics: the five tools of Infrastructure Economics; Grid: the seven grid pages) follows its pages */}
            {[...g.pages, ...(g.sub?.pages ?? [])].map((p) => (
              <dd key={p.href} className="ml-0">
                {/* session 423: a name alone on its line is a target of its own, 24 px tall (WCAG 2.2, 2.5.8: two such lines
                    side by side, /battery/customer and /shoulder, met at 18 px); a name followed by its line is inline in text */}
                <Link href={p.href} className={nameOnly(p.href) ? "inline-flex min-h-6 items-center" : undefined}>{p.label}</Link>{nameOnly(p.href) ? null : <>: {p.line}</>}
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
    </Brand>
  );
}
