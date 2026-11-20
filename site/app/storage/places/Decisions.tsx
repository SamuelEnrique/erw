// Energy Research Warehouse (ERW) site, session 8014 (chain 581, part F1): the decisions of "Batteries in every authority
// and state", in the states page's form. docs/methods/storage_places.md, "Decisions (session 8014)", carries the same list;
// tests/test_session8014_storage_places.py holds the two to one list.
import { Tip } from "@/components/tool/ToolPage";

export type PlacesDecision = { key: string; text: string; session: string; def: string; source: string };

export const PLACES_DECISIONS: PlacesDecision[] = [
  { key: "batteries", session: "session 8014",
    text: "A battery is a unit of EIA-860M whose prime mover is BA (battery), the units the storage page counts; pumped hydro, flywheels and compressed air are not counted.",
    def: "Prime mover BA.", source: "eia860m_operating_generators and eia860m_planned_generators." },
  { key: "placed-as-printed", session: "session 8014",
    text: "Each unit is placed by the balancing authority and the state EIA-860M prints for it. A unit with no authority is counted under \"no authority named\", never moved to one.",
    def: "As EIA prints it.", source: "EIA-860M's Balancing Authority Code and Plant State columns." },
  { key: "mwh-as-given", session: "session 8014",
    text: "Energy (MWh) is summed only over the units that give it, and the MW of those units stands beside it. MWh is never computed from MW, and planned units have none (EIA's planned sheet has no such column).",
    def: "MWh where given.", source: "EIA-860M's Nameplate Energy Capacity." },
  { key: "year-of-start", session: "session 8014",
    text: "The chart adds, year by year, the MW of the units operating today that started in that year: a unit retired since is not in it, so the line is today's fleet by age, not the fleet as it stood each year.",
    def: "Today's units by year of start.", source: "EIA-860M's Operating Year." },
  { key: "first-two", session: "session 8014",
    text: "The page opens on ERCOT and CAISO, the two authorities with the most battery MW.",
    def: "ERCOT and CAISO.", source: "The page's own choice, on the file's figures." },
];

export function PlacesDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="storage-places">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({PLACES_DECISIONS.length}): each choice that moves what the page shows, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={PLACES_DECISIONS.length}>
        {PLACES_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-storage-places-${d.key}`} label="this choice's default and source">
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
