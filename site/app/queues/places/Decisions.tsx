// Energy Research Warehouse (ERW) site, session 8014 (chain 581, part F2): the decisions of "Queues outside the seven
// grids", in the states page's form. docs/methods/queue_places.md, "Decisions (session 8014)", carries the same list.
import { Tip } from "@/components/tool/ToolPage";

export type QpDecision = { key: string; text: string; session: string; def: string; source: string };

export const QP_DECISIONS: QpDecision[] = [
  { key: "lbnl-names", session: "session 8014",
    text: "Each queue owner keeps the name Lawrence Berkeley National Laboratory gives it; nothing is matched to a balancing authority by name.",
    def: "LBNL's names.", source: "lbnl_interconnection_queue, its column lbnl_entity." },
  { key: "states-by-people", session: "session 8014",
    text: "A state is listed when some of its people live outside the seven grids, by county; a state no entry of LBNL's West or Southeast names is listed as having no public queue in the compilation.",
    def: "By county population.", source: "eia_county_region and census_county_population, as /states computes them." },
  { key: "first-two", session: "session 8014",
    text: "The page opens on the two queue owners with the most active MW.",
    def: "The two largest by active MW.", source: "The page's own choice, on the file's figures." },
];

export function QueuePlacesDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="queue-places">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({QP_DECISIONS.length}): each choice that moves what the page shows, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={QP_DECISIONS.length}>
        {QP_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-queue-places-${d.key}`} label="this choice's default and source">
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
