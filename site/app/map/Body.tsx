// The project map's body (session 16): summary counts, the map and the table view, from the
// energy_projects rows Supabase returned (and datacenter_projects points, when present).
import { geoAlbersUsa, geoPath } from "d3-geo";
import { feature, mesh } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import statesTopo from "us-atlas/states-albers-10m.json";
import { Cite } from "@/components/Cite";
import { Num } from "@/components/Num";
import type { ProjectPoint } from "@/lib/data";
import { count } from "@/lib/format";
import { COLOR_OF, KINDS, TECH_GROUPS, type MapData } from "./groups";
import { MapView } from "./MapView";

// us-atlas's albers files are drawn with geoAlbersUsa().scale(1300).translate([487.5, 305]) on a
// 975 x 610 canvas; the points use the same projection, so they sit on the state outlines.
const W = 975;
const H = 610;
const projection = geoAlbersUsa().scale(1300).translate([487.5, 305]);

function outlines(): { statesPath: string; nation: string } {
  const topo = statesTopo as unknown as Topology<{ states: GeometryCollection; nation: GeometryCollection }>;
  const path = geoPath();
  return {
    statesPath: path(mesh(topo, topo.objects.states, (a, b) => a !== b)) ?? "",
    nation: path(feature(topo, topo.objects.nation)) ?? "",
  };
}

export function Body({ rows }: { rows: ProjectPoint[] }) {
  // summary counts, straight from the rows Supabase returned
  const byKind = KINDS.map((k) => {
    const r = rows.filter((p) => p.kind === k.id);
    return {
      ...k,
      n: r.length,
      point: r.filter((p) => p.prec === "point").length,
      county: r.filter((p) => p.prec === "county").length,
      none: r.filter((p) => p.prec === "none").length,
      mw: r.reduce((a, p) => a + (p.capacity_mw ?? 0), 0),
    };
  }).filter((k) => k.n > 0);

  // points, projected; largest first so small points are drawn on top
  const states = Array.from(new Set(rows.map((p) => p.state ?? "").filter(Boolean))).sort();
  const statuses = Array.from(new Set(rows.map((p) => p.status ?? ""))).sort();
  const data: MapData = {
    width: W, height: H, ...outlines(),
    stateCodes: states, statuses,
    x: [], y: [], mw: [], kind: [], tech: [], state: [], status: [], county: [], table: [], id: [],
    offMap: 0, unplaced: 0,
  };
  const sorted = [...rows].sort((a, b) => (b.capacity_mw ?? 0) - (a.capacity_mw ?? 0));
  for (const p of sorted) {
    if (p.lat === null || p.lon === null) {
      data.unplaced += 1;
      continue;
    }
    const xy = projection([p.lon, p.lat]);
    if (!xy) {
      data.offMap += 1; // outside the lower 48, Alaska and Hawaii (Puerto Rico, for example)
      continue;
    }
    data.x.push(Math.round(xy[0] * 10) / 10);
    data.y.push(Math.round(xy[1] * 10) / 10);
    data.mw.push(p.capacity_mw ?? 0);
    data.kind.push(Math.max(0, KINDS.findIndex((k) => k.id === p.kind)));
    const t = TECH_GROUPS.findIndex((g) => g.id === p.tech);
    data.tech.push(t < 0 ? TECH_GROUPS.length - 1 : t);
    data.state.push(states.indexOf(p.state ?? ""));
    data.status.push(statuses.indexOf(p.status ?? ""));
    data.county.push(p.prec === "county" ? 1 : 0);
    data.table.push(0);
    data.id.push(p.entity_id);
  }

  // table view: count and MW by technology group and kind
  const table = TECH_GROUPS.map((g) => ({
    g,
    cells: byKind.map((k) => {
      const r = rows.filter((p) => p.kind === k.id && (p.tech ?? "unknown") === g.id);
      return { k: k.id, n: r.length, mw: r.reduce((a, p) => a + (p.capacity_mw ?? 0), 0) };
    }),
  })).filter((row) => row.cells.some((c) => c.n > 0));

  return (
    <>
      <section aria-label="What the map holds" className="mb-5">
        <div className="grid gap-px border border-rule bg-rule sm:grid-cols-3">
          {byKind.map((k) => (
            <div key={k.id} className="bg-panel px-3 py-2">
              <div className="text-xs text-muted">{k.label}</div>
              <div className="text-lg tabular-nums">
                <Num check={`projects|count|${k.id}|all`} raw={k.n}>{count(k.n)}</Num>{" "}
                <span className="text-sm text-muted">
                  {k.id === "queue" ? "positions" : "generators"},{" "}
                  <Num check={`projects|mw|${k.id}`} raw={k.mw}>{count(k.mw)}</Num> MW
                </span>
              </div>
              <div className="text-xs text-muted">
                <Num check={`projects|count|${k.id}|point`} raw={k.point}>{count(k.point)}</Num> at exact coordinates,{" "}
                <Num check={`projects|count|${k.id}|county`} raw={k.county}>{count(k.county)}</Num> at a county point,{" "}
                <Num check={`projects|count|${k.id}|none`} raw={k.none}>{count(k.none)}</Num> not placed
              </div>
            </div>
          ))}
        </div>
        <p className="mt-1 text-xs text-muted">
          MW as each source states it: EIA nameplate capacity; for a queue position, the MW requested. A position that is not placed names no county the
          gazetteer holds (a city, a misspelling, or no county at all); the table <code className="font-mono">energy_projects</code> says why for each.
        </p>
      </section>

      <MapView data={data} colors={COLOR_OF} />

      <section aria-label="Table view" className="mt-8">
        <h2 className="mb-2 font-serif text-xl">By technology</h2>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm tabular-nums">
            <thead>
              <tr className="border-b border-rule text-left text-xs text-muted">
                <th className="py-1 pr-3 font-normal">Technology group</th>
                {byKind.map((k) => (
                  <th key={k.id} className="py-1 pr-3 text-right font-normal" colSpan={2}>
                    {k.label}: count, MW
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {table.map((row) => (
                <tr key={row.g.id} className="border-b border-rule">
                  <td className="py-1 pr-3">
                    <span aria-hidden className="mr-2 inline-block h-2.5 w-2.5 rounded-full align-middle" style={{ background: `var(${COLOR_OF[row.g.color]})` }} />
                    {row.g.label}
                  </td>
                  {row.cells.map((c) => (
                    <FragmentCells key={c.k} kind={c.k} group={row.g.id} n={c.n} mw={c.mw} />
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-1 text-xs text-muted">
          Colors on the map: the eight fuel colors of the site; petroleum, biomass, geothermal, hybrid, transmission and unknown share the color of
          other. Hybrid is a queue position naming more than one technology (solar and storage, for example).
        </p>
      </section>
      <Cite
        tables={["energy_projects"]}
        note="Derived by warehouse/derived/energy_projects.py from the EIA-860M inventories and the six ISO queues, with county points from the U.S. Census Bureau's 2025 county gazetteer (method: docs/methods/energy_projects.md)"
      />
    </>
  );
}

function FragmentCells({ kind, group, n, mw }: { kind: string; group: string; n: number; mw: number }) {
  return (
    <>
      <td className="py-1 pr-2 text-right">
        {n ? <Num check={`projects|tech_count|${kind}|${group}`} raw={n}>{count(n)}</Num> : <span className="text-muted">0</span>}
      </td>
      <td className="py-1 pr-3 text-right text-muted">{n ? count(mw) : ""}</td>
    </>
  );
}
