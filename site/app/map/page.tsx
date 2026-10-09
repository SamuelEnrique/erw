import type { Metadata } from "next";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import statesTopo from "us-atlas/states-albers-10m.json";
import { Related } from "@/components/Related";
import { SiteLink as Link } from "@/components/SiteLink";
import { SourceLine, ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import mapJson from "@/data/map.json";
import { faceOf, whole, type MapFile } from "@/lib/projectmap";
import { ProjectMap } from "./ProjectMap";

// Session 167: the project map, one page. Version 2's layout and data (session 105: the "Choose" panel, the summary
// sentence, the totals by status, the map with hover, the source line) with what version 1 offered carried over
// (sessions 16 and 22: the unit card, the state filter both ways, the four kinds, the table by technology, Reset).
// Every filter is a multi-select with "Select all" and "Clear", and the address keeps the choice. The page reads the
// site's own copy of four tables (data/map.json, warehouse/derived/project_map.py). The card's fields are read from the
// same file, at the first click on a unit, through /map/card (built with the site; Supabase is never asked). Both earlier versions are kept unrouted in app/_retired/map-v1 and map-v2; /map/v2 redirects
// here. Method: docs/methods/energy_projects.md, "The page".

export const metadata: Metadata = { title: "The project map", robots: { index: false, follow: false } };

const METHOD = "/data/methods/energy_projects";

export default function MapPage() {
  const f = mapJson as unknown as MapFile;
  const topo = statesTopo as unknown as Topology<{ states: GeometryCollection }>;
  const c = f.counts;
  return (
    <ToolPage>
      <ToolHeader title="The project map"
        lead={<>Every generating unit in EIA&apos;s monthly inventory, operating and planned (<span data-map-units="1">{whole(c.units)}</span> units as of {f.vintage}), the interconnection queue positions that are not withdrawn, and the datacenters the ERW holds, on one map. Choose any grids, technologies, statuses, states, kinds and sizes; click a unit for its card. <Link href={METHOD}>Method</Link>.</>} />
      <ProjectMap file={faceOf(f)} statesGeo={feature(topo, topo.objects.states)} />
      <SourceLine tables={f.tables}
        note={<>U.S. Energy Information Administration, Form EIA-860M, {f.vintage} (public domain), retrieved {f.retrieved.slice(0, 10)}; the ISOs&apos; queues as energy_projects holds them, {f.vintages.queue}; the datacenter tracker, {f.vintages.datacenter}. This page is in review and reads the site&apos;s own copy of the tables, built {f.built.slice(0, 10)}.</>} />
      <Related href="/map" />
    </ToolPage>
  );
}
