// Energy Research Warehouse (ERW) site, session 9000 (chain 601, part C): the decisions of the congestion page, in the
// form of the where-and-when view's (app/curtailment/where-when/Decisions.tsx). docs/methods/grid_congestion.md,
// "Decisions", carries the same reasoning; tests/test_session9000_congestion.py holds the page to its file.
import { Tip } from "@/components/tool/ToolPage";

export type CongestionDecision = { key: string; text: string; session: string; def: string; source: string };

export const CONGESTION_DECISIONS: CongestionDecision[] = [
  { key: "as-published", session: "session 9000",
    text: "The constraints, their shadow prices and the parts of the price are the operators' own, as published. The page counts hours, sums and averages them, and computes only the shares it names. It makes no estimate and gives no advice.",
    def: "The operators' figures as published.",
    source: "site/data/conditions/congestion.json, built by warehouse/derived/congestion_page.py (docs/methods/grid_congestion.md)." },
  { key: "operators", session: "session 9000",
    text: "SPP and CAISO are drawn. ERCOT publishes its shadow prices only on paths its robots file disallows; PJM, NYISO and ISO-NE are held by their terms; MISO is paused. Each is named with its reason on hover and no number.",
    def: "SPP and CAISO.",
    source: "docs/reviews/grid-conditions-sources-2026-11-20.md; docs/licenses.md; the owner's ruling of 6 November 2026." },
  { key: "names", session: "session 9000",
    text: "A constraint is named as the operator names it. Where CAISO lists one branch under several contingencies, each contingency is its own row. No constraint is placed on a map.",
    def: "The operator's own name.",
    source: "The operators' files." },
  { key: "sign", session: "session 9000",
    text: "SPP prints shadow prices as negative numbers, CAISO as positive. Ranks, means and highs use the size of the price.",
    def: "The size of the price.",
    source: "The operators' files; the page file's sign_rule." },
  { key: "cost", session: "session 9000",
    text: "\"Cost most\" ranks by the shadow price summed over the hours a constraint bound. No flow is published with the day-ahead shadow prices, so no dollar total is made.",
    def: "Summed shadow price.",
    source: "The page file's cost_rule." },
  { key: "share", session: "session 9000",
    text: "A month's or a year's congestion share is its mean congestion part over its mean LMP, times 100; none when the mean LMP is not above zero.",
    def: "Mean over mean.",
    source: "The page file's share_rule." },
  { key: "first", session: "session 9000",
    text: "The page opens on the first operator drawn, its newest year, the constraint whose shadow price summed highest that year, and the first of that operator's places, with no second place.",
    def: "SPP, the newest year.",
    source: "The page's own choice." },
  { key: "clock", session: "session 9000",
    text: "Hours of the day, months and years are each operator's own clock: Central for SPP, Pacific for CAISO. The dates a constraint first and last bound are UTC days, as the file stamps them: an SPP hour from 18:00 Central (19:00 in summer time), or a CAISO hour from 16:00 Pacific (17:00 in summer time), falls on the next UTC day. The newest year is not whole: it ends on the newest day held, which the page names.",
    def: "As each operator keeps time.",
    source: "The operating day of each file." },
];

export function CongestionDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="congestion">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({CONGESTION_DECISIONS.length}): each choice that moves what the page shows, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={CONGESTION_DECISIONS.length}>
        {CONGESTION_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-congestion-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
              <span className="block" data-decision-session={d.key}><strong>Made in:</strong> {d.session}.</span>
            </Tip>
          </li>
        ))}
      </ul>
    </details>
  );
}
