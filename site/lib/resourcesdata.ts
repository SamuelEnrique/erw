// Energy Research Warehouse (ERW) site, session 146: what "Where the resources are" (/resources, in review) reads on
// the server. The resource layers are files the data side writes and describes in data/resources/manifest.json; the
// page asks for a layer's file only when its toggle is switched on, through /resources/layer/<name>, an address the
// release gate covers (a file under public/ is open to every visitor, whatever the page's status). The overlays are
// tables the site already holds: EIA-860M's units from the project map's own copy (data/map_v2.json), and the
// interconnection queue's rows and the datacenter facilities from the live set, through lib/supabase.ts.
import "server-only";
import fs from "node:fs";
import path from "node:path";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import countiesTopo from "us-atlas/counties-10m.json";
import mapJson from "@/data/map_v2.json";
import type { MapFile } from "@/lib/map2";
import { STATES } from "@/lib/regions";
import { QUEUE_GRIDS, boxOf, filesOf, inGeometry, queueGridOf, stemOf, type Geometry, type Layer, type Manifest, type QueueGridCount } from "@/lib/resources";
import { HOURLY, rest } from "@/lib/supabase";

// Where a layer's file may be: the site's own data folder first (not served to visitors), then the folder the data
// side writes today. Moving the files from the second to the first needs no change here.
// Each path is written out to its folder, so the server's file trace holds these two folders and nothing more.

function fileOnDisk(file: string): string | null {
  if (!/^[A-Za-z0-9._-]+$/.test(file) || file.includes("..")) return null;   // a bare file name, never a path
  const own = path.join(process.cwd(), "data", "resources", "layers", file);
  if (fs.existsSync(own)) return own;
  const written = path.join(process.cwd(), "public", "resources-data", file);
  return fs.existsSync(written) ? written : null;
}

/** The manifest as the page uses it: the layers whose files are on the server; a layer that names a file that is not
 *  there joins the missing list with that reason. `reason` is set when the manifest itself cannot be read. */
export function readManifest(): { manifest: Manifest; reason: string | null } {
  let raw: Manifest;
  try {
    raw = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "resources", "manifest.json"), "utf8")) as Manifest;
  } catch (e) {
    return { manifest: { layers: [], missing: [] }, reason: `The list of resource layers could not be read on the server (${(e as NodeJS.ErrnoException).code ?? (e as Error).message}).` };
  }
  const layers: Layer[] = [], missing = [...(raw.missing ?? [])];
  for (const l of raw.layers ?? []) {
    const files = l && typeof l.id === "string" && ["grid", "shapes", "points"].includes(l.kind) ? filesOf(l) : [];
    const there = files.filter((f) => fileOnDisk(f));
    if (!files.length || !there.length) { missing.push({ id: l?.id, group: l?.group, title: l?.title, reason: "The list names this layer, but its file is not on the server." }); continue; }
    // a legend the page can draw a scale from has a lowest and a highest value; anything else (a list of kinds, a string) is left to the features
    const lg = l.legend as unknown as { min?: unknown; max?: unknown } | null | undefined;
    const legend = lg && typeof lg === "object" && typeof lg.min === "number" && typeof lg.max === "number" ? l.legend : undefined;
    const parts = Array.isArray(l.other_extents) ? l.other_extents.filter((x) => x && Array.isArray(x.levels)).map((x) => ({ ...x, levels: x.levels.filter((v) => there.includes(v.file)) })).filter((x) => x.levels.length) : undefined;
    layers.push(l.kind === "grid" ? { ...l, legend, levels: (l.levels ?? []).filter((v) => there.includes(v.file)), other_extents: parts } : { ...l, legend });
  }
  return { manifest: { built_at_utc: raw.built_at_utc, layers, missing }, reason: null };
}

/** The name in the address of every file the manifest's layers name. */
export function layerStems(): string[] {
  return [...new Set(readManifest().manifest.layers.flatMap(filesOf).map(stemOf))];
}
/** The bytes of the file a name in the address stands for; null when no layer of the manifest names it. */
export function layerBody(stem: string): Buffer | null {
  const file = readManifest().manifest.layers.flatMap(filesOf).find((f) => stemOf(f) === stem);
  const p = file ? fileOnDisk(file) : null;
  return p ? fs.readFileSync(p) : null;
}

// ---------------------------------------------------------------------------------------------------------------------
// The overlays.

/** EIA-860M's operating and planned units with their coordinates, as the project map's own copy holds them. */
export function plants() {
  const f = mapJson as unknown as MapFile;
  return {
    ok: true as const, tables: f.tables, vintage: f.vintage, retrieved: f.retrieved, techs: f.techs, statuses: f.statuses, states: f.states, names: f.names,
    n: f.n, s: f.s, t: f.t, st: f.st, mw: f.mw, y: f.y, lo: f.lo, la: f.la,
  };
}

type QueueRow = {
  entity_id: string; lat: number | null; lon: number | null; capacity_mw: number | null; status: string | null; vintage: string | null;
  tech: string | null; state: string | null; county: string | null; prec: string | null; src: string | null;
};
type County = { id: string; name: string; geometry: Geometry; box: [number, number, number, number] };
let COUNTIES: County[] | null = null;
function counties(): County[] {
  if (COUNTIES) return COUNTIES;
  const topo = countiesTopo as unknown as Topology<{ counties: GeometryCollection<{ name: string }> }>;
  COUNTIES = feature(topo, topo.objects.counties).features.flatMap((f) => {
    const box = boxOf(f.geometry as Geometry);
    return box ? [{ id: String(f.id), name: f.properties.name, geometry: f.geometry as Geometry, box }] : [];
  });
  return COUNTIES;
}
// A county by its name and state, for a row whose point the outline does not hold (a county of islands, whose point
// the simplified outline leaves at sea): the state's code to its name, the name to the outline file's state number.
let STATE_NUMBER: Map<string, string> | null = null;
const bare = (s: string) => s.toLowerCase().replace(/\b(county|parish|borough|census area|municipality)\b/g, "").replace(/[^a-z]/g, "");
function countyNamed(state: string | null, county: string | null): County | null {
  if (!state || !county) return null;
  if (!STATE_NUMBER) {
    const topo = countiesTopo as unknown as Topology<{ states: GeometryCollection<{ name: string }> }>;
    STATE_NUMBER = new Map(feature(topo, topo.objects.states).features.map((f) => [f.properties.name, String(f.id)]));
  }
  const number = STATE_NUMBER.get(STATES[state] ?? "");
  if (!number) return null;
  const hits = counties().filter((c) => c.id.startsWith(number) && bare(c.name) === bare(county));
  return hits.length === 1 ? hits[0] : null;
}
const round3 = (c: unknown): unknown => (Array.isArray(c) ? c.map(round3) : typeof c === "number" ? Math.round(c * 1000) / 1000 : c);

/** The interconnection queue's rows of energy_projects in the live set, by county. A row the table places at a county
 *  is counted in the county whose published shape (us-atlas, from the Census Bureau's cartographic boundary files)
 *  holds the table's point for it, or, where the simplified shape leaves that point at sea, in the one county of that
 *  name in that state; the county is what is drawn, never a site. A row with coordinates of its own is a
 *  point. A row with neither is counted and not drawn. */
export async function queue() {
  const rows = await rest<QueueRow>("entities", {
    select: "entity_id,lat,lon,capacity_mw,status,vintage,tech:extra->>technology_group,state:extra->>state,county:extra->>county,prec:extra->>geo_precision,src:extra->>source_table",
    table_name: "eq.energy_projects", "extra->>kind": "eq.queue", order: "entity_id",
  }, HOURLY, 100_000);
  type Agg = { county: County; state: string; requests: number; mw: number; noMw: number; status: Record<string, number> };
  const byPoint = new Map<string, County | null>(), byCounty = new Map<string, Agg>();
  const points: { lon: number; lat: number; id: string; mw: number | null; status: string; tech: string; state: string }[] = [];
  let notPlaced = 0, noShape = 0, drawn = 0, withheld = 0;
  // session 159: the count grid by grid, as the live set gives it. A grid whose operator's terms do not allow its
  // rows on the map (QUEUE_GRIDS, shown: false) is counted and left out: no row of it reaches the page.
  const grids = new Map<string, QueueGridCount>(QUEUE_GRIDS.map((g) => [g.id, { id: g.id, label: g.label, shown: g.shown, rows: 0, drawn: 0, not_drawn: 0 }]));
  const gridOf = (r: QueueRow): QueueGridCount => {
    const id = queueGridOf(r.src);
    if (!grids.has(id)) grids.set(id, { id, label: "Another table", shown: true, rows: 0, drawn: 0, not_drawn: 0 });
    return grids.get(id) as QueueGridCount;
  };
  const vintages: string[] = [];
  for (const r of rows) {
    const grid = gridOf(r);
    grid.rows += 1;
    if (!grid.shown) { withheld += 1; continue; }
    if (r.vintage) vintages.push(r.vintage);
    if (r.lat === null || r.lon === null || !["county", "point"].includes(r.prec ?? "")) { notPlaced += 1; grid.not_drawn += 1; continue; }
    if (r.prec === "point") { points.push({ lon: r.lon, lat: r.lat, id: r.entity_id, mw: r.capacity_mw, status: r.status ?? "", tech: r.tech ?? "", state: r.state ?? "" }); drawn += 1; grid.drawn += 1; continue; }
    const key = `${r.lon},${r.lat}`;
    if (!byPoint.has(key)) {
      const lon = r.lon, lat = r.lat;
      byPoint.set(key, counties().find((c) => lon >= c.box[0] && lon <= c.box[2] && lat >= c.box[1] && lat <= c.box[3] && inGeometry(c.geometry, lon, lat)) ?? countyNamed(r.state, r.county));
    }
    const county = byPoint.get(key);
    if (!county) { noShape += 1; grid.not_drawn += 1; continue; }
    const a = byCounty.get(county.id) ?? { county, state: r.state ?? "", requests: 0, mw: 0, noMw: 0, status: {} };
    a.requests += 1;
    if (r.capacity_mw === null) a.noMw += 1; else a.mw += Number(r.capacity_mw);
    const s = r.status || "not stated";
    a.status[s] = (a.status[s] ?? 0) + 1;
    byCounty.set(county.id, a);
    drawn += 1; grid.drawn += 1;
  }
  vintages.sort();
  const features = [...byCounty.values()].sort((a, b) => a.county.id.localeCompare(b.county.id)).map((a) => ({
    type: "Feature" as const,
    properties: { name: `${a.county.name}, ${a.state}`, kind: "county", fips: a.county.id, requests: a.requests, mw: Math.round(a.mw * 10) / 10, without_mw: a.noMw, status: a.status },
    geometry: { type: a.county.geometry.type, coordinates: round3(a.county.geometry.coordinates) },
  }));
  return {
    ok: true as const, tables: ["energy_projects"], rows: rows.length, drawn, counties: features.length, not_placed: notPlaced, no_shape: noShape,
    // rows of a grid whose operator's terms do not allow them on the map: counted, never sent to the page
    withheld, grids: [...grids.values()],
    vintage_first: vintages[0] ?? "", vintage_last: vintages.at(-1) ?? "", shapes: { type: "FeatureCollection" as const, features }, points,
  };
}

type FacilityRow = {
  entity_id: string; name: string | null; lat: number | null; lon: number | null; capacity_mw: number | null; status: string | null; operator: string | null;
  vintage: string | null; src: string | null; state: string | null; city: string | null; county: string | null; prec: string | null; site: string | null;
};
/** The datacenter facilities of the live set that the table places (the operator's coordinates, or a county or city
 *  point); the rest are counted and not drawn. */
export async function datacenters() {
  const rows = await rest<FacilityRow>("entities", {
    select: "entity_id,name,lat,lon,capacity_mw,status,operator,vintage,src:extra->>kind,state:extra->>state,city:extra->>city,county:extra->>county,prec:extra->>geo_precision,site:extra->>site_name",
    table_name: "eq.datacenter_facilities", order: "entity_id",
  }, HOURLY);
  const placed = rows.filter((r) => r.lat !== null && r.lon !== null);
  const vintages = rows.map((r) => r.vintage ?? "").filter(Boolean).sort();
  return {
    ok: true as const, tables: ["datacenter_facilities"], rows: rows.length, drawn: placed.length, not_placed: rows.length - placed.length, vintage: vintages.at(-1) ?? "",
    points: placed.map((r) => ({
      lon: r.lon as number, lat: r.lat as number, id: r.entity_id, operator: r.operator ?? "", site: r.site ?? r.name ?? "", mw: r.capacity_mw === null ? null : Number(r.capacity_mw),
      status: r.status ?? "", state: r.state ?? "", city: r.city ?? "", county: r.county ?? "", prec: r.prec ?? "", src: r.src ?? "",
    })),
  };
}
