import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { AnalysisGallery } from "@/components/AnalysisGallery";
import { FindingCard } from "@/components/analysis/FindingCard";
import { RequestForm } from "@/components/analysis/RequestForm";
import { Section } from "@/components/Section";
import { DOCS, analysisWeeks } from "@/lib/markdown";
import { METHOD, loadCards, loadCatalogue } from "@/lib/findings";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Automated Analysis" };

// Session 23: Automated Analysis (platform tool 26). warehouse/analysis/run.py runs every template weekly and picks
// the chart of the week by rule. Session 170: the page is rebuilt around finding cards (warehouse/analysis/findings/):
// each a question put to the warehouse, answered with one comparing chart, before-and-after callouts, a why paragraph
// and a method footnote, with its data, Python and Stata do-file to download. A person picks a finding and its inputs;
// the request waits in a queue and runs on the data machine. The chart of the week the code disowned (W40, a count of
// what the ERW had read) is no longer drawn here; each week's chart stays on its own page in the archive below.
export default function AnalysisPage() {
  const weeks = analysisWeeks();
  const a = DOCS.analysis;
  const week = weeks[0];
  const res = week ? a.results[week] : undefined;
  const cards = loadCards();
  const catalogue = loadCatalogue();
  return (
    <>
      <h1 className="mb-1 text-3xl">Automated Analysis</h1>
      <p className="mb-6 max-w-3xl text-sm text-muted">
        Findings from the warehouse, on demand: a question, one chart that compares, the before and after numbers, the why, and a method
        footnote. Every number on a card is checked against the code that computed it, and each card downloads its data, its Python and a
        Stata do-file. Ten chart templates still run every week; the chart of the week is the measure whose latest change ranks highest
        against its own earlier changes. <Link href={METHOD}>Method note</Link>.
      </p>
      <Section title="Findings" aside={cards.length ? `${cards.length} card${cards.length === 1 ? "" : "s"}` : undefined}>
        {cards.length === 0 ? (
          <p className="text-sm text-muted" data-finding-cards="0">no card yet: no finding has run (data/findings/ is empty).</p>
        ) : (
          <div className="flex flex-col gap-10" data-finding-cards={cards.length}>
            {cards.map((c) => <FindingCard key={c.card_id} card={c} />)}
          </div>
        )}
      </Section>
      <Section title="Ask for a finding">
        <RequestForm catalogue={catalogue} />
      </Section>
      {res ? (
        <Section title={`This week's results, ${week}`} aside={<Link href={`/analysis/${week}`}>This week&apos;s chart</Link>}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-rule text-left text-xs text-muted">
                  <th className="py-1 pr-3">Template</th>
                  <th className="py-1 pr-3">Headline</th>
                  <th className="py-1 pr-3">Period</th>
                  <th className="py-1 pr-3 text-right">Value</th>
                  <th className="py-1 pr-3 text-right">Earlier values</th>
                  <th className="py-1 pr-3 text-right">Robust z</th>
                  <th className="py-1 text-right">Percentile</th>
                </tr>
              </thead>
              <tbody>
                {res.results.map((r) => (
                  <tr key={r.template} className="border-b border-rule align-top">
                    <td className="py-1 pr-3">
                      {r.title}
                      {r.template === res.picked ? <strong className="text-accent"> (picked)</strong> : null}
                    </td>
                    <td className="py-1 pr-3">{r.headline.label}</td>
                    <td className="py-1 pr-3 font-mono text-xs">{r.headline.period}</td>
                    <td className="py-1 pr-3 text-right">
                      {r.headline.value.toLocaleString("en-US")} {r.headline.unit}
                    </td>
                    <td className="py-1 pr-3 text-right">{r.history_n}</td>
                    <td className="py-1 pr-3 text-right">{r.notability_z ?? "not scored"}</td>
                    <td className="py-1 text-right">{r.percentile ?? ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-muted">
            The rule: only a measurement of the energy system competes (a count of what the ERW itself has collected is shown and never chosen);
            the statistic is the headline&apos;s change from the period it is compared with, ranked among the same measure&apos;s own earlier changes
            (the last 104 weekly or 36 monthly; at least 8), its score the share of them that were smaller; the period must be new and have ended
            within 100 days; the highest score wins, a tie going to the higher robust z. Internal templates (chokepoint transits) run on the
            warehouse&apos;s machines only.{" "}
            {res.skipped.length ? `Skipped this week: ${res.skipped.map((s) => `${s.template} (${s.reason})`).join("; ")}.` : null}
          </p>
        </Section>
      ) : null}
      <Section title="Template gallery">
        <AnalysisGallery gallery={a.gallery.templates} templates={a.templates.filter((t) => t.public)} />
        <p className="mt-3 text-xs text-muted">
          Each chart is computed by the warehouse&apos;s template code from public tables only, for every choice of its parameters, and served from that
          cache; the whole grid is recomputed every week{a.gallery.computed_at ? ` (last ${a.gallery.computed_at.slice(0, 10)})` : ""}.
        </p>
      </Section>
      <Section title="Archive: the chart of each week">
        {weeks.length === 0 ? (
          <p className="text-sm text-muted">no week has been analysed yet (docs/analysis/ is empty).</p>
        ) : (
          <ul className="text-sm">
            {weeks.map((w) => (
              <li key={w}>
                <Link href={`/analysis/${w}`}>{w}</Link>: {a.weeks[w].title}
              </li>
            ))}
          </ul>
        )}
      </Section>
    </>
  );
}
