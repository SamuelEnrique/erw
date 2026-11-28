// Energy Research Warehouse (ERW) site, session 8014 (chain 581, part B): the decisions of "Every state", in the form
// of the industry page's (app/industry/Decisions.tsx): one fold at the foot of the page, one line a choice that moves
// what the page shows, and on hover, tap or focus its default, its source and the session that made it.
// docs/methods/states_page.md, "Decisions (session 8014)", carries the same list; tests/test_session8014_states.py holds
// the two to one list.
import { Tip } from "@/components/tool/ToolPage";

export type StatesDecision = { key: string; text: string; session: string; def: string; source: string };

export const STATES_DECISIONS: StatesDecision[] = [
  { key: "as-published", session: "session 8014",
    text: "Every figure is EIA's or the Census Bureau's own as the files hold it. The page sums months into years and twelve-month windows, and computes only the shares, the revenue and the population shares it names. The ERW fills, scales and estimates nothing. EIA's monthly figures hold EIA's own estimates (Form EIA-861M's sales include its estimate for the utilities it does not survey each month: Texas's 2024 months sum to 2.07 percent more than the annual form's sales), and EIA revises its newest months.",
    def: "The publishers' figures as published.",
    source: "site/data/states/, built by warehouse/derived/states_page.py from sixteen ERW tables (docs/methods/states_page.md)." },
  { key: "not-held", session: "session 8014",
    text: "A figure a source does not print for a place is drawn as \"not held\" with the reason on hover. It is never drawn as zero; a zero is a zero the source printed. A figure smaller than half the last digit shown prints as 0.0, 0.0% or $0.00 bn: Texas's transportation sales, 4,677 MWh in the twelve months, print as 0.0 TWh.",
    def: "\"not held\" with the reason on hover.",
    source: "The contract's rules, docs/state/page_files_states.md." },
  { key: "first-place", session: "session 8014",
    text: "The page opens on Texas, the largest generator of the fifty states, with no second place. Any state, the District of Columbia or the United States can be chosen, and a second beside it.",
    def: "Texas; no second place.",
    source: "The page's own choice, on the index's twelve-month generation." },
  { key: "twelve-months", session: "session 8014",
    text: "The headline figures and the sector table are the newest twelve months the file holds, summed; a year is shown only when all twelve of its months are held.",
    def: "The newest twelve months; whole years only.",
    source: "last12 and annual in each place's file." },
  { key: "revenue", session: "session 8014",
    text: "What a sector paid is EIA's sales times EIA's average price, month by month. EIA computes its average price as revenue over sales, so the product is EIA's revenue to within the price's rounding. The twelve months' price is that revenue over those sales.",
    def: "Sales times price.",
    source: "Form EIA-861M as the ERW's tables eia_retail_sales_monthly and eia_retail_electricity_prices hold it; the warehouse holds no state revenue column." },
  { key: "who-operates", session: "session 8014",
    text: "Who operates a state's grid is told by its people: each county counts whole for its primary balancing authority (the one whose utilities serve most of its customers in EIA-861), weighted by the Census Bureau's newest county population.",
    def: "Primary authority by county, by population.",
    source: "eia_county_region and census_county_population (docs/methods/county_population_and_regions.md)." },
  { key: "monthly", session: "session 8014",
    text: "No public source gives a state's generation by the hour. The page says so once and links to the Grid tool at the region of the state's largest authority, where the hourly picture is.",
    def: "Monthly, with the link.",
    source: "The chain's step B3." },
  { key: "opening-views", session: "session 8014",
    text: "The yearly chart of generation runs from 2001; the monthly charts open on the months from 2015, and any start from 2001 can be chosen; the share chart opens on natural gas; the price chart opens on homes. Each can be changed.",
    def: "Months from 2015; natural gas; homes.",
    source: "The page's own choice." },
  { key: "nominal", session: "session 8014",
    text: "Prices and money are in nominal dollars, as EIA prints them. Nothing is adjusted for inflation. EIA prints cents a kWh; the table holds USD per MWh; the page shows cents a kWh.",
    def: "Nominal; cents a kWh.",
    source: "Form EIA-861M." },
  { key: "places", session: "session 8014",
    text: "The fifty states, the District of Columbia and the United States as a whole. Puerto Rico has no file: of the tables the page reads, only the generation table and EIA-860M hold it. The United States' capacity, plants, planned and retiring generators are the fifty states' and the District's in EIA-860M, without Puerto Rico's 6,474 MW, as its generation and sales, EIA's national totals, are without Puerto Rico.",
    def: "52 places.",
    source: "site/data/states/index.json." },
];

export function StatesDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="states">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({STATES_DECISIONS.length}): each choice that moves what the page shows, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={STATES_DECISIONS.length}>
        {STATES_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-states-${d.key}`} label="this choice's default and source">
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
