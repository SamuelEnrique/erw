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
        {/* Session 811: the rules of sessions 801 to 806 (docs/reviews/periodicals-plan-2026-10-23.md), each with the function that holds it. */}
        <p>
          <strong>The line under the headline.</strong> It says the consequence in one sentence: no adjective of the list (massive, unprecedented,
          significant, major, critical, key, huge), no figure the headline already gives, a stop before the figures and the sources. The scorer is asked
          for that and the brief checks it: an adjective is cut, a second sentence is dropped, a figure the headline holds is taken out where the sentence
          still reads, and a line that cannot be mended is left out rather than invented.{/* brief.py why_check, why_line, why_fallback, detail */} Sums of
          money are written one way, &ldquo;USD 45 billion&rdquo;.{/* brief.py money_style */}
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
          <strong>One topic, one item.</strong> The top 10 holds at most one item a topic: a topic is the scorer&apos;s sector, or two sectors whose
          stories name a party in common and share two words of their titles.{/* brief.py same_topic, TOPIC_WORDS = 2 */} A later story of a topic
          already in the ten folds under that item as &ldquo;Also on this topic&rdquo;, with its publisher&apos;s title and its outlet, at most three an
          item; past three it waits for the sections below, so no story is lost.{/* brief.py one_per_topic, ALSO_MAX = 3, also_line */} The Roundup&apos;s
          weekend stories and its five of the week follow the same rule.{/* roundup.py main: brief.one_per_topic */}
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
          email.{/* ingest.py resolves the address; brief.py link_text; email_digest.py story_list */} The link&apos;s text is the outlet&apos;s name from
          the feed, never the address; the email&apos;s text part names the outlet alone where the address is Google&apos;s. An outlet whose stories ask for
          a license (the news index&apos;s hold since 21 October 2026, read from the license file) is named with no link, so the item shows the outlet and
          the title only.{/* brief.py licensed_outlets, source_text */}
        </p>
        <p>
          <strong>Numbers.</strong> Every number in the numbers section is read from the ERW&apos;s tables through its Python package, and each names its
          table in the section&apos;s footnotes. A day-ahead average is the mean of the 24 hourly prices of the grid&apos;s own operating day, rounded half
          up to cents. The section opens with what moved most: the five largest moves in percent among the main hubs&apos; day-ahead averages
          against the day before and EIA&apos;s spot closes against the close before them, each with its level and its change, and a reason only when
          a scored story of the day names that price; the move is the price board&apos;s.{/* brief.py numbers_today, MOVERS_N = 5, day_move, price_reason */}
          A price held for a license or paused is not ranked and says so, as are TTF and JKM, which are not held.{/* brief.py held_grids, NOT_HELD */}
          The table carries the day before and the change; the closes say how old they are; US48 demand&apos;s peak is set against the same weekday a
          year before where the warehouse holds it.{/* brief.py demand_lines */} The short summary above them is written by the model under a literal check: every number in it must appear
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
          is chosen</Link>). Since 22 October 2026 the candidates are ordered first by how much each belongs to the day&apos;s top ten stories (the sector
          the candidate&apos;s table belongs to, and the words its fact, table and series share with a story&apos;s title, reason and parties; the top story
          weighs ten times the tenth), and the sentence under the chart says which story it follows.{/* daily_chart.py relevance, choose */} Its figures
          are its table&apos;s, as its record holds them.
        </p>
        <p>
          <strong>Fun fact and chart of the week.</strong> Each digest ends with a fun fact: always an energy fact first (a number from the warehouse,
          a piece of energy history, or a quirk of how the system works), sometimes with a second half. A number must match the warehouse exactly, and
          a history or word-origin claim must be found, word for word, in a stored copy of its source (Wikipedia or EIA), in the source's own words; a fact that
          fails is dropped and the digest ships without one. The Roundup carries the chart of the week, picked by a fixed rule from the Automated
          Analysis templates (<a href="/research">/research</a>); since 22 October 2026 the section says which of the measures that moved in the week
          is most related to the week&apos;s top stories, with its finding, when it is not the one drawn.{/* roundup.py chart_relevance */}
        </p>
        <p>
          <strong>The week in five numbers.</strong> The Roundup opens with five figures, each traced to its table: the week&apos;s biggest price move in
          percent among the main hubs&apos; weekly means and EIA&apos;s closes a week apart; the US48 peak with its hour; the week&apos;s largest deal by US
          dollars from the deals table, by MW when none states dollars; the largest datacenter load first reported in the week; and the headline figure
          of the week&apos;s chart. A figure the warehouse does not hold is said missing. The highest real-time price of the week says its interval
          length, since the grids&apos; series differ in it.{/* roundup.py five_numbers, interval_words */}
        </p>
      </div>

      <h2 className="mb-2 mt-6 text-xl">The platform</h2>
      <p className="mb-6 text-sm leading-relaxed">
        The ERW is the data layer of an energy intelligence platform of {DOCS.platform.total} tools for enthusiasts, investors, researchers, traders
        and educators. Today {DOCS.platform.yes + DOCS.platform.partial} of them have a working data layer ({DOCS.platform.yes} complete,{" "}
        {DOCS.platform.partial} partial), {DOCS.platform.no} are not built and {DOCS.platform.planned} are planned. The list, with each tool&apos;s tables and
        gaps, is <a href={`${site.repository}/blob/main/docs/platform-tools.md`}>docs/platform-tools.md</a>.
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
