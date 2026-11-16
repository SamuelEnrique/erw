// Energy Research Warehouse (ERW) site, session 7601 (chain 305): the decisions of /map's Projects tab, in the form the
// five tools and the trackers carry: one fold at the foot of the tab, one line a choice that moves a figure of the
// page, and on hover, tap or focus its default, its source and the session that made it. No grey text: what explains
// a line is in its hover. The list lives here, in the tool's own folder (the shared list, lib/decisions.ts, is being
// edited on other branches), and is drawn with the same marks, so a test reads it as it reads the others. Words only:
// no figure of the page reads it. docs/methods/map.md, section 14, carries the same list;
// tests/test_session7601_map.py holds the two to one list.
import { Tip } from "@/components/tool/ToolPage";

export type MapDecision = { key: string; text: string; session: string; def: string; source: string };

export const MAP_DECISIONS: MapDecision[] = [
  { key: "nameplate", session: "session 105",
    text: "A unit's megawatts are its nameplate capacity. Net summer capacity, the measure of EIA's own published totals, is lower.",
    def: "Nameplate capacity.",
    source: "EIA, Form EIA-860M, \"Nameplate Capacity (MW)\". Over the operating units of the inventory of 2026-09, net summer capacity is 7.5 percent lower (docs/methods/map.md, section 12)." },
  { key: "never-added", session: "session 167",
    text: "Megawatts are never added across kinds: a unit's nameplate, a queue position's request and a datacenter's stated load are three different things.",
    def: "Each kind has its own count and its own sum.",
    source: "A queue position is a request, and most are withdrawn before they are built (docs/methods/energy_projects.md); a datacenter's megawatts are a load a story or its operator states." },
  { key: "not-withdrawn", session: "sessions 16 and 167",
    text: "A queue position is on the map while it is not withdrawn: active, suspended, completed, or with no status stated. A completed position may be a unit the inventory already lists.",
    def: "Withdrawn positions are left out.",
    source: "The table energy_projects, its standard status; the first version of the map (session 16)." },
  { key: "queues-drawn", session: "sessions 159 and 167",
    text: "The queue positions drawn are ERCOT's, SPP's, CAISO's and ISO-NE's. MISO's and NYISO's are held back, and no queue of PJM is held.",
    def: "Four queues.",
    source: "Each grid operator's own terms: MISO's pulls are paused while its terms are reviewed (docs/methods/miso_pause.md); NYISO's legal notice confers no license." },
  { key: "grid", session: "session 105",
    text: "A unit's grid is EIA's balancing authority for it. The seven ISOs are named; every other balancing authority, and a unit with none, is \"Outside the seven ISOs\".",
    def: "EIA's balancing authority code.",
    source: "EIA, Form EIA-860M, \"Balancing Authority Code\". In the inventory of 2026-09, 973 units have none: EIA leaves 727 blank and writes \"NA\" for 246." },
  { key: "battery", session: "session 105",
    text: "A battery is a storage unit whose prime mover is a battery; pumped storage and the other kinds are \"Other storage\". A queue's storage request does not say what kind it is.",
    def: "EIA prime mover code BA.",
    source: "EIA, Form EIA-860 instructions, the prime mover codes." },
  { key: "eia-status", session: "session 167",
    text: "A planned unit keeps EIA's own seven status codes, from approvals not started to construction complete; they are not folded into \"planned\" and \"under construction\".",
    def: "EIA's code, in plain words.",
    source: "EIA, Form EIA-860 instructions, the proposed status codes P, L, T, U, V, TS and OT; the owner's words of 8 October 2026." },
  { key: "county-point", session: "sessions 16 and 349",
    text: "A queue position is drawn at its county's point, or its city's or town's, not at its site. A name the Census Bureau's files do not hold in its state leaves the position off the drawing.",
    def: "The internal point of the county, the place or the town; no fuzzy matching.",
    source: "U.S. Census Bureau, 2025 Gazetteer Files (counties, places, county subdivisions); docs/methods/energy_projects.md, \"Coordinates\"." },
  { key: "size", session: "session 167",
    text: "When a size is asked for, a row whose source states no megawatts is left out: it cannot be said to fit one. Both ends of the size are counted in.",
    def: "No size: every row.",
    source: "A choice of session 167, stated in the method note; no source sets it." },
  { key: "us-state", session: "session 167",
    text: "A datacenter is drawn when the tracker places it in a US state. A facility abroad, or one no story names a state for, is counted in the file and not drawn.",
    def: "The facilities with a US state.",
    source: "The table datacenter_facilities, its state column (docs/methods/datacenter_facilities.md)." },
  { key: "retired", session: "session 105",
    text: "Retired units are not on the map, and nothing since the inventory's month is in it.",
    def: "Operating and planned units of one month.",
    source: "EIA, Form EIA-860M, published about a month after the month it describes; retired units are in the table eia860m_retired_generators." },
];

export function MapDecisions() {
  return (
    <details className="mt-10 border-t border-rule pt-3 text-sm" data-decisions="map">
      <summary className="cursor-pointer py-1 text-accent">Decisions on this page ({MAP_DECISIONS.length}): each choice that moves a figure, with its default and its source</summary>
      <ul className="mt-2 max-w-3xl list-disc space-y-1 pl-5 text-sm" data-decision-count={MAP_DECISIONS.length}>
        {MAP_DECISIONS.map((d) => (
          <li key={d.key} data-decision={d.key}>
            {d.text}
            <Tip id={`decision-map-${d.key}`} label="this choice's default and source">
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
