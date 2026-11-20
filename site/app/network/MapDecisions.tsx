// Energy Research Warehouse (ERW) site, session 8606 (chain 504): the decisions block of the Grid tool's map, the
// Map shape of /grid?view=network. Each line is a choice that moves what the map draws, with its default and where
// it comes from, in the form the other tools' blocks have. It is drawn inside the map's own frame, so the Network
// shape's markup is as it was. The figures of line 3 are of one hour and say which; they come from
// replication/grid/crosscheck_map.csv (EIA's own series, read 19 November 2026).

export type MapDecision = { what: string; rule: string; source: string };

export const MAP_DECISIONS: MapDecision[] = [
  { what: "The hour the map opens on",
    rule: "The newest hour that every reporting pair of balancing authorities holds, as in the Network view. A pair reports when it held a flow in the last 48 hours. Later hours are on the slider.",
    source: "the network's hourly snapshot (Form EIA-930 interchange)" },
  { what: "Whose report a tie's megawatts are",
    rule: "A pair is counted once. Its flow is the report of the balancing authority whose code sorts first; in an hour that authority filed nothing, the other's report with its sign turned. Neither report is adjusted to the other.",
    source: "the snapshot's own rule; for 2026-11-17 04:00 UTC each of the 159 pairs is the report EIA publishes, to 1 MW (replication/grid/crosscheck_map.csv)" },
  { what: "A region's net exchange",
    rule: "The sum of its pairs, each read as above, zero flows counted as ties. It is not the authority's own total interchange as it files it with EIA: for 2026-11-17 04:00 UTC the two differ by more than 1 MW for 21 of the 60 authorities EIA holds a total for. PJM's pairs sum to 811 MW exported; its own total is 82 MW exported.",
    source: "replication/grid/crosscheck_map.csv (EIA's open data, total interchange, read 19 November 2026)" },
  { what: "Which ties are drawn",
    rule: "A tie whose flow is held and is not zero, from the exporter to the importer, when both ends have a boundary. Its width is its megawatts against the largest flow of the period shown.",
    source: "the snapshot; the boundary file" },
  { what: "The shape of a region",
    rule: "The balancing authority's published footprint, simplified for the web. Footprints overlap: the smaller is drawn on top, and the hover names the others that cover the point.",
    source: "the boundary file named under the map" },
  { what: "An authority with no boundary",
    rule: "Listed under the map by name, with its hover and its panel. It is not placed by hand, and its ties are not drawn here; they are in the Network view. Canada's and Mexico's operators are among them.",
    source: "the boundary file holds the United States' control areas only" },
  { what: "The color of a region",
    rule: "The carbon intensity of its generation, on the Network view's scale. It is held for the seven grids the warehouse computes it for; every other region is grey, never estimated.",
    source: "carbon_intensity_hourly" },
  { what: "State lines",
    rule: "Drawn thin so that a place can be found. They carry no figure and answer no pointer; names stay on hover only.",
    source: "US Census Bureau cartographic boundaries, through the us-atlas file" },
  { what: "The day \"California's evening\" shows",
    rule: "The newest whole Pacific day of the week for which the batteries are reported in all but one of its hours. A newer whole day with no report is named and passed over.",
    source: "caiso_battery_storage, CAISO's own data" },
];

export function MapDecisions() {
  return (
    <details className="border-t border-rule bg-panel px-2 py-1 text-xs text-ink" data-map-decisions={MAP_DECISIONS.length}>
      <summary className="cursor-pointer py-1 text-accent">Decisions on this map ({MAP_DECISIONS.length}): each choice that moves what is drawn, with its rule and its source</summary>
      <ol className="mt-1 list-decimal space-y-1.5 pb-2 pl-5 leading-snug">
        {MAP_DECISIONS.map((d) => (
          <li key={d.what} data-map-decision={d.what}>
            <span className="font-semibold">{d.what}.</span> {d.rule} <span className="text-muted">Source: {d.source}.</span>
          </li>
        ))}
      </ol>
    </details>
  );
}
