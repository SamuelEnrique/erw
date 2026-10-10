import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { FindingCard } from "@/components/analysis/FindingCard";
import { RequestForm } from "@/components/analysis/RequestForm";
import { ImpactForm } from "@/components/analysis/ImpactForm";
import { ScannerFound } from "@/components/analysis/ScannerFound";
import { RequestFlow } from "@/components/analysis/RequestFlow";
import { Section } from "@/components/Section";
import { DOCS, analysisWeeks } from "@/lib/markdown";
import { METHOD, SUPERSEDED, loadCards, loadCatalogue } from "@/lib/findings";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Automated Analysis" };

// Session 23: Automated Analysis (platform tool 26). warehouse/analysis/run.py runs every template weekly and picks
// the chart of the week by rule. Session 170: the page is rebuilt around finding cards (warehouse/analysis/findings/):
// each a question put to the warehouse, answered with one comparing chart, before-and-after callouts, a why paragraph
// and a method footnote, with its data, Python and Stata do-file to download. A person picks a finding and its inputs;
// the request waits in a queue and runs on the data machine. The chart of the week the code disowned (W40, a count of
// what the ERW had read) is no longer drawn here; each week's chart stays on its own page in the archive below.
// Session 181: two additions, the page's layout otherwise as it was. "Found by the scanner": the drafts a person
// approved at /internal/findings (public.scanner_drafts), read by the browser from /internal/findings/approved, which
// answers only the internal view; nothing appears before approval and a dismissed draft never does. "Impact of an
// event on a series": the impact study's own inputs (ImpactForm), a request like the others.
// The request flow (10 October 2026, the session after the scanner's): "Ask for a finding", the impact study's section
// and the template gallery are one flow in two steps (components/analysis/RequestFlow.tsx): what to analyze (the
// findings, the impact study and the ten weekly templates as analyses), then how to show it (a picker of chart forms,
// each drawn as an example, the analysis's own form preselected). The gallery's component is retired
// (app/_retired/analysis-gallery/); its nine public templates, every input they offered and the weekly files they
// read are in the flow, and the internal tenth is listed there. The two single-grid cards that the five-grid cards
// supersede (SUPERSEDED) leave the list of findings: each is linked under its five-grid card, stays at its own
// address, and is a choice of "Version" in the flow. The list of requests stands under the flow.
export default function AnalysisPage() {
  const weeks = analysisWeeks();
  const a = DOCS.analysis;
  const week = weeks[0];
  const res = week ? a.results[week] : undefined;
  const all = loadCards();
  const cards = all.filter((c) => !(c.id in SUPERSEDED));                       // the current cards; a superseded one is linked under its successor
  const earlier = (id: string) => all.filter((c) => SUPERSEDED[c.id] === id);
  const catalogue = loadCatalogue();
  const impact = catalogue.find((c) => c.id === "impact_study");
  const defaults = Object.fromEntries(all.filter((c) => c.card_id === c.id && catalogue.some((e) => e.id === c.id)).map((c) => [c.id, c]));
  return (
    <>
      <h1 className="mb-1 text-3xl">Automated Analysis</h1>
      <p className="mb-6 max-w-3xl text-sm text-muted">
        Findings from the warehouse, on demand: a question, one chart that compares, the before and after numbers, the why, and a method
        footnote. Every number on a card is checked against the code that computed it, and each card downloads its data, its Python and a
        Stata do-file. Ten chart templates still run every week; the chart of the week is the measure whose latest change ranks highest
        against its own earlier changes. To ask for an analysis, or to see one in another chart form, use the two steps
        under <a href="#ask">Ask for an analysis</a>. <Link href={METHOD}>Method note</Link>.
      </p>
      <Section title="Findings" aside={cards.length ? `${cards.length} card${cards.length === 1 ? "" : "s"}` : undefined}>
        {cards.length === 0 ? (
          <p className="text-sm text-muted" data-finding-cards="0">no card yet: no finding has run (data/findings/ is empty).</p>
        ) : (
          <div className="flex flex-col gap-10" data-finding-cards={cards.length}>
            {cards.map((c) => (
              <div key={c.card_id}>
                <FindingCard card={c} />
                {earlier(c.id).map((old) => (
                  <p key={old.card_id} className="mt-1 text-xs text-muted" data-superseded={old.card_id}>
                    The earlier single-grid card, kept at its own address: <Link href={`/analysis/card/${old.card_id}`}>{old.title}</Link>.
                  </p>
                ))}
              </div>
            ))}
          </div>
        )}
      </Section>
      <Section title="Found by the scanner">
        <ScannerFound />
      </Section>
      <Section title="Ask for an analysis" id="ask" aside="two steps: what to analyze, how to show it">
        <RequestFlow catalogue={catalogue} templates={a.templates} gallery={a.gallery.templates} computedAt={a.gallery.computed_at} cards={defaults}
          impactForm={impact ? <ImpactForm entry={impact} /> : null} />
      </Section>
      <Section title="Requests" id="requests">
        <RequestForm catalogue={catalogue} listOnly />
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
