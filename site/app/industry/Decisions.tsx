// Energy Research Warehouse (ERW) site, session 8012 (chain 505, part B1): the decisions of "Energy use by industry",
// in the form of the resource map's (app/resources/Decisions.tsx): one fold at the foot of the page, one line a choice
// that moves what the page shows, and on hover, tap or focus its default, its source and the session that made it.
// docs/methods/industry_page.md, "Decisions (session 8012)", carries the same list; tests/test_session8012_industry.py
// holds the two to one list.
import { Tip } from "@/components/tool/ToolPage";

export type IndustryDecision = { key: string; text: string; session: string; def: string; source: string };

export const INDUSTRY_DECISIONS: IndustryDecision[] = [
  { key: "as-published", session: "session 8012",
    text: "Every figure is EIA's own as the file holds it. The page sums only a year's twelve months, and computes only the shares and changes it names. Nothing is filled, scaled or estimated.",
    def: "EIA's figures as published.",
    source: "site/data/industry.json, built by warehouse/derived/industry_page.py from six ERW tables (docs/methods/industry_page.md)." },
  { key: "withheld", session: "session 8012",
    text: "A cell the 2022 survey prints no figure for is drawn as \"not held\", never as zero. EIA's codes for such a cell are * (an estimate under 0.5 in the table's unit), D (withheld to avoid disclosure), NA (not available) and Q (withheld, its relative standard error above 50 percent); the file does not keep which code a cell had, so the hover gives all four.",
    def: "\"not held\", with the four codes on hover.",
    source: "EIA, 2022 Manufacturing Energy Consumption Survey, the notes to Tables 3.2, 11.1 and 11.3." },
  { key: "whole-year", session: "session 8012",
    text: "A year's figure from the monthly series is the sum of its twelve months, written only when all twelve are held.",
    def: "Twelve months or no figure.",
    source: "yearSum and salesYear in site/lib/industry.ts." },
  { key: "first-two", session: "session 8012",
    text: "Industries A and B open on the two largest three-digit industries in the nation in 2022. States A and B open on the two largest by the industrial sector's total in the newest year.",
    def: "Chemicals and Petroleum and Coal Products; Texas and Louisiana in 2024.",
    source: "rankedIndustries and rankedStates in site/lib/industry.ts, on the file's own figures." },
  { key: "ranking", session: "session 8012",
    text: "The industries are ranked by their total fuel consumption in the chosen region, the states by the chosen source in the chosen year, largest first. An industry or a state with no figure stands last.",
    def: "Largest first, by the figure shown.",
    source: "The survey's three-digit industries (the file's ranked_3_digit); the State Energy Data System's states and the District of Columbia." },
  { key: "cases", session: "session 8012",
    text: "EIA's outlook opens on two of its eleven cases: the Counterfactual Baseline case and the High Electricity Demand case. Every case stands in the table under the chart.",
    def: "Case A Counterfactual Baseline, Case B High Electricity Demand.",
    source: "The Annual Energy Outlook 2026, which names no Reference case; the cases as the file lists them (outlook.cases)." },
  { key: "from-2015", session: "session 8012",
    text: "The monthly chart opens on the months from 2015; the file holds them from January 1973, and any start can be chosen.",
    def: "From 2015.",
    source: "The Monthly Energy Review, Table 2.4, as the file holds it." },
  { key: "nominal", session: "session 8012",
    text: "Prices and expenditures are in nominal dollars, as the State Energy Data System gives them. Nothing is adjusted for inflation.",
    def: "Nominal dollars.",
    source: "EIA, State Energy Data System, the industrial sector's prices and expenditures." },
];

export function IndustryDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="industry">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({INDUSTRY_DECISIONS.length}): each choice that moves what the page shows, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={INDUSTRY_DECISIONS.length}>
        {INDUSTRY_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-industry-${d.key}`} label="this choice's default and source">
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
