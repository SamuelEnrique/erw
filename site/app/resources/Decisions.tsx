// Energy Research Warehouse (ERW) site, session 8603 (chain 504): the decisions of the natural resource map (the
// Resources tab of /map), in the form the Projects tab's carry (app/map/Decisions.tsx, session 7601): one fold at the
// foot of the map, one line a choice that moves what the tab shows, and on hover, tap or focus its default, its source
// and the session that made it. No grey text: what explains a line is in its hover. Words only: no figure of the page
// reads it. docs/methods/resources.md, "Decisions (session 8603)", carries the same list; tests/test_session8603.py
// holds the two to one list.
import { Tip } from "@/components/tool/ToolPage";

export type ResourceDecision = { key: string; text: string; session: string; def: string; source: string };

export const RESOURCE_DECISIONS: ResourceDecision[] = [
  { key: "one-file", session: "session 146",
    text: "Each switch is one publisher's file, drawn as published. Nothing is computed across layers, and two layers that are on are never added or blended into one figure.",
    def: "One layer, one file, one publisher.",
    source: "The list of layers (site/data/resources/manifest.json), which names each file, its publisher, its terms and the day it was retrieved; docs/methods/resources.md, one section a layer." },
  { key: "the-resource", session: "session 146",
    text: "The layers are the resource itself: the wind, the sun, the heat, the rock, the water. What is built or planned on it is a separate set of switches, laid over from the project map's tables.",
    def: "The resource first; plants, the queue and datacenters off until switched on.",
    source: "The owner's idea of 7 October 2026. The overlays read eia860m_operating_generators, eia860m_planned_generators, energy_projects and datacenter_facilities, under the Projects tab's rules." },
  { key: "kinds-named", session: "sessions 159 and 8603",
    text: "Every kind the list names has a switch. A kind with no layer among the files (coal, uranium, critical minerals, and the gross capacity factor of wind) is a greyed switch that says why. Nothing is drawn in its place.",
    def: "A greyed switch with its reason on hover.",
    source: "The owner's list as chain 504 gives it: sun, wind, geothermal heat, hydropower potential, oil and gas, coal, uranium, critical minerals. The gross capacity factor needs a key issued to a named person, and none is asked for (session 159)." },
  { key: "plain-line", session: "session 8603",
    text: "The line under a switch says what the layer measures in the page's own plain words. The publisher's own description, word for word, is in the method note.",
    def: "One short sentence a layer, written from the method note.",
    source: "docs/methods/resources.md, each layer's \"What it is\"; the lines are MEASURE in site/lib/resources.ts." },
  { key: "opens-on-wind", session: "session 146",
    text: "The map opens with one layer on, the wind speed at 100 meters, over the contiguous states.",
    def: "Wind speed at 100 m; any layers chosen are kept in the address.",
    source: "firstLayer in site/lib/resources.ts: the wind speed layer when the files hold one, else the first layer." },
  { key: "grid-level", session: "session 146",
    text: "A grid layer (wind speed, sunlight) is held at three cell sizes, 0.2, 0.1 and 0.05 degrees. The map draws the finest whose cell is at least three quarters of a screen pixel at the zoom shown, and the hover's value is that cell's and says its size.",
    def: "Three quarters of a pixel.",
    source: "levelFor and MIN_CELL_PX in site/lib/resources.ts; each level is the publisher's raster averaged to that cell (docs/methods/resources.md, \"What holds for every layer\")." },
  { key: "outline-area", session: "session 8603",
    text: "A play's or a basin's area is the publisher's own figure for the outline it drew, a general area. It is not the whole formation and not an estimate of oil or gas. EIA's 2011 review gives other areas under the same names: the Marcellus is 95,000 square miles there and 58,326 here.",
    def: "The file's own area of each outline.",
    source: "EIA, Tight Oil and Shale Gas Plays (ShalePlays_US_EIA_Dec2021.shp), field Area_sq_mi; EIA, Review of Emerging Resources: U.S. Shale Gas and Shale Oil Plays, July 2011, page 29 of the file. The two set side by side: replication/resources/crosscheck_published.csv." },
  { key: "simplified", session: "session 146",
    text: "A shape's outline is drawn with fewer points than the publisher's, within 0.01 degrees of it for most layers, and no feature is dropped. A point is drawn at the publisher's own coordinates.",
    def: "As each layer's entry of the list of layers says under \"reduction\".",
    source: "site/data/resources/manifest.json, `reduction`; the Method note under the map prints it for each layer." },
  { key: "one-tab", session: "session 239",
    text: "The resource map is a tab of the project map, and the address /resources opens it.",
    def: "A tab of /map.",
    source: "The owner's menu of 12 October 2026 (six pages hold what thirteen held); site/next.config.ts." },
];

export function ResourceDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="resources">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({RESOURCE_DECISIONS.length}): each choice that moves what the map shows, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={RESOURCE_DECISIONS.length}>
        {RESOURCE_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-resources-${d.key}`} label="this choice's default and source">
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
