import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/SiteLink";  // session 67: every link passes the release gate
import { Brand } from "@/components/Brand";
import { Fold, ToolHeader, ToolPage, ToolSection } from "@/components/tool/ToolPage";
import { FindingCard } from "@/components/analysis/FindingCard";
import { CardChart } from "@/components/analysis/CardChart";
import { RequestForm } from "@/components/analysis/RequestForm";
import { ImpactForm } from "@/components/analysis/ImpactForm";
import { ScannerFound } from "@/components/analysis/ScannerFound";
import { RequestFlow } from "@/components/analysis/RequestFlow";
import { Library } from "@/components/research/Library";
import { ofTheFlow } from "@/lib/analysisflow";
import { DOCS, analysisWeeks, digestChartDays, digestDates, weeklyWeeks } from "@/lib/markdown";
import { METHOD, SUPERSEDED, loadCards, loadCatalogue } from "@/lib/findings";
import { GRIDS, NO_GRID, OTHER_TOPIC, TOPIC_RULES, filesHeld, gridLabel, gridsOf, newestChartWeek, roundupChart, topicLabel, topicsOf } from "@/lib/research";
import { ChartOfWeekView } from "./view";

export const revalidate = 3600;
export const metadata: Metadata = { title: "Research" };

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
//
// Session 238 (the owner's task of 12 October 2026): the page is Research, at /research; /analysis and every address
// under it redirect here (next.config.ts). Its order, his: the request form; today's chart (the Digest's daily chart,
// the newest held: docs/digest/charts/, session 232); this week's chart (the newest Roundup's: a finding's card when one
// was chosen for that Roundup, else the rule's pick); the findings library, one card a screen with a card index and a
// filter by grid and by topic (components/research/Library.tsx; how a card's grids and topics are read from its own
// data: lib/research.ts); the archive of every daily and weekly chart, last. Nothing the page showed is dropped: the
// week's results by the rule are folded under this week's chart, the scanner's group closes the library. The request
// flow sends and stores what it did. The page takes the brand (components/Brand.tsx, app/tokens.css): its sections are
// the shared tool components, its own markup carries class names the brand's file styles, and the charts are drawn in
// the tokens (data-chart-tokens, components/echarts.ts).
const day = (d: string) => new Date(`${d}T00:00:00Z`).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });

export default function ResearchPage() {
  const weeks = analysisWeeks();
  const a = DOCS.analysis;
  const all = loadCards();
  const cards = all.filter((c) => !(c.id in SUPERSEDED));                       // the current cards; a superseded one is linked under its successor
  const earlier = (id: string) => all.filter((c) => SUPERSEDED[c.id] === id);
  const catalogue = loadCatalogue();
  const impact = catalogue.find((c) => c.id === "impact_study");
  const defaults = Object.fromEntries(all.filter((c) => c.card_id === c.id && catalogue.some((e) => e.id === c.id)).map((c) => [c.id, c]));

  // today's chart: the newest day's record and picture the Digest's chart-maker left
  const days = digestChartDays();
  const charts = DOCS.digest_charts ?? {};
  const today = days.length ? charts[days[0]] : null;
  const digests = new Set(digestDates());

  // this week's chart: the newest Roundup's
  const week = newestChartWeek();
  const wk = week ? roundupChart(week) : null;
  const ruleChart = week ? a.weeks[week] : undefined;
  const res = week ? a.results[week] : undefined;
  const roundups = new Set(weeklyWeeks());

  // the library: each card with the grids and topics its own data names
  const items = cards.map((c) => ({
    id: c.card_id, title: c.title, grids: gridsOf(c), topics: topicsOf(c),
    node: (
      <>
        <p className="card-filed" data-card-filed={c.card_id}>
          Grid: {gridsOf(c).map(gridLabel).join(", ")}. Topic: {topicsOf(c).map(topicLabel).join(", ")}.
        </p>
        <FindingCard card={c} held={filesHeld(c)} fold />
        {earlier(c.id).map((old) => (
          <p key={old.card_id} className="mt-1 text-xs text-muted" data-superseded={old.card_id}>
            The earlier single-grid card, kept at its own address: <Link href={`/research/card/${old.card_id}`}>{old.title}</Link>.
          </p>
        ))}
      </>
    ),
  }));
  const gridChoices = [...GRIDS, NO_GRID].filter((g) => items.some((i) => i.grids.includes(g.id))).map(({ id, label }) => ({ id, label }));
  const topicChoices = [...TOPIC_RULES, OTHER_TOPIC].filter((t) => items.some((i) => i.topics.includes(t.id))).map(({ id, label }) => ({ id, label }));

  return (
    <Brand>
      <ToolPage>
        <div data-chart-tokens="1" data-research="1">
          <ToolHeader title="Research"
            lead={<>
              Ask the warehouse for an analysis, see today&apos;s chart and this week&apos;s, and read the findings: each a question, one chart that
              compares, the before and after numbers, the why, and a method footnote. Every number on a card is checked against the code that
              computed it, and each card downloads its data, its Stata do-file and its Python file. <Link href={METHOD}>Method note</Link>.
            </>} />
          <nav className="page-index" aria-label="On this page">
            <a href="#ask">Ask for an analysis</a>
            <a href="#today">Today&apos;s chart</a>
            <a href="#week">This week&apos;s chart</a>
            <a href="#library">Findings library</a>
            <a href="#archive">Chart archive</a>
          </nav>

          <ToolSection title="Ask for an analysis" id="ask" note="Two steps: what to analyze, then how to show it. A request waits in a queue and runs on the data machine.">
            <RequestFlow catalogue={catalogue} templates={ofTheFlow(a.templates)} gallery={ofTheFlow(a.gallery.templates)} computedAt={a.gallery.computed_at} cards={defaults}
              impactForm={impact ? <ImpactForm entry={impact} /> : null} />
          </ToolSection>
          <ToolSection title="Requests" id="requests">
            <RequestForm catalogue={catalogue} listOnly />
          </ToolSection>

          <ToolSection title="Today's chart" id="today">
            {today ? (
              <figure className="lead-chart" data-today-chart={today.date}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={`/digest-charts/${today.image}`} alt={`${today.title}. ${today.fact}`} width={1600} height={900} loading="lazy" />
                <figcaption>
                  <p className="lead-date">{day(today.date)}</p>
                  <h3>{today.title}</h3>
                  <p className="lead-fact" data-today-fact="1">{today.fact}</p>
                  <p className="lead-source text-xs text-muted" data-today-source="1">
                    Source: {today.source ? <>{today.source}, </> : null}ERW table <code className="font-mono">{today.table}</code>. The Digest&apos;s chart of the day, drawn by
                    code from the scanner&apos;s strongest flag of the day ({today.rule ? `rule: ${today.rule}` : "rule not recorded"}); <Link href="/data/methods/automated_analysis_scanner">method</Link>.
                    {today.proof ? " This picture is a proof: it was drawn to show the form, and no Digest has carried it yet." : null}
                    {digests.has(today.date) ? <> <Link href={`/digest/${today.date}`}>The Digest of {day(today.date)}</Link>.</> : null}
                  </p>
                </figcaption>
              </figure>
            ) : (
              <p className="text-sm text-muted" data-today-chart="none">No daily chart is held yet (docs/digest/charts/ is empty).</p>
            )}
          </ToolSection>

          <ToolSection title={week ? `This week's chart, ${week}` : "This week's chart"} id="week">
            {wk?.card ? (
              <figure className="lead-chart" data-week-chart={wk.week} data-week-card={wk.card.card_id}>
                <div>
                  <CardChart spec={wk.card.chart} label={wk.card.title} height={360} />
                </div>
                <figcaption>
                  <p className="lead-date">Chosen for the Roundup of {wk.week}</p>
                  <h3>{wk.card.title}</h3>
                  <p className="lead-fact">{wk.card.subtitle}</p>
                  <ul className="lead-numbers">
                    {wk.card.callouts.map((c, i) => (
                      <li key={i}>{c.label}: <span className="font-mono">{c.before.text}</span> ({c.before.period}), <span className="font-mono">{c.after.text}</span> ({c.after.period}){c.unit ? ` ${c.unit}` : ""}</li>
                    ))}
                  </ul>
                  <p className="lead-source text-xs text-muted">
                    {wk.card.source_line} <Link href={`/research/card/${wk.card.card_id}`}>The card, with its data, its Stata do-file and its Python file</Link>.
                    {roundups.has(wk.week) ? <> <Link href={`/roundup/${wk.week}`}>The Roundup of {wk.week}</Link>.</> : null}
                    {ruleChart ? <> <Link href={`/research/${wk.week}`}>The rule&apos;s own pick of the week</Link>.</> : null}
                  </p>
                </figcaption>
              </figure>
            ) : ruleChart ? (
              <div data-week-chart={week} data-week-card="rule">
                <ChartOfWeekView c={ruleChart} />
              </div>
            ) : (
              <p className="text-sm text-muted" data-week-chart="none">
                {wk?.chosen ? "The Roundup of this week chose a finding whose card is not held here." : "No chart of the week is held yet (docs/analysis/ is empty)."}
              </p>
            )}
            {res ? (
              <Fold title={`This week's results by the rule, ${week}`}>
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
              </Fold>
            ) : null}
          </ToolSection>

          <ToolSection title="Findings library" id="library">
            <p className="sub-note text-xs text-muted" data-library-rule="1">
              One card a screen. A card&apos;s grids are the grid names its own tables, inputs and chart carry (a grid the card lists as not held is
              left out); its topics are the kinds of table it read. Neither is a judgment of the finding. A filtered view keeps its address.
            </p>
            {cards.length === 0 ? (
              <p className="text-sm text-muted" data-finding-cards="0">no card yet: no finding has run (data/findings/ is empty).</p>
            ) : (
              <Library items={items} grids={gridChoices} topics={topicChoices} />
            )}
            <h3 className="sub-title">Found by the scanner</h3>
            <ScannerFound />
          </ToolSection>

          <ToolSection title="Chart archive" id="archive" note="Every daily chart and every weekly chart held, newest first. A daily chart opens its picture; a week opens its page.">
            <h3 className="sub-title">Daily charts, {days.length}</h3>
            {days.length === 0 ? (
              <p className="text-sm text-muted" data-archive-daily="0">no daily chart is held yet (docs/digest/charts/ is empty).</p>
            ) : (
              <ul className="chart-archive" data-archive-daily={days.length}>
                {days.map((d) => (
                  <li key={d}>
                    <a href={`/digest-charts/${charts[d].image}`} data-archive-day={d}>
                      <span className="archive-date">{d}</span>
                      <span className="archive-title">{charts[d].title}{charts[d].proof ? " (proof)" : ""}</span>
                    </a>
                    <span className="archive-fact">{charts[d].fact.split(": ")[0]}</span>
                  </li>
                ))}
              </ul>
            )}
            <h3 className="sub-title">Weekly charts, {weeks.length}</h3>
            {weeks.length === 0 ? (
              <p className="text-sm text-muted" data-archive-weekly="0">no week has been analysed yet (docs/analysis/ is empty).</p>
            ) : (
              <ul className="chart-archive" data-archive-weekly={weeks.length}>
                {weeks.map((w) => {
                  const chosen = roundupChart(w);
                  return (
                    <li key={w}>
                      <Link href={`/research/${w}`}><span className="archive-date">{w}</span><span className="archive-title">{a.weeks[w].title}</span></Link>
                      {chosen.card
                        ? <span className="archive-fact">The Roundup carried a finding: <Link href={`/research/card/${chosen.card.card_id}`}>{chosen.card.title}</Link></span>
                        : <span className="archive-fact">The rule&apos;s pick of the week</span>}
                    </li>
                  );
                })}
              </ul>
            )}
          </ToolSection>
        </div>
      </ToolPage>
    </Brand>
  );
}
