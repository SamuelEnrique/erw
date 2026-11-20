// Energy Research Warehouse (ERW) site, session 8014 (chain 581, part C): the decisions of the curtailment tool's "Where
// and when" view, in the form of the states page's (app/states/Decisions.tsx). docs/methods/where_when.md,
// "Decisions (session 8014)", carries the same list; tests/test_session8014_where_when.py holds the two to one list.
import { Tip } from "@/components/tool/ToolPage";

export type WhereDecision = { key: string; text: string; session: string; def: string; source: string };

export const WHERE_DECISIONS: WhereDecision[] = [
  { key: "as-published", session: "session 8014",
    text: "Curtailment is each operator's own figure as it publishes it; the hours below zero are counted from the public hub and zone prices. The view counts hours, sums months and years, and computes only the shares it names. It makes no estimate and gives no advice on where to put a load.",
    def: "The operators' figures and the prices as published.",
    source: "site/data/curtailment/where_when.json, built by warehouse/derived/where_when.py (docs/methods/where_when.md)." },
  { key: "who-publishes", session: "session 8014",
    text: "CAISO publishes its curtailment by the five minutes, so it has an hour of the day; SPP publishes by day, so its view is by month. ERCOT publishes no curtailment figure: the curtailment page's ERCOT estimate is the ERW's arithmetic and is not drawn here.",
    def: "CAISO by hour; SPP by month; ERCOT none.",
    source: "caiso_curtailment_profile, spp_curtailment_daily; the curtailment page's own notes." },
  { key: "held-prices", session: "session 8014",
    text: "A grid whose prices the license holds (NYISO, ISO-NE), or that is paused (MISO), or whose prices are not in the warehouse (PJM), is named with its places and no number, with the reason on hover.",
    def: "Named, not drawn.",
    source: "warehouse/metadata/license_status.py (the owner's ruling of 12 October 2026); paused_sources.csv." },
  { key: "hour-rule", session: "session 8014",
    text: "An hour's price is real time where the place holds 95 percent of the year's hours in real time, otherwise day-ahead, said on hover; an hour of real time is the mean of its four 15-minute prices. A year's share below zero is written only when 95 percent of its hours are held.",
    def: "Real time where held; whole years only.",
    source: "free_energy.py's rule, reused unchanged." },
  { key: "first-place", session: "session 8014",
    text: "The view opens on CAISO's curtailment, solar, in its newest whole year, with no second place.",
    def: "CAISO, solar, the newest whole year.",
    source: "The view's own choice: CAISO is the one operator that publishes by the hour." },
  { key: "shading", session: "session 8014",
    text: "Each cell is shaded by its figure over the largest figure of the same grid, so two grids' shades are not on one scale; each cell's figure is on hover.",
    def: "Each grid on its own scale.",
    source: "The view's own choice." },
  { key: "clock", session: "session 8014",
    text: "CAISO's hours are Pacific clock time, as its record is; the prices' hours and months are each grid's standard time, with no daylight saving shift.",
    def: "As each source keeps time.",
    source: "caiso_curtailment_profile; free_energy.py." },
  { key: "ranking", session: "session 8014",
    text: "The places are ranked by the share of hours below zero in each one's newest whole year, largest first; an average of hubs is not a place and is not ranked.",
    def: "Largest share first.",
    source: "ranked_negative in the file." },
];

export function WhereWhenDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="where-when">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({WHERE_DECISIONS.length}): each choice that moves what the page shows, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={WHERE_DECISIONS.length}>
        {WHERE_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-where-when-${d.key}`} label="this choice's default and source">
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
