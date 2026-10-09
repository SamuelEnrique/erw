import type { Metadata } from "next";
import { geoAlbersUsa } from "d3-geo";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import statesTopo from "us-atlas/states-albers-10m.json";
import { SiteLink as Link } from "@/components/SiteLink";
import { Fold, SourceLine, ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import mapJson from "@/data/map_v2.json";
import queuesJson from "@/data/queues.json";
import { whole, type MapData, type MapFile, type QueueViews } from "@/lib/map2";
import { MapV2 } from "./MapV2";

// Session 167: retired and kept unrouted, as it stood. /map/v2 redirects to /map (next.config.ts), the one project map,
// built on this version's layout and data; the session 167 report lists every block of this page and where it went.
// Session 105: the project map, version 2, in the battery page's layout. Every operating and planned generating unit
// of EIA's monthly inventory (Form EIA-860M), batteries among them, on a map: filtered by grid, technology, status and
// size, with the queue's active capacity for the same grid beside it and a table of what is selected. The page reads
// the site's own copy of the two tables (data/map_v2.json, warehouse/derived/project_map.py). The older map (/map)
// is as it was.

export const metadata: Metadata = { title: "The project map", robots: { index: false, follow: false } };

// us-atlas's albers files are drawn with geoAlbersUsa().scale(1300).translate([487.5, 305]) on a 975 x 610 plane; the
// units use the same projection, so they sit on the state outlines (as the older map does).
const W = 975, H = 610;
const projection = geoAlbersUsa().scale(1300).translate([487.5, 305]);

export default function MapTwo() {
  const f = mapJson as unknown as MapFile;
  const topo = statesTopo as unknown as Topology<{ states: GeometryCollection }>;
  const x: (number | null)[] = [], y2: (number | null)[] = [];
  for (let i = 0; i < f.mw.length; i++) {
    const p = f.la[i] === null || f.lo[i] === null ? null : projection([f.lo[i] as number, f.la[i] as number]);
    x.push(p ? Math.round(p[0] * 10) / 10 : null);
    y2.push(p ? Math.round(p[1] * 10) / 10 : null);
  }
  const { la: _la, lo: _lo, ...rest } = f;
  void _la; void _lo;
  const data: MapData = { ...rest, x, y2, statesGeo: feature(topo, topo.objects.states), width: W, height: H };
  const c = f.counts;
  const notDrawn = x.filter((v) => v === null).length;
  const queue = queuesJson as unknown as { views: QueueViews; vintage: string };
  return (
    <ToolPage>
      <ToolHeader title="The project map" crumb={<>Version 2, in review. The map as it was: <Link href="/map" className="underline">/map</Link></>}
        lead={<>Every generating unit in EIA&apos;s monthly inventory, operating and planned, batteries among them: <span data-map-units="1">{whole(c.units)}</span> units and {whole(c.mw)} MW as of {f.vintage}. Choose a grid, a technology, a status and a size; the queue for the same grid is beside it.</>} />
      <MapV2 data={data} queue={queue.views} queueVintage={queue.vintage} />
      <div className="mt-2 lg:pl-[272px]">
        <Fold title="What the inventory leaves out">
          <ul className="max-w-3xl list-disc space-y-1 pl-5">
            <li><strong>Plants under 1 megawatt.</strong> EIA describes the form as covering &quot;existing and proposed generating units at electric power plants with 1 megawatt or greater of combined nameplate capacity&quot;. Rooftop solar and other small generators at homes and businesses are not in it. ({whole(c.under_1_mw)} units here are smaller than 1 MW; each is at a plant that passes the threshold.)</li>
            <li><strong>Retired units.</strong> The inventory lists them; this map does not. They are in the table <code className="font-mono text-xs">eia860m_retired_generators</code>.</li>
            <li><strong>Projects that have told no one but a grid operator.</strong> A planned unit is one its owner has reported to EIA. A request in an interconnection queue is not here until then, which is why the queue beside the map is far larger than the planned units.</li>
            <li><strong>A grid for {whole(c.without_balancing_authority)} units.</strong> The inventory names no balancing authority for them; they are counted outside the seven ISOs, with the units of every other balancing authority.</li>
            <li><strong>Energy for planned batteries.</strong> The inventory gives a planned battery its power in MW and no energy in MWh.</li>
            <li><strong>{notDrawn ? `${whole(notDrawn)} units in Puerto Rico on the drawing.` : "Nothing on the drawing."}</strong> {notDrawn ? "The map's projection has no place for them; they are in the totals and the table." : ""}</li>
            <li><strong>Anything since {f.vintage}.</strong> The inventory is monthly and published about a month after the month it describes.</li>
          </ul>
        </Fold>
        <Fold title="How to read it">
          <ul className="max-w-3xl list-disc space-y-1 pl-5">
            <li>A row is a generating unit, not a plant: a plant with four turbines is four units. MW is the unit&apos;s nameplate capacity.</li>
            <li>A grid is EIA&apos;s balancing authority for the unit. The seven ISOs are named; every other balancing authority is &quot;outside the seven ISOs&quot;.</li>
            <li>Batteries are the storage units whose prime mover is a battery; pumped storage and the other kinds are &quot;other storage&quot;.</li>
            <li>Under construction and planned are EIA&apos;s statuses for a proposed unit, grouped: under construction, or not yet.</li>
          </ul>
        </Fold>
        <SourceLine tables={f.tables.concat(["interconnection_queue_summary"])}
          note={<>U.S. Energy Information Administration, Form EIA-860M, {f.vintage} (public domain), retrieved {f.retrieved.slice(0, 10)}; the queue from Lawrence Berkeley National Laboratory and GridTracker, Queued Up, {queue.vintage} (CC BY 4.0). This page is in review and reads the site&apos;s own copy of the tables, built {f.built.slice(0, 10)}.</>} />
      </div>
    </ToolPage>
  );
}
