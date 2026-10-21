import type { Metadata } from "next";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import statesTopo from "us-atlas/states-albers-10m.json";
import { Brand } from "@/components/Brand";
import { Related } from "@/components/Related";
import { SiteLink as Link } from "@/components/SiteLink";
import { Tabs } from "@/components/tool/Tabs";
import { SourceLine, ToolHeader, ToolPage } from "@/components/tool/ToolPage";
import { TableDownloads } from "@/components/tool/TableDownloads";
import mapJson from "@/data/map.json";
import { faceOf, whole, type MapFile } from "@/lib/projectmap";
import { one, tabOf } from "@/lib/tabs";
import { ResourcesView } from "../resources/view";
import { Num } from "@/components/Num";
import { HOURLY, attempt, restCount } from "@/lib/supabase";
import { ProjectMap } from "./ProjectMap";
import { QUEUE_TABLE, QueuesView } from "./QueuesView";

// Session 167: the project map, one page. Version 2's layout and data (session 105: the "Choose" panel, the summary
// sentence, the totals by status, the map with hover, the source line) with what version 1 offered carried over
// (sessions 16 and 22: the unit card, the state filter both ways, the four kinds, the table by technology, Reset).
// Every filter is a multi-select with "Select all" and "Clear", and the address keeps the choice. The page reads the
// site's own copy of four tables (data/map.json, warehouse/derived/project_map.py). The card's fields are read from the
// same file, at the first click on a unit, through /map/card (built with the site; Supabase is never asked). Both earlier versions are kept unrouted in app/_retired/map-v1 and map-v2; /map/v2 redirects
// here. Method: docs/methods/energy_projects.md, "The page".

export const metadata: Metadata = { title: "The project map", robots: { index: false, follow: false } };

const METHOD = "/data/methods/energy_projects";

// Session 239: one page, two tabs (lib/tabs.ts): the projects (what this page drew, below) and the resources (what
// /resources drew: the natural resource layers, with the plants, the queue and the datacenters over them; it
// redirects to its tab). The tab is in the address, ?tab=resources.
export default async function MapPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const sp = one(await searchParams);
  const tab = tabOf("/map", sp.tab);
  return (
    <Brand>
      <ToolPage>
        <div data-map-tab={tab}>
          <Tabs page="/map" active={tab} />
          {tab === "resources" ? <ResourcesView /> : tab === "queues" ? <QueuesView iso={sp.iso} /> : <ProjectsView />}
          {/* session 330: the four tables the map's own copy is built from (both tabs draw them), as CSV with a Python and a
              Stata reader (session 328's shared line); the resource layers are their publishers' files, named in the tab's note.
              Session 367: the Queues tab (session 349) offers its own table instead */}
          <TableDownloads tables={tab === "queues" ? [QUEUE_TABLE] : (mapJson as unknown as MapFile).tables} />
          <Related href="/map" />
        </div>
      </ToolPage>
    </Brand>
  );
}

/** The first tab: every unit, queue position and datacenter on the map of the states (what /map drew before session 239). */
async function ProjectsView() {
  const f = mapJson as unknown as MapFile;
  const topo = statesTopo as unknown as Topology<{ states: GeometryCollection }>;
  const c = f.counts;
  // session 349: the queue positions not placed on the map, read from energy_projects (the check key's own count): their
  // county words name no county, place or town the Census Bureau lists in their state, or they state none
  const unplaced = await attempt(() => restCount("entities", { table_name: "eq.energy_projects", "extra->>kind": "eq.queue", "extra->>geo_precision": "eq.none" }, HOURLY));
  return (
    <>
      <ToolHeader title="The project map"
        lead={<>Every generating unit in EIA&apos;s monthly inventory, operating and planned (<span data-map-units="1">{whole(c.units)}</span> units as of {f.vintage}), the interconnection queue positions that are not withdrawn, and the datacenters the ERW holds, on one map. Choose any grids, technologies, statuses, states, kinds and sizes; click a unit for its card. <Link href={METHOD}>Method</Link>.</>} />
      {unplaced.ok ? (
        <p className="mb-3 max-w-3xl text-sm" data-unplaced="queue">
          <Num check="projects|count|queue|none" raw={unplaced.data}>{unplaced.data.toLocaleString("en-US")}</Num> queue positions the ERW holds (withdrawn ones among them) are not on the map: their county words name no county, city or town the Census Bureau lists in their state, or they state no county or no state. <Link href={`${METHOD}#coordinates`}>How a position is placed</Link>.
        </p>
      ) : null}
      <ProjectMap file={faceOf(f)} statesGeo={feature(topo, topo.objects.states)} />
      <SourceLine tables={f.tables}
        note={<>U.S. Energy Information Administration, Form EIA-860M, {f.vintage} (public domain), retrieved {f.retrieved.slice(0, 10)}; the ISOs&apos; queues as energy_projects holds them, {f.vintages.queue}; the datacenter tracker, {f.vintages.datacenter}. This page is in review and reads the site&apos;s own copy of the tables, built {f.built.slice(0, 10)}.</>} />
    </>
  );
}
