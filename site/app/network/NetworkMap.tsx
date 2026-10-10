"use client";
// Session 180: the network as a map. The same grids, the same hour and the same ties as the network beside it
// (Network.tsx owns every one of them: the view, the hour the replay is on, the selection, the colors and the panel);
// this file only draws them on the ground. Each balancing authority is its published boundary
// (public/network/ba_boundaries.json, warehouse/connectors/eia_ba_boundaries.py), filled with the color its sphere
// has; each tie is a line between the two regions, as wide as the network draws it, with a dash that runs from the
// exporter to the importer and an arrowhead at the importer. Hovering a region names it, as hovering a sphere does;
// clicking it opens the same panel.
// Real data only: the file is read when the map is first shown, and when it is not held the frame says so and draws
// nothing. No shape is drawn from anything but the file. A grid of the network with no shape in the file (Canada's and
// Mexico's operators, and any the publisher's file does not name) is not on the map, and the line under it says which.
import { geoAlbersUsa } from "d3-geo";
import { useEffect, useMemo, useState } from "react";
import { flowWidth, readBoundaries, ringPath, type Held } from "@/lib/networkMap";

export const BOUNDARY_FILE = "/network/ba_boundaries.json";
const W = 975, H = 610;
// the plane of the site's other map (app/map/ProjectMap.tsx): Albers for the lower 48, Alaska and Hawaii inset
const projection = geoAlbersUsa().scale(1300).translate([W / 2, H / 2]);
const project = (p: [number, number]) => projection(p) as [number, number] | null;

export type MapNode = { id: string; name: string };
export type MapFlow = { source: string; target: string; mw: number; a: string; b: string };

export function NetworkMap({ nodes, flows, maxMw, colorOf, pick, neighbours, onPick }: {
  nodes: MapNode[]; flows: MapFlow[]; maxMw: number;
  /** the color the grid's sphere has for the hour shown (Network.tsx colorOf: the same measure, the same scale) */
  colorOf: (id: string) => string;
  pick: string | null;
  /** the selected grid's neighbours, which stay as they are while the rest is dimmed, as in the network */
  neighbours: Set<string>;
  onPick: (id: string) => void;
}) {
  const [held, setHeld] = useState<Held>({ state: "loading" });
  const [hover, setHover] = useState<{ id: string; x: number; y: number; right: boolean } | null>(null);
  useEffect(() => {
    let alive = true;
    fetch(BOUNDARY_FILE)
      .then(async (r) => (r.status === 404 ? ({ state: "absent" } as Held) : r.ok ? readBoundaries(await r.json()) : ({ state: "error", why: `HTTP ${r.status}` } as Held)))
      .catch((e: Error) => ({ state: "error", why: e.message }) as Held)
      .then((h) => { if (alive) setHeld(h); });
    return () => { alive = false; };
  }, []);

  const names = useMemo(() => new Map(nodes.map((n) => [n.id, n.name])), [nodes]);
  // only the grids the network draws, each once, in the file's order (largest first, so a smaller one is on top)
  const regions = useMemo(() => {
    if (held.state !== "held") return [];
    const seen = new Set<string>();
    return held.file.regions.filter((r) => names.has(r.id) && !seen.has(r.id) && !!seen.add(r.id))
      .map((r) => ({ id: r.id, d: r.rings.map((ring) => ringPath(ring, project)).join(""), at: project(r.point) })).filter((r) => r.d);
  }, [held, names]);
  const at = useMemo(() => new Map(regions.filter((r) => r.at).map((r) => [r.id, r.at as [number, number]])), [regions]);
  const drawnFlows = flows.filter((f) => at.has(f.source) && at.has(f.target));
  const noShape = nodes.filter((n) => !regions.some((r) => r.id === n.id));

  const frame = "w-full min-w-0 overflow-hidden border border-rule";
  // the frame has the map's own proportions, so a phone shows the whole country with no empty band above and below it
  const style = { aspectRatio: `${W} / ${H}`, maxHeight: "min(72vh, 620px)", minHeight: 200 };
  if (held.state !== "held") {
    return (
      <div className={`${frame} flex items-center justify-center bg-panel p-6`} style={style} data-map-state={held.state} data-map-regions="0" data-map-matched="0">
        <p className="max-w-md text-sm" role="status">
          {held.state === "loading" ? <>Reading the boundaries.</>
            : held.state === "absent" ? <>The boundary file is not yet held: the warehouse does not yet hold a published file of the balancing authorities&apos; boundaries, so no region is drawn here and none is
              sketched in its place. The Network view shows the same grids, flows and numbers.</>
              : <>The boundary file could not be read ({held.why}), so no region is drawn. The Network view shows the same grids, flows and numbers.</>}
        </p>
      </div>
    );
  }
  return (
    <div className={`${frame} relative bg-paper`} style={style} data-map-state="held" data-map-regions={regions.length} data-map-matched={held.file.matched}
      data-map-flows={drawnFlows.length} data-map-flows-all={flows.length} data-map-no-shape={noShape.map((n) => n.id).join(",")} data-map-sha={held.file.provenance.raw_sha256}>
      <svg viewBox={`0 0 ${W} ${H}`} className="h-full w-full" role="img" preserveAspectRatio="xMidYMid meet"
        aria-label="A map of the US balancing authorities, each region colored by the carbon intensity of its generation, with the power they exchange; hover a region for its name, click it for its panel">
        <defs>
          <marker id="erw-flow-head" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0L8,4L0,8Z" fill="#8C1515" /></marker>
          <marker id="erw-flow-head-dim" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0L8,4L0,8Z" fill="#D9D2C3" /></marker>
        </defs>
        <g>
          {regions.map((r) => {
            const dim = pick !== null && pick !== r.id && !neighbours.has(r.id);
            const fill = colorOf(r.id);
            return (
              <path key={r.id} d={r.d} fillRule="evenodd" fill={fill} fillOpacity={dim ? 0.22 : 0.9} stroke={pick === r.id ? "#2E2D29" : "#FBF8F2"} strokeWidth={pick === r.id ? 1.6 : 0.6}
                data-region={r.id} data-fill={fill} data-dim={dim ? "1" : "0"} className="cursor-pointer" tabIndex={0} role="button" aria-label={names.get(r.id)}
                onClick={() => onPick(r.id)} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onPick(r.id); } }}
                onPointerMove={(e) => { const b = (e.currentTarget.ownerSVGElement as SVGSVGElement).getBoundingClientRect(); setHover({ id: r.id, x: e.clientX - b.left, y: e.clientY - b.top, right: e.clientX - b.left > b.width / 2 }); }}
                onPointerLeave={() => setHover(null)} onFocus={() => setHover({ id: r.id, x: -1, y: -1, right: false })} onBlur={() => setHover(null)} />
            );
          })}
        </g>
        <g pointerEvents="none" fill="none">
          {drawnFlows.map((f) => {
            const s = at.get(f.source) as [number, number], t = at.get(f.target) as [number, number];
            const dim = pick !== null && f.a !== pick && f.b !== pick;
            const w = flowWidth(f.mw, maxMw);
            return (
              <g key={`${f.a}-${f.b}`} data-flow={`${f.source}>${f.target}`} data-mw={f.mw}>
                <line x1={s[0]} y1={s[1]} x2={t[0]} y2={t[1]} stroke={dim ? "#D9D2C3" : "#6B665E"} strokeOpacity={pick ? 0.6 : 0.45} strokeWidth={w} markerEnd={`url(#${dim ? "erw-flow-head-dim" : "erw-flow-head"})`} />
                {dim ? null : <line x1={s[0]} y1={s[1]} x2={t[0]} y2={t[1]} stroke="#8C1515" strokeWidth={Math.max(1, w * 0.5)} strokeDasharray="2 10" strokeLinecap="round"
                  className="erw-flow-dash" style={{ animationDuration: `${Math.max(0.6, 2.4 - 1.8 * (f.mw / (maxMw || 1)))}s` }} />}
              </g>
            );
          })}
        </g>
      </svg>
      {hover ? (
        <div className="pointer-events-none absolute z-10 border border-rule bg-panel px-2 py-0.5 text-xs shadow-sm" data-map-hover={hover.id}
          style={hover.x < 0 ? { left: 8, top: 8 } : hover.right ? { right: `calc(100% - ${hover.x - 12}px)`, top: hover.y + 12 } : { left: hover.x + 12, top: hover.y + 12 }}>{names.get(hover.id)}</div>
      ) : null}
      {/* the dash runs from the exporter to the importer, faster as the flow is larger; still where the reader asks for less motion */}
      <style>{`@keyframes erw-flow { to { stroke-dashoffset: -12; } } .erw-flow-dash { animation: erw-flow 1.2s linear infinite; } @media (prefers-reduced-motion: reduce) { .erw-flow-dash { animation: none; } }`}</style>
    </div>
  );
}
