// Energy Research Warehouse (ERW) site, session 9000 (chain 601, part G): the decisions of the grid conditions page, in
// the form of the congestion page's (app/congestion/Decisions.tsx). docs/methods/grid_conditions.md carries the same
// reasoning; tests/test_session9000_conditions.py holds the page to its files.
import { Tip } from "@/components/tool/ToolPage";

export type ConditionsDecision = { key: string; text: string; session: string; def: string; source: string };

export const CONDITIONS_DECISIONS: ConditionsDecision[] = [
  { key: "as-published", session: "session 9000",
    text: "Every strip is a published figure: EIA's demand and day-ahead forecast, the operators' outages, binding constraints, adders and notices. The page takes a day's peak, mean, highest hour and count, and nothing else. It makes no estimate and gives no advice.",
    def: "Published figures only.",
    source: "site/data/conditions/*.json, built by warehouse/derived/conditions_page.py (docs/methods/grid_conditions.md)." },
  { key: "available", session: "session 9000",
    text: "\"Demand against what was available\" is drawn as demand against the day-ahead demand forecast: no operator whose terms allow it publishes its available capacity hour by hour in the files read. The reserves strip is blank for the same reason, with its reason on hover.",
    def: "Demand against the forecast.",
    source: "docs/reviews/grid-conditions-sources-2026-11-20.md." },
  { key: "blank-strips", session: "session 9000",
    text: "A strip an operator's terms hold (PJM, NYISO, ISO-NE), that is paused (MISO), or that sits on paths a robots file disallows (ERCOT's outages and constraints) is drawn blank with its reason on hover. Demand is EIA's and is drawn for every grid.",
    def: "Blank, with the reason.",
    source: "docs/licenses.md; the owner's ruling of 6 November 2026; paused_sources.csv." },
  { key: "hourly-windows", session: "session 9000",
    text: "Hour-by-hour figures are kept for the newest 35 days and for the nine events of /events; any other day is drawn day by day, fifteen days either side, with the hours of the chosen day when a kept window holds them.",
    def: "Hourly for the newest days and the events.",
    source: "The page files' size: every hour of every grid since 2018 would be about 40 MB." },
  { key: "spp-area", session: "session 9000",
    text: "SPP's outages are its RTO balancing area (SPP), the area EIA's SWPP demand covers; the western area SPP added in April 2026 (SWPW) and SPP's total are in the table and not drawn here.",
    def: "The RTO balancing area.",
    source: "generation_outages_hourly." },
  { key: "scarcity", session: "session 9000",
    text: "The scarcity strip is ERCOT's online reserve price adder, held from June 2014 until it ended on 4 December 2025. It ended because ERCOT changed how it prices scarcity: since 5 December 2025 ERCOT clears energy and ancillary services together in real time, and scarcity is priced through the ancillary services' own demand curves, which the page does not draw. CAISO's alerts stand in its alerts strip; the other grids publish no adder of this kind in the files read.",
    def: "ERCOT's adder.",
    source: "ercot_rtm_price_adders; scarcity_hours_by_grid." },
  { key: "first", session: "session 9000",
    text: "The page opens on ERCOT, its newest 35 days, with no second operator.",
    def: "ERCOT, the newest days.",
    source: "The page's own choice." },
  { key: "clock", session: "session 9000",
    text: "Days are each operator's own clock (Pacific for CAISO, Central for ERCOT, SPP and MISO, Eastern for PJM, NYISO and ISO-NE); hours on the hourly charts are UTC instants.",
    def: "The operator's clock for days.",
    source: "The page files' time line." },
];

export function ConditionsDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="conditions">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({CONDITIONS_DECISIONS.length}): each choice that moves what the page shows, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={CONDITIONS_DECISIONS.length}>
        {CONDITIONS_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-conditions-${d.key}`} label="this choice's default and source">
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
