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
// Session 193: the file held is a DERIVED one (each county given to one balancing authority from EIA-861; no public
// file of the boundaries was reached in three pulls). A derived file is never drawn without its label: the words stand
// inside the frame, under the map, wherever the regions are.
// Session 1156 (chain 077): the project map's state outlines (us-atlas's states-albers-10m, the Census Bureau's, drawn
// on the same projection as app/map/ProjectMap.tsx) over the regions; every line answers a hover with its direction and
// its window, and its MW only where the panel under the map (grid_network_<grid>) holds that figure, checked
// (lib/networkMap.ts edgeTip, edgeHeld); one of the seven ISO grids clicked opens its row on the Grid tool (linkOf).
// No price is drawn here: the lines are EIA-930's public interchange, for every grid.
// Session 1158 (chain 077, 390 pixels and accessibility): the drawing is no longer an image, since it holds the regions a
// keyboard reaches and the grids' links (an image's children are presentational: AccessLint,
// aria/presentational-children-focusable): an svg with its name and no role (its own, a graphics document; AccessLint
// does not allow "group" on an svg, aria/aria-allowed-role, so the gravity shape drops it too); a tap on a line shows its card
// (pointerdown), and a touch's pointerleave, which follows the tap at once, no longer takes the card away.
import { geoAlbersUsa, geoPath } from "d3-geo";
import { useEffect, useMemo, useState, type KeyboardEvent, type PointerEvent } from "react";
import { feature, mesh } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import statesTopo from "us-atlas/states-albers-10m.json";
import { shown } from "@/lib/format";
import { cardWidth, derivedLabel, edgeHeld, edgeTip, flowWidth, hitSegment, readBoundaries, ringPath, type Held, type MapPanel, type MapWindow } from "@/lib/networkMap";

export const BOUNDARY_FILE = "/network/ba_boundaries.json";
const W = 975, H = 610;
// the plane of the site's other map (app/map/ProjectMap.tsx): Albers for the lower 48, Alaska and Hawaii inset
const projection = geoAlbersUsa().scale(1300).translate([W / 2, H / 2]);
const project = (p: [number, number]) => projection(p) as [number, number] | null;
// session 1156: the project map's outlines. us-atlas's albers files are already on this plane (geoAlbersUsa, scale 1300,
// translated to the plane's middle), so they are drawn with no projection: the land, then the borders between states
let outlines: { nation: string; states: string } | null = null;
function stateOutlines() {
  if (outlines) return outlines;
  const topo = statesTopo as unknown as Topology<{ states: GeometryCollection; nation: GeometryCollection }>;
  const path = geoPath();
  outlines = { nation: path(feature(topo, topo.objects.nation)) ?? "", states: path(mesh(topo, topo.objects.states, (a, b) => a !== b)) ?? "" };
  return outlines;
}

export type MapNode = { id: string; name: string };
export type MapFlow = { source: string; target: string; mw: number; a: string; b: string };

export function NetworkMap({ nodes, flows, maxMw, colorOf, pick, neighbours, onPick, panel = null, win, linkOf }: {
  nodes: MapNode[]; flows: MapFlow[]; maxMw: number;
  /** the color the grid's sphere has for the hour shown (Network.tsx colorOf: the same measure, the same scale) */
  colorOf: (id: string) => string;
  pick: string | null;
  /** the selected grid's neighbours, which stay as they are while the rest is dimmed, as in the network */
  neighbours: Set<string>;
  onPick: (id: string) => void;
  /** session 1156: the panel under the map (the grid in view and its hour), whose figures alone a line's hover writes */
  panel?: MapPanel | null;
  /** session 1156: the frame the lines are drawn for (the hour or day shown, the snapshot's refresh) */
  win?: MapWindow;
  /** session 1156: the Grid tool's address a region clicked opens (one of the seven ISO grids), or null: its panel opens */
  linkOf?: (id: string) => string | null;
}) {
  const [held, setHeld] = useState<Held>({ state: "loading" });
  const [hover, setHover] = useState<{ id: string; kind: "region" | "edge"; x: number; y: number; right: boolean } | null>(null);
  const hoverAt = (id: string, kind: "region" | "edge") => (e: PointerEvent<SVGElement>) => {
    const b = (e.currentTarget.ownerSVGElement as SVGSVGElement).getBoundingClientRect();
    setHover({ id, kind, x: e.clientX - b.left, y: e.clientY - b.top, right: e.clientX - b.left > b.width / 2 });
  };
  // session 1158: a mouse leaving takes the card away; a finger lifting does not (its card stays until the next tap)
  const leave = (e: PointerEvent<SVGElement>) => { if (e.pointerType !== "touch") setHover(null); };
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
  const point = (id: string) => at.get(id) as [number, number];
  const drawnFlows = flows.filter((f) => at.has(f.source) && at.has(f.target));
  const noShape = nodes.filter((n) => !regions.some((r) => r.id === n.id));
  const lines = useMemo(() => stateOutlines(), []);
  const nameOf = (id: string) => names.get(id) ?? id;
  const hoveredEdge = hover && hover.kind === "edge" ? drawnFlows.find((f) => `${f.a}-${f.b}` === hover.id) ?? null : null;

  const derived = held.state === "held" ? derivedLabel(held.file) : null;
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
    <div className={`${frame} self-start bg-paper`} data-map-state="held" data-map-regions={regions.length} data-map-matched={held.file.matched}
      data-map-flows={drawnFlows.length} data-map-flows-all={flows.length} data-map-no-shape={noShape.map((n) => n.id).join(",")} data-map-sha={held.file.provenance.raw_sha256}
      data-map-derived={derived ? "1" : "0"} data-map-states={lines.states ? "1" : "0"} data-map-panel={panel ? `${panel.ba ?? "US48"}|${panel.hour}` : ""}
      data-map-held-edges={win ? drawnFlows.filter((f) => edgeHeld(f, panel, win)).length : 0}>
      {/* the map keeps its own proportions; a derived file's label stands under it, inside the frame, and covers no region */}
      <div className="relative" style={style}>
      <svg viewBox={`0 0 ${W} ${H}`} className="h-full w-full" preserveAspectRatio="xMidYMid meet" onPointerDown={(e) => { if (e.target === e.currentTarget) setHover(null); }}
        aria-label={`A map of the US balancing authorities on the state outlines, each region colored by the carbon intensity of its generation, with the power they exchange (EIA-930's public interchange); hover a region for its name, a line for its direction and window; ${linkOf ? "click one of the seven ISO grids to open its row on the Grid tool, any other region for its panel" : "click a region for its panel"}`}>
        <defs>
          <marker id="erw-flow-head" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0L8,4L0,8Z" fill="var(--color-accent)" /></marker>
          <marker id="erw-flow-head-dim" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0L8,4L0,8Z" fill="var(--color-rule)" /></marker>
        </defs>
        {/* session 1156: the land under the regions, so a county no grid is given reads as land, not as nothing */}
        <path d={lines.nation} fill="var(--color-panel)" stroke="none" pointerEvents="none" data-map-nation="1" />
        <g>
          {regions.map((r) => {
            const dim = pick !== null && pick !== r.id && !neighbours.has(r.id);
            const fill = colorOf(r.id);
            const href = linkOf ? linkOf(r.id) : null;
            const pressed = href ? {} : { tabIndex: 0, role: "button", "aria-label": names.get(r.id), onClick: () => onPick(r.id),
              onKeyDown: (e: KeyboardEvent<SVGPathElement>) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onPick(r.id); } } };
            const shape = (
              <path key={r.id} d={r.d} fillRule="evenodd" fill={fill} fillOpacity={dim ? 0.22 : 0.9} stroke={pick === r.id ? "var(--color-ink)" : "var(--color-panel)"} strokeWidth={pick === r.id ? 1.6 : 0.6}
                data-region={r.id} data-fill={fill} data-dim={dim ? "1" : "0"} data-region-href={href ?? undefined} className="cursor-pointer" {...pressed}
                onPointerMove={hoverAt(r.id, "region")}
                onPointerLeave={leave} onFocus={() => setHover({ id: r.id, kind: "region", x: -1, y: -1, right: false })} onBlur={() => setHover(null)} />
            );
            // session 1156: one of the seven ISO grids is a link to its row on the Grid tool (the map, its ties keyed in the panel under it)
            return href ? <a key={r.id} href={href} aria-label={`${names.get(r.id)}: open its row on the Grid tool`}
              onFocus={() => setHover({ id: r.id, kind: "region", x: -1, y: -1, right: false })} onBlur={() => setHover(null)}>{shape}</a> : shape;
          })}
        </g>
        {/* session 1156: the borders between states, the project map's, over the regions; they take no pointer */}
        <path d={lines.states} fill="none" stroke="var(--color-ink)" strokeOpacity={0.3} strokeWidth={0.5} strokeLinejoin="round" pointerEvents="none" data-map-state-lines="1" />
        <g pointerEvents="none" fill="none">
          {drawnFlows.map((f) => {
            const s = at.get(f.source) as [number, number], t = at.get(f.target) as [number, number];
            const dim = pick !== null && f.a !== pick && f.b !== pick;
            const w = flowWidth(f.mw, maxMw);
            return (
              <g key={`${f.a}-${f.b}`} data-flow={`${f.source}>${f.target}`} data-mw={f.mw} data-flow-held={win && edgeHeld(f, panel, win) ? "1" : "0"}>
                <line x1={s[0]} y1={s[1]} x2={t[0]} y2={t[1]} stroke={dim ? "var(--color-rule)" : "var(--color-muted)"} strokeOpacity={pick ? 0.6 : 0.45} strokeWidth={w} markerEnd={`url(#${dim ? "erw-flow-head-dim" : "erw-flow-head"})`} />
                {dim ? null : <line x1={s[0]} y1={s[1]} x2={t[0]} y2={t[1]} stroke="var(--color-accent)" strokeWidth={Math.max(1, w * 0.5)} strokeDasharray="2 10" strokeLinecap="round"
                  className="erw-flow-dash" style={{ animationDuration: `${Math.max(0.6, 2.4 - 1.8 * (f.mw / (maxMw || 1)))}s` }} />}
              </g>
            );
          })}
        </g>
        {/* session 1156: a wide clear stroke over the middle of each line takes the hover (its ends are left to the regions, whose clicks they are); the line drawn under it is unchanged */}
        {win ? (
          <g fill="none" data-map-edge-hits="1">
            {drawnFlows.map((f) => {
              const [s, t] = hitSegment(point(f.source), point(f.target));
              return <line key={`hit-${f.a}-${f.b}`} x1={s[0]} y1={s[1]} x2={t[0]} y2={t[1]} stroke="var(--color-ink)" strokeOpacity={0} strokeWidth={Math.max(10, flowWidth(f.mw, maxMw) + 6)}
                pointerEvents="stroke" data-edge={`${f.a}-${f.b}`} onPointerMove={hoverAt(`${f.a}-${f.b}`, "edge")} onPointerDown={hoverAt(`${f.a}-${f.b}`, "edge")} onPointerLeave={leave} />;
            })}
          </g>
        ) : null}
      </svg>
      {hover && hover.kind === "region" ? (
        <div className="pointer-events-none absolute z-10 border border-rule bg-panel px-2 py-0.5 text-xs" data-map-hover={hover.id}
          style={hover.x < 0 ? { left: 8, top: 8 } : hover.right ? { right: `calc(100% - ${hover.x - 12}px)`, top: hover.y + 12 } : { left: hover.x + 12, top: hover.y + 12 }}>{names.get(hover.id)}
          {linkOf && linkOf(hover.id) ? <span className="block text-muted">Click to open its row on the Grid tool</span> : null}</div>
      ) : null}
      {hoveredEdge && win && hover ? (
        <div className="pointer-events-none absolute z-10 border border-rule bg-panel px-2 py-0.5 text-xs" data-map-hover={hover.id} data-map-hover-kind="edge"
          data-map-hover-held={edgeHeld(hoveredEdge, panel, win) ? "1" : "0"}
          style={{ ...(hover.right ? { right: `calc(100% - ${hover.x - 12}px)`, top: hover.y + 12 } : { left: hover.x + 12, top: hover.y + 12 }), maxWidth: cardWidth(hover.x, hover.right) }}>
          {edgeTip(hoveredEdge, nameOf, panel, win, shown).map((line, i) => <div key={line} className={i === 0 ? "text-ink" : "text-muted"}>{line}</div>)}
        </div>
      ) : null}
      {/* the dash runs from the exporter to the importer, faster as the flow is larger; still where the reader asks for less motion */}
      <style>{`@keyframes erw-flow { to { stroke-dashoffset: -12; } } .erw-flow-dash { animation: erw-flow 1.2s linear infinite; } @media (prefers-reduced-motion: reduce) { .erw-flow-dash { animation: none; } }`}</style>
      </div>
      {derived ? (
        <p className="border-t border-rule bg-panel px-2 py-1 text-xs leading-snug text-ink" data-map-derived-label="1">
          {derived} {held.file.provenance.vintage ? <>Data year: {held.file.provenance.vintage}.</> : null}
        </p>
      ) : null}
    </div>
  );
}
