import { Tip } from "@/components/tool/ToolPage";

// Session 7508 (chain 304): the choices the demand growth explorer's figures rest on, in the form of the tools at the
// done line (components/tool/DecisionsBlock.tsx, with the default and the source on hover that chains 303 and 304 gave
// it): one line a choice, its default and its source in a tip, no grey text. The list is this page's own file, not
// lib/decisions.ts or a file of components/explore/, which other tools share. Words only: the page does no arithmetic
// (every number is one row of eia930_demand_growth), so no choice is editable in place; each is a choice of the table's
// builder or of which row the page reads. docs/methods/demand_growth.md, "The tool as a reader meets it", lists the
// same keys, and tests/test_session7508_demand_growth.py holds the two to one list.
export type DemandGrowthDecision = { key: string; text: string; def: string; source: string };

export const DEMAND_GROWTH_DECISIONS: DemandGrowthDecision[] = [
  { key: "base-year",
    text: "Growth is measured from 2019: a year's demand over 2019's, less one, in percent.",
    def: "2019, the last whole year before the pandemic and the first whole year the warehouse holds for every area. Another base year gives another figure: ERCOT's average demand grew 27.22 percent from 2019 to 2025 and 5.57 percent from 2024 to 2025.",
    source: "Session 97; docs/methods/demand_growth.md. The growth on the year before is in the grid's table year by year." },
  { key: "weather",
    text: "Weather is not removed: a year's demand is what was metered that year.",
    def: "As metered. A mild year shows less growth than customers added, and one heat wave can set a peak. The adjustment is a second table, on Demand growth, \"With the weather taken out\".",
    source: "Session 97; docs/methods/demand_growth.md, and docs/methods/demand_weather.md for the adjustment." },
  { key: "demand-series",
    text: "Demand is EIA's hourly demand of the grid operator's balancing authority: its adjusted demand, and for the Lower 48 its demand.",
    def: "EIA's \"Adjusted demand\" for the seven operators; \"Demand\" for the Lower 48, whose file has no adjusted column. It is demand as the grid sees it: power made behind a customer's meter (rooftop solar) is not in it.",
    source: "EIA Form EIA-930, Hourly Electric Grid Monitor, the per-area workbooks; public domain." },
  { key: "hours-used",
    text: "An hour is used when it is held, above zero, within 25 percent of the median of the four hours around it, and between a third of and three times the area's median hour. Nothing is filled.",
    def: "25 percent. Since 2019 the test leaves out 38 hours of CAISO, 7 of PJM, 2 of SPP, 1 of the Lower 48 and 12 hours of zero of NYISO. Without it PJM's 2020 peak would be a faulty 224,345 MW.",
    source: "Sessions 97, 103 and 118; docs/methods/impossible_hours.md, rule A. Counted again from EIA's workbooks by session 7508." },
  { key: "whole-year",
    text: "A whole year is written when at least 95 percent of its hours are used; a month at 95 percent.",
    def: "95 percent. Every year and month of every area passes: the fewest is CAISO's 2019, 8,725 of 8,760 hours. The hours used are in the grid's table year by year.",
    source: "Session 97; docs/methods/demand_growth.md, \"The rows\"." },
  { key: "local-time",
    text: "Years, months and hours of the day are the grid's own clock time, daylight saving included.",
    def: "Central time for ERCOT, MISO and SPP; Pacific for CAISO; Eastern for PJM, NYISO, ISO-NE and the Lower 48. An hour is named by its start.",
    source: "Session 97; docs/methods/eia930_demand_growth.md, \"Placing values in time\"." },
  { key: "average-hour",
    text: "Average demand is the mean of the hours used, in MW. Over a whole year it is the year's energy divided by its hours.",
    def: "The mean, not the sum: a leap year and a year with hours left out compare with any other. Multiply by the hours in the year for MWh.",
    source: "Session 97." },
  { key: "peak-hour",
    text: "Peak demand is the highest used hour of the year, an average over that hour. A grid operator's own record is measured over minutes and reads higher.",
    def: "The hourly average. California's highest hour of 2025 is 43,860 MW here, from 18:00 on 21 August; CAISO's own peak that evening is 44,506 MW, an instant at 18:07. The seven grids' records and 2026 summer peaks that EIA gives from the same form are this table's, to EIA's rounding.",
    source: "Session 97. CAISO, California ISO Peak Load History, January 2026. EIA, Today in Energy, \"PJM, ERCOT, and SWPP all set peak load records this summer\", 15 October 2026." },
  { key: "lower-48-peak",
    text: "No peak is given for the Lower 48.",
    def: "None. Its demand is EIA's sum over every balancing authority, faulty hours included, and a faulty hour inside the sum passes the test: its highest hour could be a fault.",
    source: "Session 97; docs/methods/demand_growth.md, \"The Lower 48 has no peak\"." },
  { key: "year-so-far",
    text: "The year so far is 1 January to the end of the newest year's last whole month, compared with the same months of 2019.",
    def: "The same months of every year, so a partial year is never set against a whole one. The window moves by a month with each monthly build; the page reads its end from the table's header.",
    source: "Session 97; the table's header line \"year to date\"." },
  { key: "last-whole-year",
    text: "A month's or an hour's growth is read at the last whole year, even where the newest year already holds that month.",
    def: "The last whole year. The table writes a month's and an hour's change from 2019 on that year's row only; the newest year's months are in the grid's table year by year, without a growth.",
    source: "Session 97's builder; session 404 for the page. Whether a month the newest year holds should show its own growth is the owner's to rule." },
  { key: "california-hours",
    text: "California's hours from 1 November 2023 to 2 December 2025 are read one hour earlier than EIA stamps them.",
    def: "One hour, over that period only; the hour left empty on 2 December 2025 is not filled.",
    source: "Session 82; docs/methods/eia930_caiso_break.md, \"The late hours\"." },
  { key: "areas",
    text: "Eight areas: the seven grid operators' balancing authorities and the Lower 48. A balancing authority is not a state, and not always the operator's whole market.",
    def: "ERCOT, CAISO, PJM, MISO, SPP, NYISO, ISO-NE and the Lower 48. The large balancing authorities outside the seven (the Tennessee Valley Authority, Southern Company, Bonneville, Duke, Florida Power and Light) are not here.",
    source: "Session 97; EIA Form EIA-930's balancing authorities." },
  { key: "against-sales",
    text: "Demand at the grid is not sales to customers. EIA's retail sales moved with the Lower 48's demand, and apart from it in California and New England.",
    def: "From 2019 to 2025: United States retail sales +7.05 percent, the Lower 48's demand here +7.03; Texas +24.20, ERCOT +27.22; New York -1.26, NYISO -2.73; New England +0.14, ISO-NE -2.54; California -2.96, CAISO +4.45. A state is not a balancing authority, and sales leave out line losses. Why California's two figures have opposite signs is not established here.",
    source: "EIA, Electric Power Monthly, data for August 2026, table 5.1 (sales to ultimate customers), and the same form (EIA-861M) by state as held in eia_retail_sales_monthly on 5 November 2026; the percents computed by session 7508." },
  { key: "opening",
    text: "The page opens on ERCOT and the whole year's average hour; an address the table does not hold falls back to that and says so.",
    def: "ERCOT, the whole year's average hour: the table's headline figure. Each grid is drawn at its own latest year.",
    source: "Session 404." },
  { key: "as-written",
    text: "Every figure is one row of the table, written as the table holds it: MW whole, percent to two decimals, a growth with its sign.",
    def: "No arithmetic on the page. A figure the table does not hold reads \"not held\", with no unit.",
    source: "Sessions 404 and 7508; site/scripts/check-values.mjs reads each figure again from the live set." },
];

export function DemandGrowthDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="7508">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page (each with its default and its source on hover)</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={DEMAND_GROWTH_DECISIONS.length}>
        {DEMAND_GROWTH_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-7508-${d.key}`} label="this choice's default and source">
              <span className="block" data-decision-default={d.key}><strong>Default:</strong> {d.def}</span>
              <span className="block" data-decision-source={d.key}><strong>Source:</strong> {d.source}</span>
            </Tip>
          </li>
        ))}
      </ul>
    </details>
  );
}
